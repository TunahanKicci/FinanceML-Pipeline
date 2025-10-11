# models/forecasting_service.py
"""
Multi-day stock price forecasting service - Cache-based version
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

from data.feature_engineering import FeatureEngineer
from data.processors.fundamental_processor import FundamentalProcessor

logger = logging.getLogger(__name__)


class CachedDataClient:
    """Simple client to load cached price data"""
    
    def __init__(self, cache_dir: str = "/app/data/cache"):
        self.cache_dir = cache_dir
    
    def fetch_stock_data(self, symbol: str, period: str = "2y") -> pd.DataFrame:
        """Load stock data from CSV cache"""
        try:
            cache_file = os.path.join(self.cache_dir, f"{symbol}_2y_1d.csv")
            
            if not os.path.exists(cache_file):
                logger.error(f"Cache file not found: {cache_file}")
                raise ValueError(f"No cached data found for {symbol}")
            
            df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            
            if df.empty:
                logger.error(f"Empty data for {symbol}")
                raise ValueError(f"No data found for {symbol}")
            
            logger.info(f"✅ Loaded {len(df)} records from cache for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading cached data for {symbol}: {e}")
            raise ValueError(f"No data found for {symbol}")


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
        
        model_path = f"{self.artifacts_dir}/{self.symbol}_model.keras"
        self.model = keras.models.load_model(model_path)
        logger.info(f"Model loaded")
        
        with open(f"{self.artifacts_dir}/feature_scaler.pkl", "rb") as f:
            self.feature_scaler = pickle.load(f)
        
        with open(f"{self.artifacts_dir}/target_scaler.pkl", "rb") as f:
            self.label_scaler = pickle.load(f)
        logger.info(f"Scalers loaded")
        
        with open(f"{self.artifacts_dir}/feature_columns.json", "r") as f:
            self.feature_columns = json.load(f)
        logger.info(f"Feature columns: {len(self.feature_columns)}")
        
        with open(f"{self.artifacts_dir}/model_metadata.json", "r") as f:
            self.metadata = json.load(f)
        logger.info(f"Metadata loaded")


class ForecastingService:
    """Multi-day stock price forecasting - Cache-based version"""
    
    def __init__(self, cache_dir: str = "/app/data/cache"):
        self.data_client = CachedDataClient(cache_dir=cache_dir)
        self.feature_engineer = FeatureEngineer()
        self.fundamental_processor = FundamentalProcessor()
        self.loaded_models = {}
    
    def _get_model_loader(self, symbol: str) -> StockModelLoader:
        if symbol not in self.loaded_models:
            self.loaded_models[symbol] = StockModelLoader(symbol)
        return self.loaded_models[symbol]
    
    def _add_return_features_like_training(self, df):
        """Training kodundaki add_return_features ile aynı mantık"""
        df = df.copy()
        df['Return'] = df['Close'].pct_change().fillna(0)
        df['Return_lag_1'] = df['Return'].shift(1).fillna(0)
        df['Return_lag_2'] = df['Return'].shift(2).fillna(0)
        df['Volatility_5'] = df['Return'].rolling(5).std().ffill().fillna(0)
        df['Volatility_20'] = df['Return'].rolling(20).std().ffill().fillna(0)
        df['Price_Position'] = (df['Close'] - df['Low']) / (df['High'] - df['Low'] + 1e-8)
        df['Price_Position'] = df['Price_Position'].fillna(0.5)
        df['Volume_MA_20'] = df['Volume'].rolling(20).mean().ffill().fillna(0)
        df['Volume_Ratio'] = (df['Volume'] / (df['Volume_MA_20'] + 1e-8)).fillna(1.0)
        
        if 'SMA_5' in df.columns and 'SMA_20' in df.columns:
            df['SMA_ratio'] = df['SMA_5'] / (df['SMA_20'] + 1e-8)
        else:
            df['SMA_ratio'] = 1.0
        
        if 'MACD' in df.columns and 'MACD_Signal' in df.columns:
            df['MACD_diff'] = df['MACD'] - df['MACD_Signal']
        else:
            df['MACD_diff'] = 0.0
        
        if 'RSI' in df.columns:
            df['RSI_change'] = df['RSI'].diff().fillna(0)
        else:
            df['RSI_change'] = 0.0
        
        df['HL_Ratio'] = (df['High'] / (df['Low'] + 1e-8)).fillna(1.0)
        df['CO_Ratio'] = (df['Close'] / (df['Open'] + 1e-8)).fillna(1.0)
        
        df = df.ffill().bfill().fillna(0)
        return df
    
    def forecast_multi_day(self, symbol: str, days: int = 14, include_weekends: bool = False) -> Dict:
        try:
            logger.info(f"Starting {days}-day forecast for {symbol}")
            
            # 1. Load model
            model_loader = self._get_model_loader(symbol)
            sequence_length = model_loader.metadata.get("sequence_length", 60)
            trained_features = model_loader.feature_columns
            
            logger.info(f"Model expects features: {trained_features}")
            
            # 2. Fetch historical data
            logger.info(f"Fetching historical data for {symbol}...")
            df = self.data_client.fetch_stock_data(symbol, period="5y")
            
            # 3. Build technical indicators
            df_with_tech = self.feature_engineer.add_technical_indicators(df)
            
            # 4. Add return features (training ile aynı şekilde)
            df_features = self._add_return_features_like_training(df_with_tech)
            
            # 5. Align features
            for col in trained_features:
                if col not in df_features.columns:
                    df_features[col] = 0.0
            
            df_features = df_features[trained_features]
            
            # 6. Create working dataframe with OHLCV
            base_df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
            
            # KRITIK: Gerçek tarihsel return değerlerini kaydet
            historical_returns = df['Close'].pct_change().fillna(0).values
            
            logger.info(f"Starting iterative forecast...")
            
            # 7. ITERATIVE FORECASTING
            forecasts = []
            forecast_dates = []
            confidence_scores = []
            
            current_date = base_df.index[-1]
            
            for step in range(days):
                # Technical indicators hesapla
                features_temp = self.feature_engineer.add_technical_indicators(base_df)
                
                # Return features ekle ANCAK gerçek tarihsel veriden al
                features_temp = self._add_return_features_like_training(features_temp)
                
                # KRITIK FIX: Return lag'leri gerçek tarihsel veriden override et
                if len(historical_returns) >= 2:
                    features_temp.loc[features_temp.index[-1], 'Return_lag_1'] = historical_returns[-1]
                    features_temp.loc[features_temp.index[-1], 'Return_lag_2'] = historical_returns[-2]
                
                # Align with trained features
                for col in trained_features:
                    if col not in features_temp.columns:
                        logger.warning(f"Missing feature: {col}, setting to 0")
                        features_temp[col] = 0.0
                
                features_rebuilt = features_temp[trained_features]
                
                # Get last sequence
                if len(features_rebuilt) < sequence_length:
                    raise ValueError(f"Not enough data: {len(features_rebuilt)} < {sequence_length}")
                
                last_sequence = features_rebuilt.iloc[-sequence_length:].values
                
                # Scale and predict
                features_scaled = model_loader.feature_scaler.transform(last_sequence)
                X_input = features_scaled.reshape(1, sequence_length, -1)
                
                prediction_scaled = model_loader.model.predict(X_input, verbose=0)
                
                # Check if model predicts price or return
                prediction_type = model_loader.metadata.get('prediction_type', 'return')
                
                if prediction_type == 'price':
                    predicted_price = model_loader.label_scaler.inverse_transform(prediction_scaled)[0][0]
                else:
                    # Return prediction
                    predicted_return = model_loader.label_scaler.inverse_transform(prediction_scaled)[0][0]
                    last_close = base_df['Close'].iloc[-1]
                    predicted_price = last_close * (1.0 + predicted_return)
                
                # Get last close for validation
                last_close = base_df['Close'].iloc[-1]
                
                # Apply reasonable constraints
                recent_volatility = base_df['Close'].pct_change().tail(20).std()
                max_daily_change = min(0.05, max(0.02, recent_volatility * 3))
                
                price_change_pct = (predicted_price - last_close) / last_close
                
                # Cap extreme predictions
                if abs(price_change_pct) > max_daily_change:
                    change_direction = 1 if predicted_price > last_close else -1
                    predicted_price = last_close * (1 + max_daily_change * change_direction)
                    logger.info(f"Day {step+1}: Capped {price_change_pct:.2%} to {max_daily_change:.2%}")
                
                # Mean reversion for multi-day bias
                if step >= 3:
                    recent_changes = [
                        (forecasts[i] - forecasts[i-1])/forecasts[i-1] 
                        for i in range(max(1, len(forecasts)-3), len(forecasts))
                    ]
                    avg_change = np.mean(recent_changes) if recent_changes else 0
                    
                    if avg_change < -0.01:
                        predicted_price *= 1.003
                    elif avg_change > 0.01:
                        predicted_price *= 0.997
                
                # Ensure positive
                if predicted_price <= 0:
                    predicted_price = last_close * 0.99
                
                # Calculate next date
                next_date = current_date + timedelta(days=1)
                if not include_weekends:
                    while next_date.weekday() >= 5:
                        next_date += timedelta(days=1)
                
                # Store forecast
                forecasts.append(float(predicted_price))
                forecast_dates.append(next_date.strftime('%Y-%m-%d'))
                confidence = max(0.5, 1.0 - (step * 0.025))
                confidence_scores.append(float(confidence))
                
                # Create synthetic OHLCV for next day
                volatility = base_df['Close'].pct_change().std()
                noise = np.random.normal(0, volatility * 0.5)
                
                new_open = predicted_price
                new_high = predicted_price * (1 + abs(noise))
                new_low = predicted_price * (1 - abs(noise))
                new_close = predicted_price
                new_volume = base_df['Volume'].iloc[-1]
                
                # Add to base_df
                new_row = pd.DataFrame({
                    'Open': [new_open],
                    'High': [new_high],
                    'Low': [new_low],
                    'Close': [new_close],
                    'Volume': [new_volume]
                }, index=[next_date])
                
                base_df = pd.concat([base_df, new_row])
                
                # KRITIK: Gerçek return array'ini güncelle (tahmin edilen return'ü EKLE)
                predicted_return_val = (predicted_price - last_close) / last_close
                historical_returns = np.append(historical_returns, predicted_return_val)
                
                current_date = next_date
                
                logger.info(f"Day {step+1}/{days}: ${predicted_price:.2f} (return: {predicted_return_val:.4f})")
            
            # 8. Calculate statistics
            current_price = float(df['Close'].iloc[-1])
            final_price = forecasts[-1]
            total_change = final_price - current_price
            total_change_pct = (total_change / current_price) * 100
            
            forecast_volatility = float(np.std(forecasts))
            
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
                    "avg_price": round(np.mean(forecasts), 2),
                    "price_range": round(max(forecasts) - min(forecasts), 2)
                },
                "model_info": {
                    "version": model_loader.metadata.get("model_version", "unknown"),
                    "trained_on": model_loader.metadata.get("trained_on", "unknown"),
                    "r2_score": model_loader.metadata.get("metrics", {}).get("return_r2", None),
                    "mape": model_loader.metadata.get("metrics", {}).get("price_mape_pct", None),
                    "directional_accuracy": model_loader.metadata.get("metrics", {}).get("directional_accuracy_pct", None)
                },
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Forecast complete: {trend} ({total_change_pct:+.2f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f"Forecast failed for {symbol}: {str(e)}", exc_info=True)
            raise
    
    def forecast_multiple_symbols(self, symbols: List[str], days: int = 14) -> Dict[str, Dict]:
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