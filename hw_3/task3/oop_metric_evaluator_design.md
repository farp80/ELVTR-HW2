# HW 3.3 OOP Metric Evaluator Design

This file explains the OOP design for computing classification metrics.

I am not creating a `.py` file here. This is Markdown with code snippets and
plain explanations so I can understand the implementation before using it.

## Why Use OOP Here?

Task 3.3 has several related jobs:

- read prediction results
- compare true labels to predicted labels
- build confusion matrices
- compute accuracy, precision, recall, F1, macro-F1, and weighted-F1
- compute the same metrics for body-length slices
- summarize best and worst departments

These jobs belong together. A class helps keep them in one place.

The class name can be:

```python
class ClassificationMetricEvaluator:
```

## Important Rule

The assignment says to implement the metrics directly from labels or class
scores without using pre-built metric functions.

That means I should not use:

```python
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
```

Instead, I should count true positives, false positives, false negatives, and
true negatives myself.

## Expected Inputs

The Task 2 prediction CSV should have exactly these columns:

```text
ticket_id
true_label
recommended_department
class_scores
```

For body-length slices, I also need the original or cleaned ticket body. The
prediction CSV does not include `body`, so I should merge the prediction CSV
back to the cleaned ticket CSV using `ticket_id` only for the slice analysis.

This does not change the predictions. It only adds body length information.

## Full Class Draft

```python
class ClassificationMetricEvaluator:
    def __init__(self, prediction_df):
        self.df = prediction_df.copy()
        self.df["true_label_clean"] = self.df["true_label"].apply(self.normalize_label)
        self.df["pred_label_clean"] = self.df["recommended_department"].apply(
            self.normalize_label
        )
        self.labels = sorted(
            set(self.df["true_label_clean"]) | set(self.df["pred_label_clean"])
        )

    def normalize_label(self, label):
        return str(label).strip().lower()

    def accuracy(self, df=None):
        data = self.df if df is None else df
        correct = (data["true_label_clean"] == data["pred_label_clean"]).sum()
        total = len(data)

        if total == 0:
            return 0

        return correct / total

    def multiclass_confusion_matrix(self, df=None):
        data = self.df if df is None else df

        matrix = {}

        for true_label in self.labels:
            matrix[true_label] = {}

            for pred_label in self.labels:
                count = (
                    (data["true_label_clean"] == true_label)
                    & (data["pred_label_clean"] == pred_label)
                ).sum()

                matrix[true_label][pred_label] = int(count)

        return matrix

    def one_vs_rest_counts(self, label, df=None):
        data = self.df if df is None else df

        actual_is_label = data["true_label_clean"] == label
        predicted_is_label = data["pred_label_clean"] == label

        tp = (actual_is_label & predicted_is_label).sum()
        fp = (~actual_is_label & predicted_is_label).sum()
        fn = (actual_is_label & ~predicted_is_label).sum()
        tn = (~actual_is_label & ~predicted_is_label).sum()

        return {
            "label": label,
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(tn),
        }

    def precision_recall_f1(self, label, df=None):
        counts = self.one_vs_rest_counts(label, df)

        tp = counts["tp"]
        fp = counts["fp"]
        fn = counts["fn"]

        if tp + fp == 0:
            precision = 0
        else:
            precision = tp / (tp + fp)

        if tp + fn == 0:
            recall = 0
        else:
            recall = tp / (tp + fn)

        if precision + recall == 0:
            f1 = 0
        else:
            f1 = 2 * precision * recall / (precision + recall)

        support = tp + fn

        return {
            "label": label,
            "precision": precision,
            "recall": recall,
            "f1": f1,
            "support": int(support),
            "tp": counts["tp"],
            "fp": counts["fp"],
            "fn": counts["fn"],
            "tn": counts["tn"],
        }

    def per_class_metrics(self, df=None):
        rows = []

        for label in self.labels:
            rows.append(self.precision_recall_f1(label, df))

        return rows

    def macro_f1(self, df=None):
        per_class = self.per_class_metrics(df)

        if len(per_class) == 0:
            return 0

        total_f1 = sum(row["f1"] for row in per_class)
        return total_f1 / len(per_class)

    def weighted_f1(self, df=None):
        per_class = self.per_class_metrics(df)
        total_support = sum(row["support"] for row in per_class)

        if total_support == 0:
            return 0

        weighted_total = 0

        for row in per_class:
            weighted_total += row["f1"] * row["support"]

        return weighted_total / total_support

    def summary_metrics(self, df=None):
        return {
            "accuracy": self.accuracy(df),
            "macro_f1": self.macro_f1(df),
            "weighted_f1": self.weighted_f1(df),
        }

    def add_body_length_slices(self, body_df):
        merged = self.df.merge(body_df[["ticket_id", "body"]], on="ticket_id", how="left")
        merged["body_length"] = merged["body"].fillna("").astype(str).str.len()

        short_cutoff = merged["body_length"].quantile(0.33)
        medium_cutoff = merged["body_length"].quantile(0.66)

        def assign_slice(length):
            if length <= short_cutoff:
                return "short"
            if length <= medium_cutoff:
                return "medium"
            return "long"

        merged["body_length_slice"] = merged["body_length"].apply(assign_slice)
        self.df = merged

        return self.df

    def metrics_by_slice(self):
        results = {}

        for slice_name in ["short", "medium", "long"]:
            slice_df = self.df[self.df["body_length_slice"] == slice_name]
            results[slice_name] = {
                "row_count": len(slice_df),
                "summary": self.summary_metrics(slice_df),
                "per_class": self.per_class_metrics(slice_df),
            }

        return results
```

## Method Explanations

### `__init__()`

This saves the prediction DataFrame and normalizes labels.

Normalizing matters because one file may say:

```text
technical support
```

while predictions may say:

```text
Technical Support
```

Lowercasing both makes the comparison fair.

### `accuracy()`

Accuracy is:

```text
correct predictions / all predictions
```

It is easy to understand, but it can hide poor performance on smaller classes.

### `multiclass_confusion_matrix()`

This creates a table where:

- rows are true departments
- columns are predicted departments
- each cell is a count

This helps me see which departments are confused with each other.

### `one_vs_rest_counts()`

For one department, this calculates:

- TP: actual department and predicted department match the label
- FP: predicted as the label, but actual is different
- FN: actual is the label, but predicted is different
- TN: actual is not the label and predicted is not the label

### `precision_recall_f1()`

This computes the per-class metrics.

Precision:

```text
TP / (TP + FP)
```

Recall:

```text
TP / (TP + FN)
```

F1:

```text
2 * precision * recall / (precision + recall)
```

### `macro_f1()`

Macro-F1 averages each department's F1 equally.

This is the primary metric from Task 3.1 because the dataset is imbalanced.

### `weighted_f1()`

Weighted-F1 averages F1 scores using each department's support.

This is the secondary metric from Task 3.1 because it reflects the real label
distribution.

### `add_body_length_slices()`

This adds body length and creates three groups:

- short
- medium
- long

The method uses validation-set length cutoffs so the groups are based on the
actual validation data.

### `metrics_by_slice()`

This computes the same summary and per-class metrics for short, medium, and long
tickets.

That helps answer whether the model performs differently depending on ticket
length.

