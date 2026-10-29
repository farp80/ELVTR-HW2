# Task 5 — Retrieval evaluation report

The five queries are in `evaluation_queries.json`. `task.py retrieve` saved the top 10 chunks for each query in `retrieval_results.json`. I labeled every row. `true` means the chunk text helps answer that query, including a partial answer. The reasons are in `relevance_justification.md`. `task.py metrics` wrote `metrics.json`.

Recall uses the labeled top 10 as the full set of relevant chunks. A relevant chunk at rank 11 is not counted. When a query has no relevant chunk in the top 10, recall is recorded as 0 and that query stays in the average. That is the Q005 case.

## Metrics

I used three metrics at k = 1, 3, and 5. These are the list sizes that can fit in the later prompt.

**Precision@k** is the number of relevant rows inside the top k, divided by k. It says how much of the cutoff is useful. A 1.5B model drops asks as the prompt grows, so extra chunks have to be useful.

**Recall@k** is the number of relevant rows inside the top k, divided by how many rows in that query's top 10 are relevant. Q002 and Q004 need facts from more than one article. Recall shows whether a small cutoff has caught those parts.

**Hit@k** is 1 when the top k holds at least one relevant row, otherwise 0. It says whether the agent would see any useful chunk.

Five queries is too small a set for MRR or NDCG to add anything beyond these three.

Values below are the figures in `metrics.json`, rounded to two decimals. Q002, Q003, and Q004 each have 6 relevant rows in the top 10, so a recall such as 0.17 is 1/6.

### Precision@k

| Query | k = 1 | k = 3 | k = 5 |
| --- | ---: | ---: | ---: |
| Q001 | 0.00 | 0.00 | 0.20 |
| Q002 | 1.00 | 1.00 | 1.00 |
| Q003 | 1.00 | 0.67 | 0.60 |
| Q004 | 1.00 | 1.00 | 0.80 |
| Q005 | 0.00 | 0.00 | 0.00 |
| Mean | 0.60 | 0.53 | 0.52 |

### Recall@k

| Query | k = 1 | k = 3 | k = 5 |
| --- | ---: | ---: | ---: |
| Q001 | 0.00 | 0.00 | 0.50 |
| Q002 | 0.17 | 0.50 | 0.83 |
| Q003 | 0.17 | 0.33 | 0.50 |
| Q004 | 0.17 | 0.50 | 0.67 |
| Q005 | 0.00 | 0.00 | 0.00 |
| Mean | 0.10 | 0.27 | 0.50 |

### Hit@k

| Query | k = 1 | k = 3 | k = 5 |
| --- | ---: | ---: | ---: |
| Q001 | 0 | 0 | 1 |
| Q002 | 1 | 1 | 1 |
| Q003 | 1 | 1 | 1 |
| Q004 | 1 | 1 | 1 |
| Q005 | 0 | 0 | 0 |
| Mean | 0.60 | 0.60 | 0.80 |

## Failure patterns

**No supporting article.** Q005 asks to enroll a hardware security key and revoke a lost authenticator. No chunk in the top 10 describes either action, so precision, recall, and hit are 0 at every k. Rank 1 is `KB-SHIP-002-1`, a hardware-return rule. Rank 2 is `KB-DIST-001-2`, a password reset that only mentions updating multifactor settings at the next sign-in.

**The useful chunk is not first.** Q001 asks whether there is a current regional incident and when its status was last updated. Ranks 1 to 3 are the scheduled maintenance notice `KB-AWS-MAINT-001` (event `AMS-2023-Q4-NET-17`). The first relevant row is rank 5, `KB-AWS-NEG-003-0`, the general health overview. The row that states an open incident and the last published update is rank 6, `KB-AWS-NEG-003-1`. Hit@1 and hit@3 are 0. Precision@5 is 0.20.

**Answer split across articles, so a small k keeps one part.** Q004 asks for safe flicker checks and for a comparison of the store return with technician service. Ranks 1 to 4 are all `KB-SAM-TV-001`, the flicker checks. The technician intake is rank 7, `KB-SAM-TV-002-1`. The store-return comparison is rank 8, `KB-SAM-NEG-002-3`. At k = 5, recall is 0.67 because those two rows are still outside the cutoff. Q002 is the same shape but recovered sooner: rank 1 is the mail article `KB-JIRA-NEG-001-2`, and rank 2 is the workflow article `KB-JIRA-002-2`. Recall@1 is 0.17. Recall@3 is 0.50.

**A neighbor sits above the rest of the answer.** On Q004, rank 5 is `KB-SAM-NEG-001-2`, an audio article that says picture flicker is out of scope. It occupies a slot in front of the technician and return chunks. On Q003, ranks 3 and 4 are Limits sections (`KB-SHIP-NEG-001-3` and `KB-SHIP-001-4`). They share the shipping topic and do not say how to change an editable address or whether expedited service remains. Precision falls from 1.00 at k = 1 to 0.60 at k = 5.

## Possible improvements

**Add the missing article for Q005.** A hardware-security-key page would give the query something relevant to rank. Changing the chunk size cannot create that page.

**Do not rely on one distance cutoff.** Q005's nearest chunk is farther from the query than Q001's wrong maintenance chunks. A cutoff that drops Q005 would still keep the maintenance notice ahead of the health article. Q001 needs the current-incident wording to outweigh "status" and "health" in the maintenance notice. Putting the title and the words "current" and "unscheduled" into `embedding_text` is the change to test, then re-label and recompute these three metrics.

**Ask multi-part queries as separate searches.** Q004's flicker article fills ranks 1 to 4, and the return-versus-technician chunks land at 7 and 8. One embedding of the whole question favors the first topic. A second search for the return and technician half would give those articles their own top of the list. That matters because Task 6 keeps only one k, and k = 5 still misses both of those chunks.
