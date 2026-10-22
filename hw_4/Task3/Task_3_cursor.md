# Homework 4, Task 3 — Final Holdout Comparison (step by step, with code)

Goal: run the baseline and the Task 2 candidate on the **test set once**, compare
them, check that the result supports your Task 2 decision, and pick the routing
model.

**How to use this file**

- Paste all the Python blocks, in order, into `hw_4/Task3/task.py`.
- It runs in two stages:
  - `python hw_4/Task3/task.py freeze`
  - `python hw_4/Task3/task.py test`
- Write the report by hand at the end (outline in Step 6).

## Rules

| Rule | Why |
| --- | --- |
| Freeze both models and the Task 2 decision **before** the test set is opened. | Otherwise you can pick the winner after seeing the answer. |
| Run the test stage **once**. | A second run invites changes based on test results. |
| Do not retrain, edit, or re-tune either model after seeing test results. | That would turn the test set into a second validation set. |
| Write the selection rule before the test run. | Same reason as the Task 2 rule. |
| Report the result even if it disagrees with Task 2. | An honest "no" is a valid answer. |

## Inputs and outputs

| File | Role |
| --- | --- |
| `hw_3/... - hw3_ml_baseline.pkl` | Baseline model |
| `hw_4/Task2/... - hw4_candidate.pkl` | Candidate model |
| `hw_3/... - validation_predictions.csv`, `hw_4/Task2/... - validation_predictions_candidate.csv` | Validation results, for the validation-vs-test comparison |
| `hw_4/Task3/freeze.txt` | **Output:** proof of the freeze |
| `hw_4/Task3/... - test_predictions_baseline.csv` | **Output:** baseline test predictions |
| `hw_4/Task3/... - test_predictions_candidate.csv` | **Output:** candidate test predictions |
| `hw_4/Task3/test_metrics.txt` | **Output:** metrics and confusion matrices |
| `hw_4/Task3/test_comparison_report.md` | **Output:** your report |

---

## Step 1 — Settings, imports and helpers

**What:** two constants you must set, then shared code.

**Why:** `TASK2_DECISION` and `SELECTION_RULE` are written into `freeze.txt`
before the test stage. The test stage refuses to run if they changed.

Set `TASK2_DECISION` to what your Task 2 log says. The selection rule below is a
good default. Keep it simple and decide it now.

```python
import hashlib
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from shared.classes.classification_metric_evaluator import ClassificationMetricEvaluator
from shared.classes.ticket_routing_classifier import LABEL_NAMES, TicketRoutingClassifier

HW3 = ROOT / "hw_3"
TASK2 = ROOT / "hw_4" / "Task2"
PREFIX = "Fidel Alejandro Rosell Perez - "

BASELINE_MODEL = HW3 / f"{PREFIX}hw3_ml_baseline.pkl"
CANDIDATE_MODEL = TASK2 / f"{PREFIX}hw4_candidate.pkl"
VAL_BASELINE = HW3 / f"{PREFIX}validation_predictions.csv"
VAL_CANDIDATE = TASK2 / f"{PREFIX}validation_predictions_candidate.csv"

# ---- SET BEFORE `freeze` ----------------------------------------------------
TASK2_DECISION = "keep"  # "keep" or "revert", exactly as in your Task 2 log
SELECTION_RULE = (
    "Carry the candidate forward only if the Task 2 decision was keep AND the "
    "candidate's test macro-F1 is higher than the baseline's. Otherwise carry "
    "the baseline forward."
)
# -----------------------------------------------------------------------------

EVAL_SPLIT = "test"  # only change to "validation" for the dry run in Step 2
TAG = "" if EVAL_SPLIT == "test" else f"_DRYRUN_{EVAL_SPLIT}"

FREEZE_PATH = HERE / f"freeze{TAG}.txt"
OUT_BASELINE = HERE / f"{PREFIX}test_predictions_baseline{TAG}.csv"
OUT_CANDIDATE = HERE / f"{PREFIX}test_predictions_candidate{TAG}.csv"
METRICS_PATH = HERE / f"test_metrics{TAG}.txt"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def predict_split(model_path, df):
    """Same 4-column format as Homework 3."""
    clf = TicketRoutingClassifier.load(model_path)
    rows = []
    for _, row in df.iterrows():
        p = clf.predict(row["body"])
        rows.append(
            {
                "ticket_id": row["ticket_id"],
                "true_label": LABEL_NAMES[row["department"]],
                "recommended_department": p["recommended_department"],
                "class_scores": json.dumps(p["class_scores"]),
            }
        )
    return pd.DataFrame(rows)
```

---

## Step 2 — Dry run on validation (do this first)

**Why:** you only get one test run. Prove the code works on validation first.

1. Change `EVAL_SPLIT = "test"` to `EVAL_SPLIT = "validation"`.
2. Run `freeze`, then `test`. All files get a `_DRYRUN_validation` tag, so they
   cannot be mixed up with the real ones.
3. Check that the numbers look right. The baseline's accuracy should be 0.472, as
   in Homework 3.
4. Delete the `_DRYRUN_validation` files. Set `EVAL_SPLIT` back to `"test"`.

---

## Step 3 — Freeze

**What:** save a SHA-256 fingerprint of both model files, the Task 2 decision, and
the selection rule, with a timestamp.

**Why:** this is your proof that nothing changed between the decision and the test.
The code refuses to freeze twice.

```python
def freeze():
    if TASK2_DECISION not in ("keep", "revert"):
        raise SystemExit("Set TASK2_DECISION to keep or revert.")
    if FREEZE_PATH.exists():
        raise SystemExit("Already frozen. Do not freeze again.")
    lines = [
        f"time: {datetime.now().isoformat(timespec='seconds')}",
        f"baseline_sha256: {sha256(BASELINE_MODEL)}",
        f"candidate_sha256: {sha256(CANDIDATE_MODEL)}",
        f"task2_decision: {TASK2_DECISION}",
        f"selection_rule: {SELECTION_RULE}",
    ]
    FREEZE_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(FREEZE_PATH.read_text(encoding="utf-8"))


def read_freeze():
    values = {}
    for line in FREEZE_PATH.read_text(encoding="utf-8").splitlines():
        key, value = line.split(": ", 1)
        values[key] = value
    return values
```

Run it: `python hw_4/Task3/task.py freeze`. Open `freeze.txt` and read it. Do not
move to Step 4 until it looks right.

---

## Step 4 — Run the test, once

**What:** check the freeze, predict the test split with both models, save both CSVs,
and compute everything.

**Why each check exists:**

- Hashes must match `freeze.txt`. This proves the models are unchanged.
- The output files must not exist yet. This enforces "run once".

```python
def matrix_text(ev):
    m = pd.DataFrame(ev.multiclass_confusion_matrix()).T  # rows = true, columns = predicted
    m.index = [f"{i} {label}" for i, label in enumerate(m.index)]
    m.columns = range(len(m.columns))  # column i = department i listed on the left
    return m.to_string()


def run_test():
    if not FREEZE_PATH.exists():
        raise SystemExit("Run `freeze` first.")
    frozen = read_freeze()
    if frozen["baseline_sha256"] != sha256(BASELINE_MODEL):
        raise SystemExit("Baseline model changed.")
    if frozen["candidate_sha256"] != sha256(CANDIDATE_MODEL):
        raise SystemExit("Candidate model changed.")
    if frozen["task2_decision"] != TASK2_DECISION:
        raise SystemExit("Task 2 decision changed.")
    if frozen["selection_rule"] != SELECTION_RULE:
        raise SystemExit("Selection rule changed.")
    if OUT_BASELINE.exists() or OUT_CANDIDATE.exists():
        raise SystemExit("Already run. Run once only.")

    cleaned = pd.read_csv(HW3 / f"{PREFIX}support_tickets_cleaned.csv")
    split = pd.read_csv(HW3 / f"{PREFIX}split_manifest.csv")
    eval_df = cleaned.merge(split, on="ticket_id", how="inner")
    eval_df = eval_df[eval_df["split"] == EVAL_SPLIT]
    print("evaluating split:", EVAL_SPLIT, "| rows:", len(eval_df))

    base_pred = predict_split(BASELINE_MODEL, eval_df)
    cand_pred = predict_split(CANDIDATE_MODEL, eval_df)
    base_pred.to_csv(OUT_BASELINE, index=False)
    cand_pred.to_csv(OUT_CANDIDATE, index=False)

    evals = {
        "baseline": ClassificationMetricEvaluator(base_pred.copy()),
        "candidate": ClassificationMetricEvaluator(cand_pred.copy()),
    }
    val_preds = {"baseline": pd.read_csv(VAL_BASELINE), "candidate": pd.read_csv(VAL_CANDIDATE)}

    out, test_sum, val_sum = [], {}, {}
    for name, ev in evals.items():
        test_sum[name] = ev.summary_metrics()
        s = test_sum[name]
        out += [
            f"## {name.upper()} on {EVAL_SPLIT}",
            f"accuracy {s['accuracy']:.4f} | macro-F1 {s['macro_f1']:.4f} | weighted-F1 {s['weighted_f1']:.4f}",
            "",
            "Per department:",
            pd.DataFrame(ev.per_class_metrics())[["label", "precision", "recall", "f1", "support"]].round(3).to_string(index=False),
            "",
            "Confusion matrix (rows = true, columns = predicted):",
            matrix_text(ev),
            "",
        ]

    out.append(f"## VALIDATION vs {EVAL_SPLIT.upper()}")
    for name in evals:
        v_ev = ClassificationMetricEvaluator(val_preds[name].copy())
        val_sum[name] = v_ev.summary_metrics()
        v, t = val_sum[name], test_sum[name]
        out.append(
            f"{name}: macro-F1 {v['macro_f1']:.4f} -> {t['macro_f1']:.4f} ({t['macro_f1'] - v['macro_f1']:+.4f}) | "
            f"accuracy {v['accuracy']:.4f} -> {t['accuracy']:.4f} ({t['accuracy'] - v['accuracy']:+.4f})"
        )
        v_f1 = pd.DataFrame(v_ev.per_class_metrics()).set_index("label")["f1"]
        t_f1 = pd.DataFrame(evals[name].per_class_metrics()).set_index("label")["f1"]
        shift = (t_f1 - v_f1).sort_values(key=abs, ascending=False).head(3)
        out.append("  biggest department F1 shifts: " + ", ".join(f"{k} {d:+.3f}" for k, d in shift.items()))

    gain_val = val_sum["candidate"]["macro_f1"] - val_sum["baseline"]["macro_f1"]
    gain_test = test_sum["candidate"]["macro_f1"] - test_sum["baseline"]["macro_f1"]
    candidate_wins = gain_test > 0
    supported = candidate_wins if TASK2_DECISION == "keep" else not candidate_wins
    selected = "candidate" if (TASK2_DECISION == "keep" and candidate_wins) else "baseline"
    out += [
        "",
        "## DECISION CHECK",
        f"candidate minus baseline (macro-F1): validation {gain_val:+.4f} | {EVAL_SPLIT} {gain_test:+.4f}",
        f"Task 2 decision: {TASK2_DECISION}",
        f"Test results support the Task 2 decision: {supported}",
        f"Selected routing model (frozen rule): {selected}",
    ]
    text = "\n".join(out)
    METRICS_PATH.write_text(text + "\n", encoding="utf-8")
    print(text)


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else ""
    if stage == "freeze":
        freeze()
    elif stage == "test":
        run_test()
    else:
        print("Usage: python task.py freeze | test")
```

Run it **once**: `python hw_4/Task3/task.py test`.

---

## Step 5 — Read the result

The output is in the terminal and in `test_metrics.txt`.

- **Decision check.** "Support" means: if you kept the candidate, it beats the
  baseline on test macro-F1. If you reverted, it does not.
- **Validation vs test.** Small drops or gains on both models are normal. The two
  sets are different tickets. What matters is whether the **gap** between the
  models keeps the same sign.
- **Biggest shifts.** Small departments (General Inquiry 53 tickets, Human
  Resources 71) move a lot by chance. Say so. Do not read too much into them.
- **If test disagrees with Task 2.** Write that plainly. Do not retrain, and do not
  edit either model. The frozen rule picks the model.

---

## Step 6 — Write the report

Save as `hw_4/Task3/test_comparison_report.md`. Paste the numbers from
`test_metrics.txt`. Keep the explanations short.

```md
# Task 3 — Test Comparison Report

## Freeze
- Baseline and candidate models frozen (hashes in freeze.txt) before the test run.
- Task 2 decision: ...
- Selection rule: ...

## Metrics and confusion matrices
### Baseline
- accuracy, macro-F1, weighted-F1
- per-department metrics, confusion matrix
### Candidate
- same

## Validation vs test
- Each model's macro-F1 and accuracy, validation vs test.
- Departments with the biggest shifts, and why (small support?).

## Does the test support the Task 2 decision?
- Yes or no, with the macro-F1 numbers.

## Selected routing model
- Baseline or candidate, by the frozen rule, with the reason.
```

## Checklist

- [ ] Dry run on validation passed, and its files were deleted.
- [ ] `freeze.txt` was created before the test run.
- [ ] The test stage ran once. Both test CSVs have 4 columns and 3,755 rows.
- [ ] Metrics and confusion matrices are in the report for both models.
- [ ] Validation-vs-test differences are explained.
- [ ] The report says whether the test supports the Task 2 decision.
- [ ] The selected model follows the frozen rule.
- [ ] No model was changed or retrained after the test.
