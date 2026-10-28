# Task 6 — Merged RAG Implementation and Logic

Save the Python code as `rag_summary.py` in the Task 6 folder. Run: `python rag_summary.py 28763`.

## Logic

1. Load Task 5 precision/recall metrics and choose the smallest qualifying `k`.
2. Load the original ticket body through the established Homework 4 loader.
3. Retrieve `k` chunks using the unaltered body.
4. Reuse the accepted Homework 4 prompt, changing only its ticket-only rule to distinguish ticket facts from article context.
5. Call the same model and JSON schema, validate the response, and save retrieval and generation evidence.

## Code

```python
import importlib.util
import json
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
HW5 = HERE.parent
ROOT = HERE.parents[2]

DB = HW5 / "Task4" / "lancedb"
HELPER = HW5 / "vector_setup" / "Fidel Alejandro Rosell Perez - VectorStore.py"
METRICS = HW5 / "Task5" / "metrics.json"
LLM_PATH = ROOT / "hw_4" / "Task5" / "llm_summary.py"

ACCEPTED_RULE = (
    "Use only the information in the ticket text. Do not add facts. Do not guess. "
    "Do not suggest a solution. Do not say which department should handle the ticket."
)
RAG_RULE = (
    "The ticket body is what the customer wrote. Support articles are outside context. "
    "Use an article only when it applies. Use article context only to identify information "
    "missing from the ticket; never present article facts as customer statements. Do not "
    "add unsupported facts, guess, suggest a solution, or assign a department."
)


def load_module(name, path):
    if not path.exists():
        raise FileNotFoundError(f"Required file not found: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def choose_k(mean_precision, mean_recall):
    chosen = 1
    for bigger, smaller in ((3, 1), (5, 3)):
        recall_gain = mean_recall[bigger] - mean_recall[smaller]
        if recall_gain >= 0.10 and mean_precision[bigger] >= 0.50:
            chosen = bigger
        else:
            break
    return chosen


def selected_k():
    report = json.loads(METRICS.read_text(encoding="utf-8"))
    precision = {int(k): v for k, v in report["mean_precision"].items()}
    recall = {int(k): v for k, v in report["mean_recall"].items()}
    return choose_k(precision, recall)


def system_prompt():
    prompt_path = ROOT / "hw_4" / "Task7" / "prompt_iteration_1.txt"
    accepted = prompt_path.read_text(encoding="utf-8").strip()
    if ACCEPTED_RULE not in accepted:
        raise ValueError(
            "Accepted Homework 4 prompt does not contain the expected ticket-only rule. "
            "Check ACCEPTED_RULE against prompt_iteration_1.txt."
        )
    return accepted.replace(ACCEPTED_RULE, RAG_RULE)


def article_block(hits):
    return "\n\n".join(
        f"[{hit['chunk_id']}] {hit['metadata']['title']}\n{hit['content']}"
        for hit in hits
    )


def user_message(body, hits):
    articles = article_block(hits) or "(No support articles retrieved.)"
    return (
        f"TICKET BODY (customer-provided text):\n{body}\n\n"
        f"SUPPORT ARTICLES (external context, not customer statements):\n{articles}"
    )


def summarize_with_rag(body, llm, store, k):
    hits = store.query(body, top_k=k)
    messages = [
        {"role": "system", "content": system_prompt()},
        {"role": "user", "content": user_message(body, hits)},
    ]
    payload = {
        "model": llm.MODEL,
        "messages": messages,
        "format": llm.SCHEMA,
        "stream": False,
        "options": {"temperature": 0, "seed": 42, "num_predict": 512},
    }
    response = requests.post(llm.URL, json=payload, timeout=600)
    response.raise_for_status()
    raw = response.json()["message"]["content"]

    try:
        output, error = llm.validate_summary(raw), None
    except ValueError as exc:
        output, error = None, str(exc)

    return {
        "k": k,
        "hits": hits,
        "messages": messages,
        "raw": raw,
        "output": output,
        "error": error,
    }


def main():
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python rag_summary.py TICKET_ID")

    ticket_id = int(sys.argv[1])
    llm = load_module("llm_summary", LLM_PATH)
    vector_module = load_module("vector_store_helper", HELPER)
    store = vector_module.VectorStore(DB)
    k = selected_k()

    tickets = llm.load_tickets([ticket_id])
    if ticket_id not in tickets:
        raise KeyError(f"Ticket ID {ticket_id} was not found.")
    body = tickets[ticket_id]

    result = summarize_with_rag(body, llm, store, k)
    output_path = HERE / f"rag_{ticket_id}.json"
    output_path.write_text(
        json.dumps(result, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"k = {k}")
    print(f"error: {result['error']}")
    print(f"wrote {output_path.name}")


if __name__ == "__main__":
    main()
```

## Before running

Confirm `ROOT`, `LLM_PATH`, and `prompt_iteration_1.txt` match your repository layout. The accepted prompt must contain the exact `ACCEPTED_RULE` text. This merged implementation has not been runtime-tested against your local database, model, or files.
