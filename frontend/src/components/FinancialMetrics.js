// frontend/src/components/FinancialMetrics.js
import React from 'react';
import './FinancialMetrics.css';

const FinancialMetrics = ({ financialData }) => {
  if (!financialData) return null;

  const { metrics, financial_score } = financialData;

  const formatNumber = (num) => {
    if (!num) return 'N/A';
    if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
    return `$${num.toLocaleString()}`;
  };

  const formatPercent = (num) => {
    if (!num) return 'N/A';
    return `${(num * 100).toFixed(2)}%`;
  };

  const formatRatio = (num) => {
    if (!num) return 'N/A';
    return num.toFixed(2);
  };

  const getScoreColor = (percentage) => {
    if (percentage >= 80) return '#10b981';
    if (percentage >= 60) return '#3b82f6';
    if (percentage >= 40) return '#f59e0b';
    return financialData.financial_score.color || '#6b7280';
  };

  return (
    <div className="financial-metrics">
      {/* Company Header */}
      <div className="company-header">
        <h2>{metrics.company_name}</h2>
        <div className="company-info">
          <span className="badge">{metrics.sector}</span>
          <span className="badge">{metrics.industry}</span>
        </div>
      </div>

      {/* Financial Score */}
      {financial_score && (
        <div className="financial-score-card">
          <h3>Financial Health Score</h3>
          <div className="score-container">
            <div 
              className="score-circle"
              style={{ 
                background: `conic-gradient(${getScoreColor(financial_score.percentage)} ${financial_score.percentage * 3.6}deg, #e5e7eb 0deg)`
              }}
            >
              <div className="score-inner">
                <div className="score-value">{financial_score.score}</div>
                <div className="score-max">/ {financial_score.max_score}</div>
              </div>
            </div>
            <div className="score-details">
              <div className="score-rating">{financial_score.rating}</div>
              <div className="score-interpretation">{financial_score.interpretation}</div>
              <div className="score-factors">
                {financial_score.key_factors.map((factor, idx) => (
                  <span key={idx} className="factor-badge">{factor}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Key Metrics Grid */}
      <div className="metrics-grid">
        {/* Valuation */}
        <div className="metric-section">
          <h3>Valuation Ratios</h3>
          <div className="metric-items">
            <div className="metric-item">
              <span className="metric-label">P/E Ratio</span>
              <span className="metric-value">{formatRatio(metrics.pe_ratio)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Forward P/E</span>
              <span className="metric-value">{formatRatio(metrics.forward_pe)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">PEG Ratio</span>
              <span className="metric-value">{formatRatio(metrics.peg_ratio)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Price/Book</span>
              <span className="metric-value">{formatRatio(metrics.price_to_book)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Price/Sales</span>
              <span className="metric-value">{formatRatio(metrics.price_to_sales)}</span>
            </div>
          </div>
        </div>

        {/* Profitability */}
        <div className="metric-section">
          <h3>Profitability</h3>
          <div className="metric-items">
            <div className="metric-item">
              <span className="metric-label">Profit Margin</span>
              <span className="metric-value">{formatPercent(metrics.profit_margin)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Operating Margin</span>
              <span className="metric-value">{formatPercent(metrics.operating_margin)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Gross Margin</span>
              <span className="metric-value">{formatPercent(metrics.gross_margin)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">ROE</span>
              <span className="metric-value">{formatPercent(metrics.roe)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">ROA</span>
              <span className="metric-value">{formatPercent(metrics.roa)}</span>
            </div>
          </div>
        </div>

        {/* Financial Health */}
        <div className="metric-section">
          <h3>Financial Health</h3>
          <div className="metric-items">
            <div className="metric-item">
              <span className="metric-label">Current Ratio</span>
              <span className="metric-value">{formatRatio(metrics.current_ratio)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Quick Ratio</span>
              <span className="metric-value">{formatRatio(metrics.quick_ratio)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Debt/Equity</span>
              <span className="metric-value">{formatRatio(metrics.debt_to_equity)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Total Debt</span>
              <span className="metric-value">{formatNumber(metrics.total_debt)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Free Cash Flow</span>
              <span className="metric-value">{formatNumber(metrics.free_cashflow)}</span>
            </div>
          </div>
        </div>

        {/* Growth */}
        <div className="metric-section">
          <h3>Growth Metrics</h3>
          <div className="metric-items">
            <div className="metric-item">
              <span className="metric-label">Revenue Growth</span>
              <span className="metric-value">{formatPercent(metrics.revenue_growth)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Earnings Growth</span>
              <span className="metric-value">{formatPercent(metrics.earnings_growth)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">EPS (TTM)</span>
              <span className="metric-value">${formatRatio(metrics.eps_trailing)}</span>
            </div>
            <div className="metric-item">
              <span className="metric-label">Market Cap</span>
              <span className="metric-value">{formatNumber(metrics.market_cap)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Quarterly Data */}
      {metrics.quarterly_income && metrics.quarterly_income.length > 0 && (
        <div className="quarterly-section">
          <h3>Quarterly Performance</h3>
          <div className="quarterly-table">
            <table>
              <thead>
                <tr>
                  <th>Quarter</th>
                  <th>Revenue</th>
                  <th>Net Income</th>
                  <th>Operating Income</th>
                  <th>EBITDA</th>
                </tr>
              </thead>
              <tbody>
                {metrics.quarterly_income.slice(0, 4).map((quarter, idx) => (
                  <tr key={idx}>
                    <td>{new Date(quarter.date).toLocaleDateString('en-US', { year: 'numeric', quarter: 'short' })}</td>
                    <td>{formatNumber(quarter.total_revenue)}</td>
                    <td>{formatNumber(quarter.net_income)}</td>
                    <td>{formatNumber(quarter.operating_income)}</td>
                    <td>{formatNumber(quarter.ebitda)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};

export default FinancialMetrics;