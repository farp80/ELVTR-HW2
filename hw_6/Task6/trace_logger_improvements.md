# Trace logger improvements

## Decision

`IndexedTraceLogger` subclasses the supplied `TraceLogger`. `record` still writes one JSON object per line, with the same timestamp and the same caller fields. `read_trace` still returns those rows in file order. The supplied `test_trace_logger.py` passes when its `logger_type` is this subclass.

Save the program below as `shared/classes/indexed_trace_logger.py`. The supplied `trace_logger.py` lives in `shared/utils/`.

## Where the workflow constructs it

`TicketWorkflow.__init__` is the only line that creates a logger. In `hw_6/Task6/logic.md` that line is `self._logger = IndexedTraceLogger(log_path)`, and the import is `from shared.classes.indexed_trace_logger import IndexedTraceLogger`.

`process_ticket` then calls `self._logger.generate_trace_id()`. `_record` calls `self._logger.record(trace_id, **fields)`. Both methods are the supplied methods. The subclass adds the index, the lock, and the private-field check inside `record` and `read_trace`. No other line in `workflow.py` names a logger class.

When the process finishes, call `self._logger.close()`. The supplied `close` flushes the file and releases the handle.

The submitted `workflow.py` constructs this subclass. The object is a `TraceLogger`, and the supplied `record` method writes every line. `trace_logger.py` stays the parent class.

## How the index works

`read_trace` in the supplied class opens the whole log on every lookup. The comment in that method says the scan is acceptable for this homework. The subclass keeps that first scan, then stores the rows in `self._index`, a dictionary whose key is `trace_id`.

`record` builds the same dictionary the parent writes. It fills the caller fields, sets `timestamp`, then sets `trace_id`, so those two keys win when the caller also sent them. A missing timestamp becomes the UTC time with milliseconds. An empty timestamp stays empty. The method passes that timestamp into `TraceLogger.record`, which appends the line. After that write succeeds, the subclass stores a JSON copy of the same dictionary under the trace id.

The first `read_trace` flushes the file, scans every line once, and fills the dictionary from the file. Later lookups return copies of the stored rows. A `record` that happens before the first lookup is picked up by that scan. A `record` that happens after the scan appends to the dictionary, so the next lookup includes it.

## How the lock works

Routing and retrieval call `record` on two threads. The subclass takes `self._lock` around the parent write and the index update. `read_trace` takes the same lock around the scan and the lookup. One call finishes its file line and its dictionary update before the next call starts. The list for a trace id grows in the same order as the lines in the file.

## How private fields are refused

`record` checks the caller fields before it writes. The blocked names are `body`, `ticket_body`, `ticket_text`, `prompt`, `prompts`, `messages`, `content`, `retrieved_content`, `summary`, `ticket_summary`, `customer_request`, `missing_information`, `credentials`, `password`, `api_key`, and `reasoning`. One of those names raises `ValueError` and the file stays unchanged. A blank `trace_id` raises `ValueError` as well.

The supplied tests pass `component`, `event`, `elapsed_ms`, `retrieved_chunk_ids`, `details`, and `custom_measurement`. Those names are written. The workflow lines use `service`, `chunk_ids`, `recommended_department`, `terminal_status`, and `elapsed_ms`, and those names are written too.

## Why the log stays one file

The class opens the path in append mode and leaves every line in that file. `read_trace` and the supplied tests treat that path as the full history. `close` flushes the handler and releases the file. The context manager calls `close` on the way out. A finished process calls `close` the same way.

## Program

```python
import json
import threading
from datetime import datetime, timezone

from shared.utils.trace_logger import TraceLogger

BLOCKED_FIELDS = frozenset({
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
})


class IndexedTraceLogger(TraceLogger):
    def __init__(self, log_path):
        super().__init__(log_path)
        self._lock = threading.Lock()
        self._index = None

    def record(self, trace_id, timestamp=None, **fields):
        blocked = BLOCKED_FIELDS.intersection(fields)
        if blocked:
            raise ValueError("trace record contains a private field")
        if not isinstance(trace_id, str) or not trace_id:
            raise ValueError("trace_id must be a non-empty string")
        if timestamp is None:
            timestamp = (
                datetime.now(timezone.utc)
                .isoformat(timespec="milliseconds")
                .replace("+00:00", "Z")
            )
        stored = dict(fields)
        stored["timestamp"] = timestamp
        stored["trace_id"] = trace_id
        with self._lock:
            super().record(trace_id, timestamp=timestamp, **fields)
            if self._index is not None:
                self._index.setdefault(trace_id, []).append(
                    json.loads(json.dumps(stored))
                )

    def read_trace(self, trace_id):
        with self._lock:
            if self._index is None:
                self._handler.flush()
                self._index = self._scan()
            rows = self._index.get(trace_id, [])
            return [json.loads(json.dumps(row)) for row in rows]

    def _scan(self):
        grouped = {}
        with self.log_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    record = json.loads(line)
                except json.JSONDecodeError as error:
                    raise ValueError(
                        f"Invalid JSON in trace log at line {line_number}."
                    ) from error
                if not isinstance(record, dict):
                    raise ValueError(
                        f"Trace log line {line_number} must contain a JSON object."
                    )
                grouped.setdefault(record.get("trace_id"), []).append(record)
        return grouped
```
