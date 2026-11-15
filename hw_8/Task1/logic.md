# Task 1 — Routing-review policy

## Reasoning

The Homework 4 model picks the wrong department on 1,885 of 3,755 validation tickets. A person checks only the tickets where the model is unsure. `class_scores` holds one score per department, and the ten add up to 1. Close top two scores mean the model is unsure.

Ticket 24 scores IT Support 0.1923 and Technical Support 0.1916. The gap is 0.0007, so a person checks it. The model is wrong there. Ticket 19 scores Billing 0.9241 and Sales 0.0318. The gap is 0.8923, so it skips review. The model is right there.

Three rules flag a ticket:

- Margin: the top-two gap is below 0.05.
- Ratio: the second score is at least 80% of the top score.
- Entropy: the ten scores are spread evenly, above 2.10 (2.303 means all equal).

| Rule | Sent to a person | Errors caught | Unsent tickets right |
| --- | --- | --- | --- |
| Margin | 1,447 | 971 | 60.4% |
| Ratio | 1,349 | 897 | 58.9% |
| Entropy | 1,335 | 890 | 58.9% |

Each rule sends a similar number of tickets. Margin catches the most errors, so the workflow uses margin.

## Where class_scores come from

The Homework 4 model's predictions file was never kept on disk. `hw_3\...validation_predictions.csv` holds the Homework 3 baseline, so it is the wrong model. `build_predictions` retrains the Homework 4 model with the same settings and stop words as `hw_4\Task2\task.py`. The ticket data and the train/validation split live in `hw_3`. Homework 4 reads them from there too, so `DATA_DIR` points to `hw_3`. It calls `predict` on every validation ticket. `predict` returns `class_scores`, one probability per department from `predict_proba`. The function writes `validation_predictions.csv` next to the script. That file is the Task 1 predictions deliverable.

## How to run

From `hw_8\Task1`, run `python validation_precision.py`. The first run builds the CSV in about 30 seconds. Later runs read the saved CSV. The output is:

```text
tickets=3755 wrong=1885
margin: flagged=1447 caught=971 flag_wrong=0.671 auto_right=0.604
ratio: flagged=1349 caught=897 flag_wrong=0.665 auto_right=0.589
entropy: flagged=1335 caught=890 flag_wrong=0.667 auto_right=0.589
```

## Logic

```python
import csv
import json
import math
import sys
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from shared.classes.ticket_routing_classifier import LABEL_NAMES, TicketRoutingClassifier

DATA_DIR = ROOT / "hw_3"
PREFIX = "Fidel Alejandro Rosell Perez - "
PREDICTIONS = HERE / "validation_predictions.csv"


def build_predictions(path):
    cleaned = pd.read_csv(DATA_DIR / f"{PREFIX}support_tickets_cleaned.csv")
    split = pd.read_csv(DATA_DIR / f"{PREFIX}split_manifest.csv")
    data = cleaned.merge(split, on="ticket_id", how="inner")
    train = data[data["split"] == "train"]
    validation = data[data["split"] == "validation"]

    clf = TicketRoutingClassifier()
    clf.vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        stop_words="english",
    )
    clf.fit(train["body"], train["department"])

    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["ticket_id", "true_label", "recommended_department", "class_scores"],
        )
        writer.writeheader()
        for ticket_id, body, department in zip(
            validation["ticket_id"], validation["body"], validation["department"]
        ):
            prediction = clf.predict(body)
            writer.writerow(
                {
                    "ticket_id": ticket_id,
                    "true_label": LABEL_NAMES[department],
                    "recommended_department": prediction["recommended_department"],
                    "class_scores": json.dumps(prediction["class_scores"]),
                }
            )


def rule_flags(class_scores):
    ordered = sorted(class_scores.values(), reverse=True)
    top, second = ordered[0], ordered[1]
    margin = round(top - second, 4)
    ratio = round(second / top, 4)
    spread = round(
        -sum(score * math.log(score) for score in class_scores.values() if score > 0),
        4,
    )
    return {
        "margin": margin < 0.05,
        "ratio": ratio >= 0.80,
        "entropy": spread > 2.10,
    }


def load_rows(path):
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        for item in csv.DictReader(handle):
            rows.append(
                {
                    "correct": item["true_label"] == item["recommended_department"],
                    "class_scores": json.loads(item["class_scores"]),
                }
            )
    return rows


def evaluate(rows):
    scored = [(row["correct"], rule_flags(row["class_scores"])) for row in rows]
    wrong = sum(not correct for correct, _flags in scored)
    print(f"tickets={len(scored)} wrong={wrong}")
    for name in ("margin", "ratio", "entropy"):
        flagged = [correct for correct, flags in scored if flags[name]]
        caught = sum(not correct for correct in flagged)
        auto = [correct for correct, flags in scored if not flags[name]]
        print(
            f"{name}: flagged={len(flagged)} caught={caught} "
            f"flag_wrong={caught / len(flagged):.3f} "
            f"auto_right={sum(auto) / len(auto):.3f}"
        )


def review_decision(class_scores):
    ordered = sorted(class_scores.values(), reverse=True)
    margin = round(ordered[0] - ordered[1], 4)
    return margin < 0.05, margin


if __name__ == "__main__":
    if not PREDICTIONS.exists():
        build_predictions(PREDICTIONS)
    evaluate(load_rows(PREDICTIONS))
```
