# Task 1 — Service contracts

## Logic

Each service takes one dictionary and returns one dictionary. A bad request raises `ValueError` before the real work starts. A broken model, store, or Ollama call raises `RuntimeError`. The caller in Task 5 catches that error and returns `workflow_failed`.

## Routing

`route_ticket` reads one field, `body`. That value is the ticket `Body` as a string, and `strip()` must still leave a character. The method returns `recommended_department` and `class_scores`. The department is one of the ten Homework 4 names. `class_scores` has exactly those ten names, each score is a finite number, and the name with the highest score is the department. Task 2 checks this in `_check` before the dictionary leaves the service.

## Retrieval

`retrieve_evidence` reads the same `body`. The number of rows is not in the request. `RetrievalService.__init__` stores `top_k`, and the default is 5. The method returns `evidence`, a list in the order `VectorStore.query` produced. Each item has `rank`, `chunk_id`, `distance`, `content`, and `metadata`. An empty list is the answer when the search itself returned no rows. Task 3 checks every row in `_check`.

## LLM

`call_llm` reads `messages`, `model`, `options`, and an optional `schema`. `messages` is a non-empty list of objects with string `role` and string `content`. `model` is a non-empty string. `options` is a dictionary of generation settings. `schema` is a dictionary when the caller wants a fixed JSON shape, and it is left out otherwise. The method returns `content`, the raw text from Ollama. Task 4 copies that text into the response. Task 5 parses it later in `_summary`.
