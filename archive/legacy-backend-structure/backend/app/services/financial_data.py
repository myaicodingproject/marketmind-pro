import asyncio
import aiohttp
import redis.asyncio as redis
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import logging
from dataclasses import dataclass
from app.core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class StockData:
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[int] = None
    pe_ratio: Optional[float] = None
    dividend_yield: Optional[float] = None

@dataclass
class FinancialStatement:
    symbol: str
    period: str
    revenue: int
    net_income: int
    total_assets: int
    total_debt: int
    cash: int
    filing_date: str

class FinancialDataService:
    def __init__(self):
        self.redis_client = redis.from_url(settings.REDIS_URL)
        self.session = None
        self.cache_ttl = 900  # 15 minutes

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        await self.redis_client.close()

    async def get_stock_data(self, symbol: str) -> Optional[StockData]:
        """Get real-time stock data with caching"""
        cache_key = f"stock:{symbol}"
        
        # Try cache first
        cached = await self.redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return StockData(**data)

        # Fetch from Yahoo Finance
        try:
            data = await self._fetch_yahoo_data(symbol)
            if data:
                # Cache for 15 minutes
                await self.redis_client.setex(
                    cache_key, 
                    self.cache_ttl, 
                    json.dumps(data.__dict__)
                )
                return data
        except Exception as e:
            logger.error(f"Error fetching stock data for {symbol}: {e}")
            return None

    async def get_financial_statements(self, symbol: str) -> List[FinancialStatement]:
        """Get financial statements from SEC EDGAR"""
        cache_key = f"financials:{symbol}"
        
        # Try cache first
        cached = await self.redis_client.get(cache_key)
        if cached:
            data = json.loads(cached)
            return [FinancialStatement(**item) for item in data]

        # Fetch from SEC EDGAR
        try:
            statements = await self._fetch_sec_data(symbol)
            if statements:
                # Cache for 15 minutes
                data = [stmt.__dict__ for stmt in statements]
                await self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(data)
                )
                return statements
        except Exception as e:
            logger.error(f"Error fetching financials for {symbol}: {e}")
            return []

    async def get_market_metrics(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market metrics"""
        cache_key = f"metrics:{symbol}"
        
        cached = await self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)

        try:
            metrics = await self._fetch_market_metrics(symbol)
            if metrics:
                await self.redis_client.setex(
                    cache_key,
                    self.cache_ttl,
                    json.dumps(metrics)
                )
                return metrics
        except Exception as e:
            logger.error(f"Error fetching metrics for {symbol}: {e}")
            return {}

    async def _fetch_yahoo_data(self, symbol: str) -> Optional[StockData]:
        """Fetch data from Yahoo Finance API"""
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
        
        async with self.session.get(url) as response:
            if response.status != 200:
                return None
                
            data = await response.json()
            result = data.get('chart', {}).get('result', [])
            
            if not result:
                return None
                
            quote = result[0]
            meta = quote.get('meta', {})
            
            return StockData(
                symbol=symbol,
                price=meta.get('regularMarketPrice', 0.0),
                change=meta.get('regularMarketPrice', 0.0) - meta.get('previousClose', 0.0),
                change_percent=((meta.get('regularMarketPrice', 0.0) - meta.get('previousClose', 1.0)) / meta.get('previousClose', 1.0)) * 100,
                volume=meta.get('regularMarketVolume', 0),
                market_cap=meta.get('marketCap'),
                pe_ratio=meta.get('trailingPE'),
                dividend_yield=meta.get('dividendYield')
            )

    async def _fetch_sec_data(self, symbol: str) -> List[FinancialStatement]:
        """Fetch financial statements from SEC EDGAR"""
        # Get CIK first
        cik_url = f"https://www.sec.gov/files/company_tickers.json"
        headers = {"User-Agent": settings.SEC_EDGAR_USER_AGENT}
        
        async with self.session.get(cik_url, headers=headers) as response:
            if response.status != 200:
                return []
                
            companies = await response.json()
            cik = None
            
            for company in companies.values():
                if company.get('ticker', '').upper() == symbol.upper():
                    cik = str(company['cik_str']).zfill(10)
                    break
                    
            if not cik:
                return []

        # Get company facts
        facts_url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
        
        async with self.session.get(facts_url, headers=headers) as response:
            if response.status != 200:
                return []
                
            facts = await response.json()
            statements = []
            
            # Extract key financial metrics
            us_gaap = facts.get('facts', {}).get('us-gaap', {})
            
            revenues = us_gaap.get('Revenues', {}).get('units', {}).get('USD', [])
            net_incomes = us_gaap.get('NetIncomeLoss', {}).get('units', {}).get('USD', [])
            assets = us_gaap.get('Assets', {}).get('units', {}).get('USD', [])
            debts = us_gaap.get('LongTermDebt', {}).get('units', {}).get('USD', [])
            cash = us_gaap.get('CashAndCashEquivalentsAtCarryingValue', {}).get('units', {}).get('USD', [])
            
            # Get last 4 quarters
            for i, rev in enumerate(revenues[-4:]):
                statements.append(FinancialStatement(
                    symbol=symbol,
                    period=rev.get('fp', 'Q'),
                    revenue=rev.get('val', 0),
                    net_income=net_incomes[i].get('val', 0) if i < len(net_incomes) else 0,
                    total_assets=assets[i].get('val', 0) if i < len(assets) else 0,
                    total_debt=debts[i].get('val', 0) if i < len(debts) else 0,
                    cash=cash[i].get('val', 0) if i < len(cash) else 0,
                    filing_date=rev.get('filed', '')
                ))
                
            return statements

    async def _fetch_market_metrics(self, symbol: str) -> Dict[str, Any]:
        """Fetch comprehensive market metrics"""
        url = f"https://query2.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
        params = {
            'modules': 'summaryDetail,financialData,defaultKeyStatistics'
        }
        
        async with self.session.get(url, params=params) as response:
            if response.status != 200:
                return {}
                
            data = await response.json()
            result = data.get('quoteSummary', {}).get('result', [])
            
            if not result:
                return {}
                
            summary = result[0]
            
            return {
                'beta': summary.get('summaryDetail', {}).get('beta', {}).get('raw'),
                'trailing_pe': summary.get('summaryDetail', {}).get('trailingPE', {}).get('raw'),
                'forward_pe': summary.get('summaryDetail', {}).get('forwardPE', {}).get('raw'),
                'price_to_book': summary.get('defaultKeyStatistics', {}).get('priceToBook', {}).get('raw'),
                'debt_to_equity': summary.get('financialData', {}).get('debtToEquity', {}).get('raw'),
                'return_on_equity': summary.get('financialData', {}).get('returnOnEquity', {}).get('raw'),
                'profit_margins': summary.get('financialData', {}).get('profitMargins', {}).get('raw'),
                'revenue_growth': summary.get('financialData', {}).get('revenueGrowth', {}).get('raw'),
                'earnings_growth': summary.get('financialData', {}).get('earningsGrowth', {}).get('raw'),
                '52_week_high': summary.get('summaryDetail', {}).get('fiftyTwoWeekHigh', {}).get('raw'),
                '52_week_low': summary.get('summaryDetail', {}).get('fiftyTwoWeekLow', {}).get('raw'),
                'avg_volume': summary.get('summaryDetail', {}).get('averageVolume', {}).get('raw'),
                'market_cap': summary.get('summaryDetail', {}).get('marketCap', {}).get('raw')
            }

# Singleton instance
financial_service = FinancialDataService()