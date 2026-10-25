# Task 5 - Retrieval Evaluation Report - claude

**Status:** the method and justifications are written. The numbers and the failure analysis depend on your labels, so they are marked **TO FILL**. I did not run the vector store (the packages are not installed on my machine), and I did not invent any results. Follow `program - claude.md`, then fill the marked parts.

## 1. Setup

- 5 queries from `evaluation_queries.json`: Q001 to Q005.
- Each query returns the top 10 chunks. Total: 50 labeled rows.
- Label rule: **relevant** = the chunk contains information that helps address the query, even partly.
- Values of k tested: **1, 3, 5**.

## 2. Metrics selected and why

| Metric | Formula | Why I selected it |
| --- | --- | --- |
| **Precision@k** | relevant in top k / k | Everything we put in the prompt costs space and can distract a 1.5B model. Precision shows how much of it is useful. |
| **Recall@k** | relevant in top k / relevant in the top 10 | These queries need information from more than one article (for example Q002 and Q004). Recall shows if we caught all the parts. |
| **Hit@k** | 1 if any relevant chunk is in the top k | The weakest useful test: does the model get at least one good chunk? |

**Limit of recall.** The total is the relevant chunks found in the top 10 only. A relevant chunk ranked 11th is not counted. When a query has no relevant chunk, recall is `n/a` and that query is left out of the recall average.

**Why not more metrics.** Five queries is too small a set for rank-based scores such as MRR or NDCG to add anything beyond these three.

## 3. Results

Paste `metrics_tables.md` here. It has three tables (Precision@k, Recall@k, Hit@k). Each table has one row per query and one row for the mean over all queries, for k = 1, 3, and 5.

**TO FILL.**

## 4. Labeled results

Keep `retrieval_top10.md` (the 50 rows) and `labels.json` (your labels) in this folder. For each row, write one short reason in `labels.json` or in the table below.

| Query | Rank | Chunk ID | Relevant | Reason |
| --- | ---: | --- | :---: | --- |
| **TO FILL** | | | | |

## 5. Failure patterns

**TO FILL** from your labels. Look for these patterns first, and keep only the ones that are true:

1. **No supporting article.** Q005 asks about enrolling a hardware security key. If no article covers it, the top results are about something else (for example password resets). Recall is `n/a`. Precision is 0 for all k.
2. **Answer split across articles.** Q002 (Jira workflow and email routing) and Q004 (flicker steps and store return versus technician) each need two or three articles. Check if small k finds only one part.
3. **Similar wrong neighbor ranked higher.** Articles for the same product with another purpose (for example audio dropouts versus flicker for the QN90A) can outrank the right chunk.
4. **Generic sections.** Short sections like "Overview" or "Limits" can match many queries.

For each pattern that is true, give the query, the rank, and the chunk ID as evidence.

## 6. Possible improvements

Each idea targets one pattern. Pick the ones that match your failures.

| Idea | Fixes pattern | How |
| --- | --- | --- |
| Add a distance cutoff | 1 | Drop results above a distance limit, so "no answer" returns nothing. |
| Group chunks by article | 2, 4 | Return neighbors of a hit from the same article. |
| Rewrite the query | 3 | Reduce the ticket to its key product and action before searching. |
| Give the title more weight in `embedding_text` | 3, 4 | Repeat the title and product, so the product weighs more in the vector. Rebuild and re-test. |
| Re-rank the top 10 | 3 | Reorder with a second pass that checks product match. |
