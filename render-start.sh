#!/bin/bash
# Render.com deployment script

echo "🚀 Starting FinanceML API deployment..."

# Install dependencies
echo "📦 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /opt/render/project/src/data/cache
mkdir -p /opt/render/project/src/data/cache/fundamentals
mkdir -p /opt/render/project/src/models/artifacts

# Download cache data if needed (optional)
# echo "📊 Updating market data cache..."
# python update_cache.py

# Start the API
echo "✅ Starting FastAPI server..."
exec uvicorn api.main:app --host 0.0.0.0 --port $PORT
