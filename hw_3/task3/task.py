import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from shared.classes.classification_metric_evaluator import ClassificationMetricEvaluator

ROOT = Path(r"D:\ELVTR\homeworks\ELVTR-HW2")
HW3_ROOT = ROOT / "hw_3"
print(HW3_ROOT)
prediction_path = HW3_ROOT / "Fidel Alejandro Rosell Perez - validation_predictions.csv"
cleaned_path = ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
report_path = (
    HW3_ROOT
    / "task_3"
    / "Fidel Alejandro Rosell Perez - validation_evaluation_report.md"
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

one_vs_rest_rows = []

for label in metrics_evaluator.labels:
    one_vs_rest_rows.append(metrics_evaluator.fundamental_outcomes(label))

one_vs_rest_df = pd.DataFrame(one_vs_rest_rows)
print(one_vs_rest_df)
