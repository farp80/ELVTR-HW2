# Task 3.2 OOP Classifier Design

This file explains the object-oriented design for Task 3.2.

The goal is not to write advanced production code. The goal is to build one
clear class that I can understand and reuse in future tasks.

## Why Use a Class?

Task 3.2 says the classifier class should take raw ticket text and handle:

- text cleaning
- preprocessing
- model training
- prediction
- saving and loading

That means the class should keep all model-related work in one place.

Without a class, the code can become scattered:

- one function cleans text
- another function vectorizes text
- another block trains the model
- another block predicts
- another block saves the model

With a class, all of those steps belong to one object:

```python
classifier = TicketRoutingClassifier()
classifier.fit(train_df["body"], train_df["department"])
result = classifier.predict("My account portal is offline")
classifier.save("model.pkl")
```

That is easier to reuse later.

## Important Homework 3 Rule

In Homework 2, a TF-IDF vectorizer was already created and saved.

For Homework 3, I should not just reuse the old fitted vectorizer as the final
preprocessor because Task 3.2 says:

```text
Retrain the classifier (ML model + preprocessor) using the new training split.
```

So the Homework 2 vectorizer is useful as a reference for the settings, but the
Homework 3 classifier should fit its own TF-IDF vectorizer using only the
canonical Homework 3 training split.

This avoids data leakage and follows the assignment requirement.

## Class Name

Use this class name:

```python
class TicketRoutingClassifier:
```

Why this name?

- `Ticket` says the input is support tickets.
- `Routing` says the model chooses the department.
- `Classifier` says it is a classification model.

## Imports

The class needs these imports:

```python
import json
import re
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
```

Explanation:

- `json` is used to serialize class scores for the prediction CSV.
- `re` is used for simple text cleaning.
- `joblib` saves and loads the trained classifier.
- `pandas` helps handle Series, lists, and missing values.
- `TfidfVectorizer` turns text into numbers.
- `LogisticRegression` is the ML classifier.

## Why TF-IDF?

The model cannot learn directly from normal text like:

```text
The customer cannot access the account portal.
```

The text needs to become numbers first.

TF-IDF gives higher value to words that are useful in a document but not too
common everywhere. For ticket routing, words like `refund`, `outage`,
`invoice`, or `password` may help identify the correct department.

Use these settings:

```python
TfidfVectorizer(
    lowercase=True,
    ngram_range=(1, 2),
    min_df=2,
    max_df=0.95,
)
```

Explanation:

- `lowercase=True` treats `Refund` and `refund` as the same word.
- `ngram_range=(1, 2)` uses single words and two-word phrases.
- `min_df=2` removes words that appear only once.
- `max_df=0.95` removes words that appear in almost every ticket.

## Why Logistic Regression?

Logistic Regression is not selected because it is the final best model for all
ticket-routing problems.

It is selected because this task needs a clear ML baseline that I can understand
and explain.

At this learning stage, I want a model where the flow makes sense:

```text
ticket text -> TF-IDF features -> model weights -> department probabilities
```

That is easier to understand than starting with a more advanced model.

Use:

```python
LogisticRegression(
    max_iter=1000,
    class_weight="balanced",
    random_state=42,
)
```

Explanation:

- It is CPU-friendly, so I can run it locally.
- It works well with TF-IDF text features because TF-IDF creates many sparse
  numeric columns.
- It is easier to reason about than deep learning models. It learns which words
  and phrases push the prediction toward each department.
- It supports `predict_proba()`, which helps create the required `class_scores`.
- `class_weight="balanced"` helps because some departments have many more
  tickets than others.
- `random_state=42` helps make results reproducible.

Models I am not choosing first:

- `MultinomialNB`: simple and fast, but it can be too simple for this routing
  problem.
- `LinearSVC`: often strong for text, but probability scores are not as direct.
- `RandomForestClassifier`: useful for many tabular problems, but not usually
  my first choice for sparse TF-IDF text.
- Transformers: powerful, but too complex for this baseline and harder to
  explain at this stage.

The practical reason is:

```text
Logistic Regression is a good first baseline because it is understandable,
fast, reproducible, and compatible with TF-IDF and probability scores.
```

If validation results are weak later, I can compare another model. But for this
homework, I should first build a baseline that I understand clearly.

## Full Class Draft

This code is shown here in Markdown for learning. It is not being created as a
`.py` file automatically.

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

## Method Explanation

### `__init__()`

This method runs when I create the classifier.

It creates:

- the TF-IDF vectorizer
- the logistic regression model
- the label formatting dictionary

Nothing is trained yet.

### `clean_text()`

This method does simple cleaning inside the classifier.

It:

- handles missing text
- converts text to lowercase
- replaces extra whitespace with one space
- removes whitespace at the start and end

Even though I am using `support_tickets_cleaned.csv`, keeping this method inside
the class satisfies the assignment rule that text-cleaning should be embedded in
the classifier.

### `prepare_texts()`

This method makes sure the classifier can handle:

- one string
- a list of strings
- a pandas Series

This is important because `TfidfVectorizer` expects a list-like object, not one
plain string.

### `fit()`

This method trains the preprocessor and the model.

Step by step:

1. Clean the training ticket bodies.
2. Fit the TF-IDF vectorizer on training text only.
3. Transform the text into numeric features.
4. Train logistic regression on those features.

This is where the Homework 3 preprocessor is retrained on the canonical training
split.

### `predict()`

This method predicts one ticket.

Step by step:

1. Clean the input ticket body.
2. Transform the text using the already-fitted vectorizer.
3. Get class probabilities from the model.
4. Find the highest probability.
5. Return a dictionary with:
   - `recommended_department`
   - `class_scores`

### `predict_many()`

This method predicts many tickets.

It is simple on purpose. It loops through ticket bodies and calls `predict()`.

This is not the fastest possible way, but it is easy to understand while
learning.

### `format_label()`

The dataset labels are lowercase, like:

```text
technical support
```

The output should look cleaner:

```text
Technical Support
```

This method converts labels to the display names expected in the output.

### `save()`

This method saves the trained classifier.

It saves the entire object, including:

- the trained TF-IDF vectorizer
- the trained logistic regression model
- the label formatting dictionary

### `load()`

This method loads the saved classifier later.

After loading, I should be able to call:

```python
loaded_classifier.predict("My invoice is wrong")
```

## What This Class Should Produce

For one ticket body, `predict()` returns:

```python
{
    "recommended_department": "Technical Support",
    "class_scores": {
        "Billing and Payments": 0.0312,
        "Customer Service": 0.0541,
        "General Inquiry": 0.0124,
        "Human Resources": 0.0048,
        "IT Support": 0.1103,
        "Product Support": 0.0855,
        "Returns and Exchanges": 0.0201,
        "Sales and Pre-Sales": 0.0150,
        "Service Outages and Maintenance": 0.0990,
        "Technical Support": 0.5686
    }
}
```

The exact numbers will depend on the trained model.

