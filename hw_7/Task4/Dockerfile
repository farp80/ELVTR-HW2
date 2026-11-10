FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
ENV LOG_PATH=/logs/workflow_trace.jsonl
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY workflow_api.py workflow.py routing_client.py retrieval_client.py llm_service.py ./
COPY shared ./shared
EXPOSE 8000
CMD ["uvicorn", "workflow_api:app", "--host", "0.0.0.0", "--port", "8000"]
