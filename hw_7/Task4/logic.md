# Task 4 — Workflow container

## Steps — calls

Follow `WEEK_7_ASSIGNMENT.md` Task 4, `hw_6/Task6/workflow.py`, `hw_6/Task1/routing_contract.md`, `hw_6/Task1/retrieval_contract.md`, `hw_6/Task1/llm_contract.md`, `hw_6/Task4/llm_service.py`, and `Fidel Alejandro Rosell Perez - ollama_container_config.md`.

1. Copy `shared/utils/trace_logger.py` and `shared/classes/indexed_trace_logger.py`. Add empty `__init__.py` files in `shared`, `shared/utils`, and `shared/classes`. `hw_6/Task6/workflow.py` imports `IndexedTraceLogger` from that path.
2. Save `routing_client.py` and `retrieval_client.py`. `WEEK_7_ASSIGNMENT.md` replaces the in-process routing and retrieval calls with HTTP. POST `{"body": body}` to `ROUTER_URL/route` and `RETRIEVAL_URL/search`. Check the JSON with the two contracts. Raise `RuntimeError` on a failed call. `hw_6/WORKFLOW_CONTRACT.md` records that failure as `workflow_failed`.
3. Save `llm_service.py` from `hw_6/Task4/llm_service.py`. Read `OLLAMA_URL` and post to `/api/chat`, the path in `llm_contract.md` and `ollama_container_config.md`.

## Steps — workflow image

Follow `hw_6/Task6/workflow.py`, `hw_6/WORKFLOW_CONTRACT.md`, `example_http_service/example_http_wrapper.py`, `example_docker_setup/api/Dockerfile`, and `WEEK_7_ASSIGNMENT.md` Task 4.

4. Save `workflow.py` from `hw_6/Task6/workflow.py`. Keep `SYSTEM`, `_summary`, the two-thread executor, the trace lines, and the ten contract fields. Build the two clients and `LLMClient` from `ROUTER_URL`, `RETRIEVAL_URL`, and `OLLAMA_URL`. Write the log to `LOG_PATH`.
5. Save `workflow_api.py` from `example_http_wrapper.py`. Keep `GET /health`. Add `POST /tickets/process`. Return the package with HTTP 200, including `input_rejected` and `workflow_failed`.
6. Save the Dockerfile from `example_docker_setup/api/Dockerfile`. Set `WORKDIR /app` and `LOG_PATH=/logs/workflow_trace.jsonl`. End with `uvicorn workflow_api:app` on `0.0.0.0:8000`. Mount a volume on `/logs`. Publish host port `8000`.

## requirements.txt

```text
fastapi==0.141.1
uvicorn==0.53.0
requests==2.34.2
```

## .dockerignore

```text
__pycache__
*.pyc
.venv
*.md
```

## routing_client.py

```python
import math

import requests

DEPARTMENTS = (
    "Billing and Payments",
    "Customer Service",
    "General Inquiry",
    "Human Resources",
    "IT Support",
    "Product Support",
    "Returns and Exchanges",
    "Sales and Pre-Sales",
    "Service Outages and Maintenance",
    "Technical Support",
)


def _post(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=60)
    except requests.RequestException as exc:
        raise RuntimeError("routing request failed") from exc
    if response.status_code == 400:
        raise ValueError("routing request was rejected")
    if response.status_code >= 400:
        raise RuntimeError("routing request failed")
    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError("routing response was not JSON") from exc
    return result


def _check(result):
    if not isinstance(result, dict):
        raise RuntimeError("routing response is missing required fields")
    department = result.get("recommended_department")
    scores = result.get("class_scores")
    if department not in DEPARTMENTS or not isinstance(scores, dict):
        raise RuntimeError("routing response is missing required fields")
    if set(scores) != set(DEPARTMENTS):
        raise RuntimeError("routing scores must cover every department")
    if any(
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(score)
        for score in scores.values()
    ):
        raise RuntimeError("routing scores must be finite numbers")
    if max(scores, key=scores.get) != department:
        raise RuntimeError("recommended department is not the top score")
    return {"recommended_department": department, "class_scores": scores}


class RoutingClient:
    def __init__(self, base_url):
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("router URL must be a non-empty string")
        self._url = base_url.rstrip("/") + "/route"

    def route_ticket(self, request):
        if not isinstance(request, dict) or not isinstance(request.get("body"), str):
            raise ValueError("routing request must include body")
        if not request["body"].strip():
            raise ValueError("routing body must contain text")
        return _check(_post(self._url, {"body": request["body"]}))
```

## retrieval_client.py

```python
import math

import requests

FIELDS = ("rank", "chunk_id", "distance", "content", "metadata")


def _post(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=120)
    except requests.RequestException as exc:
        raise RuntimeError("retrieval request failed") from exc
    if response.status_code == 400:
        raise ValueError("retrieval request was rejected")
    if response.status_code >= 400:
        raise RuntimeError("retrieval request failed")
    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError("retrieval response was not JSON") from exc
    return result


def _check(result):
    if not isinstance(result, dict) or not isinstance(result.get("evidence"), list):
        raise RuntimeError("retrieval did not return a list")
    hits = result["evidence"]
    for hit in hits:
        if not isinstance(hit, dict) or any(field not in hit for field in FIELDS):
            raise RuntimeError("retrieval row is missing a required field")
        distance = hit["distance"]
        if isinstance(distance, bool) or not isinstance(distance, (int, float)):
            raise RuntimeError("retrieval distance must be a number")
        if not math.isfinite(distance):
            raise RuntimeError("retrieval distance must be finite")
    return hits


class RetrievalClient:
    def __init__(self, base_url):
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("retrieval URL must be a non-empty string")
        self._url = base_url.rstrip("/") + "/search"

    def retrieve_evidence(self, request):
        if not isinstance(request, dict) or not isinstance(request.get("body"), str):
            raise ValueError("retrieval request must include body")
        if not request["body"].strip():
            raise ValueError("retrieval body must contain text")
        return {"evidence": _check(_post(self._url, {"body": request["body"]}))}
```

## llm_service.py

```python
import requests


def _request(request):
    if not isinstance(request, dict):
        raise ValueError("LLM request must be a dictionary")
    messages = request.get("messages")
    model = request.get("model")
    options = request.get("options")
    if not isinstance(messages, list) or not messages:
        raise ValueError("LLM messages must be a non-empty list")
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("each LLM message must be an object")
        if not isinstance(message.get("role"), str) or not isinstance(message.get("content"), str):
            raise ValueError("each LLM message needs a role and content")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("LLM model must be a non-empty string")
    if not isinstance(options, dict):
        raise ValueError("LLM options must be an object")
    schema = request.get("schema")
    if schema is not None and not isinstance(schema, dict):
        raise ValueError("LLM schema must be an object or omitted")
    return messages, model, options, schema


class LLMClient:
    def __init__(self, url):
        if not isinstance(url, str) or not url.strip():
            raise ValueError("Ollama URL must be a non-empty string")
        self._url = url

    def call_llm(self, request):
        messages, model, options, schema = _request(request)
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options,
        }
        if schema is not None:
            payload["format"] = schema
        try:
            response = requests.post(self._url, json=payload, timeout=600)
            response.raise_for_status()
            content = response.json()["message"]["content"]
        except Exception as exc:
            raise RuntimeError("LLM call failed") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("LLM returned no content")
        return {"content": content}
```

## workflow.py

```python
import json
import os
from concurrent.futures import ThreadPoolExecutor
from time import perf_counter
from uuid import uuid4

from llm_service import LLMClient
from retrieval_client import RetrievalClient
from routing_client import DEPARTMENTS, RoutingClient
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


def _required_url(name):
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name} must be set")
    return value


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
    def __init__(self, log_path):
        self._routing = RoutingClient(_required_url("ROUTER_URL"))
        self._retrieval = RetrievalClient(_required_url("RETRIEVAL_URL"))
        self._llm = LLMClient(_required_url("OLLAMA_URL"))
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
            route_future = pool.submit(self._route_path, body, trace_id)
            summary_future = pool.submit(self._summarize_path, body, trace_id)
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

## workflow_api.py

```python
import os

from fastapi import FastAPI

from workflow import TicketWorkflow

workflow = TicketWorkflow(os.environ.get("LOG_PATH", "/logs/workflow_trace.jsonl"))
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tickets/process")
def process_ticket(request: dict):
    return workflow.process_ticket(request)
```

## Dockerfile

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV LOG_PATH=/logs/workflow_trace.jsonl
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY workflow_api.py workflow.py routing_client.py retrieval_client.py llm_service.py ./
COPY shared ./shared
EXPOSE 8000
CMD ["uvicorn", "workflow_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Run this container by itself

Start Task 1, Task 2, and Task 3 first. From inside this container, `localhost` is the container, not your machine. `host.docker.internal` is the machine where those three ports are published.

```text
docker volume create homework7_traces
docker build -t homework7-workflow .
docker run -d --name homework7-workflow -p 8000:8000 -e ROUTER_URL=http://host.docker.internal:8001 -e RETRIEVAL_URL=http://host.docker.internal:8002 -e OLLAMA_URL=http://host.docker.internal:8003/api/chat -e LOG_PATH=/logs/workflow_trace.jsonl -v homework7_traces:/logs homework7-workflow
```

`http://localhost:8000/health` returns `{"status": "ok"}`. A POST to `http://localhost:8000/tickets/process` with `ticket_id` and `Body` returns the ten-field package. The trace file is `/logs/workflow_trace.jsonl` inside the volume.

```text
docker stop homework7-workflow
docker rm homework7-workflow
```
