# Task 3.3 - Validation Evaluation Report

## Inputs

### Validation predictions

- File: Fidel Alejandro Rosell Perez - validation_predictions.csv
- Tickets: 3755
- Test split: not used

### Body length

- Source: cleaned ticket text
- Unit: character count

## Overall Metrics

Fewer than half of the validation tickets go to the right department.

### Accuracy

- Value: 0.472

### Macro-F1

- Value: 0.482

### Weighted-F1

- Value: 0.473

## Per-Class Metrics

### Returns and Exchanges

- Precision: 0.326
- Recall: 0.476
- F1: 0.387
- Support: 185

### Customer Service

- Precision: 0.403
- Recall: 0.388
- F1: 0.395
- Support: 565

### IT Support

- Precision: 0.369
- Recall: 0.428
- F1: 0.396
- Support: 449

### Product Support

- Precision: 0.472
- Recall: 0.357
- F1: 0.407
- Support: 695

### Sales and Pre-Sales

- Precision: 0.313
- Recall: 0.640
- F1: 0.421
- Support: 114

### General Inquiry

- Precision: 0.384
- Recall: 0.623
- F1: 0.475
- Support: 53

### Technical Support

- Precision: 0.543
- Recall: 0.452
- F1: 0.494
- Support: 1095

### Human Resources

- Precision: 0.482
- Recall: 0.563
- F1: 0.519
- Support: 71

### Service Outages and Maintenance

- Precision: 0.491
- Recall: 0.703
- F1: 0.578
- Support: 148

### Billing and Payments

- Precision: 0.759
- Recall: 0.739
- F1: 0.749
- Support: 380

## Per-Class One-vs-Rest Confusion Matrix

TP is a correct assignment. FP is another department sent here. FN is a ticket from this department sent elsewhere. TN is everything else.

### Returns and Exchanges

- TP: 88
- FP: 182
- FN: 97
- TN: 3388

### Customer Service

- TP: 219
- FP: 325
- FN: 346
- TN: 2865

### IT Support

- TP: 192
- FP: 329
- FN: 257
- TN: 2977

### Product Support

- TP: 248
- FP: 277
- FN: 447
- TN: 2783

### Sales and Pre-Sales

- TP: 73
- FP: 160
- FN: 41
- TN: 3481

### General Inquiry

- TP: 33
- FP: 53
- FN: 20
- TN: 3649

### Technical Support

- TP: 495
- FP: 416
- FN: 600
- TN: 2244

### Human Resources

- TP: 40
- FP: 43
- FN: 31
- TN: 3641

### Service Outages and Maintenance

- TP: 104
- FP: 108
- FN: 44
- TN: 3499

### Billing and Payments

- TP: 281
- FP: 89
- FN: 99
- TN: 3286

## Multi-Class Confusion Matrix

Each heading is the true department. Each setting is the predicted department and how many of those tickets were sent there.

### Billing and Payments

- Billing and Payments: 281
- Customer Service: 31
- General Inquiry: 0
- Human Resources: 3
- IT Support: 11
- Product Support: 6
- Returns and Exchanges: 12
- Sales and Pre-Sales: 16
- Service Outages and Maintenance: 1
- Technical Support: 19

### Customer Service

- Billing and Payments: 20
- Customer Service: 219
- General Inquiry: 13
- Human Resources: 7
- IT Support: 50
- Product Support: 75
- Returns and Exchanges: 38
- Sales and Pre-Sales: 40
- Service Outages and Maintenance: 11
- Technical Support: 92

### General Inquiry

- Billing and Payments: 0
- Customer Service: 5
- General Inquiry: 33
- Human Resources: 1
- IT Support: 3
- Product Support: 4
- Returns and Exchanges: 2
- Sales and Pre-Sales: 2
- Service Outages and Maintenance: 0
- Technical Support: 3

### Human Resources

- Billing and Payments: 3
- Customer Service: 4
- General Inquiry: 1
- Human Resources: 40
- IT Support: 2
- Product Support: 8
- Returns and Exchanges: 5
- Sales and Pre-Sales: 3
- Service Outages and Maintenance: 1
- Technical Support: 4

### IT Support

- Billing and Payments: 7
- Customer Service: 47
- General Inquiry: 7
- Human Resources: 5
- IT Support: 192
- Product Support: 37
- Returns and Exchanges: 15
- Sales and Pre-Sales: 15
- Service Outages and Maintenance: 17
- Technical Support: 107

### Product Support

- Billing and Payments: 14
- Customer Service: 93
- General Inquiry: 11
- Human Resources: 10
- IT Support: 72
- Product Support: 248
- Returns and Exchanges: 44
- Sales and Pre-Sales: 35
- Service Outages and Maintenance: 18
- Technical Support: 150

### Returns and Exchanges

- Billing and Payments: 8
- Customer Service: 21
- General Inquiry: 3
- Human Resources: 2
- IT Support: 8
- Product Support: 18
- Returns and Exchanges: 88
- Sales and Pre-Sales: 9
- Service Outages and Maintenance: 3
- Technical Support: 25

### Sales and Pre-Sales

- Billing and Payments: 5
- Customer Service: 11
- General Inquiry: 1
- Human Resources: 1
- IT Support: 6
- Product Support: 6
- Returns and Exchanges: 6
- Sales and Pre-Sales: 73
- Service Outages and Maintenance: 1
- Technical Support: 4

### Service Outages and Maintenance

- Billing and Payments: 2
- Customer Service: 3
- General Inquiry: 2
- Human Resources: 1
- IT Support: 18
- Product Support: 1
- Returns and Exchanges: 2
- Sales and Pre-Sales: 3
- Service Outages and Maintenance: 104
- Technical Support: 12

### Technical Support

- Billing and Payments: 30
- Customer Service: 110
- General Inquiry: 15
- Human Resources: 13
- IT Support: 159
- Product Support: 122
- Returns and Exchanges: 58
- Sales and Pre-Sales: 37
- Service Outages and Maintenance: 56
- Technical Support: 495

## Body-Length Slice Definitions

The cuts are the 33rd and 66th percentiles of validation body length.

### Short

- Rule: 260 characters or fewer
- Tickets: 1241

### Medium

- Rule: 261 to 506 characters
- Tickets: 1241

### Long

- Rule: 507 characters or more
- Tickets: 1273

## Metrics by Body-Length Slice

### Short

- Accuracy: 0.457
- Macro-F1: 0.460
- Weighted-F1: 0.461

#### Returns and Exchanges

- Precision: 0.248
- Recall: 0.456
- F1: 0.321
- Support: 57

#### Customer Service

- Precision: 0.413
- Recall: 0.365
- F1: 0.388
- Support: 208

#### IT Support

- Precision: 0.396
- Recall: 0.471
- F1: 0.430
- Support: 153

#### Product Support

- Precision: 0.459
- Recall: 0.401
- F1: 0.428
- Support: 237

#### Sales and Pre-Sales

- Precision: 0.253
- Recall: 0.588
- F1: 0.354
- Support: 34

#### General Inquiry

- Precision: 0.333
- Recall: 0.615
- F1: 0.432
- Support: 13

#### Technical Support

- Precision: 0.562
- Recall: 0.406
- F1: 0.472
- Support: 347

#### Human Resources

- Precision: 0.341
- Recall: 0.483
- F1: 0.400
- Support: 29

#### Service Outages and Maintenance

- Precision: 0.576
- Recall: 0.792
- F1: 0.667
- Support: 48

#### Billing and Payments

- Precision: 0.755
- Recall: 0.670
- F1: 0.710
- Support: 115

### Medium

- Accuracy: 0.495
- Macro-F1: 0.503
- Weighted-F1: 0.492

#### Returns and Exchanges

- Precision: 0.375
- Recall: 0.517
- F1: 0.435
- Support: 58

#### Customer Service

- Precision: 0.435
- Recall: 0.435
- F1: 0.435
- Support: 191

#### IT Support

- Precision: 0.398
- Recall: 0.430
- F1: 0.413
- Support: 158

#### Product Support

- Precision: 0.457
- Recall: 0.350
- F1: 0.397
- Support: 214

#### Sales and Pre-Sales

- Precision: 0.377
- Recall: 0.625
- F1: 0.471
- Support: 32

#### General Inquiry

- Precision: 0.364
- Recall: 0.500
- F1: 0.421
- Support: 16

#### Technical Support

- Precision: 0.542
- Recall: 0.469
- F1: 0.503
- Support: 369

#### Human Resources

- Precision: 0.538
- Recall: 0.667
- F1: 0.596
- Support: 21

#### Service Outages and Maintenance

- Precision: 0.485
- Recall: 0.717
- F1: 0.579
- Support: 46

#### Billing and Payments

- Precision: 0.748
- Recall: 0.809
- F1: 0.777
- Support: 136

### Long

- Accuracy: 0.465
- Macro-F1: 0.488
- Weighted-F1: 0.466

#### Returns and Exchanges

- Precision: 0.376
- Recall: 0.457
- F1: 0.413
- Support: 70

#### Customer Service

- Precision: 0.355
- Recall: 0.361
- F1: 0.358
- Support: 166

#### IT Support

- Precision: 0.310
- Recall: 0.377
- F1: 0.340
- Support: 138

#### Product Support

- Precision: 0.506
- Recall: 0.320
- F1: 0.392
- Support: 244

#### Sales and Pre-Sales

- Precision: 0.327
- Recall: 0.688
- F1: 0.443
- Support: 48

#### General Inquiry

- Precision: 0.425
- Recall: 0.708
- F1: 0.531
- Support: 24

#### Technical Support

- Precision: 0.531
- Recall: 0.478
- F1: 0.503
- Support: 379

#### Human Resources

- Precision: 0.750
- Recall: 0.571
- F1: 0.649
- Support: 21

#### Service Outages and Maintenance

- Precision: 0.423
- Recall: 0.611
- F1: 0.500
- Support: 54

#### Billing and Payments

- Precision: 0.777
- Recall: 0.729
- F1: 0.752
- Support: 129

## Performance Differences Across Slices

### Medium

- Result: highest accuracy and macro-F1

### Short

- Result: lowest scores
- Reason: fewer words that point to a department

### Long

- Result: below medium
- Reason: extra length does not keep adding useful clues
- IT Support F1 falls to 0.340, and Customer Service falls to 0.358

### Per class across slices

- Billing and Payments stays the strongest department in every slice
- Returns and Exchanges is weakest on short tickets, at F1 0.321, then rises on medium and long tickets
- Service Outages and Maintenance is strong on short tickets, at F1 0.667, and weaker on long tickets, at F1 0.500

## Primary and Secondary Metric Interpretation

### Macro-F1

- Role: primary metric
- Value: 0.482
- Meaning: when every department counts the same, the average department is right less than half the time

### Weighted-F1

- Role: secondary metric
- Value: 0.473
- Meaning: close to macro-F1, so the large departments are not lifting the score much

### Accuracy

- Role: reported, not used to choose the model
- Value: 0.472
- Meaning: agrees with the two F1 scores
- Imbalance: Technical Support has 1095 tickets and General Inquiry has 53

## Best and Worst Departments

### Billing and Payments

- Rank: best
- Precision: 0.759
- Recall: 0.739
- Meaning: the choice is usually right, and most of its own tickets are found

### Returns and Exchanges

- Rank: worst
- F1: 0.387
- Precision: 0.326
- False positives: 182

### Sales and Pre-Sales

- Recall: 0.640
- Precision: 0.313
- Meaning: it finds many of its own tickets and also takes tickets that belong elsewhere

### Product Support

- Precision: 0.472
- Recall: 0.357
- Missed tickets: 447

## Confusion Patterns

### Technical Support predicted as IT Support

- Count: 159

### Product Support predicted as Technical Support

- Count: 150

### Technical Support predicted as Product Support

- Count: 122

### Technical Support predicted as Customer Service

- Count: 110

### IT Support predicted as Technical Support

- Count: 107

### Product Support predicted as Customer Service

- Count: 93

### Customer Service predicted as Technical Support

- Count: 92

### Customer Service predicted as Product Support

- Count: 75

Technical Support, IT Support, Product Support, and Customer Service get mixed up with each other. That is why those four sit in the lower half of the F1 list even though they have the most tickets.

## What These Metrics Cannot Establish

### This split only

- These numbers are for this validation split. They are not the test result.

### Fairness

- The scores do not show that the model treats every user fairly.

### Individual errors

- The scores do not explain each wrong ticket.

### Deployment

- A score near 0.48 is not a reason to deploy the model.
