import os

from fastapi import FastAPI, HTTPException
from routing_client import DEPARTMENTS
from workflow import TicketWorkflow

workflow = TicketWorkflow(os.environ.get("LOG_PATH", "/logs/workflow_trace.jsonl"))
app = FastAPI()


def effective_department(record):
    reviewed = record.get("human_reviewed_route")
    if reviewed is not None:
        return reviewed
    return record.get("recommended_department")


def filter_tickets(records, requires_routing_review=None, department=None):
    if requires_routing_review is not None and requires_routing_review not in (
        "true",
        "false",
    ):
        raise ValueError("requires_routing_review must be true or false")
    chosen = records
    if requires_routing_review is not None:
        flag = requires_routing_review == "true"
        chosen = [
            record for record in chosen if record.get("requires_routing_review") is flag
        ]
    if department is not None:
        chosen = [
            record for record in chosen if effective_department(record) == department
        ]
    return chosen


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tickets/process")
def process_ticket(request: dict):
    return workflow.process_ticket(request)


@app.get("/tickets")
def list_tickets(
    requires_routing_review: str | None = None, department: str | None = None
):
    try:
        return filter_tickets(
            workflow.store.list_records(), requires_routing_review, department
        )
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc


@app.post("/tickets/{workflow_record_id}/routing-review")
def submit_review(workflow_record_id: str, request: dict):
    if set(request) != {"human_reviewed_route"}:
        raise HTTPException(400, "body must contain human_reviewed_route only")
    route = request["human_reviewed_route"]
    if route not in DEPARTMENTS:
        raise HTTPException(400, "human_reviewed_route must be an allowed department")
    try:
        return workflow.store.update_routing_review(workflow_record_id, route)
    except KeyError as exc:
        raise HTTPException(404, "workflow record was not found") from exc
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
