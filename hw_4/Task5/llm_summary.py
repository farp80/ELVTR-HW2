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



SYSTEM_PROMPT = """You write an internal summary of a customer support ticket for a human support agent.

Use only the information in the ticket text. Do not add facts. Do not guess. Do not suggest a solution. Do not say which department should handle the ticket.

Return a JSON object with exactly these fields:
- summary: one or two short sentences describing the reported issue.
- customer_request: what the customer wants done.
- missing_information: a list of details needed to understand or act on the request. Use an empty list if nothing is clearly missing."""



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



TEST_TICKET_ID = None  # set an ID here to override the automatic pick


def pick_test_ticket():
    raw = pd.read_csv(RAW_PATH)
    split = pd.read_csv(SPLIT_PATH)
    train_ids = set(split.loc[split["split"] == "train", "ticket_id"])
    raw = raw[raw["ticket_id"].isin(train_ids) & raw["Body"].notna()].copy()
    raw["chars"] = raw["Body"].str.len()
    pool = raw[(raw["chars"] >= 800) & (raw["chars"] <= 1200)].sort_values("ticket_id")
    return int(pool.iloc[0]["ticket_id"])



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
