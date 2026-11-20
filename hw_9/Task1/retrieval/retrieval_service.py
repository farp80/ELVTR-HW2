import math

from vector_store import VectorStore

FIELDS = ("rank", "chunk_id", "distance", "content", "metadata")


def _body(request):
    if not isinstance(request, dict) or "body" not in request:
        raise ValueError("retrieval request must include body")
    body = request["body"]
    if not isinstance(body, str) or not body.strip():
        raise ValueError("retrieval body must contain text")
    return body


def _check(hits):
    if not isinstance(hits, list):
        raise RuntimeError("retrieval did not return a list")  # noqa: TRY004
    for hit in hits:
        if not isinstance(hit, dict) or any(field not in hit for field in FIELDS):
            raise RuntimeError("retrieval row is missing a required field")
        distance = hit["distance"]
        if isinstance(distance, bool) or not isinstance(distance, (int, float)):
            raise RuntimeError("retrieval distance must be a number")  # noqa: TRY004
        if not math.isfinite(distance):
            raise RuntimeError("retrieval distance must be finite")
    return hits


class RetrievalService:
    def __init__(self, database_path, top_k=5):
        if isinstance(top_k, bool) or not isinstance(top_k, int) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        self._store = VectorStore(database_path)
        self._top_k = top_k

    def retrieve_evidence(self, request):
        body = _body(request)
        try:
            hits = self._store.query(body, top_k=self._top_k)
        except Exception as exc:
            raise RuntimeError("retrieval query failed") from exc
        return {"evidence": _check(hits)}
