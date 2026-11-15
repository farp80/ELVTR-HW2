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
