# Task 5 — Retrieval Evaluation: Step-by-Step Logic and Code

This document explains the Task 5 workflow and the logic behind each step. It is intended to help you understand what the program does and why, not to compare the original solutions.

## Goal of Task 5

Task 5 evaluates whether the vector store created in Task 4 retrieves text chunks that help answer the supplied evaluation queries. The program retrieves the top 10 chunks for each query. A person then labels each chunk as relevant (`true`) or not relevant (`false`). After labeling, the program calculates Precision@k, Recall@k, and Hit@k at `k = 1, 3, 5`.

The five queries come from the supplied `evaluation_queries.json`. The database is the Task 4 `lancedb` folder. The provided `VectorStore` helper must be used unchanged.

---

## Step 1 — Set the paths and constants

```python
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW5 = HERE.parent
QUERIES = HW5 / "Fidel Alejandro Rosell Perez - evaluation_queries.json"
DB = HW5 / "Task4" / "lancedb"
HELPER = HW5 / "vector_setup" / "Fidel Alejandro Rosell Perez - VectorStore.py"
RESULTS = HERE / "retrieval_results.json"
METRICS = HERE / "metrics.json"
K_VALUES = (1, 3, 5)
```

### Logic

- `Path` builds file-system paths in a way that does not depend on the terminal's current folder.
- `HERE` is the folder containing this Task 5 script.
- `HW5` is its parent homework folder.
- `QUERIES` points to the provided evaluation queries.
- `DB` points to the vector database built in Task 4.
- `HELPER` points to the course-provided `VectorStore` class.
- `RESULTS` will store retrieved results and later your relevance labels.
- `METRICS` will store the computed evaluation metrics.
- `K_VALUES` defines the cutoffs: top 1, top 3, and top 5.

The paths must match your actual homework folder layout. Do not modify the supplied helper just to make the script work.

## Step 2 — Load the supplied VectorStore class

```python
def load_vector_store_class():
    spec = importlib.util.spec_from_file_location("vector_store_helper", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.VectorStore
```

### Logic

Python normally imports modules by module name. The course helper's filename contains spaces, so this code loads it from its file path. It returns the `VectorStore` class so the script can open the database created in Task 4.

This keeps Task 5 consistent with the course's required embedding and retrieval implementation.

## Step 3 — Retrieve the top 10 chunks for every query

```python
def retrieve():
    queries = json.loads(QUERIES.read_text(encoding="utf-8"))
    store = load_vector_store_class()(DB)
    labeled = []

    for item in queries:
        hits = store.query(item["query"], top_k=10)
        labeled.append(
            {
                "query_id": item["query_id"],
                "query": item["query"],
                "results": [
                    {
                        "rank": hit["rank"],
                        "chunk_id": hit["chunk_id"],
                        "distance": hit["distance"],
                        "content": hit["content"],
                        "metadata": hit["metadata"],
                        "relevant": None,
                    }
                    for hit in hits
                ],
            }
        )

    RESULTS.write_text(
        json.dumps(labeled, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {RESULTS.name}; set relevant to true or false on every row")
```

### Logic, line by line

1. Read the query definitions from the supplied JSON file.
2. Load the `VectorStore` class and open the Task 4 database.
3. Loop through each query.
4. Call `store.query(..., top_k=10)` to retrieve up to ten results for that query.
5. Save the query ID and query text so the results remain associated with the right question.
6. Save each result's rank, chunk ID, distance, content, and metadata. These fields let you inspect what was retrieved and where it appeared in the ranking.
7. Set `relevant` to `None`. This deliberately means “not judged yet”; the program must not guess relevance automatically.
8. Write the results to `retrieval_results.json`.

With five queries and ten results per query, you expect up to 50 result rows. This assumes each query returns ten results; the actual count depends on what the database returns.

### Why retrieve before labeling?

The retrieval system ranks chunks by its search method. Distance and rank are useful signals, but they do not establish whether a chunk answers the query. A human must judge the actual content.

### Important protection for manual labels

The Cursor version writes `retrieval_results.json` every time `retrieve()` runs. If you add labels to that file and rerun retrieval, your labels can be lost. After labeling, do not rerun retrieval unless you have backed up your labels and deliberately intend to refresh the results.

---

## Step 4 — Label every result manually

Open `retrieval_results.json`. For every result, change `relevant` from `null` to `true` or `false`.

Example:

```json
{
  "rank": 1,
  "chunk_id": "example-chunk-id",
  "distance": 0.12,
  "content": "Text of the retrieved chunk...",
  "metadata": {
    "title": "Example article"
  },
  "relevant": true
}
```

The example is illustrative; use the actual chunk IDs, text, and metadata from your generated file.

### Logic for labeling

- `true`: the chunk contains information that helps answer the query, even if it only answers part of it.
- `false`: the chunk does not help answer the query, even if it uses similar words or discusses a related subject.
- Do not label by rank. Rank is the system's ordering; relevance is your independent judgment of usefulness.
- Use the same rule for every query so the evaluation is consistent.

For the homework report, keep a short reason for each judgment or document the reasoning in a separate table. The original Cursor results file does not include a reason field, so do not add one unless your workflow or instructor allows additional fields. You can record reasons separately without changing the program's expected JSON structure.

**Do not run the metric command until every result has been labeled.**

---

## Step 5 — Convert labels into a list of flags

```python
def flags_for(query):
    flags = []
    for row in query["results"]:
        if row["relevant"] is None:
            raise SystemExit(
                f"{query['query_id']} rank {row['rank']} has no label"
            )
        flags.append(bool(row["relevant"]))
    return flags
```

### Logic

The metrics need a simple ordered list of Boolean values. For example:

```python
[True, False, True, False, False, True, False, False, False, False]
```

This means ranks 1, 3, and 6 are relevant; the other ranks are not.

The function processes results in their saved order and stops if any label is still `None`. That prevents incomplete labeling from silently being treated as irrelevant.

This code expects `relevant` to contain JSON booleans (`true` or `false`), not the text strings `"true"` or `"false"`.

---

## Step 6 — Calculate Precision@k

```python
def precision_at_k(flags, k):
    return sum(flags[:k]) / k
```

### Logic

`flags[:k]` selects the first `k` results. In Python, `True` counts as 1 and `False` counts as 0 when summed.

Precision@k = relevant chunks in the top k ÷ k.

Example: if the top three labels are `[True, False, True]`, Precision@3 = 2 / 3 ≈ 0.67.

**Interpretation:** Precision tells you what fraction of the chunks supplied within that cutoff are useful.

## Step 7 — Calculate Recall@k

```python
def recall_at_k(flags, k):
    relevant = sum(flags)
    if relevant == 0:
        return 0.0
    return sum(flags[:k]) / relevant
```

### Logic in the provided Cursor code

- `relevant = sum(flags)` counts the relevant chunks among the labeled top-10 results.
- `sum(flags[:k])` counts the relevant chunks within the first `k` ranks.
- The function divides the top-k relevant count by the total relevant count in the top 10.

Recall@k = relevant chunks in the top k ÷ relevant chunks in the retrieved top 10.

Example: if three of the top 10 are relevant and two of those appear in the top five, Recall@5 = 2 / 3 ≈ 0.67.

### A caveat about zero relevant results

If the top 10 contains no relevant chunk, the denominator is zero and recall is mathematically undefined. The Cursor code uses `0.0` for this case, while the Claude code uses `None` and excludes it from the recall mean. For a mathematically careful report, `None`/`null` is preferable, because it distinguishes “undefined” from a measured recall of zero. If you must keep the supplied Cursor code unchanged, explain its convention in the report.

This is recall relative to the relevant chunks judged in the retrieved top 10, not necessarily recall across every relevant chunk in the entire database.

**Interpretation:** Recall tells you how much of the useful material found in the top 10 has been retrieved by rank `k`.

## Step 8 — Calculate Hit@k

```python
def hit_at_k(flags, k):
    return 1 if any(flags[:k]) else 0
```

### Logic

`any(flags[:k])` is true if at least one of the first `k` results is relevant.

- `1`: at least one useful chunk appears in the top `k`.
- `0`: none of the first `k` chunks is relevant.

**Interpretation:** Hit@k answers whether the downstream agent receives at least one useful chunk within that context size.

## Step 9 — Average each metric across queries

```python
def mean(values):
    return sum(values) / len(values)
```

For each cutoff (`1`, `3`, and `5`), the program computes a metric for each query, then takes the mean across the five queries.

For example, mean Precision@3 is the average of the five per-query Precision@3 values. This gives every query equal weight, regardless of how many relevant chunks it contains.

If using the Claude version's undefined-recall convention, its `mean()` removes `None` values before averaging. If using the Cursor version, the zero values are included.

## Step 10 — Save and interpret the metrics

The Cursor script builds a report containing:
- `per_query`: each query's precision, recall, and hit values at all three cutoffs.
- `mean_precision`: average precision for `k = 1, 3, 5`.
- `mean_recall`: average recall for those cutoffs.
- `mean_hit`: average hit rate for those cutoffs.

It writes the result to `metrics.json`. Task 6 uses this file to help choose how many retrieved chunks to pass to the next stage.

### How to interpret the numbers

- Higher Precision@k means a larger proportion of the top-k context is useful.
- Higher Recall@k means more of the judged relevant chunks from the top 10 are included by that cutoff.
- Higher Hit@k means more queries have at least one useful chunk in the top-k results.
- Comparing `k = 1`, `3`, and `5` shows the trade-off between giving the next-stage model more context and including extra irrelevant material.

Do not automatically conclude that the largest `k` is best. Use the actual metric values and Task 6's context constraints.

---

## Step 11 — Run the commands in the correct order

From the Task 5 folder:

```bash
python evaluate_retrieval.py retrieve
```

Then:

1. Open `retrieval_results.json`.
2. Replace every `null` in `relevant` with `true` or `false`.
3. Save the file.
4. Verify every result is labeled.
5. Run:

```bash
python evaluate_retrieval.py metrics
```

The program writes `metrics.json` and prints the metrics. Review the output before using it in Task 6.

## Final mental model

- **Retrieval** asks: “Which chunks does the vector store return for this question?”
- **Relevance labeling** asks: “Does each returned chunk actually help answer the question?”
- **Precision** asks: “How much of the top-k material is useful?”
- **Recall** asks: “How much of the relevant material found in the top 10 appears in the top k?”
- **Hit** asks: “Is there at least one useful chunk in the top k?”
- **Averaging** summarizes these scores across the five evaluation queries.

These stages measure retrieval quality. They do not, by themselves, prove that the final answer generated by the downstream assistant is correct.
