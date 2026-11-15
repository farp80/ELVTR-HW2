# Homework 8 - Add Routing Review and Monitor the Application

## Goal

Add selective human review for ambiguous routing decisions and operational
monitoring to the deployed Homework 7 application. Preserve the original model
output, allow a reviewer to set the route used by the application, and expose a
small set of useful operational metrics through aggregate endpoints.

## Provided Materials

| Material | Purpose |
| --- | --- |
| `requirements.txt` | Cumulative pinned dependencies through Homework 8 |
| `workflow_record_store.py` | JSON-backed storage for complete workflow results |
| `workflow_with_routing_review.svg` | Workflow diagram highlighting the routing-review policy step |

Bring forward your Homework 7 four-service deployment and the selected
classifier's canonical validation predictions. Continue using the Homework 6
workflow contract, including `recommended_department` and `class_scores`.

## Part 1 - Identify Ambiguous Routes

## Task 1 - Select the Routing-Review Policy

Design a policy that uses the selected classifier's validation class scores to
identify routing decisions that require human review.

### Requirements

- Use the saved validation predictions from the classifier selected in Homework 4.
- Design 3 potential approaches for deterministically identifying ambiguous
  routing predictions.
- Run the 3 approaches on the validation predictions.
- Select one approach, and justify your selection.

### Deliverables

- Validation predictions file.
- Code to apply and evaluate the 3 approaches.
- Selected policy and rationale. Rationale should be based on meaningful
  numeric evidence from evaluation.

## Task 2 - Add the Routing-Review Policy to the Workflow

Apply the selected routing-review policy in the deployed application.

<img src="workflow_with_routing_review.svg" alt="Ticket-processing workflow with the new routing-review policy step highlighted" width="760">

### Requirements

- Add a workflow step after the routing-service call that applies the selected
  routing-review policy.
- Add `requires_routing_review` to workflow results containing your policy output.
- Add `human_reviewed_route` to workflow results, initially set to `None`.
- Failed and rejected tickets should have `requires_routing_review` set to `False`.

### Deliverables

- Updated workflow code.

## Part 2 - Save and Access Workflow Results

## Task 3 - Save Workflow Results

Persist workflow results for later review and display.

### Requirements

- In Compose, create a named volume called `record-store` and mount it at
  `/app/data` in the workflow container.
- Add `workflow_record_store.py` to the workflow container. It stores records at
  `/app/data/workflow_records.json`.
- At the end of the workflow, use `workflow_record_store.py` to save every
  complete workflow result.
- Use `workflow_record_id` as the saved record's unique identifier. Preserve
  `ticket_id` as the source ticket identifier.

### Deliverables

- Updated workflow code.
- Updated Compose configuration with storage added.

## Task 4 - Implement Ticket Retrieval and Routing Review

Add the ability to retrieve saved tickets and apply routing review.

### Requirements

- Add the following endpoints to the workflow API:

  | Endpoint                                            | Behavior                                                                                                                                                                                                                                             |
  |-----------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | `GET /tickets`                                      | Return a JSON array of saved workflow results. Support optional `requires_routing_review` and `department` query parameters.                                                                                                                         |
  | `POST /tickets/{workflow_record_id}/routing-review` | Accept `{"human_reviewed_route": "<allowed department>"}` and return the updated saved result. Validate the provided department + workflow record, update `human_reviewed_route`, and set `requires_routing_review` to `false` without altering saved `ticket_body`. |

- URLs with optional params take the form `GET /tickets?{param_name}={query_value}&...`. Support these retrieval forms:
  - `GET /tickets?requires_routing_review={true|false}`
  - `GET /tickets?department={department}`
  - `GET /tickets?requires_routing_review={true|false}&department={department}`
- When filtering by `department`, use `human_reviewed_route` if non-null, otherwise, use `recommended_department`.
- Applying a human route puts the route in `human_reviewed_route` and sets `requires_routing_review` to `false`.
  No other fields in the saved record should be modified.
- Invalid routing-review `POST` requests must fail without modifying the saved record. 
- Failed and rejected records cannot have a human route applied.

### Deliverables

- API code.

## Part 3 - Add Narrow Operational Monitoring

## Task 5 - Design the Monitoring

Identify useful operational questions, select metric(s) to measure each,
and identify the information to capture in order to calculate it.

### Requirements

- Select 3 useful, varied operational questions to answer. These questions can be answered
  from 2 sources: (1) the logging/tracing from Homework 6, (2) the final workflow results. 
  Select at least 1 metric from each source. You can add logging/tracing to capture the information you need.
  Consider component timing, failures, input sizes, routing ambiguity, routing review,
  and any other meaningful aspect of workflow execution.
- For each question, identify and define an aggregate metric you will use to measure it.
- For each metric, identify what is/will-be captured to compute it, and when it will be captured.
- Ensure you do not rely on capturing or using any sensitive information.

### Deliverables

- A writeup doc containing, for each operational question:
  - The question and why it is useful
  - The metric you selected, its definition, and how it answers the question
  - The measurements you need to capture to compute the metric
  - Where in the workflow each measurement will be recorded

## Task 6 - Implement the Monitoring

Emit privacy-safe monitoring trace-events as the selected measurements and outcomes
become available, then expose the selected aggregate metrics and existing
workflow trace-events.

### Requirements

- Implement the following endpoints in the workflow API:

| Endpoint                              | Behavior                                                                                                                                              |
|---------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| `GET /ops/traces?trace_id={trace_id}` | Return a JSON array of trace-events for a given trace ID, in recorded order. Return `[]` for an unknown ID.                                          |
| `GET /ops/metrics/<metric_name>`      | Return the value of the specified metric. Support optional `start` and `end` timestamp query parameters to filter the records used in the calculation. |

- Implement an endpoint for each metric, which implements the metric aggregation.
- Implement any additional logging to capture the information you defined in Task 5.
- Include a timestamp in every trace-event. Trace-events and `start`/`end` query
  parameters should use UTC ISO 8601 strings (e.g. `2026-09-30T12:34:56.789Z`).

### Deliverables

- Updated API code.
- Updated workflow code.

## Task 7 - Test the Monitoring

Test trace capture separately from metric calculation.

### Requirements

Implement 2 test flows:

Trace-event Capture:
- Run a ticket through the workflow.
- Retrieve all traces via `GET /ops/traces` using the `trace_id` from the workflow result.
- Verify expected trace-events are present in recorded order, match the ID,
  and exclude sensitive content.
- Ensure an unknown `trace_id` returns an empty array.

Metric Computation (for each metric):
- Run a few tickets through the workflow.
- Retrieve the metric via `GET /ops/metrics/<metric_name>`.
- Retrieve all traces or workflow-results, depending on what the metric uses. Metrics are
  computed across all traces/results, including tickets processed before this test.
- Compute the expected metric value based on the traces/results, and compare to the 
  actual metric value.
- Query the metric endpoints with `start` and `end` bounds. 
  Make sure to select bounds that exclude at least 1 trace/result.
- Compute the expected metric value based on the traces/results within the bounds, 
  and compare to the actual metric value.


### Deliverables

- Test code.

## Submission Guidelines

- Submit the complete homework as one `.zip` file. Do not submit individual
  files or multiple `.zip` files.
- Name the archive `Firstname_Lastname_HW8.zip`, using the same first and last
  name shown in Google Classroom. For example: `Tanner_Gilligan_HW8.zip`.
- Organize the archive with one folder per task at its root. Each task folder
  should contain that task's deliverables:

  ```text
  Tanner_Gilligan_HW8.zip
  ├── Task1/
  ├── Task2/
  ├── Task3/
  ├── Task4/
  ├── Task5/
  ├── Task6/
  └── Task7/
  ```

- Upload the `.zip` file itself. Do not submit a Google Drive, GitHub, or other
  external link in place of the file.
- Submit data tables as static CSV files, not Excel files or links to Google
  Sheets.
- Submit writeups as `.txt` or `.md` files.
- Do not include duplicate or extraneous files unless they are relevant to
  running or interpreting your submission.
