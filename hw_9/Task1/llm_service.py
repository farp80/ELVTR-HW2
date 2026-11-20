import requests


def _request(request):
    if not isinstance(request, dict):
        raise ValueError("LLM request must be a dictionary")  # noqa: TRY004
    messages = request.get("messages")
    model = request.get("model")
    options = request.get("options")
    if not isinstance(messages, list) or not messages:
        raise ValueError("LLM messages must be a non-empty list")
    for message in messages:
        if not isinstance(message, dict):
            raise ValueError("each LLM message must be an object")  # noqa: TRY004
        if not isinstance(message.get("role"), str) or not isinstance(message.get("content"), str):
            raise ValueError("each LLM message needs a role and content")  # noqa: TRY004
    if not isinstance(model, str) or not model.strip():
        raise ValueError("LLM model must be a non-empty string")
    if not isinstance(options, dict):
        raise ValueError("LLM options must be an object")  # noqa: TRY004
    schema = request.get("schema")
    if schema is not None and not isinstance(schema, dict):
        raise ValueError("LLM schema must be an object or omitted")
    return messages, model, options, schema


class LLMClient:
    def __init__(self, url):
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
