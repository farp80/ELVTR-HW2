## Task 2 - Retrain and Apply the ML Model

Re-run your existing Homework 2 ML training workflow using the provided split
manifest, then apply the retrained model to the validation set.

### Requirements

- Replace the Homework 2 manifest input with `split_manifest.csv`.
- Retrain the classifier (ML model + preprocessor) using the new training split.
- Use the retrained model to predict every record in the validation set.
- Save the prediction results as a 4-column CSV containing `ticket_id`, `true_label`, `recommended_department`, 
  and `class_scores` (serialized JSON-dict) returned by the Python classifier class.
- Ensure text-cleaning, preprocessing, and the model are all embedded in the Python classifier class
  (in case you designed it differently in the last homework).
- Ensure training and predictions are reproducible.

### Deliverables

- Classifier Python class from homework 2, with changes made, if any. This
  class should be taking raw ticket text(s) for `fit()` and `predict()`, and:
  - Applying text-cleaning
  - Training/applying the preprocessor
  - Training/applying the ML model
- Code for applying the data split, and feeding it into the classifier.
- Saved retrained ML model.
- Prediction results CSV.