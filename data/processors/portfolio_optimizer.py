"""
Modern Portfolio Theory (Markowitz) - Portfolio Optimization
"""
import numpy as np
import pandas as pd
from scipy.optimize import minimize
from typing import Dict, List, Tuple, Optional
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class PortfolioOptimizer:
    """Markowitz Modern Portfolio Theory implementation"""
    
    def __init__(self, risk_free_rate: float = 0.02, cache_dir: Optional[str] = None):
        """
        Args:
            risk_free_rate: Annual risk-free rate (default: 2%)
            cache_dir: Directory to load cached CSV files from
        """
        self.risk_free_rate = risk_free_rate
        self.cache_dir = Path(cache_dir) if cache_dir else None
        self.returns_data = None
        self.mean_returns = None
        self.cov_matrix = None
        self.symbols = None
    
    def fetch_data(self, symbols: List[str], period: str = "2y") -> pd.DataFrame:
        """
        Load historical price data from cache for multiple stocks
        
        Args:
            symbols: List of stock symbols
            period: Historical period (ignored, using cached 2y data)
        
        Returns:
            DataFrame with close prices
        """
        try:
            logger.info(f"Loading cached data for {len(symbols)} symbols: {symbols}")
            
            if not self.cache_dir:
                raise ValueError("cache_dir not configured")
            
            all_prices = {}
            
            for symbol in symbols:
                cache_file = self.cache_dir / f"{symbol}_2y_1d.csv"
                
                if not cache_file.exists():
                    logger.warning(f"Cache file not found for {symbol}: {cache_file}")
                    continue
                
                df = pd.read_csv(cache_file, parse_dates=['Date'], index_col='Date')
                
                if 'Close' not in df.columns:
                    logger.warning(f"Close column not found in {cache_file}")
                    continue
                
                all_prices[symbol] = df['Close']
            
            if not all_prices:
                raise ValueError("No valid price data found in cache")
            
            # Combine all prices into a single DataFrame
            prices = pd.DataFrame(all_prices)
            prices = prices.dropna()
            
            if prices.empty:
                raise ValueError("No valid price data after removing NaN values")
            
            logger.info(f"Loaded {len(prices)} days of cached data for {len(all_prices)} symbols")
            return prices
            
        except Exception as e:
            logger.error(f"Error loading cached data: {e}")
            raise
    
    def calculate_returns(self, prices: pd.DataFrame) -> pd.DataFrame:
        """Calculate daily returns"""
        returns = prices.pct_change().dropna()
        return returns
    
    def prepare_data(self, symbols: List[str], period: str = "2y"):
        """
        Prepare portfolio data
        
        Args:
            symbols: List of stock symbols
            period: Historical period
        """
        prices = self.fetch_data(symbols, period)
        self.returns_data = self.calculate_returns(prices)
        self.symbols = symbols
        
        # Calculate mean returns (annualized)
        self.mean_returns = self.returns_data.mean() * 252
        
        # Calculate covariance matrix (annualized)
        self.cov_matrix = self.returns_data.cov() * 252
        
        logger.info("Data preparation complete")
    
    def portfolio_stats(self, weights: np.ndarray) -> Tuple[float, float, float]:
        """
        Calculate portfolio statistics
        
        Args:
            weights: Portfolio weights
        
        Returns:
            (return, volatility, sharpe_ratio)
        """
        portfolio_return = np.sum(self.mean_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_std
        
        return portfolio_return, portfolio_std, sharpe_ratio
    
    def negative_sharpe(self, weights: np.ndarray) -> float:
        """Negative Sharpe ratio for minimization"""
        return -self.portfolio_stats(weights)[2]
    
    def portfolio_volatility(self, weights: np.ndarray) -> float:
        """Portfolio volatility for minimization"""
        return self.portfolio_stats(weights)[1]
    
    def optimize_sharpe_ratio(
        self, 
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Find portfolio with maximum Sharpe ratio
        
        Args:
            constraints: Optional constraints dict with 'min_weight' and 'max_weight'
        
        Returns:
            Optimization result dictionary
        """
        try:
            n_assets = len(self.symbols)
            
            # Initial guess (equal weights)
            init_weights = np.array([1/n_assets] * n_assets)
            
            # Constraints
            if constraints is None:
                constraints = {}
            
            bounds = tuple(
                (constraints.get('min_weight', 0.0), constraints.get('max_weight', 1.0))
                for _ in range(n_assets)
            )
            
            # Weights must sum to 1
            constraints_opt = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
            
            # Optimize
            result = minimize(
                self.negative_sharpe,
                init_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_opt
            )
            
            if not result.success:
                raise ValueError(f"Optimization failed: {result.message}")
            
            optimal_weights = result.x
            ret, vol, sharpe = self.portfolio_stats(optimal_weights)
            
            return {
                'type': 'max_sharpe',
                'weights': {symbol: float(w) for symbol, w in zip(self.symbols, optimal_weights)},
                'expected_return': float(ret),
                'volatility': float(vol),
                'sharpe_ratio': float(sharpe),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Sharpe optimization failed: {e}")
            raise
    
    def optimize_min_variance(
        self, 
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Find minimum variance portfolio
        
        Args:
            constraints: Optional constraints dict
        
        Returns:
            Optimization result dictionary
        """
        try:
            n_assets = len(self.symbols)
            init_weights = np.array([1/n_assets] * n_assets)
            
            if constraints is None:
                constraints = {}
            
            bounds = tuple(
                (constraints.get('min_weight', 0.0), constraints.get('max_weight', 1.0))
                for _ in range(n_assets)
            )
            
            constraints_opt = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
            
            result = minimize(
                self.portfolio_volatility,
                init_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_opt
            )
            
            if not result.success:
                raise ValueError(f"Optimization failed: {result.message}")
            
            optimal_weights = result.x
            ret, vol, sharpe = self.portfolio_stats(optimal_weights)
            
            return {
                'type': 'min_variance',
                'weights': {symbol: float(w) for symbol, w in zip(self.symbols, optimal_weights)},
                'expected_return': float(ret),
                'volatility': float(vol),
                'sharpe_ratio': float(sharpe),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Min variance optimization failed: {e}")
            raise
    
    def optimize_target_return(
        self, 
        target_return: float,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Find minimum variance portfolio for a target return
        
        Args:
            target_return: Target annual return (e.g., 0.15 for 15%)
            constraints: Optional constraints
        
        Returns:
            Optimization result dictionary
        """
        try:
            n_assets = len(self.symbols)
            init_weights = np.array([1/n_assets] * n_assets)
            
            if constraints is None:
                constraints = {}
            
            bounds = tuple(
                (constraints.get('min_weight', 0.0), constraints.get('max_weight', 1.0))
                for _ in range(n_assets)
            )
            
            # Two constraints: weights sum to 1 AND return = target
            constraints_opt = [
                {'type': 'eq', 'fun': lambda x: np.sum(x) - 1},
                {'type': 'eq', 'fun': lambda x: np.sum(self.mean_returns * x) - target_return}
            ]
            
            result = minimize(
                self.portfolio_volatility,
                init_weights,
                method='SLSQP',
                bounds=bounds,
                constraints=constraints_opt
            )
            
            if not result.success:
                logger.warning(f"Target return optimization: {result.message}")
                return None
            
            optimal_weights = result.x
            ret, vol, sharpe = self.portfolio_stats(optimal_weights)
            
            return {
                'type': 'target_return',
                'target_return': float(target_return),
                'weights': {symbol: float(w) for symbol, w in zip(self.symbols, optimal_weights)},
                'expected_return': float(ret),
                'volatility': float(vol),
                'sharpe_ratio': float(sharpe),
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Target return optimization failed: {e}")
            return None
    
    def calculate_efficient_frontier(
        self, 
        num_portfolios: int = 50,
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Calculate the efficient frontier
        
        Args:
            num_portfolios: Number of portfolios to generate
            constraints: Optional constraints
        
        Returns:
            Dictionary with efficient frontier data
        """
        try:
            logger.info(f"Calculating efficient frontier with {num_portfolios} portfolios")
            
            # Get min and max returns
            min_var_portfolio = self.optimize_min_variance(constraints)
            max_sharpe_portfolio = self.optimize_sharpe_ratio(constraints)
            
            min_return = min_var_portfolio['expected_return']
            max_return = max(self.mean_returns)
            
            # Generate target returns
            target_returns = np.linspace(min_return, max_return, num_portfolios)
            
            frontier_returns = []
            frontier_volatilities = []
            frontier_sharpe = []
            frontier_weights = []
            
            for target_ret in target_returns:
                result = self.optimize_target_return(target_ret, constraints)
                if result and result['success']:
                    frontier_returns.append(result['expected_return'])
                    frontier_volatilities.append(result['volatility'])
                    frontier_sharpe.append(result['sharpe_ratio'])
                    frontier_weights.append(result['weights'])
            
            return {
                'returns': frontier_returns,
                'volatilities': frontier_volatilities,
                'sharpe_ratios': frontier_sharpe,
                'weights': frontier_weights,
                'min_variance_portfolio': min_var_portfolio,
                'max_sharpe_portfolio': max_sharpe_portfolio,
                'num_points': len(frontier_returns)
            }
            
        except Exception as e:
            logger.error(f"Efficient frontier calculation failed: {e}")
            raise
    
    def monte_carlo_simulation(
        self, 
        num_portfolios: int = 10000
    ) -> Dict:
        """
        Generate random portfolios using Monte Carlo simulation
        
        Args:
            num_portfolios: Number of random portfolios
        
        Returns:
            Dictionary with simulation results
        """
        try:
            logger.info(f"Running Monte Carlo with {num_portfolios} portfolios")
            
            n_assets = len(self.symbols)
            results = np.zeros((3, num_portfolios))
            weights_record = []
            
            for i in range(num_portfolios):
                # Random weights
                weights = np.random.random(n_assets)
                weights /= np.sum(weights)
                
                ret, vol, sharpe = self.portfolio_stats(weights)
                
                results[0, i] = ret
                results[1, i] = vol
                results[2, i] = sharpe
                weights_record.append(weights)
            
            return {
                'returns': results[0].tolist(),
                'volatilities': results[1].tolist(),
                'sharpe_ratios': results[2].tolist(),
                'weights': weights_record,
                'num_portfolios': num_portfolios
            }
            
        except Exception as e:
            logger.error(f"Monte Carlo simulation failed: {e}")
            raise
    
    def get_correlation_matrix(self) -> Dict:
        """
        Calculate correlation matrix
        
        Returns:
            Correlation matrix as dictionary
        """
        corr_matrix = self.returns_data.corr()
        
        return {
            'symbols': self.symbols,
            'matrix': corr_matrix.values.tolist()
        }
    
    def analyze_portfolio(
        self, 
        symbols: List[str], 
        period: str = "2y",
        constraints: Optional[Dict] = None
    ) -> Dict:
        """
        Complete portfolio analysis
        
        Args:
            symbols: List of stock symbols
            period: Historical period
            constraints: Optional constraints
        
        Returns:
            Complete analysis results
        """
        try:
            # Prepare data
            self.prepare_data(symbols, period)
            
            # Optimize portfolios
            max_sharpe = self.optimize_sharpe_ratio(constraints)
            min_variance = self.optimize_min_variance(constraints)
            
            # Calculate efficient frontier
            efficient_frontier = self.calculate_efficient_frontier(50, constraints)
            
            # Correlation matrix
            correlation = self.get_correlation_matrix()
            
            # Individual asset stats
            asset_stats = []
            for symbol in symbols:
                idx = self.symbols.index(symbol)
                asset_stats.append({
                    'symbol': symbol,
                    'expected_return': float(self.mean_returns[idx]),
                    'volatility': float(np.sqrt(self.cov_matrix.iloc[idx, idx])),
                    'sharpe_ratio': float((self.mean_returns[idx] - self.risk_free_rate) / np.sqrt(self.cov_matrix.iloc[idx, idx]))
                })
            
            result = {
                'symbols': symbols,
                'analysis_date': datetime.now().isoformat(),
                'period': period,
                'risk_free_rate': self.risk_free_rate,
                'max_sharpe_portfolio': max_sharpe,
                'min_variance_portfolio': min_variance,
                'efficient_frontier': efficient_frontier,
                'correlation_matrix': correlation,
                'asset_statistics': asset_stats,
                'data_points': len(self.returns_data)
            }
            
            logger.info("Portfolio analysis complete")
            return result
            
        except Exception as e:
            logger.error(f"Portfolio analysis failed: {e}")
            raise


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    optimizer = PortfolioOptimizer(risk_free_rate=0.02)
    
    # Test with tech stocks
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
    
    try:
        result = optimizer.analyze_portfolio(symbols, period="1y")
        
        print("\n" + "="*60)
        print("PORTFOLIO OPTIMIZATION RESULTS")
        print("="*60)
        
        print("\n📊 Maximum Sharpe Ratio Portfolio:")
        print(f"Expected Return: {result['max_sharpe_portfolio']['expected_return']:.2%}")
        print(f"Volatility: {result['max_sharpe_portfolio']['volatility']:.2%}")
        print(f"Sharpe Ratio: {result['max_sharpe_portfolio']['sharpe_ratio']:.3f}")
        print("\nWeights:")
        for symbol, weight in result['max_sharpe_portfolio']['weights'].items():
            print(f"  {symbol}: {weight:.2%}")
        
        print("\n🛡️ Minimum Variance Portfolio:")
        print(f"Expected Return: {result['min_variance_portfolio']['expected_return']:.2%}")
        print(f"Volatility: {result['min_variance_portfolio']['volatility']:.2%}")
        print(f"Sharpe Ratio: {result['min_variance_portfolio']['sharpe_ratio']:.3f}")
        print("\nWeights:")
        for symbol, weight in result['min_variance_portfolio']['weights'].items():
            print(f"  {symbol}: {weight:.2%}")
        
        print(f"\n✅ Efficient Frontier: {result['efficient_frontier']['num_points']} portfolios calculated")
        
    except Exception as e:
        print(f"Error: {e}")