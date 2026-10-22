# Homework 4, Task 6 — Apply the Initial Prompt (step by step, with code)

Goal: run the Task 5 prompt on 10 fixed tickets, then review every output
yourself. The review exposes the weak spots you fix in Task 7.

**How to use this file**

- Paste all the Python blocks, in order, into `hw_4/Task6/task.py`.
- It imports the Task 5 code from `hw_4/Task5/llm_summary.py`. Do not copy or edit
  that code here.
- Two runs:
  1. First run calls the model on the 10 tickets and saves `task6_results.json`.
  2. You read the outputs and fill in the review fields in that JSON.
  3. Second run checks the JSON is complete and writes `task6_report.md`.

## The 10 tickets

The longest `Body` in each department (ties: lowest `ticket_id`).

| Department | `ticket_id` |
| --- | ---: |
| Billing and Payments | 28907 |
| Customer Service | 28399 |
| General Inquiry | 28381 |
| Human Resources | 28921 |
| IT Support | 28736 |
| Product Support | 28763 |
| Returns and Exchanges | 28563 |
| Sales and Pre-Sales | 28571 |
| Service Outages and Maintenance | 28642 |
| Technical Support | 29206 |

Use them exactly as they are in `support_tickets.csv`. Do not trim, clean or
shorten any `Body`.

**Note:** two of them (28381 and 28921) are in the Homework 3 test split. This is
fine. The assignment lists them, and here the model only summarizes text. Nothing
is routed. Do not use them to judge or change the classifier.

## Rules

| Rule | Why |
| --- | --- |
| Do not change the prompt, schema, settings or code. | Task 6 measures the **initial** prompt. Task 7 changes it. |
| Do not edit ticket bodies. | The task says "without alteration". |
| Judge outputs by reading the ticket, not by trusting the model. | A fluent summary can still be wrong. |

---

## Step 1 — Load the code and verify the 10 tickets

**What:** import the Task 5 function and check that the list really is the longest
body per department.

**Why:** a typo in an ID would silently review the wrong ticket. The script prints
`True` when the list is right. If it prints `False`, fix the list.

```python
import json
import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "hw_4" / "Task5"))

from llm_summary import RAW_PATH, SYSTEM_PROMPT, load_tickets, quality_warnings, summarize_ticket

TICKETS = [
    ("Billing and Payments", 28907),
    ("Customer Service", 28399),
    ("General Inquiry", 28381),
    ("Human Resources", 28921),
    ("IT Support", 28736),
    ("Product Support", 28763),
    ("Returns and Exchanges", 28563),
    ("Sales and Pre-Sales", 28571),
    ("Service Outages and Maintenance", 28642),
    ("Technical Support", 29206),
]
RESULTS_PATH = HERE / "task6_results.json"
REPORT_PATH = HERE / "task6_report.md"

raw = pd.read_csv(RAW_PATH)
raw["chars"] = raw["Body"].fillna("").str.len()
longest = raw.sort_values(["chars", "ticket_id"], ascending=[False, True]).groupby("Department").head(1)
print("ticket list matches the longest bodies:", set(longest["ticket_id"]) == {i for _, i in TICKETS})
```

---

## Step 2 — Run the prompt on all 10

**What:** call `summarize_ticket` for each ticket and save everything: the full
input messages, the raw output, the parsed output, the schema error, the quality
warnings, and three blank review fields.

**Why:** the report needs the **full input** and the **output returned**. Saving
them now means the model is not called again when you write the report.

```python
def run_llm():
    bodies = load_tickets([i for _, i in TICKETS])
    records = []
    for department, ticket_id in TICKETS:
        body = bodies[ticket_id]
        result = summarize_ticket(body)
        record = {
            "ticket_id": ticket_id,
            "department": department,
            "input_messages": result["messages"],
            "raw_output": result["raw"],
            "output": result["output"],
            "schema_error": result["error"],
            "warnings": quality_warnings(result["output"], body) if result["output"] else [],
            # ---- you fill these three in ----
            "factually_supported": "",
            "important_information_included": "",
            "missing_information_opinion": "",
        }
        records.append(record)
        print(department, ticket_id, len(body), "characters")
        print(body)
        print("OUTPUT:", record["raw_output"])
        print("SCHEMA ERROR:", record["schema_error"])
        print("WARNINGS:", record["warnings"])
        print()

    data = {"prompt": SYSTEM_PROMPT, "tickets": records, "high_level_issues": ""}
    RESULTS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved {RESULTS_PATH}. Review it, fill in the blank fields, then run again.")
```

---

## Step 3 — Review each output (this is the real work)

Open `task6_results.json`. For each ticket, read the body and the output together.
Then fill the three blank fields. Be specific. Quote the words you mean.

| Field | Question to answer | How to judge |
| --- | --- | --- |
| *(automatic)* `schema_error` | Did the output follow the JSON schema? | `null` means the exact fields and types were right. Also check the summary is one or two sentences. `warnings` helps. |
| `factually_supported` | Is every statement in the body? | Take each claim in `summary`, `customer_request` and `missing_information`. Find it in the body. Write "Yes" or list what is not supported. A number in `warnings` that is not in the body is a strong sign of an invented fact. |
| `important_information_included` | Does it keep the most important points? | Write the body's 2–3 key points first (the problem, what is affected, what was tried, what the customer wants). Check each one is in the output. |
| `missing_information_opinion` | Do you agree with the missing information? Why? | For each listed item, is it really absent from the body? Is something clearly missing that is not listed? Is an empty list right? |

**Short examples of good answers**

- `factually_supported`: "No. The summary says the payment failed twice. The body says once."
- `important_information_included`: "Mostly. It has the problem and the request. It leaves out that the customer already reinstalled the app."
- `missing_information_opinion`: "Disagree. It lists the order number as missing, but the body gives it."

**Then fill `high_level_issues`** (once, for all 10): look across the outputs for
patterns and write how many tickets each affects. Common patterns:

- the summary copies sentences from the ticket instead of condensing them
- the summary is longer than two sentences
- `customer_request` repeats the summary
- invented details or numbers
- `missing_information` lists things already in the body, or is empty when it
  should not be
- the output covers the start of a long ticket but ignores the end
- the model adds advice or a solution

Write each pattern as a plain sentence with a count ("4 of 10 summaries are
longer than two sentences"). These are your candidates for Task 7.

---

## Step 4 — Check the JSON and write the report

**What:** the second run refuses to continue until every review field is filled,
then writes `task6_report.md`.

**Why:** it stops you from submitting a half-reviewed report.

```python
FENCE = "`" * 3  # markdown code fence, built here so it does not break this guide
REVIEW_FIELDS = ("factually_supported", "important_information_included", "missing_information_opinion")


def problems(data):
    found = []
    for t in data["tickets"]:
        for key in REVIEW_FIELDS:
            if not t[key].strip():
                found.append(f"ticket {t['ticket_id']}: '{key}' is empty")
    if not data["high_level_issues"].strip():
        found.append("'high_level_issues' is empty")
    return found


def render(data):
    lines = ["# Task 6 — Initial Prompt Applied to 10 Tickets", ""]
    for t in data["tickets"]:
        system, user = t["input_messages"][0]["content"], t["input_messages"][1]["content"]
        shown = json.dumps(t["output"], indent=2, ensure_ascii=False) if t["output"] else t["raw_output"]
        lines += [
            f"## {t['department']} (ticket {t['ticket_id']})",
            "",
            "### Full input sent to the LLM",
            FENCE + "text",
            f"[system]\n{system}\n\n[user]\n{user}",
            FENCE,
            "",
            "### Output returned by the LLM",
            FENCE + "json",
            shown,
            FENCE,
            "",
            f"- Followed the JSON schema: {'Yes' if t['schema_error'] is None else 'No. ' + t['schema_error']}",
            f"- Factually supported by the body: {t['factually_supported'].strip()}",
            f"- Most important information included: {t['important_information_included'].strip()}",
            f"- Missing information (agree or not, and why): {t['missing_information_opinion'].strip()}",
            "",
        ]
    lines += ["## High-level issues", "", data["high_level_issues"].strip(), ""]
    return "\n".join(lines)


if __name__ == "__main__":
    if not RESULTS_PATH.exists():
        run_llm()
    else:
        data = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        found = problems(data)
        if found:
            print(f"{RESULTS_PATH.name} is not complete ({len(found)} items missing):")
            for item in found[:20]:
                print(" -", item)
        else:
            REPORT_PATH.write_text(render(data), encoding="utf-8")
            print(f"Report written to {REPORT_PATH}")
```

To rerun the model from scratch, delete `task6_results.json` yourself. Do this only
if the code or setup was broken. Never to get a "better" answer.

---

## Deliverables map

| Deliverable | Where |
| --- | --- |
| Full input for each ticket | `task6_report.md`, "Full input sent to the LLM" |
| Output for each ticket | `task6_report.md`, "Output returned by the LLM" |
| Schema / factual / key info / missing info answers | The four bullets per ticket |
| High-level issues | Last section |

## Checklist

- [ ] All 10 tickets used, unaltered, and the ID list check printed `True`.
- [ ] The prompt, schema and settings are exactly Task 5's.
- [ ] Every ticket has the four answers, written after reading the body.
- [ ] High-level issues name patterns with counts.
- [ ] `task6_results.json` is kept. Task 7 uses it as the starting point.
