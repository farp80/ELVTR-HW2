import asyncio
import json
from time import perf_counter
from uuid import uuid4

from llm_service import LLMClient
from retrieval_service import RetrievalService
from routing_service import DEPARTMENTS, RoutingService
from indexed_trace_logger import IndexedTraceLogger

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


def _package(ticket_id, record_id, trace_id, status, error, route=None, body=None, summary=None, evidence=None):
    ready = status == "summary_ready_for_review"
    return {
        "ticket_id": ticket_id,
        "workflow_record_id": record_id,
        "terminal_status": status,
        "recommended_department": route["recommended_department"] if ready else None,
        "class_scores": route["class_scores"] if ready else None,
        "ticket_body": body if ready else None,
        "ticket_summary": summary if ready else None,
        "retrieved_evidence": evidence if ready else [],
        "trace_id": trace_id,
        "error": None if ready else error,
    }


class TicketWorkflow:
    def __init__(self, model_path, database_path, log_path):
        self._routing = RoutingService(model_path)
        self._retrieval = RetrievalService(database_path, top_k=5)
        self._llm = LLMClient()
        self._logger = IndexedTraceLogger(log_path)

    def _record(self, trace_id, **fields):
        self._logger.record(trace_id, **fields)

    async def _route_path(self, body, trace_id):
        started = perf_counter()
        self._record(trace_id, service="routing", event="started")
        try:
            result = await asyncio.to_thread(self._routing.route_ticket, {"body": body})
        except Exception:
            elapsed_ms = int((perf_counter() - started) * 1000)
            self._record(trace_id, service="routing", event="failed", elapsed_ms=elapsed_ms)
            raise
        elapsed_ms = int((perf_counter() - started) * 1000)
        self._record(
            trace_id,
            service="routing",
            event="completed",
            elapsed_ms=elapsed_ms,
            recommended_department=result["recommended_department"],
        )
        return result

    async def _retrieve_path(self, body, trace_id):
        started = perf_counter()
        self._record(trace_id, service="retrieval", event="started")
        try:
            found = await asyncio.to_thread(self._retrieval.retrieve_evidence, {"body": body})
        except Exception:
            elapsed_ms = int((perf_counter() - started) * 1000)
            self._record(trace_id, service="retrieval", event="failed", elapsed_ms=elapsed_ms)
            raise
        evidence = found["evidence"]
        elapsed_ms = int((perf_counter() - started) * 1000)
        self._record(
            trace_id,
            service="retrieval",
            event="completed",
            elapsed_ms=elapsed_ms,
            chunk_ids=[hit["chunk_id"] for hit in evidence],
            chunk_count=len(evidence),
        )
        return evidence

    async def _llm_path(self, body, evidence, trace_id):
        started = perf_counter()
        self._record(trace_id, service="llm", event="started", chunk_count=len(evidence))
        try:
            reply = await asyncio.to_thread(
                self._llm.call_llm,
                {
                    "messages": _messages(body, evidence),
                    "model": MODEL,
                    "options": OPTIONS,
                    "schema": SCHEMA,
                },
            )
            summary = _summary(reply["content"])
        except Exception:
            elapsed_ms = int((perf_counter() - started) * 1000)
            self._record(trace_id, service="llm", event="failed", elapsed_ms=elapsed_ms)
            raise
        elapsed_ms = int((perf_counter() - started) * 1000)
        self._record(
            trace_id,
            service="llm",
            event="completed",
            elapsed_ms=elapsed_ms,
            missing_count=len(summary["missing_information"]),
        )
        return summary

    async def _summarize_path(self, body, trace_id):
        evidence = await self._retrieve_path(body, trace_id)
        summary = await self._llm_path(body, evidence, trace_id)
        return summary, evidence

    async def _run(self, body, trace_id):
        route_task = asyncio.create_task(self._route_path(body, trace_id))
        summary_task = asyncio.create_task(self._summarize_path(body, trace_id))
        route_error = summary_error = None
        try:
            route = await route_task
        except Exception as exc:
            route, route_error = None, exc
        try:
            summary, evidence = await summary_task
        except Exception as exc:
            summary, evidence, summary_error = None, None, exc
        if route_error or summary_error:
            raise RuntimeError("a workflow service failed")
        if route["recommended_department"] not in DEPARTMENTS:
            raise RuntimeError("routing department is not allowed")
        return route, summary, evidence

    def process_ticket(self, request):
        record_id = str(uuid4())
        trace_id = self._logger.generate_trace_id()
        started = perf_counter()
        self._record(trace_id, service="workflow", event="started")
        ticket_id, body, reject = _accept(request)
        if reject:
            elapsed_ms = int((perf_counter() - started) * 1000)
            self._record(trace_id, service="workflow", event="completed", terminal_status="input_rejected", elapsed_ms=elapsed_ms)
            return _package(ticket_id, record_id, trace_id, "input_rejected", reject)
        try:
            route, summary, evidence = asyncio.run(self._run(body, trace_id))
        except Exception:
            elapsed_ms = int((perf_counter() - started) * 1000)
            self._record(trace_id, service="workflow", event="failed", terminal_status="workflow_failed", elapsed_ms=elapsed_ms)
            return _package(ticket_id, record_id, trace_id, "workflow_failed", "a workflow service failed")
        elapsed_ms = int((perf_counter() - started) * 1000)
        self._record(trace_id, service="workflow", event="completed", terminal_status="summary_ready_for_review", elapsed_ms=elapsed_ms)
        return _package(
            ticket_id,
            record_id,
            trace_id,
            "summary_ready_for_review",
            None,
            route=route,
            body=body,
            summary=summary,
            evidence=evidence,
        )