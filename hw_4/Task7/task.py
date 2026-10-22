import difflib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "hw_4" / "Task5"))

from llm_summary import load_tickets, quality_warnings, summarize_ticket

TASK6_PATH = ROOT / "hw_4" / "Task6" / "task6_results.json"
DECISIONS_PATH = HERE / "decisions.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def base_for(iteration):
    """Returns (base_prompt, base_outputs_by_ticket, label) for the iteration."""
    if iteration == 1:
        data, label = read_json(TASK6_PATH), "original prompt (Task 6)"
    else:
        decision = read_json(DECISIONS_PATH).get("1") if DECISIONS_PATH.exists() else None
        if not decision:
            raise SystemExit("Record the Iteration 1 decision first: python task.py decide 1 keep|revert")
        if decision == "keep":
            data, label = read_json(HERE / "iteration_1_outputs.json"), "Iteration 1 prompt (kept)"
        else:
            data, label = read_json(TASK6_PATH), "original prompt (Iteration 1 reverted)"
    return data["prompt"], {t["ticket_id"]: t for t in data["tickets"]}, label


def start(iteration):
    path = HERE / f"prompt_iteration_{iteration}.txt"
    if iteration not in (1, 2):
        raise SystemExit("Only two iterations.")
    if path.exists():
        raise SystemExit(f"{path.name} already exists.")
    base_prompt, _, label = base_for(iteration)
    path.write_text(base_prompt.strip() + "\n", encoding="utf-8")
    print(f"Created {path.name} from the {label}. Make exactly one change.")


def summarize_changes(base_stats, new_stats):
    return (
        f"schema failures: {base_stats[0]} -> {new_stats[0]}\n"
        f"quality warnings: {base_stats[1]} -> {new_stats[1]}"
    )


def format_output(record):
    if record["output"]:
        return json.dumps(record["output"], indent=2, ensure_ascii=False)
    return f"INVALID: {record['schema_error']}\n{record['raw_output']}"


def run_iteration(iteration):
    out_path = HERE / f"iteration_{iteration}_outputs.json"
    if out_path.exists():
        raise SystemExit(f"{out_path.name} exists. One clean run per iteration.")
    prompt_path = HERE / f"prompt_iteration_{iteration}.txt"
    if not prompt_path.exists():
        raise SystemExit(f"Run: python task.py start {iteration}")
    new_prompt = prompt_path.read_text(encoding="utf-8").strip()
    base_prompt, base, label = base_for(iteration)
    if new_prompt == base_prompt.strip():
        raise SystemExit("The prompt has not changed.")

    tickets = [(t["department"], t["ticket_id"]) for t in read_json(TASK6_PATH)["tickets"]]
    bodies = load_tickets([i for _, i in tickets])

    records = []
    for department, ticket_id in tickets:
        body = bodies[ticket_id]
        result = summarize_ticket(body, system_prompt=new_prompt)
        records.append(
            {
                "ticket_id": ticket_id,
                "department": department,
                "raw_output": result["raw"],
                "output": result["output"],
                "schema_error": result["error"],
                "warnings": quality_warnings(result["output"], body) if result["output"] else [],
            }
        )
        print(f"done {department} ({ticket_id})")

    out_path.write_text(
        json.dumps({"prompt": new_prompt, "base": label, "tickets": records}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    def stats(rows):
        return (
            sum(1 for r in rows if r["schema_error"]),
            sum(len(r["warnings"]) for r in rows),
        )

    diff = "\n".join(
        difflib.unified_diff(
            base_prompt.strip().splitlines(), new_prompt.splitlines(),
            fromfile="base prompt", tofile="new prompt", lineterm="",
        )
    )
    lines = [f"ITERATION {iteration}. BASE: {label}", "", "PROMPT DIFF", diff, "",
             "TOTALS (base -> new)", summarize_changes(stats([base[i] for _, i in tickets]), stats(records)), ""]
    for record, (department, ticket_id) in zip(records, tickets):
        lines += [
            "=" * 100,
            f"{department} | ticket {ticket_id}",
            "TICKET BODY:", str(bodies[ticket_id]), "",
            "BASE OUTPUT:", format_output(base[ticket_id]), f"warnings: {base[ticket_id]['warnings']}", "",
            "NEW OUTPUT:", format_output(record), f"warnings: {record['warnings']}", "",
        ]
    (HERE / f"iteration_{iteration}_comparison.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {out_path.name} and iteration_{iteration}_comparison.txt")


def decide(iteration, choice):
    if choice not in ("keep", "revert"):
        raise SystemExit("Choice must be keep or revert.")
    if not (HERE / f"iteration_{iteration}_outputs.json").exists():
        raise SystemExit("Run the iteration first.")
    decisions = json.loads(DECISIONS_PATH.read_text(encoding="utf-8")) if DECISIONS_PATH.exists() else {}
    if str(iteration) in decisions:
        raise SystemExit("Decision already recorded.")
    decisions[str(iteration)] = choice
    DECISIONS_PATH.write_text(json.dumps(decisions, indent=2), encoding="utf-8")
    print(f"Iteration {iteration}: {choice}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) >= 2 and args[0] == "start":
        start(int(args[1]))
    elif len(args) >= 2 and args[0] == "run":
        run_iteration(int(args[1]))
    elif len(args) == 3 and args[0] == "decide":
        decide(int(args[1]), args[2])
    else:
        print("Usage: python task.py start N | run N | decide N keep|revert")
