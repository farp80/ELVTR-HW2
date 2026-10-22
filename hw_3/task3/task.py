import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from shared.classes.classification_metric_evaluator import ClassificationMetricEvaluator

DATA_ROOT = ROOT / "hw_3"
TASK_ROOT = Path(__file__).resolve().parent
prediction_path = (
    DATA_ROOT / "Fidel Alejandro Rosell Perez - validation_predictions.csv"
)
cleaned_path = DATA_ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
report_path = (
    TASK_ROOT / "Fidel Alejandro Rosell Perez - validation_evaluation_report.md"
)

prediction_df = pd.read_csv(prediction_path)
print(prediction_df.columns.tolist())
print(prediction_df.shape)
print(prediction_df.head())

metrics_evaluator = ClassificationMetricEvaluator(prediction_df)
summary = metrics_evaluator.summary_metrics()

print("####################### SUMMARY METRICS ########################")
print(summary)
print("#" * 100)


print("####################### PER CLASS METRICS ########################")
per_class = metrics_evaluator.per_class_metrics()
per_class_df = pd.DataFrame(per_class)
print(per_class_df)
print("#" * 100)

print("####################### MULTI-CLASS CONFUSION MATRIX ########################")
matrix = metrics_evaluator.multiclass_confusion_matrix()
matrix_df = pd.DataFrame(per_class).T
print(matrix_df)
print("#" * 100)

print("####################### CONFUSION COUNTS ########################")
one_vs_rest_rows = []

for label in metrics_evaluator.labels:
    one_vs_rest_rows.append(metrics_evaluator.fundamental_outcomes(label))

one_vs_rest_df = pd.DataFrame(one_vs_rest_rows)
print(one_vs_rest_df)
print("#" * 100)

print("####################### BODY SLICES ########################")
cleaned_df = pd.read_csv(cleaned_path)
metrics_evaluator.add_body_length_slices(cleaned_df)

slice_results = metrics_evaluator.metrics_by_slice()

for slice_name, result in slice_results.items():
    print(slice_name)
    print(result["row_count"])
    print(result["summary"])
    print(pd.DataFrame(result["per_class"]))
print("#" * 100)

print("####################### DEPARTMENTS (BEST AND WORST) ########################")
per_class_df = pd.DataFrame(metrics_evaluator.per_class_metrics())
best_departments = per_class_df.sort_values("f1", ascending=False).head(5)
worst_departments = per_class_df.sort_values("f1", ascending=True).head(5)

print(f"Best departments: {best_departments}")
print(f"Worst departments: {worst_departments}")
print("#" * 100)

print("####################### CONFUSION PATTTERNS  ########################")
confusions = []

for true_label in metrics_evaluator.labels:
    for pred_label in metrics_evaluator.labels:
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
