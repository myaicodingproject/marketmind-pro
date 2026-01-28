#!/usr/bin/env python3
"""
Section 1 Agent - Executive Summary Generator
Generates institutional-grade executive summaries with investment recommendations
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import yfinance as yf
import requests
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class ExecutiveSummaryData:
    ticker: str
    recommendation: str
    price_target: float
    current_price: float
    upside_potential: float
    confidence_level: str
    key_metrics: Dict[str, Any]
    investment_thesis: List[str]
    risk_factors: List[str]
    valuation_summary: Dict[str, Any]

class Section1ExecutiveSummaryAgent:
    """Section 1 agent for generating executive summaries"""
    
    def __init__(self):
        self.data_repository = {}
        
    async def generate_executive_summary(self, ticker: str) -> Dict[str, Any]:
        """Generate comprehensive executive summary for given ticker"""
        try:
            # Step 1: Gather financial data
            financial_data = await self._get_financial_data(ticker)
            
            # Step 2: Perform web research
            web_data = await self._get_web_research(ticker)
            
            # Step 3: Generate investment recommendation
            recommendation_data = await self._generate_recommendation(ticker, financial_data, web_data)
            
            # Step 4: Create executive summary
            summary = await self._create_executive_summary(ticker, financial_data, web_data, recommendation_data)
            
            # Step 5: Store in central repository
            self._store_data(ticker, summary)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating executive summary for {ticker}: {e}")
            raise
    
    async def _get_financial_data(self, ticker: str) -> Dict[str, Any]:
        """Get current financial data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Get historical data for trends
            hist = stock.history(period="1y")
            
            return {
                "current_price": info.get("currentPrice", 0),
                "market_cap": info.get("marketCap", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "revenue_ttm": info.get("totalRevenue", 0),
                "profit_margin": info.get("profitMargins", 0),
                "roe": info.get("returnOnEquity", 0),
                "debt_to_equity": info.get("debtToEquity", 0),
                "52_week_high": info.get("fiftyTwoWeekHigh", 0),
                "52_week_low": info.get("fiftyTwoWeekLow", 0),
                "analyst_target": info.get("targetMeanPrice", 0),
                "recommendation": info.get("recommendationKey", "hold"),
                "sector": info.get("sector", "Unknown"),
                "industry": info.get("industry", "Unknown"),
                "business_summary": info.get("longBusinessSummary", ""),
                "historical_data": hist.tail(30).to_dict() if not hist.empty else {}
            }
        except Exception as e:
            logger.error(f"Error fetching financial data for {ticker}: {e}")
            return {}
    
    async def _get_web_research(self, ticker: str) -> Dict[str, Any]:
        """Get latest news and market sentiment"""
        try:
            stock = yf.Ticker(ticker)
            news = stock.news
            
            # Process news for sentiment
            recent_news = []
            for article in news[:5]:  # Get last 5 articles
                recent_news.append({
                    "title": article.get("title", ""),
                    "summary": article.get("summary", ""),
                    "published": article.get("providerPublishTime", 0),
                    "source": article.get("publisher", "")
                })
            
            return {
                "recent_news": recent_news,
                "news_sentiment": self._analyze_news_sentiment(recent_news),
                "market_trends": self._get_market_trends(ticker)
            }
        except Exception as e:
            logger.error(f"Error fetching web research for {ticker}: {e}")
            return {"recent_news": [], "news_sentiment": "neutral", "market_trends": {}}
    
    def _analyze_news_sentiment(self, news_articles: List[Dict]) -> str:
        """Simple sentiment analysis based on keywords"""
        positive_words = ["growth", "profit", "beat", "strong", "positive", "upgrade", "buy"]
        negative_words = ["loss", "decline", "weak", "negative", "downgrade", "sell", "risk"]
        
        positive_count = 0
        negative_count = 0
        
        for article in news_articles:
            text = (article.get("title", "") + " " + article.get("summary", "")).lower()
            positive_count += sum(1 for word in positive_words if word in text)
            negative_count += sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count * 1.2:
            return "positive"
        elif negative_count > positive_count * 1.2:
            return "negative"
        else:
            return "neutral"
    
    def _get_market_trends(self, ticker: str) -> Dict[str, Any]:
        """Get basic market trend analysis"""
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="3mo")
            
            if hist.empty:
                return {}
            
            current_price = hist['Close'].iloc[-1]
            price_30d_ago = hist['Close'].iloc[-30] if len(hist) >= 30 else hist['Close'].iloc[0]
            
            return {
                "30_day_return": ((current_price - price_30d_ago) / price_30d_ago * 100) if price_30d_ago > 0 else 0,
                "volatility": hist['Close'].pct_change().std() * 100,
                "volume_trend": "increasing" if hist['Volume'].tail(5).mean() > hist['Volume'].head(5).mean() else "decreasing"
            }
        except Exception as e:
            logger.error(f"Error calculating market trends for {ticker}: {e}")
            return {}
    
    async def _generate_recommendation(self, ticker: str, financial_data: Dict, web_data: Dict) -> Dict[str, Any]:
        """Generate investment recommendation based on data"""
        try:
            # Simple scoring algorithm
            score = 0
            
            # Financial metrics scoring
            if financial_data.get("pe_ratio", 0) > 0:
                if financial_data["pe_ratio"] < 15:
                    score += 2
                elif financial_data["pe_ratio"] < 25:
                    score += 1
                else:
                    score -= 1
            
            if financial_data.get("roe", 0) > 0.15:
                score += 2
            elif financial_data.get("roe", 0) > 0.10:
                score += 1
            
            if financial_data.get("debt_to_equity", 0) < 0.5:
                score += 1
            
            # Market sentiment scoring
            sentiment = web_data.get("news_sentiment", "neutral")
            if sentiment == "positive":
                score += 2
            elif sentiment == "negative":
                score -= 2
            
            # Market trends scoring
            trends = web_data.get("market_trends", {})
            if trends.get("30_day_return", 0) > 5:
                score += 1
            elif trends.get("30_day_return", 0) < -5:
                score -= 1
            
            # Generate recommendation
            if score >= 4:
                recommendation = "BUY"
                confidence = "High"
            elif score >= 2:
                recommendation = "BUY"
                confidence = "Medium"
            elif score >= 0:
                recommendation = "HOLD"
                confidence = "Medium"
            elif score >= -2:
                recommendation = "HOLD"
                confidence = "Low"
            else:
                recommendation = "SELL"
                confidence = "Medium"
            
            # Calculate price target
            current_price = financial_data.get("current_price", 0)
            analyst_target = financial_data.get("analyst_target", current_price)
            
            if recommendation == "BUY":
                price_target = max(current_price * 1.15, analyst_target)
            elif recommendation == "SELL":
                price_target = min(current_price * 0.85, analyst_target)
            else:
                price_target = analyst_target or current_price
            
            upside_potential = ((price_target - current_price) / current_price * 100) if current_price > 0 else 0
            
            return {
                "recommendation": recommendation,
                "price_target": round(price_target, 2),
                "upside_potential": round(upside_potential, 1),
                "confidence_level": confidence,
                "score": score
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendation for {ticker}: {e}")
            return {
                "recommendation": "HOLD",
                "price_target": financial_data.get("current_price", 0),
                "upside_potential": 0,
                "confidence_level": "Low",
                "score": 0
            }
    
    async def _create_executive_summary(self, ticker: str, financial_data: Dict, web_data: Dict, recommendation_data: Dict) -> Dict[str, Any]:
        """Create the final executive summary"""
        
        # Generate investment thesis points
        investment_thesis = []
        if financial_data.get("roe", 0) > 0.15:
            investment_thesis.append(f"Strong ROE of {financial_data['roe']:.1%} indicates efficient capital allocation")
        
        if financial_data.get("profit_margin", 0) > 0.10:
            investment_thesis.append(f"Healthy profit margin of {financial_data['profit_margin']:.1%} shows operational efficiency")
        
        if web_data.get("news_sentiment") == "positive":
            investment_thesis.append("Positive market sentiment and recent news coverage")
        
        # Generate risk factors
        risk_factors = []
        if financial_data.get("debt_to_equity", 0) > 1.0:
            risk_factors.append(f"High debt-to-equity ratio of {financial_data['debt_to_equity']:.2f}")
        
        if financial_data.get("pe_ratio", 0) > 30:
            risk_factors.append(f"High P/E ratio of {financial_data['pe_ratio']:.1f} suggests potential overvaluation")
        
        if web_data.get("news_sentiment") == "negative":
            risk_factors.append("Negative market sentiment and recent news coverage")
        
        # Create key metrics summary
        key_metrics = {
            "market_cap": financial_data.get("market_cap", 0),
            "pe_ratio": financial_data.get("pe_ratio", 0),
            "revenue_ttm": financial_data.get("revenue_ttm", 0),
            "profit_margin": financial_data.get("profit_margin", 0),
            "roe": financial_data.get("roe", 0),
            "52_week_range": {
                "high": financial_data.get("52_week_high", 0),
                "low": financial_data.get("52_week_low", 0)
            }
        }
        
        return {
            "ticker": ticker,
            "generated_at": datetime.now().isoformat(),
            "recommendation": recommendation_data["recommendation"],
            "price_target": recommendation_data["price_target"],
            "current_price": financial_data.get("current_price", 0),
            "upside_potential": recommendation_data["upside_potential"],
            "confidence_level": recommendation_data["confidence_level"],
            "key_metrics": key_metrics,
            "investment_thesis": investment_thesis,
            "risk_factors": risk_factors,
            "business_summary": financial_data.get("business_summary", ""),
            "sector": financial_data.get("sector", ""),
            "industry": financial_data.get("industry", ""),
            "market_sentiment": web_data.get("news_sentiment", "neutral"),
            "recent_news_count": len(web_data.get("recent_news", [])),
            "valuation_summary": {
                "current_valuation": "Fair" if abs(recommendation_data["upside_potential"]) < 10 else ("Undervalued" if recommendation_data["upside_potential"] > 0 else "Overvalued"),
                "peer_comparison": "Market average",  # Placeholder
                "historical_comparison": "In line with historical averages"  # Placeholder
            }
        }
    
    def _store_data(self, ticker: str, summary_data: Dict[str, Any]):
        """Store data in central repository for consistency across sections"""
        self.data_repository[ticker] = {
            "executive_summary": summary_data,
            "last_updated": datetime.now().isoformat()
        }
        logger.info(f"Stored executive summary data for {ticker}")
    
    def get_stored_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored data for consistency across sections"""
        return self.data_repository.get(ticker)
    
    async def generate_charts_data(self, ticker: str, summary_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate chart data matching AVGO sample style"""
        try:
            # Price trend chart data
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")
            
            price_chart = {
                "type": "line",
                "title": f"{ticker} Stock Price Trend (12 Months)",
                "data": {
                    "labels": [date.strftime("%Y-%m") for date in hist.index[-12:]],
                    "datasets": [{
                        "label": "Stock Price",
                        "data": hist['Close'].tail(12).tolist(),
                        "borderColor": "#2563eb",
                        "backgroundColor": "rgba(37, 99, 235, 0.1)"
                    }]
                }
            }
            
            # Key metrics comparison chart
            metrics_chart = {
                "type": "bar",
                "title": "Key Financial Metrics",
                "data": {
                    "labels": ["P/E Ratio", "ROE (%)", "Profit Margin (%)", "Debt/Equity"],
                    "datasets": [{
                        "label": ticker,
                        "data": [
                            summary_data["key_metrics"]["pe_ratio"],
                            summary_data["key_metrics"]["roe"] * 100,
                            summary_data["key_metrics"]["profit_margin"] * 100,
                            summary_data["key_metrics"].get("debt_to_equity", 0)
                        ],
                        "backgroundColor": ["#10b981", "#f59e0b", "#3b82f6", "#ef4444"]
                    }]
                }
            }
            
            return {
                "price_trend": price_chart,
                "key_metrics": metrics_chart
            }
            
        except Exception as e:
            logger.error(f"Error generating charts for {ticker}: {e}")
            return {}

# Usage example
async def main():
    agent = Section1ExecutiveSummaryAgent()
    summary = await agent.generate_executive_summary("AAPL")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    asyncio.run(main())