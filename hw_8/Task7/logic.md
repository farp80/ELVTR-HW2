# Task 7 — Test traces and metrics separately

## Goal

One test file runs two tests against the running app from Task 6.

The trace test sends one ticket, then reads its traces. The events must be in the right order and carry the same `trace_id` and a UTC timestamp. They must not contain the ticket text. An unknown id must return `[]`.

The metric test sends three tickets. For each metric, it downloads every saved result and every trace, works out the expected value with the same formula as Task 6, and compares it to the API. It then repeats this with `start` and `end` chosen to leave out the earliest timestamp.

## Step 1 — Create the folder and the test file

Create `hw_8\Task7`. Create `hw_8\Task7\test_monitoring.py` and paste the code from the Logic section below.

The test imports `metrics.py` from `hw_8\Task6`, so the expected values use the exact formulas the API uses. It reads ticket text from `hw_2\Fidel Alejandro Rosell Perez - support_tickets.csv`.

## Step 2 — Install requests

Run this once in PowerShell. It installs the HTTP library the test uses:

```text
python -m pip install requests==2.34.2
```

## Step 3 — Start the app from Task 6

```text
cd C:\Users\frosell\Downloads\ELVTR-HW2\hw_8\Task6
docker compose up --build -d
docker compose ps
```

Wait until all four services show `healthy`.

## Step 4 — Run the tests

```text
cd C:\Users\frosell\Downloads\ELVTR-HW2\hw_8\Task7
python test_monitoring.py
```

A passing run prints four lines:

```text
trace capture: passed
median_workflow_ms: all=... window=... passed
workflow_failure_rate: all=... window=... passed
routing_review_rate: all=... window=... passed
```

Any failed check stops the run with an `AssertionError` that names the check. The model takes time on each ticket, so the run can take a few minutes.

## Step 5 — What the trace test checks

`test_trace_capture` checks these points in order:

1. The first event is `workflow started`.
2. The last event is `workflow` with `summary_ready_for_review`.
3. The event before it is `routing_review`, and its flag matches the result.
4. Routing, retrieval, and the LLM each start before they complete.
5. Retrieval completes before the LLM starts.
6. Routing completes before the review step.
7. Every event has this `trace_id` and a valid UTC timestamp.
8. No event has a private field name, and no event contains the ticket text.
9. An unknown trace id returns an empty array.

## Step 6 — What the metric test checks

`check_metric` runs once per metric:

1. It reads the metric with no window.
2. It downloads all saved results from `GET /tickets`, and the traces of each result from `GET /ops/traces`. Tickets from earlier tasks are included.
3. It computes the expected value and compares it to the API value.
4. It sorts the timestamps this metric uses. `start` is the second one and `end` is the last one, so the earliest one is left out.
5. It reads the metric with that window, computes the expected value for the same window, and compares again.

`same` treats two `null` values as equal. It allows a rounding difference of 0.000000001.

## Step 7 — Stop the app

```text
cd C:\Users\frosell\Downloads\ELVTR-HW2\hw_8\Task6
docker compose down
```

The `record-store` and `workflow-traces` volumes keep their data.

## Logic

```python
import csv
import math
import os
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "Task6"))

from metrics import median_workflow_ms, parse_time, routing_review_rate, workflow_failure_rate

ROOT = HERE.parents[1]
DATASET = ROOT / "hw_2" / "Fidel Alejandro Rosell Perez - support_tickets.csv"
BASE = os.environ.get("WORKFLOW_URL", "http://localhost:8000")
PRIVATE = {
    "api_key",
    "body",
    "content",
    "credentials",
    "customer_request",
    "messages",
    "missing_information",
    "password",
    "prompt",
    "prompts",
    "reasoning",
    "retrieved_content",
    "summary",
    "ticket_body",
    "ticket_summary",
    "ticket_text",
}
FORMULAS = {
    "median_workflow_ms": median_workflow_ms,
    "workflow_failure_rate": workflow_failure_rate,
    "routing_review_rate": routing_review_rate,
}


def load_tickets(limit):
    rows = []
    with DATASET.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["Body"].strip():
                rows.append((int(row["ticket_id"]), row["Body"]))
            if len(rows) == limit:
                return rows
    raise AssertionError("not enough tickets in the dataset")


def post_ticket(ticket_id, body):
    response = requests.post(
        f"{BASE}/tickets/process",
        json={"ticket_id": ticket_id, "Body": body},
        timeout=600,
    )
    response.raise_for_status()
    return response.json()


def get_traces(trace_id):
    response = requests.get(f"{BASE}/ops/traces", params={"trace_id": trace_id}, timeout=30)
    response.raise_for_status()
    return response.json()


def get_metric(name, start=None, end=None):
    params = {}
    if start is not None:
        params["start"] = start
    if end is not None:
        params["end"] = end
    response = requests.get(f"{BASE}/ops/metrics/{name}", params=params, timeout=30)
    response.raise_for_status()
    return response.json()["value"]


def contains_text(value, text):
    if isinstance(value, str):
        return text in value
    if isinstance(value, dict):
        return any(contains_text(item, text) for item in value.values())
    if isinstance(value, list):
        return any(contains_text(item, text) for item in value)
    return False


def position(events, service, name):
    hits = [
        index
        for index, event in enumerate(events)
        if event.get("service") == service and event.get("event") == name
    ]
    assert len(hits) == 1, f"expected one {service} {name} event"
    return hits[0]


def test_trace_capture():
    ticket_id, body = load_tickets(1)[0]
    result = post_ticket(ticket_id, body)
    assert result["terminal_status"] == "summary_ready_for_review"
    trace_id = result["trace_id"]
    events = get_traces(trace_id)

    assert events[0]["service"] == "workflow" and events[0]["event"] == "started"
    assert events[-1]["service"] == "workflow"
    assert events[-1]["terminal_status"] == "summary_ready_for_review"
    assert events[-2]["service"] == "routing_review"
    assert events[-2]["requires_routing_review"] == result["requires_routing_review"]
    for service in ("routing", "retrieval", "llm"):
        assert position(events, service, "started") < position(events, service, "completed")
    assert position(events, "retrieval", "completed") < position(events, "llm", "started")
    assert position(events, "routing", "completed") < position(events, "routing_review", "completed")
    assert all(event["trace_id"] == trace_id for event in events)
    assert all(parse_time(event["timestamp"]) for event in events)
    assert all(PRIVATE.isdisjoint(event) for event in events)
    assert not any(contains_text(event, body) for event in events)

    assert get_traces("00000000-0000-4000-8000-000000000000") == []
    print("trace capture: passed")


def saved_data():
    response = requests.get(f"{BASE}/tickets", timeout=30)
    response.raise_for_status()
    records = response.json()
    events = []
    for record in records:
        events.extend(get_traces(record["trace_id"]))
    return records, events


def same(actual, expected):
    if actual is None or expected is None:
        assert actual is expected, (actual, expected)
    else:
        assert math.isclose(actual, expected, abs_tol=1e-9), (actual, expected)


def used_timestamps(name, records, events):
    if name == "median_workflow_ms":
        return [
            event["timestamp"]
            for event in events
            if event.get("service") == "workflow" and "elapsed_ms" in event
        ]
    if name == "workflow_failure_rate":
        return [
            event["timestamp"]
            for event in events
            if event.get("service") == "workflow"
            and event.get("terminal_status") in ("workflow_failed", "summary_ready_for_review")
        ]
    closing = {
        event["trace_id"]: event["timestamp"]
        for event in events
        if event.get("service") == "workflow" and "terminal_status" in event
    }
    return [closing[record["trace_id"]] for record in records if record["trace_id"] in closing]


def check_metric(name):
    records, events = saved_data()
    formula = FORMULAS[name]

    actual = get_metric(name)
    expected = formula(records, events, None, None)
    same(actual, expected)

    stamps = sorted(set(used_timestamps(name, records, events)))
    assert len(stamps) >= 2, "need at least two timestamps to leave one out"
    start, end = stamps[1], stamps[-1]
    actual_window = get_metric(name, start, end)
    expected_window = formula(records, events, parse_time(start), parse_time(end))
    same(actual_window, expected_window)
    print(f"{name}: all={actual} window={actual_window} passed")


def test_metrics():
    for ticket_id, body in load_tickets(3):
        post_ticket(ticket_id, body)
    for name in FORMULAS:
        check_metric(name)


if __name__ == "__main__":
    test_trace_capture()
    test_metrics()
```
