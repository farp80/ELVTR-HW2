# Task 5 — Workflow

## Logic

`TicketWorkflow.process_ticket` accepts one ticket, runs routing and the retrieval-plus-LLM path together, and returns the review package from `WORKFLOW_CONTRACT.md`. A bad request returns `input_rejected` before any service runs. A service error returns `workflow_failed`. A clean run returns `summary_ready_for_review` with the original `Body` in `ticket_body`. `trace_id` stays `None` until Task 6.

Save the program below as `workflow.py` when you run it. Task 6 replaces this file with the traced version.

## The fixed prompt settings

`MODEL` is `qwen2.5:1.5b-instruct-q4_K_M`. `OPTIONS` sets `temperature` to 0, `seed` to 42, and `num_predict` to 512. `SCHEMA` describes a JSON object with the required keys `summary`, `customer_request`, and `missing_information`, and `additionalProperties` is false. `SYSTEM` is the system message. It tells the model that the ticket body is the customer's text, that support articles are outside context, and that article facts belong in the missing-information list.

`TicketWorkflow.__init__` builds `RoutingService(model_path)`, `RetrievalService(database_path, top_k=5)`, and `LLMClient()`. Those three objects stay on the workflow and serve every later ticket.

## How a ticket is accepted

`process_ticket` starts with `record_id = str(uuid4())`. That UUID is created here. The method reads `ticket_id` and `Body` from the request and leaves every other key unused.

`_ticket_id` returns true when the value is an `int`, is not a `bool`, and is greater than 0. `True` and `False` fail because they are booleans.

`_accept` returns three values: the id to put in the package, the body to send to the services, and an error string. A non-dictionary request returns `None`, `None`, and "request must be a dictionary". A bad id becomes `None` with the error "ticket_id must be a positive integer". A `Body` that is not a string, or whose `strip()` is empty, produces the error "Body must contain text". If the id was already bad, that id error is the one returned. When both fields pass, the third value is `None` and the body is the original `Body`.

`process_ticket` treats a non-empty third value as rejection. It returns `_package` with status `input_rejected` and skips `_run`.

## How the prompt is built

`_messages` loops over the evidence list. For each hit it reads `metadata["title"]`, `chunk_id`, and `content`, and builds one block of the form `[chunk_id] title` followed by the chunk text. `"\n\n".join(blocks)` separates the blocks. An empty list becomes the sentence "(No support articles retrieved.)". The user string places the original body under the heading `TICKET BODY (customer-provided text):` and the blocks under `SUPPORT ARTICLES (external context, not customer statements):`. The return value is a list of two messages: `role` `system` with `SYSTEM`, then `role` `user` with that string.

## How the summary is parsed

`_summary` calls `json.loads` on the LLM text. A `JSONDecodeError` becomes `RuntimeError("summary was not valid JSON")`. The parsed value must be a dictionary whose keys are exactly `summary`, `customer_request`, and `missing_information`. The first two must be strings that still have a character after `strip()`. `missing_information` must be a list, and every item must be a non-blank string. An empty list passes. Any other shape raises `RuntimeError`. A good dictionary is returned as the `ticket_summary`.

## How the two paths run

`_summarize` calls `retrieve_evidence` with `{"body": body}`. It stores `found["evidence"]`. It then calls `call_llm` with `messages` from `_messages(body, evidence)`, plus `MODEL`, `OPTIONS`, and `SCHEMA`. It returns `_summary(reply["content"])` and that evidence list. Retrieval finishes before the prompt is built, because the prompt contains the chunk text. This method is the whole second path.

`_run` opens `ThreadPoolExecutor(max_workers=2)`. It submits `route_ticket({"body": body})` and `_summarize(body)` before it waits. Two workers let the two calls run at the same time. The code then calls `route_future.result()`. That call waits for routing and returns the route dictionary. If routing raised, `result()` raises, and the `except` stores the exception on `route_error`. The same pattern runs for `summary_future`, so a routing error still leaves the method waiting for the summary path. If either error is set, `_run` raises `RuntimeError("a workflow service failed")`. If the department is outside `DEPARTMENTS`, it raises `RuntimeError("routing department is not allowed")`. A clean finish returns the route, the summary, and the evidence.

## How the package is filled

`_package` returns one dictionary with the ten contract fields. `ready` is true only for `summary_ready_for_review`. In that case `recommended_department` and `class_scores` come from the route, `ticket_body` is the original body, `ticket_summary` is the parsed summary, `retrieved_evidence` is the evidence list, and `error` is `None`. For the other two statuses those review fields are `None`, `retrieved_evidence` is `[]`, and `error` is the short message. `trace_id` is `None` in every package this file builds.

`process_ticket` calls `_run` inside `try`. An exception becomes a `workflow_failed` package whose error is "a workflow service failed". A normal return becomes `summary_ready_for_review` and passes the route, the original body, the summary, and the evidence into `_package`.

## Program

```python
import json
from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4

from llm_service import LLMClient
from retrieval_service import RetrievalService
from routing_service import DEPARTMENTS, RoutingService

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
    return {
        "ticket_id": ticket_id,
        "workflow_record_id": record_id,
        "terminal_status": status,
        "recommended_department": route["recommended_department"] if ready else None,
        "class_scores": route["class_scores"] if ready else None,
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
            route_error = summary_error = None
            try:
                route = route_future.result()
            except Exception as exc:
                route, route_error = None, exc
            try:
                summary, evidence = summary_future.result()
            except Exception as exc:
                summary, evidence, summary_error = None, None, exc
        if route_error or summary_error:
            raise RuntimeError("a workflow service failed")
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
        except Exception:
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
```
