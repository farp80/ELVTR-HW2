# Task 3 — LLM container commands

Run these from any folder. No image is built for this task.

## Create the volume, start, and download the model

```text
docker volume create homework7_ollama
docker run -d --name homework7-ollama -p 8003:11434 -v homework7_ollama:/root/.ollama ollama/ollama:0.34.1
docker exec homework7-ollama ollama pull qwen2.5:1.5b-instruct-q4_K_M
```

Host port `8003` maps to container port `11434`. The model is saved in the `homework7_ollama` volume.

## Check (PowerShell)

```text
Invoke-RestMethod http://localhost:8003/api/version
Invoke-RestMethod http://localhost:8003/api/tags
```

`/api/tags` lists `qwen2.5:1.5b-instruct-q4_K_M`.

## Stop

```text
docker stop homework7-ollama
docker rm homework7-ollama
```

This removes the container only. The `homework7_ollama` volume and the model stay for Task 5.
