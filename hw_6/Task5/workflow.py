import json
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from hw_6.Task2.routing_service import DEPARTMENTS, RoutingService
from hw_6.Task3.retrieval_service import RetrievalService
from hw_6.Task4.llm_service import LLMClient

MODEL = "qwen2.5:1.5b-instruct-q4_K_M"
OPTIONS = {"temperature": 0, "seed": 42, "num_predict": 512}
SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "customer_request": {"type": "string"},
        "missing_information": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "customer_request", "missing_information"],
    "additionalProperties": False,
}
SYSTEM = """You write an internal summary of a customer support ticket for a human support agent.

The ticket body is what the customer wrote. Support articles are outside context. Use an article only when it applies. Use article context only to identify information missing from the ticket; never present article facts as customer statements. Do not add unsupported facts, guess, suggest a solution, or assign a department.

Return a JSON object with exactly these fields:
- summary: one or two short sentences describing the reported issue.
- customer_request: everything the customer asks for, in one or two sentences. Include every request and every question.
- missing_information: a list of details needed to understand or act on the request. Use an empty list if nothing is clearly missing."""


def _ticket_id(value):
    return isinstance(value, int) and not isinstance(value, bool) and value > 0


def _accept(request):
    if not isinstance(request, dict):
        return None, None, "request must be a dictionary"
    ticket_id = request.get("ticket_id")
    if not _ticket_id(ticket_id):
        ticket_id = None
        id_error = "ticket_id must be a positive integer"
    else:
        id_error = None
    body = request.get("Body")
    if not isinstance(body, str) or not body.strip():
        return ticket_id, None, id_error or "Body must contain text"
    return ticket_id, body, id_error


def _summary(raw):
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("summary was not valid JSON") from exc
    fields = {"summary", "customer_request", "missing_information"}
    if not isinstance(data, dict) or set(data) != fields:
        raise RuntimeError("summary fields are wrong")
    if any(not isinstance(data[key], str) or not data[key].strip() for key in ("summary", "customer_request")):
        raise RuntimeError("summary text is empty")
    missing = data["missing_information"]
    if not isinstance(missing, list) or any(not isinstance(item, str) or not item.strip() for item in missing):
        raise RuntimeError("missing_information must be a list of strings")
    return data


def _messages(body, evidence):
    blocks = []
    for hit in evidence:
        title = hit["metadata"]["title"]
        blocks.append(f"[{hit['chunk_id']}] {title}\n{hit['content']}")
    articles = "\n\n".join(blocks) or "(No support articles retrieved.)"
    user = (
        "TICKET BODY (customer-provided text):\n"
        f"{body}\n\n"
        "SUPPORT ARTICLES (external context, not customer statements):\n"
        f"{articles}"
    )
    return [{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}]


def _package(ticket_id, record_id, status, error, route=None, body=None, summary=None, evidence=None):
    ready = status == "summary_ready_for_review"
    route = route or {}
    return {
        "ticket_id": ticket_id,
        "workflow_record_id": record_id,
        "terminal_status": status,
        "recommended_department": route.get("recommended_department") if ready else None,
        "class_scores": route.get("class_scores") if ready else None,
        "ticket_body": body if ready else None,
        "ticket_summary": summary if ready else None,
        "retrieved_evidence": evidence if ready else [],
        "trace_id": None,
        "error": None if ready else error,
    }


class TicketWorkflow:
    def __init__(self, model_path, database_path):
        self._routing = RoutingService(model_path)
        self._retrieval = RetrievalService(database_path, top_k=5)
        self._llm = LLMClient()

    def _summarize(self, body):
        found = self._retrieval.retrieve_evidence({"body": body})
        evidence = found["evidence"]
        reply = self._llm.call_llm(
            {
                "messages": _messages(body, evidence),
                "model": MODEL,
                "options": OPTIONS,
                "schema": SCHEMA,
            }
        )
        return _summary(reply["content"]), evidence

    def _run(self, body):
        with ThreadPoolExecutor(max_workers=2) as pool:
            route_future = pool.submit(self._routing.route_ticket, {"body": body})
            summary_future = pool.submit(self._summarize, body)
            # exception() waits for the path and returns its error, if any.
            route_error = route_future.exception()
            summary_error = summary_future.exception()
        if route_error or summary_error:
            raise RuntimeError("a workflow service failed") from (
                route_error or summary_error
            )
        route = route_future.result()
        summary, evidence = summary_future.result()
        if route["recommended_department"] not in DEPARTMENTS:
            raise RuntimeError("routing department is not allowed")
        return route, summary, evidence

    def process_ticket(self, request):
        record_id = str(uuid4())
        ticket_id, body, reject = _accept(request)
        if reject:
            return _package(ticket_id, record_id, "input_rejected", reject)
        try:
            route, summary, evidence = self._run(body)
        except RuntimeError:
            return _package(ticket_id, record_id, "workflow_failed", "a workflow service failed")
        return _package(
            ticket_id,
            record_id,
            "summary_ready_for_review",
            None,
            route=route,
            body=body,
            summary=summary,
            evidence=evidence,
        )