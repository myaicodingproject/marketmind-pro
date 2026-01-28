#!/usr/bin/env python3
"""
Section 6 API Endpoints
Market Size & Growth Potential Analysis endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any, Optional
import logging

from ..services.section6_integration_service import Section6IntegrationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/section6", tags=["Section 6 - Market Analysis"])

# Initialize service
section6_service = Section6IntegrationService()

@router.post("/generate/{ticker}")
async def generate_market_analysis(
    ticker: str,
    background_tasks: BackgroundTasks,
    context_data: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generate Section 6 Market Size & Growth Potential analysis
    
    Args:
        ticker: Stock ticker symbol
        context_data: Optional context from other sections
        
    Returns:
        Market analysis report with TAM, SAM, forecasts, and strategic roadmap
    """
    try:
        logger.info(f"Generating Section 6 market analysis for {ticker}")
        
        # Generate analysis
        result = await section6_service.generate_section6_report(ticker, context_data)
        
        if 'error' in result.get('section_6', {}):
            raise HTTPException(status_code=500, detail=result['section_6']['error'])
        
        return {
            "status": "success",
            "ticker": ticker,
            "section": 6,
            "title": "Market Size & Growth Potential",
            "data": result,
            "message": "Market analysis generated successfully"
        }
        
    except Exception as e:
        logger.error(f"Error generating Section 6 for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{ticker}")
async def get_analysis_status(ticker: str) -> Dict[str, Any]:
    """
    Get status of Section 6 analysis capabilities
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Status information for Section 6 analysis
    """
    try:
        status = await section6_service.get_section_status(ticker)
        
        return {
            "status": "success",
            "ticker": ticker,
            "section_info": status
        }
        
    except Exception as e:
        logger.error(f"Error getting Section 6 status for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-data/{ticker}")
async def get_market_data_preview(ticker: str) -> Dict[str, Any]:
    """
    Get preview of market data for the ticker
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Preview of market size and competitive data
    """
    try:
        # Get basic market data without full analysis
        agent = section6_service.market_agent
        company_data = await agent._get_company_data(ticker)
        market_data = await agent._research_market_data(ticker, company_data)
        
        return {
            "status": "success",
            "ticker": ticker,
            "preview": {
                "company": {
                    "name": company_data.get('company_name', ''),
                    "sector": company_data.get('sector', ''),
                    "industry": company_data.get('industry', ''),
                    "market_cap": company_data.get('market_cap', 0)
                },
                "market": {
                    "tam_size_billions": market_data.get('tam_size_billions', 0),
                    "sam_size_billions": market_data.get('sam_size_billions', 0),
                    "historical_growth": market_data.get('historical_growth', 0),
                    "key_segments": market_data.get('key_segments', [])
                }
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting market data preview for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/charts/{ticker}")
async def generate_market_charts(ticker: str) -> Dict[str, Any]:
    """
    Generate market analysis charts for the ticker
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Chart data for market visualization
    """
    try:
        agent = section6_service.market_agent
        
        # Get data needed for charts
        company_data = await agent._get_company_data(ticker)
        market_data = await agent._research_market_data(ticker, company_data)
        growth_analysis = await agent._generate_growth_forecasts(ticker, market_data, {})
        
        # Generate charts
        charts = await agent._generate_market_charts(ticker, market_data, growth_analysis)
        
        return {
            "status": "success",
            "ticker": ticker,
            "charts": charts,
            "chart_count": len(charts)
        }
        
    except Exception as e:
        logger.error(f"Error generating charts for {ticker}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))