import importlib.util
import math
from pathlib import Path

FIELDS = ("rank", "chunk_id", "distance", "content", "metadata")

class RetrievalService:
    def __init__(self, database_path, top_k=5):
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        self._store = self.__store_class()(database_path)
        self._top_k = top_k

    def __store_class(self):
        root = Path(__file__).resolve().parents[2]
        path = root / "hw_5" / "Fidel Alejandro Rosell Perez - VectorStore.py"
        spec = importlib.util.spec_from_file_location("vector_store", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.VectorStore

    def __body(self,request):
        if not isinstance(request, dict) or "body" not in request:
            raise ValueError("retrieval request must include body")
        body = request["body"]
        if not isinstance(body, str) or not body.strip():
            raise ValueError("retrieval body must contain text")
        return body

    def __check(self,hits):
        if not isinstance(hits, list):
            raise RuntimeError("retrieval did not return a list")
        for hit in hits:
            if not isinstance(hit, dict) or any(field not in hit for field in FIELDS):
                raise RuntimeError("retrieval row is missing a required field")
            if not isinstance(hit["distance"], (int, float)) or isinstance(hit["distance"], bool):
                raise RuntimeError("retrieval distance must be a number")
            if not math.isfinite(hit["distance"]):
                raise RuntimeError("retrieval distance must be finite")
        return hits

    def retrieve_evidence(self, request):
        body = self.__body(request) 
        try:
            hits = self._store.query(body, top_k=self._top_k)
        except Exception as exc:
            raise RuntimeError("retrieval query failed") from exc
        return {"evidence": self.__check(hits)}
