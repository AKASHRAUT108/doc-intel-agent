FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY services/prompt_service/requirements.txt services/prompt_service/requirements.txt
RUN pip install --no-cache-dir -r services/prompt_service/requirements.txt

COPY shared shared
COPY services/prompt_service services/prompt_service

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8006

CMD ["uvicorn", "services.prompt_service.app.main:app", "--host", "0.0.0.0", "--port", "8006"]