# Task 3 - Test Comparison Report

## Freeze

Both models and the Task 2 decision were saved in `freeze.txt` before the test set was opened. The file holds a SHA-256 hash of each model. The test stage checked the hashes before it ran. They matched.

- Task 2 decision: keep.
- Selection rule: carry the candidate forward only if the Task 2 decision was keep and its test macro-F1 is higher than the baseline's. Otherwise carry the baseline.

The test stage ran once. The test set has 3,755 tickets. Both prediction files keep `recommended_department` and `class_scores`.

## Metrics and confusion matrices

Full output is in `test_metrics.txt`. In the matrices, rows are the true department and columns are the predicted department. The column number is the department number on the left.

### Baseline

Accuracy 0.4727, macro-F1 0.4758, weighted-F1 0.4732.

```text
                          label  precision  recall    f1  support
           billing and payments      0.741   0.729 0.735      380
               customer service      0.392   0.398 0.395      565
                general inquiry      0.342   0.509 0.409       53
                human resources      0.422   0.535 0.472       71
                     it support      0.383   0.432 0.406      449
                product support      0.460   0.373 0.412      695
          returns and exchanges      0.376   0.573 0.454      185
            sales and pre-sales      0.332   0.614 0.431      114
service outages and maintenance      0.462   0.696 0.555      148
              technical support      0.559   0.435 0.489     1095

                                     0    1   2   3    4    5    6   7    8    9
0 billing and payments             277   31   3   4   11   11   12  10    2   19
1 customer service                  18  225  11   8   52   73   46  28   11   93
2 general inquiry                    2    7  27   1    6    3    2   2    0    3
3 human resources                    1   10   1  38    6    5    2   2    0    6
4 it support                        14   59   3   7  194   36   15  12   25   84
5 product support                   18   74  18  13   60  259   47  36   19  151
6 returns and exchanges              9   18   3   1   12   20  106   6    3    7
7 sales and pre-sales                5   16   0   1    2   11    5  70    0    4
8 service outages and maintenance    1   11   0   1   10    7    5   1  103    9
9 technical support                 29  123  13  16  154  138   42  44   60  476
```

### Candidate

Accuracy 0.4959, macro-F1 0.5005, weighted-F1 0.4967.

```text
                          label  precision  recall    f1  support
           billing and payments      0.783   0.758 0.770      380
               customer service      0.403   0.419 0.411      565
                general inquiry      0.429   0.509 0.466       53
                human resources      0.416   0.592 0.488       71
                     it support      0.407   0.445 0.425      449
                product support      0.500   0.404 0.447      695
          returns and exchanges      0.389   0.589 0.469      185
            sales and pre-sales      0.345   0.623 0.444      114
service outages and maintenance      0.480   0.723 0.577      148
              technical support      0.573   0.457 0.508     1095

                                     0    1   2   3    4    5    6   7    8    9
0 billing and payments             288   27   6   1   10   10   11   8    3   16
1 customer service                  15  237   5  15   53   67   47  32    8   86
2 general inquiry                    0    7  27   2    4    2    4   2    0    5
3 human resources                    1    8   0  42    5    6    1   1    0    7
4 it support                        10   61   3   6  200   38   16   6   16   93
5 product support                   16   74  12  14   58  281   44  34   16  146
6 returns and exchanges              8   23   2   2    8   14  109   6    2   11
7 sales and pre-sales                4   10   2   1    2   15    6  71    0    3
8 service outages and maintenance    2   10   0   1   10    8    3   2  107    5
9 technical support                 24  131   6  17  142  121   39  44   71  500
```

The candidate has a higher F1 than the baseline in all 10 departments.

## Validation vs test

- Baseline macro-F1: 0.4820 on validation, 0.4758 on test (-0.0062).
- Candidate macro-F1: 0.5133 on validation, 0.5005 on test (-0.0128).
- Both models score a little lower on test. This is normal, because the tickets are different.
- The gap between the models stayed positive: +0.0313 on validation, +0.0247 on test.

The biggest department shifts are General Inquiry (53 tickets), Human Resources (71 tickets) and Returns and Exchanges. These departments are small, so their scores move by chance. I do not read much into them.

## Does the test support the Task 2 decision?

Yes. I kept the candidate in Task 2. On the test set it beats the baseline on macro-F1 (0.5005 against 0.4758, +0.0247). Accuracy also goes up (0.4959 against 0.4727).

## Selected routing model

The candidate. The frozen rule says to carry the candidate forward if the decision was keep and its test macro-F1 is higher. Both are true. No model was changed or retrained after the test.
