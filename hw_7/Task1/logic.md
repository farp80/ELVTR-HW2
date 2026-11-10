# Task 1 — Router container

## Steps 1–3 — fill the build folder

The container has its own disk. It cannot open `C:\Users\frosell\Downloads\ELVTR-HW2\shared`. `docker build` reads only the folder you give it, `hw_7\Task1`. `hw_4\Task2\task.py` saved the class as `shared.classes.ticket_routing_classifier.TicketRoutingClassifier`. `WEEK_7_ASSIGNMENT.md` Task 1 requires that same path inside the image, under `/app`.

1. In `hw_7\Task1`, create two folders: `shared\classes` and `model`.
2. Copy `shared\classes\ticket_routing_classifier.py` from the repo to `hw_7\Task1\shared\classes\ticket_routing_classifier.py`. Put an empty `__init__.py` in `hw_7\Task1\shared` and in `hw_7\Task1\shared\classes`. `clean_text` and `prepare_texts` in this copy are the preprocessing.
3. Copy `hw_4\Task2\Fidel Alejandro Rosell Perez - hw4_candidate.pkl` to `hw_7\Task1\model\hw4_candidate.pkl`.

## Steps 4–6 — write the Python that the container runs

Follow `hw_6\Task2\routing_service.py`, `hw_6\Task1\routing_contract.md`, `example_http_service\example_http_wrapper.py`, and `Fidel Alejandro Rosell Perez - requirements.txt`.

4. Save `routing_service.py` in `hw_7\Task1`. Keep `route_ticket` and the checks in `routing_contract.md`. Its import is `from shared.classes.ticket_routing_classifier import TicketRoutingClassifier`. That line runs inside the container. It loads `/app/shared/classes/ticket_routing_classifier.py`, the copy from step 2. It does not load the repo file.
5. Save `router_api.py` in `hw_7\Task1`, using `example_http_wrapper.py`. Keep `GET /health` returning `{"status": "ok"}`. Add `POST /route`. Load `/app/model/hw4_candidate.pkl`, the copy from step 3. Return HTTP 400 for `ValueError` and HTTP 500 for `RuntimeError`.
6. Save `requirements.txt` in `hw_7\Task1` from the pins in `Fidel Alejandro Rosell Perez - requirements.txt`. Keep `scikit-learn==1.9.1`.

## Steps 7–8 — copy the build folder into the image

Follow `example_docker_setup\api\Dockerfile` and `WEEK_7_ASSIGNMENT.md` Task 1.

7. Save the Dockerfile in `hw_7\Task1`. Set `WORKDIR /app`. `COPY shared ./shared` writes the step 2 copy to `/app/shared`. `COPY model ./model` writes the step 3 pickle to `/app/model`. The last line is the command in `WEEK_7_ASSIGNMENT.md`: `uvicorn router_api:app` on `0.0.0.0:8000`.
8. From `hw_7\Task1`, run `docker build -t homework7-router .`, then `docker run -d --name homework7-router -p 8001:8000 homework7-router`. Host port `8001` maps to container port `8000`. The running container uses `/app/shared` only. The repo folder `shared` stays on your PC.

## requirements.txt

```text
pandas==3.0.5
scikit-learn==1.9.1
joblib==1.6.0
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

## routing_service.py

```python
import math

from shared.classes.ticket_routing_classifier import TicketRoutingClassifier

DEPARTMENTS = (
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
)


def _body(request):
    if not isinstance(request, dict) or "body" not in request:
        raise ValueError("routing request must include body")
    body = request["body"]
    if not isinstance(body, str) or not body.strip():
        raise ValueError("routing body must contain text")
    return body


def _check(result):
    department = result.get("recommended_department")
    scores = result.get("class_scores")
    if department not in DEPARTMENTS or not isinstance(scores, dict):
        raise RuntimeError("routing response is missing required fields")
    if set(scores) != set(DEPARTMENTS):
        raise RuntimeError("routing scores must cover every department")
    if any(
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(score)
        for score in scores.values()
    ):
        raise RuntimeError("routing scores must be finite numbers")
    if max(scores, key=scores.get) != department:
        raise RuntimeError("recommended department is not the top score")
    return {"recommended_department": department, "class_scores": scores}


class RoutingService:
    def __init__(self, model_path):
        self._classifier = TicketRoutingClassifier.load(model_path)

    def route_ticket(self, request):
        body = _body(request)
        try:
            result = self._classifier.predict(body)
        except Exception as exc:
            raise RuntimeError("routing classifier failed") from exc
        return _check(result)
```

## router_api.py

```python
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
```

## Dockerfile

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY router_api.py routing_service.py ./
COPY shared ./shared
COPY model ./model
EXPOSE 8000
CMD ["uvicorn", "router_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Commands

Build and run this folder by itself. The last command removes the container. The image remains.

```text
docker build -t homework7-router .
docker run -d --name homework7-router -p 8001:8000 homework7-router
docker stop homework7-router
docker rm homework7-router
```

`http://localhost:8001/health` returns `{"status": "ok"}` when the pickle loaded. A POST to `http://localhost:8001/route` with JSON `{"body": "I was charged twice."}` returns `recommended_department` and `class_scores`.
