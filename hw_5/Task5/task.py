import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW5 = HERE.parent
QUERIES = HW5 / "Fidel Alejandro Rosell Perez - evaluation_queries.json"
DB = HW5 / "Task4" / "lancedb"
HELPER = HW5 / "Fidel Alejandro Rosell Perez - VectorStore.py"
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

    RESULTS.write_text(
        json.dumps(labeled, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"Wrote {RESULTS.name}; set relevant to true or false on every row")

def flags_for(query):
    flags = []
    for row in query["results"]:
        if row["relevant"] is None:
            raise SystemExit(
                f"{query['query_id']} rank {row['rank']} has no label"
            )
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
