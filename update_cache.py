#!/usr/bin/env python3
"""
Update Cache Script
Bu script local olarak çalıştırılır ve tüm cache dosyalarını günceller.
Docker container'da yfinance API çağrısı yapmak yerine bu script kullanılır.
"""

import yfinance as yf
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import logging

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CacheUpdater:
    def __init__(self):
        self.cache_dir = "data/cache"
        self.fundamentals_cache_dir = "data/cache/fundamentals"
        os.makedirs(self.cache_dir, exist_ok=True)
        os.makedirs(self.fundamentals_cache_dir, exist_ok=True)
        
        # Stock symbols to update
        self.symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 
            'META', 'NVDA', 'JPM', 'V', 'WMT'
        ]
        
        # Market index
        self.market_symbols = ['^GSPC']
        
    def update_price_data(self, symbol: str, period: str = "2y", interval: str = "1d"):
        """Update price data cache"""
        try:
            logger.info(f"📊 Updating price data for {symbol}...")
            
            # Rate limiting
            time.sleep(random.uniform(2, 5))
            
            # Fetch data
            df = yf.download(symbol, period=period, interval=interval, 
                           threads=False, progress=False)
            
            if df.empty:
                logger.error(f"❌ No price data received for {symbol}")
                return False
            
            # Flatten multi-level columns if exists (for single symbol)
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = df.columns.get_level_values(0)
            
            # Save to cache
            cache_file = os.path.join(self.cache_dir, f"{symbol}_{period}_{interval}.csv")
            df.to_csv(cache_file)
            
            logger.info(f"✅ Price data cached for {symbol}: {len(df)} records")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update price data for {symbol}: {e}")
            return False
    
    def update_fundamental_data(self, symbol: str):
        """Update fundamental data cache"""
        try:
            logger.info(f"📈 Updating fundamental data for {symbol}...")
            
            # Rate limiting - more aggressive for fundamentals
            time.sleep(random.uniform(5, 10))
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            if not info or len(info) < 10:
                logger.warning(f"⚠️ Limited fundamental data for {symbol}")
                return False
            
            # Extract fundamental metrics
            fundamental_features = {
                # Valuation
                'PE_Ratio': info.get('trailingPE'),
                'Forward_PE': info.get('forwardPE'),
                'PEG_Ratio': info.get('pegRatio'),
                'Price_to_Book': info.get('priceToBook'),
                'Price_to_Sales': info.get('priceToSalesTrailing12Months'),
                'EV_to_Revenue': info.get('enterpriseToRevenue'),
                'EV_to_EBITDA': info.get('enterpriseToEbitda'),
                
                # Profitability
                'Profit_Margin': info.get('profitMargins'),
                'Operating_Margin': info.get('operatingMargins'),
                'Gross_Margin': info.get('grossMargins'),
                'ROE': info.get('returnOnEquity'),
                'ROA': info.get('returnOnAssets'),
                
                # Financial Health
                'Current_Ratio': info.get('currentRatio'),
                'Quick_Ratio': info.get('quickRatio'),
                'Debt_to_Equity': info.get('debtToEquity'),
                
                # Growth
                'Revenue_Growth': info.get('revenueGrowth'),
                'Earnings_Growth': info.get('earningsGrowth'),
                
                # Per Share
                'EPS': info.get('trailingEps'),
                'Book_Value_Per_Share': info.get('bookValue'),
                
                # Dividend
                'Dividend_Yield': info.get('dividendYield'),
                'Payout_Ratio': info.get('payoutRatio'),
                
                # Additional Info
                'Market_Cap': info.get('marketCap'),
                'Enterprise_Value': info.get('enterpriseValue'),
                'Total_Debt': info.get('totalDebt'),
                'Free_Cashflow': info.get('freeCashflow'),
                'Sector': info.get('sector'),
                'Industry': info.get('industry'),
                'Company_Name': info.get('shortName', symbol)
            }
            
            # Convert None to null for JSON serialization
            for key, value in fundamental_features.items():
                if value is None or (isinstance(value, float) and pd.isna(value)):
                    fundamental_features[key] = None
            
            # Save to cache
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'fundamentals': fundamental_features
            }
            
            cache_file = os.path.join(self.fundamentals_cache_dir, f"{symbol}_fundamentals.json")
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            # Count non-null values
            non_null_count = sum(1 for v in fundamental_features.values() if v is not None)
            logger.info(f"✅ Fundamental data cached for {symbol}: {non_null_count}/25 metrics")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to update fundamental data for {symbol}: {e}")
            return False
    
    def update_all_price_data(self):
        """Update price data for all symbols"""
        logger.info("🚀 Starting price data update for all symbols...")
        
        all_symbols = self.symbols + self.market_symbols
        successful = 0
        
        for symbol in all_symbols:
            if self.update_price_data(symbol):
                successful += 1
            
            # Progress update
            logger.info(f"📊 Progress: {successful}/{len(all_symbols)} symbols updated")
        
        logger.info(f"✅ Price data update complete: {successful}/{len(all_symbols)} successful")
    
    def update_all_fundamental_data(self):
        """Update fundamental data for all symbols"""
        logger.info("📈 Starting fundamental data update for all symbols...")
        
        successful = 0
        
        for symbol in self.symbols:
            if self.update_fundamental_data(symbol):
                successful += 1
            
            # Progress update
            logger.info(f"📈 Progress: {successful}/{len(self.symbols)} symbols updated")
        
        logger.info(f"✅ Fundamental data update complete: {successful}/{len(self.symbols)} successful")
    
    def update_all(self):
        """Update both price and fundamental data"""
        logger.info("🔄 Starting complete cache update...")
        
        print("=" * 60)
        print("📊 FINANCEML CACHE UPDATER")
        print("=" * 60)
        print(f"Updating data for symbols: {', '.join(self.symbols)}")
        print(f"Market indices: {', '.join(self.market_symbols)}")
        print("=" * 60)
        
        # Update price data first
        self.update_all_price_data()
        
        print()
        print("-" * 60)
        
        # Update fundamental data
        self.update_all_fundamental_data()
        
        print()
        print("=" * 60)
        print("✅ CACHE UPDATE COMPLETE!")
        print("=" * 60)
        print("🐳 You can now start Docker containers with fresh data:")
        print("   docker compose up -d")
        print("=" * 60)

def main():
    """Main function"""
    try:
        updater = CacheUpdater()
        updater.update_all()
        
    except KeyboardInterrupt:
        print("\n⚠️ Update cancelled by user")
    except Exception as e:
        logger.error(f"❌ Update failed: {e}")
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()