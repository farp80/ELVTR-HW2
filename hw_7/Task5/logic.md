# Task 5 — Docker Compose

## Steps — services

Follow `WEEK_7_ASSIGNMENT.md` Task 5, `example_docker_setup/compose.yaml`, and `Fidel Alejandro Rosell Perez - ollama_container_config.md`. Finish Task 3 before the first `up`.

1. Save `compose.yaml` in the shape of `example_docker_setup/compose.yaml`: build, ports, environment, volumes, and `healthcheck` on every service.
2. Build `workflow` from `../Task4`, `router` from `../Task1`, and `retrieval` from `../Task2`. Start image `ollama/ollama:0.34.1` from `ollama_container_config.md`. `WEEK_7_ASSIGNMENT.md` builds those three images and starts that Ollama image.
3. Set `ROUTER_URL` to `http://router:8000`, `RETRIEVAL_URL` to `http://retrieval:8000`, and `OLLAMA_URL` to `http://ollama:11434/api/chat`. `WEEK_7_ASSIGNMENT.md` requires those three URLs. The host names are the Compose service names. The ports are the container ports from Tasks 1, 2, and 3.

## Steps — storage and checks

Follow `ollama_container_config.md`, Task 4, and the port list in `WEEK_7_ASSIGNMENT.md` Tasks 1 through 4.

4. Mount external volume `homework7_ollama` at `/root/.ollama`. Mount `homework7_traces` at `/logs`. Keep `LOG_PATH` at `/logs/workflow_trace.jsonl`.
5. Publish host `8000`, `8001`, `8002`, and `8003`.
6. Copy the `healthcheck` from `example_docker_setup/compose.yaml` onto the three Python services. Each one calls `http://127.0.0.1:8000/health`. For Ollama, use the check in `ollama_container_config.md`: `ollama show qwen2.5:1.5b-instruct-q4_K_M`. Make `workflow` wait until the other three checks pass.

## compose.yaml

```yaml
services:
  workflow:
    build: ../Task4
    ports:
      - "8000:8000"
    environment:
      ROUTER_URL: http://router:8000
      RETRIEVAL_URL: http://retrieval:8000
      OLLAMA_URL: http://ollama:11434/api/chat
      LOG_PATH: /logs/workflow_trace.jsonl
    volumes:
      - homework7_traces:/logs
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
    build: ../Task1
    ports:
      - "8001:8000"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)"]
      interval: 15s
      timeout: 10s
      retries: 5
      start_period: 30s

  retrieval:
    build: ../Task2
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
  homework7_traces:
```

## What each health check is waiting for

The router check passes after `joblib` loads the pickle and Uvicorn binds port `8000`. The retrieval check waits longer because opening LanceDB and the embedding model is slower than loading the pickle. The Ollama check passes only when the CLI can see `qwen2.5:1.5b-instruct-q4_K_M` in the mounted volume. The workflow check passes after Uvicorn binds and the three URLs were read at startup.
