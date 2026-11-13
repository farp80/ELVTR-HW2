# Task 1 — Router container commands

Run these from the `hw_7/Task1` folder.

## Build and start

```text
docker build -t homework7-router .
docker run -d --name homework7-router -p 8001:8000 homework7-router
```

Host port `8001` maps to container port `8000`.

## Check (PowerShell)

```text
Invoke-RestMethod http://localhost:8001/health
Invoke-RestMethod -Method Post -Uri http://localhost:8001/route -ContentType "application/json" -Body '{"body": "My TV flickers."}'
```

`/health` returns `{"status": "ok"}`. `/route` returns `recommended_department` and `class_scores`.

## Stop

```text
docker stop homework7-router
docker rm homework7-router
```
