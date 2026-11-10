# Task 3 — LLM container

## Steps

Follow `WEEK_7_ASSIGNMENT.md` Task 3, `Fidel Alejandro Rosell Perez - ollama_container_config.md`, `hw_6/Task4/llm_service.py`, and `hw_6/Task1/llm_contract.md`. Those Homework 6 files already call `POST /api/chat` on port `11434`. Use that server.

1. Use image `ollama/ollama:0.34.1` and model `qwen2.5:1.5b-instruct-q4_K_M` from `ollama_container_config.md`. Add no Dockerfile and no Python file. `WEEK_7_ASSIGNMENT.md` assigns the image Ollama already ships.
2. Run `docker volume create homework7_ollama`.
3. Run `docker run -d --name homework7-ollama -p 8003:11434 -v homework7_ollama:/root/.ollama ollama/ollama:0.34.1`. The config mounts the volume on `/root/.ollama`. Host `8003` maps to container `11434`.
4. Run `docker exec homework7-ollama ollama pull qwen2.5:1.5b-instruct-q4_K_M`. The pull writes the model into the volume.
5. Open the two URLs in the config: `http://localhost:8003/api/version` and `http://localhost:8003/api/tags`. The tag list must include the model name.
6. Run `docker stop homework7-ollama` and `docker rm homework7-ollama`. Leave the volume. Task 5 mounts `homework7_ollama` again.

## Commands

Create the volume, start the pinned image, and download the model into the volume.

```text
docker volume create homework7_ollama
docker run -d --name homework7-ollama -p 8003:11434 -v homework7_ollama:/root/.ollama ollama/ollama:0.34.1
docker exec homework7-ollama ollama pull qwen2.5:1.5b-instruct-q4_K_M
```

## How to tell it worked

`http://localhost:8003/api/version` returns a version object when the API is up. `http://localhost:8003/api/tags` lists local models. The list includes `qwen2.5:1.5b-instruct-q4_K_M` after the pull. No Python test is required for those two checks.

## Stop

```text
docker stop homework7-ollama
docker rm homework7-ollama
```

Those two commands remove the container. They do not remove `homework7_ollama` or the model stored in it. Leave the volume in place for Task 5.
