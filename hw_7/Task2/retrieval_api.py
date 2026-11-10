from pathlib import Path

from fastapi import FastAPI, HTTPException

from retrieval_service import RetrievalService

service = RetrievalService(Path("/app/data/lancedb"), top_k=5)
app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/search")
def search(request: dict):
    try:
        return service.retrieve_evidence(request)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(500, str(exc)) from exc
