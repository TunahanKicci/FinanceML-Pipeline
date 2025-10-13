# api/main.py
"""
FastAPI Main Application
"""
from models.forecasting_service import ForecastingService
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import logging
import sys
import os
from fastapi.responses import JSONResponse
import yfinance as yf
import math
import numpy as np
import time

# Path setup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.prediction_service import PredictionService
from fastapi import HTTPException
from data.processors.fundamental_processor import FundamentalProcessor
from data.sources.yahoo_finance import YahooFinanceClient
from fastapi import APIRouter
from data.sources.sentiment_analyzer import SentimentAnalyzer
from data.processors.risk_analyzer import RiskAnalyzer
from api.database.simple_db import db
from data.processors.portfolio_optimizer import PortfolioOptimizer
from datetime import datetime

# Import Prometheus metrics
try:
    from monitoring.prometheus_metrics import (
        REQUEST_COUNT,
        REQUEST_LATENCY,
        PREDICTION_COUNT,
        CACHE_HITS,
        CACHE_MISSES,
        update_system_metrics
    )
    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False
    print("Warning: Prometheus metrics not available")

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="FinanceML API",
    description="AI-powered stock price prediction API",
    version="1.0.0"
)

# CORS - Allow frontend domains
allowed_origins = [
    "http://localhost:3000",  # Local development
    "http://localhost:3001",  # Alternative local port
    "https://financeml-frontend.onrender.com",  # Render frontend
    # Add your custom domain here when you have one:
    # "https://yourdomain.me",
    # "https://www.yourdomain.me",
]

# In development, allow all origins
if os.getenv("ENVIRONMENT") == "development":
    allowed_origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request, call_next):
    """Collect metrics for each request"""
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Record metrics
    if METRICS_ENABLED:
        duration = time.time() - start_time
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(duration)
        
        # Update system metrics periodically (every 10 requests)
        if REQUEST_COUNT._metrics:
            try:
                update_system_metrics()
            except:
                pass
    
    return response


# Global service instance
prediction_service = None
forecasting_service = None
sentiment_analyzer = None
risk_analyzer = None
portfolio_optimizer = None

# Pydantic Models
class PredictionRequest(BaseModel):
    symbol: str
    days_ahead: Optional[int] = 1


class PredictionResponse(BaseModel):
    symbol: str
    current_price: float
    predicted_price: float
    price_change: float
    price_change_pct: float
    trend: str
    prediction_date: str
    confidence: str
    timestamp: str

class PortfolioOptimizeRequest(BaseModel):
    symbols: List[str]
    period: Optional[str] = "2y"
    constraints: Optional[dict] = None


class EfficientFrontierRequest(BaseModel):
    symbols: List[str]
    period: Optional[str] = "2y"
    num_portfolios: Optional[int] = 50
    constraints: Optional[dict] = None


class MonteCarloRequest(BaseModel):
    symbols: List[str]
    period: Optional[str] = "2y"
    num_portfolios: Optional[int] = 10000


# Global instances
data_client = YahooFinanceClient()
fundamental_processor = FundamentalProcessor()
router = APIRouter()

def safe_get(df, col):
    """DataFrame'den güvenli şekilde son değeri al, yoksa None döndür"""
    if col in df.columns and not df[col].isna().all():
        return df[col].iloc[-1]
    return None

def safe_float(val):
    """Convert any numeric type to JSON-safe value (None if NaN/inf), including numpy types"""
    if val is None:
        return None
    
    # Handle string values
    if isinstance(val, str):
        return val
    
    # Handle numpy types
    if isinstance(val, (np.generic, np.int64, np.float64, np.float32, np.int32)):
        val = val.item()
    
    # Handle Python numeric types
    if isinstance(val, (float, int)):
        if isinstance(val, float) and (math.isnan(val) or math.isinf(val)):
            return None
        return float(val)
    
    return val


def calculate_financial_score(metrics: dict) -> dict:
    """
    Calculate dynamic financial health score based on actual metrics
    
    Scoring breakdown:
    - Valuation (25 points)
    - Profitability (25 points)
    - Financial Health (25 points)
    - Growth (25 points)
    """
    score = 0
    max_score = 100
    factors = []
    
    # ========== VALUATION (25 points) ==========
    
    # P/E Ratio (10 points)
    pe = metrics.get('pe_ratio')
    if pe is not None and pe > 0:
        if 10 < pe < 20:
            score += 10
            factors.append("Ideal P/E ratio")
        elif 5 < pe < 30:
            score += 7
            factors.append("Good P/E ratio")
        elif pe < 40:
            score += 4
            factors.append("Fair P/E ratio")
        else:
            score += 2
            factors.append("High P/E ratio")
    
    # PEG Ratio (8 points)
    peg = metrics.get('peg_ratio')
    if peg is not None and peg > 0:
        if peg < 1:
            score += 8
            factors.append("Undervalued (PEG < 1)")
        elif peg < 1.5:
            score += 6
            factors.append("Fair valuation (PEG < 1.5)")
        elif peg < 2:
            score += 3
            factors.append("Slightly overvalued")
    
    # Price to Book (7 points)
    pb = metrics.get('price_to_book')
    if pb is not None and pb > 0:
        if pb < 1:
            score += 7
            factors.append("Trading below book value")
        elif pb < 3:
            score += 5
            factors.append("Reasonable P/B ratio")
        elif pb < 5:
            score += 3
            factors.append("Moderate P/B ratio")
    
    # ========== PROFITABILITY (25 points) ==========
    
    # Profit Margin (10 points)
    profit_margin = metrics.get('profit_margin')
    if profit_margin is not None:
        if profit_margin > 0.20:
            score += 10
            factors.append("Excellent profit margin (>20%)")
        elif profit_margin > 0.15:
            score += 8
            factors.append("Strong profit margin (>15%)")
        elif profit_margin > 0.10:
            score += 6
            factors.append("Good profit margin (>10%)")
        elif profit_margin > 0.05:
            score += 3
            factors.append("Moderate profit margin")
        elif profit_margin > 0:
            score += 1
    
    # ROE (Return on Equity) (10 points)
    roe = metrics.get('roe')
    if roe is not None:
        if roe > 0.20:
            score += 10
            factors.append("Outstanding ROE (>20%)")
        elif roe > 0.15:
            score += 8
            factors.append("Excellent ROE (>15%)")
        elif roe > 0.10:
            score += 6
            factors.append("Good ROE (>10%)")
        elif roe > 0.05:
            score += 3
            factors.append("Fair ROE")
    
    # Operating Margin (5 points)
    op_margin = metrics.get('operating_margin')
    if op_margin is not None:
        if op_margin > 0.15:
            score += 5
            factors.append("Strong operating margin")
        elif op_margin > 0.10:
            score += 3
        elif op_margin > 0.05:
            score += 1
    
    # ========== FINANCIAL HEALTH (25 points) ==========
    
    # Current Ratio (8 points)
    current_ratio = metrics.get('current_ratio')
    if current_ratio is not None:
        if current_ratio > 2:
            score += 8
            factors.append("Excellent liquidity (CR > 2)")
        elif current_ratio > 1.5:
            score += 6
            factors.append("Good liquidity (CR > 1.5)")
        elif current_ratio > 1:
            score += 4
            factors.append("Adequate liquidity")
        elif current_ratio > 0.5:
            score += 1
    
    # Debt to Equity (12 points)
    de = metrics.get('debt_to_equity')
    if de is not None:
        if de < 0.3:
            score += 12
            factors.append("Very low debt (D/E < 0.3)")
        elif de < 0.5:
            score += 10
            factors.append("Low debt (D/E < 0.5)")
        elif de < 1.0:
            score += 7
            factors.append("Moderate debt (D/E < 1.0)")
        elif de < 2.0:
            score += 3
            factors.append("High debt level")
        else:
            score += 1
            factors.append("Very high debt")
    
    # Quick Ratio (5 points)
    quick_ratio = metrics.get('quick_ratio')
    if quick_ratio is not None:
        if quick_ratio > 1.5:
            score += 5
            factors.append("Strong quick ratio")
        elif quick_ratio > 1:
            score += 3
        elif quick_ratio > 0.5:
            score += 1
    
    # ========== GROWTH (25 points) ==========
    
    # Revenue Growth (13 points)
    rev_growth = metrics.get('revenue_growth')
    if rev_growth is not None:
        if rev_growth > 0.20:
            score += 13
            factors.append("Exceptional revenue growth (>20%)")
        elif rev_growth > 0.15:
            score += 11
            factors.append("Strong revenue growth (>15%)")
        elif rev_growth > 0.10:
            score += 8
            factors.append("Good revenue growth (>10%)")
        elif rev_growth > 0.05:
            score += 5
            factors.append("Moderate revenue growth")
        elif rev_growth > 0:
            score += 2
            factors.append("Slow revenue growth")
    
    # Earnings Growth (12 points)
    earnings_growth = metrics.get('earnings_growth')
    if earnings_growth is not None:
        if earnings_growth > 0.20:
            score += 12
            factors.append("Exceptional earnings growth (>20%)")
        elif earnings_growth > 0.15:
            score += 10
            factors.append("Strong earnings growth (>15%)")
        elif earnings_growth > 0.10:
            score += 7
            factors.append("Good earnings growth (>10%)")
        elif earnings_growth > 0.05:
            score += 4
            factors.append("Moderate earnings growth")
        elif earnings_growth > 0:
            score += 2
    
    # ========== RATING ==========
    
    percentage = (score / max_score) * 100
    
    if percentage >= 90:
        rating = "Exceptional"
        interpretation = "Outstanding financial health across all metrics"
        color = "#10b981"
    elif percentage >= 75:
        rating = "Excellent"
        interpretation = "Strong financial fundamentals with minor concerns"
        color = "#3b82f6"
    elif percentage >= 60:
        rating = "Good"
        interpretation = "Solid financial position with some areas for improvement"
        color = "#8b5cf6"
    elif percentage >= 45:
        rating = "Fair"
        interpretation = "Mixed financial indicators, requires careful analysis"
        color = "#f59e0b"
    elif percentage >= 30:
        rating = "Poor"
        interpretation = "Weak fundamentals with significant risks"
        color = "#ef4444"
    else:
        rating = "Critical"
        interpretation = "Severe financial concerns, high investment risk"
        color = "#991b1b"
    
    return {
        "score": int(score),
        "max_score": max_score,
        "percentage": round(percentage, 1),
        "rating": rating,
        "interpretation": interpretation,
        "color": color,
        "key_factors": factors[:8]  # Top 8 factors
    }

@app.get("/financials/{symbol}")
async def get_financials(symbol: str):
    """
    Return financial data from cache (JSON files)
    """
    try:
        import json
        import os
        
        cache_file = f"/app/data/cache/fundamentals/{symbol.upper()}_fundamentals.json"
        
        # Dosya var mı kontrol 
        if not os.path.exists(cache_file):
            return JSONResponse(content={"error": f"No cached data found for {symbol.upper()}"}, status_code=404)
        
        # JSON dosyası
        with open(cache_file, 'r') as f:
            cached_data = json.load(f)
        
        # fundamentals objesi
        metrics = cached_data.get("fundamentals", {})
        
        # Frontend için düzenleme (key isimleri küçük harfe çevir)
        frontend_metrics = {
            "company_name": metrics.get("Company_Name", symbol.upper()),
            "pe_ratio": safe_float(metrics.get("PE_Ratio")),
            "forward_pe": safe_float(metrics.get("Forward_PE")),
            "peg_ratio": safe_float(metrics.get("PEG_Ratio")),
            "price_to_book": safe_float(metrics.get("Price_to_Book")),
            "price_to_sales": safe_float(metrics.get("Price_to_Sales")),
            "profit_margin": safe_float(metrics.get("Profit_Margin")),
            "operating_margin": safe_float(metrics.get("Operating_Margin")),
            "gross_margin": safe_float(metrics.get("Gross_Margin")),
            "roe": safe_float(metrics.get("ROE")),
            "roa": safe_float(metrics.get("ROA")),
            "current_ratio": safe_float(metrics.get("Current_Ratio")),
            "quick_ratio": safe_float(metrics.get("Quick_Ratio")),
            "debt_to_equity": safe_float(metrics.get("Debt_to_Equity")),
            "total_debt": safe_float(metrics.get("Total_Debt")),
            "free_cashflow": safe_float(metrics.get("Free_Cashflow")),
            "revenue_growth": safe_float(metrics.get("Revenue_Growth")),
            "earnings_growth": safe_float(metrics.get("Earnings_Growth")),
            "eps_trailing": safe_float(metrics.get("EPS")),
            "market_cap": safe_float(metrics.get("Market_Cap")),
            "quarterly_income": [],
            "sector": metrics.get("Sector", "Technology"),
            "industry": metrics.get("Industry", "Software")
        }
        
        # Financial score hesapla
        financial_score = calculate_financial_score(frontend_metrics)

        return JSONResponse(content={"metrics": frontend_metrics, "financial_score": financial_score})

    except Exception as e:
        logger.error(f"Error fetching financials for {symbol}: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)




# Startup event
@app.on_event("startup")
async def startup_event():
    global prediction_service, forecasting_service , sentiment_analyzer, risk_analyzer, portfolio_optimizer
    
    logger.info("🚀 Starting FinanceML API...")
    
    try:
        prediction_service = PredictionService()
        forecasting_service = ForecastingService(cache_dir="/app/data/cache")
        sentiment_analyzer = SentimentAnalyzer(min_news_threshold=1, news_api_key="96195a56e9224ebf8d25d17d42ec3ba9")
        risk_analyzer = RiskAnalyzer(cache_dir="/app/data/cache")
        portfolio_optimizer = PortfolioOptimizer(risk_free_rate=0.02, cache_dir="/app/data/cache")
        logger.info("✅ Services initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {str(e)}")
        raise

@app.get("/sentiment/{symbol}")
async def get_sentiment(symbol: str, days: int = 7):
    if sentiment_analyzer is None:
        raise HTTPException(status_code=503, detail="Service not initialized")

    try:
        result = sentiment_analyzer.analyze_stock_sentiment(
            symbol.upper(),
            days=days
        )

        if result.get('error'):
            raise HTTPException(status_code=404, detail=result['error'])

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Sentiment analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Sentiment analysis failed")


@app.get("/risk/{symbol}")
async def get_risk_analysis(symbol: str):
    """
    Get comprehensive risk analysis
    
    - **symbol**: Stock symbol
    """
    if risk_analyzer is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = risk_analyzer.analyze_risk(symbol.upper())
        return result
        
    except Exception as e:
        logger.error(f"Risk analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail="Risk analysis failed")


# Health check
@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "service": "FinanceML API",
        "version": "1.0.0"
    }


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    try:
        from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
        from fastapi import Response
        return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
    except ImportError:
        return {"error": "prometheus_client not installed"}


@app.get("/model/status")
async def model_status():
    """Model durumu"""
    if prediction_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    return prediction_service.get_model_status()


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: PredictionRequest):
    """
    Hisse senedi fiyat tahmini
    
    - **symbol**: Hisse kodu (AAPL, MSFT, GOOGL, etc.)
    - **days_ahead**: Kaç gün sonrası (1-7, default: 1)
    """
    if prediction_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = prediction_service.predict_next_day(
            symbol=request.symbol.upper(),
            days_ahead=request.days_ahead
        )
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        raise HTTPException(status_code=500, detail="Prediction failed")
    
class ForecastRequest(BaseModel):
    symbol: str
    days: Optional[int] = 14
    include_weekends: Optional[bool] = False


@app.get("/")
async def root():
    """API root"""
    return {
        "message": "FinanceML API",
        "docs": "/docs",
        "health": "/health"
    }


@app.post("/portfolio/optimize")
async def optimize_portfolio(request: PortfolioOptimizeRequest):
    """
    Complete portfolio optimization using Modern Portfolio Theory
    
    - **symbols**: List of stock symbols (e.g., ["AAPL", "MSFT", "GOOGL"])
    - **period**: Historical data period (default: 2y)
    - **constraints**: Optional dict with 'min_weight' and 'max_weight'
    
    Returns:
    - Maximum Sharpe ratio portfolio
    - Minimum variance portfolio
    - Efficient frontier
    - Correlation matrix
    - Individual asset statistics
    """
    if portfolio_optimizer is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        if len(request.symbols) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 symbols required for portfolio optimization"
            )
        
        result = portfolio_optimizer.analyze_portfolio(
            symbols=request.symbols,
            period=request.period,
            constraints=request.constraints
        )
        
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Portfolio optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Portfolio optimization failed")


@app.post("/portfolio/efficient-frontier")
async def get_efficient_frontier(request: EfficientFrontierRequest):
    """
    Calculate efficient frontier for a set of assets
    
    - **symbols**: List of stock symbols
    - **period**: Historical data period
    - **num_portfolios**: Number of portfolios to generate (default: 50)
    - **constraints**: Optional weight constraints
    """
    if portfolio_optimizer is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        if len(request.symbols) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 symbols required"
            )
        
        # Prepare data
        portfolio_optimizer.prepare_data(request.symbols, request.period)
        
        # Calculate efficient frontier
        result = portfolio_optimizer.calculate_efficient_frontier(
            num_portfolios=request.num_portfolios,
            constraints=request.constraints
        )
        
        return {
            'symbols': request.symbols,
            'period': request.period,
            'efficient_frontier': result,
            'timestamp': datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Efficient frontier error: {str(e)}")
        raise HTTPException(status_code=500, detail="Efficient frontier calculation failed")


@app.post("/portfolio/monte-carlo")
async def monte_carlo_simulation(request: MonteCarloRequest):
    """
    Run Monte Carlo simulation for random portfolio generation
    
    - **symbols**: List of stock symbols
    - **period**: Historical data period
    - **num_portfolios**: Number of random portfolios (default: 10000)
    """
    if portfolio_optimizer is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        if len(request.symbols) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 symbols required"
            )
        
        # Prepare data
        portfolio_optimizer.prepare_data(request.symbols, request.period)
        
        # Run Monte Carlo
        result = portfolio_optimizer.monte_carlo_simulation(
            num_portfolios=request.num_portfolios
        )
        
        # Also get optimal portfolios for reference
        max_sharpe = portfolio_optimizer.optimize_sharpe_ratio()
        min_variance = portfolio_optimizer.optimize_min_variance()
        
        return {
            'symbols': request.symbols,
            'period': request.period,
            'simulation': result,
            'optimal_portfolios': {
                'max_sharpe': max_sharpe,
                'min_variance': min_variance
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Monte Carlo simulation error: {str(e)}")
        raise HTTPException(status_code=500, detail="Monte Carlo simulation failed")


@app.get("/portfolio/correlation/{symbols}")
async def get_correlation_matrix(symbols: str, period: str = "2y"):
    """
    Get correlation matrix for assets
    
    - **symbols**: Comma-separated stock symbols (e.g., "AAPL,MSFT,GOOGL")
    - **period**: Historical data period (default: 2y)
    """
    if portfolio_optimizer is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        if len(symbol_list) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 symbols required"
            )
        
        # Prepare data
        portfolio_optimizer.prepare_data(symbol_list, period)
        
        # Get correlation matrix
        result = portfolio_optimizer.get_correlation_matrix()
        
        return {
            'symbols': symbol_list,
            'period': period,
            'correlation_matrix': result,
            'timestamp': datetime.now().isoformat()
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Correlation matrix error: {str(e)}")
        raise HTTPException(status_code=500, detail="Correlation matrix calculation failed")


@app.post("/portfolio/target-return")
async def optimize_target_return(
    symbols: List[str],
    target_return: float,
    period: str = "2y",
    constraints: Optional[dict] = None
):
    """
    Find minimum variance portfolio for a target return
    
    - **symbols**: List of stock symbols
    - **target_return**: Target annual return (e.g., 0.15 for 15%)
    - **period**: Historical data period
    - **constraints**: Optional weight constraints
    """
    if portfolio_optimizer is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        if len(symbols) < 2:
            raise HTTPException(
                status_code=400, 
                detail="At least 2 symbols required"
            )
        
        # Prepare data
        portfolio_optimizer.prepare_data(symbols, period)
        
        # Optimize for target return
        result = portfolio_optimizer.optimize_target_return(
            target_return=target_return,
            constraints=constraints
        )
        
        if result is None or not result.get('success'):
            raise HTTPException(
                status_code=400,
                detail=f"Could not find portfolio with target return {target_return:.2%}"
            )
        
        return {
            'symbols': symbols,
            'period': period,
            'portfolio': result,
            'timestamp': datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Target return optimization error: {str(e)}")
        raise HTTPException(status_code=500, detail="Optimization failed")

@app.post("/forecast")
async def forecast_multi_day(request: ForecastRequest):
    """
    Multi-day stock price forecast
    
    - **symbol**: Stock symbol
    - **days**: Number of days (1-30, default: 14)
    - **include_weekends**: Include weekends (default: false)
    """
    if forecasting_service is None:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        result = forecasting_service.forecast_multi_day(
            symbol=request.symbol.upper(),
            days=min(request.days, 30),
            include_weekends=request.include_weekends
        )

        # Save to database
        try:
            db.save_prediction(
                symbol=result['symbol'],
                prediction_type='multi_day',
                prediction_date=result['forecast']['dates'][-1],
                current_price=result['current_price'],
                predicted_price=result['final_predicted_price'],
                forecast_days=result['forecast_days'],
                trend=result['trend'],
                prediction_data={
                    'forecast': result['forecast'],
                    'statistics': result['statistics']
                }
            )
        except Exception as e:
            logger.warning(f"Failed to save prediction: {e}")

        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Forecast error: {str(e)}")
        raise HTTPException(status_code=500, detail="Forecast failed")
    



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)