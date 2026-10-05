## Task 6 - Build an ML Baseline

Build one CPU-friendly classifier.

### Requirements

- Input: ticket `Body`.
- Output: dictionary matching `ml_baseline_output_example.json`.
  - Look at using `predict_proba` or `decision_function` (depends on model)
    to get the class scores.
- Implement a single Python class with functions for:
  - `fit()`: Trains the preprocessor and model
  - `predict()`: Applies preprocessing to the ticket body and predicts the label
  - `save()`: Saves the trained model to disk (use `joblib` Python lib)
  - `load()`: Loads the trained model from disk
- Ensure predictions are reproducible.
- You may use scikit-learn for model training.

### Deliverables

- Python class code.
- Persisted model artifact.
- ML-baseline writeup containing:
  - Text-featurization choice and rationale
  - Model choice and rationale
  - Percentage of training records predicted correctly