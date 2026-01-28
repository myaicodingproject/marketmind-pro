#!/usr/bin/env python3
"""
Section 1 Integration - Simple FastAPI Server
Standalone server for testing Section 1 Executive Summary agent
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import logging
import uvicorn

from app.services.section1_executive_summary import Section1ExecutiveSummaryAgent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MarketMind Pro - Section 1 Agent",
    description="Executive Summary Generation Service",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Section 1 agent
section1_agent = Section1ExecutiveSummaryAgent()

class ExecutiveSummaryRequest(BaseModel):
    ticker: str
    include_charts: bool = True

class ExecutiveSummaryResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    charts: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "MarketMind Pro - Section 1 Agent",
        "status": "running",
        "endpoints": {
            "generate": "/api/v1/section1/generate",
            "data": "/api/v1/section1/data/{ticker}",
            "health": "/api/v1/section1/health"
        }
    }

@app.post("/api/v1/section1/generate", response_model=ExecutiveSummaryResponse)
async def generate_executive_summary(request: ExecutiveSummaryRequest):
    """Generate executive summary for given ticker"""
    try:
        logger.info(f"Generating executive summary for {request.ticker}")
        
        # Generate executive summary
        summary_data = await section1_agent.generate_executive_summary(request.ticker)
        
        # Generate charts if requested
        charts_data = None
        if request.include_charts:
            charts_data = await section1_agent.generate_charts_data(request.ticker, summary_data)
        
        logger.info(f"Successfully generated executive summary for {request.ticker}")
        
        return ExecutiveSummaryResponse(
            success=True,
            data=summary_data,
            charts=charts_data
        )
        
    except Exception as e:
        logger.error(f"Error generating executive summary for {request.ticker}: {e}")
        return ExecutiveSummaryResponse(
            success=False,
            error=str(e)
        )

@app.get("/api/v1/section1/data/{ticker}")
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

@app.get("/api/v1/section1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy", 
        "service": "Section 1 - Executive Summary",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/v1/section1/test/{ticker}")
async def test_ticker(ticker: str):
    """Quick test endpoint for a ticker"""
    try:
        # Generate summary
        summary = await section1_agent.generate_executive_summary(ticker)
        
        # Return simplified response
        return {
            "success": True,
            "ticker": ticker,
            "recommendation": summary["recommendation"],
            "price_target": summary["price_target"],
            "current_price": summary["current_price"],
            "upside_potential": summary["upside_potential"],
            "confidence": summary["confidence_level"],
            "key_metrics": {
                "market_cap": summary["key_metrics"]["market_cap"],
                "pe_ratio": summary["key_metrics"]["pe_ratio"],
                "roe": summary["key_metrics"]["roe"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error testing ticker {ticker}: {e}")
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "section1_server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )