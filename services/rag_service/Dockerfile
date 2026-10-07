FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir \
    torch==2.4.1 \
    --index-url https://download.pytorch.org/whl/cpu

COPY requirements.txt .
COPY services/rag_service/requirements.txt services/rag_service/requirements.txt
RUN pip install --no-cache-dir -r services/rag_service/requirements.txt

COPY shared shared
COPY services/rag_service services/rag_service
COPY data/samples data/samples

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8003

CMD ["uvicorn", "services.rag_service.app.main:app", "--host", "0.0.0.0", "--port", "8003"]