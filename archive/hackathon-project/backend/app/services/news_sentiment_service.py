"""
News Sentiment Service - News analysis and sentiment scoring
"""

import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
from textblob import TextBlob
import re

class NewsSentimentService:
    def __init__(self):
        self.news_sources = [
            'https://newsapi.org/v2/everything',
            'https://api.marketaux.com/v1/news/all'
        ]
    
    async def get_sentiment_analysis(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive news sentiment analysis"""
        try:
            # Get news from multiple sources
            news_data = await self._fetch_news_data(ticker)
            
            # Analyze sentiment
            sentiment_analysis = self._analyze_sentiment(news_data)
            
            # Calculate sentiment scores
            sentiment_scores = self._calculate_sentiment_scores(sentiment_analysis)
            
            return {
                'ticker': ticker,
                'news_count': len(news_data),
                'sentiment_scores': sentiment_scores,
                'recent_headlines': self._get_recent_headlines(news_data),
                'sentiment_trend': self._calculate_sentiment_trend(sentiment_analysis),
                'key_themes': self._extract_key_themes(news_data),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _fetch_news_data(self, ticker: str) -> List[Dict]:
        """Fetch news data from multiple sources"""
        news_articles = []
        
        # Simulate news data (in production, would use real APIs)
        sample_news = [
            {
                'title': f'{ticker} Reports Strong Q3 Earnings Beat',
                'description': f'{ticker} exceeded analyst expectations with strong revenue growth',
                'published_at': (datetime.now() - timedelta(days=1)).isoformat(),
                'source': 'Financial News',
                'url': f'https://example.com/news/{ticker}-earnings'
            },
            {
                'title': f'Analysts Upgrade {ticker} Price Target',
                'description': f'Multiple analysts raise price targets for {ticker} following positive outlook',
                'published_at': (datetime.now() - timedelta(days=2)).isoformat(),
                'source': 'Market Watch',
                'url': f'https://example.com/news/{ticker}-upgrade'
            },
            {
                'title': f'{ticker} Faces Regulatory Challenges',
                'description': f'New regulations may impact {ticker} business operations',
                'published_at': (datetime.now() - timedelta(days=3)).isoformat(),
                'source': 'Reuters',
                'url': f'https://example.com/news/{ticker}-regulation'
            }
        ]
        
        return sample_news
    
    def _analyze_sentiment(self, news_data: List[Dict]) -> List[Dict]:
        """Analyze sentiment of news articles"""
        analyzed_articles = []
        
        for article in news_data:
            # Combine title and description for analysis
            text = f"{article.get('title', '')} {article.get('description', '')}"
            
            # Use TextBlob for sentiment analysis
            blob = TextBlob(text)
            sentiment = blob.sentiment
            
            # Classify sentiment
            if sentiment.polarity > 0.1:
                sentiment_label = 'positive'
            elif sentiment.polarity < -0.1:
                sentiment_label = 'negative'
            else:
                sentiment_label = 'neutral'
            
            analyzed_articles.append({
                **article,
                'sentiment_score': sentiment.polarity,
                'sentiment_label': sentiment_label,
                'subjectivity': sentiment.subjectivity
            })
        
        return analyzed_articles
    
    def _calculate_sentiment_scores(self, analyzed_articles: List[Dict]) -> Dict[str, Any]:
        """Calculate overall sentiment scores"""
        if not analyzed_articles:
            return {}
        
        sentiments = [article['sentiment_score'] for article in analyzed_articles]
        sentiment_labels = [article['sentiment_label'] for article in analyzed_articles]
        
        # Calculate metrics
        avg_sentiment = sum(sentiments) / len(sentiments)
        positive_count = sentiment_labels.count('positive')
        negative_count = sentiment_labels.count('negative')
        neutral_count = sentiment_labels.count('neutral')
        
        total_articles = len(analyzed_articles)
        
        return {
            'overall_sentiment': avg_sentiment,
            'sentiment_classification': self._classify_overall_sentiment(avg_sentiment),
            'positive_percentage': (positive_count / total_articles) * 100,
            'negative_percentage': (negative_count / total_articles) * 100,
            'neutral_percentage': (neutral_count / total_articles) * 100,
            'sentiment_strength': abs(avg_sentiment),
            'articles_analyzed': total_articles
        }
    
    def _classify_overall_sentiment(self, score: float) -> str:
        """Classify overall sentiment based on score"""
        if score > 0.2:
            return 'Very Positive'
        elif score > 0.05:
            return 'Positive'
        elif score > -0.05:
            return 'Neutral'
        elif score > -0.2:
            return 'Negative'
        else:
            return 'Very Negative'
    
    def _get_recent_headlines(self, news_data: List[Dict]) -> List[Dict]:
        """Get most recent headlines with sentiment"""
        # Sort by date and take top 5
        sorted_news = sorted(news_data, 
                           key=lambda x: x.get('published_at', ''), 
                           reverse=True)
        
        return [{
            'title': article['title'],
            'published_at': article['published_at'],
            'source': article.get('source', 'Unknown'),
            'sentiment_score': getattr(TextBlob(article['title']), 'sentiment', {}).polarity
        } for article in sorted_news[:5]]
    
    def _calculate_sentiment_trend(self, analyzed_articles: List[Dict]) -> Dict[str, Any]:
        """Calculate sentiment trend over time"""
        # Group articles by day
        daily_sentiment = {}
        
        for article in analyzed_articles:
            try:
                date = datetime.fromisoformat(article['published_at'].replace('Z', '+00:00'))
                day_key = date.strftime('%Y-%m-%d')
                
                if day_key not in daily_sentiment:
                    daily_sentiment[day_key] = []
                
                daily_sentiment[day_key].append(article['sentiment_score'])
            except:
                continue
        
        # Calculate daily averages
        trend_data = []
        for day, scores in daily_sentiment.items():
            avg_score = sum(scores) / len(scores)
            trend_data.append({
                'date': day,
                'sentiment_score': avg_score,
                'article_count': len(scores)
            })
        
        # Sort by date
        trend_data.sort(key=lambda x: x['date'])
        
        return {
            'daily_sentiment': trend_data,
            'trend_direction': self._determine_trend_direction(trend_data)
        }
    
    def _determine_trend_direction(self, trend_data: List[Dict]) -> str:
        """Determine if sentiment is improving or declining"""
        if len(trend_data) < 2:
            return 'Insufficient Data'
        
        recent_scores = [day['sentiment_score'] for day in trend_data[-3:]]  # Last 3 days
        earlier_scores = [day['sentiment_score'] for day in trend_data[:-3]]  # Earlier days
        
        if not earlier_scores:
            return 'Insufficient Data'
        
        recent_avg = sum(recent_scores) / len(recent_scores)
        earlier_avg = sum(earlier_scores) / len(earlier_scores)
        
        if recent_avg > earlier_avg + 0.05:
            return 'Improving'
        elif recent_avg < earlier_avg - 0.05:
            return 'Declining'
        else:
            return 'Stable'
    
    def _extract_key_themes(self, news_data: List[Dict]) -> List[str]:
        """Extract key themes from news articles"""
        # Simple keyword extraction (would use more sophisticated NLP in production)
        all_text = ' '.join([
            f"{article.get('title', '')} {article.get('description', '')}"
            for article in news_data
        ]).lower()
        
        # Common financial themes
        themes = {
            'earnings': ['earnings', 'profit', 'revenue', 'income'],
            'growth': ['growth', 'expansion', 'increase', 'rising'],
            'regulation': ['regulation', 'regulatory', 'compliance', 'legal'],
            'competition': ['competition', 'competitor', 'market share'],
            'innovation': ['innovation', 'technology', 'product', 'development'],
            'management': ['ceo', 'management', 'leadership', 'executive']
        }
        
        detected_themes = []
        for theme, keywords in themes.items():
            if any(keyword in all_text for keyword in keywords):
                detected_themes.append(theme.title())
        
        return detected_themes[:5]  # Top 5 themes