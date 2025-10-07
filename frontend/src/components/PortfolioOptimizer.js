// frontend/src/components/PortfolioOptimizer.js
import React, { useState } from 'react';
import './PortfolioOptimizer.css';
import { optimizePortfolio } from '../services/api';
import EfficientFrontierChart from './EfficientFrontierChart';

const PortfolioOptimizer = () => {
  const [symbols, setSymbols] = useState(['AAPL', 'MSFT', 'GOOGL', 'AMZN']);
  const [newSymbol, setNewSymbol] = useState('');
  const [period, setPeriod] = useState('2y');
  const [constraints, setConstraints] = useState({
    min_weight: 0.05,
    max_weight: 0.50
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const popularStocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'META', 'NVDA', 'JPM', 'V', 'WMT'
  ];

  const handleAddSymbol = () => {
    const upper = newSymbol.toUpperCase().trim();
    if (upper && !symbols.includes(upper)) {
      setSymbols([...symbols, upper]);
      setNewSymbol('');
    }
  };

  const handleRemoveSymbol = (symbol) => {
    if (symbols.length > 2) {
      setSymbols(symbols.filter(s => s !== symbol));
    }
  };

  const handleQuickAdd = (symbol) => {
    if (!symbols.includes(symbol)) {
      setSymbols([...symbols, symbol]);
    }
  };

  const handleOptimize = async () => {
    if (symbols.length < 2) {
      setError('At least 2 symbols required for portfolio optimization');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await optimizePortfolio({
        symbols,
        period,
        constraints: {
          min_weight: parseFloat(constraints.min_weight),
          max_weight: parseFloat(constraints.max_weight)
        }
      });

      setResult(data);
    } catch (err) {
      setError(err.message || 'Portfolio optimization failed');
    } finally {
      setLoading(false);
    }
  };

  const formatPercent = (num) => {
    return `${(num * 100).toFixed(2)}%`;
  };

  const formatWeight = (num) => {
    return `${(num * 100).toFixed(1)}%`;
  };

  return (
    <div className="portfolio-optimizer">
      {/* Header */}
      <div className="portfolio-header">
        <h2>Portfolio Optimization</h2>
        <p className="subtitle">Modern Portfolio Theory (Markowitz)</p>
      </div>

      {/* Configuration Section */}
      <div className="config-section">
        <div className="config-card">
          <h3>Select Assets</h3>
          
          {/* Symbol Input */}
          <div className="symbol-input-group">
            <input
              type="text"
              value={newSymbol}
              onChange={(e) => setNewSymbol(e.target.value.toUpperCase())}
              onKeyPress={(e) => e.key === 'Enter' && handleAddSymbol()}
              placeholder="Add symbol (e.g., TSLA)"
              disabled={loading}
            />
            <button 
              onClick={handleAddSymbol}
              disabled={loading || !newSymbol}
              className="add-button"
            >
              Add
            </button>
          </div>

          {/* Selected Symbols */}
          <div className="selected-symbols">
            {symbols.map((symbol) => (
              <div key={symbol} className="symbol-chip">
                <span>{symbol}</span>
                <button
                  onClick={() => handleRemoveSymbol(symbol)}
                  disabled={loading || symbols.length <= 2}
                  className="remove-btn"
                >
                  ×
                </button>
              </div>
            ))}
          </div>

          {/* Quick Add */}
          <div className="quick-add-section">
            <label>Quick Add:</label>
            <div className="quick-add-chips">
              {popularStocks
                .filter(s => !symbols.includes(s))
                .slice(0, 10)
                .map((symbol) => (
                  <button
                    key={symbol}
                    onClick={() => handleQuickAdd(symbol)}
                    disabled={loading}
                    className="quick-add-chip"
                  >
                    + {symbol}
                  </button>
                ))}
            </div>
          </div>
        </div>

        <div className="config-card">
          <h3>Settings</h3>
          
          {/* Period Selection */}
          <div className="form-group">
            <label>Historical Period</label>
            <select 
              value={period} 
              onChange={(e) => setPeriod(e.target.value)}
              disabled={loading}
            >
              <option value="1y">1 Year</option>
              <option value="2y">2 Years</option>
              <option value="3y">3 Years</option>
              <option value="5y">5 Years</option>
            </select>
          </div>

          {/* Constraints */}
          <div className="constraints-group">
            <div className="form-group">
              <label>Min Weight per Asset</label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={constraints.min_weight}
                onChange={(e) => setConstraints({...constraints, min_weight: e.target.value})}
                disabled={loading}
              />
              <span className="input-hint">{formatWeight(constraints.min_weight)}</span>
            </div>
            <div className="form-group">
              <label>Max Weight per Asset</label>
              <input
                type="number"
                min="0"
                max="1"
                step="0.01"
                value={constraints.max_weight}
                onChange={(e) => setConstraints({...constraints, max_weight: e.target.value})}
                disabled={loading}
              />
              <span className="input-hint">{formatWeight(constraints.max_weight)}</span>
            </div>
          </div>

          {/* Optimize Button */}
          <button 
            onClick={handleOptimize}
            disabled={loading || symbols.length < 2}
            className="optimize-button"
          >
            {loading ? 'Optimizing...' : 'Optimize Portfolio'}
          </button>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Results Section */}
      {result && (
        <div className="results-section">
          {/* Optimal Portfolios */}
          <div className="portfolios-grid">
            {/* Max Sharpe Portfolio */}
            <div className="portfolio-card sharpe-card">
              <div className="portfolio-header">
                <h3>Maximum Sharpe Ratio</h3>
                <div className="portfolio-badge">Optimal Risk/Return</div>
              </div>
              
              <div className="portfolio-metrics">
                <div className="metric">
                  <span className="metric-label">Expected Return</span>
                  <span className="metric-value return-positive">
                    {formatPercent(result.max_sharpe_portfolio.expected_return)}
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Volatility</span>
                  <span className="metric-value">
                    {formatPercent(result.max_sharpe_portfolio.volatility)}
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Sharpe Ratio</span>
                  <span className="metric-value sharpe-value">
                    {result.max_sharpe_portfolio.sharpe_ratio.toFixed(3)}
                  </span>
                </div>
              </div>

              <div className="weights-section">
                <h4>Asset Allocation</h4>
                <div className="weights-list">
                  {Object.entries(result.max_sharpe_portfolio.weights)
                    .sort((a, b) => b[1] - a[1])
                    .map(([symbol, weight]) => (
                      <div key={symbol} className="weight-item">
                        <span className="weight-symbol">{symbol}</span>
                        <div className="weight-bar-container">
                          <div 
                            className="weight-bar"
                            style={{ width: `${weight * 100}%` }}
                          />
                        </div>
                        <span className="weight-value">{formatWeight(weight)}</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>

            {/* Min Variance Portfolio */}
            <div className="portfolio-card variance-card">
              <div className="portfolio-header">
                <h3>Minimum Variance</h3>
                <div className="portfolio-badge">Lowest Risk</div>
              </div>
              
              <div className="portfolio-metrics">
                <div className="metric">
                  <span className="metric-label">Expected Return</span>
                  <span className="metric-value return-positive">
                    {formatPercent(result.min_variance_portfolio.expected_return)}
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Volatility</span>
                  <span className="metric-value">
                    {formatPercent(result.min_variance_portfolio.volatility)}
                  </span>
                </div>
                <div className="metric">
                  <span className="metric-label">Sharpe Ratio</span>
                  <span className="metric-value sharpe-value">
                    {result.min_variance_portfolio.sharpe_ratio.toFixed(3)}
                  </span>
                </div>
              </div>

              <div className="weights-section">
                <h4>Asset Allocation</h4>
                <div className="weights-list">
                  {Object.entries(result.min_variance_portfolio.weights)
                    .sort((a, b) => b[1] - a[1])
                    .map(([symbol, weight]) => (
                      <div key={symbol} className="weight-item">
                        <span className="weight-symbol">{symbol}</span>
                        <div className="weight-bar-container">
                          <div 
                            className="weight-bar"
                            style={{ width: `${weight * 100}%` }}
                          />
                        </div>
                        <span className="weight-value">{formatWeight(weight)}</span>
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>

          {/* Efficient Frontier Chart */}
          <div className="chart-card">
            <h3>Efficient Frontier</h3>
            <EfficientFrontierChart data={result} />
          </div>

          {/* Asset Statistics */}
          <div className="asset-stats-card">
            <h3>Individual Asset Statistics</h3>
            <div className="asset-stats-table">
              <table>
                <thead>
                  <tr>
                    <th>Symbol</th>
                    <th>Expected Return</th>
                    <th>Volatility</th>
                    <th>Sharpe Ratio</th>
                  </tr>
                </thead>
                <tbody>
                  {result.asset_statistics
                    .sort((a, b) => b.sharpe_ratio - a.sharpe_ratio)
                    .map((asset) => (
                      <tr key={asset.symbol}>
                        <td className="symbol-cell">{asset.symbol}</td>
                        <td className={asset.expected_return > 0 ? 'positive' : 'negative'}>
                          {formatPercent(asset.expected_return)}
                        </td>
                        <td>{formatPercent(asset.volatility)}</td>
                        <td className={asset.sharpe_ratio > 1 ? 'good' : ''}>
                          {asset.sharpe_ratio.toFixed(3)}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Correlation Matrix */}
          <div className="correlation-card">
            <h3>Correlation Matrix</h3>
            <div className="correlation-matrix">
              <table>
                <thead>
                  <tr>
                    <th></th>
                    {result.correlation_matrix.symbols.map(s => (
                      <th key={s}>{s}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {result.correlation_matrix.symbols.map((symbol, i) => (
                    <tr key={symbol}>
                      <td className="symbol-cell">{symbol}</td>
                      {result.correlation_matrix.matrix[i].map((corr, j) => (
                        <td 
                          key={j}
                          className="correlation-cell"
                          style={{
                            background: `rgba(${corr > 0 ? '16, 185, 129' : '239, 68, 68'}, ${Math.abs(corr) * 0.5})`,
                            color: Math.abs(corr) > 0.5 ? 'white' : '#1f2937'
                          }}
                        >
                          {corr.toFixed(2)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Analysis Info */}
          <div className="analysis-info">
            <div className="info-item">
              <span className="info-label">Analysis Date:</span>
              <span>{new Date(result.analysis_date).toLocaleString()}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Historical Period:</span>
              <span>{result.period}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Risk-Free Rate:</span>
              <span>{formatPercent(result.risk_free_rate)}</span>
            </div>
            <div className="info-item">
              <span className="info-label">Data Points:</span>
              <span>{result.data_points}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default PortfolioOptimizer;