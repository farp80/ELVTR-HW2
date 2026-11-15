# Task 6 — Record the measurements and serve them

## Goal

The workflow already writes `elapsed_ms`, `terminal_status`, and a UTC `timestamp` on its closing trace event. This task adds one trace event for the review step. It also adds two endpoints: one returns the traces of a ticket, and one returns a metric from Task 5.

## Step 1 — Create the folder

Create `hw_8\Task6`. Copy everything from `hw_8\Task4` into it except `logic.md` and any `__pycache__` folder. That includes `compose.yaml`. Its router and retrieval builds already point to `../Task3/router` and `../Task3/retrieval`, which also work from `Task6`.

## Step 2 — Let the logger return every event

Open `hw_8\Task6\shared\classes\indexed_trace_logger.py`. Find this line:

```python
    def _scan(self):
```

Paste the `read_all` method right above it, with the same indentation:

```python
    def read_all(self):
        with self._lock:
            self._handler.flush()
            if self._index is None:
                self._index = self._scan()
            rows = []
            for group in self._index.values():
                rows.extend(json.loads(json.dumps(group)))
            return rows
```

`read_trace` returns the events of one ticket. `read_all` returns the events of every ticket. The metrics need all of them.

## Step 3 — Replace _process in workflow.py

Open `hw_8\Task6\workflow.py`. `_process` is the last method in the file. Select from `    def _process(self, request):` down to the end of the file and delete it. Paste the code from "Code for Step 3" at the end of this file.

The new code adds `_mark_review`. It writes one trace event with `service` set to `routing_review` just before the closing event. A successful ticket also stores `score_margin`, the gap from Task 1. Rejected and failed tickets store `requires_routing_review` as `false` with no margin.

`traces` and `events` let the API read the trace log without touching the logger directly.

## Step 4 — Add metrics.py

Create `hw_8\Task6\metrics.py`. Paste the code from "Code for Step 4".

- `parse_time` accepts only UTC strings that end in `Z`.
- `in_window` keeps a timestamp between `start` and `end`, and both ends count.
- Each metric takes the saved records, the trace events, `start`, and `end`, and returns a number or `None`.
- `METRICS` maps each URL name to its function.

## Step 5 — Add the two routes

Open `hw_8\Task6\workflow_api.py`. Find this line:

```python
from routing_client import DEPARTMENTS
```

Add this line right above it:

```python
from metrics import METRICS, parse_time
```

Then paste the code from "Code for Step 5" at the end of the file.

`/ops/traces` returns the events in the order they were written. An unknown id returns `[]`. `/ops/metrics/{metric_name}` returns `{"value": ...}`. An unknown name returns 404. A badly formatted `start` or `end` returns 400.

## Step 6 — Copy metrics.py into the image

Open `hw_8\Task6\Dockerfile`. Change the second `COPY` line to this:

```dockerfile
COPY workflow_api.py workflow.py routing_client.py retrieval_client.py llm_service.py routing_review.py workflow_record_store.py metrics.py ./
```

## Step 7 — Rebuild and start

```text
cd C:\Users\frosell\Downloads\ELVTR-HW2\hw_8\Task6
docker compose up --build -d
docker compose ps
```

Wait until all four services show `healthy`.

## Step 8 — Check the new endpoints

Send one ticket. Copy `trace_id` from the reply and put it in place of `<TRACE>`:

```text
Invoke-RestMethod -Method Post -Uri http://localhost:8000/tickets/process -ContentType "application/json" -Body '{"ticket_id": 3, "Body": "The website is down for everyone."}'
Invoke-RestMethod "http://localhost:8000/ops/traces?trace_id=<TRACE>"
Invoke-RestMethod "http://localhost:8000/ops/traces?trace_id=unknown"
Invoke-RestMethod "http://localhost:8000/ops/metrics/median_workflow_ms"
Invoke-RestMethod "http://localhost:8000/ops/metrics/workflow_failure_rate"
Invoke-RestMethod "http://localhost:8000/ops/metrics/routing_review_rate"
Invoke-RestMethod "http://localhost:8000/ops/metrics/median_workflow_ms?start=2026-01-01T00:00:00.000Z&end=2026-12-31T23:59:59.999Z"
```

The trace starts with `workflow started`, then the routing, retrieval, and LLM events. It ends with `routing_review completed` and `workflow completed`. The unknown id returns an empty array.

Leave the app running for Task 7.

## Code for Step 3

```python
    def _process(self, request):
        record_id = str(uuid4())
        trace_id = self._logger.generate_trace_id()
        started = perf_counter()
        self._record(trace_id, service="workflow", event="started")
        ticket_id, body, reject = _accept(request)
        if reject:
            self._mark_review(trace_id, False)
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
            self._mark_review(trace_id, False)
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
        needs, margin = review_decision(route["class_scores"])
        self._mark_review(trace_id, needs, margin)
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
            requires_routing_review=needs,
        )

    def _mark_review(self, trace_id, needs, margin=None):
        fields = {
            "service": "routing_review",
            "event": "completed",
            "requires_routing_review": needs,
        }
        if margin is not None:
            fields["score_margin"] = margin
        self._record(trace_id, **fields)

    def traces(self, trace_id):
        return self._logger.read_trace(trace_id)

    def events(self):
        return self._logger.read_all()
```

## Code for Step 4

```python
from datetime import datetime


def parse_time(value):
    if not isinstance(value, str) or not value.endswith("Z"):
        raise ValueError("timestamp must be UTC ISO 8601")
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("timestamp must be UTC ISO 8601") from exc


def in_window(stamp, start, end):
    moment = parse_time(stamp)
    if start is not None and moment < start:
        return False
    if end is not None and moment > end:
        return False
    return True


def median(values):
    ordered = sorted(values)
    count = len(ordered)
    if count == 0:
        return None
    mid = count // 2
    if count % 2:
        return ordered[mid]
    return (ordered[mid - 1] + ordered[mid]) / 2


def median_workflow_ms(records, events, start, end):
    values = [
        event["elapsed_ms"]
        for event in events
        if event.get("service") == "workflow"
        and "elapsed_ms" in event
        and in_window(event["timestamp"], start, end)
    ]
    return median(values)


def workflow_failure_rate(records, events, start, end):
    rows = [
        event
        for event in events
        if event.get("service") == "workflow"
        and event.get("terminal_status") in ("workflow_failed", "summary_ready_for_review")
        and in_window(event["timestamp"], start, end)
    ]
    if not rows:
        return None
    failed = sum(event["terminal_status"] == "workflow_failed" for event in rows)
    return failed / len(rows)


def routing_review_rate(records, events, start, end):
    closing = {}
    for event in events:
        if event.get("service") == "workflow" and "terminal_status" in event:
            closing[event["trace_id"]] = event["timestamp"]
    chosen = []
    for record in records:
        stamp = closing.get(record.get("trace_id"))
        if stamp is None:
            if start is None and end is None:
                chosen.append(record)
            continue
        if in_window(stamp, start, end):
            chosen.append(record)
    if not chosen:
        return None
    flagged = sum(record.get("requires_routing_review") is True for record in chosen)
    return flagged / len(chosen)


METRICS = {
    "median_workflow_ms": median_workflow_ms,
    "workflow_failure_rate": workflow_failure_rate,
    "routing_review_rate": routing_review_rate,
}
```

## Code for Step 5

```python
@app.get("/ops/traces")
def read_traces(trace_id: str):
    return workflow.traces(trace_id)


@app.get("/ops/metrics/{metric_name}")
def read_metric(metric_name: str, start: str | None = None, end: str | None = None):
    if metric_name not in METRICS:
        raise HTTPException(404, "unknown metric")
    try:
        start_at = parse_time(start) if start is not None else None
        end_at = parse_time(end) if end is not None else None
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    value = METRICS[metric_name](
        workflow.store.list_records(),
        workflow.events(),
        start_at,
        end_at,
    )
    return {"value": value}
```
