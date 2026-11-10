import math

import requests

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


def _post(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=60)
    except requests.RequestException as exc:
        raise RuntimeError("routing request failed") from exc
    if response.status_code == 400:
        raise ValueError("routing request was rejected")
    if response.status_code >= 400:
        raise RuntimeError("routing request failed")
    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError("routing response was not JSON") from exc
    return result


def _check(result):
    if not isinstance(result, dict):
        raise RuntimeError("routing response is missing required fields")
    department = result.get("recommended_department")
    scores = result.get("class_scores")
    if department not in DEPARTMENTS or not isinstance(scores, dict):
        raise RuntimeError("routing response is missing required fields")
    if set(scores) != set(DEPARTMENTS):
        raise RuntimeError("routing scores must cover every department")
    if any(
        isinstance(score, bool)
        or not isinstance(score, (int, float))
        or not math.isfinite(score)
        for score in scores.values()
    ):
        raise RuntimeError("routing scores must be finite numbers")
    if max(scores, key=scores.get) != department:
        raise RuntimeError("recommended department is not the top score")
    return {"recommended_department": department, "class_scores": scores}


class RoutingClient:
    def __init__(self, base_url):
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("router URL must be a non-empty string")
        self._url = base_url.rstrip("/") + "/route"

    def route_ticket(self, request):
        if not isinstance(request, dict) or not isinstance(request.get("body"), str):
            raise ValueError("routing request must include body")
        if not request["body"].strip():
            raise ValueError("routing body must contain text")
        return _check(_post(self._url, {"body": request["body"]}))
