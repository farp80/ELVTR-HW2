## Task 3 - Build a Constant Baseline

Build a baseline that always predicts one department.

### Requirements

- Input: ticket `Body`.
- Output: One `Department` label listed in the dataset card.
- Implement a single Python class with functions for:
  - `fit()`: "Trains" the model
  - `predict()`: Predicts the label for a ticket body
  - `save()`: Saves the trained model to disk
  - `load()`: Loads the trained model from disk
- Ensure predictions are reproducible.

### Deliverables

- Python class code.
- Persisted model artifact.
- Writeup containing:
  - Selected label
  - Rationale
  - Percentage of training records that have the selected label