"""
Alpha Vantage API Service - Professional financial data integration
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
import httpx
import pandas as pd
from datetime import datetime
from ..core.config import settings

logger = logging.getLogger(__name__)

class AlphaVantageService:
    def __init__(self):
        self.api_key = settings.ALPHA_VANTAGE_API_KEY
        self.base_url = "https://www.alphavantage.co/query"
        self.session = None
        
    async def _get_session(self):
        if not self.session:
            self.session = httpx.AsyncClient(timeout=30.0)
        return self.session
    
    async def _make_request(self, params: Dict) -> Dict:
        """Make API request with error handling"""
        params['apikey'] = self.api_key
        
        session = await self._get_session()
        try:
            response = await session.get(self.base_url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if 'Error Message' in data:
                raise ValueError(f"Alpha Vantage API Error: {data['Error Message']}")
            if 'Note' in data:
                raise ValueError(f"Alpha Vantage API Limit: {data['Note']}")
                
            return data
        except httpx.HTTPError as e:
            logger.error(f"HTTP error in Alpha Vantage request: {e}")
            raise
        except Exception as e:
            logger.error(f"Error in Alpha Vantage request: {e}")
            raise

    async def get_intraday_data(self, symbol: str, interval: str = "5min") -> Dict:
        """Get intraday stock data"""
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'outputsize': 'compact'
        }
        return await self._make_request(params)

    async def get_daily_data(self, symbol: str, outputsize: str = "compact") -> Dict:
        """Get daily stock data"""
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize
        }
        return await self._make_request(params)

    async def get_company_overview(self, symbol: str) -> Dict:
        """Get comprehensive company overview"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }
        return await self._make_request(params)

    async def get_income_statement(self, symbol: str) -> Dict:
        """Get annual and quarterly income statements"""
        params = {
            'function': 'INCOME_STATEMENT',
            'symbol': symbol
        }
        return await self._make_request(params)

    async def get_balance_sheet(self, symbol: str) -> Dict:
        """Get annual and quarterly balance sheets"""
        params = {
            'function': 'BALANCE_SHEET',
            'symbol': symbol
        }
        return await self._make_request(params)

    async def get_cash_flow(self, symbol: str) -> Dict:
        """Get annual and quarterly cash flow statements"""
        params = {
            'function': 'CASH_FLOW',
            'symbol': symbol
        }
        return await self._make_request(params)

    async def get_earnings(self, symbol: str) -> Dict:
        """Get quarterly and annual earnings data"""
        params = {
            'function': 'EARNINGS',
            'symbol': symbol
        }
        return await self._make_request(params)

    async def get_financial_ratios(self, symbol: str) -> Dict:
        """Calculate key financial ratios from fundamental data"""
        try:
            # Get all fundamental data concurrently
            overview_task = self.get_company_overview(symbol)
            income_task = self.get_income_statement(symbol)
            balance_task = self.get_balance_sheet(symbol)
            
            overview, income, balance = await asyncio.gather(
                overview_task, income_task, balance_task, return_exceptions=True
            )
            
            ratios = {}
            
            # Extract ratios from overview if available
            if not isinstance(overview, Exception) and overview:
                ratios.update({
                    'pe_ratio': self._safe_float(overview.get('PERatio')),
                    'peg_ratio': self._safe_float(overview.get('PEGRatio')),
                    'price_to_book': self._safe_float(overview.get('PriceToBookRatio')),
                    'price_to_sales': self._safe_float(overview.get('PriceToSalesRatioTTM')),
                    'ev_to_revenue': self._safe_float(overview.get('EVToRevenue')),
                    'ev_to_ebitda': self._safe_float(overview.get('EVToEBITDA')),
                    'profit_margin': self._safe_float(overview.get('ProfitMargin')),
                    'operating_margin': self._safe_float(overview.get('OperatingMarginTTM')),
                    'return_on_assets': self._safe_float(overview.get('ReturnOnAssetsTTM')),
                    'return_on_equity': self._safe_float(overview.get('ReturnOnEquityTTM')),
                    'revenue_per_share': self._safe_float(overview.get('RevenuePerShareTTM')),
                    'quarterly_earnings_growth': self._safe_float(overview.get('QuarterlyEarningsGrowthYOY')),
                    'quarterly_revenue_growth': self._safe_float(overview.get('QuarterlyRevenueGrowthYOY')),
                    'analyst_target_price': self._safe_float(overview.get('AnalystTargetPrice')),
                    'trailing_pe': self._safe_float(overview.get('TrailingPE')),
                    'forward_pe': self._safe_float(overview.get('ForwardPE')),
                    'dividend_per_share': self._safe_float(overview.get('DividendPerShare')),
                    'dividend_yield': self._safe_float(overview.get('DividendYield')),
                    'beta': self._safe_float(overview.get('Beta'))
                })
            
            return {
                'symbol': symbol,
                'ratios': ratios,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating financial ratios for {symbol}: {e}")
            raise

    async def get_technical_indicators(self, symbol: str) -> Dict:
        """Get technical analysis indicators"""
        try:
            # RSI
            rsi_params = {
                'function': 'RSI',
                'symbol': symbol,
                'interval': 'daily',
                'time_period': 14,
                'series_type': 'close'
            }
            
            # MACD
            macd_params = {
                'function': 'MACD',
                'symbol': symbol,
                'interval': 'daily',
                'series_type': 'close'
            }
            
            # Bollinger Bands
            bb_params = {
                'function': 'BBANDS',
                'symbol': symbol,
                'interval': 'daily',
                'time_period': 20,
                'series_type': 'close'
            }
            
            # Execute requests concurrently
            rsi_task = self._make_request(rsi_params)
            macd_task = self._make_request(macd_params)
            bb_task = self._make_request(bb_params)
            
            rsi_data, macd_data, bb_data = await asyncio.gather(
                rsi_task, macd_task, bb_task, return_exceptions=True
            )
            
            indicators = {
                'symbol': symbol,
                'rsi': rsi_data if not isinstance(rsi_data, Exception) else None,
                'macd': macd_data if not isinstance(macd_data, Exception) else None,
                'bollinger_bands': bb_data if not isinstance(bb_data, Exception) else None,
                'last_updated': datetime.now().isoformat()
            }
            
            return indicators
            
        except Exception as e:
            logger.error(f"Error fetching technical indicators for {symbol}: {e}")
            raise

    async def get_market_news(self, symbol: str) -> Dict:
        """Get latest market news for a symbol"""
        params = {
            'function': 'NEWS_SENTIMENT',
            'tickers': symbol,
            'limit': 50
        }
        return await self._make_request(params)

    async def search_symbol(self, keywords: str) -> Dict:
        """Search for stock symbols"""
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': keywords
        }
        return await self._make_request(params)

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == 'None' or value == '' or value == 'N/A':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    async def close(self):
        """Close the HTTP session"""
        if self.session:
            await self.session.aclose()

# Global instance
alpha_vantage_service = AlphaVantageService()