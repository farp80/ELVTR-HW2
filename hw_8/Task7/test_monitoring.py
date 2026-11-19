"""Check Task 6 traces and metrics against the running app.

Start the Task 6 app first, then run:  python test_monitoring.py
"""

import csv
import math
import os
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "Task6"))

from metrics import (  # noqa: E402
    median_workflow_ms,
    parse_time,
    routing_review_rate,
    workflow_failure_rate,
)

ROOT = HERE.parents[1]
DATASET = ROOT / "hw_2" / "Fidel Alejandro Rosell Perez - support_tickets.csv"
BASE = os.environ.get("WORKFLOW_URL", "http://localhost:8000")
PRIVATE_FIELDS = {
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
    """Return the first tickets that have a body."""
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
    response = requests.get(
        f"{BASE}/ops/traces",
        params={"trace_id": trace_id},
        timeout=30,
    )
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


def find_event(events, service, name):
    hits = [
        index
        for index, event in enumerate(events)
        if event.get("service") == service and event.get("event") == name
    ]
    assert len(hits) == 1, f"expected one {service} {name} event"
    return hits[0]


def test_trace_capture():
    """Send one ticket and check that its trace events were saved in order."""
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
        assert find_event(events, service, "started") < find_event(events, service, "completed")
    assert find_event(events, "retrieval", "completed") < find_event(events, "llm", "started")
    assert find_event(events, "routing", "completed") < find_event(
        events, "routing_review", "completed"
    )
    assert all(event["trace_id"] == trace_id for event in events)
    assert all(parse_time(event["timestamp"]) for event in events)
    assert all(PRIVATE_FIELDS.isdisjoint(event) for event in events)
    assert not any(contains_text(event, body) for event in events)

    assert get_traces("00000000-0000-4000-8000-000000000000") == []
    print("trace capture: passed")


def saved_data():
    """Download every saved ticket and the trace events for each one."""
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
    """Return the times this metric actually counts."""
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
    """Send three tickets, then check each metric with and without a time window."""
    for ticket_id, body in load_tickets(3):
        post_ticket(ticket_id, body)
    check_metric("median_workflow_ms")
    check_metric("workflow_failure_rate")
    check_metric("routing_review_rate")


if __name__ == "__main__":
    test_trace_capture()
    test_metrics()
