#!/usr/bin/env python3
"""
Section 5 API Endpoints - Competitive Advantages Analysis
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import logging

from ..services.section5_competitive_advantages_agent import Section5CompetitiveAdvantagesAgent

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/section5", tags=["Section 5 - Competitive Advantages"])

# Initialize agent (would be dependency injected in production)
section5_agent = Section5CompetitiveAdvantagesAgent()

@router.post("/analyze/{ticker}")
async def generate_competitive_advantages_analysis(
    ticker: str,
    background_tasks: BackgroundTasks,
    company_data: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Generate Section 5 competitive advantages analysis for a given ticker
    
    Args:
        ticker: Stock ticker symbol
        company_data: Optional company data context
        
    Returns:
        Comprehensive competitive advantages analysis
    """
    try:
        logger.info(f"Starting Section 5 analysis for {ticker}")
        
        # Use provided company data or fetch default
        if not company_data:
            company_data = {
                "ticker": ticker,
                "company_name": f"{ticker} Inc.",
                "sector": "Technology",  # Would be fetched from data service
                "industry": "Software"
            }
        
        # Generate analysis
        analysis = await section5_agent.generate_analysis(ticker, company_data)
        
        logger.info(f"Completed Section 5 analysis for {ticker}")
        return {
            "status": "success",
            "ticker": ticker,
            "analysis": analysis
        }
        
    except Exception as e:
        logger.error(f"Error generating Section 5 analysis for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate competitive advantages analysis: {str(e)}"
        )

@router.get("/moats/{ticker}")
async def get_competitive_moats_analysis(ticker: str) -> Dict[str, Any]:
    """
    Get competitive moats analysis for a specific ticker
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Competitive moats assessment
    """
    try:
        # This would typically fetch from cache or database
        # For now, generate fresh analysis
        company_data = {"ticker": ticker}
        moats_analysis = await section5_agent._analyze_competitive_moats(ticker, company_data)
        
        return {
            "status": "success",
            "ticker": ticker,
            "moats_analysis": moats_analysis
        }
        
    except Exception as e:
        logger.error(f"Error getting moats analysis for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get moats analysis: {str(e)}"
        )

@router.get("/porters-forces/{ticker}")
async def get_porters_five_forces_analysis(ticker: str) -> Dict[str, Any]:
    """
    Get Porter's Five Forces analysis for a specific ticker
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Porter's Five Forces assessment
    """
    try:
        company_data = {"ticker": ticker}
        porters_analysis = await section5_agent._assess_porters_five_forces(ticker, company_data)
        
        return {
            "status": "success",
            "ticker": ticker,
            "porters_analysis": {
                "threat_of_new_entrants": porters_analysis.threat_of_new_entrants,
                "bargaining_power_suppliers": porters_analysis.bargaining_power_suppliers,
                "bargaining_power_buyers": porters_analysis.bargaining_power_buyers,
                "threat_of_substitutes": porters_analysis.threat_of_substitutes,
                "competitive_rivalry": porters_analysis.competitive_rivalry,
                "overall_attractiveness": porters_analysis.overall_attractiveness
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting Porter's analysis for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get Porter's Five Forces analysis: {str(e)}"
        )

@router.get("/barriers/{ticker}")
async def get_barriers_to_entry_analysis(ticker: str) -> Dict[str, Any]:
    """
    Get barriers to entry analysis for a specific ticker
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Barriers to entry assessment
    """
    try:
        company_data = {"ticker": ticker}
        barriers_analysis = await section5_agent._evaluate_barriers_to_entry(ticker, company_data)
        
        return {
            "status": "success",
            "ticker": ticker,
            "barriers_analysis": barriers_analysis
        }
        
    except Exception as e:
        logger.error(f"Error getting barriers analysis for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get barriers to entry analysis: {str(e)}"
        )

@router.get("/sustainability/{ticker}")
async def get_competitive_sustainability_analysis(ticker: str) -> Dict[str, Any]:
    """
    Get competitive sustainability analysis for a specific ticker
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Competitive advantage sustainability assessment
    """
    try:
        company_data = {"ticker": ticker}
        sustainability_analysis = await section5_agent._analyze_competitive_sustainability(ticker, company_data)
        
        return {
            "status": "success",
            "ticker": ticker,
            "sustainability_analysis": sustainability_analysis
        }
        
    except Exception as e:
        logger.error(f"Error getting sustainability analysis for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get competitive sustainability analysis: {str(e)}"
        )

@router.get("/visualizations/{ticker}")
async def get_competitive_visualizations(ticker: str) -> Dict[str, Any]:
    """
    Get competitive advantage visualizations for a specific ticker
    
    Args:
        ticker: Stock ticker symbol
        
    Returns:
        Visualization data for competitive analysis
    """
    try:
        # Generate sample analysis data for visualizations
        analysis_data = {
            "moats": await section5_agent._analyze_competitive_moats(ticker, {"ticker": ticker}),
            "porters": await section5_agent._assess_porters_five_forces(ticker, {"ticker": ticker}),
            "barriers": await section5_agent._evaluate_barriers_to_entry(ticker, {"ticker": ticker}),
            "sustainability": await section5_agent._analyze_competitive_sustainability(ticker, {"ticker": ticker})
        }
        
        visualizations = await section5_agent._create_competitive_visualizations(ticker, analysis_data)
        
        return {
            "status": "success",
            "ticker": ticker,
            "visualizations": visualizations
        }
        
    except Exception as e:
        logger.error(f"Error getting visualizations for {ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get competitive visualizations: {str(e)}"
        )