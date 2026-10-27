FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
COPY services/ui/requirements.txt services/ui/requirements.txt
RUN pip install --no-cache-dir -r services/ui/requirements.txt

COPY shared shared
COPY services/ui services/ui

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "services/ui/app/main.py", "--server.address=0.0.0.0", "--server.port=8501", "--server.headless=true"]