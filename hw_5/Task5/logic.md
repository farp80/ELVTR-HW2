# Task 5 — Score retrieval

The program is in `program-cursor.md`.

## Logic

Run the five queries in `evaluation_queries.json`. For each query, call `query()` with `top_k` 10. Label all 50 rows relevant or not relevant. A row is relevant when the chunk text helps answer that query.

Use three cutoffs: k = 1, k = 3, and k = 5. For each query and each k, compute:

- Precision: relevant rows inside the top k, divided by k.
- Recall: relevant rows inside the top k, divided by how many rows in that query's top 10 are relevant.
- Hit: 1 when the top k has at least one relevant row, otherwise 0.

Average each metric across the five queries at that same k.

Group the misses in the report.

- Q005 asks for a hardware security key and a lost authenticator. No article covers that, so those misses are missing documents.
- Q002 needs a workflow article and a mail article. Q004 needs flicker checks, the store-return window, and technician routing. Those misses are split answers.
- A neighbor article that ranks above the article that answers the question is the third group. On Q001 the named maintenance notice ranks above the general health article. On Q004 an audio chunk ranks above the return and technician chunks.

## Reasoning

Precision says how much of the cutoff is useful. Recall says how much of the useful material already found in the top 10 sits inside that cutoff. Hit says whether at least one useful chunk would reach the agent. The report states that recall treats the labeled top 10 as the full set of relevant chunks.

k = 1, 3, and 5 are the list sizes that can fit in the later prompt. The average at each k is what Task 6 uses to pick one k. Q005 stays low until the knowledge base has a page for security keys. A different chunk size does not create that page.
