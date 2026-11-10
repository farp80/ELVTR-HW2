import csv
import json
import math
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "hw_2" / "Fidel Alejandro Rosell Perez - support_tickets.csv"
RESULT = Path(__file__).resolve().with_name("ticket_28763_result.json")
URL = "http://localhost:8000/tickets/process"
KEYS = (
    "ticket_id",
    "workflow_record_id",
    "terminal_status",
    "recommended_department",
    "class_scores",
    "ticket_body",
    "ticket_summary",
    "retrieved_evidence",
    "trace_id",
    "error",
)
DEPARTMENTS = {
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
}
SUMMARY_FIELDS = {"summary", "customer_request", "missing_information"}
EVIDENCE_FIELDS = {"rank", "chunk_id", "distance", "content", "metadata"}


def load_body():
    with DATASET.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row["ticket_id"] == "28763":
                return row["Body"]
    raise AssertionError("ticket 28763 is not in the dataset")


def test_ticket_28763():
    body = load_body()
    response = requests.post(
        URL,
        json={"ticket_id": 28763, "Body": body},
        timeout=600,
    )
    response.raise_for_status()
    result = response.json()
    RESULT.write_text(json.dumps(result, indent=2), encoding="utf-8")

    assert set(result) == set(KEYS)
    assert result["ticket_body"] == body
    assert result["ticket_id"] == 28763
    assert result["terminal_status"] == "summary_ready_for_review"
    assert result["error"] is None
    assert isinstance(result["workflow_record_id"], str) and result["workflow_record_id"]
    assert isinstance(result["trace_id"], str) and result["trace_id"]
    assert result["recommended_department"] in DEPARTMENTS

    scores = result["class_scores"]
    assert isinstance(scores, dict) and set(scores) == DEPARTMENTS
    assert all(
        not isinstance(score, bool)
        and isinstance(score, (int, float))
        and math.isfinite(score)
        for score in scores.values()
    )
    assert max(scores, key=scores.get) == result["recommended_department"]

    summary = result["ticket_summary"]
    assert isinstance(summary, dict) and set(summary) == SUMMARY_FIELDS
    assert isinstance(summary["summary"], str) and summary["summary"].strip()
    assert isinstance(summary["customer_request"], str) and summary["customer_request"].strip()
    assert isinstance(summary["missing_information"], list)
    assert all(isinstance(item, str) and item.strip() for item in summary["missing_information"])

    evidence = result["retrieved_evidence"]
    assert isinstance(evidence, list)
    assert all(isinstance(hit, dict) and EVIDENCE_FIELDS <= set(hit) for hit in evidence)


if __name__ == "__main__":
    test_ticket_28763()
