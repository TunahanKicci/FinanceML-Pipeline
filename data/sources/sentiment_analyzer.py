# data/sources/sentiment_analyzer.py
"""
News sentiment analysis for stocks
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import requests
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta
import logging
from typing import Dict, List
import re

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except:
    TEXTBLOB_AVAILABLE = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except:
    VADER_AVAILABLE = False

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Stock news sentiment analyzer"""
    
    def __init__(self, min_news_threshold=3, news_api_key=None):
        self.min_news_threshold = min_news_threshold
        self.news_api_key = news_api_key
        self.vader_analyzer = SentimentIntensityAnalyzer() if VADER_AVAILABLE else None
        
        # Sentiment keywords
        self.positive_words = {
            'strong': ['surge', 'soar', 'boom', 'rally', 'bullish', 'profit', 'gain',
                      'success', 'strong', 'excellent', 'outstanding', 'record', 'high',
                      'upgrade', 'buy', 'positive', 'growth', 'increase', 'rise'],
            'medium': ['good', 'better', 'improve', 'favorable', 'optimistic', 'stable'],
            'light': ['steady', 'maintain', 'hold', 'continue']
        }
        
        self.negative_words = {
            'strong': ['crash', 'collapse', 'plunge', 'dive', 'bearish', 'loss',
                      'decline', 'drop', 'fall', 'weak', 'terrible', 'crisis', 'panic'],
            'medium': ['bad', 'poor', 'concern', 'worry', 'uncertain', 'volatile'],
            'light': ['pause', 'halt', 'delay', 'postpone']
        }
    
    def get_news(self, symbol: str, days: int = 7) -> List[Dict]:
        """Fetch news from News API (English only)"""
        if not self.news_api_key:
            logger.warning("News API key not provided, returning empty list")
            return []

        try:
            company_name = symbol
            query = f'"{company_name}"'

            url = "https://newsapi.org/v2/everything"
            params = {
                'q': query,
                'apiKey': self.news_api_key,
                'language': 'en',
                'sortBy': 'publishedAt',
                'pageSize': 50,
                'from': (datetime.now() - timedelta(days=days)).date().isoformat()
            }

            response = requests.get(url, params=params, timeout=10)
            news_list = []

            if response.status_code == 200:
                data = response.json()
                articles = data.get('articles', [])

                for article in articles:
                    if not article.get('title'):
                        continue

                    pub_time = article.get('publishedAt', None)
                    news_item = {
                        'title': article['title'],
                        'publisher': article.get('source', {}).get('name', 'News API'),
                        'link': article.get('url', ''),
                        'published_at': pub_time,
                        'content': article.get('content') or article.get('description') or article['title']
                    }
                    news_list.append(news_item)

                logger.info(f"Found {len(news_list)} news articles via News API")
            else:
                logger.error(f"News API error: {response.status_code} - {response.text}")

            return news_list

        except Exception as e:
            logger.error(f"Error fetching news from News API: {e}")
            return []
    
    def calculate_sentiment_score(self, text: str) -> float:
        """Calculate weighted sentiment score"""
        if not text:
            return 0.0
        
        text_lower = text.lower()
        words = text_lower.split()
        
        total_score = 0
        word_count = 0
        
        for word in words:
            # Positive words
            for strength, word_list in self.positive_words.items():
                if any(pos_word in word for pos_word in word_list):
                    if strength == 'strong':
                        total_score += 3
                    elif strength == 'medium':
                        total_score += 2
                    else:
                        total_score += 1
                    word_count += 1
                    break
            
            # Negative words
            for strength, word_list in self.negative_words.items():
                if any(neg_word in word for neg_word in word_list):
                    if strength == 'strong':
                        total_score -= 3
                    elif strength == 'medium':
                        total_score -= 2
                    else:
                        total_score -= 1
                    word_count += 1
                    break
        
        if word_count == 0:
            return 0.0
        
        avg_score = total_score / word_count
        normalized = max(-1.0, min(1.0, avg_score / 3.0))
        
        return normalized
    
    def analyze_sentiment_hybrid(self, text: str) -> Dict:
        """Hybrid sentiment analysis using multiple methods"""
        if not text:
            return {
                'score': 0.0,
                'label': 'Neutral',
                'confidence': 0.0,
                'method': 'none'
            }
        
        scores = []
        methods = []
        
        # Custom scoring
        custom_score = self.calculate_sentiment_score(text)
        scores.append(custom_score)
        methods.append('custom')
        
        # VADER (if available)
        if VADER_AVAILABLE and self.vader_analyzer:
            try:
                vader_scores = self.vader_analyzer.polarity_scores(text)
                scores.append(vader_scores['compound'])
                methods.append('vader')
            except:
                pass
        
        # TextBlob (if available)
        if TEXTBLOB_AVAILABLE:
            try:
                blob = TextBlob(text)
                scores.append(blob.sentiment.polarity)
                methods.append('textblob')
            except:
                pass
        
        # Weighted average (custom score has more weight)
        if len(scores) > 1:
            weights = [2.0] + [1.0] * (len(scores) - 1)
            final_score = np.average(scores, weights=weights)
        else:
            final_score = scores[0] if scores else 0.0
        
        # Label
        if final_score > 0.3:
            label = 'Very Positive'
            emoji = '🚀'
        elif final_score > 0.1:
            label = 'Positive'
            emoji = '📈'
        elif final_score < -0.3:
            label = 'Very Negative'
            emoji = '📉'
        elif final_score < -0.1:
            label = 'Negative'
            emoji = '⚠️'
        else:
            label = 'Neutral'
            emoji = '➡️'
        
        confidence = min(abs(final_score) * 100, 100)
        
        return {
            'score': round(final_score, 3),
            'label': label,
            'emoji': emoji,
            'confidence': round(confidence, 2),
            'method': '+'.join(methods)
        }
    
    def analyze_stock_sentiment(
        self, 
        symbol: str, 
        days: int = 7
    ) -> Dict:
        """
        Analyze sentiment for a stock
        
        Returns:
            Dict with sentiment analysis results
        """
        try:
            logger.info(f"Analyzing sentiment for {symbol}")
            
            # Get news
            news_list = self.get_news(symbol, days)
            
            if len(news_list) < self.min_news_threshold:
                return {
                    'symbol': symbol,
                    'error': f'Insufficient news data: {len(news_list)} articles found, minimum {self.min_news_threshold} required',
                    'total_news': len(news_list),
                    'analyzed_news': []
                }
            
            # Analyze each news item
            analyzed_news = []
            all_scores = []
            
            for news in news_list:
                sentiment = self.analyze_sentiment_hybrid(news['content'])
                all_scores.append(sentiment['score'])
                
                analyzed_news.append({
                    'title': news['title'],
                    'publisher': news['publisher'],
                    'published_at': news['published_at'],
                    'link': news['link'],
                    'sentiment': sentiment
                })
            
            # Overall sentiment
            if all_scores:
                overall_score = float(np.mean(all_scores))
                median_score = float(np.median(all_scores))
                std_score = float(np.std(all_scores))
                
                # Distribution
                very_positive = sum(1 for s in all_scores if s > 0.3)
                positive = sum(1 for s in all_scores if 0.1 < s <= 0.3)
                neutral = sum(1 for s in all_scores if -0.1 <= s <= 0.1)
                negative = sum(1 for s in all_scores if -0.3 <= s < -0.1)
                very_negative = sum(1 for s in all_scores if s < -0.3)
                
                # Label
                if overall_score > 0.3:
                    overall_label = 'Very Positive'
                    overall_emoji = '🚀'
                elif overall_score > 0.1:
                    overall_label = 'Positive'
                    overall_emoji = '📈'
                elif overall_score < -0.3:
                    overall_label = 'Very Negative'
                    overall_emoji = '📉'
                elif overall_score < -0.1:
                    overall_label = 'Negative'
                    overall_emoji = '⚠️'
                else:
                    overall_label = 'Neutral'
                    overall_emoji = '➡️'
                
                confidence = min(abs(overall_score) * 100, 100)
            else:
                overall_score = median_score = std_score = confidence = 0
                overall_label = 'No Data'
                overall_emoji = '❓'
                very_positive = positive = neutral = negative = very_negative = 0
            
            result = {
                'symbol': symbol,
                'analysis_date': datetime.now().isoformat(),
                'analysis_period_days': days,
                'total_news': len(analyzed_news),
                'overall_sentiment': {
                    'score': round(overall_score, 4),
                    'median_score': round(median_score, 4),
                    'volatility': round(std_score, 4),
                    'label': overall_label,
                    'emoji': overall_emoji,
                    'confidence': round(confidence, 2)
                },
                'distribution': {
                    'very_positive': very_positive,
                    'positive': positive,
                    'neutral': neutral,
                    'negative': negative,
                    'very_negative': very_negative
                },
                'news': analyzed_news[:10],  # Top 10 most recent
                'statistics': {
                    'max_positive': round(max(all_scores), 3) if all_scores else 0,
                    'min_negative': round(min(all_scores), 3) if all_scores else 0,
                    'positive_ratio': round((very_positive + positive) / max(len(all_scores), 1) * 100, 1),
                    'negative_ratio': round((very_negative + negative) / max(len(all_scores), 1) * 100, 1)
                }
            }
            
            logger.info(f"Sentiment analysis complete: {overall_label} ({overall_score:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            raise


# Test
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    analyzer = SentimentAnalyzer(min_news_threshold=1)
    result = analyzer.analyze_stock_sentiment("AAPL", days=15)
    
    print("\n" + "="*60)
    print("SENTIMENT ANALYSIS")
    print("="*60)
    print(f"Symbol: {result['symbol']}")
    print(f"Total News: {result['total_news']}")
    print(f"\nOverall Sentiment: {result['overall_sentiment']['label']} {result['overall_sentiment']['emoji']}")
    print(f"Score: {result['overall_sentiment']['score']}")
    print(f"Confidence: {result['overall_sentiment']['confidence']}%")
    print(f"\nDistribution:")
    print(f"  Very Positive: {result['distribution']['very_positive']}")
    print(f"  Positive: {result['distribution']['positive']}")
    print(f"  Neutral: {result['distribution']['neutral']}")
    print(f"  Negative: {result['distribution']['negative']}")
    print(f"  Very Negative: {result['distribution']['very_negative']}")