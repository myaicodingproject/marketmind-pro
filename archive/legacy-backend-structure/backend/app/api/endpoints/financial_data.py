from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
import asyncio
import logging
from app.services.financial_data import financial_service, StockData, FinancialStatement
from app.core.auth import get_current_user
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/stock/{symbol}", response_model=Dict[str, Any])
async def get_stock_data(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get real-time stock data"""
    try:
        async with financial_service as service:
            stock_data = await service.get_stock_data(symbol.upper())
            
            if not stock_data:
                raise HTTPException(status_code=404, detail=f"Stock data not found for {symbol}")
                
            return {
                "symbol": stock_data.symbol,
                "price": stock_data.price,
                "change": stock_data.change,
                "change_percent": stock_data.change_percent,
                "volume": stock_data.volume,
                "market_cap": stock_data.market_cap,
                "pe_ratio": stock_data.pe_ratio,
                "dividend_yield": stock_data.dividend_yield,
                "timestamp": "real-time"
            }
    except Exception as e:
        logger.error(f"Error fetching stock data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/financials/{symbol}")
async def get_financial_statements(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get financial statements from SEC EDGAR"""
    try:
        async with financial_service as service:
            statements = await service.get_financial_statements(symbol.upper())
            
            return {
                "symbol": symbol.upper(),
                "statements": [
                    {
                        "period": stmt.period,
                        "revenue": stmt.revenue,
                        "net_income": stmt.net_income,
                        "total_assets": stmt.total_assets,
                        "total_debt": stmt.total_debt,
                        "cash": stmt.cash,
                        "filing_date": stmt.filing_date
                    }
                    for stmt in statements
                ]
            }
    except Exception as e:
        logger.error(f"Error fetching financials: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/metrics/{symbol}")
async def get_market_metrics(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get comprehensive market metrics"""
    try:
        async with financial_service as service:
            metrics = await service.get_market_metrics(symbol.upper())
            
            return {
                "symbol": symbol.upper(),
                "metrics": metrics
            }
    except Exception as e:
        logger.error(f"Error fetching metrics: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/comprehensive/{symbol}")
async def get_comprehensive_data(
    symbol: str,
    current_user: User = Depends(get_current_user)
):
    """Get all financial data for a symbol"""
    try:
        async with financial_service as service:
            # Fetch all data concurrently
            stock_data, statements, metrics = await asyncio.gather(
                service.get_stock_data(symbol.upper()),
                service.get_financial_statements(symbol.upper()),
                service.get_market_metrics(symbol.upper()),
                return_exceptions=True
            )
            
            result = {"symbol": symbol.upper()}
            
            if isinstance(stock_data, StockData):
                result["stock_data"] = {
                    "price": stock_data.price,
                    "change": stock_data.change,
                    "change_percent": stock_data.change_percent,
                    "volume": stock_data.volume,
                    "market_cap": stock_data.market_cap,
                    "pe_ratio": stock_data.pe_ratio,
                    "dividend_yield": stock_data.dividend_yield
                }
            
            if isinstance(statements, list):
                result["financial_statements"] = [
                    {
                        "period": stmt.period,
                        "revenue": stmt.revenue,
                        "net_income": stmt.net_income,
                        "total_assets": stmt.total_assets,
                        "total_debt": stmt.total_debt,
                        "cash": stmt.cash,
                        "filing_date": stmt.filing_date
                    }
                    for stmt in statements
                ]
            
            if isinstance(metrics, dict):
                result["market_metrics"] = metrics
                
            return result
            
    except Exception as e:
        logger.error(f"Error fetching comprehensive data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")