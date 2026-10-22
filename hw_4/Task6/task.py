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
