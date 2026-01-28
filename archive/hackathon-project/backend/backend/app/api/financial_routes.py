"""
Financial Data API Routes - Real-time financial data endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
from ..services.financial_aggregator import financial_aggregator
from ..services.financial_data_service import financial_data_service
from ..services.alpha_vantage_service import alpha_vantage_service
from ..services.yahoo_finance_service import yahoo_finance_service
from ..services.sec_edgar_service import sec_edgar_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/financial", tags=["financial-data"])

@router.get("/stock/{symbol}")
async def get_stock_data(symbol: str):
    """Get comprehensive stock data for a symbol"""
    try:
        symbol = symbol.upper()
        data = await financial_aggregator.get_comprehensive_stock_data(symbol)
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error fetching stock data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/price/{symbol}")
async def get_real_time_price(symbol: str):
    """Get real-time price for a stock symbol"""
    try:
        symbol = symbol.upper()
        price_data = await financial_data_service.get_real_time_price(symbol)
        return {
            "success": True,
            "data": price_data.dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/prices")
async def get_multiple_prices(symbols: str = Query(..., description="Comma-separated stock symbols")):
    """Get real-time prices for multiple symbols"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        data = await financial_aggregator.get_real_time_market_data(symbol_list)
        return {
            "success": True,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching multiple prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/historical/{symbol}")
async def get_historical_data(
    symbol: str,
    period: str = Query("1y", description="Period: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"),
    interval: str = Query("1d", description="Interval: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo")
):
    """Get historical price data"""
    try:
        symbol = symbol.upper()
        hist_data = await yahoo_finance_service.get_historical_data(symbol, period, interval)
        
        # Convert DataFrame to dict for JSON serialization
        hist_dict = hist_data.to_dict('index')
        
        # Convert timestamps to strings
        formatted_data = {}
        for timestamp, values in hist_dict.items():
            formatted_data[timestamp.isoformat()] = values
        
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "period": period,
                "interval": interval,
                "historical_data": formatted_data
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching historical data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/company/{symbol}")
async def get_company_info(symbol: str):
    """Get comprehensive company information"""
    try:
        symbol = symbol.upper()
        company_info = await financial_data_service.get_company_info(symbol)
        return {
            "success": True,
            "data": company_info.dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching company info for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/metrics/{symbol}")
async def get_financial_metrics(symbol: str):
    """Get financial metrics and ratios"""
    try:
        symbol = symbol.upper()
        metrics = await financial_data_service.get_financial_metrics(symbol)
        return {
            "success": True,
            "data": metrics.dict(),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching financial metrics for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/statements/{symbol}")
async def get_financial_statements(symbol: str):
    """Get financial statements (income, balance sheet, cash flow)"""
    try:
        symbol = symbol.upper()
        statements = await yahoo_finance_service.get_financial_statements(symbol)
        return {
            "success": True,
            "data": statements,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching financial statements for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/earnings/{symbol}")
async def get_earnings_data(symbol: str):
    """Get earnings data and estimates"""
    try:
        symbol = symbol.upper()
        earnings = await yahoo_finance_service.get_earnings_data(symbol)
        return {
            "success": True,
            "data": earnings,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching earnings data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analysis/{symbol}")
async def get_financial_analysis(symbol: str):
    """Get comprehensive financial analysis"""
    try:
        symbol = symbol.upper()
        analysis = await financial_aggregator.get_financial_analysis(symbol)
        return {
            "success": True,
            "data": analysis,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error performing financial analysis for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sec-filings/{symbol}")
async def get_sec_filings(
    symbol: str,
    filing_types: Optional[str] = Query(None, description="Comma-separated filing types (10-K, 10-Q, 8-K, etc.)"),
    limit: int = Query(10, description="Number of filings to retrieve")
):
    """Get SEC filings for a company"""
    try:
        symbol = symbol.upper()
        
        filing_type_list = None
        if filing_types:
            filing_type_list = [ft.strip() for ft in filing_types.split(",")]
        
        filings = await sec_edgar_service.get_recent_filings(symbol, filing_type_list, limit)
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "filings": filings
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching SEC filings for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sec-filing-content/{symbol}")
async def get_sec_filing_content(
    symbol: str,
    accession_number: str = Query(..., description="SEC accession number"),
    primary_document: str = Query(..., description="Primary document filename")
):
    """Get content of a specific SEC filing"""
    try:
        symbol = symbol.upper()
        content = await sec_edgar_service.get_filing_content(accession_number, primary_document)
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "accession_number": accession_number,
                "primary_document": primary_document,
                "content": content[:10000]  # Limit content length for API response
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching SEC filing content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/technical-indicators/{symbol}")
async def get_technical_indicators(symbol: str):
    """Get technical analysis indicators"""
    try:
        symbol = symbol.upper()
        indicators = await alpha_vantage_service.get_technical_indicators(symbol)
        return {
            "success": True,
            "data": indicators,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching technical indicators for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/analyst-recommendations/{symbol}")
async def get_analyst_recommendations(symbol: str):
    """Get analyst recommendations and price targets"""
    try:
        symbol = symbol.upper()
        recommendations = await yahoo_finance_service.get_analyst_recommendations(symbol)
        return {
            "success": True,
            "data": recommendations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching analyst recommendations for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/institutional-holders/{symbol}")
async def get_institutional_holders(symbol: str):
    """Get institutional and mutual fund holders"""
    try:
        symbol = symbol.upper()
        holders = await yahoo_finance_service.get_institutional_holders(symbol)
        return {
            "success": True,
            "data": holders,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching institutional holders for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/options/{symbol}")
async def get_options_data(symbol: str):
    """Get options chain data"""
    try:
        symbol = symbol.upper()
        options = await yahoo_finance_service.get_options_data(symbol)
        return {
            "success": True,
            "data": options,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching options data for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dividends/{symbol}")
async def get_dividend_history(symbol: str):
    """Get dividend payment history"""
    try:
        symbol = symbol.upper()
        dividends = await yahoo_finance_service.get_dividend_history(symbol)
        return {
            "success": True,
            "data": dividends,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching dividend history for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/market-news/{symbol}")
async def get_market_news(symbol: str):
    """Get latest market news for a symbol"""
    try:
        symbol = symbol.upper()
        news = await alpha_vantage_service.get_market_news(symbol)
        return {
            "success": True,
            "data": news,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching market news for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/search")
async def search_symbols(keywords: str = Query(..., description="Keywords to search for")):
    """Search for stock symbols"""
    try:
        results = await alpha_vantage_service.search_symbol(keywords)
        return {
            "success": True,
            "data": results,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error searching symbols for '{keywords}': {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/validate/{symbol}")
async def validate_symbol(symbol: str):
    """Validate if a stock symbol exists"""
    try:
        symbol = symbol.upper()
        is_valid = await financial_data_service.validate_symbol(symbol)
        return {
            "success": True,
            "data": {
                "symbol": symbol,
                "is_valid": is_valid
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error validating symbol {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/compare")
async def compare_stocks(
    symbols: str = Query(..., description="Comma-separated stock symbols to compare"),
    metrics: Optional[str] = Query(None, description="Comma-separated metrics to compare")
):
    """Compare multiple stocks"""
    try:
        symbol_list = [s.strip().upper() for s in symbols.split(",")]
        
        if len(symbol_list) < 2:
            raise HTTPException(status_code=400, detail="At least 2 symbols required for comparison")
        
        primary_symbol = symbol_list[0]
        peer_symbols = symbol_list[1:]
        
        comparison = await financial_aggregator.get_market_comparison(primary_symbol, peer_symbols)
        return {
            "success": True,
            "data": comparison,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error comparing stocks: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def health_check():
    """Health check endpoint for financial data services"""
    try:
        # Test basic functionality
        test_symbol = "AAPL"
        is_valid = await financial_data_service.validate_symbol(test_symbol)
        
        return {
            "success": True,
            "data": {
                "status": "healthy",
                "services": {
                    "yahoo_finance": "operational",
                    "alpha_vantage": "operational" if alpha_vantage_service.api_key else "no_api_key",
                    "sec_edgar": "operational",
                    "symbol_validation": "operational" if is_valid else "limited"
                }
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "success": False,
            "data": {
                "status": "unhealthy",
                "error": str(e)
            },
            "timestamp": datetime.now().isoformat()
        }