# Task 2 — Put the margin rule in the workflow

## Reasoning

The margin rule from Task 1 runs after routing has returned `class_scores` and the ticket has reached `summary_ready_for_review`. `review_decision` rounds the top score minus the second score to 4 decimals and returns true when that gap is below 0.05. That boolean is stored in `requires_routing_review`. `human_reviewed_route` is `None` because a person has not chosen a department yet. A rejected ticket and a failed ticket skip the scores and store `False`. Those tickets have no route for a person to confirm. Routing, retrieval, and the summary stay as they are in Homework 7. The rule does not change `recommended_department` or `class_scores`.

## Where the files go

Work in `hw_8\Task2`. Leave `hw_7\Task4` unchanged, because it is the Homework 7 submission. Copy everything from `hw_7\Task4` into `hw_8\Task2`: `workflow.py`, `workflow_api.py`, `routing_client.py`, `retrieval_client.py`, `llm_service.py`, `Dockerfile`, `requirements.txt`, `.dockerignore`, and the `shared` folder. Then add `routing_review.py` and edit `workflow.py` as shown below. Task 3 starts from a copy of this folder.

Add `routing_review.py` to the `COPY` line in the Dockerfile. Without it, the container cannot import the rule.

```dockerfile
COPY workflow_api.py workflow.py routing_client.py retrieval_client.py llm_service.py routing_review.py ./
```

## Logic

Save this as `routing_review.py` next to `workflow.py`.

```python
def review_decision(class_scores):
    ordered = sorted(class_scores.values(), reverse=True)
    margin = round(ordered[0] - ordered[1], 4)
    return margin < 0.05, margin
```

In the Homework 7 `workflow.py`, import the function and add the two fields in `_package`. Pass the flag only on the success return. The other branches keep the default `False`.

```python
from routing_review import review_decision


def _package(
    ticket_id,
    record_id,
    trace_id,
    status,
    error,
    route=None,
    body=None,
    summary=None,
    evidence=None,
    requires_routing_review=False,
):
    ready = status == "summary_ready_for_review"
    route = route or {}
    return {
        "ticket_id": ticket_id,
        "workflow_record_id": record_id,
        "terminal_status": status,
        "recommended_department": route.get("recommended_department") if ready else None,
        "class_scores": route.get("class_scores") if ready else None,
        "ticket_body": body if ready else None,
        "ticket_summary": summary if ready else None,
        "retrieved_evidence": evidence if ready else [],
        "trace_id": trace_id,
        "error": None if ready else error,
        "requires_routing_review": requires_routing_review if ready else False,
        "human_reviewed_route": None,
    }
```

After `_run` returns, set the flag, keep the completed trace, and pass the flag into `_package`.

```python
        route, summary, evidence = self._run(body, trace_id)
        needs, _margin = review_decision(route["class_scores"])
        elapsed_ms = int((perf_counter() - started) * 1000)
        self._record(
            trace_id,
            service="workflow",
            event="completed",
            terminal_status="summary_ready_for_review",
            elapsed_ms=elapsed_ms,
        )
        return _package(
            ticket_id,
            record_id,
            trace_id,
            "summary_ready_for_review",
            None,
            route=route,
            body=body,
            summary=summary,
            evidence=evidence,
            requires_routing_review=needs,
        )
```
