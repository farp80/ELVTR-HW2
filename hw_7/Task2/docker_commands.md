# Task 2 — Retrieval container commands

Run these from the `hw_7/Task2` folder.

## Build and start

```text
docker build -t homework7-retrieval .
docker run -d --name homework7-retrieval -p 8002:8000 homework7-retrieval
```

Host port `8002` maps to container port `8000`. The build downloads the pinned embedding model into the image.

## Check (PowerShell)

```text
Invoke-RestMethod http://localhost:8002/health
Invoke-RestMethod -Method Post -Uri http://localhost:8002/search -ContentType "application/json" -Body '{"body": "My TV flickers."}'
```

`/health` returns `{"status": "ok"}`. `/search` returns an `evidence` list of at most five rows.

## Stop

```text
docker stop homework7-retrieval
docker rm homework7-retrieval
```
