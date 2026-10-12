## Task 3 - Compute and Interpret Classification Metrics

Compute the Task 1 metrics from the task 2 prediction CSV, and interpret
the results.

### Requirements

- Use the Task 2 prediction results as the input.
- Implement the Task 1 metrics directly from the predicted/true labels
  or class scores without using pre-built functions.
- Produce an evaluation report containing the computed metrics and explanations.
- Identify slices of body-length (e.g. short, medium, long), explain your
  slice definitions, and compute the same metrics for each slice.

### Deliverables

- Metric-computation code
- Evaluation report containing:
  - Per-class (one-vs-rest) confusion matrix
  - Multi-class confusion matrix
  - Computed metric values for each selected metric from Task 1.
  - Computed metrics per-slice.
  - How performance differs across the body-length slices and what those
    differences may indicate.
  - What the primary and secondary metrics indicate about overall performance,
    and whether the other summary metrics change that interpretation
  - Which departments perform best and worst, and which confusion patterns help
    explain those results
  - What the metrics and this validation set cannot establish