import os

from fastapi import FastAPI
from workflow import TicketWorkflow

workflow = TicketWorkflow(os.environ.get("LOG_PATH", "/logs/workflow_trace.jsonl"))
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/tickets/process")
def process_ticket(request: dict):
    return workflow.process_ticket(request)
