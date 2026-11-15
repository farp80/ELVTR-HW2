import re

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

LABEL_NAMES = {
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


class TicketRoutingClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            min_df=2,
            max_df=0.95,
        )

        self.model = LogisticRegression(
            max_iter=1000, class_weight="balanced", random_state=42
        )

    def clean_text(self, text):
        """Cleans the text of the input data."""
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
        """Fits the model to the training data."""
        x_train = self.prepare_texts(train_bodies)
        X_train = self.vectorizer.fit_transform(x_train)
        self.model.fit(X_train, train_labels)

    def predict(self, ticket_body):
        """Predicts the class of the input data."""
        cleaned_body = self.prepare_texts(ticket_body)
        X = self.vectorizer.transform(cleaned_body)
        probabilities = self.model.predict_proba(X)[0]
        classes = self.model.classes_
        best_index = probabilities.argmax()

        return {
            "recommended_department": LABEL_NAMES[classes[best_index]],
            "class_scores": {
                LABEL_NAMES[label]: round(float(score), 4)
                for label, score in zip(classes, probabilities)
            },
        }

    def predit_many(self, ticket_bodies):
        """Predicts the class of the input data."""
        return [self.predict(ticket_body) for ticket_body in ticket_bodies]

    def save(self, model_path):
        joblib.dump(self, model_path)

    @classmethod
    def load(cls, model_path):
        return joblib.load(model_path)
