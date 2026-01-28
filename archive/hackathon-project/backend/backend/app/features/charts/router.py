"""
Chart Router - API endpoints for chart data generation
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
import logging

from .service import chart_service
from ...shared.schemas.schemas import ChartRequest, ChartResponse, ChartSummaryResponse
from ...shared.utils.exceptions import ValidationError, DataProcessingError

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/charts", tags=["charts"])

@router.post("/generate/{ticker}", response_model=ChartResponse)
async def generate_company_charts(
    ticker: str,
    request: ChartRequest
):
    """
    Generate all chart configurations for a company
    """
    try:
        logger.info(f"Generating charts for {ticker}")
        
        # Validate request
        is_valid, errors = chart_service.validate_chart_request({
            'ticker': ticker,
            'chart_types': request.chart_types
        })
        
        if not is_valid:
            raise HTTPException(status_code=400, detail=f"Invalid request: {'; '.join(errors)}")
        
        # Generate charts
        charts = await chart_service.generate_company_charts(ticker, request.financial_data)
        
        # Filter charts if specific types requested
        if request.chart_types:
            filtered_charts = {k: v for k, v in charts.items() if k in request.chart_types}
            charts = filtered_charts
        
        # Serialize for API response
        serialized_charts = chart_service.serialize_charts_for_api(charts)
        
        return ChartResponse(
            ticker=ticker,
            charts=serialized_charts,
            generated_at=None,  # Will be set by response model
            chart_count=len(serialized_charts)
        )
        
    except ValidationError as e:
        logger.error(f"Validation error for {ticker}: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except DataProcessingError as e:
        logger.error(f"Data processing error for {ticker}: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    
    except Exception as e:
        logger.error(f"Chart generation failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Chart generation failed")

@router.post("/peer-comparison/{ticker}")
async def generate_peer_comparison(
    ticker: str,
    company_data: Dict,
    peer_tickers: List[str] = Query(..., description="List of peer company tickers"),
    peer_data: List[Dict] = None
):
    """
    Generate peer comparison chart
    """
    try:
        logger.info(f"Generating peer comparison for {ticker} vs {peer_tickers}")
        
        if not peer_data:
            raise HTTPException(status_code=400, detail="Peer data is required")
        
        if len(peer_tickers) != len(peer_data):
            raise HTTPException(status_code=400, detail="Peer tickers and data count mismatch")
        
        # Generate peer comparison chart
        chart = await chart_service.generate_peer_comparison_chart(
            ticker, company_data, peer_tickers, peer_data
        )
        
        # Serialize chart
        serialized_chart = chart_service.serialize_charts_for_api({'peer_comparison': chart})
        
        return {
            'ticker': ticker,
            'peer_tickers': peer_tickers,
            'chart': serialized_chart['peer_comparison']
        }
        
    except Exception as e:
        logger.error(f"Peer comparison generation failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Peer comparison generation failed")

@router.get("/summary/{ticker}", response_model=ChartSummaryResponse)
async def get_chart_summary(
    ticker: str,
    financial_data: Dict
):
    """
    Get summary of available chart data for a company
    """
    try:
        logger.info(f"Getting chart summary for {ticker}")
        
        summary = await chart_service.get_chart_data_summary(ticker, financial_data)
        
        return ChartSummaryResponse(**summary)
        
    except Exception as e:
        logger.error(f"Chart summary failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Chart summary generation failed")

@router.get("/time-series/{ticker}")
async def generate_time_series_chart(
    ticker: str,
    data_type: str = Query(..., description="Type of time series data (revenue, margins)"),
    financial_data: Dict = None,
    periods: int = Query(5, description="Number of periods to include")
):
    """
    Generate time series chart for specific data type
    """
    try:
        logger.info(f"Generating {data_type} time series for {ticker}")
        
        if not financial_data:
            raise HTTPException(status_code=400, detail="Financial data is required")
        
        chart = await chart_service.generate_time_series_chart(
            ticker, data_type, financial_data, periods
        )
        
        serialized_chart = chart_service.serialize_charts_for_api({data_type: chart})
        
        return {
            'ticker': ticker,
            'data_type': data_type,
            'periods': periods,
            'chart': serialized_chart[data_type]
        }
        
    except Exception as e:
        logger.error(f"Time series generation failed for {ticker}: {e}")
        raise HTTPException(status_code=500, detail="Time series generation failed")

@router.get("/health")
async def chart_service_health():
    """
    Health check endpoint for chart service
    """
    return {
        'status': 'healthy',
        'service': 'chart_service',
        'version': '1.0.0'
    }