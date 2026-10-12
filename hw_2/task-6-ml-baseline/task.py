"""Task 6 — Build an ML Baseline.

CPU-friendly classifier for department routing.
"""

from pathlib import Path

import sys
import pandas as pd
from ml_baseline import MLBaseline

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

cleaned_df = pd.read_csv(ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv")
split_df = pd.read_csv(ROOT / "Fidel Alejandro Rosell Perez - support_tickets_splitted.csv")
df = cleaned_df.merge(split_df, on="ticket_id", how="inner")
train_df = df[df["split"] == "train"].copy()

baseline = MLBaseline(
    vectorizer_path=ROOT / "Fidel Alejandro Rosell Perez - tfidf_vectorizer.pkl"
)

baseline.fit(train_df["body"], train_df["department"])
baseline.save(ROOT / "Fidel Alejandro Rosell Perez - ml_baseline.pkl")
loaded = MLBaseline.load(ROOT / "Fidel Alejandro Rosell Perez - ml_baseline.pkl")
result = loaded.predict("The customer cannot access the product dashboard")
print(result)

X_train = baseline.vectorizer.transform(baseline._prepare_texts(train_df["body"]))
train_predictions = baseline.model.predict(X_train)
training_accuracy = (train_predictions == train_df["department"]).mean() * 100
print(f"Training accuracy: {training_accuracy:.2f}%")
