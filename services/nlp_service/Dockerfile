FROM python:3.11-slim

WORKDIR /app

# CPU-only torch first
RUN pip install --no-cache-dir \
    torch==2.4.1 \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
COPY services/nlp_service/requirements.txt services/nlp_service/requirements.txt
RUN pip install --no-cache-dir -r services/nlp_service/requirements.txt

COPY shared shared
COPY services/nlp_service services/nlp_service

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8002

CMD ["uvicorn", "services.nlp_service.app.main:app", "--host", "0.0.0.0", "--port", "8002"]