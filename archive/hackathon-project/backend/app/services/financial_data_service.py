"""
Financial Data Service - Comprehensive data collection for MarketMind Pro
Integrates Yahoo Finance, SEC EDGAR, and web research for all 8 report sections
"""

import asyncio
import yfinance as yf
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import pandas as pd
from dataclasses import dataclass
from .yahoo_finance_service import YahooFinanceService
from .sec_edgar_service import SECEdgarService
from .news_sentiment_service import NewsSentimentService
from .analyst_ratings_service import AnalystRatingsService

@dataclass
class ComprehensiveFinancialData:
    ticker: str
    company_info: Dict[str, Any]
    stock_data: Dict[str, Any]
    financial_statements: Dict[str, pd.DataFrame]
    sec_filings: Dict[str, Any]
    analyst_ratings: Dict[str, Any]
    news_sentiment: Dict[str, Any]
    market_data: Dict[str, Any]
    peer_comparison: Dict[str, Any]
    timestamp: datetime

class FinancialDataService:
    def __init__(self):
        self.yahoo_service = YahooFinanceService()
        self.sec_service = SECEdgarService()
        self.news_service = NewsSentimentService()
        self.analyst_service = AnalystRatingsService()
    
    async def get_comprehensive_data(self, ticker: str) -> ComprehensiveFinancialData:
        """Collect all financial data needed for 8 report sections"""
        
        # Execute all data collection concurrently
        results = await asyncio.gather(
            self.yahoo_service.get_complete_stock_data(ticker),
            self.sec_service.get_latest_filings(ticker),
            self.news_service.get_sentiment_analysis(ticker),
            self.analyst_service.get_ratings_consensus(ticker),
            self._get_peer_comparison_data(ticker),
            return_exceptions=True
        )
        
        stock_data, sec_data, news_data, analyst_data, peer_data = results
        
        return ComprehensiveFinancialData(
            ticker=ticker,
            company_info=stock_data.get('info', {}),
            stock_data=stock_data,
            financial_statements=stock_data.get('financials', {}),
            sec_filings=sec_data,
            analyst_ratings=analyst_data,
            news_sentiment=news_data,
            market_data=stock_data.get('market_data', {}),
            peer_comparison=peer_data,
            timestamp=datetime.now()
        )
    
    async def _get_peer_comparison_data(self, ticker: str) -> Dict[str, Any]:
        """Get peer comparison data for valuation analysis"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            sector = info.get('sector', '')
            industry = info.get('industry', '')
            
            # Get sector peers (simplified - would use more sophisticated peer selection)
            peers = await self._find_sector_peers(sector, industry)
            peer_metrics = {}
            
            for peer in peers[:5]:  # Top 5 peers
                peer_data = await self.yahoo_service.get_key_metrics(peer)
                peer_metrics[peer] = peer_data
            
            return {
                'sector': sector,
                'industry': industry,
                'peers': peer_metrics
            }
        except Exception as e:
            return {'error': str(e)}
    
    async def _find_sector_peers(self, sector: str, industry: str) -> List[str]:
        """Find peer companies in same sector/industry"""
        # Simplified peer mapping - would use more sophisticated matching
        sector_peers = {
            'Technology': ['AAPL', 'MSFT', 'GOOGL', 'META', 'NVDA'],
            'Healthcare': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK'],
            'Financial Services': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
            'Consumer Cyclical': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE']
        }
        return sector_peers.get(sector, ['SPY'])  # Default to SPY if sector not found