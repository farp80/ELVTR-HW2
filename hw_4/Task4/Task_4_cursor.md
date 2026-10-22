# Homework 4, Task 4 — Set Up the Local LLM (step by step)

Goal: install Ollama, download the fixed course model, and prove you can call its
API from the command line and from Python. No separate deliverable. Keep short
notes as evidence of completion in `hw_4/Task4/setup_notes.md`.

**Fixed values. Never change them.**

| Item | Value |
| --- | --- |
| Model | `qwen2.5:1.5b-instruct-q4_K_M` |
| API | `http://localhost:11434` |
| Settings | `temperature: 0`, `seed: 42` |

**Why fixed:** Tasks 5–7 compare prompts. If the model or settings change between
runs, you cannot tell whether the prompt or the model caused a difference.

---

## Step 1 — Install and start Ollama (Windows)

```powershell
winget install --id Ollama.Ollama --exact
```

Open Ollama from the Start menu. It runs in the background. Close and reopen the
terminal if `ollama` is not found.

**Why:** the app hosts the model and exposes the local API.

## Step 2 — Check the runtime

```powershell
ollama --version
Invoke-RestMethod http://localhost:11434/api/version
```

**Pass:** both print a version. **Fail:** "connection refused" means Ollama is not
running. Start the app. Do not also run `ollama serve` if the app is already open.

## Step 3 — Download the model

```powershell
ollama pull qwen2.5:1.5b-instruct-q4_K_M
ollama list
```

**Pass:** `ollama list` shows exactly `qwen2.5:1.5b-instruct-q4_K_M` (about 986 MB).
**Fail:** "model not found" means the tag is wrong. Copy it exactly.

## Step 4 — Smoke test from PowerShell

```powershell
$request = @{
    model = "qwen2.5:1.5b-instruct-q4_K_M"
    messages = @(@{ role = "user"; content = "Reply with exactly READY." })
    stream = $false
    options = @{ temperature = 0; seed = 42 }
}
$response = Invoke-RestMethod -Method Post -Uri "http://localhost:11434/api/chat" `
    -ContentType "application/json" -Body ($request | ConvertTo-Json -Depth 10)
$response.message.content
```

**Pass:** the reply is non-empty (ideally `READY`). The first call can be slow
because the model is loading. Wait and retry once.

## Step 5 — Check the call from Python (including a JSON schema)

**Why:** Tasks 5–7 call the API from Python and force JSON output with a schema.
Test both now. `requests` is already in `requirements.txt`.

Paste into `hw_4/Task4/task.py` and run it:

```python
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
```

**Pass:** the plain call prints a non-empty reply, and `fields:` shows `['answer']`.

---

## Step 6 — Write the setup notes

Save a short `hw_4/Task4/setup_notes.md`:

```md
# Task 4 — Setup Notes
- Ollama version: ...
- `ollama list` shows qwen2.5:1.5b-instruct-q4_K_M
- PowerShell smoke test reply: ...
- Python plain call reply: ...
- Python schema call reply: ...
- Problems and how I fixed them (if any): ...
```

## Troubleshooting

| Problem | Fix |
| --- | --- |
| `ollama` not recognized | Close and reopen the terminal. Launch Ollama from the Start menu. |
| Connection refused on 11434 | Start the Ollama app. Do not start a second server. |
| Model not found | Re-run the `ollama pull` command. Check the tag with `ollama list`. |
| First request times out | Wait for the model to load. Retry. |
| Not enough disk space | Free several GB, or move the Ollama model folder. |

## Checklist

- [ ] `ollama --version` and the version API both work.
- [ ] `ollama list` shows the exact model tag.
- [ ] PowerShell smoke test returned a non-empty reply.
- [ ] Python plain call and schema call both worked.
- [ ] Temperature 0 and seed 42 used everywhere.
- [ ] Setup notes saved.
