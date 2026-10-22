# Homework 4, Task 5 — Initial Prompt and LLM Call (step by step, with code)

Goal: a prompt plus a reusable function that sends one ticket `Body` to the local
model and returns a **validated** JSON summary. Prove it on one non-trivial ticket.

**How to use this file**

- Paste all the Python blocks, in order, into `hw_4/Task5/llm_summary.py`.
  Tasks 6 and 7 import from this file, so keep the name.
- Run it: `python hw_4/Task5/llm_summary.py`. The last block runs the test ticket.
- Ollama must be running (Task 4).

## The output contract

The model must return a JSON object with **exactly** these fields:

| Field | Type | Meaning |
| --- | --- | --- |
| `summary` | string | One or two short sentences about the reported issue |
| `customer_request` | string | What the customer wants |
| `missing_information` | list of strings | Details needed to act. Empty list if nothing is clearly missing |

Every field comes **only** from the ticket body. No outside facts, no guessed
solution, no routing.

## Inputs and outputs

| File | Role |
| --- | --- |
| `hw_2/... - support_tickets.csv` | The canonical dataset. Column `Body` (capital B). Never edit it. |
| `hw_3/... - split_manifest.csv` | Used only to pick a test ticket from the training split |
| `hw_4/Task5/llm_summary.py` | **Output:** the code deliverable |
| `hw_4/Task5/task5_result.json` | **Output:** test ticket ID, input and result |
| `hw_4/Task5/task5_notes.md` | **Output:** your notes (prompt, ticket ID, output) |

---

## Step 1 — Settings and the JSON schema

**What:** fix the model, options, and a JSON Schema for the contract.

**Why:** Ollama uses the schema in `format` to force the shape of the answer, so
you get valid JSON far more often. `additionalProperties: False` blocks extra
fields. These stay **unchanged** in Tasks 6 and 7. Only the prompt changes later.

```python
import json
import re
from pathlib import Path

import pandas as pd
import requests

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PREFIX = "Fidel Alejandro Rosell Perez - "
RAW_PATH = ROOT / "hw_2" / f"{PREFIX}support_tickets.csv"
SPLIT_PATH = ROOT / "hw_3" / f"{PREFIX}split_manifest.csv"

URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b-instruct-q4_K_M"
OPTIONS = {"temperature": 0, "seed": 42}

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
```

---

## Step 2 — Write the initial prompt

**What:** one system prompt with the task, the rules, and the fields.

**Why each part is there:**

- *Role and audience* ("for a human support agent"): sets the tone and purpose.
- *"Use only the ticket text. Do not add facts. Do not guess."*: the grounding rule
  from the contract.
- *"Do not suggest a solution. Do not say which department."*: the model must not
  route or resolve.
- *The three fields with their meaning*: the schema gives the shape, the prompt
  gives the meaning.
- *"Empty list if nothing is clearly missing"*: tells the model when `[]` is right.

Keep it plain. This is the **initial** prompt. Tasks 6 and 7 find its weaknesses.

```python
SYSTEM_PROMPT = """You write an internal summary of a customer support ticket for a human support agent.

Use only the information in the ticket text. Do not add facts. Do not guess. Do not suggest a solution. Do not say which department should handle the ticket.

Return a JSON object with exactly these fields:
- summary: one or two short sentences describing the reported issue.
- customer_request: what the customer wants done.
- missing_information: a list of details needed to understand or act on the request. Use an empty list if nothing is clearly missing."""
```

---

## Step 3 — The reusable function and the validation

**What:** `summarize_ticket(body, system_prompt)` builds the messages, calls the
model, and validates the answer. It returns the full messages, the raw text, the
parsed output, and an error message (or `None`).

**Why:**

- The ticket is in the **user** message. The instructions are in the **system**
  message. Later you swap only the system prompt.
- Validation does not trust the schema. It checks the exact fields and types
  itself.
- A schema failure is returned as `error`, not raised. Task 6 must report
  failures, not crash on them. Connection problems still raise.
- `system_prompt` is a parameter so Task 7 can pass new prompts with no code change.

```python
def build_messages(body, system_prompt=SYSTEM_PROMPT):
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Ticket body:\n{body}"},
    ]


def call_llm(messages):
    payload = {
        "model": MODEL,
        "messages": messages,
        "format": SCHEMA,
        "stream": False,
        "options": OPTIONS,
    }
    response = requests.post(URL, json=payload, timeout=600)
    response.raise_for_status()
    return response.json()["message"]["content"]


def validate_summary(raw_text):
    """Returns the parsed dict, or raises ValueError with the reason."""
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError(f"not valid JSON: {exc}")
    if not isinstance(data, dict):
        raise ValueError("output is not a JSON object")
    expected = {"summary", "customer_request", "missing_information"}
    if set(data) != expected:
        raise ValueError(f"fields must be exactly {sorted(expected)}, got {sorted(data)}")
    for key in ("summary", "customer_request"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"'{key}' must be a non-empty string")
    missing = data["missing_information"]
    if not isinstance(missing, list) or not all(isinstance(x, str) and x.strip() for x in missing):
        raise ValueError("'missing_information' must be a list of non-empty strings")
    return data


def summarize_ticket(body, system_prompt=SYSTEM_PROMPT):
    messages = build_messages(body, system_prompt)
    raw = call_llm(messages)
    try:
        output, error = validate_summary(raw), None
    except ValueError as exc:
        output, error = None, str(exc)
    return {"messages": messages, "raw": raw, "output": output, "error": error}
```

---

## Step 4 — Helpers for loading tickets and checking quality

**What:** `load_tickets` reads bodies straight from the canonical file.
`quality_warnings` flags a few easy problems.

**Why:**

- Bodies must not be altered, so nothing is cleaned or trimmed.
- The warnings are **hints for your review**, not the review. They catch three
  cheap problems: a summary longer than two sentences, a request that repeats the
  summary, and numbers in the output that are not in the body (a sign of invented
  facts). You still read every output yourself.

```python
def load_tickets(ticket_ids):
    raw = pd.read_csv(RAW_PATH).set_index("ticket_id")
    bodies = {}
    for ticket_id in ticket_ids:
        bodies[ticket_id] = raw.loc[ticket_id, "Body"]
    return bodies


def quality_warnings(output, body):
    warnings = []
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", output["summary"].strip()) if s]
    if len(sentences) > 2:
        warnings.append(f"summary has {len(sentences)} sentences (max 2)")
    if output["customer_request"].strip().lower() == output["summary"].strip().lower():
        warnings.append("customer_request repeats the summary")
    text = " ".join([output["summary"], output["customer_request"], *output["missing_information"]])
    for number in sorted(set(re.findall(r"\d+(?:[.,:/-]\d+)*", text))):
        if number not in body:
            warnings.append(f"number '{number}' is not in the ticket body")
    return warnings
```

---

## Step 5 — Pick a non-trivial test ticket

**What:** the first training-split ticket (lowest ID) whose `Body` is 800–1200
characters.

**Why:** a one-line ticket proves nothing. This length has several details and a
request, so there is something to summarize and something that could be missing.
Using the **training** split keeps the evaluation tickets untouched.

**Then read it.** Confirm it has a problem, some details, and a request. If it
does not, set `TEST_TICKET_ID` to another ticket you read and chose.

```python
TEST_TICKET_ID = None  # set an ID here to override the automatic pick


def pick_test_ticket():
    raw = pd.read_csv(RAW_PATH)
    split = pd.read_csv(SPLIT_PATH)
    train_ids = set(split.loc[split["split"] == "train", "ticket_id"])
    raw = raw[raw["ticket_id"].isin(train_ids) & raw["Body"].notna()].copy()
    raw["chars"] = raw["Body"].str.len()
    pool = raw[(raw["chars"] >= 800) & (raw["chars"] <= 1200)].sort_values("ticket_id")
    return int(pool.iloc[0]["ticket_id"])
```

---

## Step 6 — Run it on the one ticket

The `if __name__` guard means Tasks 6 and 7 can import this file without running
this block.

```python
if __name__ == "__main__":
    ticket_id = TEST_TICKET_ID or pick_test_ticket()
    body = load_tickets([ticket_id])[ticket_id]
    print(f"TICKET {ticket_id}\n{body}\n")

    result = summarize_ticket(body)
    print("RAW  :", result["raw"])
    print("ERROR:", result["error"])
    if result["output"]:
        print(json.dumps(result["output"], indent=2))
        print("warnings:", quality_warnings(result["output"], body))

    (HERE / "task5_result.json").write_text(
        json.dumps(
            {
                "ticket_id": ticket_id,
                "messages": result["messages"],
                "output": result["output"],
                "error": result["error"],
            },
            indent=2,
        ),
        encoding="utf-8",
    )
```

**Check:** `ERROR: None`, three fields, and the content matches the ticket. Read it
against the body. Every statement must be in the text.

---

## Step 7 — Write the notes

Save as `hw_4/Task5/task5_notes.md`:

```md
# Task 5 — Initial Prompt

## Initial prompt
(paste SYSTEM_PROMPT)

## Code
- hw_4/Task5/llm_summary.py: prompt, call function, validation.

## Test ticket
- Ticket ID: ...
- Why it is non-trivial: ...

## Generated output
(paste the JSON)
- Valid against the contract: yes. Supported by the body: yes/no, with a note.
```

## Checklist

- [ ] Prompt takes the ticket `Body` and asks for the three exact fields.
- [ ] One reusable function calls the model and validates the result.
- [ ] Validation checks exact fields, types, and the list of strings.
- [ ] Test ticket is non-trivial and the ID is recorded.
- [ ] Output is valid and grounded in the body only.
- [ ] Model, options and schema are the fixed ones from Task 4.
