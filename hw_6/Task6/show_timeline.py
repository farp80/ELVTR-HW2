"""Print the timeline of one workflow request from workflow_trace.jsonl.

Usage:  python show_timeline.py [trace_id]
Without a trace_id, the most recent request in the log is shown.
"""

import json
import sys
from datetime import datetime
from pathlib import Path

LOG = Path(__file__).resolve().parent / "workflow_trace.jsonl"


def _time(row):
    return datetime.fromisoformat(row["timestamp"])


def main():
    rows = [json.loads(line) for line in LOG.read_text(encoding="utf-8").splitlines()]
    trace_id = sys.argv[1] if len(sys.argv) > 1 else rows[-1]["trace_id"]
    rows = [row for row in rows if row["trace_id"] == trace_id]
    rows.sort(key=_time)
    t0 = _time(rows[0])

    print(f"trace_id {trace_id}")
    for row in rows:
        ms = (_time(row) - t0).total_seconds() * 1000
        print(f"+{ms:7.0f} ms  {row['service']:10} {row['event']:10}")

    def span(service):
        events = {r["event"]: _time(r) for r in rows if r["service"] == service}
        return events["started"], events.get("completed") or events["failed"]

    route_start, route_end = span("routing")
    sum_start, sum_end = span("retrieval")[0], span("llm")[1]
    overlap = (min(route_end, sum_end) - max(route_start, sum_start)).total_seconds() * 1000
    route_ms = (route_end - route_start).total_seconds() * 1000
    sum_ms = (sum_end - sum_start).total_seconds() * 1000
    total_ms = (_time(rows[-1]) - t0).total_seconds() * 1000

    print()
    print(f"routing path       {route_ms:7.0f} ms")
    print(f"summarization path {sum_ms:7.0f} ms")
    print(f"if sequential      {route_ms + sum_ms:7.0f} ms")
    print(f"actual total       {total_ms:7.0f} ms")
    print(f"paths overlapped   {max(overlap, 0):7.0f} ms")
    print("PARALLEL" if overlap > 0 else "NOT PARALLEL")


if __name__ == "__main__":
    main()
