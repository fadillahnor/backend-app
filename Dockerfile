FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (dibutuhkan opencv-python-headless)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgl1 \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy seluruh source code
COPY . .

# Buat folder uploads agar tidak error saat runtime
RUN mkdir -p uploads/profile uploads/event uploads/payment uploads/scan_wajah

# Jalankan dengan Gunicorn, bind ke PORT (Railway) dengan fallback ke 5000
CMD gunicorn run:app --bind 0.0.0.0:${PORT:-5000} --workers 2 --timeout 120
