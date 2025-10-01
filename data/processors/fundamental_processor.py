# data/processors/fundamental_processor.py
"""
Process fundamental financial data for ML training
"""
import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class FundamentalProcessor:
    """Process and merge fundamental data with price data"""
    
    def __init__(self):
        pass
    
    def fetch_and_merge_fundamentals(self, symbol: str, price_df: pd.DataFrame) -> pd.DataFrame:
        """
        Fetch fundamental data and merge with price data
        
        Args:
            symbol: Stock symbol
            price_df: DataFrame with OHLCV data (index: date)
        
        Returns:
            DataFrame with price + fundamental features
        """
        try:
            logger.info(f"Fetching fundamental data for {symbol}")
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Get quarterly financials
            quarterly_financials = ticker.quarterly_financials
            quarterly_balance = ticker.quarterly_balance_sheet
            quarterly_cashflow = ticker.quarterly_cashflow
            
            # Extract key metrics (will be same for all days until next quarter)
            fundamental_features = {
                # Valuation
                'PE_Ratio': info.get('trailingPE', np.nan),
                'Forward_PE': info.get('forwardPE', np.nan),
                'PEG_Ratio': info.get('pegRatio', np.nan),
                'Price_to_Book': info.get('priceToBook', np.nan),
                'Price_to_Sales': info.get('priceToSalesTrailing12Months', np.nan),
                'EV_to_Revenue': info.get('enterpriseToRevenue', np.nan),
                'EV_to_EBITDA': info.get('enterpriseToEbitda', np.nan),
                
                # Profitability
                'Profit_Margin': info.get('profitMargins', np.nan),
                'Operating_Margin': info.get('operatingMargins', np.nan),
                'Gross_Margin': info.get('grossMargins', np.nan),
                'ROE': info.get('returnOnEquity', np.nan),
                'ROA': info.get('returnOnAssets', np.nan),
                
                # Financial Health
                'Current_Ratio': info.get('currentRatio', np.nan),
                'Quick_Ratio': info.get('quickRatio', np.nan),
                'Debt_to_Equity': info.get('debtToEquity', np.nan),
                
                # Growth
                'Revenue_Growth': info.get('revenueGrowth', np.nan),
                'Earnings_Growth': info.get('earningsGrowth', np.nan),
                
                # Per Share
                'EPS': info.get('trailingEps', np.nan),
                'Book_Value_Per_Share': info.get('bookValue', np.nan),
                
                # Dividend
                'Dividend_Yield': info.get('dividendYield', np.nan),
                'Payout_Ratio': info.get('payoutRatio', np.nan),
            }
            
            # Create DataFrame with fundamental features
            df_with_fundamentals = price_df.copy()
            
            # Add fundamental columns (will be constant across all rows)
            for key, value in fundamental_features.items():
                df_with_fundamentals[key] = value
            
            # Process quarterly data if available
            if not quarterly_balance.empty:
                df_with_fundamentals = self._add_quarterly_metrics(
                    df_with_fundamentals, 
                    quarterly_balance,
                    quarterly_financials,
                    quarterly_cashflow
                )
            
            # Forward fill NaN values (fundamentals don't change daily)
            df_with_fundamentals = df_with_fundamentals.fillna(method='ffill')
            
            logger.info(f"Added {len(fundamental_features)} fundamental features")
            
            return df_with_fundamentals
            
        except Exception as e:
            logger.warning(f"Could not fetch fundamentals for {symbol}: {e}")
            # Return original dataframe if fundamentals fail
            return price_df
    
    def _add_quarterly_metrics(self, df, balance_sheet, financials, cashflow):
        """Add quarterly fundamental metrics"""
        
        # Get latest quarter data
        if not balance_sheet.empty:
            latest_quarter = balance_sheet.columns[0]
            
            # Balance sheet items
            total_assets = balance_sheet.loc['Total Assets', latest_quarter] if 'Total Assets' in balance_sheet.index else np.nan
            total_liabilities = balance_sheet.loc['Total Liabilities Net Minority Interest', latest_quarter] if 'Total Liabilities Net Minority Interest' in balance_sheet.index else np.nan
            stockholders_equity = balance_sheet.loc['Stockholders Equity', latest_quarter] if 'Stockholders Equity' in balance_sheet.index else np.nan
            total_debt = balance_sheet.loc['Total Debt', latest_quarter] if 'Total Debt' in balance_sheet.index else np.nan
            cash = balance_sheet.loc['Cash And Cash Equivalents', latest_quarter] if 'Cash And Cash Equivalents' in balance_sheet.index else np.nan
            
            df['Total_Assets'] = total_assets
            df['Total_Liabilities'] = total_liabilities
            df['Stockholders_Equity'] = stockholders_equity
            df['Total_Debt'] = total_debt
            df['Cash'] = cash
            
            # Calculate derived metrics
            if not np.isnan(total_assets) and not np.isnan(total_liabilities):
                df['Assets_to_Liabilities'] = total_assets / (total_liabilities + 1e-9)
            
            if not np.isnan(total_debt) and not np.isnan(stockholders_equity):
                df['Debt_to_Equity_Calc'] = total_debt / (stockholders_equity + 1e-9)
        
        if not financials.empty:
            latest_quarter = financials.columns[0]
            
            total_revenue = financials.loc['Total Revenue', latest_quarter] if 'Total Revenue' in financials.index else np.nan
            gross_profit = financials.loc['Gross Profit', latest_quarter] if 'Gross Profit' in financials.index else np.nan
            operating_income = financials.loc['Operating Income', latest_quarter] if 'Operating Income' in financials.index else np.nan
            net_income = financials.loc['Net Income', latest_quarter] if 'Net Income' in financials.index else np.nan
            
            df['Total_Revenue'] = total_revenue
            df['Gross_Profit'] = gross_profit
            df['Operating_Income'] = operating_income
            df['Net_Income'] = net_income
            
            # Margins
            if not np.isnan(total_revenue) and total_revenue > 0:
                if not np.isnan(gross_profit):
                    df['Gross_Margin_Calc'] = gross_profit / total_revenue
                if not np.isnan(operating_income):
                    df['Operating_Margin_Calc'] = operating_income / total_revenue
                if not np.isnan(net_income):
                    df['Net_Margin_Calc'] = net_income / total_revenue
        
        if not cashflow.empty:
            latest_quarter = cashflow.columns[0]
            
            operating_cf = cashflow.loc['Operating Cash Flow', latest_quarter] if 'Operating Cash Flow' in cashflow.index else np.nan
            free_cf = cashflow.loc['Free Cash Flow', latest_quarter] if 'Free Cash Flow' in cashflow.index else np.nan
            
            df['Operating_Cashflow'] = operating_cf
            df['Free_Cashflow'] = free_cf
        
        return df


# Test
if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    from data.sources.yahoo_finance import YahooFinanceClient
    
    logging.basicConfig(level=logging.INFO)
    
    # Fetch price data
    client = YahooFinanceClient()
    df_price = client.fetch_stock_data("AAPL", period="1y")
    
    print(f"\nOriginal columns: {len(df_price.columns)}")
    print(df_price.columns.tolist())
    
    # Add fundamentals
    processor = FundamentalProcessor()
    df_enhanced = processor.fetch_and_merge_fundamentals("AAPL", df_price)
    
    print(f"\nEnhanced columns: {len(df_enhanced.columns)}")
    print(df_enhanced.columns.tolist())
    
    print(f"\nSample data:")
    print(df_enhanced[['Close', 'PE_Ratio', 'ROE', 'Debt_to_Equity']].tail())