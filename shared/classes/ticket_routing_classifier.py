import json
import re
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from shared.classes.ticket_preprocessor import TicketPreprocessor

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
    def __init__(self, cleaned_df, splitted_df):
        self.__cleaned_df = cleaned_df
        self.__splitted_df = splitted_df
        self.vectorizer = TicketPreprocessor(cleaned_df, splitted_df)
        self.model = LogisticRegression(max_iter=1000, class_weight='balanced', random_state=42)

    def clean_text(self, text):
        """ Cleans the text of the input data. """
        if pd.isna(text):
            return ""

        text = str(text)
        text = text.lower()
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text

    def fit(self):
        """ Fits the model to the training data. """
        X_train = self.vectorizer.fit_transform()
        self.model.fit(X_train,self.vectorizer.y_train)

    def predict(self, ticket_body):
        """ Predicts the class of the input data. """
        X = self.vectorizer.transform(ticket_body)
        probabilities = self.model.predict_proba(X)[0]
        classes = self.model.classes_
        best_index = probabilities.argmax()

        return {
            "recommended_department_name": LABEL_NAMES[classes[best_index]],
            "class_scores": {
                LABEL_NAMES[label]: round(float(score), 4) for label, score in zip(classes, probabilities)
            }
        }

    def predit_many(self, ticket_bodies):
        """ Predicts the class of the input data. """
        return [ self.predict(ticket_body) for ticket_body in ticket_bodies ]
        
    def save(self, model_path):
        joblib.dump(self.model, model_path)

    @classmethod
    def load(cls, model_path):
        return joblib.load(model_path)