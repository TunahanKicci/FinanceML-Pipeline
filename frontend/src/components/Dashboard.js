// src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { predictStock, getModelStatus, healthCheck } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [symbol, setSymbol] = useState('AAPL');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);

  // Popüler hisse senetleri
  const popularStocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'META', 'NVDA', 'JPM', 'V', 'WMT'
  ];

  // Component mount olduğunda sistem durumunu kontrol et
  useEffect(() => {
    checkSystemStatus();
  }, []);

  const checkSystemStatus = async () => {
    try {
      const health = await healthCheck();
      const status = await getModelStatus();
      setSystemHealth(health);
      setModelStatus(status);
    } catch (err) {
      console.error('System check failed:', err);
    }
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setPrediction(null);

    try {
      const result = await predictStock(symbol);
      setPrediction(result);
    } catch (err) {
      setError(err.response?.data?.detail || 'Prediction failed');
      console.error('Prediction error:', err);
    } finally {
      setLoading(false);
    }
  };

  const getTrendColor = (trend) => {
    if (trend === 'UP') return '#10b981';
    if (trend === 'DOWN') return '#ef4444';
    return '#6b7280';
  };

  const getTrendIcon = (trend) => {
    if (trend === 'UP') return '↑';
    if (trend === 'DOWN') return '↓';
    return '→';
  };

  return (
    <div className="dashboard">
      {/* Header */}
      <header className="dashboard-header">
        <h1>FinanceML Dashboard</h1>
        <div className="system-status">
          {systemHealth && (
            <span className="status-badge status-healthy">
              System: {systemHealth.status}
            </span>
          )}
          {modelStatus && (
            <span className="status-badge status-model">
              Model: {modelStatus.version}
            </span>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="dashboard-content">
        {/* Prediction Form */}
        <div className="card prediction-form-card">
          <h2>Stock Price Prediction</h2>
          
          <form onSubmit={handlePredict} className="prediction-form">
            <div className="form-group">
              <label htmlFor="symbol">Stock Symbol</label>
              <input
                type="text"
                id="symbol"
                value={symbol}
                onChange={(e) => setSymbol(e.target.value.toUpperCase())}
                placeholder="Enter stock symbol (e.g., AAPL)"
                disabled={loading}
                required
              />
            </div>

            <button 
              type="submit" 
              className="predict-button"
              disabled={loading || !symbol}
            >
              {loading ? 'Predicting...' : 'Predict Price'}
            </button>
          </form>

          {/* Popular Stocks */}
          <div className="popular-stocks">
            <p>Quick Select:</p>
            <div className="stock-chips">
              {popularStocks.map((stock) => (
                <button
                  key={stock}
                  className={`stock-chip ${symbol === stock ? 'active' : ''}`}
                  onClick={() => setSymbol(stock)}
                  disabled={loading}
                >
                  {stock}
                </button>
              ))}
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="error-message">
              <strong>Error:</strong> {error}
            </div>
          )}
        </div>

        {/* Prediction Results */}
        {prediction && (
          <div className="card prediction-results-card">
            <h2>Prediction Results</h2>
            
            <div className="results-grid">
              <div className="result-item">
                <span className="result-label">Symbol</span>
                <span className="result-value symbol-value">
                  {prediction.symbol}
                </span>
              </div>

              <div className="result-item">
                <span className="result-label">Current Price</span>
                <span className="result-value">
                  ${prediction.current_price.toFixed(2)}
                </span>
              </div>

              <div className="result-item">
                <span className="result-label">Predicted Price</span>
                <span className="result-value predicted-price">
                  ${prediction.predicted_price.toFixed(2)}
                </span>
              </div>

              <div className="result-item">
                <span className="result-label">Price Change</span>
                <span 
                  className="result-value"
                  style={{ color: getTrendColor(prediction.trend) }}
                >
                  {getTrendIcon(prediction.trend)} ${Math.abs(prediction.price_change).toFixed(2)}
                  ({prediction.price_change_pct > 0 ? '+' : ''}{prediction.price_change_pct.toFixed(2)}%)
                </span>
              </div>

              <div className="result-item">
                <span className="result-label">Trend</span>
                <span 
                  className="result-value trend-badge"
                  style={{ 
                    backgroundColor: getTrendColor(prediction.trend),
                    color: 'white',
                    padding: '4px 12px',
                    borderRadius: '12px',
                    fontSize: '14px'
                  }}
                >
                  {prediction.trend}
                </span>
              </div>

              <div className="result-item">
                <span className="result-label">Prediction Date</span>
                <span className="result-value">
                  {prediction.prediction_date}
                </span>
              </div>
            </div>

            <div className="prediction-disclaimer">
              This is an AI prediction and should not be considered as financial advice.
              Always do your own research before making investment decisions.
            </div>
          </div>
        )}

        {/* Model Info */}
        {modelStatus && (
          <div className="card model-info-card">
            <h2>Model Information</h2>
            
            <div className="info-grid">
              <div className="info-item">
                <span className="info-label">Version</span>
                <span className="info-value">{modelStatus.version}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Status</span>
                <span className="info-value">{modelStatus.status}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Format</span>
                <span className="info-value">{modelStatus.model_format}</span>
              </div>
              
              <div className="info-item">
                <span className="info-label">Sequence Length</span>
                <span className="info-value">{modelStatus.sequence_length} days</span>
              </div>
              
              {modelStatus.trained_on && (
                <div className="info-item full-width">
                  <span className="info-label">Last Trained</span>
                  <span className="info-value">
                    {new Date(modelStatus.trained_on).toLocaleString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>FinanceML Pipeline - AI-Powered Stock Prediction System</p>
      </footer>
    </div>
  );
};

export default Dashboard;