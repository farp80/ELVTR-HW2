# Task 4 — Workflow container commands

Run these from the `hw_7/Task4` folder. Start the Task 1, Task 2, and Task 3 containers first. Inside this container, `localhost` is the container itself, so it reaches the other three through `host.docker.internal`.

## Build and start

```text
docker volume create homework7_traces
docker build -t homework7-workflow .
docker run -d --name homework7-workflow -p 8000:8000 -e ROUTER_URL=http://host.docker.internal:8001 -e RETRIEVAL_URL=http://host.docker.internal:8002 -e OLLAMA_URL=http://host.docker.internal:8003/api/chat -e LOG_PATH=/logs/workflow_trace.jsonl -v homework7_traces:/logs homework7-workflow
```

Host port `8000` maps to container port `8000`. Traces are written to `/logs/workflow_trace.jsonl` in the `homework7_traces` volume.

## Check (PowerShell)

```text
Invoke-RestMethod http://localhost:8000/health
docker exec homework7-workflow tail -n 20 /logs/workflow_trace.jsonl
```

`/health` returns `{"status": "ok"}`. A POST to `http://localhost:8000/tickets/process` with `ticket_id` and `Body` returns the ten-field package.

## Stop

```text
docker stop homework7-workflow
docker rm homework7-workflow
```

This removes the container only. The `homework7_traces` volume keeps the trace file.
