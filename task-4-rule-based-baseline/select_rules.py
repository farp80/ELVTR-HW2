import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.pandas_utils import PandasUtils
from utils.shared import score_phrase, score_words, words_in

data_cleaned_base = PandasUtils(
    file_path=r"D:\ELVTR\homeworks\ELVTR-HW2\Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
)
splitted_base = PandasUtils(
    file_path=r"D:\ELVTR\homeworks\ELVTR-HW2\Fidel Alejandro Rosell Perez - support_tickets_splitted.csv"
)

current_df = data_cleaned_base.df.merge(splitted_base.df, on="ticket_id", how="left")

trained_df = current_df[current_df["split"] == "train"].copy()
total_rows = len(trained_df)

# in_class       = matching tickets whose department is the rule's department
# out_of_class   = matching tickets whose department is anything else
# majority_hits  = matching tickets whose department is technical support
# gain           = in_class - majority_hits
# precision      = in_class / (in_class + out_of_class)
# coverage       = (in_class + out_of_class) / 20749

MAJORITY = "technical support"
DEPARTMENTS = ["product support", "customer service", "it support"]

## Step 1. Count words on the training rows: Count it once per ticket, under that ticket's department.
counts = {label: Counter() for label in trained_df["department"].unique()}

for body, label in zip(trained_df["body"].fillna(""), trained_df["department"]):
    for word in words_in(body):
        if len(word) < 3:
            continue
        counts[label][word] += 1

## Step 2. Rank those words by gain
for label in DEPARTMENTS:
    print(label)
    for row in score_words(counts, label, len(trained_df))[:15]:
        print(
            row["phrase"],
            row["in_class"],
            row["out_of_class"],
            row["majority_hits"],
            row["gain"],
            round(row["precision"], 2),
            round(row["coverage"], 4),
        )

## Step 3. Score a phrase taken from a real ticket
# 3.1 pick one word from the list of words
# 3.2 pick one department from the list of departments
# 3.3 score the phrase
# 3.4 print the results

word = "engagement"
label = "product support"
matches = trained_df["body"].fillna("").str.lower().str.contains(word, regex=False)
print(
    trained_df.loc[matches & (trained_df["department"] == label), "body"]
    .head(3)
    .tolist()
)

engagement_scores = score_phrase(trained_df, label, "engagement")
print(score_phrase(trained_df, label, "low engagement"))
print(score_phrase(trained_df, label, "engagement metrics"))
print("-" * 60)
word = "learning"
label = "customer service"
matches = trained_df["body"].fillna("").str.lower().str.contains(word, regex=False)
print(
    trained_df.loc[matches & (trained_df["department"] == label), "body"]
    .head(3)
    .tolist()
)
learning_scores = score_phrase(trained_df, label, "learning")
print(score_phrase(trained_df, label, "machine learning"))
print(score_phrase(trained_df, label, "interested in learning"))
print("-" * 60)
word = "inaccessibility"
label = "it support"
matches = trained_df["body"].fillna("").str.lower().str.contains(word, regex=False)
print(
    trained_df.loc[matches & (trained_df["department"] == label), "body"]
    .head(3)
    .tolist()
)
inaccessibility_scores = score_phrase(trained_df, label, "inaccessibility")
print(score_phrase(trained_df, label, "inaccessibility of figma"))
print("-" * 60)

# Step 4: Keep the word with the biggest gain
prd_word_mapping = {
    "product support": "engagement",
    "customer service": "learning",
    "it support": "inaccessibility",
}

scores = {
    "product support": engagement_scores,
    "customer service": learning_scores,
    "it support": inaccessibility_scores,
}
rules = []

for department, word in prd_word_mapping.items():
    rules.append(
        {
            "department": department,
            "type": "word",
            "description": f"If the word '{word}' is in the body, return the department {department}",
            "rationale": f"Fixes {scores[department]['in_class']} product-support tickets and breaks {scores[department]['out_of_class']} technical-support tickets, for a gain of {scores[department]['gain']}.",
            "phrase": word,
            "in_class": scores[department]["in_class"],
            "out_of_class": scores[department]["out_of_class"],
            "majority_hits": scores[department]["majority_hits"],
            "gain": scores[department]["gain"],
            "precision": scores[department]["precision"],
            "coverage": scores[department]["coverage"],
        }
    )

settings = {
    "train_rows": len(trained_df),
    "majority_department": MAJORITY,
    "departments": DEPARTMENTS,
    "rules": rules,
}

output_path = ROOT / "possible_baselinerules.json"
with open(output_path, "w", encoding="utf-8") as file:
    json.dump(settings, file, indent=2)

## Step 7. Count correct training rows

# Sort the rules by precision, highest first.
# Read each training body once.
# The first phrase found in the body chooses the department.
#  When no phrase is found, predict `technical support`.

rules.sort(key=lambda rule: rule["precision"], reverse=True)
correct = 0

for body, actual in zip(trained_df["body"].fillna(""), trained_df["department"]):
    text = str(body).lower()
    prediction = MAJORITY
    for rule in rules:
        if rule["phrase"] in text:
            prediction = rule["department"]
            break
    if prediction == actual:
        correct += 1

print(f" Ruled based baseline: {correct}")
print(f" Percentage ruled based baseline: {correct / total_rows * 100:.2f}%")
