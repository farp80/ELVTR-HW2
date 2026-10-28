# Task 6 program

Put the blocks below, in order, into `rag_summary.py` in this folder. Run it after Task 5 has written `metrics.json`: `python rag_summary.py 28763`.

## Logic — pick the smallest k that still finds the articles

`k` is how many chunks go into the prompt. It starts at 1. It moves to 3 when mean recall at 3 is at least 0.10 above recall at 1 and mean precision at 3 stays at or above 0.5. It moves to 5 only when recall at 5 clears the same bar over recall at 3. A smaller rise counts as close, so the smaller k stays. Homework 4 showed this 1.5B model drops asks as the instruction gets longer, so extra chunks have to earn the extra length. The averages come from `metrics.json`.

```python
import importlib.util
import json
import sys
from pathlib import Path

import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HW5 = HERE.parent
DB = HW5 / "Task4" / "lancedb"
HELPER = HW5 / "vector_setup" / "Fidel Alejandro Rosell Perez - VectorStore.py"
METRICS = HW5 / "Task5" / "metrics.json"
LLM_PATH = ROOT / "hw_4" / "Task5" / "llm_summary.py"


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def choose_k(mean_precision, mean_recall):
    chosen = 1
    for k, smaller in ((3, 1), (5, 3)):
        gain = mean_recall[k] - mean_recall[smaller]
        if gain >= 0.10 and mean_precision[k] >= 0.5:
            chosen = k
    return chosen


def selected_k():
    report = json.loads(METRICS.read_text(encoding="utf-8"))
    precision = {int(k): value for k, value in report["mean_precision"].items()}
    recall = {int(k): value for k, value in report["mean_recall"].items()}
    return choose_k(precision, recall)
```

## Logic — one prompt, two labeled sources

The accepted Homework 4 prompt is `prompt_iteration_1.txt`. The summary task and the three JSON fields stay as written. One sentence changes. The old sentence said to use only the ticket text. The new sentence names two sources. The ticket body is what the customer wrote. The support articles are outside context. An article is used only when it applies to this ticket. When no article applies, the summary comes from the body alone. Article facts stay article facts.

Search uses the unaltered Body, so the search question and the ticket being summarized are the same text. The user message puts the chunks under the heading `Support articles` and the ticket under the heading `Ticket body`. The model can tell the customer's words from the retrieved text.

The call keeps the Homework 4 model, JSON shape, temperature 0, seed 42, and `stream` false. `num_predict` is 512, which is the Homework 5 limit for ticket summaries. The Homework 4 checker still requires the three fields.

```python
ACCEPTED_RULE = (
    "Use only the information in the ticket text. Do not add facts. Do not guess. "
    "Do not suggest a solution. Do not say which department should handle the ticket."
)
RAG_RULE = (
    "The ticket body is what the customer wrote. The support articles are outside context. "
    "Use an article only when it applies to this ticket. When no article applies, summarize "
    "the body on its own. Article facts stay article facts. Do not add facts from outside "
    "the ticket body and the support articles. Do not guess. Do not suggest a solution. "
    "Do not say which department should handle the ticket."
)


def system_prompt():
    accepted = (ROOT / "hw_4" / "Task7" / "prompt_iteration_1.txt").read_text(encoding="utf-8").strip()
    if ACCEPTED_RULE not in accepted:
        raise SystemExit("the accepted prompt no longer contains the ticket-text rule")
    return accepted.replace(ACCEPTED_RULE, RAG_RULE)


def article_block(hits):
    parts = []
    for hit in hits:
        title = hit["metadata"]["title"]
        parts.append(f"[{hit['chunk_id']}] {title}\n{hit['content']}")
    return "\n\n".join(parts)


def user_message(body, hits):
    return f"Support articles:\n{article_block(hits)}\n\nTicket body:\n{body}"


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
    return {"k": k, "hits": hits, "messages": messages, "raw": raw, "output": output, "error": error}


def main():
    if len(sys.argv) != 2:
        raise SystemExit("use: python rag_summary.py TICKET_ID")
    ticket_id = int(sys.argv[1])
    llm = load_module("llm_summary", LLM_PATH)
    store = load_module("vector_store_helper", HELPER).VectorStore(DB)
    k = selected_k()
    body = llm.load_tickets([ticket_id])[ticket_id]
    result = summarize_with_rag(body, llm, store, k)
    out = HERE / f"rag_{ticket_id}.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("k =", k)
    print("error:", result["error"])
    print("wrote", out.name)


if __name__ == "__main__":
    main()
```
