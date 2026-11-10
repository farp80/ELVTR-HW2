import math

import requests

FIELDS = ("rank", "chunk_id", "distance", "content", "metadata")


def _post(url, payload):
    try:
        response = requests.post(url, json=payload, timeout=120)
    except requests.RequestException as exc:
        raise RuntimeError("retrieval request failed") from exc
    if response.status_code == 400:
        raise ValueError("retrieval request was rejected")
    if response.status_code >= 400:
        raise RuntimeError("retrieval request failed")
    try:
        result = response.json()
    except ValueError as exc:
        raise RuntimeError("retrieval response was not JSON") from exc
    return result


def _check(result):
    if not isinstance(result, dict) or not isinstance(result.get("evidence"), list):
        raise RuntimeError("retrieval did not return a list")
    hits = result["evidence"]
    for hit in hits:
        if not isinstance(hit, dict) or any(field not in hit for field in FIELDS):
            raise RuntimeError("retrieval row is missing a required field")
        distance = hit["distance"]
        if isinstance(distance, bool) or not isinstance(distance, (int, float)):
            raise RuntimeError("retrieval distance must be a number")
        if not math.isfinite(distance):
            raise RuntimeError("retrieval distance must be finite")
    return hits


class RetrievalClient:
    def __init__(self, base_url):
        if not isinstance(base_url, str) or not base_url.strip():
            raise ValueError("retrieval URL must be a non-empty string")
        self._url = base_url.rstrip("/") + "/search"

    def retrieve_evidence(self, request):
        if not isinstance(request, dict) or not isinstance(request.get("body"), str):
            raise ValueError("retrieval request must include body")
        if not request["body"].strip():
            raise ValueError("retrieval body must contain text")
        return {"evidence": _check(_post(self._url, {"body": request["body"]}))}
