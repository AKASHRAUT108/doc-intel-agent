FROM python:3.11-slim

# System deps for pdf2image (Poppler) and EasyOCR's OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install CPU-only PyTorch first (avoids 2.5GB of CUDA downloads)
RUN pip install --no-cache-dir \
    torch==2.4.1 torchvision==0.19.1 \
    --index-url https://download.pytorch.org/whl/cpu

# Now install other deps
COPY requirements.txt .
COPY services/cv_service/requirements.txt services/cv_service/requirements.txt
RUN pip install --no-cache-dir -r services/cv_service/requirements.txt

# Copy code
COPY shared shared
COPY services/cv_service services/cv_service

ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

EXPOSE 8001

CMD ["uvicorn", "services.cv_service.app.main:app", "--host", "0.0.0.0", "--port", "8001"]