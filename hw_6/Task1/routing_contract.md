# Task 1 — Routing service contract

`RoutingService.route_ticket(request)` in `Task2/routing_service.py`.

## Request

`route_ticket` takes one dictionary. It reads one field, `body`. That value is the ticket `Body` as a string, and `strip()` must still leave a character.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `body` | string | Yes | The unaltered ticket `Body`. At least one non-whitespace character. |

## Response

The method returns one dictionary. The department is one of the ten Homework 4 names. `class_scores` has exactly those ten names, each score is a finite number, and the name with the highest score is the department. Task 2 checks this in `__check` before the dictionary leaves the service.

| Field | Type | Always present | Rules |
| --- | --- | --- | --- |
| `recommended_department` | string | Yes | One of the ten allowed departments. Equal to the highest-scoring name in `class_scores`. |
| `class_scores` | object | Yes | Exactly the ten allowed departments as keys. Each value is a finite number, not a Boolean. |

## Errors

- A request that is not a dictionary, or a `body` that is missing or blank, raises `ValueError`. The classifier is not called.
- If the saved model fails, or the prediction breaks a response rule above, the method raises `RuntimeError`.
- The service never returns a default department.
