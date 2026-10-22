# Task 1 — Analyze Validation Errors

## Requirements

- Use the Homework 3 metrics and confusion matrix to select one consequential confusion family or weak slice.
- Explain why you chose the slice.
- Deterministically select at least 30 misclassified records from the slice for inspection.
- For each record, identify why the classifier failed, using slice metrics, ticket text, and/or model internals as appropriate.
- Define failure categories and assign every inspected ticket to one category.
- Identify which categories can be addressed through model or preprocessing changes.

## Deliverables

An error-analysis writeup containing:

- The selected slice and rationale.
- For every inspected record: ID, true label, predicted label (`recommended_department`), assigned failure category and rationale, and the best explanation for why the model selected the predicted department.
- For every failure category: record count, likely performance impact, and whether model or preprocessing changes can address it.
