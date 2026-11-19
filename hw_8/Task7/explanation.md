# Task 7 — Test the monitoring

## What this test does

Task 7 checks the monitoring from Task 6. The two checks stay separate. One looks at trace events. The other looks at the three metric numbers. The code is `test_monitoring.py`. It calls the running app at `http://localhost:8000`. It imports the metric functions from Task 6, so the expected number uses the same formula as the API. Ticket text comes from the Homework 2 CSV. Only rows with a body are used.

## Trace test

Send one ticket. Read `trace_id` from the reply. Call `GET /ops/traces` with that id. The first event must be `workflow` started. The last event must be `workflow` completed, with status `summary_ready_for_review`. The event before that must be `routing_review`, and its flag must match the result. Routing, retrieval, and the model each start before they finish. Retrieval finishes before the model starts. Routing finishes before the review step. Every event has this `trace_id` and a UTC time that ends in `Z`. No event uses a private field name. No event contains the ticket text. An unknown id must return `[]`.

## Metric test

Send three tickets. Read these with no window: `GET /ops/metrics/median_workflow_ms`, `GET /ops/metrics/workflow_failure_rate`, and `GET /ops/metrics/routing_review_rate`. Then download every saved ticket with `GET /tickets`, and the traces of each ticket. Older tickets count too. Pass those lists to the same Task 6 function. The API value and that result must match. Sort the times that metric uses. Set `start` to the second time and `end` to the last time. That leaves out the earliest ticket. Read the same three URLs again with that window and compare once more. Two `null` values match. A gap smaller than 0.000000001 is allowed.

## How to run it

1. From `hw_8\Task6`, run `docker compose up --build -d`. Wait until all four services are healthy.
2. Install the HTTP library once: `python -m pip install requests==2.34.2`.
3. From `hw_8\Task7`, run `python test_monitoring.py`.
4. A pass prints four lines. The first is `trace capture: passed`. Then one line per metric.
5. A failed check stops with `AssertionError` and names the check.
6. The model is slow, so the run can take a few minutes.
7. From `hw_8\Task6`, run `docker compose down`. The volumes keep their data.
