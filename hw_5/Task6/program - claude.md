# Task 6 - RAG Prompt and LLM-Call Code - claude

Save the code block below as `rag_summary.py` in this folder. Run it after Task 5 has written `../Task5/metrics.json`:

```text
python rag_summary.py 28763
```

It picks `k`, searches the vector store with the unaltered ticket `Body`, builds the prompt from `prompt - claude.md`, calls the model, and writes `rag_28763.json`. Task 7 imports the same file.

I could not run it on my machine (the vector-store packages and the local model are not available there). Check the first run yourself.

## Logic (read this before the code)

1. **Choose `k`.** Read the mean precision and recall from `metrics.json`. Apply the rule in `prompt - claude.md`: start at 1, move up only when recall rises by at least 0.10 and precision stays at 0.5 or more.
2. **Get the ticket text.** Read the unaltered `Body` from the canonical dataset. Nothing is cleaned or shortened.
3. **Retrieve.** Call `store.query(body, top_k=k)`. The query is the raw body.
4. **Build the messages.**
   - System message: the Task 6 prompt.
   - User message: a `TICKET BODY` block, then a `SUPPORT ARTICLES` block.
5. **Call the model** with the Homework 4 settings: model `qwen2.5:1.5b-instruct-q4_K_M`, `temperature` 0, `seed` 42, `stream` false, `num_predict` 512. The JSON schema forces the three fields.
6. **Validate** the answer with the same checks as Homework 4. Return the output, or the error.
7. **Save everything** (k, retrieved chunks, messages, raw answer) so Task 7 can show retrieval results next to each summary.

## What did not change from Homework 4

The model, the three output fields, the schema, the validation, and the field descriptions. The only changes are the prompt's source paragraph, the second block in the user message, and `num_predict`.

## Code

```python
import importlib.util
import json
import sys
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
HW5 = HERE.parent
DB = HW5 / "Task4" / "lancedb"
METRICS = HW5 / "Task5" / "metrics.json"
HELPER = HW5 / "vector_setup" / "Fidel Alejandro Rosell Perez - VectorStore.py"
# Canonical dataset. Change this path to where the CSV lives on your machine.
DATA_PATH = HW5.parent / "hw_2" / "Fidel Alejandro Rosell Perez - support_tickets.csv"

URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b-instruct-q4_K_M"
OPTIONS = {"temperature": 0, "seed": 42, "num_predict": 512}

SCHEMA = {
    "type": "object",
    "properties": {
        "summary": {"type": "string"},
        "customer_request": {"type": "string"},
        "missing_information": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["summary", "customer_request", "missing_information"],
    "additionalProperties": False,
}

SYSTEM_PROMPT = """You write an internal summary of a customer support ticket for a human support agent.

You receive two sources, in two labeled blocks:
- TICKET BODY: what the customer wrote. This is the only text you summarize.
- SUPPORT ARTICLES: approved company articles found for this ticket. The customer did not write them. They are background help only.

Describe only what the customer wrote in the TICKET BODY. Use the SUPPORT ARTICLES only to decide which details the customer did not give but support needs. Never copy article facts into summary or customer_request. If no article applies to this ticket, ignore the articles. Do not add facts. Do not guess. Do not suggest a solution. Do not say which department should handle the ticket.

Return a JSON object with exactly these fields:
- summary: one or two short sentences describing the reported issue.
- customer_request: everything the customer asks for, in one or two sentences. Include every request and every question.
- missing_information: a list of details needed to understand or act on the request. Use an empty list if nothing is clearly missing."""


def choose_k(mean_precision, mean_recall):
    chosen = 1
    for bigger, smaller in ((3, 1), (5, 3)):
        gain = mean_recall[bigger] - mean_recall[smaller]
        if gain >= 0.10 and mean_precision[bigger] >= 0.5:
            chosen = bigger
        else:
            break  # a failed step stops the climb
    return chosen


def selected_k():
    report = json.loads(METRICS.read_text(encoding="utf-8"))
    precision = {int(k): v for k, v in report["mean_precision"].items()}
    recall = {int(k): v for k, v in report["mean_recall"].items()}
    return choose_k(precision, recall)


def load_store():
    spec = importlib.util.spec_from_file_location("vector_store_helper", HELPER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.VectorStore(DB)


def load_body(ticket_id):
    tickets = pd.read_csv(DATA_PATH).set_index("ticket_id")
    return tickets.loc[ticket_id, "Body"]  # unaltered


def format_articles(hits):
    parts = [f"[{h['chunk_id']}] {h['metadata']['title']}\n{h['content']}" for h in hits]
    return "\n\n".join(parts)


def build_messages(body, hits):
    user = (
        f"TICKET BODY (written by the customer):\n{body}\n\n"
        f"SUPPORT ARTICLES (company knowledge, not written by the customer):\n{format_articles(hits)}"
    )
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user},
    ]


def call_llm(messages):
    payload = {"model": MODEL, "messages": messages, "format": SCHEMA, "stream": False, "options": OPTIONS}
    response = requests.post(URL, json=payload, timeout=600)
    response.raise_for_status()
    return response.json()["message"]["content"]


def validate_summary(raw_text):
    """Same checks as Homework 4. Returns the dict, or raises ValueError."""
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"not valid JSON: {exc}")
    expected = {"summary", "customer_request", "missing_information"}
    if not isinstance(data, dict) or set(data) != expected:
        raise ValueError(f"fields must be exactly {sorted(expected)}")
    for key in ("summary", "customer_request"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"'{key}' must be a non-empty string")
    missing = data["missing_information"]
    if not isinstance(missing, list) or not all(isinstance(x, str) and x.strip() for x in missing):
        raise ValueError("'missing_information' must be a list of non-empty strings")
    return data


def summarize_with_rag(body, store, k):
    hits = store.query(body, top_k=k)  # search with the raw body
    messages = build_messages(body, hits)
    raw = call_llm(messages)
    try:
        output, error = validate_summary(raw), None
    except ValueError as exc:
        output, error = None, str(exc)
    return {"k": k, "hits": hits, "messages": messages, "raw": raw, "output": output, "error": error}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("use: python rag_summary.py TICKET_ID")
    ticket_id = int(sys.argv[1])
    k = selected_k()
    result = summarize_with_rag(load_body(ticket_id), load_store(), k)
    out = HERE / f"rag_{ticket_id}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("k =", k)
    print("error:", result["error"])
    print("wrote", out.name)


if __name__ == "__main__":
    main()
```

## What each part of the code does

| Part | What it does |
| --- | --- |
| `OPTIONS` | The fixed generation settings, including `num_predict: 512`. |
| `SYSTEM_PROMPT` | The updated prompt, copied from `prompt - claude.md`. |
| `choose_k`, `selected_k` | The k rule applied to the Task 5 averages. |
| `load_body` | Returns the ticket `Body` from the canonical CSV with no edits. |
| `format_articles` | Writes each chunk as `[chunk_id] title` and its content. |
| `build_messages` | Keeps the ticket and the articles in two labeled blocks. |
| `validate_summary` | The Homework 4 shape check. |
| `summarize_with_rag` | Retrieve, build, call, validate, and return everything. |
