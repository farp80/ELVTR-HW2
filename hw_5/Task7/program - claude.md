# Task 7 - Run the RAG Summaries on Three Tickets - claude

Save the code block below as `run_task7.py` in this folder. Run it with `python run_task7.py` after Tasks 4, 5, and 6 are done. It writes:

- `task7_results.json`: everything, for your records.
- `task7_outputs.md`: for each ticket, the retrieved chunks and the generated summary, ready to read and grade.

I could not run it on my machine (the vector store and the local model are not available there), so no generated summaries are in this folder yet.

## Logic (read this before the code)

1. **Fixed tickets.** 28763 (supported request), 29206 (supported, many sources), 28921 (unsupported request).
2. **Reuse Task 6.** Import `rag_summary.py` from the Task 6 folder. Same prompt, same model, same settings, same `k`. Nothing is redefined here, so Task 7 cannot drift from Task 6.
3. **Per ticket:** read the unaltered `Body`, search with it, build the prompt, call the model.
4. **Write the results** twice: as JSON for records, and as Markdown with the retrieved chunks (rank, chunk ID, text) above the generated summary, so you can grade by reading one page.
5. **Grade by hand** after the run. Use the frozen rubric in `../Task2/rubric_frozen.md`. The grading sheet is in `report - claude.md`.

## Why these three tickets

| Ticket | Case | What it tests |
| --- | --- | --- |
| 28763 | Supported request | The knowledge base has articles on Samsung QN90A flicker and warranty. Does the model stay true to the ticket while articles are present? |
| 29206 | Supported, many sources | The request touches Jira priorities, workflow statuses, and transitions. Several chunks from several articles compete for space. |
| 28921 | Unsupported request | The customer wants an HR system redesign. No article covers it. The model must ignore weak matches and not copy their facts. |

## Code

```python
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAG_FILE = HERE.parent / "Task6" / "rag_summary.py"
TICKETS = [(28763, "Supported request"), (29206, "Supported multi-source request"), (28921, "Unsupported request")]


def load_rag_module():
    spec = importlib.util.spec_from_file_location("rag_summary", RAG_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    rag = load_rag_module()
    store = rag.load_store()
    k = rag.selected_k()
    results = {}
    lines = [f"# Task 7 - RAG outputs (k = {k})", ""]
    for ticket_id, case in TICKETS:
        body = rag.load_body(ticket_id)
        result = rag.summarize_with_rag(body, store, k)
        results[str(ticket_id)] = {"case": case, **result}
        lines += [f"## Ticket {ticket_id} - {case}", "", "### Retrieved chunks", ""]
        for hit in result["hits"]:
            lines += [f"**Rank {hit['rank']} - {hit['chunk_id']}** (distance {hit['distance']:.4f})", "",
                      "> " + hit["content"].replace("\n", "\n> "), ""]
        lines += ["### Generated summary", ""]
        if result["output"]:
            lines += ["~~~json", json.dumps(result["output"], indent=2, ensure_ascii=False), "~~~", ""]
        else:
            lines += [f"INVALID OUTPUT: {result['error']}", "", "~~~text", result["raw"], "~~~", ""]
        print("done", ticket_id)
    (HERE / "task7_results.json").write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    (HERE / "task7_outputs.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote task7_results.json and task7_outputs.md")


if __name__ == "__main__":
    main()
```

## What each part of the code does

| Part | What it does |
| --- | --- |
| `load_rag_module` | Imports the Task 6 file by path. |
| `rag.selected_k()` | Reuses the k chosen from the Task 5 metrics. |
| `rag.summarize_with_rag` | The exact Task 6 interaction. |
| the `for` loop | Runs the three tickets and writes retrieved chunks and the summary in readable form. |
| invalid output branch | Shows the raw text if the JSON was broken, so a failure is visible and gets a 0 under the rubric gate. |
