# Homework 4, Task 2 — Controlled Classifier Iteration (step by step, with code)

Goal: make **one** change that targets a Task 1 failure category, retrain, compare
to the baseline on validation, and decide keep or revert.

**How to use this file**

- Paste all the Python blocks, in order, into `hw_4/Task2/task.py`. Together they
  are the "modified training code" deliverable. (This file does not create it.)
- Run it from anywhere: `python hw_4/Task2/task.py`.
- Write the experiment log by hand at the end (outline in Step 8).

## Rules

| Rule | Why |
| --- | --- |
| One change only. | If you change two things, you cannot say which one caused the result. |
| Train on the Homework 3 training split only. | Same data as the baseline, so the comparison is fair. |
| Judge on validation only. Never open the test split. | The test set is for Task 3. |
| Do not edit or overwrite the Homework 3 model or predictions. | They are the baseline. |
| Write the keep/revert rule **before** you run. | Otherwise you can bend the rule to fit the result. |

## Inputs and outputs

| File | Role |
| --- | --- |
| `hw_3/... - support_tickets_cleaned.csv`, `split_manifest.csv` | Training and validation data |
| `hw_3/... - hw3_ml_baseline.pkl` | Baseline model (read only) |
| `hw_3/... - validation_predictions.csv` | Baseline predictions (read only) |
| `hw_4/Task1/ticket_review.json` | Your Task 1 categories and ticket IDs |
| `hw_4/Task2/... - hw4_candidate.pkl` | **Output:** retrained model |
| `hw_4/Task2/... - validation_predictions_candidate.csv` | **Output:** same 4 columns as Homework 3 |
| `hw_4/Task2/experiment_log.md` | **Output:** your log |

`.pkl` and `.csv` files are in `.gitignore`. They still go in the submission zip.

---

## Step 1 — Choose the change and write the decision rule

**Target:** the Task 1 category `Generic words`. It has 12 of the 30 errors.

**Change:** `stop_words="english"` in the TF-IDF vectorizer. Nothing else changes.

**Why not `max_df`:** on the training split, `max_df=0.5` removes only `to`, `the`
and `and`. The Task 1 noise was word pairs like `the problems` and `or hardware`,
and `max_df` keeps those. `stop_words` removes the common words before the pairs
are built, so the pairs disappear.

**Risks (check them in Step 6):**

- `it` is a stop word. In IT Support tickets it may be the acronym "IT". Watch IT
  Support recall.
- `bill`, `amount` and `system` are stop words too. Watch Billing and Payments F1.
- `tools`, `problems` and `marketing` are not stop words. This change will not
  fix tickets driven by them.

**Write the rule before you run the code:**

> Keep the candidate only if all three are true:
> 1. Macro-F1 goes up by at least 0.005.
> 2. More of the 12 `Generic words` tickets are correct than before.
> 3. No department's F1 drops by more than 0.03.
> Otherwise revert.

My run on validation: macro-F1 went from 0.4820 to 0.5133. The rule was met.
The numbers are in `experiment_log.md`.

---

## Step 2 — Load the data (train and validation only)

**Why:** the test rows are dropped immediately, so nothing in this script can touch
them.

```python
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

cleaned = pd.read_csv(HW3 / f"{PREFIX}support_tickets_cleaned.csv")
split = pd.read_csv(HW3 / f"{PREFIX}split_manifest.csv")
data = cleaned.merge(split, on="ticket_id", how="inner")
data = data[data["split"].isin(["train", "validation"])]  # test rows dropped here

train_df = data[data["split"] == "train"].copy()
validation_df = data[data["split"] == "validation"].copy()

baseline_pred = pd.read_csv(HW3 / f"{PREFIX}validation_predictions.csv")  # read only
baseline_model = TicketRoutingClassifier.load(HW3 / f"{PREFIX}hw3_ml_baseline.pkl")
print("train:", len(train_df), "| validation:", len(validation_df))
```

**Check:** train 17,524, validation 3,755.

---

## Step 3 — Retrain with the one change

**What:** build the same classifier as Homework 3, replace only the vectorizer
setting, and fit on the training split.

**Why this way:** the saved object is still a `TicketRoutingClassifier`, so Task 3
can load it with no extra code. The check stops the script if you changed more than one thing.

```python
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
```

**Check:** the only vectorizer change is `stop_words`, and the model has none.

---

## Step 4 — Predict validation and save in the Homework 3 format

**Why:** the format must match exactly: `ticket_id`, `true_label`,
`recommended_department`, `class_scores` (a JSON string).

```python
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
```

---

## Step 5 — Compare to the baseline on validation

**What:** same Homework 3 metrics for both models, then per-department changes.

**Why:** improvements and regressions both go in the log. A better macro-F1 can hide
a department that got worse.

```python
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
```

**How to read it:** sort is worst to best. Negative `f1_change` rows are your
regressions. Look at `it support` (recall) and `billing and payments` first.

---

## Step 6 — Check the targeted records and the side effects

**What:** count correct predictions before and after for: the target category, your
30 inspected tickets, the whole slice, and the tickets that could break.

**Why:** Task 2 asks how the targeted records changed. The last two rows catch the
risks named in Step 1.

```python
review = json.loads((HERE.parent / "Task1" / "ticket_review.json").read_text(encoding="utf-8"))
TARGET = "Generic words"
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
```

---

## Step 7 — Decide

Apply the rule from Step 1 to the numbers. Do not change the rule now.

- Rule met → **keep**. The candidate is your Task 2 result.
- Rule not met → **revert**. The baseline stays the Task 2 result. The candidate
  files stay in the folder and in the submission.

Either decision is a valid result. Write the reason with numbers.

---

## Step 8 — Write the experiment log

Save as `hw_4/Task2/experiment_log.md`. Write it by hand. The code does not
create it. Use short sections, no tables. Keep each explanation under 100 words,
in simple words. In each section say where the numbers come from:

- Category and ticket IDs: `hw_4/Task1/ticket_review.json`.
- Metric changes and per-department F1: the "compare" printout of `task.py`.
- Targeted records, risk groups, fixed and broken: the "targeted tickets" printout of `task.py`.

```md
# Task 2 — Experiment Log

## Targeted category and change
- Category: Generic words (12 of 30 inspected errors)
- Change: stop_words="english" in the TF-IDF vectorizer. Nothing else changed.
- Why: ...

## Decision rule (written before running)
- ...

## Effect on the targeted records
- Target category: X of 12 correct before, Y after.
- 30 inspected tickets: ...
- Slice (Technical Support -> IT Support): ...

## Improvements (validation, vs baseline)
- Accuracy / macro-F1 / weighted-F1 changes.
- Departments that improved, with F1 change.

## Regressions
- Departments that got worse, with F1 change.
- IT Support recall change. Billing and Payments F1 change.
- Tickets fixed vs broken.

## Decision
- Keep or revert, and the reason using the rule.
```

## Checklist

- [ ] Exactly one change; the check in Step 3 did not stop the script.
- [ ] Trained on the training split only; test never loaded.
- [ ] Candidate CSV has the same 4 columns and 3,755 rows.
- [ ] Baseline model and predictions untouched.
- [ ] Log has the category, the change, the targeted-record result, improvements,
      regressions, and the decision with reasons.
- [ ] Decision follows the rule written before running.
