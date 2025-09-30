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

# Path setup
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.prediction_service import PredictionService

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


# Startup event
@app.on_event("startup")
async def startup_event():
    global prediction_service, forecasting_service
    
    logger.info("🚀 Starting FinanceML API...")
    
    try:
        prediction_service = PredictionService()
        forecasting_service = ForecastingService()
        logger.info("✅ Services initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize: {str(e)}")
        raise


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