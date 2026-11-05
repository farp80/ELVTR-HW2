# Task 6 — Workflow with tracing

## Logic

`TicketWorkflow.process_ticket` accepts one ticket, runs routing and the retrieval-plus-LLM path together, and returns the review package. A bad request returns `input_rejected` before any service runs. A service error returns `workflow_failed`. A clean run returns `summary_ready_for_review` with the original `Body` in `ticket_body`. One `IndexedTraceLogger` puts a `trace_id` on every log line and in the response. Each service writes `started`, then `completed` or `failed`, with `elapsed_ms`. The routing line adds the department. The retrieval line adds the chunk ids.

Save this program as `workflow.py`.

## The fixed prompt settings

`MODEL` is `qwen2.5:1.5b-instruct-q4_K_M`. `OPTIONS` sets `temperature` to 0, `seed` to 42, and `num_predict` to 512. `SCHEMA` describes a JSON object with the required keys `summary`, `customer_request`, and `missing_information`, and `additionalProperties` is false. `SYSTEM` tells the model that the ticket body is the customer's text, that support articles are outside context, and that article facts belong in the missing-information list.

`__init__` receives `model_path`, `database_path`, and `log_path`. It builds `RoutingService(model_path)`, `RetrievalService(database_path, top_k=5)`, and `LLMClient()`. Those three objects stay on the workflow and serve every later ticket.

## How a ticket is accepted

`process_ticket` starts with `record_id = str(uuid4())`. That UUID is created here. The method reads `ticket_id` and `Body` from the request and leaves every other key unused.

`_ticket_id` returns true when the value is an `int`, is not a `bool`, and is greater than 0. `True` and `False` fail because they are booleans.

`_accept` returns three values: the id to put in the package, the body to send to the services, and an error string. A non-dictionary request returns `None`, `None`, and "request must be a dictionary". A bad id becomes `None` with the error "ticket_id must be a positive integer". A `Body` that is not a string, or whose `strip()` is empty, produces the error "Body must contain text". If the id was already bad, that id error is the one returned. When both fields pass, the third value is `None` and the body is the original `Body`.

A non-empty third value is a rejection. `process_ticket` returns `_package` with status `input_rejected` and skips `_run`.

## How the prompt is built

`_messages` loops over the evidence list. For each hit it reads `metadata["title"]`, `chunk_id`, and `content`, and builds one block of the form `[chunk_id] title` followed by the chunk text. `"\n\n".join(blocks)` separates the blocks. An empty list becomes the sentence "(No support articles retrieved.)". The user string places the original body under the heading `TICKET BODY (customer-provided text):` and the blocks under `SUPPORT ARTICLES (external context, not customer statements):`. The return value is a list of two messages: `role` `system` with `SYSTEM`, then `role` `user` with that string.

## How the summary is parsed

`_summary` calls `json.loads` on the LLM text. A `JSONDecodeError` becomes `RuntimeError("summary was not valid JSON")`. The parsed value must be a dictionary whose keys are exactly `summary`, `customer_request`, and `missing_information`. The first two must be strings that still have a character after `strip()`. `missing_information` must be a list, and every item must be a non-blank string. An empty list passes. Any other shape raises `RuntimeError`. A good dictionary is returned as the `ticket_summary`.

## How the package is filled

`_package` returns one dictionary with the ten contract fields. `ready` is true only for `summary_ready_for_review`. In that case `recommended_department` and `class_scores` come from the route, `ticket_body` is the original body, `ticket_summary` is the parsed summary, `retrieved_evidence` is the evidence list, and `error` is `None`. For `input_rejected` and `workflow_failed`, those review fields are `None`, `retrieved_evidence` is `[]`, and `error` is the short message. `ticket_id` and `workflow_record_id` are the values `process_ticket` passed in. `terminal_status` is the status argument. `trace_id` is the id created for this ticket.

## How the logger is created

`__init__` runs `IndexedTraceLogger(log_path)` once and stores it on `self._logger`. That object is a `TraceLogger`, so `generate_trace_id`, `record`, and `close` are the methods from the supplied class. The subclass keeps an index of rows by `trace_id`, locks the write together with that index, and raises `ValueError` when a private field is passed. `_record` calls `self._logger.record(trace_id, **fields)`. `record` adds a UTC `timestamp` and the `trace_id`, then writes one JSON line. `process_ticket` calls `generate_trace_id()` once. That same id goes on every line and into the package.

## How the parallel paths run

`process_ticket` starts the service work with `self._run(body, trace_id)`. `_run` opens a `ThreadPoolExecutor` with two workers and submits `_route_path` and `_summarize_path` before it waits, the same way `parallelism_example.py` does. Both paths start, then `exception()` waits for each one and returns its error, or `None`. Either error becomes `RuntimeError("a workflow service failed")`, chained to the original error. A department outside `DEPARTMENTS` raises `RuntimeError("routing department is not allowed")`.

`_route_path` writes `service` `routing` and `event` `started`, then calls `route_ticket`. The completed line includes `elapsed_ms` and `recommended_department`. A raised error writes `event` `failed` with `elapsed_ms`, then the same error propagates.

`_summarize_path` calls `_retrieve_path`, then `_llm_path`. Retrieval writes `started`, runs `retrieve_evidence`, and its completed line includes `chunk_ids` and `chunk_count`. `_llm_path` writes `started` with `chunk_count`, runs `call_llm`, parses the reply with `_summary`, and its completed line includes `elapsed_ms` and `missing_count`. `_messages` builds the prompt inside `_llm_path`. The ticket text, the prompt, the article text, and the summary stay out of every line.

## How process_ticket finishes

`process_ticket` records `perf_counter()` and writes `service` `workflow`, `event` `started`, before `_accept`. A rejected request writes `event` `completed`, `terminal_status` `input_rejected`, and `elapsed_ms`, then returns the rejected package with this `trace_id`. An exception from `_run` writes `event` `failed`, `terminal_status` `workflow_failed`, and `elapsed_ms`, and the error text is "a workflow service failed". A clean run writes `event` `completed`, `terminal_status` `summary_ready_for_review`, and `elapsed_ms`. That return passes the route, the original body, the summary, and the evidence into `_package`. Every package carries the same `trace_id`.

## Program

```python
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from time import perf_counter
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from hw_6.Task2.routing_service import DEPARTMENTS, RoutingService
from hw_6.Task3.retrieval_service import RetrievalService
from hw_6.Task4.llm_service import LLMClient
from shared.classes.indexed_trace_logger import IndexedTraceLogger

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
    if any(
        not isinstance(data[key], str) or not data[key].strip()
        for key in ("summary", "customer_request")
    ):
        raise RuntimeError("summary text is empty")
    missing = data["missing_information"]
    if not isinstance(missing, list) or any(
        not isinstance(item, str) or not item.strip() for item in missing
    ):
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


def _package(
    ticket_id,
    record_id,
    trace_id,
    status,
    error,
    route=None,
    body=None,
    summary=None,
    evidence=None,
):
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

    def _route_path(self, body, trace_id):
        started = perf_counter()
        self._record(trace_id, service="routing", event="started")
        try:
            result = self._routing.route_ticket({"body": body})
        except Exception:
            elapsed_ms = int((perf_counter() - started) * 1000)
            self._record(
                trace_id, service="routing", event="failed", elapsed_ms=elapsed_ms
            )
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

    def _retrieve_path(self, body, trace_id):
        started = perf_counter()
        self._record(trace_id, service="retrieval", event="started")
        try:
            found = self._retrieval.retrieve_evidence({"body": body})
        except Exception:
            elapsed_ms = int((perf_counter() - started) * 1000)
            self._record(
                trace_id, service="retrieval", event="failed", elapsed_ms=elapsed_ms
            )
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

    def _llm_path(self, body, evidence, trace_id):
        started = perf_counter()
        self._record(
            trace_id, service="llm", event="started", chunk_count=len(evidence)
        )
        try:
            reply = self._llm.call_llm(
                {
                    "messages": _messages(body, evidence),
                    "model": MODEL,
                    "options": OPTIONS,
                    "schema": SCHEMA,
                }
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

    def _summarize_path(self, body, trace_id):
        evidence = self._retrieve_path(body, trace_id)
        summary = self._llm_path(body, evidence, trace_id)
        return summary, evidence

    def _run(self, body, trace_id):
        with ThreadPoolExecutor(max_workers=2) as pool:
            # Submit both paths before waiting, so they run at the same time.
            route_future = pool.submit(self._route_path, body, trace_id)
            summary_future = pool.submit(self._summarize_path, body, trace_id)
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
        trace_id = self._logger.generate_trace_id()
        started = perf_counter()
        self._record(trace_id, service="workflow", event="started")
        ticket_id, body, reject = _accept(request)
        if reject:
            elapsed_ms = int((perf_counter() - started) * 1000)
            self._record(
                trace_id,
                service="workflow",
                event="completed",
                terminal_status="input_rejected",
                elapsed_ms=elapsed_ms,
            )
            return _package(ticket_id, record_id, trace_id, "input_rejected", reject)
        try:
            route, summary, evidence = self._run(body, trace_id)
        except RuntimeError as exc:
            elapsed_ms = int((perf_counter() - started) * 1000)
            cause = exc.__cause__ or exc
            self._record(
                trace_id,
                service="workflow",
                event="failed",
                terminal_status="workflow_failed",
                elapsed_ms=elapsed_ms,
                error_type=type(cause).__name__,
            )
            return _package(
                ticket_id,
                record_id,
                trace_id,
                "workflow_failed",
                "a workflow service failed",
            )
        elapsed_ms = int((perf_counter() - started) * 1000)
        self._record(
            trace_id,
            service="workflow",
            event="completed",
            terminal_status="summary_ready_for_review",
            elapsed_ms=elapsed_ms,
        )
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
```
