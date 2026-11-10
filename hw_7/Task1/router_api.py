from pathlib import Path
from fastapi import FastAPI, HTTPException
from routing_service import RoutingService

service = RoutingService(Path("/app/model/hw4_candidate.pkl"))
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/route")
def route(request: dict):
    try:
        return service.route_ticket(request)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(500, str(exc)) from exc
