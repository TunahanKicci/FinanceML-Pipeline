// frontend/src/components/RiskAnalysis.js
import React from 'react';
import './RiskAnalysis.css';

const RiskAnalysis = ({ riskData }) => {
  if (!riskData) return null;

  const { risk_rating, risk_color, beta, volatility, var_95, sharpe_ratio, max_drawdown, risk_factors } = riskData;

  const getBetaInterpretation = (beta) => {
    if (!beta) return 'N/A';
    if (beta > 1.5) return 'Very High Volatility';
    if (beta > 1.2) return 'High Volatility';
    if (beta > 0.8) return 'Moderate Volatility';
    if (beta > 0.5) return 'Low Volatility';
    return 'Very Low Volatility';
  };

  const getSharpeInterpretation = (sharpe) => {
    if (!sharpe) return 'N/A';
    if (sharpe > 3) return 'Excellent';
    if (sharpe > 2) return 'Very Good';
    if (sharpe > 1) return 'Good';
    if (sharpe > 0) return 'Acceptable';
    return 'Poor';
  };

  return (
    <div className="risk-analysis">
      <div className="risk-header">
        <h2>Risk & Volatility Analysis</h2>
        <div 
          className="risk-badge"
          style={{ backgroundColor: risk_color }}
        >
          {risk_rating}
        </div>
      </div>

      {/* Risk Factors */}
      {risk_factors && risk_factors.length > 0 && (
        <div className="risk-factors">
          <h3>Key Risk Factors</h3>
          <div className="factors-list">
            {risk_factors.map((factor, idx) => (
              <span key={idx} className="factor-badge">{factor}</span>
            ))}
          </div>
        </div>
      )}

      {/* Metrics Grid */}
      <div className="risk-metrics-grid">
        {/* Beta */}
        <div className="risk-metric-card">
          <div className="metric-icon">β</div>
          <div className="metric-content">
            <h4>Beta Coefficient</h4>
            <div className="metric-value">{beta ? beta.toFixed(3) : 'N/A'}</div>
            <div className="metric-description">
              {getBetaInterpretation(beta)}
            </div>
            <div className="metric-info">
              Market correlation indicator
            </div>
          </div>
        </div>

        {/* Volatility */}
        {volatility && (
          <div className="risk-metric-card">
            <div className="metric-icon">σ</div>
            <div className="metric-content">
              <h4>Annual Volatility</h4>
              <div className="metric-value">{(volatility.annual_volatility * 100).toFixed(2)}%</div>
              <div className="metric-description">
                30d: {(volatility.volatility_30d * 100).toFixed(2)}%
              </div>
              <div className="metric-info">
                Price fluctuation measure
              </div>
            </div>
          </div>
        )}

        {/* Sharpe Ratio */}
        <div className="risk-metric-card">
          <div className="metric-icon">S</div>
          <div className="metric-content">
            <h4>Sharpe Ratio</h4>
            <div className="metric-value">{sharpe_ratio ? sharpe_ratio.toFixed(3) : 'N/A'}</div>
            <div className="metric-description">
              {getSharpeInterpretation(sharpe_ratio)}
            </div>
            <div className="metric-info">
              Risk-adjusted returns
            </div>
          </div>
        </div>

        {/* Max Drawdown */}
        {max_drawdown && (
          <div className="risk-metric-card">
            <div className="metric-icon">↓</div>
            <div className="metric-content">
              <h4>Max Drawdown</h4>
              <div className="metric-value">{max_drawdown.max_drawdown_pct}%</div>
              <div className="metric-description">
                {max_drawdown.recovery_status}
              </div>
              <div className="metric-info">
                Largest peak-to-trough decline
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Value at Risk */}
      {var_95 && (
        <div className="var-section">
          <h3>Value at Risk (VaR)</h3>
          <div className="var-grid">
            <div className="var-card">
              <div className="var-label">95% Confidence</div>
              <div className="var-value">${var_95.var_parametric}</div>
              <div className="var-description">
                {var_95.interpretation}
              </div>
            </div>
            <div className="var-card cvar">
              <div className="var-label">CVaR (Expected Shortfall)</div>
              <div className="var-value">${var_95.cvar}</div>
              <div className="var-description">
                Average loss if VaR is exceeded
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Volatility Timeline */}
      {volatility && (
        <div className="volatility-timeline">
          <h3>Volatility Over Time</h3>
          <div className="timeline-bars">
            <div className="timeline-item">
              <div className="timeline-label">30 Days</div>
              <div className="timeline-bar-container">
                <div 
                  className="timeline-bar"
                  style={{ 
                    width: `${Math.min((volatility.volatility_30d / volatility.annual_volatility) * 100, 100)}%`,
                    backgroundColor: volatility.volatility_30d > volatility.annual_volatility ? '#ef4444' : '#3b82f6'
                  }}
                />
              </div>
              <div className="timeline-value">{(volatility.volatility_30d * 100).toFixed(2)}%</div>
            </div>
            <div className="timeline-item">
              <div className="timeline-label">90 Days</div>
              <div className="timeline-bar-container">
                <div 
                  className="timeline-bar"
                  style={{ 
                    width: `${Math.min((volatility.volatility_90d / volatility.annual_volatility) * 100, 100)}%`,
                    backgroundColor: '#8b5cf6'
                  }}
                />
              </div>
              <div className="timeline-value">{(volatility.volatility_90d * 100).toFixed(2)}%</div>
            </div>
            <div className="timeline-item">
              <div className="timeline-label">180 Days</div>
              <div className="timeline-bar-container">
                <div 
                  className="timeline-bar"
                  style={{ 
                    width: `${Math.min((volatility.volatility_180d / volatility.annual_volatility) * 100, 100)}%`,
                    backgroundColor: '#10b981'
                  }}
                />
              </div>
              <div className="timeline-value">{(volatility.volatility_180d * 100).toFixed(2)}%</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default RiskAnalysis;