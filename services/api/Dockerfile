FROM python:3.11-slim

WORKDIR /app

# CPU-only torch (needed transitively via httpx→numpy? actually not needed for API)
# API Gateway doesn't need torch — keep it light.

# Install Python deps
COPY requirements.txt .
COPY services/api/requirements.txt services/api/requirements.txt
RUN pip install --no-cache-dir -r services/api/requirements.txt

# Copy code
COPY shared shared
COPY services/api services/api

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8000

CMD ["uvicorn", "services.api.app.main:app", "--host", "0.0.0.0", "--port", "8000"]