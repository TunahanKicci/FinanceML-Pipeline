// src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { predictStock, getModelStatus, healthCheck, forecastStock } from '../services/api';
import './Dashboard.css';
import ForecastChart from './ForecastChart';

const Dashboard = () => {
  const [forecastData, setForecastData] = useState(null);
  const [forecastDays] = useState(14); // sadece okunacak
  const [symbol, setSymbol] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);

  // Popüler hisse senetleri
  const popularStocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'META', 'NVDA', 'JPM', 'V', 'WMT'
  ];

  const handleForecast = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await forecastStock(symbol, forecastDays);
      console.log("Forecast API raw response:", result);

      setForecastData(result); // artık result.forecast.dates ve result.forecast.prices var
    } catch (err) {
      console.error("Forecast API error:", err);
      setError(err.message || 'Forecast failed');
    } finally {
      setLoading(false);
    }
  };
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
          
          <form onSubmit={handleForecast} className="prediction-form">
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
              {loading ? 'Forecasting...' : `Forecast ${forecastDays} Days`}
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
      
      {forecastData && (
  <div className="card">
    <h2>{forecastData.symbol} - {forecastDays}-Day Forecast</h2>
    <ForecastChart forecastData={forecastData} />
  </div>
)}

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>FinanceML Pipeline - AI-Powered Stock Prediction System</p>
      </footer>
    </div>
  );
};

export default Dashboard;