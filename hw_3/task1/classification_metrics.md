## Context ##
We need to classify each support ticket into 1 of the 10 departments.
There is a class imbalance. Technical Support Department has the biggest number of tickets while general inquiry has the least. This can cause the model to miss correct routing for smaller departments.
I am choosing these metrics before looking at the validation results, so the evaluation criteria are decided ahead of time.

## 4 basic outcomes ##
For any department we need to classify each ticket's result into 4 categories. Let's use *IT Support* as example:
1. **TP (True Positive):**
    Actual *IT Support* predicted IT Support.
2. **FP (False Positive):**
    Other department, incorrectly predicted *IT Support*
3. **FN (False Negative):**
    Actual *IT Support*, predicted another department.
4. **TN (True negative):**
    other department correctly predicted as not *IT Support*.

## Metrics selection ##
### 1. **Accuracy**
#### **Definition**: It is the number of correct predictions divided by the total number of evaluated tickets.
#### **Aggregation**: A single overall score across all tickets.
#### **Rationale**: Accuracy is easy to interpret and measures the proportion of tickets assigned to the correct department.
#### **Limitation**: Accuracy can be dominated by large departments. A model can achieve high accuracy while performing poorly on minority departments.

### 2. **Macro F-1**
#### **Definition**: It is the harmonic mean of precision and recall. Macro-F1 calculates F1 independently for each department and takes the unweighted arithmetic mean across all departments.
#### **Aggregation**: Each department receives equal weight, regardless of its number of tickets.
#### **Rationale**: Macro F-1 is appropriate for this imbalanced multiclass problem because it reflects performance across all departments rather than allowing large departments to dominate the summary.
#### **Limitations**: Poor performance in a small department can substantially lower macro F-1. The aggregate score does not identify which departments are responsible for the result, so per-class metrics must also be examined.

### 3. **Weighted-F1**
#### **Definition**: It calculates the F1-score for each department and averages the scores using each department's support, or number of actual tickets, as its weight.
#### **Aggregation**: Each department's contribution is proportional to its number of actual tickets.
#### **Rationale**: Weighted F-1 provides an additional overall summary that reflects the distribution of tickets in the dataset.
#### **Limitations**: Large departments contribute more to the results. Consequently, a high weighted F-1 can coexist with weak performance on minority departments.

### 4. **Per-Class Recall**
#### **Definition**: For a department, recall is the number of correctly predicted tickets for that department divided by all tickets that actually belong to that department.
#### **Aggregation**: Calculated separately for every department.
#### **Rationale**: Recall measures how effectively the model identifies tickets belonging to each department. Low recall indicates that many of its tickets are routed elsewhere.
#### **Limitations**: Recall does not indicate how many incorrectly assigned tickets are sent into the department.

### 5. **Per-Class Precision**
#### **Definition**: For a department, precision is the number of correctly predicted tickets for that department divided by all tickets predicted as that department.
#### **Aggregation**: Calculated separately for every department.
#### **Rationale**: Precision measures how reliable the model is when it routes a ticket to a specific department. Low precision means the department receives many tickets that should have gone elsewhere.
#### **Limitations**: Precision does not show how many actual tickets for the department were missed and routed to other departments.

### 6. **Per-Class F1-Score**
#### **Definition**: F1-score is the harmonic mean of precision and recall for an individual department.
#### **Aggregation**: Calculated separately for each department, with macro-F1 and weighted-F1 providing different ways to summarize these scores.
#### **Rationale**: Per-class F1 helps identify departments where the balance between assignment reliability and ticket coverage is poor.
#### **Limitations**: A single F1-score does not show whether precision or recall is the main source of poor performance. Both should be reviewed separately.

### 7. **Confusion Matrix Diagnostic**
#### **Definition**: A confusion matrix counts actual versus predicted department assignments. Rows represent actual departments, and columns represent predicted departments.
#### **Aggregation**: This is not one score. It is a diagnostic table of counts across all departments.
#### **Rationale**: It reveals which department pairs are frequently confused and helps identify opportunities for model improvement.
#### **Limitations**: Raw counts can be difficult to compare across departments of different sizes. The confusion matrix should be interpreted alongside normalized results and per-class metrics.

## Primary and Secondary Metrics ##

### Primary metric: **Macro-F1**

**Macro-F1** was selected as the primary metric because the dataset contains imbalanced department classes, and the objective is to develop a model that performs across all departments. Giving each department equal weight reduces the risk of selecting a model that performs well mainly on the largest classes.

### Secondary metric: **Weighted-F1**

**Weighted-F1** was selected as the secondary metric because it summarizes F1 performance while accounting for the actual support of each department. Reporting it alongside macro-F1 helps compare balanced cross-department performance against performance weighted by the real distribution of tickets.

**Accuracy** will still be reported as a simple communication metric for stakeholders, but it will not guide model iteration because it can hide poor performance on minority departments. **Per-class precision**, **recall**, and **F1** will be used to diagnose department-specific weaknesses. The **confusion matrix** will be used to investigate recurring misclassification patterns.

## Evaluation Procedure ##

The selected metrics will be calculated on the validation set after training. **Macro-F1** will guide model iteration, with **Weighted-F1** used as the secondary metric and **per-class** results used to diagnose errors. **Accuracy** will be reported for interpretability but will not be the main basis for model-selection decisions. The test set will remain reserved for final evaluation after model-selection decisions are complete.


