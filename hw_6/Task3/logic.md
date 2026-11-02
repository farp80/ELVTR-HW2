# Task 3 — Retrieval service

## Logic

`RetrievalService` opens the Homework 5 LanceDB folder once, stores k = 5, and searches that folder for the ticket body. Homework 5 chose 5 because mean recall rose by more than 0.10 from k = 3 and mean precision stayed above 0.50. The method returns those rows as `evidence` after `_check` confirms the Task 1 fields.

Save the program below as `retrieval_service.py` when you run it.

## How the store is opened

`_store_class` loads `hw_5/Fidel Alejandro Rosell Perez - VectorStore.py` from the repository root. `parents[2]` is that root when this file is saved at `hw_6/Task3/retrieval_service.py`. The function returns the `VectorStore` class.

`RetrievalService.__init__` takes `database_path` and `top_k`. The default of `top_k` is 5. The constructor raises `ValueError` unless `top_k` is an `int` greater than 0. It also rejects `True` and `False`, because a boolean is a subclass of `int` and the code tests `isinstance(top_k, bool)` before the integer test. The constructor then calls `VectorStore(database_path)`, which opens the existing database, and stores the count on `self._top_k`. The index is already in `hw_5/Task4/lancedb`. This constructor opens it.

## How the request is checked

`retrieve_evidence` calls `_body` first. The request must be a dictionary that contains `body`. The value must be a string, and `strip()` must leave a character. A failed check raises `ValueError` with either "retrieval request must include body" or "retrieval body must contain text". `query` runs only after `_body` returns. The returned string is the original body.

## How the search runs

The method calls `self._store.query(body, top_k=self._top_k)`. `query` embeds that body, opens the table, and searches with cosine distance, limited to the stored k. It returns a list. Each item has `rank` starting at 1, `chunk_id`, `distance`, `content`, and `metadata`. `metadata` is the JSON object the store parsed from the saved row. If `query` raises, the `except` block raises `RuntimeError("retrieval query failed")` and attaches the original error with `from exc`.

## How each row is checked

`_check` requires `hits` to be a list. For every item it requires a dictionary that contains `rank`, `chunk_id`, `distance`, `content`, and `metadata`. `distance` must be an int or a float, it must fail the boolean test, and `math.isfinite` must accept it. A bad list or a bad row raises `RuntimeError`. A good list is returned inside `{"evidence": hits}`. When `query` returns `[]`, that empty list is the `evidence` value.

## Program

```python
import importlib.util
import math
from pathlib import Path

FIELDS = ("rank", "chunk_id", "distance", "content", "metadata")


def _store_class():
    root = Path(__file__).resolve().parents[2]
    path = root / "hw_5" / "Fidel Alejandro Rosell Perez - VectorStore.py"
    spec = importlib.util.spec_from_file_location("vector_store", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.VectorStore


def _body(request):
    if not isinstance(request, dict) or "body" not in request:
        raise ValueError("retrieval request must include body")
    body = request["body"]
    if not isinstance(body, str) or not body.strip():
        raise ValueError("retrieval body must contain text")
    return body


def _check(hits):
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


class RetrievalService:
    def __init__(self, database_path, top_k=5):
        if not isinstance(top_k, int) or isinstance(top_k, bool) or top_k <= 0:
            raise ValueError("top_k must be a positive integer")
        self._store = _store_class()(database_path)
        self._top_k = top_k

    def retrieve_evidence(self, request):
        body = _body(request)
        try:
            hits = self._store.query(body, top_k=self._top_k)
        except Exception as exc:
            raise RuntimeError("retrieval query failed") from exc
        return {"evidence": _check(hits)}
```
