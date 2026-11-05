# Task 2 — Routing service

## Logic

`RoutingService` loads the Homework 4 candidate once and classifies the ticket body on every call. The candidate is the Homework 3 baseline with English stop words. Homework 4 kept it because its test macro-F1 was higher. The method returns the classifier's department and scores after `_check` confirms the Task 1 rules.

Save the program below as `routing_service.py` when you run it. This folder stays markdown until then.

## How the class is loaded

`_classifier_class` finds the repository from the saved script. `Path(__file__).resolve().parents[2]` is the repo root when the file lives at `hw_6/Task2/routing_service.py`. The function opens `shared/classes/ticket_routing_classifier.py` with `importlib` and returns `TicketRoutingClassifier`.

`RoutingService.__init__` receives `model_path`. It calls `TicketRoutingClassifier.load`, which runs `joblib.load` on that path, and stores the object on `self._classifier`. Every later `route_ticket` call uses that object. The pickle is read during construction.

## How the request is checked

`route_ticket` hands the incoming dictionary to `_body`. `_body` raises `ValueError("routing request must include body")` when the value is not a dictionary or when the key `body` is absent. It raises `ValueError("routing body must contain text")` when `body` is not a string or when `body.strip()` is empty. A passing string is returned with its original characters. `predict` lowercases its own copy. This function leaves the caller's string as it arrived.

## How the ticket is classified

`route_ticket` calls `self._classifier.predict(body)`. Inside the classifier, `predict` cleans a copy, turns that copy into counts with the saved vectorizer, and reads `predict_proba`. It returns a dictionary with `recommended_department` and `class_scores` for the ten departments. The `try` block catches any exception from that call and raises `RuntimeError("routing classifier failed")`. The word `from exc` keeps the original exception attached, so the traceback still shows the model error.

## How the answer is checked

`_check` reads `recommended_department` and `class_scores` with `.get`. It raises `RuntimeError` in four cases. The department is missing from the `DEPARTMENTS` tuple, or `class_scores` is not a dictionary. The score keys are not exactly those ten names. Any score is a boolean, is not an int or a float, or fails `math.isfinite`. The name with the largest score, from `max(scores, key=scores.get)`, differs from `recommended_department`.

A result that passes is a new dictionary with only those two keys. The workflow in Task 5 receives that dictionary from `route_ticket`.

## Program

```python
import importlib.util
import math
from pathlib import Path

DEPARTMENTS = (
    "Billing and Payments",
    "Customer Service",
    "General Inquiry",
    "Human Resources",
    "IT Support",
    "Product Support",
    "Returns and Exchanges",
    "Sales and Pre-Sales",
    "Service Outages and Maintenance",
    "Technical Support",
)


def _classifier_class():
    root = Path(__file__).resolve().parents[2]
    path = root / "shared" / "classes" / "ticket_routing_classifier.py"
    spec = importlib.util.spec_from_file_location("ticket_routing_classifier", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.TicketRoutingClassifier


def _body(request):
    if not isinstance(request, dict) or "body" not in request:
        raise ValueError("routing request must include body")
    body = request["body"]
    if not isinstance(body, str) or not body.strip():
        raise ValueError("routing body must contain text")
    return body


def _check(result):
    department = result.get("recommended_department")
    scores = result.get("class_scores")
    if department not in DEPARTMENTS or not isinstance(scores, dict):
        raise RuntimeError("routing response is missing required fields")
    if set(scores) != set(DEPARTMENTS):
        raise RuntimeError("routing scores must cover every department")
    if any(isinstance(score, bool) or not isinstance(score, (int, float)) or not math.isfinite(score) for score in scores.values()):
        raise RuntimeError("routing scores must be finite numbers")
    if max(scores, key=scores.get) != department:
        raise RuntimeError("recommended department is not the top score")
    return {"recommended_department": department, "class_scores": scores}


class RoutingService:
    def __init__(self, model_path):
        self._classifier = _classifier_class().load(model_path)

    def route_ticket(self, request):
        body = _body(request)
        try:
            result = self._classifier.predict(body)
        except Exception as exc:
            raise RuntimeError("routing classifier failed") from exc
        return _check(result)
```
