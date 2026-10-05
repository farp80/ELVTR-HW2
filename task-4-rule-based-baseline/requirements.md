## Task 4 - Build a Rule-Based Baseline

Build a deterministic non-ML baseline and describe the signals its rules use.

### Requirements

- Input: ticket `Body`.
- Output: exactly one `Department` label listed in the dataset card.
- Implement a single Python class with functions for:
  - `predict()`: Predicts the label for a ticket body using your rules
  - `save()`: Saves the trained model to disk
  - `load()`: Loads the trained model from disk
- Ensure predictions are reproducible.
- Implement rules for `Product Support`, `Customer Service`, and `IT Support`,
  which are the second through fourth most frequent classes.
- Fall back to the majority class when no rule matches.
- Only use the train-partition data for rule development.
- Your rules should improve on the constant baseline's accuracy, even if only marginally.

### Deliverables

- Python class code.
- Persisted model artifact.
- Writeup containing:
  - General
    - How rule matches are resolved into a final label
    - Percentage of training records predicted correctly
  - For each rule
    - Description
    - Rationale
    - Number of in-class training records that match
    - Number of out-of-class training records that match