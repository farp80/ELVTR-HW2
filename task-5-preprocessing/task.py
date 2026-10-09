"""Task 5 — Implement Preprocessing.

Feature vectors from cleaned ticket bodies.
"""
from pathlib import Path
import sys

import joblib


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


from utils.pandas_utils import PandasUtils
from ticket_preprocessor import TicketPreprocessor

cleaned_baseline = PandasUtils(
    file_path=ROOT / "Fidel Alejandro Rosell Perez - support_tickets_cleaned.csv"
)
cleaned_df = cleaned_baseline.df

splitted_baseline = PandasUtils(
    file_path=ROOT / "Fidel Alejandro Rosell Perez - support_tickets_splitted.csv"
)
splitted_df = splitted_baseline.df

preprocessor = TicketPreprocessor(cleaned_df, splitted_df)
df = preprocessor.load()
x_train, y_train, x_validation, y_validation, x_test, y_test = preprocessor.split()
X_train_vectors = preprocessor.fit_transform()
X_validation_vectors = preprocessor.transform(x_validation)
X_test_vectors = preprocessor.transform(x_test)

print("Training:", X_train_vectors.shape)
print("Validation:", X_validation_vectors.shape)
print("Test:", X_test_vectors.shape)

joblib.dump(
    preprocessor.vectorizer,
    ROOT / "Fidel Alejandro Rosell Perez - tfidf_vectorizer.pkl",
)