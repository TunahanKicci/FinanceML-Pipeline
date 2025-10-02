# data/processors/risk_analyzer.py
"""
Risk and Volatility Analysis
"""
import numpy as np
import pandas as pd
from scipy import stats
import yfinance as yf
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """Calculate risk metrics for stocks"""
    
    def __init__(self):
        pass
    
    def calculate_beta(self, stock_symbol: str, market_symbol: str = "^GSPC", period: str = "1y") -> float:
        """
        Calculate Beta coefficient (stock vs market correlation)
        
        Beta > 1: More volatile than market
        Beta = 1: Moves with market
        Beta < 1: Less volatile than market
        Beta < 0: Inverse correlation
        """
        try:
            # Fetch stock and market data
            stock = yf.Ticker(stock_symbol)
            market = yf.Ticker(market_symbol)
            
            stock_hist = stock.history(period=period)
            market_hist = market.history(period=period)
            
            if stock_hist.empty or market_hist.empty:
                return None
            
            # Calculate returns
            stock_returns = stock_hist['Close'].pct_change().dropna()
            market_returns = market_hist['Close'].pct_change().dropna()
            
            # Align dates
            df = pd.DataFrame({
                'stock': stock_returns,
                'market': market_returns
            }).dropna()
            
            if len(df) < 20:  # Need minimum data
                return None
            
            # Calculate covariance and variance
            covariance = np.cov(df['stock'], df['market'])[0][1]
            market_variance = np.var(df['market'])
            
            beta = covariance / market_variance if market_variance != 0 else None
            
            return float(beta) if beta is not None else None
            
        except Exception as e:
            logger.error(f"Error calculating beta: {e}")
            return None
    
    def calculate_volatility(self, symbol: str, period: str = "1y", window: int = 30) -> dict:
        """
        Calculate volatility metrics
        
        Returns:
            - Annual volatility (standard deviation of returns)
            - Rolling volatility
            - Historical volatility
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Daily returns
            returns = hist['Close'].pct_change().dropna()
            
            # Daily volatility
            daily_vol = float(returns.std())
            
            # Annualized volatility (252 trading days)
            annual_vol = daily_vol * np.sqrt(252)
            
            # Rolling volatility (last N days)
            rolling_vol = returns.rolling(window=window).std().iloc[-1]
            rolling_vol_annual = rolling_vol * np.sqrt(252)
            
            # Historical volatility ranges
            vol_30d = returns.tail(30).std() * np.sqrt(252)
            vol_90d = returns.tail(90).std() * np.sqrt(252)
            vol_180d = returns.tail(180).std() * np.sqrt(252)
            
            return {
                'daily_volatility': round(daily_vol, 6),
                'annual_volatility': round(annual_vol, 4),
                'volatility_30d': round(vol_30d, 4),
                'volatility_90d': round(vol_90d, 4),
                'volatility_180d': round(vol_180d, 4),
                'rolling_volatility': round(rolling_vol_annual, 4)
            }
            
        except Exception as e:
            logger.error(f"Error calculating volatility: {e}")
            return None
    
    def calculate_var(
        self, 
        symbol: str, 
        confidence_level: float = 0.95, 
        holding_period: int = 1,
        period: str = "1y"
    ) -> dict:
        """
        Calculate Value at Risk (VaR)
        
        VaR: Maximum expected loss over a time period at a given confidence level
        
        Args:
            confidence_level: 0.90, 0.95, or 0.99 (90%, 95%, 99%)
            holding_period: Days to hold position (typically 1)
            
        Returns:
            - Parametric VaR
            - Historical VaR
            - CVaR (Conditional VaR / Expected Shortfall)
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            # Get current price and calculate returns
            current_price = float(hist['Close'].iloc[-1])
            returns = hist['Close'].pct_change().dropna()
            
            if len(returns) < 20:
                return None
            
            # 1. Parametric VaR (assumes normal distribution)
            mean_return = returns.mean()
            std_return = returns.std()
            
            # Z-score for confidence level
            z_score = stats.norm.ppf(1 - confidence_level)
            
            # VaR calculation
            var_parametric = -(mean_return + z_score * std_return) * current_price * np.sqrt(holding_period)
            
            # 2. Historical VaR (uses actual historical distribution)
            var_historical = -np.percentile(returns, (1 - confidence_level) * 100) * current_price * np.sqrt(holding_period)
            
            # 3. CVaR (Conditional VaR / Expected Shortfall)
            # Average loss beyond VaR threshold
            threshold = np.percentile(returns, (1 - confidence_level) * 100)
            tail_losses = returns[returns <= threshold]
            cvar = -tail_losses.mean() * current_price * np.sqrt(holding_period) if len(tail_losses) > 0 else var_historical
            
            return {
                'current_price': round(current_price, 2),
                'confidence_level': confidence_level,
                'holding_period_days': holding_period,
                'var_parametric': round(var_parametric, 2),
                'var_historical': round(var_historical, 2),
                'cvar': round(cvar, 2),
                'var_percentage': round((var_parametric / current_price) * 100, 2),
                'interpretation': f"With {confidence_level*100}% confidence, maximum loss in {holding_period} day(s) should not exceed ${abs(var_parametric):.2f}"
            }
            
        except Exception as e:
            logger.error(f"Error calculating VaR: {e}")
            return None
    
    def calculate_sharpe_ratio(self, symbol: str, period: str = "1y", risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio (risk-adjusted return)
        
        Sharpe > 1: Good
        Sharpe > 2: Very good
        Sharpe > 3: Excellent
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            returns = hist['Close'].pct_change().dropna()
            
            # Annualized return
            annual_return = returns.mean() * 252
            
            # Annualized volatility
            annual_vol = returns.std() * np.sqrt(252)
            
            # Sharpe ratio
            sharpe = (annual_return - risk_free_rate) / annual_vol if annual_vol != 0 else None
            
            return float(sharpe) if sharpe is not None else None
            
        except Exception as e:
            logger.error(f"Error calculating Sharpe ratio: {e}")
            return None
    
    def calculate_max_drawdown(self, symbol: str, period: str = "1y") -> dict:
        """
        Calculate Maximum Drawdown (largest peak-to-trough decline)
        """
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return None
            
            prices = hist['Close']
            
            # Calculate running maximum
            running_max = prices.expanding().max()
            
            # Calculate drawdown
            drawdown = (prices - running_max) / running_max
            
            # Max drawdown
            max_dd = drawdown.min()
            max_dd_date = drawdown.idxmin()
            
            # Find peak before max drawdown
            peak_price = running_max.loc[max_dd_date]
            trough_price = prices.loc[max_dd_date]
            
            return {
                'max_drawdown': round(max_dd, 4),
                'max_drawdown_pct': round(max_dd * 100, 2),
                'peak_price': round(peak_price, 2),
                'trough_price': round(trough_price, 2),
                'drawdown_date': max_dd_date.strftime('%Y-%m-%d'),
                'recovery_status': 'Recovered' if prices.iloc[-1] >= peak_price else 'Not Recovered'
            }
            
        except Exception as e:
            logger.error(f"Error calculating max drawdown: {e}")
            return None
    
    def analyze_risk(self, symbol: str) -> dict:
        """
        Comprehensive risk analysis
        """
        try:
            logger.info(f"Analyzing risk for {symbol}")
            
            # Calculate all metrics
            beta = self.calculate_beta(symbol)
            volatility = self.calculate_volatility(symbol)
            var_95 = self.calculate_var(symbol, confidence_level=0.95)
            var_99 = self.calculate_var(symbol, confidence_level=0.99)
            sharpe = self.calculate_sharpe_ratio(symbol)
            max_dd = self.calculate_max_drawdown(symbol)
            
            # Risk rating
            risk_score = 0
            risk_factors = []
            
            # Beta assessment
            if beta is not None:
                if beta > 1.5:
                    risk_score += 30
                    risk_factors.append("High market sensitivity")
                elif beta > 1.2:
                    risk_score += 20
                    risk_factors.append("Above-average volatility")
                elif beta < 0.8:
                    risk_score -= 10
                    risk_factors.append("Low market correlation")
            
            # Volatility assessment
            if volatility:
                vol = volatility['annual_volatility']
                if vol > 0.40:
                    risk_score += 30
                    risk_factors.append("Very high volatility")
                elif vol > 0.25:
                    risk_score += 20
                    risk_factors.append("High volatility")
                elif vol < 0.15:
                    risk_score -= 10
                    risk_factors.append("Low volatility")
            
            # Sharpe ratio assessment
            if sharpe is not None:
                if sharpe < 0:
                    risk_score += 20
                    risk_factors.append("Negative risk-adjusted returns")
                elif sharpe > 2:
                    risk_score -= 20
                    risk_factors.append("Excellent risk-adjusted returns")
            
            # Max drawdown assessment
            if max_dd:
                dd_pct = abs(max_dd['max_drawdown_pct'])
                if dd_pct > 50:
                    risk_score += 30
                    risk_factors.append("Severe historical drawdown")
                elif dd_pct > 30:
                    risk_score += 20
                    risk_factors.append("Significant historical drawdown")
            
            # Risk rating
            if risk_score > 50:
                risk_rating = "Very High Risk"
                risk_color = "#dc2626"
            elif risk_score > 30:
                risk_rating = "High Risk"
                risk_color = "#f59e0b"
            elif risk_score > 10:
                risk_rating = "Moderate Risk"
                risk_color = "#3b82f6"
            elif risk_score > -10:
                risk_rating = "Low Risk"
                risk_color = "#10b981"
            else:
                risk_rating = "Very Low Risk"
                risk_color = "#059669"
            
            result = {
                'symbol': symbol,
                'analysis_date': datetime.now().isoformat(),
                'risk_rating': risk_rating,
                'risk_score': risk_score,
                'risk_color': risk_color,
                'risk_factors': risk_factors,
                'beta': round(beta, 3) if beta is not None else None,
                'volatility': volatility,
                'var_95': var_95,
                'var_99': var_99,
                'sharpe_ratio': round(sharpe, 3) if sharpe is not None else None,
                'max_drawdown': max_dd
            }
            
            logger.info(f"Risk analysis complete: {risk_rating}")
            
            return result
            
        except Exception as e:
            logger.error(f"Risk analysis failed: {e}")
            raise


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = RiskAnalyzer()
    result = analyzer.analyze_risk("AAPL")
    
    print("\n" + "="*60)
    print("RISK ANALYSIS")
    print("="*60)
    print(f"Symbol: {result['symbol']}")
    print(f"Risk Rating: {result['risk_rating']}")
    print(f"Risk Score: {result['risk_score']}")
    print(f"\nBeta: {result['beta']}")
    print(f"Annual Volatility: {result['volatility']['annual_volatility']}")
    print(f"Sharpe Ratio: {result['sharpe_ratio']}")
    print(f"\nVaR (95%): ${result['var_95']['var_parametric']}")
    print(f"CVaR (95%): ${result['var_95']['cvar']}")
    print(f"\nMax Drawdown: {result['max_drawdown']['max_drawdown_pct']}%")