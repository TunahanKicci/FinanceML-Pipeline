FROM python:3.10-slim

WORKDIR /app

# System dependencies (SSL ve certificate paketlerini ekle)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    dnsutils \
    ca-certificates \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Copy requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy API code
COPY api/ ./api/
COPY models/ ./models/
COPY data/ ./data/

# Set Python path
ENV PYTHONPATH=/app

# SSL doğrulamasını geçici olarak devre dışı bırak (sadece test için)
ENV PYTHONHTTPSVERIFY=0

EXPOSE 8000

CMD ["python", "-m", "api.main"]