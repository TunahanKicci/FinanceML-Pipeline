# models/forecasting_service.py
"""
Multi-day stock price forecasting service - Per Stock Models
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List
import logging
import json
import pickle
from tensorflow import keras

from data.sources.yahoo_finance import YahooFinanceClient
from data.feature_engineering import FeatureEngineer
from data.processors.fundamental_processor import FundamentalProcessor

logger = logging.getLogger(__name__)


class StockModelLoader:
    """Load model artifacts for a specific stock"""
    
    def __init__(self, symbol: str):
        self.symbol = symbol
        self.artifacts_dir = f"models/artifacts/{symbol}"
        self.model = None
        self.feature_scaler = None
        self.label_scaler = None
        self.feature_columns = None
        self.metadata = None
        
        if not os.path.exists(self.artifacts_dir):
            raise ValueError(f"No trained model found for {symbol}. Train it first!")
        
        self.load_all()
    
    def load_all(self):
        """Load all artifacts for the stock"""
        logger.info(f"Loading model artifacts for {self.symbol}...")
        
        # 1. Load model
        model_path = f"{self.artifacts_dir}/{self.symbol}_model.keras"
        self.model = keras.models.load_model(model_path)
        logger.info(f"✅ Model loaded: {model_path}")
        
        # 2. Load scalers
        with open(f"{self.artifacts_dir}/feature_scaler.pkl", "rb") as f:
            self.feature_scaler = pickle.load(f)
        
        with open(f"{self.artifacts_dir}/label_scaler.pkl", "rb") as f:
            self.label_scaler = pickle.load(f)
        logger.info(f"✅ Scalers loaded")
        
        # 3. Load feature columns
        with open(f"{self.artifacts_dir}/feature_columns.json", "r") as f:
            self.feature_columns = json.load(f)
        logger.info(f"✅ Feature columns loaded: {len(self.feature_columns)} features")
        
        # 4. Load metadata
        with open(f"{self.artifacts_dir}/model_metadata.json", "r") as f:
            self.metadata = json.load(f)
        logger.info(f"✅ Metadata loaded")
        
        logger.info(f"🎉 All artifacts loaded for {self.symbol}")


class ForecastingService:
    """Multi-day stock price forecasting"""
    
    def __init__(self):
        self.data_client = YahooFinanceClient()
        self.feature_engineer = FeatureEngineer()
        self.fundamental_processor = FundamentalProcessor()
        self.loaded_models = {}  # Cache for loaded models
    
    def _get_model_loader(self, symbol: str) -> StockModelLoader:
        """Get or load model for symbol (with caching)"""
        if symbol not in self.loaded_models:
            self.loaded_models[symbol] = StockModelLoader(symbol)
        return self.loaded_models[symbol]
    
    def forecast_multi_day(self, symbol: str, days: int = 14, include_weekends: bool = False) -> Dict:
        """
        Forecast stock prices for multiple days
        
        Args:
            symbol: Stock symbol (must have a trained model)
            days: Number of days to forecast
            include_weekends: Whether to include weekend dates
        
        Returns:
            Dict with forecast results
        """
        try:
            logger.info(f"Starting {days}-day forecast for {symbol}")
            
            # 1. Load model for this specific symbol
            model_loader = self._get_model_loader(symbol)
            sequence_length = model_loader.metadata.get("sequence_length", 60)
            use_fundamentals = model_loader.metadata.get("use_fundamentals", True)
            
            # 2. Fetch historical data
            logger.info(f"Fetching historical data for {symbol}...")
            df = self.data_client.fetch_stock_data(symbol, period="5y")
            
            # 3. Add technical indicators
            df_features = self.feature_engineer.add_technical_indicators(df)
            
            # 4. Add fundamental features (if used in training)
            if use_fundamentals:
                df_features = self.fundamental_processor.fetch_and_merge_fundamentals(symbol, df_features)
            
            # 5. CRITICAL: Align features with trained model
            # Get the EXACT feature columns used during training
            trained_features = model_loader.feature_columns
            
            # Ensure all trained features exist
            for col in trained_features:
                if col not in df_features.columns:
                    df_features[col] = 0.0
                    logger.warning(f"Missing feature '{col}', filled with 0")
            
            # Remove extra features not in training
            df_features = df_features[trained_features]
            
            # 6. Combine with target (Close)
            df_with_target = df[['Close']].join(df_features)
            df_with_target = df_with_target.dropna()
            
            logger.info(f"Data prepared: {len(df_with_target)} rows, {len(trained_features)} features")
            
            # 7. ITERATIVE FORECASTING
            forecasts = []
            forecast_dates = []
            confidence_scores = []
            
            current_date = df_with_target.index[-1]
            working_df = df_with_target.copy()
            
            for step in range(days):
                # Get last sequence
                last_sequence = working_df[trained_features].iloc[-sequence_length:].values
                last_close = working_df['Close'].iloc[-1]
                
                # Scale features
                features_scaled = model_loader.feature_scaler.transform(last_sequence)
                X_input = features_scaled.reshape(1, sequence_length, -1)
                
                # Predict
                prediction_scaled = model_loader.model.predict(X_input, verbose=0)
                predicted_price = model_loader.label_scaler.inverse_transform(prediction_scaled)[0][0]
                
                # Sanity check - prevent unrealistic jumps
                max_daily_change = 0.10  # Max 10% daily change
                if abs(predicted_price - last_close) / last_close > max_daily_change:
                    change_direction = 1 if predicted_price > last_close else -1
                    predicted_price = last_close * (1 + max_daily_change * change_direction)
                    logger.warning(f"Day {step+1}: Capped extreme prediction")
                
                # Calculate next date
                next_date = current_date + timedelta(days=1)
                if not include_weekends:
                    while next_date.weekday() >= 5:  # Skip weekends
                        next_date += timedelta(days=1)
                
                # Confidence decreases over time
                confidence = max(0.4, 1.0 - (step * 0.03))
                
                forecasts.append(float(predicted_price))
                forecast_dates.append(next_date.strftime('%Y-%m-%d'))
                confidence_scores.append(float(confidence))
                
                # Add new row to working dataframe
                new_row = pd.Series(index=trained_features, dtype=float)
                
                # Copy previous values for features
                for col in trained_features:
                    # Most features will use last known value
                    new_row[col] = working_df[col].iloc[-1]
                
                # Create new row with predicted close
                new_close_row = pd.DataFrame({
                    'Close': [predicted_price]
                }, index=[next_date])
                
                new_feature_row = pd.DataFrame([new_row], index=[next_date])
                
                # Concatenate
                working_df = pd.concat([working_df, new_close_row.join(new_feature_row)])
                
                # Update rolling technical indicators
                close_series = working_df['Close']
                
                # Update moving averages if they exist
                if 'SMA_5' in trained_features:
                    working_df['SMA_5'] = close_series.rolling(5).mean()
                if 'SMA_10' in trained_features:
                    working_df['SMA_10'] = close_series.rolling(10).mean()
                if 'SMA_20' in trained_features:
                    working_df['SMA_20'] = close_series.rolling(20).mean()
                if 'SMA_50' in trained_features:
                    working_df['SMA_50'] = close_series.rolling(50).mean()
                
                # Update returns
                if 'Returns' in trained_features:
                    working_df['Returns'] = close_series.pct_change()
                
                # Update RSI if exists
                if 'RSI' in trained_features:
                    working_df['RSI'] = self.feature_engineer.calculate_rsi(close_series, 14)
                
                # Fill NaN values
                working_df = working_df.fillna(method='ffill')
                
                current_date = next_date
                
                logger.info(f"Day {step+1}/{days}: ${predicted_price:.2f} (confidence: {confidence:.2f})")
            
            # 8. Calculate statistics
            current_price = float(df['Close'].iloc[-1])
            final_price = forecasts[-1]
            total_change = final_price - current_price
            total_change_pct = (total_change / current_price) * 100
            
            # Volatility
            forecast_volatility = float(np.std(forecasts))
            
            # Trend determination
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
            
            # Historical data for charting (last 30 days)
            historical_dates = df.index[-30:].strftime('%Y-%m-%d').tolist()
            historical_prices = df['Close'].iloc[-30:].values.tolist()
            
            # Build result
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
                    "avg_price": round(np.mean(forecasts), 2),
                    "price_range": round(max(forecasts) - min(forecasts), 2)
                },
                "model_info": {
                    "version": model_loader.metadata.get("model_version", "unknown"),
                    "trained_on": model_loader.metadata.get("trained_on", "unknown"),
                    "r2_score": model_loader.metadata.get("metrics", {}).get("r2", None),
                    "mape": model_loader.metadata.get("metrics", {}).get("mape", None)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"✅ Forecast complete: {trend} ({total_change_pct:+.2f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Forecast failed for {symbol}: {str(e)}", exc_info=True)
            raise
    
    def forecast_multiple_symbols(self, symbols: List[str], days: int = 14) -> Dict[str, Dict]:
        """
        Forecast multiple stocks at once
        
        Args:
            symbols: List of stock symbols
            days: Number of days to forecast
        
        Returns:
            Dict mapping symbol to forecast results
        """
        results = {}
        
        for symbol in symbols:
            try:
                logger.info(f"\n{'='*60}")
                logger.info(f"Forecasting {symbol}")
                logger.info(f"{'='*60}")
                
                results[symbol] = self.forecast_multi_day(symbol, days)
                
            except Exception as e:
                logger.error(f"Failed to forecast {symbol}: {str(e)}")
                results[symbol] = {
                    "error": str(e),
                    "symbol": symbol
                }
        
        return results


# Test
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    service = ForecastingService()
    
    # Test single stock
    print("\n" + "="*60)
    print("📊 TESTING SINGLE STOCK FORECAST")
    print("="*60)
    
    result = service.forecast_multi_day("AAPL", days=14)
    
    print(f"\nSymbol: {result['symbol']}")
    print(f"Current: ${result['current_price']}")
    print(f"14-day prediction: ${result['final_predicted_price']}")
    print(f"Change: ${result['total_change']} ({result['total_change_pct']:+.2f}%)")
    print(f"Trend: {result['trend']}")
    print(f"Volatility: ${result['volatility']}")
    print(f"Model R² Score: {result['model_info']['r2_score']:.4f}")
    print(f"Model MAPE: {result['model_info']['mape']:.2f}%")
    
    # Test multiple stocks
    print("\n" + "="*60)
    print("📊 TESTING MULTIPLE STOCKS FORECAST")
    print("="*60)
    
    results = service.forecast_multiple_symbols(["AAPL", "MSFT", "GOOGL"], days=7)
    
    print(f"\nSymbol  | Current | 7-day   | Change  | Trend")
    print(f"{'-'*60}")
    
    for symbol, data in results.items():
        if "error" not in data:
            print(f"{symbol:<7} | ${data['current_price']:<7} | ${data['final_predicted_price']:<7} | {data['total_change_pct']:+6.2f}% | {data['trend']}")
        else:
            print(f"{symbol:<7} | ERROR: {data['error']}")