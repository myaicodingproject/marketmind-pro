#!/usr/bin/env python3
"""
Section 4 Agent - Market Position & Competitive Analysis (5 pages)
Research company's market position, competitive landscape, market share analysis, and industry dynamics
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
import yfinance as yf
import requests
from dataclasses import dataclass
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class CompetitiveAnalysisData:
    ticker: str
    market_position: str
    market_share: float
    competitive_advantages: List[str]
    key_competitors: List[Dict[str, Any]]
    industry_dynamics: Dict[str, Any]
    competitive_threats: List[str]
    market_opportunities: List[str]

class Section4MarketCompetitiveAgent:
    """Section 4 agent for market position and competitive analysis"""
    
    def __init__(self):
        self.data_repository = {}
        self.kiro_cli_path = "kiro-cli"
        self.prompts_dir = Path(".kiro/prompts")
        
    async def generate_competitive_analysis(self, ticker: str) -> Dict[str, Any]:
        """Generate comprehensive competitive analysis for given ticker"""
        try:
            # Step 1: Gather company and industry data
            company_data = await self._get_company_data(ticker)
            
            # Step 2: Identify and analyze competitors
            competitors_data = await self._analyze_competitors(ticker, company_data)
            
            # Step 3: Perform market research and web search
            market_research = await self._conduct_market_research(ticker, company_data)
            
            # Step 4: Generate competitive positioning analysis using Kiro
            positioning_analysis = await self._generate_positioning_analysis(ticker, company_data, competitors_data, market_research)
            
            # Step 5: Create market share and industry dynamics analysis
            market_dynamics = await self._analyze_market_dynamics(ticker, company_data, competitors_data)
            
            # Step 6: Generate competitive matrices and charts
            competitive_matrices = await self._generate_competitive_matrices(ticker, company_data, competitors_data)
            
            # Step 7: Compile final analysis
            analysis = await self._compile_competitive_analysis(
                ticker, company_data, competitors_data, market_research, 
                positioning_analysis, market_dynamics, competitive_matrices
            )
            
            # Step 8: Store in central repository
            self._store_data(ticker, analysis)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating competitive analysis for {ticker}: {e}")
            raise
    
    async def _get_company_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive company data for competitive analysis"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "ticker": ticker,
                "company_name": info.get("longName", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
                "market_cap": info.get("marketCap", 0),
                "revenue_ttm": info.get("totalRevenue", 0),
                "employees": info.get("fullTimeEmployees", 0),
                "business_summary": info.get("longBusinessSummary", ""),
                "website": info.get("website", ""),
                "country": info.get("country", ""),
                "exchange": info.get("exchange", ""),
                "current_price": info.get("currentPrice", 0),
                "pe_ratio": info.get("trailingPE", 0),
                "profit_margin": info.get("profitMargins", 0),
                "roe": info.get("returnOnEquity", 0),
                "revenue_growth": info.get("revenueGrowth", 0),
                "earnings_growth": info.get("earningsGrowth", 0)
            }
        except Exception as e:
            logger.error(f"Error fetching company data for {ticker}: {e}")
            return {}
    
    async def _analyze_competitors(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Identify and analyze key competitors"""
        try:
            # Get industry peers based on sector/industry
            sector = company_data.get("sector", "")
            industry = company_data.get("industry", "")
            
            # Define competitor mapping for major companies
            competitor_mapping = {
                "AAPL": ["MSFT", "GOOGL", "AMZN", "META", "TSLA"],
                "MSFT": ["AAPL", "GOOGL", "AMZN", "ORCL", "CRM"],
                "GOOGL": ["AAPL", "MSFT", "AMZN", "META", "NFLX"],
                "AMZN": ["AAPL", "MSFT", "GOOGL", "WMT", "NFLX"],
                "TSLA": ["F", "GM", "NIO", "RIVN", "LCID"],
                "NVDA": ["AMD", "INTC", "QCOM", "AVGO", "MU"]
            }
            
            # Get predefined competitors or find similar companies
            competitor_tickers = competitor_mapping.get(ticker, [])
            
            if not competitor_tickers:
                # Fallback: use sector-based approach
                competitor_tickers = await self._find_sector_competitors(sector, industry)
            
            competitors = []
            for comp_ticker in competitor_tickers[:5]:  # Limit to top 5
                try:
                    comp_stock = yf.Ticker(comp_ticker)
                    comp_info = comp_stock.info
                    
                    competitor = {
                        "ticker": comp_ticker,
                        "name": comp_info.get("longName", ""),
                        "market_cap": comp_info.get("marketCap", 0),
                        "revenue_ttm": comp_info.get("totalRevenue", 0),
                        "pe_ratio": comp_info.get("trailingPE", 0),
                        "profit_margin": comp_info.get("profitMargins", 0),
                        "roe": comp_info.get("returnOnEquity", 0),
                        "revenue_growth": comp_info.get("revenueGrowth", 0),
                        "current_price": comp_info.get("currentPrice", 0),
                        "sector": comp_info.get("sector", ""),
                        "industry": comp_info.get("industry", "")
                    }
                    competitors.append(competitor)
                except Exception as e:
                    logger.warning(f"Could not fetch data for competitor {comp_ticker}: {e}")
                    continue
            
            return {
                "competitors": competitors,
                "total_competitors_analyzed": len(competitors),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing competitors for {ticker}: {e}")
            return {"competitors": [], "total_competitors_analyzed": 0}
    
    async def _find_sector_competitors(self, sector: str, industry: str) -> List[str]:
        """Find competitors based on sector and industry"""
        # This is a simplified approach - in production, you'd use a financial data API
        sector_mapping = {
            "Technology": ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "ORCL", "CRM"],
            "Healthcare": ["JNJ", "PFE", "UNH", "ABBV", "TMO", "DHR", "BMY", "MRK"],
            "Financial Services": ["JPM", "BAC", "WFC", "GS", "MS", "C", "USB", "PNC"],
            "Consumer Cyclical": ["AMZN", "TSLA", "HD", "MCD", "NKE", "SBUX", "TGT", "LOW"],
            "Energy": ["XOM", "CVX", "COP", "EOG", "SLB", "PSX", "VLO", "MPC"]
        }
        
        return sector_mapping.get(sector, [])
    
    async def _conduct_market_research(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct web research for market trends and industry analysis"""
        try:
            # Get recent news and market sentiment
            stock = yf.Ticker(ticker)
            news = stock.news
            
            # Process news for market insights
            market_news = []
            for article in news[:10]:  # Get last 10 articles
                market_news.append({
                    "title": article.get("title", ""),
                    "summary": article.get("summary", ""),
                    "published": article.get("providerPublishTime", 0),
                    "source": article.get("publisher", ""),
                    "url": article.get("link", "")
                })
            
            # Analyze industry trends from news
            industry_trends = self._analyze_industry_trends(market_news, company_data.get("industry", ""))
            
            # Get market sentiment
            market_sentiment = self._analyze_market_sentiment(market_news)
            
            return {
                "market_news": market_news,
                "industry_trends": industry_trends,
                "market_sentiment": market_sentiment,
                "research_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error conducting market research for {ticker}: {e}")
            return {"market_news": [], "industry_trends": [], "market_sentiment": "neutral"}
    
    def _analyze_industry_trends(self, news_articles: List[Dict], industry: str) -> List[str]:
        """Analyze industry trends from news articles"""
        trend_keywords = {
            "growth": ["expansion", "growth", "increase", "rising", "surge", "boom"],
            "decline": ["decline", "decrease", "falling", "drop", "slump", "downturn"],
            "innovation": ["innovation", "technology", "AI", "digital", "automation", "breakthrough"],
            "regulation": ["regulation", "policy", "government", "compliance", "law", "regulatory"],
            "competition": ["competition", "competitive", "market share", "rivalry", "competitor"]
        }
        
        trends = []
        for category, keywords in trend_keywords.items():
            count = 0
            for article in news_articles:
                text = (article.get("title", "") + " " + article.get("summary", "")).lower()
                count += sum(1 for keyword in keywords if keyword in text)
            
            if count >= 2:  # Threshold for trend identification
                trends.append(f"{category.title()} trend detected in {industry} industry")
        
        return trends
    
    def _analyze_market_sentiment(self, news_articles: List[Dict]) -> str:
        """Analyze overall market sentiment"""
        positive_words = ["growth", "profit", "beat", "strong", "positive", "upgrade", "buy", "bullish"]
        negative_words = ["loss", "decline", "weak", "negative", "downgrade", "sell", "bearish", "risk"]
        
        positive_count = 0
        negative_count = 0
        
        for article in news_articles:
            text = (article.get("title", "") + " " + article.get("summary", "")).lower()
            positive_count += sum(1 for word in positive_words if word in text)
            negative_count += sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count * 1.3:
            return "positive"
        elif negative_count > positive_count * 1.3:
            return "negative"
        else:
            return "neutral"
    
    async def _generate_positioning_analysis(self, ticker: str, company_data: Dict, competitors_data: Dict, market_research: Dict) -> Dict[str, Any]:
        """Generate competitive positioning analysis using Kiro CLI"""
        try:
            # Prepare data for Kiro prompt
            analysis_data = {
                "ticker": ticker,
                "company_name": company_data.get("company_name", ""),
                "sector": company_data.get("sector", ""),
                "industry": company_data.get("industry", ""),
                "market_cap": company_data.get("market_cap", 0),
                "revenue_ttm": company_data.get("revenue_ttm", 0),
                "competitors": competitors_data.get("competitors", []),
                "industry_trends": market_research.get("industry_trends", []),
                "market_sentiment": market_research.get("market_sentiment", "neutral")
            }
            
            # Execute Kiro prompt for competitive positioning
            positioning_result = await self._execute_kiro_prompt("competitive-positioning-analysis", analysis_data)
            
            return {
                "positioning_analysis": positioning_result,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating positioning analysis for {ticker}: {e}")
            return {"positioning_analysis": "Analysis unavailable", "generated_at": datetime.now().isoformat()}
    
    async def _analyze_market_dynamics(self, ticker: str, company_data: Dict, competitors_data: Dict) -> Dict[str, Any]:
        """Analyze market dynamics and calculate market share estimates"""
        try:
            competitors = competitors_data.get("competitors", [])
            company_revenue = company_data.get("revenue_ttm", 0)
            
            # Calculate total market size (simplified approach)
            total_market_revenue = company_revenue
            for competitor in competitors:
                total_market_revenue += competitor.get("revenue_ttm", 0)
            
            # Calculate market share
            market_share = (company_revenue / total_market_revenue * 100) if total_market_revenue > 0 else 0
            
            # Analyze competitive position
            company_market_cap = company_data.get("market_cap", 0)
            market_position = "Leader"
            
            for competitor in competitors:
                if competitor.get("market_cap", 0) > company_market_cap:
                    market_position = "Challenger"
                    break
            
            # Industry growth analysis
            avg_growth = sum(comp.get("revenue_growth", 0) for comp in competitors) / len(competitors) if competitors else 0
            company_growth = company_data.get("revenue_growth", 0)
            
            growth_position = "Above Average" if company_growth > avg_growth else "Below Average"
            
            return {
                "market_share_estimate": round(market_share, 2),
                "market_position": market_position,
                "total_addressable_market": total_market_revenue,
                "growth_position": growth_position,
                "competitive_intensity": "High" if len(competitors) > 3 else "Medium",
                "market_dynamics": {
                    "market_concentration": "Fragmented" if market_share < 20 else "Concentrated",
                    "barriers_to_entry": "High" if company_data.get("market_cap", 0) > 100000000000 else "Medium",
                    "switching_costs": "Medium"  # Simplified assessment
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market dynamics for {ticker}: {e}")
            return {}
    
    async def _generate_competitive_matrices(self, ticker: str, company_data: Dict, competitors_data: Dict) -> Dict[str, Any]:
        """Generate competitive positioning matrices and comparison charts"""
        try:
            competitors = competitors_data.get("competitors", [])
            
            # Create peer comparison matrix
            peer_comparison = {
                "companies": [company_data["ticker"]] + [comp["ticker"] for comp in competitors],
                "metrics": {
                    "market_cap": [company_data.get("market_cap", 0)] + [comp.get("market_cap", 0) for comp in competitors],
                    "revenue_ttm": [company_data.get("revenue_ttm", 0)] + [comp.get("revenue_ttm", 0) for comp in competitors],
                    "pe_ratio": [company_data.get("pe_ratio", 0)] + [comp.get("pe_ratio", 0) for comp in competitors],
                    "profit_margin": [company_data.get("profit_margin", 0)] + [comp.get("profit_margin", 0) for comp in competitors],
                    "roe": [company_data.get("roe", 0)] + [comp.get("roe", 0) for comp in competitors]
                }
            }
            
            # Generate competitive advantage matrix
            competitive_advantages = await self._identify_competitive_advantages(company_data, competitors)
            
            # Create market share visualization data
            market_share_data = {
                "companies": [company_data["ticker"]] + [comp["ticker"] for comp in competitors[:4]],
                "market_shares": self._calculate_market_shares(company_data, competitors)
            }
            
            return {
                "peer_comparison_matrix": peer_comparison,
                "competitive_advantages": competitive_advantages,
                "market_share_visualization": market_share_data,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating competitive matrices for {ticker}: {e}")
            return {}
    
    async def _identify_competitive_advantages(self, company_data: Dict, competitors: List[Dict]) -> List[str]:
        """Identify competitive advantages based on financial metrics"""
        advantages = []
        
        # Compare key metrics
        company_roe = company_data.get("roe", 0)
        company_margin = company_data.get("profit_margin", 0)
        company_growth = company_data.get("revenue_growth", 0)
        
        # Calculate competitor averages
        avg_roe = sum(comp.get("roe", 0) for comp in competitors) / len(competitors) if competitors else 0
        avg_margin = sum(comp.get("profit_margin", 0) for comp in competitors) / len(competitors) if competitors else 0
        avg_growth = sum(comp.get("revenue_growth", 0) for comp in competitors) / len(competitors) if competitors else 0
        
        if company_roe > avg_roe * 1.2:
            advantages.append("Superior return on equity vs peers")
        
        if company_margin > avg_margin * 1.2:
            advantages.append("Higher profit margins than competitors")
        
        if company_growth > avg_growth * 1.2:
            advantages.append("Faster revenue growth than industry average")
        
        if company_data.get("market_cap", 0) > max([comp.get("market_cap", 0) for comp in competitors], default=0):
            advantages.append("Market leadership position")
        
        return advantages
    
    def _calculate_market_shares(self, company_data: Dict, competitors: List[Dict]) -> List[float]:
        """Calculate estimated market shares based on revenue"""
        revenues = [company_data.get("revenue_ttm", 0)]
        revenues.extend([comp.get("revenue_ttm", 0) for comp in competitors[:4]])
        
        total_revenue = sum(revenues)
        if total_revenue == 0:
            return [0] * len(revenues)
        
        return [round((revenue / total_revenue) * 100, 1) for revenue in revenues]
    
    async def _execute_kiro_prompt(self, prompt_name: str, data: Dict[str, Any]) -> str:
        """Execute Kiro CLI prompt for competitive analysis"""
        try:
            prompt_path = self.prompts_dir / f"{prompt_name}.md"
            
            if not prompt_path.exists():
                logger.warning(f"Prompt file not found: {prompt_path}")
                return "Kiro analysis unavailable"
            
            # Read prompt template
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
            
            # Format prompt with data
            formatted_prompt = prompt_template.format(**data)
            
            # Execute Kiro CLI
            cmd = [self.kiro_cli_path, "chat", "--no-interactive", "--trust-all-tools"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=formatted_prompt.encode())
            
            if process.returncode != 0:
                logger.error(f"Kiro CLI failed: {stderr.decode()}")
                return "Kiro analysis failed"
            
            return stdout.decode().strip()
            
        except Exception as e:
            logger.error(f"Error executing Kiro prompt {prompt_name}: {e}")
            return "Kiro analysis error"
    
    async def _compile_competitive_analysis(self, ticker: str, company_data: Dict, competitors_data: Dict, 
                                          market_research: Dict, positioning_analysis: Dict, 
                                          market_dynamics: Dict, competitive_matrices: Dict) -> Dict[str, Any]:
        """Compile final competitive analysis report"""
        
        return {
            "ticker": ticker,
            "generated_at": datetime.now().isoformat(),
            "section": "Market Position & Competitive Analysis",
            "pages": 5,
            
            # Company Overview
            "company_profile": {
                "name": company_data.get("company_name", ""),
                "sector": company_data.get("sector", ""),
                "industry": company_data.get("industry", ""),
                "market_cap": company_data.get("market_cap", 0),
                "revenue_ttm": company_data.get("revenue_ttm", 0)
            },
            
            # Market Position
            "market_position": {
                "market_share": market_dynamics.get("market_share_estimate", 0),
                "position": market_dynamics.get("market_position", "Unknown"),
                "competitive_advantages": competitive_matrices.get("competitive_advantages", []),
                "growth_position": market_dynamics.get("growth_position", "Unknown")
            },
            
            # Competitive Landscape
            "competitive_landscape": {
                "key_competitors": competitors_data.get("competitors", []),
                "competitive_intensity": market_dynamics.get("competitive_intensity", "Medium"),
                "peer_comparison": competitive_matrices.get("peer_comparison_matrix", {}),
                "market_concentration": market_dynamics.get("market_dynamics", {}).get("market_concentration", "Unknown")
            },
            
            # Industry Dynamics
            "industry_dynamics": {
                "industry_trends": market_research.get("industry_trends", []),
                "market_sentiment": market_research.get("market_sentiment", "neutral"),
                "barriers_to_entry": market_dynamics.get("market_dynamics", {}).get("barriers_to_entry", "Medium"),
                "switching_costs": market_dynamics.get("market_dynamics", {}).get("switching_costs", "Medium")
            },
            
            # Market Research Insights
            "market_research": {
                "recent_news_count": len(market_research.get("market_news", [])),
                "key_insights": market_research.get("industry_trends", [])[:3],  # Top 3 insights
                "research_date": market_research.get("research_date", "")
            },
            
            # Kiro Analysis
            "ai_analysis": {
                "positioning_analysis": positioning_analysis.get("positioning_analysis", ""),
                "generated_at": positioning_analysis.get("generated_at", "")
            },
            
            # Visualization Data
            "charts_data": {
                "market_share_chart": competitive_matrices.get("market_share_visualization", {}),
                "peer_comparison_chart": competitive_matrices.get("peer_comparison_matrix", {}),
                "competitive_positioning": {
                    "x_axis": "Market Share",
                    "y_axis": "Revenue Growth",
                    "companies": self._create_positioning_chart_data(company_data, competitors_data.get("competitors", []))
                }
            }
        }
    
    def _create_positioning_chart_data(self, company_data: Dict, competitors: List[Dict]) -> List[Dict]:
        """Create data for competitive positioning scatter plot"""
        chart_data = []
        
        # Add company data
        chart_data.append({
            "name": company_data.get("ticker", ""),
            "x": 20,  # Placeholder market share
            "y": company_data.get("revenue_growth", 0) * 100,
            "size": company_data.get("market_cap", 0) / 1000000000,  # Billions
            "color": "#3B82F6"  # Primary color for target company
        })
        
        # Add competitor data
        for i, competitor in enumerate(competitors[:4]):
            chart_data.append({
                "name": competitor.get("ticker", ""),
                "x": 15 - i * 3,  # Placeholder market shares
                "y": competitor.get("revenue_growth", 0) * 100,
                "size": competitor.get("market_cap", 0) / 1000000000,
                "color": "#6B7280"  # Gray for competitors
            })
        
        return chart_data
    
    def _store_data(self, ticker: str, analysis_data: Dict[str, Any]):
        """Store data in central repository for consistency across sections"""
        self.data_repository[ticker] = {
            "competitive_analysis": analysis_data,
            "last_updated": datetime.now().isoformat()
        }
        logger.info(f"Stored competitive analysis data for {ticker}")
    
    def get_stored_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Retrieve stored data for consistency across sections"""
        return self.data_repository.get(ticker)

# Usage example
async def main():
    agent = Section4MarketCompetitiveAgent()
    analysis = await agent.generate_competitive_analysis("AAPL")
    print(json.dumps(analysis, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())