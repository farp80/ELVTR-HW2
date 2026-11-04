import json
import threading
from datetime import datetime, timezone

from trace_logger import TraceLogger

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