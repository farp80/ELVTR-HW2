# Retrieval service contract

## Request

`retrieve_evidence` takes one dictionary. The required field is `body`, a string. After `strip()`, at least one character must remain. That string is the same ticket `Body` that routing receives.

`top_k` is not a request field. The service stores k = 5 from Homework 5 when it starts.

## Response

The method returns one dictionary with the field `evidence`. The value is the ordered list from `VectorStore.query`. Each record has `rank`, `chunk_id`, `distance`, `content`, and `metadata`.

A query that returns no rows returns an empty list. That list is the search result.

## Errors

A request that is not a dictionary, or a `body` that is missing or blank, raises `ValueError`. The store is not queried.

If the store cannot be read, the query throws, or a row is missing a required field, the method raises `RuntimeError`.
