# Homework 4 - Checklist

Based on `WEEK_4_ASSIGNMENT.md`. Status is checked against the files in `hw_4/`.
"Done" means the file exists and I checked it. "Open" means something is left to do.

## Fixed evaluation rules

| Rule | Status |
| --- | --- |
| Fit preprocessing and model on training data only | Done. Task 2 uses the training split only. |
| Prediction features are `Body` text only | Done. The classifier reads `body` only. |
| Validation and test records, inputs and labels unchanged | Done. Nothing writes to the data files. |
| Homework 3 metrics unchanged | Done. Task 1 reproduces 0.472 / 0.482 / 0.473. |
| Use validation data for analysis and iteration | Done. Tasks 1 and 2 use validation only. |
| Homework 3 model and validation predictions kept as the baseline | Done. Only loaded, never saved. The baseline hash in `Task3/freeze.txt` matches the file. |
| No test split inspected before Task 3 | Done. The test split is first loaded in Task 3. |
| No classifier change after the test results | Done. The hashes in `freeze.txt` still match both models. |

## Task 1 - Analyze validation errors

| Item | Status |
| --- | --- |
| One confusion pair chosen from the Homework 3 metrics | Done. Technical Support predicted as IT Support, 159 tickets. |
| Reason for the choice written | Done. `Task1/analysis.md`, "Slice selection". |
| 30 or more wrong records picked with a fixed rule | Done. First 30 by `ticket_id`. The rule is in `analysis.md`. |
| Each record has ID, true label, predicted label | Done. 30 tickets in `analysis.md`. |
| Each record has a category and the reason for it | Done. |
| Each record has why the model chose the predicted department | Done. Words and scores are quoted. |
| Failure categories named, each ticket in one | Done. 4 categories. Counts 12, 10, 5, 3 = 30. |
| Each category has a count and the likely impact | Done. |
| Each category says if a model or text change can fix it | Done. |

## Task 2 - Controlled classifier iteration

| Item | Status |
| --- | --- |
| One change tied to a Task 1 category | Done. `stop_words="english"` for "Generic words". |
| Retrained on the Homework 3 training split | Done. 17,524 tickets. |
| Evaluated on the validation set | Done. 3,755 tickets. |
| Modified code | Done. `Task2/task.py`. |
| Retrained model | Done. `Task2/... - hw4_candidate.pkl`. |
| Validation predictions, same 4 columns | Done. 3,755 rows. |
| Log: category and change | Done. `Task2/experiment_log.md`. |
| Log: result on the targeted records | Done. 0 of 12 correct before, 5 after. |
| Log: improvements and regressions | Done. Macro-F1 +0.0313. No department got worse. |
| Log: keep or revert with the reason | Done. Keep. |

## Task 3 - Final holdout comparison

| Item | Status |
| --- | --- |
| Both models and the Task 2 decision frozen before the test | Done. `Task3/freeze.txt`. |
| Both models applied to the test set | Done. 3,755 rows each. |
| Test predictions keep `recommended_department` and `class_scores` | Done. Two CSV files. |
| Metrics and confusion matrices for both models | Done. `test_metrics.txt` and the report. |
| Validation vs test differences explained | Done. |
| Does the test support the Task 2 decision | Done. Yes. |
| Selected routing model with the reason | Done. The candidate. |
| No model changed or rerun after the test | Done. Do not run `task.py` for Task 2 or 3 again. |

## Task 4 - Set up the local LLM

| Item | Status |
| --- | --- |
| Follow `LLM_SETUP.md` | Done. Ollama 0.40.7, model downloaded, API calls worked. |
| Notes (not required) | Done. `Task4/setup_notes.md`. |

## Task 5 - Initial prompt

| Item | Status |
| --- | --- |
| Prompt with the ticket `Body` as input and the JSON as output | Done. `Task5/task5_notes.md`. |
| Reusable function with output validation | Done. `Task5/llm_summary.py`. |
| Test ticket ID | Done. Ticket 87. |
| Generated output for the test ticket | Done. Valid JSON, three fields. |

## Task 6 - Apply the initial prompt

| Item | Status |
| --- | --- |
| All 10 tickets used unchanged | Done. |
| Full input for each ticket | Done. `Task6/task6_report.md`. |
| Output for each ticket | Done. |
| Followed the schema? Supported by the body? Key information? | Done. Answered for each ticket. |
| Agree with the missing information, and why | Done. |
| High-level issues | Done. |
| Review answers read and approved by you | Open. I wrote them. Read them and edit in your own words. |

## Task 7 - Two prompt iterations

| Item | Status |
| --- | --- |
| Iteration 1: pattern and why | Done. `Task7/experiment_log.md`. |
| Iteration 1: updated prompt and 10 outputs | Done. `prompt_iteration_1.txt`, `iteration_1_outputs.json`. |
| Iteration 1: improvements, regressions, decision | Done. Keep. |
| Iteration 2 starts from the accepted prompt | Done. The code enforces it. |
| Iteration 2: pattern, change, prompt, 10 outputs | Done. `prompt_iteration_2.txt`, `iteration_2_outputs.json`. |
| Iteration 2: improvements, regressions, decision | Done. Revert. |
| Only the prompt changed | Done. The prompt difference is in each comparison file. |
| Judgments read and approved by you | Open. I wrote them. Check them. |

## Submission

| Item | Status |
| --- | --- |
| One zip named `Firstname_Lastname_HW4.zip` | Open. Not built yet. Use your Google Classroom name. |
| Folders `Task1` to `Task7` at the root | Open. Build the zip from `hw_4/Task1` to `hw_4/Task7`. |
| Tables are CSV files, not Excel | Done. |
| Writeups are `.md` or `.txt` | Done. |
| No extra files | Open. Leave out `Task_N_cursor.md`, `REQUIREMENTS.md` and `__init__.py`. |

## Code rules from the review brief

| Rule | Status |
| --- | --- |
| No `assert`, `show` or `display` in the `.py` files | Done. Searched all seven task folders. |
| Rerun and freeze guards kept as plain `if` checks | Done. Tasks 2, 3 and 7. |
| Plain English, under 200 words per explanation | Done. Longest section checked. |
