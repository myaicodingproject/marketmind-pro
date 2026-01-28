"""
Section 4 API Endpoints - Market Position & Competitive Analysis
FastAPI endpoints for competitive analysis functionality
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging

from ..services.section4_integration_service import (
    section4_service,
    generate_competitive_analysis,
    get_competitive_charts,
    get_market_position_summary
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/section4", tags=["Section 4 - Competitive Analysis"])

@router.get("/competitive-analysis/{ticker}")
async def get_competitive_analysis(
    ticker: str,
    use_cache: bool = True,
    background_tasks: BackgroundTasks = None
) -> Dict[str, Any]:
    """
    Generate comprehensive competitive analysis for a given ticker
    
    - **ticker**: Stock ticker symbol (e.g., AAPL, MSFT)
    - **use_cache**: Whether to use cached data if available
    
    Returns 5-page competitive analysis including:
    - Market position assessment
    - Competitive landscape analysis
    - Industry dynamics
    - Market research insights
    - Investment implications
    """
    try:
        ticker = ticker.upper()
        logger.info(f"Generating competitive analysis for {ticker}")
        
        # Generate analysis
        analysis = await section4_service.generate_section4_report(ticker, use_cache)
        
        return {
            "success": True,
            "ticker": ticker,
            "data": analysis,
            "message": f"Competitive analysis generated successfully for {ticker}"
        }
        
    except Exception as e:
        logger.error(f"Error generating competitive analysis for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate competitive analysis: {str(e)}"
        )

@router.get("/charts/{ticker}")
async def get_competitive_analysis_charts(ticker: str) -> Dict[str, Any]:
    """
    Get chart data for competitive analysis visualization
    
    - **ticker**: Stock ticker symbol
    
    Returns chart configurations for:
    - Market share pie chart
    - Peer comparison bar chart
    - Competitive positioning scatter plot
    - Industry trends line chart
    """
    try:
        ticker = ticker.upper()
        logger.info(f"Generating competitive charts for {ticker}")
        
        charts = await get_competitive_charts(ticker)
        
        return {
            "success": True,
            "ticker": ticker,
            "charts": charts,
            "message": f"Competitive charts generated for {ticker}"
        }
        
    except Exception as e:
        logger.error(f"Error generating competitive charts for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate competitive charts: {str(e)}"
        )

@router.get("/market-position/{ticker}")
async def get_market_position(ticker: str) -> Dict[str, Any]:
    """
    Get concise market position summary for dashboard display
    
    - **ticker**: Stock ticker symbol
    
    Returns key metrics:
    - Market share estimate
    - Market position (Leader/Challenger/Follower)
    - Competitive intensity
    - Number of key competitors
    - Market sentiment
    """
    try:
        ticker = ticker.upper()
        logger.info(f"Getting market position summary for {ticker}")
        
        summary = await get_market_position_summary(ticker)
        
        return {
            "success": True,
            "ticker": ticker,
            "market_position": summary,
            "message": f"Market position summary retrieved for {ticker}"
        }
        
    except Exception as e:
        logger.error(f"Error getting market position for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get market position: {str(e)}"
        )

@router.get("/competitor-comparison/{ticker}/{competitor}")
async def get_competitor_comparison(ticker: str, competitor: str) -> Dict[str, Any]:
    """
    Get detailed comparison between company and specific competitor
    
    - **ticker**: Primary company ticker
    - **competitor**: Competitor ticker to compare against
    
    Returns detailed head-to-head comparison including:
    - Financial metrics comparison
    - Market position analysis
    - Competitive advantages assessment
    """
    try:
        ticker = ticker.upper()
        competitor = competitor.upper()
        
        logger.info(f"Generating comparison between {ticker} and {competitor}")
        
        comparison = await section4_service.get_competitor_comparison(ticker, competitor)
        
        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])
        
        return {
            "success": True,
            "primary_ticker": ticker,
            "competitor_ticker": competitor,
            "comparison": comparison,
            "message": f"Competitor comparison generated for {ticker} vs {competitor}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating competitor comparison for {ticker} vs {competitor}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate competitor comparison: {str(e)}"
        )

@router.get("/competitors/{ticker}")
async def get_key_competitors(ticker: str) -> Dict[str, Any]:
    """
    Get list of key competitors for a given ticker
    
    - **ticker**: Stock ticker symbol
    
    Returns list of key competitors with basic metrics
    """
    try:
        ticker = ticker.upper()
        logger.info(f"Getting key competitors for {ticker}")
        
        # Get full analysis to extract competitors
        analysis = await section4_service.generate_section4_report(ticker)
        competitors = analysis.get("detailed_analysis", {}).get("competitive_landscape", {}).get("key_competitors", [])
        
        # Format competitor data
        formatted_competitors = []
        for comp in competitors:
            formatted_competitors.append({
                "ticker": comp.get("ticker", ""),
                "name": comp.get("name", ""),
                "market_cap": comp.get("market_cap", 0),
                "revenue_ttm": comp.get("revenue_ttm", 0),
                "sector": comp.get("sector", ""),
                "industry": comp.get("industry", "")
            })
        
        return {
            "success": True,
            "ticker": ticker,
            "competitors": formatted_competitors,
            "total_competitors": len(formatted_competitors),
            "message": f"Key competitors retrieved for {ticker}"
        }
        
    except Exception as e:
        logger.error(f"Error getting competitors for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get competitors: {str(e)}"
        )

@router.get("/industry-analysis/{ticker}")
async def get_industry_analysis(ticker: str) -> Dict[str, Any]:
    """
    Get industry dynamics and trends analysis
    
    - **ticker**: Stock ticker symbol
    
    Returns industry analysis including:
    - Industry trends
    - Market sentiment
    - Barriers to entry
    - Market research insights
    """
    try:
        ticker = ticker.upper()
        logger.info(f"Getting industry analysis for {ticker}")
        
        # Get full analysis to extract industry data
        analysis = await section4_service.generate_section4_report(ticker)
        industry_data = analysis.get("detailed_analysis", {}).get("industry_dynamics", {})
        market_research = analysis.get("detailed_analysis", {}).get("market_research", {})
        
        return {
            "success": True,
            "ticker": ticker,
            "industry_analysis": {
                "industry_trends": industry_data.get("industry_trends", []),
                "market_sentiment": industry_data.get("market_sentiment", "neutral"),
                "barriers_to_entry": industry_data.get("barriers_to_entry", "Medium"),
                "switching_costs": industry_data.get("switching_costs", "Medium"),
                "recent_news_count": market_research.get("recent_news_count", 0),
                "key_insights": market_research.get("key_insights", [])
            },
            "message": f"Industry analysis retrieved for {ticker}"
        }
        
    except Exception as e:
        logger.error(f"Error getting industry analysis for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get industry analysis: {str(e)}"
        )

@router.post("/refresh-analysis/{ticker}")
async def refresh_competitive_analysis(
    ticker: str,
    background_tasks: BackgroundTasks
) -> Dict[str, Any]:
    """
    Force refresh of competitive analysis (bypass cache)
    
    - **ticker**: Stock ticker symbol
    
    Triggers fresh analysis generation in background
    """
    try:
        ticker = ticker.upper()
        logger.info(f"Refreshing competitive analysis for {ticker}")
        
        # Add background task to refresh analysis
        background_tasks.add_task(
            section4_service.generate_section4_report,
            ticker,
            False  # Don't use cache
        )
        
        return {
            "success": True,
            "ticker": ticker,
            "message": f"Competitive analysis refresh initiated for {ticker}",
            "status": "processing"
        }
        
    except Exception as e:
        logger.error(f"Error refreshing analysis for {ticker}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh analysis: {str(e)}"
        )

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """Health check endpoint for Section 4 services"""
    try:
        # Test basic functionality
        test_ticker = "AAPL"
        summary = await get_market_position_summary(test_ticker)
        
        return {
            "success": True,
            "service": "Section 4 - Competitive Analysis",
            "status": "healthy",
            "test_result": "passed" if summary else "failed",
            "message": "Section 4 services are operational"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "service": "Section 4 - Competitive Analysis", 
            "status": "unhealthy",
            "error": str(e),
            "message": "Section 4 services are experiencing issues"
        }