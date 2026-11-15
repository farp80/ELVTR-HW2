FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV HF_HOME=/app/models
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='qdrant/bge-small-en-v1.5-onnx-q', revision='52398278842ec682c6f32300af41344b1c0b0bb2', allow_patterns=['config.json','model_optimized.onnx','special_tokens_map.json','tokenizer.json','tokenizer_config.json'])"
ENV HF_HUB_OFFLINE=1
COPY retrieval_api.py retrieval_service.py vector_store.py ./
COPY data ./data
EXPOSE 8000
CMD ["uvicorn", "retrieval_api:app", "--host", "0.0.0.0", "--port", "8000"]
