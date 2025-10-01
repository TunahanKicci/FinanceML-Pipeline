# api/main.py
"""
FastAPI Main Application
"""
from models.forecasting_service import ForecastingService
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import logging
import sys
import os
from fastapi.responses import JSONResponse
import yfinance as yf
import math

# Path setup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.prediction_service import PredictionService
from fastapi import HTTPException
from data.processors.fundamental_processor import FundamentalProcessor
from data.sources.yahoo_finance import YahooFinanceClient
from fastapi import APIRouter
from data.sources.sentiment_analyzer import SentimentAnalyzer


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

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Production'da kısıtla
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
prediction_service = None
forecasting_service = None
sentiment_analyzer = None

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
    """Convert float/int to JSON-safe value (None if NaN or inf)"""
    if val is None:
        return None
    if isinstance(val, (float, int)):
        if math.isnan(val) or math.isinf(val):
            return None
        return float(val)
    return val

@app.get("/financials/{symbol}")
async def get_financials(symbol: str):
    """
    Return real financial data using yfinance
    """
    try:
        # 1. Fiyat verisini al (son 1 yıl)
        ticker = yf.Ticker(symbol)
        price_df = ticker.history(period="1y")
        if price_df.empty:
            return JSONResponse(content={"error": "Price data not found"}, status_code=404)

        # 2. Temel verileri merge et
        df_with_fundamentals = fundamental_processor.fetch_and_merge_fundamentals(symbol, price_df)

        # 3. Frontend’in beklediği JSON yapısına dönüştür
        metrics = {
            "company_name": ticker.info.get("shortName", symbol.upper()),
            "pe_ratio": safe_float(df_with_fundamentals.get("PE_Ratio").iloc[-1] if "PE_Ratio" in df_with_fundamentals else None),
            "forward_pe": safe_float(df_with_fundamentals.get("Forward_PE").iloc[-1] if "Forward_PE" in df_with_fundamentals else None),
            "peg_ratio": safe_float(df_with_fundamentals.get("PEG_Ratio").iloc[-1] if "PEG_Ratio" in df_with_fundamentals else None),
            "price_to_book": safe_float(df_with_fundamentals.get("Price_to_Book").iloc[-1] if "Price_to_Book" in df_with_fundamentals else None),
            "price_to_sales": safe_float(df_with_fundamentals.get("Price_to_Sales").iloc[-1] if "Price_to_Sales" in df_with_fundamentals else None),
            "profit_margin": safe_float(df_with_fundamentals.get("Profit_Margin").iloc[-1] if "Profit_Margin" in df_with_fundamentals else None),
            "operating_margin": safe_float(df_with_fundamentals.get("Operating_Margin").iloc[-1] if "Operating_Margin" in df_with_fundamentals else None),
            "gross_margin": safe_float(df_with_fundamentals.get("Gross_Margin").iloc[-1] if "Gross_Margin" in df_with_fundamentals else None),
            "roe": safe_float(df_with_fundamentals.get("ROE").iloc[-1] if "ROE" in df_with_fundamentals else None),
            "roa": safe_float(df_with_fundamentals.get("ROA").iloc[-1] if "ROA" in df_with_fundamentals else None),
            "current_ratio": safe_float(df_with_fundamentals.get("Current_Ratio").iloc[-1] if "Current_Ratio" in df_with_fundamentals else None),
            "quick_ratio": safe_float(df_with_fundamentals.get("Quick_Ratio").iloc[-1] if "Quick_Ratio" in df_with_fundamentals else None),
            "debt_to_equity": safe_float(df_with_fundamentals.get("Debt_to_Equity").iloc[-1] if "Debt_to_Equity" in df_with_fundamentals else None),
            "total_debt": safe_float(df_with_fundamentals.get("Total_Debt").iloc[-1] if "Total_Debt" in df_with_fundamentals else None),
            "free_cashflow": safe_float(df_with_fundamentals.get("Free_Cashflow").iloc[-1] if "Free_Cashflow" in df_with_fundamentals else None),
            "revenue_growth": safe_float(df_with_fundamentals.get("Revenue_Growth").iloc[-1] if "Revenue_Growth" in df_with_fundamentals else None),
            "earnings_growth": safe_float(df_with_fundamentals.get("Earnings_Growth").iloc[-1] if "Earnings_Growth" in df_with_fundamentals else None),
            "eps_trailing": safe_float(df_with_fundamentals.get("EPS").iloc[-1] if "EPS" in df_with_fundamentals else None),
            "market_cap": safe_float(ticker.info.get("marketCap")),
            "quarterly_income": [],  # opsiyonel: quarterly_financials eklenebilir
            "sector": ticker.info.get("sector", ""),
            "industry": ticker.info.get("industry", "")
        }

        # Mock financial score (opsiyonel: gerçek algoritma ile hesaplanabilir)
        financial_score = {
            "score": 85,
            "max_score": 100,
            "percentage": 85 / 100,
            "rating": "Excellent",
            "interpretation": "Strong financial health",
            "key_factors": ["High ROE", "Low Debt", "Consistent Revenue Growth"]
        }

        return JSONResponse(content={"metrics": metrics, "financial_score": financial_score})

    except Exception as e:
        logger.error(f"Error fetching financials for {symbol}: {e}")
        return JSONResponse(content={"error": str(e)}, status_code=500)




# Startup event
@app.on_event("startup")
async def startup_event():
    global prediction_service, forecasting_service , sentiment_analyzer
    
    logger.info("🚀 Starting FinanceML API...")
    
    try:
        prediction_service = PredictionService()
        forecasting_service = ForecastingService()
        sentiment_analyzer = SentimentAnalyzer(min_news_threshold=1, news_api_key="96195a56e9224ebf8d25d17d42ec3ba9")
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


# Health check
@app.get("/health")
async def health_check():
    """System health check"""
    return {
        "status": "healthy",
        "service": "FinanceML API",
        "version": "1.0.0"
    }


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
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Forecast error: {str(e)}")
        raise HTTPException(status_code=500, detail="Forecast failed")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)