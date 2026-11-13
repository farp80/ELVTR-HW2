# Task 6 — Run the deployment

Run these from the `hw_7` folder, not from `hw_7/Task6`.

## Start all four services

```text
docker compose -f Task5/compose.yaml up --build -d
docker compose -f Task5/compose.yaml ps
```

Wait until all four services show `healthy`.

## Run the test

```text
python Task6/test_deployment.py
```

The test posts ticket `28763`, checks the ten contract fields and the exact `ticket_body`, and writes `Task6/ticket_28763_result.json`. No output and exit code `0` means it passed.

## Read the trace for that request

```text
docker compose -f Task5/compose.yaml exec -T workflow tail -n 20 /logs/workflow_trace.jsonl
```

## Stop

```text
docker compose -f Task5/compose.yaml down
```
