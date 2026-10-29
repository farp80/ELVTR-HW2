# Task 5 — Retrieval evaluation report

The five queries are in `evaluation_queries.json`. `task.py retrieve` saved the top 10 chunks for each query in `retrieval_results.json`. I labeled every row. `true` means the chunk text helps answer that query, including a partial answer. The reasons are in `relevance_justification.md`. `task.py metrics` wrote `metrics.json`.

Recall uses the labeled top 10 as the full set of relevant chunks. A relevant chunk at rank 11 is not counted. When a query has no relevant chunk in the top 10, recall is recorded as 0 and that query stays in the average. That is the Q005 case.

## Metrics

I used three metrics at k = 1, 3, and 5. These are the list sizes that can fit in the later prompt. Five queries is too small a set for MRR or NDCG to add anything beyond these three.

Values below are the figures in `metrics.json`, rounded to two decimals. Q002, Q003, and Q004 each have 6 relevant rows in the top 10, so a recall such as 0.17 is 1/6.

### Precision@k

**What it measures:** relevant rows inside the top k, divided by k. It says how much of the cutoff is useful. A 1.5B model drops asks as the prompt grows, so extra chunks have to be useful.

**Q001:** k = 1 is 0.00. k = 3 is 0.00. k = 5 is 0.20.

**Q002:** k = 1 is 1.00. k = 3 is 1.00. k = 5 is 1.00.

**Q003:** k = 1 is 1.00. k = 3 is 0.67. k = 5 is 0.60.

**Q004:** k = 1 is 1.00. k = 3 is 1.00. k = 5 is 0.80.

**Q005:** k = 1 is 0.00. k = 3 is 0.00. k = 5 is 0.00.

**Mean:** k = 1 is 0.60. k = 3 is 0.53. k = 5 is 0.52.

### Recall@k

**What it measures:** relevant rows inside the top k, divided by the relevant rows in that query's top 10. Q002 and Q004 need facts from more than one article. Recall shows whether a small cutoff has caught those parts.

**Q001:** k = 1 is 0.00. k = 3 is 0.00. k = 5 is 0.50.

**Q002:** k = 1 is 0.17. k = 3 is 0.50. k = 5 is 0.83.

**Q003:** k = 1 is 0.17. k = 3 is 0.33. k = 5 is 0.50.

**Q004:** k = 1 is 0.17. k = 3 is 0.50. k = 5 is 0.67.

**Q005:** k = 1 is 0.00. k = 3 is 0.00. k = 5 is 0.00.

**Mean:** k = 1 is 0.10. k = 3 is 0.27. k = 5 is 0.50.

### Hit@k

**What it measures:** 1 when the top k holds at least one relevant row, otherwise 0. It says whether the agent would see any useful chunk.

**Q001:** k = 1 is 0. k = 3 is 0. k = 5 is 1.

**Q002:** k = 1 is 1. k = 3 is 1. k = 5 is 1.

**Q003:** k = 1 is 1. k = 3 is 1. k = 5 is 1.

**Q004:** k = 1 is 1. k = 3 is 1. k = 5 is 1.

**Q005:** k = 1 is 0. k = 3 is 0. k = 5 is 0.

**Mean:** k = 1 is 0.60. k = 3 is 0.60. k = 5 is 0.80.

## Failure patterns

### Q005 — No supporting article

The query asks to enroll a hardware security key and revoke a lost authenticator. No chunk describes either action, so precision, recall, and hit are 0 at every k. Rank 1 is `KB-SHIP-002-1`, a hardware-return rule. Rank 2 is `KB-DIST-001-2`, a password reset that only mentions updating multifactor settings at the next sign-in.

### Q001 — The useful chunk is not first

The query asks whether there is a current regional incident and when its status was last updated. Ranks 1 to 3 are the scheduled maintenance notice `KB-AWS-MAINT-001` (event `AMS-2023-Q4-NET-17`). The first relevant row is rank 5, `KB-AWS-NEG-003-0`. The row that states an open incident and the last published update is rank 6, `KB-AWS-NEG-003-1`. Hit@1 and hit@3 are 0. Precision@5 is 0.20.

### Q004 — Answer split across articles

The query asks for safe flicker checks and a comparison of the store return with technician service. Ranks 1 to 4 are all `KB-SAM-TV-001`. The technician intake is rank 7, `KB-SAM-TV-002-1`. The store-return comparison is rank 8, `KB-SAM-NEG-002-3`. At k = 5, recall is 0.67 because those two rows are still outside the cutoff.

### Q002 — Answer split across articles

Rank 1 is the mail article `KB-JIRA-NEG-001-2`, and rank 2 is the workflow article `KB-JIRA-002-2`. Recall@1 is 0.17. Recall@3 is 0.50. The two parts arrive earlier than they do on Q004.

### Q004 — A neighbor sits above the rest of the answer

Rank 5 is `KB-SAM-NEG-001-2`, an audio article that says picture flicker is out of scope. It occupies a slot in front of the technician and return chunks.

### Q003 — A neighbor sits above the rest of the answer

Ranks 3 and 4 are Limits sections (`KB-SHIP-NEG-001-3` and `KB-SHIP-001-4`). They share the shipping topic and do not say how to change an editable address or whether expedited service remains. Precision falls from 1.00 at k = 1 to 0.60 at k = 5.

## Possible improvements

### Add a hardware-security-key article for Q005

The query has nothing relevant to rank. Changing the chunk size cannot create that page.

### Put "current" and "unscheduled" into the embedded text

Put the title and the words "current" and "unscheduled" into `embedding_text`, then re-label and recompute. Q005's nearest chunk is farther from the query than Q001's wrong maintenance chunks. A distance cutoff that drops Q005 would still keep the maintenance notice ahead of the health article.

### Search each part of a multi-part query on its own

Q004's flicker article fills ranks 1 to 4, and the return-versus-technician chunks land at 7 and 8. One embedding of the whole question favors the first topic. Task 6 keeps one k, and k = 5 still misses both of those chunks.
