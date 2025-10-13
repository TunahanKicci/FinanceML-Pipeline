FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    ca-certificates \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/* \
    && update-ca-certificates

# Copy requirements
COPY requirements.txt ./

# Install Python packages
ENV PIP_DEFAULT_TIMEOUT=180
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY api/ ./api/
COPY models/ ./models/
COPY data/ ./data/

# Create cache directories
RUN mkdir -p /app/data/.stock_cache && \
    mkdir -p /app/data/.yahoo_cache && \
    chmod -R 777 /app/data

# Set Python path
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

CMD ["python", "-m", "api.main"]