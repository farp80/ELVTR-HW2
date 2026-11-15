# Task 1 — Explanation of the routing-review policy

The policy answers one question: which tickets should a person check before the model's department is trusted?

## 1. Why a person needs to check

The model is wrong a lot. On the 3,755 validation tickets it picks the wrong department 1,885 times, about half. A person cannot check all 3,755 tickets. A person checks only the tickets where the model is unsure.

## 2. How the model shows it is unsure

For every ticket, the model gives `class_scores`: one score per department. The ten scores add up to 1. The department with the highest score is the one the model picks. When the top two scores are close, the model could not decide.

| Ticket | Top score | Second score | Gap | What happened |
| --- | --- | --- | --- | --- |
| 19 | Billing 0.9241 | Sales 0.0318 | 0.8923 | Sure, and right |
| 24 | IT Support 0.1923 | Technical Support 0.1916 | 0.0007 | Unsure, and wrong (true department is Customer Service) |
| 5 | Customer Service 0.2644 | Sales 0.1350 | 0.1294 | Looked fairly sure, but wrong |

Ticket 24 is the kind a person must see. Ticket 5 shows that no rule catches every mistake.

## 3. Three ways to measure "unsure"

The assignment asks for three rules.

- Margin: flag the ticket when the gap between the top two scores is below 0.05. Ticket 24 is flagged. Ticket 19 is not.
- Ratio: flag the ticket when the second score is at least 80% of the top score. It asks the same question as margin, as a percentage.
- Entropy: flag the ticket when the ten scores are spread out evenly instead of piling onto one department. The value reaches 2.303 when all ten scores are equal. The rule flags tickets above 2.10.

## 4. How the best rule is picked

Each rule sends some tickets to a person. Three numbers are compared.

| Rule | Sent to a person | Wrong routes caught (of 1,885) | Tickets not sent that were right |
| --- | --- | --- | --- |
| Margin | 1,447 (38.5%) | 971 (51.5%) | 60.4% |
| Ratio | 1,349 (35.9%) | 897 (47.6%) | 58.9% |
| Entropy | 1,335 (35.6%) | 890 (47.2%) | 58.9% |

All three send about the same number of tickets to a person, so the workload is similar. Margin catches the most wrong routes. The tickets it does not send are right most often. The workflow uses margin.

## 5. The last check

Wrong tickets have a typical gap of 0.0482. Right tickets have a typical gap of 0.1233. A small gap goes with wrong answers, so the gap is a fair signal for doubtful routes.
