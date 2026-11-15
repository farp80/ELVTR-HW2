# Task 4 — List tickets and apply a human route

## Goal

Two new endpoints go in `workflow_api.py`.

`GET /tickets` returns the saved results. Two optional filters narrow the list. `requires_routing_review` accepts only `true` or `false`. `department` uses `human_reviewed_route` when a person set it, and `recommended_department` otherwise.

`POST /tickets/{workflow_record_id}/routing-review` stores a person's department. It sets `human_reviewed_route` and turns `requires_routing_review` to `false`. Nothing else in the record changes, so `ticket_body` stays as saved. A bad request fails before anything is written.

## Step 1 — Create the folder

Create `hw_8\Task4`. Copy everything from `hw_8\Task3` into it except `logic.md`, the `router` folder, the `retrieval` folder, and any `__pycache__` folder. That includes `compose.yaml` and `workflow_record_store.py`.

Open `hw_8\Task4\compose.yaml`. Change the two service builds so they point to the one copy in Task 3:

```yaml
  router:
    build: ../Task3/router
```

```yaml
  retrieval:
    build: ../Task3/retrieval
```

Leave the rest of the file unchanged.

## Step 2 — Replace workflow_api.py

Open `hw_8\Task4\workflow_api.py`. Delete everything in it. Paste the code from the Logic section below. The file keeps `/health` and `/tickets/process` from Homework 7 and adds the two new routes. No other file changes in this task.

## Step 3 — What each part does

`effective_department` returns the human route when it is set. Otherwise it returns the model's route.

`filter_tickets` rejects any `requires_routing_review` value other than `true` or `false`. It then keeps the records whose flag matches. Last, it keeps the records whose effective department matches.

`submit_review` checks the request in this order:

1. The body must have exactly one key, `human_reviewed_route`. Otherwise it returns 400.
2. The value must be one of the ten departments. Otherwise it returns 400.
3. The store looks up the record. An unknown id returns 404. A malformed id, a failed record, or a rejected record returns 400.

The store writes only after all three checks pass. A failed request leaves the file unchanged.

## Step 4 — Rebuild and start

```text
cd C:\Users\frosell\Downloads\ELVTR-HW2\hw_8\Task4
docker compose up --build -d
docker compose ps
```

Wait until all four services show `healthy`. Records saved in Task 3 are still there, because the `record-store` volume is reused.

## Step 5 — Test listing

Send one ticket, then list the tickets four ways:

```text
Invoke-RestMethod -Method Post -Uri http://localhost:8000/tickets/process -ContentType "application/json" -Body '{"ticket_id": 2, "Body": "My laptop will not connect to the VPN."}'
Invoke-RestMethod "http://localhost:8000/tickets"
Invoke-RestMethod "http://localhost:8000/tickets?requires_routing_review=true"
Invoke-RestMethod "http://localhost:8000/tickets?department=IT%20Support"
Invoke-RestMethod "http://localhost:8000/tickets?requires_routing_review=false&department=IT%20Support"
```

`%20` is a space in a URL.

## Step 6 — Test a review

Copy a `workflow_record_id` from a result whose `terminal_status` is `summary_ready_for_review`. Put it in place of `<ID>`:

```text
Invoke-RestMethod -Method Post -Uri http://localhost:8000/tickets/<ID>/routing-review -ContentType "application/json" -Body '{"human_reviewed_route": "Billing and Payments"}'
```

The reply shows `human_reviewed_route` as `Billing and Payments` and `requires_routing_review` as `false`. `ticket_body` is unchanged. Now send `{"human_reviewed_route": "Nope"}`. It returns 400, and listing the tickets shows the record did not change. Try the id of a rejected record too. It also returns 400.

## Step 7 — Stop

```text
docker compose down
```

## Logic

```python
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
    if requires_routing_review is not None and requires_routing_review not in ("true", "false"):
        raise ValueError("requires_routing_review must be true or false")
    chosen = records
    if requires_routing_review is not None:
        flag = requires_routing_review == "true"
        chosen = [record for record in chosen if record.get("requires_routing_review") is flag]
    if department is not None:
        chosen = [record for record in chosen if effective_department(record) == department]
    return chosen


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tickets/process")
def process_ticket(request: dict):
    return workflow.process_ticket(request)


@app.get("/tickets")
def list_tickets(requires_routing_review: str | None = None, department: str | None = None):
    try:
        return filter_tickets(workflow.store.list_records(), requires_routing_review, department)
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
```
