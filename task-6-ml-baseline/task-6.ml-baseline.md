- **Text-featurization choice and rationale:** `TfidfVectorizer` from Task 5, with lowercase normalization, unigrams,
  bigrams, `min_df=2`, and `max_df=0.95`.
- **Model choice and rationale:** `LogisticRegression` because it is CPU-friendly, works with sparse TF-IDF 
  features, supports class weighting, and provides probability scores.
- **Class-imbalance handling:** `class_weight="balanced"` in the classifier.
- **Reproducibility:**  `random_state=42`.
- **Training accuracy:** `76.80%`
- **Artifact:** The saved model file, for example: `Fidel Alejandro Rosell Perez - ml_baseline.pkl`.