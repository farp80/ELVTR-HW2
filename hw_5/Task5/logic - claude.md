# Task 5 - Evaluate Retrieval - claude

## Logic

1. Load the five queries from `evaluation_queries.json`.
2. Run each with `top_k = 10`. That gives 50 rows.
3. Label each row relevant or not relevant. Relevant means the chunk helps answer the query.
4. Test k = 1, 3, and 5.
5. For each query and each k, compute:
   - **Precision@k**: relevant in top k, divided by k.
   - **Recall@k**: relevant in top k, divided by all relevant in the top 10.
   - **Hit@k**: 1 if any relevant chunk is in the top k, else 0.
6. Average each metric over the five queries.
7. Report failures.

## Reasoning

Precision shows how much of what we give the model is useful. Recall shows how much of the useful material we caught. Hit shows if the model gets at least one good chunk.

Recall uses the labeled top 10 as its total, because that is all we labeled.

k = 1, 3, 5 fit in a small model's prompt. The averages decide k in Task 6.

Failures to look for: no matching article (Q005), answers split across articles (Q002, Q004), and a similar wrong article ranked higher.
