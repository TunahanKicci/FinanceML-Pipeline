# data/sources/yahoo_finance.py
"""
Yahoo Finance veri çekme modülü
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional

class YahooFinanceClient:
    """Yahoo Finance API wrapper"""
    
    def __init__(self):
        self.cache = {}
    
    def fetch_stock_data(
        self,
        symbol: str,
        period: str = "2y",
        interval: str = "1d"
    ) -> pd.DataFrame:
        """
        Hisse senedi verilerini çek
        
        Args:
            symbol: Hisse kodu (örn: AAPL, TSLA)
            period: Zaman aralığı (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)
            interval: Veri aralığı (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
        
        Returns:
            DataFrame: OHLCV verileri
        """
        try:
            print(f"📊 Fetching data for {symbol}...")
            stock = yf.Ticker(symbol)
            df = stock.history(period=period, interval=interval)
            
            if df.empty:
                raise ValueError(f"No data found for {symbol}")
            
            print(f"✅ Downloaded {len(df)} records for {symbol}")
            print(f"📅 Date range: {df.index[0]} to {df.index[-1]}")
            
            return df
        
        except Exception as e:
            print(f"❌ Error fetching {symbol}: {str(e)}")
            raise
    
    def fetch_multiple_stocks(
        self,
        symbols: list,
        period: str = "2y"
    ) -> dict:
        """Birden fazla hisse senedi verisi çek"""
        data = {}
        for symbol in symbols:
            try:
                data[symbol] = self.fetch_stock_data(symbol, period)
            except Exception as e:
                print(f"⚠️ Skipping {symbol}: {str(e)}")
        return data


# Test fonksiyonu
if __name__ == "__main__":
    client = YahooFinanceClient()
    
    # Test: Apple hissesini çek
    df = client.fetch_stock_data("AAPL", period="1y")
    
    print("\n📊 Data Preview:")
    print(df.head())
    print(f"\n📈 Shape: {df.shape}")
    print(f"\n📋 Columns: {df.columns.tolist()}")