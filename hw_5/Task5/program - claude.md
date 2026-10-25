# Task 5 - Query Code and Metric Code - claude

This file has two code blocks. Save each in this folder. They run in order, with **your manual labeling in between**.

| Step | File to save | Command | What it produces |
| --- | --- | --- | --- |
| 1 | `run_queries.py` | `python run_queries.py` | `retrieval_top10.md` (to read) and `labels.json` (to fill in) |
| 2 | you | edit `labels.json` | Set every `relevant` to `true` or `false` |
| 3 | `compute_metrics.py` | `python compute_metrics.py` | `metrics.json` and `metrics_tables.md` |

I could not run this code on my machine because the vector-store packages are not installed there. No results are claimed in this file.

---

## Logic - Step 1: query the store

1. Load the five queries from `evaluation_queries.json`.
2. For each query, call `VectorStore.query(query, top_k=10)`. That is 50 rows.
3. Write every row to `retrieval_top10.md`: query, rank, chunk ID, distance, and the chunk text. You read this file to label.
4. Write `labels.json` with one entry per row and `"relevant": null`. If `labels.json` already exists, **do not overwrite it**, so your labels are never lost.

## Code - `run_queries.py`

```python
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
HW5 = HERE.parent
DB = HW5 / "Task4" / "lancedb"
QUERIES = HW5 / "Fidel Alejandro Rosell Perez - evaluation_queries.json"
HELPER = HW5 / "vector_setup" / "Fidel Alejandro Rosell Perez - VectorStore.py"
TOP_K = 10
FENCE = "`" * 3  # Markdown code fence, written this way so it does not break this page


def load_store():
    spec = importlib.util.spec_from_file_location("vector_store_helper", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.VectorStore(DB)


def main():
    store = load_store()
    queries = json.loads(QUERIES.read_text(encoding="utf-8"))
    lines = ["# Task 5 - Top 10 results per query", ""]
    labels = {}
    for item in queries:
        qid, text = item["query_id"], item["query"]
        hits = store.query(text, top_k=TOP_K)
        lines += [f"## {qid}", "", f"**Query:** {text}", ""]
        labels[qid] = {"query": text, "results": []}
        for hit in hits:
            lines += [
                f"### {qid} rank {hit['rank']} - {hit['chunk_id']} (distance {hit['distance']:.4f})",
                f"Article: {hit['metadata']['title']}",
                "",
                FENCE + "text",
                hit["content"],
                FENCE,
                "",
            ]
            labels[qid]["results"].append(
                {"rank": hit["rank"], "chunk_id": hit["chunk_id"], "relevant": None}
            )
    (HERE / "retrieval_top10.md").write_text("\n".join(lines), encoding="utf-8")
    labels_path = HERE / "labels.json"
    if labels_path.exists():
        print("labels.json exists - not overwritten")
    else:
        labels_path.write_text(json.dumps(labels, indent=2, ensure_ascii=False), encoding="utf-8")
        print("wrote labels.json - set every relevant to true or false")


if __name__ == "__main__":
    main()
```

---

## Step 2 - How to label (by hand)

For each of the 50 rows, ask one question: **does this chunk contain information that helps answer the query?**

- `true`: it helps, even if it answers only part of the query.
- `false`: it is on a related topic but does not help, or it is about another product.

Write a short reason for each label in your report. Label by meaning, not by rank.

---

## Logic - Step 3: compute metrics

For each query, make a list of 10 labels in rank order, for example `[1, 0, 1, 0, 0, ...]`. Then for each `k` in **1, 3, 5**:

| Metric | Formula | What it tells you |
| --- | --- | --- |
| **Precision@k** | relevant in top k / k | How much of what the model receives is useful. |
| **Recall@k** | relevant in top k / relevant in the top 10 | How much of the useful material was caught. |
| **Hit@k** | 1 if any relevant chunk is in the top k, else 0 | Does the model get at least one good chunk? |

**Recall caveat.** The total is the number of relevant chunks you labeled in the top 10, because only those are labeled. A relevant chunk at rank 30 is invisible. If a query has no relevant chunk at all (likely Q005, which asks about a security key), recall cannot be computed. The code records `null` and leaves that query out of the recall average. Say this in the report.

**Why these k values.** k = 1, 3, 5 are sizes that fit in the prompt of a small model. Task 6 chooses from them.

## Code - `compute_metrics.py`

```python
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
KS = (1, 3, 5)


def precision(rel, k):
    return sum(rel[:k]) / k


def recall(rel, k):
    total = sum(rel)
    return sum(rel[:k]) / total if total else None  # undefined with no relevant chunk


def hit(rel, k):
    return 1 if any(rel[:k]) else 0


def mean(values):
    values = [v for v in values if v is not None]
    return sum(values) / len(values) if values else None


def fmt(value):
    return "n/a" if value is None else f"{value:.2f}"


def main():
    labels = json.loads((HERE / "labels.json").read_text(encoding="utf-8"))
    per_query = {}
    for qid, entry in labels.items():
        rows = sorted(entry["results"], key=lambda r: r["rank"])
        if any(r["relevant"] is None for r in rows):
            raise SystemExit(f"{qid} still has unlabeled rows")
        rel = [1 if r["relevant"] else 0 for r in rows]
        per_query[qid] = {
            str(k): {"precision": precision(rel, k), "recall": recall(rel, k), "hit": hit(rel, k)}
            for k in KS
        }

    summary = {
        name: {str(k): mean([per_query[q][str(k)][name] for q in per_query]) for k in KS}
        for name in ("precision", "recall", "hit")
    }
    metrics = {
        "ks": list(KS),
        "mean_precision": summary["precision"],
        "mean_recall": summary["recall"],
        "mean_hit": summary["hit"],
        "per_query": per_query,
    }
    (HERE / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    lines = ["# Task 5 - Metric tables", ""]
    for name, title in (("precision", "Precision@k"), ("recall", "Recall@k"), ("hit", "Hit@k")):
        lines += [f"## {title}", "", "| Query | " + " | ".join(f"k={k}" for k in KS) + " |",
                  "| --- | " + " | ".join("---:" for _ in KS) + " |"]
        for qid in per_query:
            lines.append(f"| {qid} | " + " | ".join(fmt(per_query[qid][str(k)][name]) for k in KS) + " |")
        lines.append("| **All queries (mean)** | " + " | ".join(f"**{fmt(summary[name][str(k)])}**" for k in KS) + " |")
        lines.append("")
    (HERE / "metrics_tables.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote metrics.json and metrics_tables.md")


if __name__ == "__main__":
    main()
```

## What each part does

| Part | What it does |
| --- | --- |
| `precision`, `recall`, `hit` | The three formulas above, one function each. |
| `mean` | Averages over queries and skips `None` (recall with no relevant chunk). |
| `sorted(..., key=rank)` | Keeps the labels in rank order, so `rel[:k]` is exactly the top k. |
| unlabeled check | Stops the program if any `relevant` is still `null`. |
| `metrics.json` | Read by Task 6 to choose `k`. |
| `metrics_tables.md` | Per-query and overall values for every k. Paste it into the report. |
