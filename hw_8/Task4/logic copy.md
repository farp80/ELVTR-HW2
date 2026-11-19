# Task 3 — Save every workflow result

## Goal

Every ticket result is written to `/app/data/workflow_records.json` inside the workflow container. That folder is a Docker volume named `record-store`, so the file survives a restart. Rejected and failed tickets are saved too. `workflow_record_id` is the unique key. `ticket_id` stays as the caller sent it.

## Step 1 — Create the folder

Create `hw_8\Task3`. Copy these items from `hw_8\Task2` into it:

- `workflow.py`
- `workflow_api.py`
- `routing_client.py`
- `retrieval_client.py`
- `llm_service.py`
- `routing_review.py`
- `Dockerfile`
- `requirements.txt`
- `.dockerignore`
- the `shared` folder

Do not copy `__pycache__`, `docker_commands.md`, or the Task 2 `logic.md`.

## Step 2 — Add the record store

Copy `hw_8\Fidel Alejandro Rosell Perez - workflow_record_store.py` into `hw_8\Task3`. Rename the copy to `workflow_record_store.py`. Python can only import a file whose name has no spaces or dashes. Do not change its code.

## Step 3 — Import the store in workflow.py

Open `hw_8\Task3\workflow.py`. Find this line near the top:

```python
from routing_review import review_decision
```

Add this line right below it:

```python
from workflow_record_store import WorkflowRecordStore
```

## Step 4 — Create the store once

In `workflow.py`, find `def __init__(self, log_path):` inside `class TicketWorkflow`. Its last line is:

```python
        self._logger = IndexedTraceLogger(log_path)
```

Add this line right below it, with the same indentation:

```python
        self.store = WorkflowRecordStore()
```

The store is built once when the app starts. With no path, it uses `/app/data/workflow_records.json`. The API in Task 4 reads the same store through `workflow.store`.

## Step 5 — Save the result at the end

In `workflow.py`, find this line:

```python
    def process_ticket(self, request):
```

Rename that method to `_process`. Keep its whole body unchanged. Then paste the new `process_ticket` right above it. The result looks like this:

```python
    def process_ticket(self, request):
        return self.store.save_record(self._process(request))

    def _process(self, request):
        record_id = str(uuid4())
        # ...the rest of the old method stays exactly the same...
```

`_process` still builds the result for all three outcomes. `process_ticket` saves that result and returns the saved copy. The API still calls `process_ticket`, so `workflow_api.py` does not change in this task.

## Step 6 — Copy the store into the image

Open `hw_8\Task3\Dockerfile`. Replace the whole file with this:

```dockerfile
FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV LOG_PATH=/logs/workflow_trace.jsonl
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY workflow_api.py workflow.py routing_client.py retrieval_client.py llm_service.py routing_review.py workflow_record_store.py ./
COPY shared ./shared
EXPOSE 8000
CMD ["uvicorn", "workflow_api:app", "--host", "0.0.0.0", "--port", "8000"]
```

The only change is `workflow_record_store.py` at the end of the second `COPY` line.

## Step 7 — Bring the router and retrieval services

The submitted zip holds only the task folders, so the two Homework 7 services must live inside `hw_8`. Their code does not change.

1. Copy `hw_7\Task1` to `hw_8\Task3\router`. Leave out `.md` files and `__pycache__`.
2. Check that `hw_8\Task3\router\model\hw4_candidate.pkl` exists. The router Dockerfile copies it. This file is the Homework 4 model, retrained with the same settings. Its validation accuracy is 0.498.
3. Copy `hw_7\Task2` to `hw_8\Task3\retrieval`. Leave out `.md` files and `__pycache__`. Keep `data\lancedb`.
4. Open `hw_8\Task3\.dockerignore` and add two lines at the end:

```text
router
retrieval
```

The workflow image is built from `hw_8\Task3`. Those two lines keep the router and retrieval files out of it.

## Step 8 — Write compose.yaml

Create `hw_8\Task3\compose.yaml` with the content below.

- `build: .` builds the workflow from this folder.
- `build: ./router` and `build: ./retrieval` build the two services from Step 7.
- `record-store` is mounted at `/app/data`.
- Traces go to a new volume, `workflow-traces`. It holds only Homework 8 traces, and every one of those tickets is saved. Task 7 depends on that match.
- `name:` keeps the real Docker volume names exactly `record-store` and `workflow-traces`. Tasks 4 and 6 then reuse the same data.

```yaml
services:
  workflow:
    build: .
    ports:
      - "8000:8000"
    environment:
      ROUTER_URL: http://router:8000
      RETRIEVAL_URL: http://retrieval:8000
      OLLAMA_URL: http://ollama:11434/api/chat
      LOG_PATH: /logs/workflow_trace.jsonl
    volumes:
      - workflow-traces:/logs
      - record-store:/app/data
    depends_on:
      router:
        condition: service_healthy
      retrieval:
        condition: service_healthy
      ollama:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 20s

  router:
    build: ./router
    ports:
      - "8001:8000"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s

  retrieval:
    build: ./retrieval
    ports:
      - "8002:8000"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"]
      interval: 15s
      timeout: 10s
      retries: 8
      start_period: 60s

  ollama:
    image: ollama/ollama:0.34.1
    ports:
      - "8003:11434"
    volumes:
      - homework7_ollama:/root/.ollama
    healthcheck:
      test: ["CMD", "ollama", "show", "qwen2.5:1.5b-instruct-q4_K_M"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

volumes:
  homework7_ollama:
    external: true
    name: homework7_ollama
  workflow-traces:
    name: workflow-traces
  record-store:
    name: record-store
```

## Step 9 — Start the app

Stop any Homework 7 deployment first, because it uses the same ports. Then start this one. Run these in PowerShell:

```text
cd C:\Users\frosell\Downloads\ELVTR-HW2\hw_7
docker compose -f Task5/compose.yaml down
cd C:\Users\frosell\Downloads\ELVTR-HW2\hw_8\Task3
docker compose up --build -d
docker compose ps
```

Wait until all four services show `healthy`.

## Step 10 — Check that a result was saved

Send one ticket, then read the saved file inside the container:

```text
Invoke-RestMethod -Method Post -Uri http://localhost:8000/tickets/process -ContentType "application/json" -Body '{"ticket_id": 1, "Body": "I was charged twice this month."}'
docker compose exec workflow cat /app/data/workflow_records.json
```

The file is a JSON array. It holds the same result the POST returned, including `requires_routing_review` and `human_reviewed_route`. Send a blank `Body` once. That rejected result is saved too.

## Step 11 — Stop

```text
docker compose down
```

`down` removes the containers only. The `record-store` volume keeps the saved results for Task 4.
