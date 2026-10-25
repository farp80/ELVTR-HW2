# Task 5 program

Put the blocks below, in order, into `evaluate_retrieval.py` in this folder. Run `python evaluate_retrieval.py retrieve`, label the file, then run `python evaluate_retrieval.py metrics`.

## Logic — pull the top 10 and leave the judgment blank

The five queries are the supplied `evaluation_queries.json`. Each query is sent to the Task 4 database with `top_k` 10. The script copies rank, chunk id, distance, content, and metadata. `relevant` is left empty. You set it to `true` or `false` by hand. A row is relevant when the chunk text helps answer that query. The script writes `retrieval_results.json` and stops there, so the labels are yours.

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


def load_vector_store_class():
    spec = importlib.util.spec_from_file_location("vector_store_helper", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.VectorStore


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
    RESULTS.write_text(json.dumps(labeled, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote {RESULTS.name}; set relevant to true or false on every row")
```

## Logic — three scores at three cutoffs

`flags_for` turns your labels into a list in rank order. An empty label stops the run, so a skipped row cannot become a zero by accident.

Precision at k is the number of relevant rows inside the top k, divided by k. It says how much of that cutoff is useful.

Recall at k is the number of relevant rows inside the top k, divided by how many rows in that query's top 10 are relevant. It says how much of the useful material you already found has reached that cutoff. When the top 10 has no relevant row, recall is 0. That is the Q005 case: no article covers a hardware security key.

Hit at k is 1 when the top k holds at least one relevant row. It says whether the agent would see a useful chunk.

The cutoffs are k = 1, k = 3, and k = 5. Those are the list sizes that can fit in the Task 6 prompt. The script then averages each score across the five queries. Task 6 reads those averages from `metrics.json`.

```python
def flags_for(query):
    flags = []
    for row in query["results"]:
        if row["relevant"] is None:
            raise SystemExit(f"{query['query_id']} rank {row['rank']} has no label")
        flags.append(bool(row["relevant"]))
    return flags


def precision_at_k(flags, k):
    return sum(flags[:k]) / k


def recall_at_k(flags, k):
    relevant = sum(flags)
    if relevant == 0:
        return 0.0
    return sum(flags[:k]) / relevant


def hit_at_k(flags, k):
    return 1 if any(flags[:k]) else 0


def mean(values):
    return sum(values) / len(values)


def metrics():
    labeled = json.loads(RESULTS.read_text(encoding="utf-8"))
    per_query = []
    for query in labeled:
        flags = flags_for(query)
        per_query.append(
            {
                "query_id": query["query_id"],
                "precision": {str(k): precision_at_k(flags, k) for k in K_VALUES},
                "recall": {str(k): recall_at_k(flags, k) for k in K_VALUES},
                "hit": {str(k): hit_at_k(flags, k) for k in K_VALUES},
            }
        )
    report = {
        "per_query": per_query,
        "mean_precision": {
            str(k): mean([row["precision"][str(k)] for row in per_query]) for k in K_VALUES
        },
        "mean_recall": {
            str(k): mean([row["recall"][str(k)] for row in per_query]) for k in K_VALUES
        },
        "mean_hit": {
            str(k): mean([row["hit"][str(k)] for row in per_query]) for k in K_VALUES
        },
    }
    METRICS.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "retrieve":
        retrieve()
    elif command == "metrics":
        metrics()
    else:
        raise SystemExit("use: python evaluate_retrieval.py retrieve|metrics")
```
