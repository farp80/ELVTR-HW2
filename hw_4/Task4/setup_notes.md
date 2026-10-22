# Task 4 - Setup Notes

## Runtime
- Ollama version: 0.40.7 (`ollama --version`).
- The API answers at `http://localhost:11434/api/version`.
- Installed with `winget install --id Ollama.Ollama --exact` on Windows.

## Model
- `ollama pull qwen2.5:1.5b-instruct-q4_K_M` finished.
- `ollama list` shows `qwen2.5:1.5b-instruct-q4_K_M`, 986 MB.

## Smoke tests
- PowerShell call to `/api/chat`, with `temperature 0` and `seed 42`: the reply was `READY`.
- Python plain call (`hw_4/Task4/task.py`): the reply was `READY`.
- Python schema call with `format`: the reply was `{"answer": "ok"}`. The shape matches the schema.

## Problems
- The first `winget` run printed only a spinner for several minutes on a phone hotspot. It finished after waiting.
