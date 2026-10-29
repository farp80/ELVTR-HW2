# Task 6 — Selection Reasoning

**Selected approach:** Cursor’s reuse-oriented structure, combined with Claude’s sequential `k` selection.

Cursor reuses the accepted Homework 4 prompt, model settings, schema, validator, and ticket loader. This reduces duplicated logic and keeps behavior consistent across tasks. Claude’s `choose_k` stops at the first failed threshold, matching the stated policy: increase `k` only when recall improves by at least 0.10 and precision remains at least 0.50.

The ticket body is retrieved unchanged and kept separate from support articles. The model summarizes customer-provided facts; articles only help identify missing information. The output records retrieved chunks, messages, raw response, validated result, and validation errors for analysis.

**Important:** verify repository paths and the exact prompt rule before running. Runtime correctness is not confirmed until tested with the local vector database, model, metrics, and a known ticket.

## Selected k

**k = 5.**

The values come from the means in `hw_5/Task5/metrics.json`.

| k | Mean precision | Mean recall | Mean hit |
| --- | --- | --- | --- |
| 1 | 0.60 | 0.10 | 0.60 |
| 3 | 0.53 | 0.27 | 0.60 |
| 5 | 0.52 | 0.50 | 0.80 |

**Rule:** start at 1. Move to a bigger k only if mean recall rises by at least 0.10 and mean precision stays at or above 0.50.

**Rationale:**
- From 1 to 3, recall rises by 0.17 and precision is 0.53. The rule moves k to 3.
- From 3 to 5, recall rises by 0.23 and precision is 0.52. The rule moves k to 5.
- At k = 5, the hit rate rises from 0.60 to 0.80. More tickets get at least one useful article.

**Limits:**
- Precision at k = 5 is only 0.02 above the 0.50 floor.
- Only 5 queries were scored, so the numbers are noisy.
- Q005 scored 0 at every k. A bigger k does not fix that retrieval gap.

`task.py` applies this rule in code (`choose_k`). It reads `metrics.json` and returned k = 5 when run on ticket 87.
