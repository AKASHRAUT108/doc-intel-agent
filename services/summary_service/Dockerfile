FROM python:3.11-slim

WORKDIR /app

# No torch needed — Gemini SDK is lightweight
COPY requirements.txt .
COPY services/summary_service/requirements.txt services/summary_service/requirements.txt
RUN pip install --no-cache-dir -r services/summary_service/requirements.txt

COPY shared shared
COPY services/summary_service services/summary_service

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8005

CMD ["uvicorn", "services.summary_service.app.main:app", "--host", "0.0.0.0", "--port", "8005"]