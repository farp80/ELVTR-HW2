# Task 5 — Docker Compose commands

Run these from the `hw_7` folder, not from `hw_7/Task5`. Task 3 must have created the `homework7_ollama` volume and pulled the model, because `compose.yaml` uses that volume as external.

If the single containers from Tasks 1 to 4 are still running, remove them first so the ports are free:

```text
docker rm -f homework7-router homework7-retrieval homework7-ollama homework7-workflow
```

## Build and start all four services

```text
docker compose -f Task5/compose.yaml up --build -d
```

## Check

```text
docker compose -f Task5/compose.yaml ps
```

All four services show `healthy`. The ports are `8000` workflow, `8001` router, `8002` retrieval, and `8003` Ollama.

## Stop

```text
docker compose -f Task5/compose.yaml down
```

This removes the containers and the network. The Ollama model and the trace volume stay.
