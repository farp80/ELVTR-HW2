# Homework 8 — what each task adds

Each section covers the Python added or changed in that task. Homework 7 helpers that were only copied, such as `_accept`, `_run`, and the service clients, stay as they were.

## Task 1

`validation_precision.py` is new. It compares three review rules on the Homework 4 model.

`build_predictions` retrains that model on the Homework 3 train tickets. It writes `validation_predictions.csv` for the validation tickets. Each row stores the true department, the predicted department, and the ten class scores.

`rule_flags` looks at one ticket and returns three flags. Margin is true when the top score minus the second score is below 0.05. Ratio is true when the second score is at least 80 percent of the top score. Entropy is true when the ten scores are spread out above 2.10.

`load_rows` reads the CSV. It keeps whether the prediction was right and the class scores.

`evaluate` runs the three rules on every row. It prints how many tickets go to a person, how many of those are wrong, and how often the skipped tickets are right.

`review_decision` is the rule later tasks use. It returns true when the top-two gap is below 0.05, and it also returns that gap.

## Task 2

`routing_review.py` is new. `workflow.py` is changed. The rest of the Homework 7 workflow stays.

`review_decision` sorts the class scores. It subtracts the second score from the top score, rounds to 4 decimals, and returns true when that gap is below 0.05. It also returns the gap.

`_package` adds two fields. `requires_routing_review` holds the flag. `human_reviewed_route` starts as `None`. A rejected or failed ticket always stores `False`. Those tickets have no route for a person to check.

`process_ticket` calls `review_decision` only after routing and the summary succeed. It passes the flag into `_package`. `recommended_department` and `class_scores` stay as the model returned them.

## Task 3

`workflow_record_store.py` is added. `workflow.py` saves every finished result. The Compose file mounts the `record-store` volume at `/app/data`.

`WorkflowRecordStore.__init__` opens `/app/data/workflow_records.json`. A missing file starts as an empty list.

`save_record` checks one result, appends it, and returns a copy. `list_records` returns every saved result in order. `get_record` returns one result by id. `delete_record` removes one result when its trace id still matches. `update_routing_review` sets `human_reviewed_route` and sets `requires_routing_review` to `false`. It refuses a failed or rejected record.

`_copy_and_validate_record` checks that the value is a dict with a UUID id. `_copy_json` copies a value through JSON. `_validate_workflow_record_id` rejects a blank or non-UUID id. `_read_records` loads the file. `_write_records` writes a temp file, then replaces the real file.

`process_ticket` runs `_process`, then `save_record`, and returns the saved copy. The object stores that store as `_store`.

`workflow_api.py` also defines `effective_department`, `filter_tickets`, `list_tickets`, and `submit_review`. Those call `workflow.store`. This file's attribute is `_store`, so those two routes do not line up yet. Task 4 fixes the name.

## Task 4

`workflow.py` renames `_store` to `store`. `process_ticket` still returns the saved record.

`workflow_api.py` adds listing and review. `/health` and `POST /tickets/process` stay.

`effective_department` returns `human_reviewed_route` when a person set it. Otherwise it returns `recommended_department`.

`filter_tickets` keeps records whose review flag is `true` or `false`. Then it keeps records whose effective department matches. Any other flag value raises `ValueError`.

`list_tickets` reads the store and returns the filtered list. A bad flag becomes HTTP 400.

`submit_review` requires a body with only `human_reviewed_route`. The value must be one of the ten departments. It calls `update_routing_review`. An unknown id is 404. A bad id, or a failed or rejected record, is 400. `ticket_body` stays as saved.

## Task 5

This task adds no Python. `monitoring_design.md` names the three metrics that Task 6 computes: `median_workflow_ms`, `workflow_failure_rate`, and `routing_review_rate`. The first two come from the trace log. The third comes from the saved results.

## Task 6

`metrics.py` is new. `IndexedTraceLogger.read_all` is new. `workflow.py` adds review tracing. `workflow_api.py` adds the ops routes.

`parse_time` accepts a UTC string that ends in `Z` and returns a datetime. `in_window` keeps a timestamp between `start` and `end`. Both ends count. `median` sorts the numbers and returns the middle value. With an even count, it averages the two middle values.

`median_workflow_ms` takes `elapsed_ms` from closing workflow events in the window. `workflow_failure_rate` divides `workflow_failed` events by failed plus successful events. Rejected events stay out. `routing_review_rate` divides saved results that still need review by the saved results in the window. `METRICS` maps each URL name to its function.

`_mark_review` writes one `routing_review` event. A successful ticket also stores `score_margin`. `traces` returns one ticket's events. `events` returns every event. `read_all` flushes the log and returns every stored event.

`read_traces` returns one ticket's events in order. An unknown id returns `[]`. `read_metric` runs the named function and returns `{"value": ...}`. An unknown name is 404. A bad `start` or `end` is 400.

## Task 7

This folder has no Python file. No test function was added.
