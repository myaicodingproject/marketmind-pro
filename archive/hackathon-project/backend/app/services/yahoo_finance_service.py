"""
Yahoo Finance Service - Real-time stock data and financial statements
"""

import yfinance as yf
import pandas as pd
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

class YahooFinanceService:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    async def get_complete_stock_data(self, ticker: str) -> Dict[str, Any]:
        """Get comprehensive stock data for all report sections"""
        
        def _fetch_data():
            stock = yf.Ticker(ticker)
            
            # Get all data types needed
            info = stock.info
            hist = stock.history(period="2y")  # 2 years of price data
            
            # Financial statements
            financials = {
                'income_statement': stock.financials,
                'balance_sheet': stock.balance_sheet,
                'cash_flow': stock.cashflow,
                'quarterly_financials': stock.quarterly_financials
            }
            
            # Key metrics for analysis
            key_metrics = {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_book': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'roe': info.get('returnOnEquity'),
                'roa': info.get('returnOnAssets'),
                'profit_margin': info.get('profitMargins'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth')
            }
            
            return {
                'info': info,
                'price_history': hist,
                'financials': financials,
                'key_metrics': key_metrics,
                'market_data': self._calculate_market_metrics(hist, info)
            }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _fetch_data)
    
    async def get_key_metrics(self, ticker: str) -> Dict[str, Any]:
        """Get key financial metrics for peer comparison"""
        
        def _fetch_metrics():
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'price_to_book': info.get('priceToBook'),
                'debt_to_equity': info.get('debtToEquity'),
                'roe': info.get('returnOnEquity'),
                'profit_margin': info.get('profitMargins'),
                'revenue_growth': info.get('revenueGrowth')
            }
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, _fetch_metrics)
    
    def _calculate_market_metrics(self, price_data: pd.DataFrame, info: Dict) -> Dict[str, Any]:
        """Calculate additional market metrics"""
        if price_data.empty:
            return {}
        
        # Calculate volatility and performance metrics
        returns = price_data['Close'].pct_change().dropna()
        
        return {
            'volatility_30d': returns.tail(30).std() * (252 ** 0.5),  # Annualized
            'volatility_90d': returns.tail(90).std() * (252 ** 0.5),
            'beta': self._calculate_beta(price_data),
            'ytd_return': self._calculate_ytd_return(price_data),
            'avg_volume': price_data['Volume'].tail(30).mean(),
            'price_52w_high': price_data['High'].tail(252).max(),
            'price_52w_low': price_data['Low'].tail(252).min()
        }
    
    def _calculate_beta(self, price_data: pd.DataFrame) -> Optional[float]:
        """Calculate stock beta vs market (simplified)"""
        try:
            # Get SPY data for beta calculation
            spy = yf.Ticker("SPY")
            spy_hist = spy.history(period="1y")
            
            # Align dates and calculate returns
            stock_returns = price_data['Close'].pct_change().dropna()
            spy_returns = spy_hist['Close'].pct_change().dropna()
            
            # Find common dates
            common_dates = stock_returns.index.intersection(spy_returns.index)
            if len(common_dates) < 50:  # Need sufficient data
                return None
            
            stock_aligned = stock_returns.loc[common_dates]
            spy_aligned = spy_returns.loc[common_dates]
            
            # Calculate beta
            covariance = stock_aligned.cov(spy_aligned)
            spy_variance = spy_aligned.var()
            
            return covariance / spy_variance if spy_variance != 0 else None
        except:
            return None
    
    def _calculate_ytd_return(self, price_data: pd.DataFrame) -> Optional[float]:
        """Calculate year-to-date return"""
        try:
            current_year = datetime.now().year
            ytd_data = price_data[price_data.index.year == current_year]
            
            if len(ytd_data) < 2:
                return None
            
            start_price = ytd_data['Close'].iloc[0]
            current_price = ytd_data['Close'].iloc[-1]
            
            return (current_price - start_price) / start_price
        except:
            return None