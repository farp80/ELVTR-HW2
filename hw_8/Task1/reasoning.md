# Task 1 — Requirements and reasoning

## What the task asks

Task 1 asks for a rule that decides which routing decisions need a person to check them. The rule must use the class scores from the classifier selected in Homework 4. The task has four requirements. Use the saved validation predictions. Design three rules. Run all three on those predictions. Pick one and justify it with numbers.

## Requirement 1: Use the saved validation predictions

The selected classifier is the Homework 4 model with English stop words. Its validation predictions were not saved on disk. The Homework 3 file belongs to an older model, so it does not count. `validation_precision.py` trains the Homework 4 model again with the same data and settings. It then writes `validation_predictions.csv`. The file has 3,755 tickets. Each row holds the ticket id, the true department, the predicted department, and the ten class scores. The accuracy is 0.4980, the same value Homework 4 reported. That match shows it is the same model.

## Requirement 2: Design three rules

Each rule looks at the ten class scores of one ticket and returns yes or no. Yes means a person must check the route.

The margin rule says yes when the top score minus the second score is below 0.05.

The ratio rule says yes when the second score is at least 80% of the top score.

The entropy rule says yes when the ten scores are spread out evenly. The cutoff is 2.10. The highest possible value is 2.303, which means all ten scores are equal.

All three rules are fixed. The same scores always give the same answer.

## Requirement 3: Run the three rules

`evaluate` in `validation_precision.py` runs each rule on all 3,755 tickets. For each rule it counts three things. First, how many tickets go to a person. Second, how many wrong routes are inside that group. Third, how often the tickets that skip review are right.

## Requirement 4: Pick one rule and justify it

The workflow uses the margin rule.

The margin rule sends 1,447 tickets to a person. The ratio rule sends 1,349. The entropy rule sends 1,335. The workload is close for all three.

The margin rule catches 971 of the 1,885 wrong routes. The ratio rule catches 897. The entropy rule catches 890. Margin catches 74 more errors than ratio and 81 more than entropy.

Tickets that skip review under the margin rule are right 60.4% of the time. Under the other two rules they are right 58.9% of the time.

One more check supports the choice. Wrong tickets have a typical margin of 0.0482. Right tickets have a typical margin of 0.1233. A small margin goes with a wrong route.

## Deliverables in this folder

`validation_predictions.csv` is the validation predictions file. `validation_precision.py` and the code in `logic.md` apply and score the three rules. `logic.md` and this file hold the selected rule and the reasons for it.
