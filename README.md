# FinanceML Pipeline

AI-powered stock market analysis and forecasting platform with production-ready MLOps infrastructure.

## Overview

FinanceML Pipeline is an end-to-end machine learning system that provides real-time stock market analysis, price forecasting, risk assessment, and portfolio optimization. The platform leverages LSTM neural networks for time-series prediction and integrates with financial data APIs to deliver actionable insights.

**Live Demo:** [https://financeml-frontend.onrender.com](https://financeml-frontend.onrender.com)

**API Documentation:** [https://financeml-api.onrender.com/docs](https://financeml-api.onrender.com/docs)

> **Note:** The application is hosted on Render's free tier. The first request after 15 minutes of inactivity may take 50-90 seconds to respond as the service spins up from sleep mode. Subsequent requests will be fast. This is a known limitation of free-tier hosting and does not reflect the application's actual performance capabilities.

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

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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

