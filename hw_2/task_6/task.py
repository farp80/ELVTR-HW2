"""Task 6 — Build an ML Baseline.

CPU-friendly classifier for department routing.
"""

from pathlib import Path

import sys
import pandas as pd
from shared.classes.ml_baseline import MLBaseline

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HW2_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

cleaned_df = pd.read_csv(PROJECT_ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv")
split_df = pd.read_csv(HW2_ROOT / "Fidel Alejandro Rosell Perez - support_tickets_splitted.csv")
df = cleaned_df.merge(split_df, on="ticket_id", how="inner")
train_df = df[df["split"] == "train"].copy()

baseline = MLBaseline(
    vectorizer_path=HW2_ROOT / "Fidel Alejandro Rosell Perez - tfidf_vectorizer.pkl"
)

baseline.fit(train_df["body"], train_df["department"])
baseline.save(HW2_ROOT / "Fidel Alejandro Rosell Perez - ml_baseline.pkl")
loaded = MLBaseline.load(HW2_ROOT / "Fidel Alejandro Rosell Perez - ml_baseline.pkl")
result = loaded.predict("The customer cannot access the product dashboard")
print(result)

X_train = baseline.vectorizer.transform(baseline._prepare_texts(train_df["body"]))
train_predictions = baseline.model.predict(X_train)
training_accuracy = (train_predictions == train_df["department"]).mean() * 100
print(f"Training accuracy: {training_accuracy:.2f}%")
