import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TASK6_FILE = HERE.parent / "Task6" / "task.py"

TICKETS = [
    (28763, "Supported request"),
    (29206, "Supported multi-source request"),
    (28921, "Unsupported request"),
]


def load_task6():
    # Task 6 holds the prompt, the call and the k rule. Task 7 only reuses them.
    spec = importlib.util.spec_from_file_location("task6", TASK6_FILE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    task6 = load_task6()
    llm = task6.load_module("llm_summary", task6.LLM_PATH)
    vector_module = task6.load_module("vector_store_helper", task6.HELPER)
    store = vector_module.VectorStore(task6.DB)
    k = task6.selected_k()

    ids = [ticket_id for ticket_id, _ in TICKETS]
    bodies = llm.load_tickets(ids)

    results = {}
    lines = [f"# Task 7 - RAG outputs (k = {k})", ""]

    for ticket_id, case in TICKETS:
        body = bodies[ticket_id]
        result = task6.summarize_with_rag(body, llm, store, k)
        results[str(ticket_id)] = {"case": case, "body": body, **result}

        lines += [f"## Ticket {ticket_id} - {case}", "", "### Retrieved chunks", ""]
        for hit in result["hits"]:
            lines.append(f"Rank {hit['rank']} - {hit['chunk_id']} (distance {hit['distance']:.4f})")
            lines.append(hit["content"])
            lines.append("")

        lines += ["### Generated summary", ""]
        if result["output"]:
            for field in ("summary", "customer_request", "missing_information"):
                lines.append(f"- {field}: {result['output'][field]}")
        else:
            lines.append(f"INVALID OUTPUT: {result['error']}")
            lines.append(result["raw"])
        lines.append("")
        print("done", ticket_id, "error:", result["error"])

    (HERE / "task7_results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (HERE / "task7_outputs.md").write_text("\n".join(lines), encoding="utf-8")
    print("wrote task7_results.json and task7_outputs.md")


if __name__ == "__main__":
    main()
