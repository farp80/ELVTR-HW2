import joblib
import pandas as pd
from sklearn.linear_model import LogisticRegression

class MLBaseline:
    def __init__(self, vectorizer_path, model=None):
        self.vectorizer_path = vectorizer_path
        self.vectorizer = joblib.load(vectorizer_path)
        self.model = model or LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=42,
    )

    def fit(self, train_bodies, train_labels):
        X_train = self.vectorizer.transform(self._prepare_texts(train_bodies))
        self.model.fit(X_train, train_labels)
        return self

    def predict(self, ticket_body):
        X = self.vectorizer.transform(self._prepare_texts(ticket_body))

        probabilities = self.model.predict_proba(X)[0] 
        classes = self.model.classes_
        #identifies the highest-scoring department.
        best_index = probabilities.argmax()

        return {
            "recommended_department": self._format_label(classes[best_index]),
            "class_scores": {
                self._format_label(label): round(float(score), 4)
                for label, score in zip(classes, probabilities)
            },
        }

    def save(self, model_path):
        joblib.dump(self, model_path)

    def _prepare_texts(self, texts):
        """ - A single string must be wrapped in a list.
            - Missing values should become empty strings.
            - All values should be converted to strings before vectorization."""
        if isinstance(texts, str):
            return [texts]

        if isinstance(texts, pd.Series):
            return texts.fillna("").astype(str)

        return pd.Series(texts).fillna("").astype(str)

    def _format_label(self, label):
        """- Converts department names to title case for consistency."""
        return str(label).title()

    @classmethod
    def load(cls, model_path):
        return joblib.load(model_path)