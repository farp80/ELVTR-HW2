import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from shared.classes.ticket_routing_classifier import (
    LABEL_NAMES,
    TicketRoutingClassifier,
)

DATA_ROOT = ROOT / "hw_3"
CLEANED_DF_PATH = DATA_ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
MODEL_PATH = DATA_ROOT / "Fidel Alejandro Rosell Perez - hw3_ml_baseline.pkl"
PREDICTION_PATH = DATA_ROOT / "Fidel Alejandro Rosell Perez - validation_predictions.csv"
SPLIT_PATH = DATA_ROOT / "Fidel Alejandro Rosell Perez - split_manifest.csv"

cleaned_df = pd.read_csv(CLEANED_DF_PATH)
split_df = pd.read_csv(SPLIT_PATH)
merged_df = cleaned_df.merge(split_df, on="ticket_id", how="inner")

train_df = merged_df[merged_df["split"] == "train"].copy()
validation_df = merged_df[merged_df["split"] == "validation"].copy()

classifier = TicketRoutingClassifier()
classifier.fit(train_df["body"], train_df["department"])
classifier.save(MODEL_PATH)

rows = []

for _, row in validation_df.iterrows():
    prediction = classifier.predict(row["body"])
    rows.append(
        {
            "ticket_id": row["ticket_id"],
            "true_label": LABEL_NAMES[row["department"]],
            "recommended_department": prediction["recommended_department"],
            "class_scores": json.dumps(prediction["class_scores"]),
        }
    )

prediction_df = pd.DataFrame(rows)
prediction_df.to_csv(PREDICTION_PATH, index=False)

print(prediction_df.head())
print(prediction_df.columns.tolist())
print(prediction_df.shape)
