# Homework 4, Task 1 - Validation Error Analysis (step by step, with code)

Goal: find one repeated mistake of the classifier, read 30 of those tickets, find out why
each one failed, group them into categories, and say which categories a change can fix.

**How it works**

- Put all the code blocks below, in order, into `hw_4/Task1/task.py`.
- Run `python hw_4/Task1/task.py`. You run it three times:
  1. First run: it prints the numbers and creates `ticket_review.json`.
  2. You read the tickets and fill in `ticket_review.json`.
  3. Second run: it checks the JSON and writes the findings into `analysis.md`.
- The deliverable is `analysis.md`. You write the first part by hand (slice and
  rationale, selection rule). The script writes the part under `## TICKETS' EVIDENCE ##`.

## Rules

- Use validation tickets only. Do not open or predict the test split.
- Do not fit, save or change the Homework 3 model. Only load it.
- The model reads only `body`. Other columns are for analysis only.
- Write the selection rule before you read any ticket text.

## Files used (all from `hw_3/`)

- `... - validation_predictions.csv`: `ticket_id`, `true_label`, `recommended_department`, `class_scores`.
- `... - support_tickets_cleaned.csv`: `ticket_id`, `body`.
- `... - hw3_ml_baseline.pkl`: the trained classifier.

---

## Step 1 - Imports and paths

```python
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
```

---

## Step 2 - Load the validation data

**What:** read the predictions and the ticket text, and join them in one table, `val`.

**Why:** every later step uses this one table. The bodies are pulled only for the
ticket IDs in the validation predictions, so no other ticket text is read.

```python
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
```

**Check:** 3,755 validation rows and 1,982 errors.

---

## Step 3 - Reproduce the Homework 3 numbers

**What:** compute accuracy, macro-F1 and weighted-F1 from the prediction file.

**Why:** if your numbers match the Homework 3 report, you are looking at the same
predictions. If they do not, stop and find out why.

```python
# 2. Reproduce the Homework 3 metrics.
y_true, y_pred = val["true_label"], val["recommended_department"]
print("accuracy   :", round(accuracy_score(y_true, y_pred), 3))  # report: 0.472
print("macro-F1   :", round(f1_score(y_true, y_pred, average="macro"), 3))  # 0.482
print("weighted-F1:", round(f1_score(y_true, y_pred, average="weighted"), 3))  # 0.473
print(classification_report(y_true, y_pred, digits=3))
```

**Check:** accuracy 0.472, macro-F1 0.482, weighted-F1 0.473.

---

## Step 4 - Find the repeated mistakes

**What:** list every "true A predicted as B" pair, biggest first. Then check the
weak slice by body length.

**Why:** you want a mistake that is big and specific. A big count gives you enough
tickets to test a fix in Task 2. The share of the true department keeps you from
picking a tiny department by accident.

```python
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
```

**Result:** the biggest pair is Technical Support predicted as IT Support (159
tickets). Short bodies are the weakest by length, but their errors come from every
department. A fix aimed at "short tickets" is too broad.

---

## Step 5 - Choose the slice

**What:** define the slice with one rule and count it.

**Choice:** true label `Technical Support`, predicted `IT Support`.

**Why:**

- It is the biggest pair (159 tickets), far above the 30 required.
- Both departments are big, so this is not a small-sample accident.
- They share words (software, access, errors), so the text gives you something to explain.
- Other options are weaker. Billing is already strong. Returns and Exchanges errors
  are spread over many departments.

```python
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
```

**Write in `analysis.md`:** the slice, the 159 count, the share of all errors (0.08),
two sentences on why it beats the other pairs, and a note that the reverse
direction (IT predicted as Technical Support, 107 tickets) exists. A fix could move
errors instead of removing them.

---

## Step 6 - Select the 30 tickets with a fixed rule

**The rule (copy it into `analysis.md` before you read tickets):**

1. Keep the slice: true Technical Support, predicted IT Support.
2. Keep only wrong predictions.
3. Sort by `ticket_id`, as a number.
4. Take the first 30.

**Why:** anyone with the same file gets the same 30 tickets. You cannot choose
tickets that fit a story you like.

```python
# 5. Select the first 30 errors by ticket_id.
N = 30
eligible = val[in_slice & val["is_error"]].sort_values("ticket_id")
sample = eligible.head(N).copy()

print("eligible records:", len(eligible), "| inspected:", len(sample))
print(sample["ticket_id"].tolist())
```

---

## Step 7 - Find the words behind each prediction

**What:** for each ticket, measure how much each word pushed the model toward IT
Support or toward Technical Support.

**Why:** the class scores tell you what the model chose, not why. This model is
TF-IDF plus logistic regression. For each word, the pull is its TF-IDF value times
the weight difference between the two departments. A positive pull is toward IT
Support. A negative pull is toward Technical Support.

```python
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
```

---

## Step 8 - Create the review file

**What:** the script writes one entry per ticket into `ticket_review.json`. Each
entry has the ticket text, the scores and the word lists. You fill in three fields.

```python
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
```

**Fill in `ticket_review.json`.** Read the tickets slowly. For each one:

- `failure_category`: the category name.
- `category_rationale`: why the ticket fits that category. Quote the ticket.
- `why_model_predicted`: the words and scores behind the prediction.

If the evidence is not clear, write "cause unclear". Do not invent a cause.

Then fill `categories` (one entry per category) and `task2_candidate`. Remove the
empty example entry in `categories`.

---

## Step 9 - Define the categories

Name 3 to 6 categories. Each one describes a cause, not the labels.

- Every ticket gets exactly one category.
- Write a one or two sentence definition for each.
- "Cause unclear" is allowed.

The categories I used: Generic words (12 tickets), Network and server words (10),
Label could be IT Support (5), Very short ticket (3).

For each category, fill in:

- `likely_performance_impact`: how many of the 30, and what share of the errors.
- `addressable_by_model_or_preprocessing`: Yes, No or Partly.
- `addressable_reason`: the reason in one or two sentences.

Rule of thumb: word-weight problems can be fixed by a model or text change. A
ticket with too little text, or a label that is debatable, cannot.

Keep the estimates honest. Say "about N of the 30". Thirty tickets cannot prove an
effect on the whole validation set.

---

## Step 10 - Check the JSON

**What:** list everything still empty or wrong in the JSON.

**Why:** the findings are written only when the JSON is complete.

```python
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
```

---

## Step 11 - Write the findings into analysis.md

**What:** for each ticket, write the ID, true label, predicted label, category,
rationale and model explanation. Then write each category with its count, impact
and addressable answer. Then write the Task 2 candidate.

**Why:** it writes everything under `## TICKETS' EVIDENCE ##` and keeps the part
above it. You can run it again safely.

```python
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
```

---

## Step 12 - Run it

**What:** the last block decides what to do. No JSON: it creates the template. JSON
incomplete: it lists what is missing. JSON complete: it writes `analysis.md`.

```python
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
```

---

## Step 13 - Choose the Task 2 candidate

Fill `task2_candidate` in the JSON. Pick the category that is addressable, has a
clear reason, and has the most tickets. State:

- The category and its count.
- One change only.
- What you expect to improve.
- What might get worse (for example IT Support recall).

My choice: Generic words, remove very common words (stop words).

---

## analysis.md outline

```md
## Slice selection
(slice, count, rationale, reverse direction)

## Selecting 30 records
(the four-line rule)

## TICKETS' EVIDENCE
(written by the script: ticket findings, failure categories, Task 2 candidate)
```

## Checklist

- [ ] The Homework 3 numbers were reproduced.
- [ ] The slice has at least 30 errors and the choice is explained.
- [ ] The selection rule was written before reading tickets.
- [ ] Each of the 30 tickets has an ID, true label, predicted label, category,
      rationale and model explanation.
- [ ] Each ticket has one category, and the counts add up to 30.
- [ ] Each category has an impact note and an addressable answer with a reason.
- [ ] Claims cite words or scores. "Cause unclear" is used where needed.
- [ ] No test ticket was read. The Homework 3 model and data were not changed.
