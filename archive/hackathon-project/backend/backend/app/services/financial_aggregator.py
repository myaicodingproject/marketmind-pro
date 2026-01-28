"""
Financial Data Aggregator - Unified interface for all financial data sources
"""
import asyncio
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import pandas as pd
from .alpha_vantage_service import alpha_vantage_service
from .yahoo_finance_service import yahoo_finance_service
from .sec_edgar_service import sec_edgar_service
from .financial_data_service import financial_data_service

logger = logging.getLogger(__name__)

class FinancialDataAggregator:
    def __init__(self):
        self.alpha_vantage = alpha_vantage_service
        self.yahoo_finance = yahoo_finance_service
        self.sec_edgar = sec_edgar_service
        self.financial_data = financial_data_service
        
    async def get_comprehensive_stock_data(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock data from all sources"""
        try:
            logger.info(f"Fetching comprehensive data for {symbol}")
            
            # Validate symbol first
            is_valid = await self.financial_data.validate_symbol(symbol)
            if not is_valid:
                raise ValueError(f"Invalid stock symbol: {symbol}")
            
            # Fetch data from all sources concurrently
            tasks = {
                'yahoo_summary': self.yahoo_finance.get_market_data_summary(symbol),
                'alpha_vantage_overview': self._safe_execute(self.alpha_vantage.get_company_overview, symbol),
                'alpha_vantage_ratios': self._safe_execute(self.alpha_vantage.get_financial_ratios, symbol),
                'sec_recent_filings': self._safe_execute(self.sec_edgar.get_recent_filings, symbol),
                'real_time_price': self._safe_execute(self.financial_data.get_real_time_price, symbol),
                'financial_statements': self._safe_execute(self.yahoo_finance.get_financial_statements, symbol)
            }
            
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            data = dict(zip(tasks.keys(), results))
            
            # Process and combine data
            comprehensive_data = {
                'symbol': symbol,
                'last_updated': datetime.now().isoformat(),
                'data_sources': {
                    'yahoo_finance': not isinstance(data['yahoo_summary'], Exception),
                    'alpha_vantage': not isinstance(data['alpha_vantage_overview'], Exception),
                    'sec_edgar': not isinstance(data['sec_recent_filings'], Exception)
                },
                'real_time_data': self._extract_real_time_data(data),
                'company_profile': self._extract_company_profile(data),
                'financial_metrics': self._extract_financial_metrics(data),
                'market_data': self._extract_market_data(data),
                'fundamental_analysis': self._extract_fundamental_analysis(data),
                'regulatory_data': self._extract_regulatory_data(data),
                'risk_metrics': self._extract_risk_metrics(data)
            }
            
            return comprehensive_data
            
        except Exception as e:
            logger.error(f"Error fetching comprehensive data for {symbol}: {e}")
            raise

    async def get_real_time_market_data(self, symbols: List[str]) -> Dict[str, Any]:
        """Get real-time market data for multiple symbols"""
        try:
            tasks = [self.financial_data.get_real_time_price(symbol) for symbol in symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            market_data = {
                'symbols': symbols,
                'timestamp': datetime.now().isoformat(),
                'data': {}
            }
            
            for symbol, result in zip(symbols, results):
                if isinstance(result, Exception):
                    market_data['data'][symbol] = {'error': str(result)}
                else:
                    market_data['data'][symbol] = result.dict()
            
            return market_data
            
        except Exception as e:
            logger.error(f"Error fetching real-time market data: {e}")
            raise

    async def get_financial_analysis(self, symbol: str) -> Dict[str, Any]:
        """Get detailed financial analysis combining multiple sources"""
        try:
            # Fetch detailed financial data
            tasks = {
                'yahoo_financials': self.yahoo_finance.get_financial_statements(symbol),
                'yahoo_earnings': self.yahoo_finance.get_earnings_data(symbol),
                'alpha_income': self._safe_execute(self.alpha_vantage.get_income_statement, symbol),
                'alpha_balance': self._safe_execute(self.alpha_vantage.get_balance_sheet, symbol),
                'alpha_cashflow': self._safe_execute(self.alpha_vantage.get_cash_flow, symbol),
                'sec_10k': self._safe_execute(self.sec_edgar.parse_10k_filing, symbol)
            }
            
            results = await asyncio.gather(*tasks.values(), return_exceptions=True)
            data = dict(zip(tasks.keys(), results))
            
            analysis = {
                'symbol': symbol,
                'analysis_date': datetime.now().isoformat(),
                'financial_statements': self._consolidate_financial_statements(data),
                'earnings_analysis': self._analyze_earnings_trends(data),
                'balance_sheet_analysis': self._analyze_balance_sheet(data),
                'cash_flow_analysis': self._analyze_cash_flow(data),
                'regulatory_insights': self._extract_regulatory_insights(data),
                'financial_health_score': self._calculate_financial_health_score(data)
            }
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error performing financial analysis for {symbol}: {e}")
            raise

    async def get_market_comparison(self, symbol: str, peer_symbols: List[str] = None) -> Dict[str, Any]:
        """Get market comparison data"""
        try:
            if not peer_symbols:
                # Auto-discover peers (simplified - in production use sector/industry data)
                peer_symbols = []
            
            all_symbols = [symbol] + peer_symbols
            
            # Fetch comparison data
            tasks = [self.yahoo_finance.get_ticker_info(s) for s in all_symbols]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            comparison = {
                'primary_symbol': symbol,
                'peer_symbols': peer_symbols,
                'comparison_date': datetime.now().isoformat(),
                'metrics_comparison': {},
                'relative_performance': {}
            }
            
            # Process comparison data
            valid_data = []
            for sym, result in zip(all_symbols, results):
                if not isinstance(result, Exception):
                    valid_data.append((sym, result))
            
            if valid_data:
                comparison['metrics_comparison'] = self._compare_financial_metrics(valid_data)
                comparison['relative_performance'] = self._calculate_relative_performance(valid_data)
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error performing market comparison for {symbol}: {e}")
            raise

    async def _safe_execute(self, func, *args, **kwargs):
        """Safely execute a function and return None on error"""
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Safe execution failed for {func.__name__}: {e}")
            return None

    def _extract_real_time_data(self, data: Dict) -> Dict:
        """Extract real-time market data"""
        real_time = {}
        
        if 'real_time_price' in data and not isinstance(data['real_time_price'], Exception):
            price_data = data['real_time_price']
            real_time = {
                'current_price': price_data.price,
                'change': price_data.change,
                'change_percent': price_data.change_percent,
                'volume': price_data.volume,
                'market_cap': price_data.market_cap,
                'timestamp': price_data.timestamp.isoformat()
            }
        
        return real_time

    def _extract_company_profile(self, data: Dict) -> Dict:
        """Extract company profile information"""
        profile = {}
        
        # From Yahoo Finance
        if 'yahoo_summary' in data and not isinstance(data['yahoo_summary'], Exception):
            yahoo_data = data['yahoo_summary'].get('basic_info', {})
            profile.update({
                'name': yahoo_data.get('name'),
                'sector': yahoo_data.get('sector'),
                'industry': yahoo_data.get('industry'),
                'employees': yahoo_data.get('full_time_employees'),
                'website': yahoo_data.get('website'),
                'description': yahoo_data.get('long_business_summary')
            })
        
        # From Alpha Vantage
        if 'alpha_vantage_overview' in data and not isinstance(data['alpha_vantage_overview'], Exception):
            av_data = data['alpha_vantage_overview']
            profile.update({
                'exchange': av_data.get('Exchange'),
                'currency': av_data.get('Currency'),
                'country': av_data.get('Country'),
                'fiscal_year_end': av_data.get('FiscalYearEnd')
            })
        
        return profile

    def _extract_financial_metrics(self, data: Dict) -> Dict:
        """Extract key financial metrics"""
        metrics = {}
        
        # From Yahoo Finance
        if 'yahoo_summary' in data and not isinstance(data['yahoo_summary'], Exception):
            yahoo_data = data['yahoo_summary'].get('basic_info', {})
            metrics.update({
                'market_cap': yahoo_data.get('market_cap'),
                'enterprise_value': yahoo_data.get('enterprise_value'),
                'trailing_pe': yahoo_data.get('trailing_pe'),
                'forward_pe': yahoo_data.get('forward_pe'),
                'price_to_book': yahoo_data.get('price_to_book'),
                'price_to_sales': yahoo_data.get('price_to_sales'),
                'profit_margins': yahoo_data.get('profit_margins'),
                'operating_margins': yahoo_data.get('operating_margins'),
                'return_on_assets': yahoo_data.get('return_on_assets'),
                'return_on_equity': yahoo_data.get('return_on_equity'),
                'debt_to_equity': yahoo_data.get('debt_to_equity'),
                'current_ratio': yahoo_data.get('current_ratio'),
                'beta': yahoo_data.get('beta')
            })
        
        # From Alpha Vantage ratios
        if 'alpha_vantage_ratios' in data and not isinstance(data['alpha_vantage_ratios'], Exception):
            av_ratios = data['alpha_vantage_ratios'].get('ratios', {})
            metrics.update(av_ratios)
        
        return metrics

    def _extract_market_data(self, data: Dict) -> Dict:
        """Extract market performance data"""
        market_data = {}
        
        if 'yahoo_summary' in data and not isinstance(data['yahoo_summary'], Exception):
            yahoo_data = data['yahoo_summary']
            market_data.update({
                'price_performance': yahoo_data.get('price_performance', {}),
                'volatility_metrics': yahoo_data.get('volatility_metrics', {}),
                'volume_data': yahoo_data.get('volume_data', {})
            })
        
        return market_data

    def _extract_fundamental_analysis(self, data: Dict) -> Dict:
        """Extract fundamental analysis data"""
        fundamental = {}
        
        if 'financial_statements' in data and not isinstance(data['financial_statements'], Exception):
            statements = data['financial_statements']
            fundamental['financial_statements'] = statements
        
        if 'yahoo_summary' in data and not isinstance(data['yahoo_summary'], Exception):
            earnings = data['yahoo_summary'].get('earnings_summary', {})
            fundamental['earnings_data'] = earnings
        
        return fundamental

    def _extract_regulatory_data(self, data: Dict) -> Dict:
        """Extract regulatory and SEC filing data"""
        regulatory = {}
        
        if 'sec_recent_filings' in data and not isinstance(data['sec_recent_filings'], Exception):
            regulatory['recent_filings'] = data['sec_recent_filings']
        
        return regulatory

    def _extract_risk_metrics(self, data: Dict) -> Dict:
        """Extract risk assessment metrics"""
        risk_metrics = {}
        
        if 'yahoo_summary' in data and not isinstance(data['yahoo_summary'], Exception):
            volatility = data['yahoo_summary'].get('volatility_metrics', {})
            risk_metrics.update({
                'volatility': volatility.get('annualized_volatility'),
                'beta': volatility.get('beta'),
                'max_drawdown': volatility.get('max_drawdown'),
                'var_95': volatility.get('var_95'),
                'sharpe_ratio': volatility.get('sharpe_ratio')
            })
        
        return risk_metrics

    def _consolidate_financial_statements(self, data: Dict) -> Dict:
        """Consolidate financial statements from multiple sources"""
        consolidated = {
            'income_statement': {},
            'balance_sheet': {},
            'cash_flow': {}
        }
        
        # Add Yahoo Finance data
        if 'yahoo_financials' in data and not isinstance(data['yahoo_financials'], Exception):
            yahoo_statements = data['yahoo_financials']
            consolidated['income_statement']['yahoo'] = yahoo_statements.get('income_statement', {})
            consolidated['balance_sheet']['yahoo'] = yahoo_statements.get('balance_sheet', {})
            consolidated['cash_flow']['yahoo'] = yahoo_statements.get('cash_flow', {})
        
        # Add Alpha Vantage data
        for statement_type in ['income', 'balance', 'cashflow']:
            key = f'alpha_{statement_type}'
            if key in data and not isinstance(data[key], Exception):
                target_key = statement_type if statement_type != 'cashflow' else 'cash_flow'
                if statement_type == 'income':
                    target_key = 'income_statement'
                elif statement_type == 'balance':
                    target_key = 'balance_sheet'
                consolidated[target_key]['alpha_vantage'] = data[key]
        
        return consolidated

    def _analyze_earnings_trends(self, data: Dict) -> Dict:
        """Analyze earnings trends"""
        analysis = {}
        
        if 'yahoo_earnings' in data and not isinstance(data['yahoo_earnings'], Exception):
            earnings_data = data['yahoo_earnings']
            # Perform earnings trend analysis
            analysis['earnings_growth'] = self._calculate_earnings_growth(earnings_data)
            analysis['earnings_consistency'] = self._calculate_earnings_consistency(earnings_data)
        
        return analysis

    def _analyze_balance_sheet(self, data: Dict) -> Dict:
        """Analyze balance sheet strength"""
        analysis = {}
        
        # Analyze debt levels, liquidity, asset quality
        # This would be implemented with detailed balance sheet analysis
        
        return analysis

    def _analyze_cash_flow(self, data: Dict) -> Dict:
        """Analyze cash flow patterns"""
        analysis = {}
        
        # Analyze operating cash flow, free cash flow trends
        # This would be implemented with detailed cash flow analysis
        
        return analysis

    def _extract_regulatory_insights(self, data: Dict) -> Dict:
        """Extract insights from regulatory filings"""
        insights = {}
        
        if 'sec_10k' in data and not isinstance(data['sec_10k'], Exception):
            sec_data = data['sec_10k']
            insights.update({
                'business_overview': sec_data.get('business_overview'),
                'risk_factors': sec_data.get('risk_factors'),
                'management_discussion': sec_data.get('management_discussion')
            })
        
        return insights

    def _calculate_financial_health_score(self, data: Dict) -> float:
        """Calculate overall financial health score (0-100)"""
        score = 50.0  # Base score
        
        # This would implement a sophisticated scoring algorithm
        # based on multiple financial metrics
        
        return score

    def _compare_financial_metrics(self, company_data: List) -> Dict:
        """Compare financial metrics across companies"""
        comparison = {}
        
        # Extract key metrics for comparison
        metrics_to_compare = [
            'trailing_pe', 'price_to_book', 'profit_margins',
            'return_on_equity', 'debt_to_equity', 'market_cap'
        ]
        
        for metric in metrics_to_compare:
            comparison[metric] = {}
            for symbol, data in company_data:
                comparison[metric][symbol] = data.get(metric)
        
        return comparison

    def _calculate_relative_performance(self, company_data: List) -> Dict:
        """Calculate relative performance metrics"""
        performance = {}
        
        # This would implement relative performance calculations
        # comparing returns, volatility, and other performance metrics
        
        return performance

    def _calculate_earnings_growth(self, earnings_data: Dict) -> float:
        """Calculate earnings growth rate"""
        # Implement earnings growth calculation
        return 0.0

    def _calculate_earnings_consistency(self, earnings_data: Dict) -> float:
        """Calculate earnings consistency score"""
        # Implement earnings consistency calculation
        return 0.0

    async def close_all_sessions(self):
        """Close all service sessions"""
        await asyncio.gather(
            self.alpha_vantage.close(),
            self.sec_edgar.close(),
            return_exceptions=True
        )

# Global instance
financial_aggregator = FinancialDataAggregator()