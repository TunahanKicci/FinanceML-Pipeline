# models/forecasting_service.py
"""
Multi-day stock price forecasting service
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import logging

from models.model_loader import ModelLoader
from data.sources.yahoo_finance import YahooFinanceClient
from data.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class ForecastingService:
    """Multi-day stock price forecasting"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.data_client = YahooFinanceClient()
        self.feature_engineer = FeatureEngineer()
        
        # Load model
        self.model_loader.load_all()
        self.sequence_length = self.model_loader.metadata.get("sequence_length", 60)
    
    def forecast_multi_day(
        self, 
        symbol: str, 
        days: int = 14,
        include_weekends: bool = False
    ) -> Dict:
        """
        Multi-day forecasting with iterative prediction
        
        Args:
            symbol: Stock symbol
            days: Number of days to forecast (max 30)
            include_weekends: Include weekend days in forecast
        
        Returns:
            Dict with forecast data and metadata
        """
        try:
            if days > 30:
                days = 30
                logger.warning("Forecast days limited to 30")
            
            logger.info(f"🔮 Forecasting {symbol} for {days} days")
            
            # 1. Get historical data (need more for feature calculation)
            end_date = datetime.now()
            start_date = end_date - timedelta(days=120)  # Extra buffer
            
            df = self.data_client.fetch_stock_data(
                symbol,
                period="5y"  # 5 yıllık veri çek, istersen "max" da olabilir
            )
            
            # 2. Feature engineering
            df_features = self.feature_engineer.add_technical_indicators(df)
            df_features = df_features.dropna()
            
            if len(df_features) < self.sequence_length:
                raise ValueError(f"Not enough data. Need {self.sequence_length}, got {len(df_features)}")
            
            # 3. Prepare feature columns
            feature_columns = [col for col in df_features.columns if col != 'Close']
            
            # 4. Iterative forecasting
            forecasts = []
            forecast_dates = []
            confidence_scores = []
            
            current_date = df_features.index[-1]
            working_df = df_features.copy()
            
            for step in range(days):
                # Get last sequence
                last_sequence = working_df[feature_columns].iloc[-self.sequence_length:].values
                last_close = working_df['Close'].iloc[-1]

                # Scale features
                features_scaled = self.model_loader.feature_scaler.transform(last_sequence)

                print("features_scaled shape before reshape:", features_scaled.shape)
                print("sequence_length:", self.sequence_length)

                X_input = features_scaled[-self.sequence_length:].reshape(1, self.sequence_length, -1)
                
                # Predict
                prediction_scaled = self.model_loader.model.predict(X_input, verbose=0)
                predicted_price = self.model_loader.label_scaler.inverse_transform(prediction_scaled)[0][0]
                
                # Next date
                if include_weekends:
                    next_date = current_date + timedelta(days=1)
                else:
                    # Skip weekends
                    next_date = current_date + timedelta(days=1)
                    while next_date.weekday() >= 5:  # Saturday=5, Sunday=6
                        next_date += timedelta(days=1)
                
                # Calculate confidence (decreases with forecast horizon)
                confidence = max(0.5, 1.0 - (step * 0.02))  # Drops 2% per day
                
                forecasts.append(float(predicted_price))
                forecast_dates.append(next_date.strftime('%Y-%m-%d'))
                confidence_scores.append(float(confidence))
                
                # Update working dataframe with prediction
                new_row = working_df.iloc[-1].copy()
                new_row['Close'] = predicted_price
                new_row['Open'] = predicted_price * 0.995  # Approximate
                new_row['High'] = predicted_price * 1.01
                new_row['Low'] = predicted_price * 0.99
                new_row['Volume'] = working_df['Volume'].iloc[-20:].mean()
                
                # Add as new row
                new_df = pd.DataFrame([new_row], index=[next_date])
                working_df = pd.concat([working_df, new_df])
                
                # Recalculate features
                working_df = self.feature_engineer.add_technical_indicators(working_df)
                working_df = working_df.dropna()
                
                current_date = next_date
                
                logger.info(f"Day {step+1}/{days}: ${predicted_price:.2f} (confidence: {confidence:.2f})")
            
            # 5. Calculate statistics
            current_price = float(df['Close'].iloc[-1])
            final_price = forecasts[-1]
            total_change = final_price - current_price
            total_change_pct = (total_change / current_price) * 100
            
            # Volatility
            forecast_volatility = float(np.std(forecasts))
            
            # Trend
            if total_change_pct > 5:
                trend = "STRONG_UP"
            elif total_change_pct > 1:
                trend = "UP"
            elif total_change_pct < -5:
                trend = "STRONG_DOWN"
            elif total_change_pct < -1:
                trend = "DOWN"
            else:
                trend = "SIDEWAYS"
            
            # Historical data for charting
            historical_dates = df.index[-30:].strftime('%Y-%m-%d').tolist()
            historical_prices = df['Close'].iloc[-30:].values.tolist()
            
            result = {
                "symbol": symbol,
                "forecast_days": days,
                "current_price": round(current_price, 2),
                "final_predicted_price": round(final_price, 2),
                "total_change": round(total_change, 2),
                "total_change_pct": round(total_change_pct, 2),
                "trend": trend,
                "volatility": round(forecast_volatility, 2),
                "forecast": {
                    "dates": forecast_dates,
                    "prices": [round(p, 2) for p in forecasts],
                    "confidence": [round(c, 2) for c in confidence_scores]
                },
                "historical": {
                    "dates": historical_dates,
                    "prices": [round(float(p), 2) for p in historical_prices]
                },
                "statistics": {
                    "min_price": round(min(forecasts), 2),
                    "max_price": round(max(forecasts), 2),
                    "avg_price": round(np.mean(forecasts), 2)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Forecast complete: {trend} ({total_change_pct:+.2f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Forecast failed: {str(e)}")
            raise


# Test
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    service = ForecastingService()
    
    # Test 14-day forecast
    result = service.forecast_multi_day("AAPL", days=14)
    
    print("\n" + "="*60)
    print("📊 MULTI-DAY FORECAST RESULTS")
    print("="*60)
    print(f"Symbol: {result['symbol']}")
    print(f"Current: ${result['current_price']}")
    print(f"14-day prediction: ${result['final_predicted_price']}")
    print(f"Change: ${result['total_change']} ({result['total_change_pct']:+.2f}%)")
    print(f"Trend: {result['trend']}")
    print(f"Volatility: ${result['volatility']}")
    print(f"\nForecast dates: {len(result['forecast']['dates'])} days")
    print(f"Price range: ${result['statistics']['min_price']} - ${result['statistics']['max_price']}")