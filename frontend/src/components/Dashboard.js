// frontend/src/components/Dashboard.js
// Mevcut kodunuzu şu şekilde güncelleyin:

import React, { useState, useEffect } from 'react';
import { getModelStatus, healthCheck, forecastStock, getFinancials, getSentiment, getRiskAnalysis } from '../services/api';
import './Dashboard.css';
import ForecastChart from './ForecastChart';
import FinancialMetrics from './FinancialMetrics';
import SentimentCard from './SentimentCard';
import RiskAnalysis from './RiskAnalysis';
import PortfolioOptimizer from './PortfolioOptimizer'; 
import InfoCard from './InfoCard';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('prediction'); 
  const [forecastData, setForecastData] = useState(null);
  const [forecastDays] = useState(14);
  const [symbol, setSymbol] = useState('AAPL');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [modelStatus, setModelStatus] = useState(null);
  const [systemHealth, setSystemHealth] = useState(null);
  const [financialData, setFinancialData] = useState(null);
  const [sentimentData, setSentimentData] = useState(null);
  const [riskData, setRiskData] = useState(null);

  const popularStocks = [
    'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA',
    'META', 'NVDA', 'JPM', 'V', 'WMT'
  ];

  const fetchFinancials = async (symbol) => {
    try {
      const data = await getFinancials(symbol);
      setFinancialData(data);
    } catch (err) {
      console.error('Failed to fetch financials:', err);
    }
  };

  const fetchSentiment = async (symbol) => {
    try {
      const data = await getSentiment(symbol);
      setSentimentData(data);
    } catch (err) {
      console.error('Failed to fetch sentiment:', err);
    }
  };

  const fetchRiskAnalysis = async (symbol) => {
    try {
      const data = await getRiskAnalysis(symbol);
      setRiskData(data);
    } catch (err) {
      console.error('Failed to fetch risk analysis:', err);
    }
  };

  const handleForecast = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const result = await forecastStock(symbol, forecastDays);
      console.log("Forecast API raw response:", result);

      if (result) {
        setForecastData(result);
        await fetchFinancials(symbol);
        await fetchSentiment(symbol);
        await fetchRiskAnalysis(symbol);
      }
    } catch (err) {
      console.error("Forecast API error:", err);
      setError(err.message || 'Forecast failed');
    } finally {
      setLoading(false);
    }
  };

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
    if (trend.includes('UP')) return '#10b981';
    if (trend.includes('DOWN')) return '#ef4444';
    return '#6b7280';
  };

  const getTrendIcon = (trend) => {
    if (trend.includes('UP')) return '↑';
    if (trend.includes('DOWN')) return '↓';
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

      {/* YENİ: Tab Navigation */}
      <div className="tab-navigation">
        <button 
          className={`tab-button ${activeTab === 'prediction' ? 'active' : ''}`}
          onClick={() => setActiveTab('prediction')}
        >
          📈 Stock Prediction
        </button>
        <button 
          className={`tab-button ${activeTab === 'portfolio' ? 'active' : ''}`}
          onClick={() => setActiveTab('portfolio')}
        >
          💼 Portfolio Optimization
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'prediction' ? (
        <>
          {/* Mevcut Prediction Content */}
          <div className="dashboard-content">
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

              {error && (
                <div className="error-message">
                  <strong>Error:</strong> {error}
                </div>
              )}
            </div>

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
            <>
              <div className="card forecast-card">
                <h2>
                  {forecastData.symbol} - {forecastDays}-Day Forecast
                  {forecastData.trend && (
                    <span 
                      style={{ 
                        marginLeft: '10px', 
                        color: getTrendColor(forecastData.trend),
                        fontWeight: '600'
                      }}
                    >
                      {getTrendIcon(forecastData.trend)} {forecastData.trend}
                    </span>
                  )}
                </h2>
                <ForecastChart forecastData={forecastData} />
              </div>

              {financialData && (
                <div className="card financial-card">
                  <FinancialMetrics financialData={financialData} />
                </div>
              )}

              {riskData && (
                <div className="card" style={{ marginTop: "20px" }}>
                  <RiskAnalysis riskData={riskData} />
                </div>
              )}

              {sentimentData && (
                <div className="card sentiment-card" style={{ marginTop: "20px" }}>
                  <SentimentCard sentimentData={sentimentData} />
                </div>
              )}
            </>
          )}
        </>
      ) : (
        /* YENİ: Portfolio Tab Content */
        <div className="dashboard-content">
          <PortfolioOptimizer />
        </div>
      )}

      <InfoCard />

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>FinanceML Pipeline - AI-Powered Stock Prediction System</p>
      </footer>
    </div>
  );
};

export default Dashboard;