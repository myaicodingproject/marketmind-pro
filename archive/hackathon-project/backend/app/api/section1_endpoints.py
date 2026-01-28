#!/usr/bin/env python3
"""
Section 1 API Endpoints - Executive Summary
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional
import logging

from app.services.section1_executive_summary import Section1ExecutiveSummaryAgent

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/section1", tags=["Section 1 - Executive Summary"])

# Initialize the agent
section1_agent = Section1ExecutiveSummaryAgent()

class ExecutiveSummaryRequest(BaseModel):
    ticker: str
    include_charts: bool = True

class ExecutiveSummaryResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    charts: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/generate", response_model=ExecutiveSummaryResponse)
async def generate_executive_summary(request: ExecutiveSummaryRequest):
    """Generate executive summary for given ticker"""
    try:
        # Generate executive summary
        summary_data = await section1_agent.generate_executive_summary(request.ticker)
        
        # Generate charts if requested
        charts_data = None
        if request.include_charts:
            charts_data = await section1_agent.generate_charts_data(request.ticker, summary_data)
        
        return ExecutiveSummaryResponse(
            success=True,
            data=summary_data,
            charts=charts_data
        )
        
    except Exception as e:
        logger.error(f"Error generating executive summary for {request.ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/data/{ticker}")
async def get_stored_data(ticker: str):
    """Get stored data for ticker"""
    try:
        data = section1_agent.get_stored_data(ticker)
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
        
        return {"success": True, "data": data}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving data for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Section 1 - Executive Summary"}