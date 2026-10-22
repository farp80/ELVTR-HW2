import json
import sys
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from shared.classes.classification_metric_evaluator import ClassificationMetricEvaluator
from shared.classes.ticket_routing_classifier import LABEL_NAMES, TicketRoutingClassifier

HW3 = ROOT / "hw_3"
PREFIX = "Fidel Alejandro Rosell Perez - "
MODEL_PATH = HERE / f"{PREFIX}hw4_candidate.pkl"
PREDICTION_PATH = HERE / f"{PREFIX}validation_predictions_candidate.csv"
TARGET = "Generic words"  # Task 1 failure category

# 1. Load train and validation only. Test rows are dropped here.
cleaned = pd.read_csv(HW3 / f"{PREFIX}support_tickets_cleaned.csv")
split = pd.read_csv(HW3 / f"{PREFIX}split_manifest.csv")
data = cleaned.merge(split, on="ticket_id", how="inner")
data = data[data["split"].isin(["train", "validation"])]

train_df = data[data["split"] == "train"].copy()
validation_df = data[data["split"] == "validation"].copy()

baseline_pred = pd.read_csv(HW3 / f"{PREFIX}validation_predictions.csv")  # read only
baseline_model = TicketRoutingClassifier.load(HW3 / f"{PREFIX}hw3_ml_baseline.pkl")
print("train:", len(train_df), "| validation:", len(validation_df))

# 2. Retrain with the one change: stop_words="english".
clf = TicketRoutingClassifier()
clf.vectorizer = TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
    stop_words="english",  # THE ONE CHANGE
)
clf.fit(train_df["body"], train_df["department"])
clf.save(MODEL_PATH)


def changed_params(a, b):
    pa, pb = a.get_params(), b.get_params()
    return {k: (pa[k], pb[k]) for k in pa if pa[k] != pb[k]}


vec_diff = changed_params(baseline_model.vectorizer, clf.vectorizer)
model_diff = changed_params(baseline_model.model, clf.model)
print("vectorizer changes:", vec_diff)
print("model changes     :", model_diff)
if set(vec_diff) != {"stop_words"} or model_diff:
    raise SystemExit("More than one change. Stop.")

# 3. Predict validation and save in the Homework 3 format (4 columns).
rows = []
for _, row in validation_df.iterrows():
    prediction = clf.predict(row["body"])
    rows.append(
        {
            "ticket_id": row["ticket_id"],
            "true_label": LABEL_NAMES[row["department"]],
            "recommended_department": prediction["recommended_department"],
            "class_scores": json.dumps(prediction["class_scores"]),
        }
    )
candidate_pred = pd.DataFrame(rows)
candidate_pred.to_csv(PREDICTION_PATH, index=False)
print(candidate_pred.shape, candidate_pred.columns.tolist())

# 4. Compare with the baseline on validation.
base_eval = ClassificationMetricEvaluator(baseline_pred.copy())
cand_eval = ClassificationMetricEvaluator(candidate_pred.copy())

base_sum, cand_sum = base_eval.summary_metrics(), cand_eval.summary_metrics()
for key in base_sum:
    print(f"{key:12} baseline {base_sum[key]:.4f} | candidate {cand_sum[key]:.4f} | change {cand_sum[key] - base_sum[key]:+.4f}")

base_pc = pd.DataFrame(base_eval.per_class_metrics())
cand_pc = pd.DataFrame(cand_eval.per_class_metrics())
pc = base_pc[["label", "support", "precision", "recall", "f1"]].merge(
    cand_pc[["label", "precision", "recall", "f1"]], on="label", suffixes=("_base", "_new")
)
for m in ("precision", "recall", "f1"):
    pc[f"{m}_change"] = pc[f"{m}_new"] - pc[f"{m}_base"]
print(pc[["label", "support", "f1_base", "f1_new", "f1_change", "recall_change", "precision_change"]]
      .round(3).sort_values("f1_change").to_string(index=False))

# 5. Check the targeted tickets and the side effects.
review = json.loads((HERE.parent / "Task1" / "ticket_review.json").read_text(encoding="utf-8"))
target_ids = [t["ticket_id"] for t in review["tickets"] if t["failure_category"] == TARGET]
inspected_ids = [t["ticket_id"] for t in review["tickets"]]

cmp = baseline_pred.merge(candidate_pred, on="ticket_id", suffixes=("_base", "_new"))
cmp["ok_base"] = cmp["true_label_base"] == cmp["recommended_department_base"]
cmp["ok_new"] = cmp["true_label_new"] == cmp["recommended_department_new"]


groups = {
    f"target category ({TARGET})": cmp["ticket_id"].isin(target_ids),
    "all 30 inspected tickets": cmp["ticket_id"].isin(inspected_ids),
    "slice: Technical Support -> IT Support": (cmp.true_label_base == "Technical Support") & (cmp.recommended_department_base == "IT Support"),
    "risk: IT Support tickets baseline got right": (cmp.true_label_base == "IT Support") & cmp.ok_base,
    "risk: Billing tickets baseline got right": (cmp.true_label_base == "Billing and Payments") & cmp.ok_base,
}
for name, mask in groups.items():
    g = cmp[mask]
    print(f"{name:50} n={len(g):4d} | correct before={int(g.ok_base.sum()):4d} after={int(g.ok_new.sum()):4d}")

fixed = cmp[~cmp.ok_base & cmp.ok_new]
broken = cmp[cmp.ok_base & ~cmp.ok_new]
print("\nfixed:", len(fixed), "| broken:", len(broken), "| net:", len(fixed) - len(broken))
print("broken by true department:")
print(broken.groupby("true_label_base").size().sort_values(ascending=False).to_string())
