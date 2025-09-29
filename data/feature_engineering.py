# data/feature_engineering.py
"""
Teknik indikatörler ve feature engineering
"""
import pandas as pd
import numpy as np
from typing import Optional

class FeatureEngineer:
    """Teknik indikatör hesaplama"""
    
    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        OHLCV verisine teknik indikatörler ekle
        
        Returns:
            DataFrame: Zenginleştirilmiş veri
        """
        df = df.copy()
        
        # 1. Moving Averages
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()
        
        # 2. MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # 3. RSI (Relative Strength Index)
        df['RSI'] = FeatureEngineer.calculate_rsi(df['Close'], period=14)
        
        # 4. Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
        df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']
        
        # 5. Volume indicators
        df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_20']
        
        # 6. Price changes
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        
        # 7. Volatility
        df['Volatility'] = df['Returns'].rolling(window=20).std()
        
        # 8. High-Low Range
        df['HL_Range'] = df['High'] - df['Low']
        df['HL_Pct'] = (df['High'] - df['Low']) / df['Close']
        
        # 9. Gap
        df['Gap'] = df['Open'] - df['Close'].shift(1)
        
        # 10. ATR (Average True Range)
        df['ATR'] = FeatureEngineer.calculate_atr(df, period=14)
        
        return df
    
    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        """RSI hesapla"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Average True Range hesapla"""
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(window=period).mean()
        
        return atr
    
    @staticmethod
    def create_sequences(
        df: pd.DataFrame,
        sequence_length: int = 60,
        target_column: str = 'Close'
    ) -> tuple:
        """
        LSTM için sequence oluştur
        
        Args:
            df: Feature'lı DataFrame
            sequence_length: Kaç günlük pencere
            target_column: Tahmin edilecek sütun
        
        Returns:
            X, y: (samples, sequence_length, features), (samples,)
        """
        # NaN değerleri temizle
        df = df.dropna()
        
        # Target column'u ayır
        target_idx = df.columns.tolist().index(target_column)
        
        X, y = [], []
        
        for i in range(sequence_length, len(df)):
            X.append(df.iloc[i-sequence_length:i].values)
            y.append(df.iloc[i][target_column])
        
        return np.array(X), np.array(y)


# Test fonksiyonu
if __name__ == "__main__":
    from data.sources.yahoo_finance import YahooFinanceClient
    
    # Veri çek
    client = YahooFinanceClient()
    df = client.fetch_stock_data("AAPL", period="1y")
    
    # Feature'ları ekle
    engineer = FeatureEngineer()
    df_features = engineer.add_technical_indicators(df)
    
    print("\n📊 Features Added:")
    print(f"Original columns: {len(df.columns)}")
    print(f"After features: {len(df_features.columns)}")
    print(f"\n📋 New columns:")
    print(df_features.columns.tolist())
    
    print("\n📈 Sample data:")
    print(df_features.tail())
    
    # Sequence oluştur
    X, y = engineer.create_sequences(df_features, sequence_length=60)
    print(f"\n🔢 Sequences created:")
    print(f"X shape: {X.shape}")  # (samples, 60, features)
    print(f"y shape: {y.shape}")  # (samples,)