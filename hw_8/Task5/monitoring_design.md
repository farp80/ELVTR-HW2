# Task 5 — Monitoring design

## Setup

1. This file is the Task 5 writeup.
2. No code goes in this folder.
3. There are three questions. Each one has one metric.
4. Task 6 uses these names: `median_workflow_ms`, `workflow_failure_rate`, and `routing_review_rate`.
5. Two metrics come from the trace log. One comes from the saved results.
6. No metric reads the ticket text, the summary, or the article text.

## Question 1 — How long does one ticket take?

1. A slow ticket means routing, search, or the model is slow.
2. The metric is `median_workflow_ms`.
3. Take `elapsed_ms` from each closing workflow trace event.
4. Sort those numbers. Pick the middle one.
5. If the count is even, average the two middle numbers.
6. The middle value stays steady when one ticket is very slow.
7. Record `elapsed_ms` and the UTC `timestamp`.
8. `_process` writes them on the last event where `service` is `workflow`.
9. Success, rejected, and failed tickets all write this event.
10. Source: the trace log.

## Question 2 — How often does a service fail?

1. A high rate means a container is down.
2. The metric is `workflow_failure_rate`.
3. Count closing workflow events with `terminal_status` set to `workflow_failed`.
4. Divide that count by the closing events set to `workflow_failed` or `summary_ready_for_review`.
5. A blank ticket is `input_rejected`. Those events stay out of this rate.
6. Record `terminal_status`, `error_type` (for example `RuntimeError`), and the UTC `timestamp`.
7. Do not record the error text or the ticket text.
8. `_process` writes them on the last event where `service` is `workflow`.
9. Source: the trace log.

## Question 3 — How many tickets wait for a person?

1. This is the size of the review queue.
2. The metric is `routing_review_rate`.
3. Count saved results with `requires_routing_review` set to `true`.
4. Divide that count by all saved results.
5. After a person sets a route, the flag becomes `false`. The rate goes down.
6. Record `requires_routing_review` and `trace_id` on each saved result.
7. A saved result has no time of its own.
8. Use the time on the closing workflow event with the same `trace_id`.
9. The flag is set after routing returns. The result is saved at the end of `process_ticket`.
10. Source: the saved workflow results.

## Time window

1. Each metric can take `start` and `end`.
2. Both are UTC times, such as `2026-09-30T12:34:56.789Z`.
3. A record counts when its time is inside that range.
4. The start time and the end time both count.
5. If no record is in the range, the metric returns `null`.
