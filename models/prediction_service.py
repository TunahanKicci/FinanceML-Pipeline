"""
Prediction Service - Business logic layer (FIXED)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime, timedelta
import logging

from models.model_loader import ModelLoader
from data.sources.yahoo_finance import YahooFinanceClient
from data.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class PredictionService:
    """Stock prediction service"""
    
    def __init__(self):
        self.model_loader = ModelLoader()
        self.data_client = YahooFinanceClient()
        self.feature_engineer = FeatureEngineer()
        self.sequence_length = 60
        
        # Model'i yükle
        self.model_loader.load_all()
        self.sequence_length = self.model_loader.metadata.get("sequence_length", 60)
    
    def predict_next_day(self, symbol: str, days_ahead: int = 1) -> Dict:
        """
        Bir sonraki gün fiyat tahmini
        
        Args:
            symbol: Hisse kodu (AAPL, TSLA, etc.)
            days_ahead: Kaç gün sonrası (1-7)
        
        Returns:
            Dict: Tahmin sonuçları
        """
        try:
            logger.info(f" Predicting {symbol} for {days_ahead} days ahead")
            
            df = self.data_client.fetch_stock_data(
                symbol,
                period="1y",   
                interval="1d"
            )
            
            # 2. Feature engineering
            df_features = self.feature_engineer.add_technical_indicators(df)
            df_features = df_features.dropna()
            
            if len(df_features) < self.sequence_length:
                raise ValueError(f"Not enough data. Need {self.sequence_length}, got {len(df_features)}")
            
            # 3. Son sequence'i al
            last_sequence = df_features.iloc[-self.sequence_length:]
            
            # 4. Target'ı ayır
            target_col = 'Close'
            current_price = float(df['Close'].iloc[-1])
            
            # 5. Feature columns'ı yükle
            import json
            feature_columns_path = 'models/artifacts/feature_columns.json'
            with open(feature_columns_path) as f:
                feature_columns = json.load(f)
            
            print(f" Model bekliyor: {len(feature_columns)} features")
            print(f" Feature columns: {feature_columns}")
            
            # 6. Target'ı çıkar
            features_df = last_sequence.drop([target_col], axis=1, errors='ignore')
            
            print(f" Mevcut features: {list(features_df.columns)}")
            print(f" Mevcut features sayısı: {len(features_df.columns)}")
            
            # 7. CRITICAL: Feature columns ile reindex et
            # Eksik kolonlar 0 ile doldurulur, fazla kolonlar atılır
            features_df = features_df.reindex(columns=feature_columns, fill_value=0.0)
            
            print(f" Reindex sonrası: {features_df.shape}")
            print(f" Final features: {list(features_df.columns)}")
            
            feature_data = features_df.values
            target_data = last_sequence[[target_col]].values
            
            # 8. Scale
            feature_scaled = self.model_loader.feature_scaler.transform(feature_data)
            target_scaled = self.model_loader.label_scaler.transform(target_data)
            
            # 9. Sequence oluştur
            X = np.array([feature_scaled])  # (1, 60, features)
            
            print(f" Input shape to model: {X.shape}")
            
            # 10. Tahmin yap
            prediction = self.model_loader.predict(X)
            predicted_price = float(prediction[0][0])
            
            # 11. Değişim hesapla
            price_change = predicted_price - current_price
            price_change_pct = (price_change / current_price) * 100
            
            # 12. Trend
            trend = "UP" if price_change > 0 else "DOWN" if price_change < 0 else "FLAT"
            
            result = {
                "symbol": symbol,
                "current_price": round(current_price, 2),
                "predicted_price": round(predicted_price, 2),
                "price_change": round(price_change, 2),
                "price_change_pct": round(price_change_pct, 2),
                "trend": trend,
                "prediction_date": (datetime.now() + timedelta(days=days_ahead)).strftime('%Y-%m-%d'),
                "confidence": "medium",
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f" Prediction complete: {symbol} ${predicted_price:.2f} ({price_change_pct:+.2f}%)")
            
            return result
            
        except Exception as e:
            logger.error(f" Prediction failed: {str(e)}")
            raise
    
    def get_model_status(self) -> Dict:
        """Model durumunu döndür"""
        return self.model_loader.get_model_info()


# Test
if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    service = PredictionService()
    
    # Test prediction
    symbols = ["AAPL", "MSFT", "GOOGL"]
    
    for symbol in symbols:
        try:
            print(f"\n{'='*60}")
            print(f"Testing: {symbol}")
            print('='*60)
            
            result = service.predict_next_day(symbol)
            
            print(f"\n Prediction Results:")
            print(f"  Symbol:           {result['symbol']}")
            print(f"  Current Price:    ${result['current_price']}")
            print(f"  Predicted Price:  ${result['predicted_price']}")
            print(f"  Change:           ${result['price_change']} ({result['price_change_pct']:+.2f}%)")
            print(f"  Trend:            {result['trend']}")
            print(f"  Prediction Date:  {result['prediction_date']}")
            
            break  # İlk başarılı tahmin sonrası dur
            
        except Exception as e:
            print(f" Failed: {str(e)}")
            import traceback
            traceback.print_exc()
            continue