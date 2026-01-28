"""
Section 4 Integration Service - Market Position & Competitive Analysis
Integrates Section 4 agent with the main MarketMind Pro application
"""

import asyncio
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from .section4_market_competitive_agent import Section4MarketCompetitiveAgent
from .kiro_prompt_service import kiro_service

logger = logging.getLogger(__name__)

class Section4IntegrationService:
    """Integration service for Section 4 competitive analysis"""
    
    def __init__(self):
        self.agent = Section4MarketCompetitiveAgent()
        self.cache = {}
        self.cache_ttl = 3600  # 1 hour cache
    
    async def generate_section4_report(self, ticker: str, use_cache: bool = True) -> Dict[str, Any]:
        """Generate Section 4 competitive analysis report"""
        
        # Check cache first
        if use_cache and self._is_cached(ticker):
            logger.info(f"Returning cached Section 4 data for {ticker}")
            return self.cache[ticker]["data"]
        
        try:
            logger.info(f"Generating Section 4 analysis for {ticker}")
            
            # Generate comprehensive competitive analysis
            analysis = await self.agent.generate_competitive_analysis(ticker)
            
            # Format for report integration
            formatted_report = self._format_for_report(analysis)
            
            # Cache the results
            if use_cache:
                self._cache_data(ticker, formatted_report)
            
            logger.info(f"Section 4 analysis completed for {ticker}")
            return formatted_report
            
        except Exception as e:
            logger.error(f"Error generating Section 4 report for {ticker}: {e}")
            raise
    
    async def generate_competitive_charts(self, ticker: str) -> Dict[str, Any]:
        """Generate chart data for competitive analysis visualization"""
        try:
            # Get analysis data
            analysis = await self.generate_section4_report(ticker)
            
            # Extract chart data
            charts_data = analysis.get("charts_data", {})
            
            # Format charts for frontend
            formatted_charts = {
                "market_share_pie": self._format_market_share_chart(charts_data.get("market_share_chart", {})),
                "peer_comparison_bar": self._format_peer_comparison_chart(charts_data.get("peer_comparison_chart", {})),
                "competitive_positioning_scatter": self._format_positioning_chart(charts_data.get("competitive_positioning", {})),
                "industry_trends_line": self._format_trends_chart(analysis.get("industry_dynamics", {}))
            }
            
            return formatted_charts
            
        except Exception as e:
            logger.error(f"Error generating competitive charts for {ticker}: {e}")
            return {}
    
    async def get_competitor_comparison(self, ticker: str, competitor_ticker: str) -> Dict[str, Any]:
        """Get detailed comparison between company and specific competitor"""
        try:
            analysis = await self.generate_section4_report(ticker)
            
            # Find the specific competitor
            competitors = analysis.get("competitive_landscape", {}).get("key_competitors", [])
            competitor_data = None
            
            for comp in competitors:
                if comp.get("ticker") == competitor_ticker:
                    competitor_data = comp
                    break
            
            if not competitor_data:
                return {"error": f"Competitor {competitor_ticker} not found in analysis"}
            
            # Get company data
            company_profile = analysis.get("company_profile", {})
            
            # Create detailed comparison
            comparison = {
                "company": {
                    "ticker": ticker,
                    "name": company_profile.get("name", ""),
                    "market_cap": company_profile.get("market_cap", 0),
                    "revenue_ttm": company_profile.get("revenue_ttm", 0)
                },
                "competitor": competitor_data,
                "comparison_metrics": self._calculate_comparison_metrics(company_profile, competitor_data),
                "competitive_advantages": analysis.get("market_position", {}).get("competitive_advantages", []),
                "generated_at": datetime.now().isoformat()
            }
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error generating competitor comparison for {ticker} vs {competitor_ticker}: {e}")
            return {"error": str(e)}
    
    async def get_market_position_summary(self, ticker: str) -> Dict[str, Any]:
        """Get concise market position summary for dashboard"""
        try:
            analysis = await self.generate_section4_report(ticker)
            
            market_position = analysis.get("market_position", {})
            competitive_landscape = analysis.get("competitive_landscape", {})
            industry_dynamics = analysis.get("industry_dynamics", {})
            
            summary = {
                "ticker": ticker,
                "market_share": market_position.get("market_share", 0),
                "market_position": market_position.get("position", "Unknown"),
                "competitive_intensity": competitive_landscape.get("competitive_intensity", "Medium"),
                "key_competitors_count": len(competitive_landscape.get("key_competitors", [])),
                "competitive_advantages_count": len(market_position.get("competitive_advantages", [])),
                "market_sentiment": industry_dynamics.get("market_sentiment", "neutral"),
                "industry_trends_count": len(industry_dynamics.get("industry_trends", [])),
                "last_updated": analysis.get("generated_at", "")
            }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating market position summary for {ticker}: {e}")
            return {}
    
    def _format_for_report(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format analysis data for report integration"""
        
        return {
            "section": "Market Position & Competitive Analysis",
            "section_number": 4,
            "pages": 5,
            "ticker": analysis.get("ticker", ""),
            "generated_at": analysis.get("generated_at", ""),
            
            # Executive Summary
            "executive_summary": {
                "market_position": analysis.get("market_position", {}).get("position", ""),
                "market_share": analysis.get("market_position", {}).get("market_share", 0),
                "competitive_intensity": analysis.get("competitive_landscape", {}).get("competitive_intensity", ""),
                "key_insights": self._extract_key_insights(analysis)
            },
            
            # Detailed Analysis
            "detailed_analysis": {
                "company_profile": analysis.get("company_profile", {}),
                "market_position": analysis.get("market_position", {}),
                "competitive_landscape": analysis.get("competitive_landscape", {}),
                "industry_dynamics": analysis.get("industry_dynamics", {}),
                "market_research": analysis.get("market_research", {})
            },
            
            # AI Analysis
            "ai_analysis": analysis.get("ai_analysis", {}),
            
            # Charts and Visualizations
            "charts_data": analysis.get("charts_data", {}),
            
            # Investment Implications
            "investment_implications": self._extract_investment_implications(analysis)
        }
    
    def _extract_key_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Extract key insights from analysis"""
        insights = []
        
        # Market position insight
        market_position = analysis.get("market_position", {})
        position = market_position.get("position", "")
        market_share = market_position.get("market_share", 0)
        
        if position and market_share > 0:
            insights.append(f"Company holds {position.lower()} position with {market_share:.1f}% estimated market share")
        
        # Competitive advantages
        advantages = market_position.get("competitive_advantages", [])
        if advantages:
            insights.append(f"Key competitive advantages: {', '.join(advantages[:2])}")
        
        # Industry trends
        trends = analysis.get("industry_dynamics", {}).get("industry_trends", [])
        if trends:
            insights.append(f"Industry experiencing: {trends[0]}")
        
        # Competitive intensity
        intensity = analysis.get("competitive_landscape", {}).get("competitive_intensity", "")
        if intensity:
            insights.append(f"{intensity} competitive intensity in the market")
        
        return insights[:4]  # Limit to top 4 insights
    
    def _extract_investment_implications(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Extract investment implications from analysis"""
        
        market_position = analysis.get("market_position", {})
        competitive_landscape = analysis.get("competitive_landscape", {})
        industry_dynamics = analysis.get("industry_dynamics", {})
        
        # Determine overall competitive strength
        position = market_position.get("position", "")
        advantages_count = len(market_position.get("competitive_advantages", []))
        
        if position == "Leader" and advantages_count >= 2:
            competitive_strength = "Strong"
        elif position in ["Leader", "Challenger"] and advantages_count >= 1:
            competitive_strength = "Average"
        else:
            competitive_strength = "Weak"
        
        # Assess market attractiveness
        sentiment = industry_dynamics.get("market_sentiment", "neutral")
        trends_count = len(industry_dynamics.get("industry_trends", []))
        
        if sentiment == "positive" and trends_count >= 2:
            market_attractiveness = "High"
        elif sentiment != "negative" and trends_count >= 1:
            market_attractiveness = "Medium"
        else:
            market_attractiveness = "Low"
        
        return {
            "competitive_strength": competitive_strength,
            "market_attractiveness": market_attractiveness,
            "investment_rating": self._calculate_investment_rating(competitive_strength, market_attractiveness),
            "key_risks": self._identify_key_risks(analysis),
            "key_opportunities": self._identify_key_opportunities(analysis)
        }
    
    def _calculate_investment_rating(self, competitive_strength: str, market_attractiveness: str) -> str:
        """Calculate overall investment rating based on competitive position"""
        
        strength_score = {"Strong": 3, "Average": 2, "Weak": 1}.get(competitive_strength, 1)
        attractiveness_score = {"High": 3, "Medium": 2, "Low": 1}.get(market_attractiveness, 1)
        
        total_score = strength_score + attractiveness_score
        
        if total_score >= 5:
            return "Attractive"
        elif total_score >= 4:
            return "Neutral"
        else:
            return "Unattractive"
    
    def _identify_key_risks(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify key competitive risks"""
        risks = []
        
        # High competitive intensity
        intensity = analysis.get("competitive_landscape", {}).get("competitive_intensity", "")
        if intensity == "High":
            risks.append("High competitive intensity may pressure margins")
        
        # Negative market sentiment
        sentiment = analysis.get("industry_dynamics", {}).get("market_sentiment", "")
        if sentiment == "negative":
            risks.append("Negative market sentiment affecting industry outlook")
        
        # Low barriers to entry
        barriers = analysis.get("industry_dynamics", {}).get("barriers_to_entry", "")
        if barriers == "Low":
            risks.append("Low barriers to entry increase new entrant risk")
        
        # Market position weakness
        position = analysis.get("market_position", {}).get("position", "")
        if position in ["Follower", "Niche"]:
            risks.append("Weaker market position limits pricing power")
        
        return risks[:3]  # Top 3 risks
    
    def _identify_key_opportunities(self, analysis: Dict[str, Any]) -> List[str]:
        """Identify key market opportunities"""
        opportunities = []
        
        # Strong market position
        position = analysis.get("market_position", {}).get("position", "")
        if position == "Leader":
            opportunities.append("Market leadership enables expansion opportunities")
        
        # Positive market sentiment
        sentiment = analysis.get("industry_dynamics", {}).get("market_sentiment", "")
        if sentiment == "positive":
            opportunities.append("Positive market sentiment supports growth")
        
        # Competitive advantages
        advantages = analysis.get("market_position", {}).get("competitive_advantages", [])
        if len(advantages) >= 2:
            opportunities.append("Multiple competitive advantages provide defensive moat")
        
        # Industry trends
        trends = analysis.get("industry_dynamics", {}).get("industry_trends", [])
        if any("growth" in trend.lower() for trend in trends):
            opportunities.append("Industry growth trends support expansion")
        
        return opportunities[:3]  # Top 3 opportunities
    
    def _format_market_share_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format market share data for pie chart"""
        companies = chart_data.get("companies", [])
        shares = chart_data.get("market_shares", [])
        
        if not companies or not shares:
            return {}
        
        return {
            "type": "pie",
            "title": "Market Share Distribution",
            "data": {
                "labels": companies,
                "datasets": [{
                    "data": shares,
                    "backgroundColor": [
                        "#3B82F6",  # Primary for target company
                        "#6B7280", "#9CA3AF", "#D1D5DB", "#E5E7EB"  # Grays for competitors
                    ]
                }]
            },
            "options": {
                "responsive": True,
                "plugins": {
                    "legend": {"position": "bottom"},
                    "tooltip": {
                        "callbacks": {
                            "label": "function(context) { return context.label + ': ' + context.parsed + '%'; }"
                        }
                    }
                }
            }
        }
    
    def _format_peer_comparison_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format peer comparison data for bar chart"""
        if not chart_data:
            return {}
        
        companies = chart_data.get("companies", [])
        metrics = chart_data.get("metrics", {})
        
        return {
            "type": "bar",
            "title": "Peer Comparison - Key Metrics",
            "data": {
                "labels": companies,
                "datasets": [
                    {
                        "label": "P/E Ratio",
                        "data": metrics.get("pe_ratio", []),
                        "backgroundColor": "#3B82F6"
                    },
                    {
                        "label": "Profit Margin (%)",
                        "data": [m * 100 for m in metrics.get("profit_margin", [])],
                        "backgroundColor": "#10B981"
                    },
                    {
                        "label": "ROE (%)",
                        "data": [m * 100 for m in metrics.get("roe", [])],
                        "backgroundColor": "#F59E0B"
                    }
                ]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "y": {"beginAtZero": True}
                }
            }
        }
    
    def _format_positioning_chart(self, chart_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format competitive positioning data for scatter plot"""
        companies = chart_data.get("companies", [])
        
        if not companies:
            return {}
        
        return {
            "type": "scatter",
            "title": "Competitive Positioning Matrix",
            "data": {
                "datasets": [{
                    "label": "Companies",
                    "data": [{"x": comp["x"], "y": comp["y"], "label": comp["name"]} for comp in companies],
                    "backgroundColor": [comp["color"] for comp in companies],
                    "pointRadius": [comp["size"] for comp in companies]
                }]
            },
            "options": {
                "responsive": True,
                "scales": {
                    "x": {"title": {"display": True, "text": chart_data.get("x_axis", "Market Share")}},
                    "y": {"title": {"display": True, "text": chart_data.get("y_axis", "Revenue Growth")}}
                }
            }
        }
    
    def _format_trends_chart(self, industry_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format industry trends for line chart (placeholder)"""
        return {
            "type": "line",
            "title": "Industry Trends",
            "data": {
                "labels": ["Q1", "Q2", "Q3", "Q4"],
                "datasets": [{
                    "label": "Market Sentiment",
                    "data": [70, 75, 80, 85],  # Placeholder data
                    "borderColor": "#3B82F6",
                    "fill": False
                }]
            }
        }
    
    def _calculate_comparison_metrics(self, company_data: Dict, competitor_data: Dict) -> Dict[str, Any]:
        """Calculate comparison metrics between company and competitor"""
        
        company_market_cap = company_data.get("market_cap", 0)
        competitor_market_cap = competitor_data.get("market_cap", 0)
        
        company_revenue = company_data.get("revenue_ttm", 0)
        competitor_revenue = competitor_data.get("revenue_ttm", 0)
        
        return {
            "market_cap_ratio": (company_market_cap / competitor_market_cap) if competitor_market_cap > 0 else 0,
            "revenue_ratio": (company_revenue / competitor_revenue) if competitor_revenue > 0 else 0,
            "size_advantage": "Company" if company_market_cap > competitor_market_cap else "Competitor",
            "revenue_advantage": "Company" if company_revenue > competitor_revenue else "Competitor"
        }
    
    def _is_cached(self, ticker: str) -> bool:
        """Check if data is cached and still valid"""
        if ticker not in self.cache:
            return False
        
        cache_time = self.cache[ticker]["timestamp"]
        current_time = datetime.now().timestamp()
        
        return (current_time - cache_time) < self.cache_ttl
    
    def _cache_data(self, ticker: str, data: Dict[str, Any]):
        """Cache analysis data"""
        self.cache[ticker] = {
            "data": data,
            "timestamp": datetime.now().timestamp()
        }

# Singleton instance
section4_service = Section4IntegrationService()

# Convenience functions for FastAPI endpoints
async def generate_competitive_analysis(ticker: str) -> Dict[str, Any]:
    """Generate competitive analysis report"""
    return await section4_service.generate_section4_report(ticker)

async def get_competitive_charts(ticker: str) -> Dict[str, Any]:
    """Get competitive analysis charts"""
    return await section4_service.generate_competitive_charts(ticker)

async def get_market_position_summary(ticker: str) -> Dict[str, Any]:
    """Get market position summary"""
    return await section4_service.get_market_position_summary(ticker)