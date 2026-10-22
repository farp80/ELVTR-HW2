# Homework 4, Task 7 — Two Controlled Prompt Iterations (step by step, with code)

Goal: improve the prompt twice. Each time you change **one thing**, run the same
10 tickets, check for improvements **and** regressions, then **keep or revert**.

**How to use this file**

- Paste the Python block into `hw_4/Task7/task.py`. It imports the Task 5 code and
  reads the Task 6 results.
- Task 6 must be done first (`hw_4/Task6/task6_results.json` must exist).
- Commands:
  - `python task.py start 1` creates `prompt_iteration_1.txt` (a copy of the base prompt)
  - `python task.py run 1` runs the 10 tickets and writes the outputs and a comparison
  - `python task.py decide 1 keep` (or `revert`) records your decision
  - Then the same three commands with `2`.

## What "controlled" means

| Rule | Why |
| --- | --- |
| Change only the prompt. | If the code, schema, model or tickets change too, you cannot say what caused the result. |
| One change per iteration. | One change gives one cause. |
| Same 10 tickets, same settings (`temperature 0`, `seed 42`). | Differences then come from the prompt only. |
| Write the keep/revert rule **before** you run. | You cannot bend the rule after seeing the result. |
| One clean run per iteration. | Rerunning until it looks good is cheating. The code refuses to overwrite. |
| Iteration 2 starts from the accepted prompt. | Kept: use Iteration 1's prompt. Rejected: use the original. The code enforces this. |

---

## Step 1 — Choose the failure pattern for Iteration 1

**What:** open the "High-level issues" in `task6_report.md`. Pick **one** pattern
that a prompt can fix.

**Why:** a pattern fixed by the prompt is a real test. A pattern that comes from
the model being small is not.

**Prompt-addressable (good picks):** summary too long; summary copies the ticket;
`customer_request` repeats the summary; model adds advice; `missing_information`
lists things already in the body; invented details (add a "never invent" rule).

**Not prompt-addressable (do not pick):** the model misreads a very long ticket;
it forgets the end of a long text; it is a weak model in general. A sentence will
not fix those.

**Pick the pattern that affects the most tickets**, and write down the count.
That is your selection rationale.

## Step 2 — Write the plan and the rule (before running)

Start `hw_4/Task7/experiment_log.md` with this, filled in for Iteration 1:

```md
# Task 7 — Experiment Log

## Iteration 1
- Targeted failure pattern: ...
- Why this one: it affects N of 10 tickets in Task 6, and a prompt can address it.
- Exact prompt change: (one sentence added or changed, quoted)
- Keep rule (written before the run): keep only if the pattern gets better in at
  least 2 tickets AND no ticket gets worse (no new schema failure, no new
  unsupported fact, no important information lost). Otherwise revert.
```

## Step 3 — Create the prompt file and make the one change

```
python task.py start 1
```

This copies the base prompt into `prompt_iteration_1.txt`. Open it and make
**exactly one change**: add one sentence or reword one sentence. Do not change
anything else, and keep the three field names as they are (the schema needs them).

**Tips for a good change**

- Be direct and specific. "Write the summary in at most two sentences" works better
  than "be brief".
- Say what to do, not only what not to do.
- Do not stack several fixes in one edit.

## Step 4 — Run the 10 tickets

```
python task.py run 1
```

It writes:

- `iteration_1_outputs.json`: prompt and outputs for all 10 tickets (deliverable)
- `iteration_1_comparison.txt`: for every ticket the body, the base output and the
  new output, plus the prompt diff

The prompt diff proves **only the intended line changed**. If it shows more, you
changed too much. Delete `prompt_iteration_1.txt`, run `start` again, and redo it.
Delete only before the run. The run refuses to overwrite its own outputs.

## Step 5 — Review: improvements and regressions

Read `iteration_1_comparison.txt` ticket by ticket. Do not trust counts alone.

For each ticket decide:

- **Targeted pattern:** better, same, or worse?
- **Regression check** (this is where people skip work):
  - schema still valid?
  - every statement still in the body? (no new invented facts)
  - important information still there?
  - did another problem appear (longer, vaguer, odd missing-information list)?

Count them: "targeted pattern improved in X tickets, same in Y, worse in Z.
Regressions: ...". The comparison file also shows schema errors and warning counts
as a quick guide. They do **not** replace reading.

## Step 6 — Decide and record

Apply the rule from Step 2. Do not change it now.

```
python task.py decide 1 keep
```

or `revert`. Add to the log:

```md
- Result: improved in X tickets. Regressions: ... (ticket IDs).
- Decision: KEEP / REVERT. Reason: it meets / does not meet the rule because ...
```

## Step 7 — Iteration 2

Same steps with a **different** failure pattern. Pick one that remains after
Iteration 1, or one that Iteration 1 revealed.

- `start 2` copies the right base for you: the Iteration 1 prompt if you kept it,
  the original if you reverted. The code reads `decisions.json` for this.
- Write the Iteration 2 plan and rule in the log **before** `run 2`.
- Then review, `decide 2`, and log, exactly like Iteration 1.

Compare Iteration 2 against its own base (the accepted prompt), not the original.

## Step 8 — Finish the log

At the end of `experiment_log.md`, add:

```md
## Final prompt
Iteration 1: kept / reverted. Iteration 2: kept / reverted.
(paste the final accepted prompt)
```

---

## The code

```python
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
```

**Why this code is built this way**

- `base_for` enforces the rule "Iteration 2 starts from the accepted prompt".
- `run_iteration` refuses to overwrite and refuses an unchanged prompt.
- The prompt diff shows you changed one thing.
- The tickets come from the Task 6 file, so they are always the same 10.
- It passes the new prompt through the same `summarize_ticket` function, so the
  code, schema and settings stay identical.

---

## Deliverables map

| Deliverable | Where |
| --- | --- |
| Updated prompt, each iteration | `prompt_iteration_N.txt` and the `prompt` field in `iteration_N_outputs.json` |
| LLM outputs for all 10 tickets | `iteration_N_outputs.json` (readable version in `iteration_N_comparison.txt`) |
| Experiment log | `experiment_log.md`: pattern and rationale, exact change, improvements and regressions, keep/revert and reason |

## Checklist

- [ ] Each iteration targets one pattern that a prompt can fix.
- [ ] The keep rule was written before the run.
- [ ] Exactly one prompt change, confirmed by the diff.
- [ ] Code, schema, settings and tickets unchanged.
- [ ] All 10 tickets run once per iteration.
- [ ] Improvements and regressions checked by reading, not only counting.
- [ ] Decision recorded with `decide`, with a reason in the log.
- [ ] Iteration 2 started from the accepted prompt.
- [ ] Final accepted prompt written at the end of the log.
