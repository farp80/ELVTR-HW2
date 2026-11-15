# Task 5 — Monitoring design

## Step by step

1. This file is the Task 5 writeup. No code goes in `hw_8\Task5`.
2. Read the three questions below. Each one lists the metric, its formula, what is recorded, and where in the workflow it is recorded.
3. Two metrics come from the trace log. One metric comes from the saved workflow results. The assignment asks for at least one from each source.
4. No metric reads the ticket text, the summary, or the retrieved articles. The logger already refuses fields such as `body`, `ticket_body`, and `summary`.
5. Task 6 builds these three metrics. Use these exact names: `median_workflow_ms`, `workflow_failure_rate`, and `routing_review_rate`.

## Question 1 — How long does one ticket take?

Why it matters: a slow ticket means routing, search, or the model is stuck or overloaded.

Metric: `median_workflow_ms`. Sort every `elapsed_ms` value from the closing workflow trace events. Take the middle value. With an even count, take the average of the two middle values. The median is used because one very slow ticket would pull an average far up.

What is recorded: `elapsed_ms`, which is milliseconds from start to finish, plus the UTC `timestamp`.

Where: in `_process`, on the last trace event with `service` set to `workflow`. All three outcomes write it: success, rejected, and failed.

Source: the trace log.

## Question 2 — How often does a service break?

Why it matters: a high rate means a container is down. That needs a fix in the deployment, not in the ticket.

Metric: `workflow_failure_rate`. Count the closing workflow events with `terminal_status` set to `workflow_failed`. Divide by the closing events set to `workflow_failed` or `summary_ready_for_review`. Rejected tickets stay out, because a blank ticket is the caller's mistake, not a broken service.

What is recorded: `terminal_status`, `error_type` (for example `RuntimeError`), and the UTC `timestamp`. No error text and no ticket text.

Where: in `_process`, on the last trace event with `service` set to `workflow`.

Source: the trace log.

## Question 3 — How much of the work waits for a person?

Why it matters: this is the size of the review queue. It shows how much staff time the margin rule creates.

Metric: `routing_review_rate`. Count the saved results with `requires_routing_review` set to `true`. Divide by all saved results. The rate falls when a person submits a route, because that sets the flag to `false`.

What is recorded: `requires_routing_review` and `trace_id` in each saved result. A saved result has no clock of its own. Its time comes from the closing workflow trace event with the same `trace_id`.

Where: the flag is set right after the routing result arrives. It is saved at the end of `process_ticket`.

Source: the saved workflow results.

## Time window

All three metrics accept `start` and `end`. Both are UTC ISO 8601 strings, such as `2026-09-30T12:34:56.789Z`. A record counts when its timestamp is between them, and both ends count. When no record falls in the window, the metric returns `null`.
