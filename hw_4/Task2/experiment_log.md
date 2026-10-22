# Task 2 - Experiment Log

## Targeted category and change

Category: Generic words. It has 12 of the 30 tickets I inspected in Task 1.

Change: `stop_words="english"` in the TF-IDF vectorizer. Nothing else changed.

Why: these errors came from very common words, like "the problems" and "or hardware". Stop words are removed before the word pairs are built, so those pairs disappear. `max_df` would keep them.

Where the values come from: the category and ticket IDs are in `hw_4/Task1/ticket_review.json`. The check that only `stop_words` changed is the first print in `task.py` (step 2).

## Decision rule (written before running)

Keep the candidate only if all three are true:

1. Macro-F1 goes up by at least 0.005.
2. More of the 12 Generic words tickets are correct than before.
3. No department's F1 drops by more than 0.03.

Otherwise revert.

## Effect on the targeted records

- Generic words: 0 of 12 correct before, 5 after.
- All 30 inspected tickets: 0 of 30 correct before, 5 after.
- Technical Support predicted as IT Support (the slice): 0 of 159 correct before, 39 after.

The change helps the tickets I aimed at, but 7 of the 12 are still wrong. Words like "tools" and "problems" are not stop words, so this change cannot fix them.

Where the values come from: step 5 of `task.py`, the lines "target category", "all 30 inspected tickets" and "slice".

## Improvements (validation, compared with the baseline)

- Accuracy: 0.4722 to 0.4980 (+0.0258).
- Macro-F1: 0.4820 to 0.5133 (+0.0313).
- Weighted-F1: 0.4729 to 0.4982 (+0.0253).
- All 10 departments improved. The biggest gains are General Inquiry (+0.080), Customer Service (+0.041) and Human Resources (+0.039).

Macro-F1 is the main metric. It gives every department the same weight, so it shows gains in the small departments too.

Where the values come from: step 4 of `task.py`, the three metric lines and the per-department table (`f1_change` column).

## Regressions

- No department's F1 went down. The smallest gain is Product Support (+0.008).
- IT Support recall went up: 0.428 to 0.445 (+0.018).
- Billing and Payments F1 went up: 0.749 to 0.778 (+0.029).
- Tickets fixed: 303. Tickets broken: 206. Net: +97.
- IT Support: the baseline got 192 right. 154 are still right, so 38 broke.
- Billing: the baseline got 281 right. 273 are still right, so 8 broke.
- Most broken tickets are Technical Support (60) and Product Support (51).

The word "it" is a stop word, so I watched IT Support. Its recall still rose, but 38 tickets that were right now fail. This is the cost of the change.

Where the values come from: step 4 (per-department table) and step 5 (the "risk" lines, "fixed / broken" line and "broken by true department" list) of `task.py`.

## Decision

Decision: KEEP.

- Rule 1: met. Macro-F1 gain is +0.0313, above 0.005.
- Rule 2: met. Generic words went from 0 to 5 correct.
- Rule 3: met. No department dropped. The weakest change is +0.008.

All three rules are met, so the candidate is the Task 2 result. The validation set was used for the decision. The test set was not touched.
