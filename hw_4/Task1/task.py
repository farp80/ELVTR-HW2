import json
import sys
from collections import Counter
from pathlib import Path

import pandas as pd
from sklearn.metrics import accuracy_score, classification_report, f1_score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))

from shared.classes.ticket_routing_classifier import TicketRoutingClassifier

HW3 = ROOT / "hw_3"
PREFIX = "Fidel Alejandro Rosell Perez - "
REVIEW_PATH = HERE / "ticket_review.json"
ANALYSIS_PATH = HERE / "analysis.md"
EVIDENCE_HEADER = "## TICKETS' EVIDENCE ##"

# 1. Load the data. Only the validation predictions are used.
prediction = pd.read_csv(HW3 / f"{PREFIX}validation_predictions.csv")
cleaned = pd.read_csv(HW3 / f"{PREFIX}support_tickets_cleaned.csv")

for frame in (prediction, cleaned):
    frame["ticket_id"] = pd.to_numeric(frame["ticket_id"]).astype(int)

bodies = cleaned.loc[
    cleaned["ticket_id"].isin(prediction["ticket_id"]), ["ticket_id", "body"]
]
val = prediction.merge(bodies, on="ticket_id", how="left", validate="one_to_one")
val["body"] = val["body"].fillna("")
val["is_error"] = val["true_label"] != val["recommended_department"]
val["scores"] = val["class_scores"].apply(json.loads)

# The Homework 3 model is only loaded. It is never fitted or saved here.
clf = TicketRoutingClassifier.load(HW3 / f"{PREFIX}hw3_ml_baseline.pkl")

print("validation rows:", len(val), "| errors:", int(val["is_error"].sum()))

# 2. Reproduce the Homework 3 metrics.
y_true, y_pred = val["true_label"], val["recommended_department"]
print("accuracy   :", round(accuracy_score(y_true, y_pred), 3))  # report: 0.472
print("macro-F1   :", round(f1_score(y_true, y_pred, average="macro"), 3))  # 0.482
print("weighted-F1:", round(f1_score(y_true, y_pred, average="weighted"), 3))  # 0.473
print(classification_report(y_true, y_pred, digits=3))

# 3. Biggest repeated mistakes (rows = true department, columns = predicted).
labels = sorted(val["true_label"].unique())
cm = pd.crosstab(val["true_label"], val["recommended_department"]).reindex(
    index=labels, columns=labels, fill_value=0
)

pairs = cm.stack().rename("incorrect_count").reset_index()
pairs = pairs[pairs["true_label"] != pairs["recommended_department"]].copy()
pairs["true_support"] = pairs["true_label"].map(cm.sum(axis=1))
pairs["share_of_true_dept"] = (pairs["incorrect_count"] / pairs["true_support"]).round(
    3
)
print(
    pairs.sort_values("incorrect_count", ascending=False)
    .head(10)
    .to_string(index=False)
)

# Weak slice check: accuracy and macro-F1 by body length (same cuts as the report).
val["body_chars"] = val["body"].str.len()
short_cut, long_cut = val["body_chars"].quantile([0.33, 0.66])
val["length_slice"] = val["body_chars"].apply(
    lambda n: "short" if n <= short_cut else ("medium" if n <= long_cut else "long")
)
for name, grp in val.groupby("length_slice"):
    print(
        f"{name:6s} n={len(grp):4d} "
        f"acc={accuracy_score(grp.true_label, grp.recommended_department):.3f} "
        f"macroF1={f1_score(grp.true_label, grp.recommended_department, average='macro'):.3f}"
    )

# 4. The slice: true Technical Support, predicted IT Support.
TRUE_LABEL = "Technical Support"
PREDICTED_LABEL = "IT Support"

in_slice = (val["true_label"] == TRUE_LABEL) & (
    val["recommended_department"] == PREDICTED_LABEL
)
n_slice = int(in_slice.sum())
reverse = (val["true_label"] == PREDICTED_LABEL) & (
    val["recommended_department"] == TRUE_LABEL
)

print(f"Slice: true={TRUE_LABEL!r}, predicted={PREDICTED_LABEL!r}")
print("records in slice               :", n_slice)
print("all Technical Support tickets  :", int((val.true_label == TRUE_LABEL).sum()))
print(
    "all predicted IT Support       :",
    int((val.recommended_department == PREDICTED_LABEL).sum()),
)
print("share of all validation errors :", round(n_slice / val["is_error"].sum(), 3))
print("reverse direction (IT -> TS)   :", int(reverse.sum()))

# 5. Select the first 30 errors by ticket_id.
N = 30
eligible = val[in_slice & val["is_error"]].sort_values("ticket_id")
sample = eligible.head(N).copy()

print("eligible records:", len(eligible), "| inspected:", len(sample))
print(sample["ticket_id"].tolist())

# 6. Evidence for each ticket (scores and the words behind the prediction).
classes = list(clf.model.classes_)
terms = clf.vectorizer.get_feature_names_out()

# Per-word pull toward the predicted department (model classes are lowercase).
w_diff = (
    clf.model.coef_[classes.index(PREDICTED_LABEL.lower())]
    - clf.model.coef_[classes.index(TRUE_LABEL.lower())]
)


def explain(body, top=6):
    """Words pushing toward the predicted department and toward the true one."""
    x = clf.vectorizer.transform(clf.prepare_texts(body)).tocoo()
    contrib = sorted(
        ((terms[j], float(v * w_diff[j])) for j, v in zip(x.col, x.data)),
        key=lambda t: t[1],
    )
    return {
        "n_known_terms": int(x.nnz),
        "toward_pred": [(t, round(c, 3)) for t, c in reversed(contrib[-top:]) if c > 0],
        "toward_true": [(t, round(c, 3)) for t, c in contrib[:top] if c < 0],
    }


sample["score_pred"] = sample["scores"].apply(lambda s: s[PREDICTED_LABEL])
sample["score_true"] = sample["scores"].apply(lambda s: s[TRUE_LABEL])
sample["score_gap"] = (sample["score_pred"] - sample["score_true"]).round(4)


TICKET_FIELDS = ("failure_category", "category_rationale", "why_model_predicted")
CATEGORY_FIELDS = (
    "definition",
    "likely_performance_impact",
    "addressable_by_model_or_preprocessing",
    "addressable_reason",
)
TASK2_FIELDS = (
    "category",
    "single_change",
    "expected_improvement",
    "possible_regression",
)


def build_review_template():
    tickets = []
    for _, r in sample.iterrows():
        e = explain(r["body"])
        top3 = sorted(r["scores"].items(), key=lambda kv: kv[1], reverse=True)[:3]
        tickets.append(
            {
                "ticket_id": int(r["ticket_id"]),
                "true_label": r["true_label"],
                "recommended_department": r["recommended_department"],
                "body": r["body"],
                "evidence": {
                    "score_predicted": float(r["score_pred"]),
                    "score_true": float(r["score_true"]),
                    "score_gap": float(r["score_gap"]),
                    "top3_scores": [[k, float(v)] for k, v in top3],
                    "body_chars": int(r["body_chars"]),
                    "n_known_terms": e["n_known_terms"],
                    "terms_toward_predicted": e["toward_pred"],
                    "terms_toward_true": e["toward_true"],
                },
                "failure_category": "",  # must match a category name below
                "category_rationale": "",  # why this ticket is in that category
                "why_model_predicted": "",  # why the model chose IT Support
            }
        )

    return {
        "slice": {
            "true_label": TRUE_LABEL,
            "predicted_label": PREDICTED_LABEL,
            "records_in_slice": n_slice,
            "inspected": len(tickets),
        },
        "tickets": tickets,
        "categories": [
            {
                "name": "",
                "definition": "",
                "likely_performance_impact": "",
                "addressable_by_model_or_preprocessing": "",  # Yes / No / Partly
                "addressable_reason": "",
            }
        ],
        "task2_candidate": {
            "category": "",
            "single_change": "",
            "expected_improvement": "",
            "possible_regression": "",
        },
    }


def named_categories(review):
    return {c["name"].strip(): c for c in review["categories"] if c["name"].strip()}


def review_problems(review):
    """Things still missing. An empty list means the JSON is ready."""
    problems = []

    if [t["ticket_id"] for t in review["tickets"]] != sample["ticket_id"].tolist():
        problems.append("ticket list in the JSON differs from the selected sample")

    categories = named_categories(review)
    if not categories:
        problems.append("no category defined")
    for name, c in categories.items():
        for key in CATEGORY_FIELDS:
            if not str(c.get(key, "")).strip():
                problems.append(f"category '{name}': '{key}' is empty")

    for t in review["tickets"]:
        for key in TICKET_FIELDS:
            if not str(t[key]).strip():
                problems.append(f"ticket {t['ticket_id']}: '{key}' is empty")
        category = t["failure_category"].strip()
        if category and category not in categories:
            problems.append(
                f"ticket {t['ticket_id']}: category '{category}' is not defined"
            )

    task2 = review["task2_candidate"]
    for key in TASK2_FIELDS:
        if not str(task2.get(key, "")).strip():
            problems.append(f"task2_candidate: '{key}' is empty")
    if task2["category"].strip() and task2["category"].strip() not in categories:
        problems.append("task2_candidate: category is not defined")

    return problems


def render_findings(review):
    tickets = review["tickets"]
    categories = named_categories(review)
    counts = Counter(t["failure_category"].strip() for t in tickets)
    total_errors = int(val["is_error"].sum())

    lines = ["### Ticket findings", ""]
    for t in tickets:
        lines += [
            f"#### Ticket {t['ticket_id']}",
            f"- True label: {t['true_label']}",
            f"- Predicted label (recommended_department): {t['recommended_department']}",
            f"- Category: {t['failure_category'].strip()}",
            f"- Why this category: {t['category_rationale'].strip()}",
            f"- Why the model chose {t['recommended_department']}: {t['why_model_predicted'].strip()}",
            "",
        ]

    lines += ["### Failure categories", ""]
    for name, count in counts.most_common():
        c = categories[name]
        approx = round(count / len(tickets) * n_slice)
        pct = approx / total_errors * 100
        lines += [
            f"#### {name}",
            f"- Definition: {c['definition'].strip()}",
            f"- Count: {count} of {len(tickets)}",
            (
                f"- Impact: {c['likely_performance_impact'].strip()} "
                f"Estimate for the whole slice: about {approx} of the {n_slice} tickets "
                f"({pct:.1f}% of all {total_errors} validation errors). "
                f"It comes from the first {len(tickets)} tickets, so it is only an estimate."
            ),
            (
                f"- Can a model or preprocessing change fix it? "
                f"{c['addressable_by_model_or_preprocessing'].strip()}. {c['addressable_reason'].strip()}"
            ),
            "",
        ]
    lines += [f"The counts add up to {sum(counts.values())} tickets.", ""]

    task2 = review["task2_candidate"]
    lines += [
        "### Task 2 candidate",
        f"- Category to target: {task2['category'].strip()}",
        f"- Change to try: {task2['single_change'].strip()}",
        f"- Expected gain: {task2['expected_improvement'].strip()}",
        f"- Risk: {task2['possible_regression'].strip()}",
    ]
    return "\n".join(lines)


def write_to_analysis(findings):
    text = ANALYSIS_PATH.read_text(encoding="utf-8")
    before = text.partition(EVIDENCE_HEADER)[0].rstrip()
    ANALYSIS_PATH.write_text(
        f"{before}\n\n{EVIDENCE_HEADER}\n\n{findings}\n", encoding="utf-8"
    )


if not REVIEW_PATH.exists():
    REVIEW_PATH.write_text(
        json.dumps(build_review_template(), indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Created {REVIEW_PATH}. Fill it in and run this script again.")
else:
    review = json.loads(REVIEW_PATH.read_text(encoding="utf-8"))
    problems = review_problems(review)
    if problems:
        print(f"{REVIEW_PATH.name} is not complete ({len(problems)} items missing):")
        for p in problems[:20]:
            print(" -", p)
    else:
        write_to_analysis(render_findings(review))
        print(f"Findings written to {ANALYSIS_PATH}")
