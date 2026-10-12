# Task 3.2 - Retrain and Apply the ML Model

This file explains how I should complete Task 3.2 step by step.

I am keeping the explanation beginner-friendly because the goal is to learn the
process, not to write advanced code.

The OOP classifier design is also explained in:

```text
oop_classifier_design.md
```

However, this file also includes the full class outline and the full workflow
because this main `.md` file should contain everything needed to understand Task
3.2.

## Requirement Summary

Task 3.2 asks me to:

1. Use the Homework 3 split manifest instead of the Homework 2 split.
2. Retrain the classifier using the new training split.
3. Apply the retrained classifier to every validation record.
4. Save a prediction CSV with exactly 4 columns:
   - `ticket_id`
   - `true_label`
   - `recommended_department`
   - `class_scores`
5. Make sure text-cleaning, preprocessing, and the ML model are inside the
   classifier class.
6. Make training and predictions reproducible.

## Required Input Files

These are the files that must be used:

```text
C:\Users\frosell\Downloads\ELVTR-HW2\Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv
```

```text
C:\Users\frosell\Downloads\ELVTR-HW2\hw_3\Fidel Alejandro Rosell Perez - split_manifest.csv
```

The cleaned ticket file has these columns:

```text
ticket_id
body
department
priority
tags
```

The Homework 3 split manifest has these columns:

```text
ticket_id
split
```

The split values are:

```text
train
validation
test
```

For Task 3.2, I should use:

- `train` for fitting the classifier
- `validation` for prediction output
- not `test`

The assignment says not to use the test split in this homework.

## Important Decision About Cleaning

I am using:

```text
support_tickets_cleaned.csv
```

That means the body text has already gone through my Homework 2 cleaning work.

However, Task 3.2 also says the classifier class should apply text-cleaning.
Because of that, the class should still include a simple `clean_text()` method.

This method does basic safe cleaning:

- handles missing text
- converts text to lowercase
- removes extra spaces

This is not advanced cleaning. It is included so the classifier owns the full
pipeline: cleaning, preprocessing, and model prediction.

## Important Decision About TF-IDF

Homework 2 already created and saved a TF-IDF vectorizer.

For Homework 3, I should not reuse the old fitted vectorizer as the final
preprocessor because the requirement says:

```text
Retrain the classifier (ML model + preprocessor) using the new training split.
```

So the Homework 3 class should create a new `TfidfVectorizer` and fit it only on
the Homework 3 canonical training split.

The Homework 2 vectorizer is still helpful because I can reuse the same settings:

```python
TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
)
```

This keeps the idea consistent while still following the Homework 3 requirement.

## Model Selection

Use logistic regression:

```python
LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42,
)
```

Why this model?

- It is a good basic baseline for text classification.
- It works with TF-IDF features.
- It is CPU-friendly.
- It can return probability scores with `predict_proba()`.
- `class_weight="balanced"` helps with the department imbalance.
- `random_state=42` helps make the result reproducible.

This is not meant to be the best possible model. It is a clear baseline.

## Step 1 - Import the Needed Libraries

The implementation needs these imports:

```python
import json
from pathlib import Path

import pandas as pd
```

The classifier file, shown in `oop_classifier_design.md`, also needs:

```python
import re
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
```

Why:

- `Path` helps create file paths.
- `pandas` loads and works with CSV files.
- `json` converts `class_scores` into a CSV-safe string.
- `joblib` saves the trained model.
- `TfidfVectorizer` creates text features.
- `LogisticRegression` trains the classifier.

## Step 2 - Set the File Paths

Use `Path` so the code is easier to read:

```python
ROOT = Path(r"C:\Users\frosell\Downloads\ELVTR-HW2")
HW3_ROOT = ROOT / "hw_3"

cleaned_path = ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
split_path = HW3_ROOT / "Fidel Alejandro Rosell Perez - split_manifest.csv"
model_path = HW3_ROOT / "Fidel Alejandro Rosell Perez - hw3_ml_baseline.pkl"
prediction_path = HW3_ROOT / "Fidel Alejandro Rosell Perez - validation_predictions.csv"
```

Why:

- `cleaned_path` points to the cleaned ticket data.
- `split_path` points to the official Homework 3 split.
- `model_path` is where the retrained classifier will be saved.
- `prediction_path` is where the validation predictions will be saved.

## Step 3 - Load the Two Required CSV Files

```python
cleaned_df = pd.read_csv(cleaned_path)
split_df = pd.read_csv(split_path)
```

Why:

- `cleaned_df` contains the ticket text and true department labels.
- `split_df` tells me which records are train, validation, or test.

## Step 4 - Merge the Data

```python
df = cleaned_df.merge(split_df, on="ticket_id", how="inner")
```

Why:

- Both files have `ticket_id`.
- The merge attaches the Homework 3 split to each cleaned ticket.
- `how="inner"` keeps only ticket IDs that exist in both files.

This matters because the Homework 3 split manifest is the official split.

## Step 5 - Create Training and Validation DataFrames

```python
train_df = df[df["split"] == "train"].copy()
validation_df = df[df["split"] == "validation"].copy()
```

Why:

- `train_df` is used to fit the classifier.
- `validation_df` is used to create predictions.
- The test split is not used in this homework.

## Step 6 - Create the Classifier

The class is also explained in:

```text
oop_classifier_design.md
```

But the full class outline is included here too, so this main file has
everything in one place.

```python
class TicketRoutingClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
        )

        self.model = LogisticRegression(
            max_iter=1000,
            class_weight="balanced",
            random_state=42,
        )

        self.label_names = {
            "billing and payments": "Billing and Payments",
            "customer service": "Customer Service",
            "general inquiry": "General Inquiry",
            "human resources": "Human Resources",
            "it support": "IT Support",
            "product support": "Product Support",
            "returns and exchanges": "Returns and Exchanges",
            "sales and pre-sales": "Sales and Pre-Sales",
            "service outages and maintenance": "Service Outages and Maintenance",
            "technical support": "Technical Support",
        }

    def clean_text(self, text):
        if pd.isna(text):
            return ""

        text = str(text)
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text

    def prepare_texts(self, texts):
        if isinstance(texts, str):
            texts = [texts]

        cleaned_texts = []

        for text in texts:
            cleaned_texts.append(self.clean_text(text))

        return cleaned_texts

    def fit(self, train_bodies, train_labels):
        cleaned_bodies = self.prepare_texts(train_bodies)
        X_train = self.vectorizer.fit_transform(cleaned_bodies)
        self.model.fit(X_train, train_labels)

        return self

    def predict(self, ticket_body):
        cleaned_body = self.prepare_texts(ticket_body)
        X = self.vectorizer.transform(cleaned_body)

        probabilities = self.model.predict_proba(X)[0]
        classes = self.model.classes_
        best_index = probabilities.argmax()

        return {
            "recommended_department": self.format_label(classes[best_index]),
            "class_scores": {
                self.format_label(label): round(float(score), 4)
                for label, score in zip(classes, probabilities)
            },
        }

    def predict_many(self, ticket_bodies):
        results = []

        for body in ticket_bodies:
            results.append(self.predict(body))

        return results

    def format_label(self, label):
        label = str(label)
        return self.label_names.get(label, label.title())

    def save(self, model_path):
        joblib.dump(self, model_path)

    @classmethod
    def load(cls, model_path):
        return joblib.load(model_path)
```

Why the class is written this way:

- `__init__()` creates the vectorizer, model, and label names.
- `clean_text()` keeps basic text cleaning inside the classifier.
- `prepare_texts()` makes one string or many strings safe for TF-IDF.
- `fit()` trains the TF-IDF preprocessor and model on training data.
- `predict()` returns the required dictionary with department and class scores.
- `predict_many()` is a simple helper for multiple tickets.
- `format_label()` makes labels look like the assignment example.
- `save()` stores the trained classifier.
- `load()` opens the saved classifier later.

Basic usage:

```python
classifier = TicketRoutingClassifier()
```

Why:

- This creates the text cleaner, TF-IDF vectorizer, and logistic regression
  model.
- The model is not trained until `.fit()` is called.
- The Homework 3 TF-IDF vectorizer is fitted during `.fit()`, using only the
  canonical Homework 3 training split.

## Step 7 - Train the Classifier

```python
classifier.fit(train_df["body"], train_df["department"])
```

Why:

- `train_df["body"]` is the input text.
- `train_df["department"]` is the correct label.
- Inside `fit()`, the class:
  1. cleans the text
  2. fits TF-IDF on training text
  3. trains logistic regression

This satisfies the requirement to retrain the ML model and preprocessor on the
new training split.

## Step 8 - Save the Retrained Model

```python
classifier.save(model_path)
```

Why:

- The trained classifier should be saved as an artifact.
- This makes the model reusable later.
- The saved object includes the fitted vectorizer and trained model.

## Step 9 - Predict Every Validation Record

Use a simple loop:

```python
rows = []

for _, row in validation_df.iterrows():
    prediction = classifier.predict(row["body"])

    rows.append(
        {
            "ticket_id": row["ticket_id"],
            "true_label": row["department"],
            "recommended_department": prediction["recommended_department"],
            "class_scores": json.dumps(prediction["class_scores"]),
        }
    )
```

Why:

- The requirement says to predict every validation record.
- Each row creates one prediction.
- `json.dumps()` turns the `class_scores` dictionary into a string that can be
  saved inside a CSV cell.

This loop is not the fastest possible approach, but it is clear for learning.

## Step 10 - Save the Prediction CSV

```python
prediction_df = pd.DataFrame(rows)
prediction_df.to_csv(prediction_path, index=False)
```

Why:

- This creates the required prediction CSV.
- `index=False` avoids adding an extra unwanted column.

The final CSV should have exactly these columns:

```text
ticket_id
true_label
recommended_department
class_scores
```

## Step 11 - Check the Output

After saving, check the first few rows:

```python
print(prediction_df.head())
print(prediction_df.columns.tolist())
print(prediction_df.shape)
```

Expected columns:

```text
['ticket_id', 'true_label', 'recommended_department', 'class_scores']
```

The number of rows should match the number of validation tickets.

In the Homework 3 split file, validation has 3,755 rows, so the prediction CSV
should also have 3,755 rows.

## Complete Workflow After the Class

After the `TicketRoutingClassifier` class, the workflow should look like this.

This is included here so the main `.md` file has the full process in one place.

```python
ROOT = Path(r"C:\Users\frosell\Downloads\ELVTR-HW2")
HW3_ROOT = ROOT / "hw_3"

cleaned_path = ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
split_path = HW3_ROOT / "Fidel Alejandro Rosell Perez - split_manifest.csv"
model_path = HW3_ROOT / "Fidel Alejandro Rosell Perez - hw3_ml_baseline.pkl"
prediction_path = HW3_ROOT / "Fidel Alejandro Rosell Perez - validation_predictions.csv"

cleaned_df = pd.read_csv(cleaned_path)
split_df = pd.read_csv(split_path)

df = cleaned_df.merge(split_df, on="ticket_id", how="inner")

train_df = df[df["split"] == "train"].copy()
validation_df = df[df["split"] == "validation"].copy()

classifier = TicketRoutingClassifier()
classifier.fit(train_df["body"], train_df["department"])
classifier.save(model_path)

rows = []

for _, row in validation_df.iterrows():
    prediction = classifier.predict(row["body"])

    rows.append(
        {
            "ticket_id": row["ticket_id"],
            "true_label": row["department"],
            "recommended_department": prediction["recommended_department"],
            "class_scores": json.dumps(prediction["class_scores"]),
        }
    )

prediction_df = pd.DataFrame(rows)
prediction_df.to_csv(prediction_path, index=False)

print(prediction_df.head())
print(prediction_df.columns.tolist())
print(prediction_df.shape)
```

What this produces:

```text
Fidel Alejandro Rosell Perez - hw3_ml_baseline.pkl
Fidel Alejandro Rosell Perez - validation_predictions.csv
```

The saved model file is created by:

```python
classifier.save(model_path)
```

The 4-column validation prediction CSV is created by:

```python
prediction_df.to_csv(prediction_path, index=False)
```

The CSV must contain:

```text
ticket_id
true_label
recommended_department
class_scores
```

## Step 12 - Reproducibility

The implementation is reproducible because:

- the official Homework 3 split manifest is used
- only the train split is used for fitting
- `random_state=42` is set in logistic regression
- the same cleaning and TF-IDF steps happen inside the class every time

## What Files Should Exist After Running the Real Code

Task 3.2 eventually needs these deliverables:

```text
Fidel Alejandro Rosell Perez - hw3_ml_baseline.pkl
Fidel Alejandro Rosell Perez - validation_predictions.csv
```

The `.pkl` file is the saved model.

The `.csv` file is the validation prediction output.

## What I Am Not Doing Here

I am not using the test split.

I am not changing the model after seeing validation results.

I am not trying to build the most advanced classifier.

I am not creating a `.py` file in this step because the current instruction is
to create Markdown instruction files only.

## Final Checklist

Before considering Task 3.2 complete, check:

- The cleaned support tickets CSV is used.
- The Homework 3 split manifest is used.
- The data is merged on `ticket_id`.
- The training split is used for `.fit()`.
- The validation split is used for predictions.
- The test split is not used.
- The classifier class includes cleaning, preprocessing, and the model.
- The preprocessor is fitted only on training text.
- The model is saved with `joblib`.
- The prediction CSV has exactly 4 columns.
- `class_scores` is saved as a JSON string.
- The prediction CSV has one row per validation ticket.

