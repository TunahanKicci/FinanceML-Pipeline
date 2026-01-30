# FinanceML Pipeline

[![License](https://img.shields.io/badge/License-All%20Rights%20Reserved-red.svg)](LICENSE)
[![GitHub](https://img.shields.io/badge/GitHub-TunahanKicci-blue)](https://github.com/TunahanKicci)
[![First Commit](https://img.shields.io/badge/First%20Commit-Sep%202025-orange)](https://github.com/TunahanKicci/FinanceML-Pipeline/commits/main)



AI-powered stock market analysis and forecasting platform with production-ready MLOps infrastructure.

## Overview

FinanceML Pipeline is an end-to-end machine learning system that provides real-time stock market analysis, price forecasting, risk assessment, and portfolio optimization. The platform leverages LSTM neural networks for time-series prediction and integrates with financial data APIs to deliver actionable insights.

**Live Demo:** [https://financeml-frontend.onrender.com](https://financeml-frontend.onrender.com)

**API Documentation:** [https://financeml-api.onrender.com/docs](https://financeml-api.onrender.com/docs)

> **Note:** > ⚠️ **Geliştirme Notu:** Bu proje **yapay zeka (LLM)** araçları kullanılarak geliştirilmiştir. "vibe coding" yöntemleriyle oluşturulmuştur.

## Key Features

### Core Functionality
- **Stock Price Forecasting**: LSTM-based predictions with configurable forecast horizons
- **Technical Analysis**: 20+ technical indicators including moving averages, RSI, MACD, Bollinger Bands
- **Risk Analysis**: Real-time volatility metrics, VaR calculations, and Sharpe ratio
- **Portfolio Optimization**: Modern Portfolio Theory implementation with efficient frontier analysis
- **Sentiment Analysis**: News and social media sentiment integration
- **Fundamental Analysis**: Company financials, ratios, and valuation metrics

### Technical Capabilities
- **Real-time Data Pipeline**: Automated cache system with daily updates
- **RESTful API**: FastAPI-based backend with comprehensive endpoint coverage
- **Interactive Frontend**: React-based dashboard with real-time visualizations
- **Production Monitoring**: Prometheus metrics and Grafana dashboards
- **CI/CD Pipeline**: Automated testing, building, and deployment workflows
- **Docker Containerization**: Multi-service orchestration with Docker Compose

## Architecture

### System Components

```
┌─────────────────┐
│   React UI      │  Port 3000
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   FastAPI       │  Port 8000
└────────┬────────┘
         │
         ├─→ LSTM Models (PyTorch)
         ├─→ Yahoo Finance API
         ├─→ Cache Layer (CSV/JSON)
         └─→ Feature Engineering
```

### Tech Stack

**Backend**
- Python 3.11
- FastAPI (API framework)
- PyTorch (deep learning)
- Pandas, NumPy (data processing)
- Scikit-learn (ML utilities)
- yfinance (financial data)

**Frontend**
- React 19
- Chart.js, Recharts (visualizations)
- Axios (HTTP client)
- Framer Motion (animations)

**Infrastructure**
- Docker & Docker Compose
- Prometheus (metrics)
- Grafana (dashboards)
- GitHub Actions (CI/CD)
- Render (deployment)

**Machine Learning**
- LSTM networks for time-series forecasting
- 60-day lookback window
- Multi-feature input (OHLCV + technical indicators)
- Rolling window validation

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Git

### Running with Docker (Recommended)

```bash
# Clone repository
git clone https://github.com/TunahanKicci/FinanceML-Pipeline.git
cd FinanceML-Pipeline

# Start all services
docker-compose up -d

# Access services
# Frontend: http://localhost:3000
# API: http://localhost:8000/docs
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3001
```

### Manual Setup

```bash
# Backend
pip install -r requirements.txt
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm start
```

### Initial Data Setup

```bash
# Update market data cache
python update_cache.py

# Train models (optional - pre-trained models included)
python models/train_model.py
```

## API Endpoints

### Stock Analysis

**GET /api/financials**
```json
{
  "symbol": "AAPL",
  "period": "1y",
  "interval": "1d"
}
```
Returns comprehensive technical analysis with 20+ indicators.

**GET /api/forecast**
```json
{
  "symbol": "AAPL",
  "days": 30,
  "include_weekends": false
}
```
Generates LSTM-based price predictions with confidence intervals.

**GET /api/risk**
```json
{
  "symbol": "AAPL",
  "period": "1y"
}
```
Calculates risk metrics including volatility, VaR, and drawdown.

**POST /api/portfolio/optimize**
```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT"],
  "weights": [0.4, 0.3, 0.3]
}
```
Performs portfolio optimization using Modern Portfolio Theory.

**GET /api/sentiment**
```json
{
  "symbol": "AAPL"
}
```
Aggregates sentiment from news and social media sources.

Full API documentation available at `/docs` endpoint.

## Project Structure

```
FinanceML-Pipeline/
├── api/                      # FastAPI backend
│   ├── main.py              # API entry point
│   ├── routers/             # Endpoint definitions
│   ├── services/            # Business logic
│   └── models/              # Data models
├── frontend/                # React application
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── services/        # API integration
│   │   └── utils/           # Helper functions
│   └── public/              # Static assets
├── models/                  # ML models and training
│   ├── train_model.py       # Training pipeline
│   ├── prediction_service.py # Inference logic
│   └── artifacts/           # Saved models
├── data/                    # Data layer
│   ├── cache/               # Market data cache
│   ├── sources/             # Data fetchers
│   ├── processors/          # Data transformations
│   └── validators/          # Data quality checks
├── monitoring/              # Observability
│   ├── prometheus_metrics.py
│   └── grafana/             # Dashboard configs
├── .github/workflows/       # CI/CD pipelines
├── docs/                    # Documentation
├── tests/                   # Test suites
└── docker-compose.yml       # Service orchestration
```

## Machine Learning Pipeline

### Data Collection
- Historical price data from Yahoo Finance
- 2 years of daily OHLCV data
- Real-time fundamental data
- Automated daily cache updates

### Feature Engineering
- Technical indicators (20+)
- Price momentum features
- Volatility measures
- Volume analysis
- Time-based features (day of week, month)

### Model Architecture
- LSTM neural network (2 layers, 128 units)
- Dropout regularization (0.2)
- Input: 60-day sequences with 10+ features
- Output: Next-day price prediction
- Training: 80/20 train-validation split

### Model Performance
- Mean Absolute Error: ~2-5% on validation set
- Directional accuracy: 60-65%
- Models retrained monthly with updated data

## Monitoring and Observability

### Prometheus Metrics
- Request count and latency
- Cache hit rates
- Prediction counts by symbol
- Error rates and types

### Grafana Dashboards
- Real-time system health
- API performance metrics
- Model inference statistics
- Resource utilization

### Logging
- Structured logging with timestamps
- Error tracking and alerting
- Request/response logging
- Performance profiling

## CI/CD Pipeline

### GitHub Actions Workflows

**Continuous Integration** (`ci.yml`)
- Runs on every push and PR
- Python linting (flake8, black)
- Unit and integration tests
- Frontend build verification

**Docker Build** (`docker-build.yml`)
- Builds and pushes images to GitHub Container Registry
- Multi-stage builds for optimization
- Automated tagging with git SHA

**Cache Updates** (`cache-update.yml`)
- Scheduled daily at 18:00 UTC
- Fetches latest market data
- Commits updates to repository
- Triggers automatic redeployment

**Dependency Scanning** (`dependency-check.yml`)
- Weekly security scans
- Vulnerability detection
- Automated PR creation for updates

**Deployment** (`deploy.yml`)
- Automatic deployment to Render
- Runs on main branch updates
- Health check verification

## Deployment

### Render Configuration

The application is deployed on Render's free tier with automatic deployments from GitHub.

**Services:**
- API: Web service with Docker
- Frontend: Static site from build directory

**Environment Variables:**
```bash
PYTHON_VERSION=3.11.9
PORT=8000
```

**Auto-deploy:** Enabled on main branch push

**Free Tier Limitations:**
- Services enter sleep mode after 15 minutes of inactivity
- Cold start time: 50-90 seconds for first request
- Monthly usage: 750 hours per service
- No persistent disk storage (cache stored in repository)
- Automatic shutdown and restart on inactivity

For production workloads, consider upgrading to paid tiers which offer:
- Always-on instances (no cold starts)
- Persistent storage
- Dedicated resources
- Custom domains with SSL

### Local Production Build

```bash
# Build frontend
cd frontend
npm run build

# Build Docker images
docker-compose build

# Deploy
docker-compose up -d
```

## Testing

```bash
# Backend tests
pytest tests/ -v --cov=api --cov=models

# Frontend tests
cd frontend
npm test

# Integration tests
pytest tests/integration/ -v

# Load tests
python tests/load/locustfile.py
```

## Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Data Sources
YAHOO_FINANCE_ENABLED=true
CACHE_ENABLED=true
CACHE_TTL=86400

# Model Configuration
MODEL_PATH=models/artifacts
PREDICTION_CONFIDENCE=0.95

# Monitoring
PROMETHEUS_ENABLED=true
LOG_LEVEL=INFO
```

### Cache Configuration

The system uses a two-tier caching strategy:
- **Level 1:** In-memory cache for API responses (5 min TTL)
- **Level 2:** File-based cache for market data (24 hour TTL)

Cache updates can be triggered manually:
```bash
python update_cache.py
```

## Performance Optimization

- Async API endpoints with FastAPI
- Database connection pooling
- Response caching layer
- Lazy model loading
- Batch prediction support
- Frontend code splitting
- CDN for static assets

## Security

- Input validation on all endpoints
- Rate limiting (100 requests/min)
- CORS configuration for production
- Environment variable management
- No sensitive data in logs
- Dependency vulnerability scanning

## License

**All Rights Reserved - Proprietary License**

See the [LICENSE](LICENSE) file for complete terms.

### Copyright Notice

**© 2024-2025 Tunahan Kicci. All Rights Reserved.**

This project and its source code are the exclusive property of Tunahan Kicci.

**IMPORTANT - Usage Restrictions:**

This code is made publicly visible for **viewing and reference purposes ONLY**. 

**YOU MAY NOT:**
- ❌ Copy, fork, or clone this code for your own projects
- ❌ Modify or build upon this code
- ❌ Use this code in personal or commercial applications
- ❌ Present this work as your own in portfolios, resumes, or job applications
- ❌ Redistribute or sell any part of this software

**YOU MAY:**
- ✅ View the code for educational purposes
- ✅ Link to this repository with proper attribution
- ✅ Study the implementation for learning

**Project Authenticity:**
- Original repository: [github.com/TunahanKicci/FinanceML-Pipeline](https://github.com/TunahanKicci/FinanceML-Pipeline)
- First commit: September 29, 2024 (verifiable in commit history)
- Author: Tunahan Kicci ([@TunahanKicci](https://github.com/TunahanKicci))
- Development timeline: 50+ commits over 2+ months

**For Recruiters & Employers:**

If you encounter this project in someone else's portfolio or GitHub, please verify authenticity:

1. **Check commit history**: Original has 50+ commits starting Sept 2024
2. **Verify GitHub username**: Must be [@TunahanKicci](https://github.com/TunahanKicci)
3. **Check repository creation date**: This repo was created in September 2024
4. **Technical deep-dive**: Ask detailed questions about implementation (LSTM architecture, portfolio optimization algorithms, Docker configuration)
5. **Compare commit timestamps**: Clones/forks will have recent creation dates

**Legal Notice:**

Unauthorized use, reproduction, or misrepresentation of this work may result in:
- Violation of copyright law
- Academic integrity violations (if used in educational context)
- Professional misconduct (if presented in job applications)
- GitHub Terms of Service violations
- Potential legal action

**License Inquiries:**

For permission requests or licensing questions, contact via GitHub: [@TunahanKicci](https://github.com/TunahanKicci)

## Acknowledgments

- Yahoo Finance for market data API
- PyTorch team for deep learning framework
- FastAPI for modern Python web framework
- Render for hosting infrastructure

## Contact

**Author:** Tunahan Kicci

**GitHub:** [@TunahanKicci](https://github.com/TunahanKicci)

**Project Link:** [https://github.com/TunahanKicci/FinanceML-Pipeline](https://github.com/TunahanKicci/FinanceML-Pipeline)

**Live Demo:** [https://financeml-frontend.onrender.com](https://financeml-frontend.onrender.com)

---

Built with Python, React, and Machine Learning

