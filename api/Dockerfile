FROM python:3.10-slim

WORKDIR /app

# Sistem bağımlılıkları (Aynen korundu)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ca-certificates \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Gereksinimleri kopyala
COPY requirements.txt ./

# Bağımlılıkları yükle
ENV PIP_DEFAULT_TIMEOUT=180
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Kodları kopyala (Aynen korundu)
COPY api/ ./api/
COPY models/ ./models/
COPY data/ ./data/

RUN mkdir -p /app/data/.stock_cache && \
    mkdir -p /app/data/.yahoo_cache && \
    chmod -R 777 /app/data

# Ortam değişkenleri
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Render için EXPOSE (Bilgi amaçlı kalabilir)
EXPOSE 8000

# Healthcheck silindi (Render ile çakışmaması için).
# CMD değiştirildi: main.py koduna dokunmadan port sorununu burada çözüyoruz.
# Render $PORT verirse onu kullanır, vermezse 8000 kullanır.
CMD ["sh", "-c", "uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}"]