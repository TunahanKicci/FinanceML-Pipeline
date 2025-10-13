// frontend/src/components/Dashboard.js
import React, { useState, useEffect } from 'react';
import { getModelStatus, healthCheck, forecastStock, getFinancials, getSentiment, getRiskAnalysis } from '../services/api';
import './Dashboard.css';
import ForecastChart from './ForecastChart';
import FinancialMetrics from './FinancialMetrics';
import SentimentCard from './SentimentCard';
import RiskAnalysis from './RiskAnalysis';
import PortfolioOptimizer from './PortfolioOptimizer'; 
import InfoCard from './InfoCard';
import { AnimatePresence, motion } from 'framer-motion'; // tek import satırı

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

  const popularStocks = ['AAPL','MSFT','GOOGL','AMZN','TSLA','META','NVDA','JPM','V','WMT'];

  const fetchFinancials = async (symbol) => { try { const data = await getFinancials(symbol); setFinancialData(data); } catch (err) { console.error('Failed to fetch financials:', err); } };
  const fetchSentiment = async (symbol) => { try { const data = await getSentiment(symbol); setSentimentData(data); } catch (err) { console.error('Failed to fetch sentiment:', err); } };
  const fetchRiskAnalysis = async (symbol) => { try { const data = await getRiskAnalysis(symbol); setRiskData(data); } catch (err) { console.error('Failed to fetch risk analysis:', err); } };

  const handleForecast = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const result = await forecastStock(symbol, forecastDays);
      if (result) {
        setForecastData(result);
        await fetchFinancials(symbol);
        await fetchSentiment(symbol);
        await fetchRiskAnalysis(symbol);
      }
    } catch (err) {
      setError(err.message || 'Forecast failed');
    } finally { setLoading(false); }
  };

  useEffect(() => { checkSystemStatus(); }, []);
  const checkSystemStatus = async () => {
    try { const health = await healthCheck(); const status = await getModelStatus(); setSystemHealth(health); setModelStatus(status); } catch (err) { console.error('System check failed:', err); }
  };

  const getTrendColor = (trend) => trend.includes('UP') ? '#10b981' : trend.includes('DOWN') ? '#ef4444' : '#6b7280';
  const getTrendIcon = (trend) => trend.includes('UP') ? '↑' : trend.includes('DOWN') ? '↓' : '→';

  return (
    <motion.div
      className="dashboard"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      transition={{ duration: 0.8 }}
    >
      {/* Header */}
      <header className="dashboard-header">
        <h1>Hisse Senedi Analiz Platformu</h1>
        <div className="system-status">
          {systemHealth && <span className="status-badge status-healthy">System: {systemHealth.status}</span>}
          {modelStatus && <span className="status-badge status-model">Model: {modelStatus.version}</span>}
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="tab-navigation">
        <button className={`tab-button ${activeTab === 'prediction' ? 'active' : ''}`} onClick={() => setActiveTab('prediction')}>Comprehensive Stock Analysis</button>
        <button className={`tab-button ${activeTab === 'portfolio' ? 'active' : ''}`} onClick={() => setActiveTab('portfolio')}> Portfolio Optimization</button>
      </div>

      {/* Tab Content Animasyonu */}
      <AnimatePresence mode="wait">
        {activeTab === 'prediction' ? (
          <motion.div
            key="prediction"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
            transition={{ duration: 0.5 }}
          >
            {/* Prediction Content */}
            <div className="dashboard-content">
              <div className="card prediction-form-card">
                <h2>Stock Price Prediction</h2>
                <form onSubmit={handleForecast} className="prediction-form">
                  <div className="form-group">
                    <label htmlFor="symbol">Stock Symbol</label>
                    <input type="text" id="symbol" value={symbol} onChange={(e) => setSymbol(e.target.value.toUpperCase())} placeholder="Enter stock symbol (e.g., AAPL)" disabled={loading} required />
                  </div>
                  <button type="submit" className="predict-button" disabled={loading || !symbol}>
                    {loading ? 'Forecasting...' : 'View Full Analysis'}
                  </button>
                </form>

                <div className="popular-stocks">
                  <p>Quick Select:</p>
                  <div className="stock-chips">
                    {popularStocks.map((stock) => (
                      <button key={stock} className={`stock-chip ${symbol === stock ? 'active' : ''}`} onClick={() => setSymbol(stock)} disabled={loading}>{stock}</button>
                    ))}
                  </div>
                </div>

                {error && <div className="error-message"><strong>Error:</strong> {error}</div>}
              </div>

              {modelStatus && (
                <div className="card model-info-card">
                  <h2>Model Information</h2>
                  <div className="info-grid">
                    <div className="info-item"><span className="info-label">Version</span><span className="info-value">{modelStatus.version}</span></div>
                    <div className="info-item"><span className="info-label">Status</span><span className="info-value">{modelStatus.status}</span></div>
                    <div className="info-item"><span className="info-label">Sequence Length</span><span className="info-value">{modelStatus.sequence_length} days</span></div>
                    {modelStatus.trained_on && (
                      <div className="info-item full-width"><span className="info-label">Last Trained</span><span className="info-value">{new Date(modelStatus.trained_on).toLocaleString()}</span></div>
                    )}
                  </div>
                </div>
              )}
            </div>

            {forecastData && (
              <div className="dashboard-content">
                {/* Forecast Card */}
                <div className="card forecast-card">
                  <h2>
                    {forecastData.symbol} - {forecastDays}-Day Forecast
                    {forecastData.trend && (
                      <span
                        style={{
                          marginLeft: '10px',
                          color: getTrendColor(forecastData.trend),
                          fontWeight: '600',
                        }}
                      >
                        {getTrendIcon(forecastData.trend)} {forecastData.trend}
                      </span>
                    )}
                  </h2>
                  <ForecastChart forecastData={forecastData} />
                </div>

                {/* Financial Metrics */}
                {financialData && (
                  <div className="card financial-card">
                    <FinancialMetrics financialData={financialData} />
                  </div>
                )}

                {/* Risk Analysis */}
                {riskData && (
                  <div className="card risk-card">
                    <RiskAnalysis riskData={riskData} />
                  </div>
                )}

                {/* Sentiment Analysis */}
                {sentimentData && (
                  <div className="card sentiment-card">
                    <SentimentCard sentimentData={sentimentData} />
                  </div>
                )}
              </div>
            )}
          </motion.div>
        ) : (
          <motion.div
            key="portfolio"
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -30 }}
            transition={{ duration: 0.5 }}
          >
            <div className="dashboard-content">
              <PortfolioOptimizer />
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <InfoCard />

      {/* Footer */}
      <footer className="dashboard-footer">
        <p>© 2025 FinanceML Pipeline — Bu platformda sunulan tüm tahmin, analiz ve veriler 
        yalnızca eğitim ve bilgilendirme amaçlıdır. Sunulan içerikler, yapay zekâ modelleri 
        tarafından otomatik olarak üretilir ve yatırım danışmanlığı kapsamında değildir. 
        Hiçbir veri, grafik veya tahmin “al”, “sat” ya da “tut” önerisi niteliği taşımaz. 
        Yatırım kararlarınızı, kişisel risk-getiri tercihlerinize uygun olarak 
        SPK tarafından yetkilendirilmiş kurumların profesyonel danışmanlarıyla almanız önerilir.</p>
      </footer>
    </motion.div>
  );
};

export default Dashboard;
