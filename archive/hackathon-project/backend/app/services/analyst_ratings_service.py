"""
Analyst Ratings Service - Professional analyst ratings and price targets
"""

import yfinance as yf
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor

class AnalystRatingsService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.rating_scale = {
            1: 'Strong Buy',
            2: 'Buy', 
            3: 'Hold',
            4: 'Sell',
            5: 'Strong Sell'
        }
    
    async def get_ratings_consensus(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive analyst ratings and consensus"""
        try:
            # Get analyst data from Yahoo Finance
            analyst_data = await self._fetch_analyst_data(ticker)
            
            # Process ratings and recommendations
            ratings_summary = self._process_ratings(analyst_data)
            
            # Get price targets
            price_targets = self._process_price_targets(analyst_data)
            
            # Calculate consensus metrics
            consensus_metrics = self._calculate_consensus_metrics(ratings_summary, price_targets)
            
            return {
                'ticker': ticker,
                'ratings_summary': ratings_summary,
                'price_targets': price_targets,
                'consensus_metrics': consensus_metrics,
                'analyst_count': analyst_data.get('analyst_count', 0),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    async def _fetch_analyst_data(self, ticker: str) -> Dict[str, Any]:
        """Fetch analyst data from Yahoo Finance"""
        
        def _get_data():
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get analyst recommendations
            recommendations = stock.recommendations
            
            # Extract analyst info from stock info
            analyst_info = {
                'target_mean_price': info.get('targetMeanPrice'),
                'target_high_price': info.get('targetHighPrice'),
                'target_low_price': info.get('targetLowPrice'),
                'recommendation_mean': info.get('recommendationMean'),
                'recommendation_key': info.get('recommendationKey'),
                'number_of_analyst_opinions': info.get('numberOfAnalystOpinions'),
                'current_price': info.get('currentPrice', info.get('regularMarketPrice'))
            }
            
            return {
                'info': analyst_info,
                'recommendations': recommendations,
                'analyst_count': info.get('numberOfAnalystOpinions', 0)
            }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _get_data)
    
    def _process_ratings(self, analyst_data: Dict) -> Dict[str, Any]:
        """Process analyst ratings and recommendations"""
        info = analyst_data.get('info', {})
        recommendations_df = analyst_data.get('recommendations')
        
        # Current consensus rating
        recommendation_mean = info.get('recommendation_mean')
        recommendation_key = info.get('recommendation_key', 'hold')
        
        # Process historical recommendations if available
        rating_distribution = {}
        if recommendations_df is not None and not recommendations_df.empty:
            # Get most recent recommendations
            recent_recs = recommendations_df.tail(12)  # Last 12 months
            
            # Count rating distribution
            for rating in ['strongBuy', 'buy', 'hold', 'sell', 'strongSell']:
                if rating in recent_recs.columns:
                    rating_distribution[rating] = recent_recs[rating].iloc[-1] if len(recent_recs) > 0 else 0
                else:
                    rating_distribution[rating] = 0
        else:
            # Default distribution if no data
            rating_distribution = {
                'strongBuy': 0,
                'buy': 0, 
                'hold': 0,
                'sell': 0,
                'strongSell': 0
            }
        
        return {
            'consensus_rating': recommendation_key.title() if recommendation_key else 'Hold',
            'consensus_score': recommendation_mean,
            'rating_distribution': rating_distribution,
            'total_analysts': sum(rating_distribution.values()),
            'rating_breakdown': self._calculate_rating_percentages(rating_distribution)
        }
    
    def _process_price_targets(self, analyst_data: Dict) -> Dict[str, Any]:
        """Process analyst price targets"""
        info = analyst_data.get('info', {})
        
        target_mean = info.get('target_mean_price')
        target_high = info.get('target_high_price') 
        target_low = info.get('target_low_price')
        current_price = info.get('current_price')
        
        # Calculate upside/downside
        upside_potential = None
        if target_mean and current_price:
            upside_potential = ((target_mean - current_price) / current_price) * 100
        
        return {
            'mean_target': target_mean,
            'high_target': target_high,
            'low_target': target_low,
            'current_price': current_price,
            'upside_potential': upside_potential,
            'target_range': {
                'low': target_low,
                'high': target_high,
                'spread': (target_high - target_low) if (target_high and target_low) else None
            }
        }
    
    def _calculate_consensus_metrics(self, ratings_summary: Dict, price_targets: Dict) -> Dict[str, Any]:
        """Calculate overall consensus metrics"""
        
        # Analyst sentiment score (1-5 scale, lower is better)
        consensus_score = ratings_summary.get('consensus_score', 3.0)
        
        # Convert to sentiment classification
        if consensus_score <= 1.5:
            sentiment = 'Very Bullish'
        elif consensus_score <= 2.5:
            sentiment = 'Bullish'
        elif consensus_score <= 3.5:
            sentiment = 'Neutral'
        elif consensus_score <= 4.5:
            sentiment = 'Bearish'
        else:
            sentiment = 'Very Bearish'
        
        # Calculate conviction level based on rating distribution
        rating_dist = ratings_summary.get('rating_distribution', {})
        total_analysts = ratings_summary.get('total_analysts', 1)
        
        # High conviction if most analysts agree (>60% in buy/sell categories)
        buy_percentage = ((rating_dist.get('strongBuy', 0) + rating_dist.get('buy', 0)) / total_analysts * 100) if total_analysts > 0 else 0
        sell_percentage = ((rating_dist.get('strongSell', 0) + rating_dist.get('sell', 0)) / total_analysts * 100) if total_analysts > 0 else 0
        
        if buy_percentage > 60 or sell_percentage > 60:
            conviction = 'High'
        elif buy_percentage > 40 or sell_percentage > 40:
            conviction = 'Medium'
        else:
            conviction = 'Low'
        
        return {
            'analyst_sentiment': sentiment,
            'conviction_level': conviction,
            'buy_percentage': buy_percentage,
            'sell_percentage': sell_percentage,
            'consensus_strength': max(buy_percentage, sell_percentage),
            'price_target_confidence': self._assess_price_target_confidence(price_targets)
        }
    
    def _calculate_rating_percentages(self, rating_distribution: Dict) -> Dict[str, float]:
        """Calculate percentage breakdown of ratings"""
        total = sum(rating_distribution.values())
        if total == 0:
            return {rating: 0.0 for rating in rating_distribution.keys()}
        
        return {
            rating: (count / total) * 100 
            for rating, count in rating_distribution.items()
        }
    
    def _assess_price_target_confidence(self, price_targets: Dict) -> str:
        """Assess confidence level in price targets"""
        target_range = price_targets.get('target_range', {})
        spread = target_range.get('spread')
        mean_target = price_targets.get('mean_target')
        
        if not spread or not mean_target:
            return 'Low'
        
        # Calculate spread as percentage of mean target
        spread_percentage = (spread / mean_target) * 100
        
        if spread_percentage < 20:
            return 'High'  # Tight range indicates consensus
        elif spread_percentage < 40:
            return 'Medium'
        else:
            return 'Low'  # Wide range indicates disagreement