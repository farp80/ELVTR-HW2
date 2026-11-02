# Task 4 — LLM service

## Logic

`LLMClient` stores the Ollama chat URL and posts one request per call. The workflow supplies the messages, the model name, the generation settings, and the summary schema on that call. The method returns the reply text as `content`.

Save the program below as `llm_service.py` when you run it.

## What the object stores

`LLMClient.__init__` takes `url`. The default is `http://localhost:11434/api/chat`. A value that is not a string, or a string whose `strip()` is empty, raises `ValueError("Ollama URL must be a non-empty string")`. A good URL is stored on `self._url`. Ollama is the program listening at that address. This class keeps the address and posts to it.

## How the request is checked

`call_llm` passes its dictionary to `_request`. `_request` raises `ValueError` when the value is not a dictionary, when `messages` is missing or empty or is not a list, when any message is not a dictionary, or when `role` or `content` is not a string. It raises when `model` is missing, is not a string, or is blank after `strip()`. It raises when `options` is not a dictionary. `schema` may be absent. `dict.get` then returns `None`, and that `None` is allowed. A present `schema` must be a dictionary. `_request` returns the four values `messages`, `model`, `options`, and `schema`. `requests.post` runs only after this return.

## How the HTTP call is built

`call_llm` puts `model`, `messages`, `stream` set to `False`, and `options` into `payload`. `stream` set to `False` tells Ollama to send the full reply in one response. When `schema` is a dictionary, the code adds it as `payload["format"]`. Ollama uses `format` as the JSON shape of the reply. The method posts `payload` to `self._url` with `timeout=600`, so the call waits up to 600 seconds. `raise_for_status()` raises when the HTTP status is an error. The next line reads `response.json()["message"]["content"]`, which is the text Ollama placed on the assistant message.

Any exception in that `try` block becomes `RuntimeError("LLM call failed")`. The original exception stays attached through `from exc`.

## What comes back

After the `try` block, `content` must be a string whose `strip()` still has a character. Any other value raises `RuntimeError("LLM returned no content")`. A good string is returned as `{"content": content}`. The string stays text here. Task 5 passes it to `json.loads` inside `_summary`.

## Program

```python
import requests


def _request(request):
    if not isinstance(request, dict):
        raise ValueError("LLM request must be a dictionary")
    messages = request.get("messages")
    model = request.get("model")
    options = request.get("options")
    if not isinstance(messages, list) or not messages:
        raise ValueError("LLM messages must be a non-empty list")
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("each LLM message must be an object")
        if not isinstance(message.get("role"), str) or not isinstance(message.get("content"), str):
            raise ValueError("each LLM message needs a role and content")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("LLM model must be a non-empty string")
    if not isinstance(options, dict):
        raise ValueError("LLM options must be an object")
    schema = request.get("schema")
    if schema is not None and not isinstance(schema, dict):
        raise ValueError("LLM schema must be an object or omitted")
    return messages, model, options, schema


class LLMClient:
    def __init__(self, url="http://localhost:11434/api/chat"):
        if not isinstance(url, str) or not url.strip():
            raise ValueError("Ollama URL must be a non-empty string")
        self._url = url

    def call_llm(self, request):
        messages, model, options, schema = _request(request)
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options,
        }
        if schema is not None:
            payload["format"] = schema
        try:
            response = requests.post(self._url, json=payload, timeout=600)
            response.raise_for_status()
            content = response.json()["message"]["content"]
        except Exception as exc:
            raise RuntimeError("LLM call failed") from exc
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("LLM returned no content")
        return {"content": content}
```
