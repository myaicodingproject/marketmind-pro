"""
Financial Data Service - Real-time integration with Alpha Vantage, Yahoo Finance, and SEC EDGAR
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import httpx
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from alpha_vantage.fundamentaldata import FundamentalData
from sec_edgar_downloader import Downloader
import pandas as pd
from pydantic import BaseModel
import os
from ..core.config import settings

logger = logging.getLogger(__name__)

class StockPrice(BaseModel):
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    market_cap: Optional[float] = None
    timestamp: datetime

class FinancialMetrics(BaseModel):
    symbol: str
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    eps: Optional[float] = None
    pe_ratio: Optional[float] = None
    pb_ratio: Optional[float] = None
    debt_to_equity: Optional[float] = None
    roe: Optional[float] = None
    roa: Optional[float] = None
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    profit_margin: Optional[float] = None

class CompanyInfo(BaseModel):
    symbol: str
    name: str
    sector: str
    industry: str
    description: str
    employees: Optional[int] = None
    headquarters: Optional[str] = None
    website: Optional[str] = None
    ceo: Optional[str] = None

class FinancialDataService:
    def __init__(self):
        self.alpha_vantage_key = settings.ALPHA_VANTAGE_API_KEY
        self.sec_user_agent = settings.SEC_EDGAR_USER_AGENT
        self.ts = TimeSeries(key=self.alpha_vantage_key, output_format='pandas')
        self.fd = FundamentalData(key=self.alpha_vantage_key, output_format='pandas')
        self.sec_downloader = Downloader("MarketMind", "info@marketmind.com")
        
    async def get_real_time_price(self, symbol: str) -> StockPrice:
        """Get real-time stock price from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1d")
            
            if hist.empty:
                raise ValueError(f"No data found for symbol {symbol}")
                
            current_price = hist['Close'].iloc[-1]
            previous_close = info.get('previousClose', current_price)
            change = current_price - previous_close
            change_percent = (change / previous_close) * 100 if previous_close else 0
            
            return StockPrice(
                symbol=symbol,
                price=float(current_price),
                change=float(change),
                change_percent=float(change_percent),
                volume=int(hist['Volume'].iloc[-1]),
                market_cap=info.get('marketCap'),
                timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error fetching real-time price for {symbol}: {e}")
            raise

    async def get_historical_prices(self, symbol: str, period: str = "1y") -> pd.DataFrame:
        """Get historical price data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            return hist
        except Exception as e:
            logger.error(f"Error fetching historical data for {symbol}: {e}")
            raise

    async def get_financial_metrics(self, symbol: str) -> FinancialMetrics:
        """Get comprehensive financial metrics from multiple sources"""
        try:
            # Yahoo Finance data
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Alpha Vantage fundamental data
            try:
                overview, _ = self.fd.get_company_overview(symbol)
                av_data = overview.iloc[0] if not overview.empty else {}
            except:
                av_data = {}
            
            return FinancialMetrics(
                symbol=symbol,
                revenue=self._safe_float(info.get('totalRevenue') or av_data.get('RevenueTTM')),
                net_income=self._safe_float(info.get('netIncomeToCommon') or av_data.get('NetIncomeTTM')),
                eps=self._safe_float(info.get('trailingEps') or av_data.get('EPS')),
                pe_ratio=self._safe_float(info.get('trailingPE') or av_data.get('PERatio')),
                pb_ratio=self._safe_float(info.get('priceToBook') or av_data.get('PriceToBookRatio')),
                debt_to_equity=self._safe_float(info.get('debtToEquity')),
                roe=self._safe_float(info.get('returnOnEquity') or av_data.get('ReturnOnEquityTTM')),
                roa=self._safe_float(info.get('returnOnAssets') or av_data.get('ReturnOnAssetsTTM')),
                gross_margin=self._safe_float(info.get('grossMargins') or av_data.get('GrossProfitTTM')),
                operating_margin=self._safe_float(info.get('operatingMargins')),
                profit_margin=self._safe_float(info.get('profitMargins'))
            )
        except Exception as e:
            logger.error(f"Error fetching financial metrics for {symbol}: {e}")
            raise

    async def get_company_info(self, symbol: str) -> CompanyInfo:
        """Get comprehensive company information"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return CompanyInfo(
                symbol=symbol,
                name=info.get('longName', info.get('shortName', symbol)),
                sector=info.get('sector', 'Unknown'),
                industry=info.get('industry', 'Unknown'),
                description=info.get('longBusinessSummary', ''),
                employees=info.get('fullTimeEmployees'),
                headquarters=f"{info.get('city', '')}, {info.get('state', '')} {info.get('country', '')}".strip(),
                website=info.get('website'),
                ceo=info.get('companyOfficers', [{}])[0].get('name') if info.get('companyOfficers') else None
            )
        except Exception as e:
            logger.error(f"Error fetching company info for {symbol}: {e}")
            raise

    async def get_sec_filings(self, symbol: str, filing_type: str = "10-K", limit: int = 5) -> List[Dict]:
        """Download and parse SEC filings"""
        try:
            # Download filings
            self.sec_downloader.get(filing_type, symbol, limit=limit)
            
            # Parse filing metadata
            filings = []
            filing_dir = f"sec-edgar-filings/{symbol}/{filing_type}"
            
            if os.path.exists(filing_dir):
                for filing in os.listdir(filing_dir)[:limit]:
                    filing_path = os.path.join(filing_dir, filing)
                    if os.path.isdir(filing_path):
                        # Extract filing metadata
                        filings.append({
                            "filing_type": filing_type,
                            "symbol": symbol,
                            "filing_date": filing,
                            "path": filing_path
                        })
            
            return filings
        except Exception as e:
            logger.error(f"Error fetching SEC filings for {symbol}: {e}")
            return []

    async def get_market_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive market data combining all sources"""
        try:
            # Run all data fetching concurrently
            price_task = self.get_real_time_price(symbol)
            metrics_task = self.get_financial_metrics(symbol)
            info_task = self.get_company_info(symbol)
            
            price, metrics, info = await asyncio.gather(
                price_task, metrics_task, info_task, return_exceptions=True
            )
            
            # Handle exceptions
            if isinstance(price, Exception):
                logger.error(f"Price fetch failed: {price}")
                price = None
            if isinstance(metrics, Exception):
                logger.error(f"Metrics fetch failed: {metrics}")
                metrics = None
            if isinstance(info, Exception):
                logger.error(f"Info fetch failed: {info}")
                info = None
            
            return {
                "symbol": symbol,
                "price_data": price.dict() if price else None,
                "financial_metrics": metrics.dict() if metrics else None,
                "company_info": info.dict() if info else None,
                "last_updated": datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            raise

    async def validate_symbol(self, symbol: str) -> bool:
        """Validate if a stock symbol exists"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            return 'symbol' in info or 'shortName' in info
        except:
            return False

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float"""
        if value is None or value == 'None' or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

    async def get_peer_comparison(self, symbol: str) -> List[Dict]:
        """Get peer comparison data"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            sector = info.get('sector')
            
            if not sector:
                return []
            
            # This is a simplified peer comparison
            # In production, you'd use a more sophisticated method
            peers = []
            
            # Get some basic peer data (this would be enhanced with actual peer discovery)
            return peers
        except Exception as e:
            logger.error(f"Error fetching peer comparison for {symbol}: {e}")
            return []

# Global instance
financial_data_service = FinancialDataService()