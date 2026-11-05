# Task 1 — LLM service contract

`LLMClient.call_llm(request)` in `Task4/llm_service.py`.

## Request

`call_llm` takes one dictionary. The service stores the Ollama URL. The caller sends the prompt, the model, the settings, and the schema on every call.

| Field | Type | Required | Rules |
| --- | --- | --- | --- |
| `messages` | array of objects | Yes | At least one message. |
| `messages[].role` | string | Yes | For example `system` or `user`. |
| `messages[].content` | string | Yes | The text of that message. |
| `model` | string | Yes | Non-empty Ollama model name for this call. |
| `options` | object | Yes | Generation settings for this call, such as `temperature`, `seed`, and `num_predict`. |
| `schema` | object | No | Describes the output shape. When it is omitted, the call has no fixed shape. |

## Response

The method returns one dictionary with the field `content`. The value is the raw text from Ollama. Parsing that text is the caller's job.

| Field | Type | Always present | Rules |
| --- | --- | --- | --- |
| `content` | string | Yes | Non-empty raw reply text from Ollama. |

## Errors

- A request that breaks a rule above raises `ValueError`. Ollama is not called.
- If Ollama cannot be reached, the HTTP call fails, or the reply has no text, the method raises `RuntimeError`.
- The service never returns a default reply.
