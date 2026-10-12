# Task 3.3 - Compute and Interpret Classification Metrics

This file explains how to complete HW 3.3 step by step.

I am still learning AI, so the code snippets are written in a direct and
readable way instead of a highly optimized way.

No `.py` file is created here. This Markdown file contains the implementation
plan, code snippets, and explanations.

The OOP design is in:

```text
oop_metric_evaluator_design.md
```

## Requirement Summary

Task 3.3 asks me to:

1. Use the Task 2 prediction CSV as input.
2. Compute the Task 1 metrics directly from true and predicted labels.
3. Avoid pre-built metric functions.
4. Produce an evaluation report.
5. Include:
   - per-class one-vs-rest confusion matrix
   - multi-class confusion matrix
   - accuracy
   - macro-F1
   - weighted-F1
   - per-class precision
   - per-class recall
   - per-class F1
   - metrics by body-length slice
   - explanation of best and worst departments
   - explanation of what the validation set cannot prove

## Input Files

The main input is the Task 2 prediction CSV:

```text
Fidel Alejandro Rosell Perez - validation_predictions.csv
```

It should have these columns:

```text
ticket_id
true_label
recommended_department
class_scores
```

For body-length slices, I also need the cleaned ticket body:

```text
C:\Users\frosell\Downloads\ELVTR-HW2\Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv
```

Why:

- The prediction CSV has labels and scores.
- The cleaned ticket CSV has the ticket `body`.
- Body length slices need the `body`, so I merge it by `ticket_id`.

## Important Rule About Metrics

The requirement says:

```text
Implement the Task 1 metrics directly from the predicted/true labels
or class scores without using pre-built functions.
```

So I should not use:

```python
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
```

Instead, I should count everything myself.

## Metrics From Task 3.1

The selected metrics are:

- accuracy
- macro-F1
- weighted-F1
- per-class precision
- per-class recall
- per-class F1
- confusion matrix diagnostics

The primary metric is:

```text
Macro-F1
```

The secondary metric is:

```text
Weighted-F1
```

## Step 1 - Import Libraries

```python
import json
from pathlib import Path

import pandas as pd
```

Why:

- `json` is useful if I need to read the `class_scores` string.
- `Path` makes file paths easier to read.
- `pandas` loads CSV files and stores results.

## Step 2 - Define File Paths

```python
ROOT = Path(r"C:\Users\frosell\Downloads\ELVTR-HW2")
HW3_ROOT = ROOT / "hw_3"

prediction_path = HW3_ROOT / "Fidel Alejandro Rosell Perez - validation_predictions.csv"
cleaned_path = ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
report_path = HW3_ROOT / "task_3" / "Fidel Alejandro Rosell Perez - validation_evaluation_report.md"
```

Why:

- `prediction_path` points to the Task 2 output.
- `cleaned_path` gives access to ticket bodies for slice analysis.
- `report_path` is where the final evaluation report can be saved.

## Step 3 - Load the Prediction CSV

```python
prediction_df = pd.read_csv(prediction_path)
```

Check the columns:

```python
print(prediction_df.columns.tolist())
print(prediction_df.shape)
print(prediction_df.head())
```

Expected columns:

```text
ticket_id
true_label
recommended_department
class_scores
```

## Step 4 - Create the Evaluator

The class is explained in:

```text
oop_metric_evaluator_design.md
```

Basic usage:

```python
evaluator = ClassificationMetricEvaluator(prediction_df)
```

Why:

- The class keeps all metric logic together.
- It normalizes labels before comparison.
- It avoids pre-built metric functions.

## Step 5 - Compute Overall Summary Metrics

```python
summary = evaluator.summary_metrics()
print(summary)
```

This returns:

```python
{
    "accuracy": 0.0,
    "macro_f1": 0.0,
    "weighted_f1": 0.0,
}
```

The real numbers will depend on the predictions.

Explanation:

- accuracy tells how many validation tickets were routed correctly overall
- macro-F1 tells how well the model balances performance across departments
- weighted-F1 tells how well the model performs when larger departments count
  more

## Step 6 - Compute Per-Class Metrics

```python
per_class = evaluator.per_class_metrics()
per_class_df = pd.DataFrame(per_class)
print(per_class_df)
```

This gives one row per department with:

```text
precision
recall
f1
support
tp
fp
fn
tn
```

Why:

- Precision shows whether routed tickets are reliable for a department.
- Recall shows whether actual tickets for a department are being found.
- F1 balances precision and recall.
- TP, FP, FN, and TN explain where the metric values come from.

## Step 7 - Compute the Multi-Class Confusion Matrix

```python
matrix = evaluator.multiclass_confusion_matrix()
matrix_df = pd.DataFrame(matrix).T
print(matrix_df)
```

How to read it:

- rows are true departments
- columns are predicted departments
- diagonal cells are correct predictions
- off-diagonal cells are mistakes

This helps find confusion patterns, such as:

```text
Actual IT Support predicted as Technical Support
```

## Step 8 - Compute One-vs-Rest Confusion Counts

```python
one_vs_rest_rows = []

for label in evaluator.labels:
    one_vs_rest_rows.append(evaluator.one_vs_rest_counts(label))

one_vs_rest_df = pd.DataFrame(one_vs_rest_rows)
print(one_vs_rest_df)
```

This gives TP, FP, FN, and TN for each department.

Why:

- This is required by the evaluation report.
- It also explains each department's precision, recall, and F1.

## Step 9 - Add Body-Length Slices

Load the cleaned ticket CSV:

```python
cleaned_df = pd.read_csv(cleaned_path)
```

Add body length to the evaluator:

```python
evaluator.add_body_length_slices(cleaned_df)
```

The slice logic is:

- shortest third of validation tickets: `short`
- middle third: `medium`
- longest third: `long`

Why use thirds?

- It avoids guessing random length numbers.
- It creates groups based on the actual validation data.
- It keeps the groups reasonably balanced.

## Step 10 - Compute Metrics Per Slice

```python
slice_results = evaluator.metrics_by_slice()
```

To print the summary for each slice:

```python
for slice_name, result in slice_results.items():
    print(slice_name)
    print(result["row_count"])
    print(result["summary"])
```

Why:

- A model may perform better on long tickets because they contain more clues.
- A model may perform worse on short tickets because they have less context.
- Slice metrics help find this kind of pattern.

## Step 11 - Identify Best and Worst Departments

Use per-class F1:

```python
per_class_df = pd.DataFrame(evaluator.per_class_metrics())

best_departments = per_class_df.sort_values("f1", ascending=False).head(3)
worst_departments = per_class_df.sort_values("f1", ascending=True).head(3)

print(best_departments)
print(worst_departments)
```

Why F1?

- F1 balances precision and recall.
- A department with high precision but very low recall is still a problem.
- A department with high recall but very low precision is also a problem.

## Step 12 - Find Confusion Patterns

Use the multi-class confusion matrix.

Look for high off-diagonal counts.

Simple approach:

```python
confusions = []

for true_label in evaluator.labels:
    for pred_label in evaluator.labels:
        if true_label == pred_label:
            continue

        count = matrix[true_label][pred_label]

        if count > 0:
            confusions.append(
                {
                    "true_label": true_label,
                    "predicted_label": pred_label,
                    "count": count,
                }
            )

confusion_df = pd.DataFrame(confusions)
confusion_df = confusion_df.sort_values("count", ascending=False)
print(confusion_df.head(10))
```

Why:

- This shows the most common wrong routes.
- These patterns help explain why some departments have weak recall or
  precision.

## Step 13 - Report Template

The final report should include these sections:

```md
# Task 3.3 - Validation Evaluation Report

## Inputs

## Overall Metrics

## Per-Class Metrics

## Per-Class One-vs-Rest Confusion Matrix

## Multi-Class Confusion Matrix

## Body-Length Slice Definitions

## Metrics by Body-Length Slice

## Performance Differences Across Slices

## Primary and Secondary Metric Interpretation

## Best and Worst Departments

## Confusion Patterns

## What These Metrics Cannot Establish
```

## Interpretation Guide

### Overall Metrics

Explain:

- What macro-F1 says about balanced department performance.
- What weighted-F1 says about performance weighted by department size.
- Whether accuracy agrees with or hides the F1 results.

### Per-Class Metrics

Explain:

- Which departments have high precision.
- Which departments have high recall.
- Which departments have low F1.
- Whether low F1 is caused more by low precision or low recall.

### Body-Length Slices

Explain:

- Whether short, medium, or long tickets perform better.
- Why that might happen.
- For example, short tickets may have fewer clues.

### Confusion Patterns

Explain:

- Which departments are confused most often.
- Whether the confused departments are similar.
- For example, `IT Support` and `Technical Support` may overlap in language.

### What the Validation Set Cannot Establish

Mention:

- Validation performance is not final test performance.
- The results depend on this specific validation split.
- Metrics do not prove the model is fair for every real-world user.
- Metrics do not explain every individual wrong prediction.
- A high score does not mean the model should be deployed without review.

## Final Checklist

Before Task 3.3 is complete, check:

- The Task 2 prediction CSV is used.
- No test split is used.
- No pre-built metric functions are used.
- Accuracy is computed directly.
- Per-class precision is computed directly.
- Per-class recall is computed directly.
- Per-class F1 is computed directly.
- Macro-F1 is computed directly.
- Weighted-F1 is computed directly.
- One-vs-rest confusion counts are included.
- Multi-class confusion matrix is included.
- Body-length slices are defined and explained.
- Metrics are computed for each body-length slice.
- Best and worst departments are discussed.
- Confusion patterns are discussed.
- Limits of the validation metrics are explained.

## Rubric Self-Check

Expected score: incomplete until the Task 2 prediction CSV exists and the metrics are actually computed.

- Requirement: use the Task 2 prediction results as input.
  - Status: planned.
- Requirement: implement metrics directly without pre-built metric functions.
  - Status: planned in `oop_metric_evaluator_design.md`.
- Requirement: include per-class one-vs-rest confusion matrix.
  - Status: planned.
- Requirement: include multi-class confusion matrix.
  - Status: planned.
- Requirement: compute selected Task 3.1 metrics.
  - Status: planned.
- Requirement: compute metrics by body-length slice.
  - Status: planned by merging body text from the cleaned ticket CSV.
- Requirement: interpret primary and secondary metrics.
  - Status: included in the report template.
- Requirement: identify best and worst departments and confusion patterns.
  - Status: planned.
- Requirement: explain what validation metrics cannot establish.
  - Status: included in the interpretation guide.

Main risk:

- The actual metric values cannot be filled in until `validation_predictions.csv` exists.

