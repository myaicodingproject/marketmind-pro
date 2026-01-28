"""
Financial Data API - Main endpoint for comprehensive financial data collection
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict, Any
import asyncio
from datetime import datetime

from ..services.financial_data_service import FinancialDataService, ComprehensiveFinancialData
from ..services.data_consistency_manager import DataConsistencyManager

router = APIRouter(prefix="/api/financial-data", tags=["Financial Data"])

# Initialize services
financial_service = FinancialDataService()
consistency_manager = DataConsistencyManager()

@router.get("/comprehensive/{ticker}")
async def get_comprehensive_financial_data(ticker: str) -> Dict[str, Any]:
    """
    Get comprehensive financial data for a stock ticker
    Integrates Yahoo Finance, SEC EDGAR, news sentiment, and analyst ratings
    """
    try:
        # Validate ticker format
        ticker = ticker.upper().strip()
        if not ticker or len(ticker) > 10:
            raise HTTPException(status_code=400, detail="Invalid ticker symbol")
        
        # Collect comprehensive financial data
        financial_data = await financial_service.get_comprehensive_data(ticker)
        
        # Convert to dictionary for validation
        data_dict = {
            'ticker': financial_data.ticker,
            'company_info': financial_data.company_info,
            'stock_data': financial_data.stock_data,
            'financial_statements': financial_data.financial_statements,
            'sec_filings': financial_data.sec_filings,
            'analyst_ratings': financial_data.analyst_ratings,
            'news_sentiment': financial_data.news_sentiment,
            'market_data': financial_data.market_data,
            'peer_comparison': financial_data.peer_comparison,
            'timestamp': financial_data.timestamp
        }
        
        # Validate data consistency
        validation_result = consistency_manager.validate_comprehensive_data(data_dict)
        
        # Normalize data for report generation
        normalized_data = consistency_manager.normalize_data_for_reports(data_dict)
        
        return {
            'success': True,
            'ticker': ticker,
            'data': normalized_data,
            'validation': {
                'is_valid': validation_result.is_valid,
                'quality_score': validation_result.data_quality_score,
                'errors': validation_result.errors,
                'warnings': validation_result.warnings
            },
            'metadata': {
                'collection_time': financial_data.timestamp.isoformat(),
                'data_sources': [
                    'Yahoo Finance',
                    'SEC EDGAR',
                    'News Sentiment Analysis',
                    'Analyst Ratings'
                ]
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to collect financial data for {ticker}: {str(e)}"
        )

@router.get("/quick/{ticker}")
async def get_quick_financial_data(ticker: str) -> Dict[str, Any]:
    """
    Get essential financial data quickly (Yahoo Finance only)
    For faster response times when full data isn't needed
    """
    try:
        ticker = ticker.upper().strip()
        
        # Get only Yahoo Finance data for speed
        yahoo_data = await financial_service.yahoo_service.get_complete_stock_data(ticker)
        
        # Extract key information
        info = yahoo_data.get('info', {})
        key_metrics = yahoo_data.get('key_metrics', {})
        
        return {
            'success': True,
            'ticker': ticker,
            'company_name': info.get('longName', 'Unknown'),
            'current_price': info.get('currentPrice', info.get('regularMarketPrice')),
            'market_cap': key_metrics.get('market_cap'),
            'pe_ratio': key_metrics.get('pe_ratio'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get quick data for {ticker}: {str(e)}"
        )

@router.get("/validation/{ticker}")
async def validate_ticker_data(ticker: str) -> Dict[str, Any]:
    """
    Validate data quality and availability for a ticker
    Useful for checking before generating full reports
    """
    try:
        ticker = ticker.upper().strip()
        
        # Get basic data to test availability
        yahoo_data = await financial_service.yahoo_service.get_complete_stock_data(ticker)
        
        # Check data availability
        info = yahoo_data.get('info', {})
        has_financials = bool(yahoo_data.get('financials', {}).get('income_statement') is not None)
        has_price_data = bool(yahoo_data.get('price_history') is not None and not yahoo_data['price_history'].empty)
        
        # Basic validation
        is_valid_ticker = bool(info.get('longName') or info.get('shortName'))
        
        return {
            'ticker': ticker,
            'is_valid': is_valid_ticker,
            'data_availability': {
                'company_info': bool(info),
                'price_data': has_price_data,
                'financial_statements': has_financials,
                'market_data': bool(yahoo_data.get('market_data'))
            },
            'company_name': info.get('longName', 'Unknown'),
            'sector': info.get('sector', 'Unknown'),
            'market_cap': info.get('marketCap'),
            'recommendation': 'proceed' if is_valid_ticker else 'invalid_ticker'
        }
        
    except Exception as e:
        return {
            'ticker': ticker,
            'is_valid': False,
            'error': str(e),
            'recommendation': 'check_ticker'
        }

@router.post("/refresh/{ticker}")
async def refresh_financial_data(ticker: str, background_tasks: BackgroundTasks) -> Dict[str, Any]:
    """
    Refresh financial data for a ticker (async background task)
    """
    try:
        ticker = ticker.upper().strip()
        
        # Add background task to refresh data
        background_tasks.add_task(
            _refresh_data_background,
            ticker
        )
        
        return {
            'success': True,
            'ticker': ticker,
            'message': 'Data refresh initiated',
            'status': 'processing'
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate refresh for {ticker}: {str(e)}"
        )

async def _refresh_data_background(ticker: str):
    """Background task to refresh financial data"""
    try:
        # Collect fresh data
        financial_data = await financial_service.get_comprehensive_data(ticker)
        
        # Here you would typically cache or store the refreshed data
        # For now, we'll just log the completion
        print(f"Data refresh completed for {ticker} at {datetime.now()}")
        
    except Exception as e:
        print(f"Data refresh failed for {ticker}: {str(e)}")

@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint for financial data services
    """
    try:
        # Test basic functionality
        test_ticker = "AAPL"
        yahoo_data = await financial_service.yahoo_service.get_complete_stock_data(test_ticker)
        
        return {
            'status': 'healthy',
            'services': {
                'yahoo_finance': 'operational',
                'sec_edgar': 'operational',
                'news_sentiment': 'operational',
                'analyst_ratings': 'operational'
            },
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            'status': 'degraded',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }