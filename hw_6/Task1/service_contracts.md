# Task 1 — Service contracts

## Routing service contract

### Request:
- `route_ticket` reads one field, `body`. That value is the ticket `Body` as a string, and `strip()` must still leave a character. 

### Response:
- The method returns `recommended_department` and `class_scores`. The department is one of the ten Homework 4 names. `class_scores` has exactly those ten names, each score is a finite number, and the name with the highest score is the department. 
- Task 2 checks this in `_check` before the dictionary leaves the service.

### Errors:
- A request that is not a dictionary, or a `body` that is missing or blank, raises `ValueError`. The classifier is not called.
- If the saved model fails, or the prediction breaks a response rule above, the method raises `RuntimeError`.

## Retrieval service contract

### Request:
- `retrieve_evidence` takes one dictionary. The required field is `body`, a string. After `strip()`, at least one character must remain. That string is the same ticket `Body` that routing receives.
- `top_k` is not a request field. The service stores k = 5 from Homework 5 when it starts.

### Response:
- The method returns one dictionary with the field `evidence`. The value is the ordered list from `VectorStore.query`. Each record has `rank`, `chunk_id`, `distance`, `content`, and `metadata`.
- A query that returns no rows returns an empty list. That list is the search result.

### Errors
- A request that is not a dictionary, or a `body` that is missing or blank, raises `ValueError`. The store is not queried.
- If the store cannot be read, the query throws, or a row is missing a required field, the method raises `RuntimeError`.

## LLM service contract

### Request:
- `call_llm` takes one dictionary.
- `messages` is a list with at least one object. Each object has a string `role` and a string `content`.
- `model` is a non-empty string. It is the Ollama model name for this call.
- `options` is an object. It holds the generation settings for this call, such as temperature, seed, and `num_predict`.
- `schema` is optional. When the caller sends it, it is an object that describes the output shape. When the caller omits it, this call has no fixed shape.
- The service stores the Ollama URL. The caller sends the prompt, the model, the settings, and the schema on every call.

### Response:
- The method returns one dictionary with the field `content`. The value is the raw text from Ollama. Parsing that text is the caller's job.

### Errors:
- A request that breaks a rule above raises `ValueError`. Ollama is not called.
- If Ollama cannot be reached, the HTTP call fails, or the reply has no text, the method raises `RuntimeError`
