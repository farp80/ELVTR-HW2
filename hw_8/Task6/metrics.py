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
    return not (end is not None and moment > end)


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
        and event.get("terminal_status")
        in ("workflow_failed", "summary_ready_for_review")
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
