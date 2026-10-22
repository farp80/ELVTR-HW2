import json

import requests

URL = "http://localhost:11434/api/chat"
MODEL = "qwen2.5:1.5b-instruct-q4_K_M"
OPTIONS = {"temperature": 0, "seed": 42}


def chat(messages, schema=None):
    payload = {"model": MODEL, "messages": messages, "stream": False, "options": OPTIONS}
    if schema is not None:
        payload["format"] = schema
    response = requests.post(URL, json=payload, timeout=600)
    response.raise_for_status()
    return response.json()["message"]["content"]


# 1. Plain call
reply = chat([{"role": "user", "content": "Reply with exactly READY."}])
print("plain call :", repr(reply))

# 2. Structured call (JSON schema in `format`)
schema = {
    "type": "object",
    "properties": {"answer": {"type": "string"}},
    "required": ["answer"],
    "additionalProperties": False,
}
structured = chat(
    [{"role": "user", "content": "Return a JSON object with the field answer set to ok."}],
    schema,
)
print("schema call:", structured)
data = json.loads(structured)
print("fields:", list(data))
