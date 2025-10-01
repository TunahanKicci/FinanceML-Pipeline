// frontend/src/components/SentimentCard.js
import React from 'react';
import './SentimentCard.css';

const SentimentCard = ({ sentimentData }) => {
  if (!sentimentData) return null;

  const { overall_sentiment, distribution, news, statistics } = sentimentData;

  const getSentimentColor = (score) => {
    if (score > 0.3) return '#10b981';
    if (score > 0.1) return '#3b82f6';
    if (score < -0.3) return '#ef4444';
    if (score < -0.1) return '#f59e0b';
    return '#6b7280';
  };

  const getScorePercentage = (score) => {
    // Convert -1 to 1 scale to 0 to 100
    return ((score + 1) / 2) * 100;
  };

  return (
    <div className="sentiment-card">
      {/* Header */}
      <div className="sentiment-header">
        <h2>News Sentiment Analysis</h2>
        <span className="news-count">{sentimentData.total_news} articles analyzed</span>
      </div>

      {/* Overall Sentiment */}
      <div className="sentiment-overall">
        <div className="sentiment-score-container">
          <div 
            className="sentiment-circle"
            style={{
              background: `conic-gradient(${getSentimentColor(overall_sentiment.score)} ${getScorePercentage(overall_sentiment.score) * 3.6}deg, #e5e7eb 0deg)`
            }}
          >
            <div className="sentiment-circle-inner">
              <div className="sentiment-emoji">{overall_sentiment.emoji}</div>
              <div className="sentiment-score-value">{overall_sentiment.score.toFixed(3)}</div>
            </div>
          </div>
          
          <div className="sentiment-details">
            <h3 style={{ color: getSentimentColor(overall_sentiment.score) }}>
              {overall_sentiment.label}
            </h3>
            <div className="sentiment-confidence">
              Confidence: {overall_sentiment.confidence}%
            </div>
            <div className="sentiment-stats">
              <span>Median: {overall_sentiment.median_score.toFixed(3)}</span>
              <span>Volatility: {overall_sentiment.volatility.toFixed(3)}</span>
            </div>
          </div>
        </div>

        {/* Sentiment Bar */}
        <div className="sentiment-bar">
          <div 
            className="sentiment-bar-fill very-negative"
            style={{ width: `${(distribution.very_negative / sentimentData.total_news) * 100}%` }}
            title={`Very Negative: ${distribution.very_negative}`}
          />
          <div 
            className="sentiment-bar-fill negative"
            style={{ width: `${(distribution.negative / sentimentData.total_news) * 100}%` }}
            title={`Negative: ${distribution.negative}`}
          />
          <div 
            className="sentiment-bar-fill neutral"
            style={{ width: `${(distribution.neutral / sentimentData.total_news) * 100}%` }}
            title={`Neutral: ${distribution.neutral}`}
          />
          <div 
            className="sentiment-bar-fill positive"
            style={{ width: `${(distribution.positive / sentimentData.total_news) * 100}%` }}
            title={`Positive: ${distribution.positive}`}
          />
          <div 
            className="sentiment-bar-fill very-positive"
            style={{ width: `${(distribution.very_positive / sentimentData.total_news) * 100}%` }}
            title={`Very Positive: ${distribution.very_positive}`}
          />
        </div>

        {/* Distribution Legend */}
        <div className="distribution-legend">
          <div className="legend-item">
            <span className="legend-color very-negative-color"></span>
            <span>Very Negative ({distribution.very_negative})</span>
          </div>
          <div className="legend-item">
            <span className="legend-color negative-color"></span>
            <span>Negative ({distribution.negative})</span>
          </div>
          <div className="legend-item">
            <span className="legend-color neutral-color"></span>
            <span>Neutral ({distribution.neutral})</span>
          </div>
          <div className="legend-item">
            <span className="legend-color positive-color"></span>
            <span>Positive ({distribution.positive})</span>
          </div>
          <div className="legend-item">
            <span className="legend-color very-positive-color"></span>
            <span>Very Positive ({distribution.very_positive})</span>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="sentiment-statistics">
        <div className="stat-item">
          <span className="stat-label">Positive Ratio</span>
          <span className="stat-value positive">{statistics.positive_ratio}%</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Negative Ratio</span>
          <span className="stat-value negative">{statistics.negative_ratio}%</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Max Positive</span>
          <span className="stat-value">{statistics.max_positive}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">Min Negative</span>
          <span className="stat-value">{statistics.min_negative}</span>
        </div>
      </div>

      {/* Recent News */}
      <div className="recent-news">
        <h3>Recent News Headlines</h3>
        <div className="news-list">
          {news.map((item, idx) => (
            <div 
              key={idx} 
              className="news-item"
              style={{ borderLeftColor: getSentimentColor(item.sentiment.score) }}
            >
              <div className="news-header">
                <span className="news-sentiment-emoji">{item.sentiment.emoji}</span>
                <a 
                  href={item.link} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="news-title"
                >
                  {item.title}
                </a>
              </div>
              <div className="news-meta">
                <span className="news-publisher">{item.publisher}</span>
                <span className="news-date">
                  {new Date(item.published_at).toLocaleDateString()}
                </span>
                <span 
                  className="news-sentiment-label"
                  style={{ color: getSentimentColor(item.sentiment.score) }}
                >
                  {item.sentiment.label} ({item.sentiment.score.toFixed(3)})
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default SentimentCard;