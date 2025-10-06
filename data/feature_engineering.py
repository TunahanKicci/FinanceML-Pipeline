# data/feature_engineering.py
"""
Teknik indikatörler ve feature engineering
"""
import pandas as pd
import numpy as np

class FeatureEngineer:
    """Teknik indikatör hesaplama ve feature engineering"""

    @staticmethod
    def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Ortalama ve momentum bazlı göstergeler
        df['SMA_5'] = df['Close'].rolling(window=5).mean()
        df['SMA_10'] = df['Close'].rolling(window=10).mean()
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

        # MACD
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']

        # RSI
        df['RSI'] = FeatureEngineer.calculate_rsi(df['Close'])

        # Bollinger Bands
        df['BB_Middle'] = df['Close'].rolling(window=20).mean()
        bb_std = df['Close'].rolling(window=20).std()
        df['BB_Upper'] = df['BB_Middle'] + 2 * bb_std
        df['BB_Lower'] = df['BB_Middle'] - 2 * bb_std
        df['BB_Width'] = df['BB_Upper'] - df['BB_Lower']

        # Hacim bazlı göstergeler
        df['Volume_SMA_20'] = df['Volume'].rolling(window=20).mean()
        df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_20']

        # Fiyat değişimleri
        df['Returns'] = df['Close'].pct_change()
        df['Log_Returns'] = np.log(df['Close'] / df['Close'].shift(1))
        df['Volatility'] = df['Returns'].rolling(window=20).std()

        # High-Low ilişkileri
        df['HL_Range'] = df['High'] - df['Low']
        df['HL_Pct'] = (df['High'] - df['Low']) / df['Close']
        df['Gap'] = df['Open'] - df['Close'].shift(1)

        # ATR
        df['ATR'] = FeatureEngineer.calculate_atr(df)

        # 🔹 EKLENEN ÖZEL FEATURE'LAR (Modelle tam uyumlu)
        # RSI değişim oranı
        df['RSI_change'] = df['RSI'].diff()

        # MACD farkı
        df['MACD_diff'] = df['MACD'] - df['MACD_Signal']

        # SMA oranı
        df['SMA_ratio'] = df['SMA_5'] / df['SMA_20']

        # Kısa ve uzun volatilite
        df['Volatility_5'] = df['Returns'].rolling(window=5).std()
        df['Volatility_20'] = df['Returns'].rolling(window=20).std()

        # Fiyatın Bollinger Band’ındaki konumu
        df['Price_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])

        # High-Low oranı
        df['HL_Ratio'] = df['High'] / df['Low']

        # Close-Open oranı
        df['CO_Ratio'] = df['Close'] / df['Open']

        # Gecikmeli getiriler
        df['Return_lag_1'] = df['Returns'].shift(1)
        df['Return_lag_2'] = df['Returns'].shift(2)

        # NaN temizliği (ilk 50 gün civarı boş olur)
        df = df.dropna().reset_index(drop=True)
        return df

    @staticmethod
    def calculate_rsi(prices: pd.Series, period: int = 14) -> pd.Series:
        delta = prices.diff()
        gain = delta.clip(lower=0)
        loss = -delta.clip(upper=0)
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        high_low = df['High'] - df['Low']
        high_close = np.abs(df['High'] - df['Close'].shift())
        low_close = np.abs(df['Low'] - df['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()

    @staticmethod
    def create_sequences(df: pd.DataFrame, sequence_length: int = 60, target_column: str = 'Close'):
        df = df.dropna().reset_index(drop=True)
        feature_cols = [c for c in df.columns if c != target_column]

        X, y = [], []
        for i in range(sequence_length, len(df)):
            seq = df[feature_cols].iloc[i-sequence_length:i].values
            target = df[target_column].iloc[i]
            X.append(seq)
            y.append(target)

        X, y = np.array(X), np.array(y)
        return X, y, feature_cols
