# Task 5 - Preprocessing

## Input-Field Decisions

The cleaned dataset and split manifest are merged using ticket_id.

The ticket body is used as the model input because the task requires
preparing the ticket body for modeling.

Department is retained as the target variable.

ticket_id is excluded from the feature representation because it is an
identifier and does not represent ticket content.

Priority and tags are excluded from this preprocessing pipeline because
the task specifies the cleaned ticket body as the modeling input.

## Preprocessing Rationale

TF-IDF was selected to convert ticket bodies into numerical feature
vectors suitable for text classification.

The vectorizer uses lowercase=True to normalize capitalization.

Unigrams and bigrams are included using ngram_range=(1, 2) so that both
individual terms and short phrases can be represented.

min_df=2 removes features that occur in only one document.

max_df=0.95 removes extremely common features that occur in most
documents.

The TF-IDF vectorizer is fitted only on the training partition.
Validation and test data are transformed using the fitted vectorizer.
This prevents information from the validation and test partitions from
influencing the learned vocabulary or IDF statistics.

The resulting feature representation contains 61,157 features.
The fitted TF-IDF vectorizer is also saved as a `.pkl` artifact so the
same preprocessing vocabulary can be reused by the modeling task.

Numeric-only features were not explicitly removed. Only 53 of the
61,157 features (0.087%) were numeric-only, so removing them was not
considered justified based on their proportion of the vocabulary.

## Class-Imbalance Decision

The training data contains an imbalanced distribution of departments,
with technical support substantially larger than the smaller classes.

No oversampling or undersampling was performed during preprocessing.
The original training distribution was retained.

Class imbalance will instead be addressed during model training using
class weighting when supported by the selected classifier. This avoids
duplicating or discarding training examples while allowing the classifier
to give greater importance to minority classes.