# Task 2 — Retrieval container

## Steps — code

Follow `WEEK_7_ASSIGNMENT.md` Task 2, `hw_6/Task3/retrieval_service.py`, `hw_6/Task1/retrieval_contract.md`, `hw_5/Fidel Alejandro Rosell Perez - VectorStore.py`, `hw_5/Task4/lancedb`, and `example_http_service/example_http_wrapper.py`.

1. Copy `VectorStore.py` to `vector_store.py`. Copy `hw_5/Task4/lancedb` to `data/lancedb`. That folder holds `homework5_chunks.lance`. `WEEK_7_ASSIGNMENT.md` puts the service code and the saved store under `/app`.
2. Save `retrieval_service.py` from `hw_6/Task3/retrieval_service.py`. Import `VectorStore` from `vector_store`. Keep `top_k` at 5 and `retrieve_evidence` as `retrieval_contract.md` defines it. Create one service at startup.
3. Save `retrieval_api.py` from `example_http_wrapper.py`. Keep `GET /health` returning `{"status": "ok"}`. Use `POST /search` in place of `/items`. Return HTTP 400 for `ValueError` and HTTP 500 for `RuntimeError`.

## Steps — image

Follow `example_docker_setup/api/Dockerfile`, `Fidel Alejandro Rosell Perez - requirements.txt`, `VectorStore.py`, and the model rule in `WEEK_7_ASSIGNMENT.md` Task 2.

4. Save `requirements.txt` from those pins: `fastembed==0.8.0`, `lancedb==0.38.0`, `fastapi`, and `uvicorn`.
5. Save the Dockerfile from `example_docker_setup/api/Dockerfile`. Set `WORKDIR /app` and `HF_HOME=/app/models`. During the build, download the snapshot named in `VectorStore.py`: `qdrant/bge-small-en-v1.5-onnx-q` at revision `52398278842ec682c6f32300af41344b1c0b0bb2`. `WEEK_7_ASSIGNMENT.md` requires that model inside the image. Set `HF_HUB_OFFLINE=1` after the download.
6. Run `docker build -t homework7-retrieval .`, then `docker run -d --name homework7-retrieval -p 8002:8000 homework7-retrieval`. Host `8002` maps to container `8000`.

## requirements.txt

```text
fastembed==0.8.0
lancedb==0.38.0
fastapi==0.141.1
uvicorn==0.53.0
```

## .dockerignore

```text
__pycache__
*.pyc
.venv
*.md
```

## retrieval_service.py

```python
import math

from vector_store import VectorStore

FIELDS = ("rank", "chunk_id", "distance", "content", "metadata")


def _body(request):
    if not isinstance(request, dict) or "body" not in request:
        raise ValueError("retrieval request must include body")
    body = request["body"]
    if not isinstance(body, str) or not body.strip():
        raise ValueError("retrieval body must contain text")
    return body


def _check(hits):
    if not isinstance(hits, list):
        raise RuntimeError("retrieval did not return a list")
    for hit in hits:
        if not isinstance(hit, dict) or any(field not in hit for field in FIELDS):
            raise RuntimeError("retrieval row is missing a required field")
        distance = hit["distance"]
        if isinstance(distance, bool) or not isinstance(distance, (int, float)):
            raise RuntimeError("retrieval distance must be a number")
        if not math.isfinite(distance):
            raise RuntimeError("retrieval distance must be finite")
    return hits


class RetrievalService:
    def __init__(self, database_path, top_k=5):
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        self._store = VectorStore(database_path)
        self._top_k = top_k

    def retrieve_evidence(self, request):
        body = _body(request)
        try:
            hits = self._store.query(body, top_k=self._top_k)
        except Exception as exc:
            raise RuntimeError("retrieval query failed") from exc
        return {"evidence": _check(hits)}
```

## retrieval_api.py

```python
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
```

## Dockerfile

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV HF_HOME=/app/models
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='qdrant/bge-small-en-v1.5-onnx-q', revision='52398278842ec682c6f32300af41344b1c0b0bb2', allow_patterns=['config.json','model_optimized.onnx','special_tokens_map.json','tokenizer.json','tokenizer_config.json'])"
ENV HF_HUB_OFFLINE=1
COPY retrieval_api.py retrieval_service.py vector_store.py ./
COPY data ./data
EXPOSE 8000
CMD ["uvicorn", "retrieval_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Commands

The build needs network access once, for pip and for the pinned embedding files. After that, the model is a layer in the image.

```text
docker build -t homework7-retrieval .
docker run -d --name homework7-retrieval -p 8002:8000 homework7-retrieval
docker stop homework7-retrieval
docker rm homework7-retrieval
```

`http://localhost:8002/health` returns `{"status": "ok"}` after the store opens. A POST to `http://localhost:8002/search` with JSON `{"body": "My TV flickers."}` returns an `evidence` list of at most five rows.
