# Task 7 - RAG vs No-RAG Comparison Report - claude

**Status:** the no-RAG baseline scores are filled in from Task 2. The retrieval results, the summaries, and the RAG scores are marked **TO FILL**, because they only exist after you run `run_task7.py`. I did not invent them.

**Rubric:** the frozen version in `../Task2/rubric_frozen.md`. Scale for every score: 0, 0.5, or 1. Score the RAG output against the unaltered ticket `Body`. Judge the Grounded dimension against the body, not against the articles: a fact that came only from an article counts as added.

## How to grade and compare

1. Copy the retrieved chunks and the summary from `task7_outputs.md`.
2. Score the four dimensions. Write one sentence of reason per score, quoting the output or the body.
3. Compute **change = RAG score - no-RAG score** for each dimension.
4. Write which field changed (`summary`, `customer_request`, `missing_information`) and why. Compare the two outputs side by side, not only the numbers.
5. Report the result as it is, even when RAG ties or loses. The assignment says that a weak model may not gain.

## No-RAG baseline (from Task 2)

| Ticket | Grounded | Request coverage | Missing information | Summary job | Total |
| --- | :---: | :---: | :---: | :---: | :---: |
| 28763 | 1 | 1 | 0.5 | 0.5 | 3.0 |
| 29206 | 1 | 0.5 | 0.5 | 1 | 3.0 |
| 28921 | 0.5 | 0.5 | 0.5 | 0.5 | 2.0 |

No-RAG output for each ticket is in `../Task2/scoring.md` (rationales) and in the Homework 4 file `iteration_1_outputs.json`.

---

## Ticket 28763 - Supported request

**What to look for.** Chunks from Samsung QN90A articles (flicker troubleshooting, warranty and technician routing). A good outcome: the summary stays true to the ticket, and `missing_information` names something real, such as the purchase date or order number.

### Retrieval results
**TO FILL** - rank, chunk ID, and one line on whether each chunk applies.

### Generated summary
**TO FILL** - paste the JSON.

### Grading
| Dimension | No-RAG | RAG | Change | Reason for the RAG score |
| --- | :---: | :---: | :---: | --- |
| Grounded | 1 | **TO FILL** | | |
| Request coverage | 1 | **TO FILL** | | |
| Missing information | 0.5 | **TO FILL** | | |
| Summary job | 0.5 | **TO FILL** | | |

### Comparison with no-RAG
**TO FILL** - what changed in each field, and whether the articles caused it.

---

## Ticket 29206 - Supported, many sources

**What to look for.** Chunks from several Jira articles (custom priorities, statuses and transitions, maybe notifications and permissions). Watch two risks: the model copies article facts into `summary` or `customer_request` (hurts Grounded), or it loses some asks while handling more text (hurts Request coverage).

### Retrieval results
**TO FILL**

### Generated summary
**TO FILL**

### Grading
| Dimension | No-RAG | RAG | Change | Reason for the RAG score |
| --- | :---: | :---: | :---: | --- |
| Grounded | 1 | **TO FILL** | | |
| Request coverage | 0.5 | **TO FILL** | | |
| Missing information | 0.5 | **TO FILL** | | |
| Summary job | 1 | **TO FILL** | | |

### Comparison with no-RAG
**TO FILL**

---

## Ticket 28921 - Unsupported request

**What to look for.** The customer asks for an HR system redesign and data analysis tools. No article is expected to cover it, so the chunks are weak matches. A good outcome: the output matches the no-RAG one in substance and no article fact appears. A bad outcome: the model uses unrelated article content.

### Retrieval results
**TO FILL** - note the distances. If they are high, the matches are weak.

### Generated summary
**TO FILL**

### Grading
| Dimension | No-RAG | RAG | Change | Reason for the RAG score |
| --- | :---: | :---: | :---: | --- |
| Grounded | 0.5 | **TO FILL** | | |
| Request coverage | 0.5 | **TO FILL** | | |
| Missing information | 0.5 | **TO FILL** | | |
| Summary job | 0.5 | **TO FILL** | | |

### Comparison with no-RAG
**TO FILL**

---

## Overall comparison

| Ticket | No-RAG total | RAG total | Change |
| --- | :---: | :---: | :---: |
| 28763 | 3.0 | **TO FILL** | |
| 29206 | 3.0 | **TO FILL** | |
| 28921 | 2.0 | **TO FILL** | |

**Conclusion - TO FILL.** Answer in plain words: (1) Did RAG help, tie, or hurt on each ticket? (2) Which dimension moved most? (3) Did the "ignore the articles" instruction work on 28921? (4) With only three tickets and a 1.5B model, what can and cannot be claimed?
