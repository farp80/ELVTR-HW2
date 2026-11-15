"""Atomic JSON storage for complete ticket-preparation workflow results."""

from __future__ import annotations

import json
import os
from pathlib import Path
from tempfile import NamedTemporaryFile
from threading import RLock
from typing import Any
from uuid import UUID


# The Compose volume is mounted here. Tests can pass a different path to the store.
DEFAULT_RECORD_PATH = Path("/app/data/workflow_records.json")

# FastAPI may run synchronous endpoints in different threads. Keep each complete
# read-modify-write operation together within the workflow process.
_FILE_LOCK = RLock()


class WorkflowRecordStore:
    """Save, list, and update workflow results by workflow-record ID."""

    def __init__(
        self,
        record_path: str | Path = DEFAULT_RECORD_PATH,
    ) -> None:
        self.record_path = Path(record_path)
        self.record_path.parent.mkdir(parents=True, exist_ok=True)
        with _FILE_LOCK:
            # A new store starts as an empty JSON array.
            if not self.record_path.exists():
                self._write_records([])

    def save_record(self, record: dict[str, Any]) -> dict[str, Any]:
        """Save one complete workflow result without changing its fields."""
        # Copying through JSON verifies that the same value can be written to disk
        # and prevents later caller mutations from changing the stored record.
        # Content-bearing fields such as ticket_body are therefore preserved
        # exactly as supplied by the workflow or test seeding endpoint.
        saved_record = _copy_and_validate_record(record)
        workflow_record_id = saved_record["workflow_record_id"]

        with _FILE_LOCK:
            records = self._read_records()
            # Generated IDs should already be unique. Refuse to overwrite data if
            # a duplicate nevertheless reaches the storage boundary.
            if any(
                existing["workflow_record_id"] == workflow_record_id
                for existing in records
            ):
                raise ValueError(
                    f"Workflow record {workflow_record_id!r} already exists."
                )
            records.append(saved_record)
            self._write_records(records)
        return _copy_json(saved_record)

    def list_records(self) -> list[dict[str, Any]]:
        """Return all saved workflow results in insertion order."""
        with _FILE_LOCK:
            # Return copies so endpoint code cannot mutate persisted state directly.
            return _copy_json(self._read_records())

    def get_record(self, workflow_record_id: str) -> dict[str, Any]:
        _validate_workflow_record_id(workflow_record_id)
        with _FILE_LOCK:
            for record in self._read_records():
                if record["workflow_record_id"] == workflow_record_id:
                    return _copy_json(record)
        raise KeyError(f"Workflow record {workflow_record_id!r} was not found.")

    def delete_record(self, workflow_record_id: str, trace_id: str) -> None:
        """Remove a known record, verifying the trace identity used for cleanup."""
        _validate_workflow_record_id(workflow_record_id)
        if not isinstance(trace_id, str) or not trace_id.strip():
            raise ValueError("Stored workflow record has an invalid trace_id.")
        with _FILE_LOCK:
            records = self._read_records()
            matching = [
                record for record in records
                if record["workflow_record_id"] == workflow_record_id
            ]
            if not matching:
                raise KeyError(f"Workflow record {workflow_record_id!r} was not found.")
            if matching[0].get("trace_id") != trace_id:
                raise ValueError("Workflow record trace_id changed during deletion.")
            if any(
                record["workflow_record_id"] != workflow_record_id
                and record.get("trace_id") == trace_id
                for record in records
            ):
                raise ValueError("Another workflow record shares this trace_id.")
            self._write_records([
                record for record in records
                if record["workflow_record_id"] != workflow_record_id
            ])

    def update_routing_review(
        self,
        workflow_record_id: str,
        human_reviewed_route: str,
    ) -> dict[str, Any]:
        """Apply a validated human route to one successful workflow result."""
        _validate_workflow_record_id(workflow_record_id)
        if (
            not isinstance(human_reviewed_route, str)
            or not human_reviewed_route.strip()
        ):
            raise ValueError("human_reviewed_route must be a non-empty string.")

        with _FILE_LOCK:
            records = self._read_records()
            for record in records:
                if record["workflow_record_id"] == workflow_record_id:
                    if record.get("terminal_status") != "summary_ready_for_review":
                        raise ValueError(
                            "Only successful workflow records can be manually assigned."
                        )
                    # Apply the complete review state transition before replacing
                    # the file, so readers never see a partially updated record.
                    record["human_reviewed_route"] = human_reviewed_route
                    record["requires_routing_review"] = False
                    self._write_records(records)
                    return _copy_json(record)
        raise KeyError(f"Workflow record {workflow_record_id!r} was not found.")

    def _read_records(self) -> list[dict[str, Any]]:
        try:
            # The whole file is one JSON array because the assignment's data set is
            # intentionally small and students should not implement a database.
            stored_value = json.loads(
                self.record_path.read_text(encoding="utf-8")
            )
        except json.JSONDecodeError as error:
            raise ValueError("Workflow-record file contains invalid JSON.") from error

        if not isinstance(stored_value, list):
            raise ValueError("Workflow-record file must contain a JSON array.")

        records: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for index, record in enumerate(stored_value):
            try:
                # Validate every record while loading so corrupt data fails visibly.
                validated_record = _copy_and_validate_record(record)
            except ValueError as error:
                raise ValueError(
                    f"Workflow record at index {index} is invalid."
                ) from error
            workflow_record_id = validated_record["workflow_record_id"]
            if workflow_record_id in seen_ids:
                raise ValueError(
                    "Workflow-record file contains duplicate record IDs."
                )
            seen_ids.add(workflow_record_id)
            records.append(validated_record)
        return records

    def _write_records(self, records: list[dict[str, Any]]) -> None:
        # Write beside the real file and atomically replace it only after the full
        # JSON document succeeds. This avoids leaving a partial file after errors.
        temporary_path: Path | None = None
        try:
            with NamedTemporaryFile(
                "w",
                encoding="utf-8",
                dir=self.record_path.parent,
                delete=False,
            ) as temporary_file:
                temporary_path = Path(temporary_file.name)
                json.dump(
                    records,
                    temporary_file,
                    ensure_ascii=True,
                    allow_nan=False,
                    indent=2,
                )
                temporary_file.write("\n")
            os.replace(temporary_path, self.record_path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)


def _copy_and_validate_record(record: object) -> dict[str, Any]:
    # The adapter stays independent of the evolving workflow schema. It validates
    # only the JSON representation and the field used as persistent identity.
    if not isinstance(record, dict):
        raise ValueError("Workflow record must be a dictionary.")
    copied_record = _copy_json(record)
    _validate_workflow_record_id(copied_record.get("workflow_record_id"))
    return copied_record


def _copy_json(value: Any) -> Any:
    try:
        # A JSON round trip is both a serializability check and a simple deep copy.
        return json.loads(
            json.dumps(
                value,
                ensure_ascii=True,
                allow_nan=False,
                separators=(",", ":"),
            )
        )
    except (TypeError, ValueError) as error:
        raise ValueError("Stored values must be JSON-compatible.") from error


def _validate_workflow_record_id(workflow_record_id: object) -> None:
    # Workflow record IDs are generated UUID strings, not client-selected ticket
    # identifiers.
    if not isinstance(workflow_record_id, str) or not workflow_record_id:
        raise ValueError("workflow_record_id must be a non-empty UUID string.")
    try:
        UUID(workflow_record_id)
    except ValueError as error:
        raise ValueError(
            "workflow_record_id must be a non-empty UUID string."
        ) from error
