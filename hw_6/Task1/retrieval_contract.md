# Task 1 — Retrieval service contract

`RetrievalService.retrieve_evidence(request)` in `Task3/retrieval_service.py`.

## Request

`retrieve_evidence` takes one dictionary. The required field is `body`, a string. After `strip()`, at least one character must remain. That string is the same ticket `Body` that routing receives. `top_k` is not a request field. The service stores k = 5 from Homework 5 when it starts.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `body` | string | Yes | The unaltered ticket `Body`. At least one non-whitespace character. |

## Response

The method returns one dictionary with the field `evidence`. The value is the ordered list from `VectorStore.query`. A query that returns no rows returns an empty list. That list is the search result.

| Field | Type | Always present | Rules |
| --- | --- | --- | --- |
| `evidence` | array of objects | Yes | Ordered as `VectorStore.query` returns them. At most 5 records. |
| `evidence[].rank` | integer | Yes | Position in the result, starting at 1. |
| `evidence[].chunk_id` | string | Yes | ID of the knowledge-base chunk. |
| `evidence[].distance` | number | Yes | Finite, not a Boolean. Lower is closer. |
| `evidence[].content` | string | Yes | Text of the chunk. |
| `evidence[].metadata` | object | Yes | `article_id`, `title`, `chunk_position`. |

## Errors

- A request that is not a dictionary, or a `body` that is missing or blank, raises `ValueError`. The store is not queried.
- If the store cannot be read, the query throws, or a row is missing a required field, the method raises `RuntimeError`.
- An error never becomes an empty `evidence` list.
