"""
Data Pipeline Integration for Kiro Context Preparation
Integrates with existing data services to prepare comprehensive context for Kiro prompts
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json

from app.services.error_handler import with_retry, RetryConfig, GracefulDegradation

logger = logging.getLogger(__name__)

class DataPipelineIntegrator:
    """
    Integrates with data pipeline to prepare comprehensive context for Kiro prompts
    Handles data fetching, validation, and formatting for optimal prompt execution
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
    
    async def prepare_comprehensive_context(
        self, 
        ticker: str, 
        include_sections: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Prepare comprehensive context data for all report sections
        
        Args:
            ticker: Stock ticker symbol
            include_sections: Specific sections to prepare data for
            
        Returns:
            Comprehensive context dictionary
        """
        
        try:
            logger.info(f"Preparing comprehensive context for {ticker}")
            
            # Check cache first
            cache_key = f"context_{ticker}"
            if self._is_cached_valid(cache_key):
                logger.info(f"Using cached context for {ticker}")
                return self.cache[cache_key]['data']
            
            # Gather all required data concurrently
            context_data = await self._gather_all_data(ticker)
            
            # Validate and enrich data
            validated_context = await self._validate_and_enrich_context(ticker, context_data)
            
            # Cache the result
            self.cache[cache_key] = {
                'data': validated_context,
                'timestamp': datetime.now(),
                'ticker': ticker
            }
            
            logger.info(f"Successfully prepared context for {ticker}")
            return validated_context
            
        except Exception as e:
            logger.error(f"Failed to prepare context for {ticker}: {str(e)}")
            
            # Return fallback context
            return self._get_fallback_context(ticker)
    
    @with_retry(RetryConfig(max_attempts=3, base_delay=2.0))
    async def _gather_all_data(self, ticker: str) -> Dict[str, Any]:
        """Gather all required data from various sources"""
        
        # Define data gathering tasks
        tasks = {
            'company_info': self._fetch_company_info(ticker),
            'financial_data': self._fetch_financial_data(ticker),
            'market_data': self._fetch_market_data(ticker),
            'news_data': self._fetch_news_data(ticker),
            'peer_data': self._fetch_peer_data(ticker),
            'analyst_data': self._fetch_analyst_data(ticker),
            'sec_filings': self._fetch_sec_filings(ticker),
            'technical_data': self._fetch_technical_data(ticker)
        }
        
        # Execute all tasks concurrently
        results = {}
        for key, task in tasks.items():
            try:
                results[key] = await task
            except Exception as e:
                logger.warning(f"Failed to fetch {key} for {ticker}: {str(e)}")
                results[key] = None
        
        return results
    
    async def _fetch_company_info(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch basic company information"""
        try:
            # Integration with existing data services
            from backend.data.alpha_vantage import AlphaVantageClient
            
            client = AlphaVantageClient()
            company_overview = await client.get_company_overview(ticker)
            
            return {
                'company_name': company_overview.get('Name', f"{ticker} Inc."),
                'sector': company_overview.get('Sector', 'Unknown'),
                'industry': company_overview.get('Industry', 'Unknown'),
                'market_cap': company_overview.get('MarketCapitalization', 'Unknown'),
                'description': company_overview.get('Description', 'Description not available'),
                'exchange': company_overview.get('Exchange', 'Unknown'),
                'currency': company_overview.get('Currency', 'USD'),
                'country': company_overview.get('Country', 'Unknown'),
                'employees': company_overview.get('FullTimeEmployees', 'Unknown'),
                'fiscal_year_end': company_overview.get('FiscalYearEnd', 'Unknown')
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch company info for {ticker}: {str(e)}")
            return None
    
    async def _fetch_financial_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch comprehensive financial data"""
        try:
            from backend.data.alpha_vantage import AlphaVantageClient
            
            client = AlphaVantageClient()
            
            # Fetch multiple financial datasets
            income_statement = await client.get_income_statement(ticker)
            balance_sheet = await client.get_balance_sheet(ticker)
            cash_flow = await client.get_cash_flow(ticker)
            
            return {
                'income_statement': income_statement,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch financial data for {ticker}: {str(e)}")
            return None
    
    async def _fetch_market_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch current market data and price history"""
        try:
            from backend.data.alpha_vantage import AlphaVantageClient
            
            client = AlphaVantageClient()
            
            # Get current quote and historical data
            quote = await client.get_quote(ticker)
            daily_data = await client.get_daily_data(ticker, outputsize='compact')
            
            return {
                'current_quote': quote,
                'daily_data': daily_data,
                'current_price': quote.get('05. price', 'Unknown'),
                'change': quote.get('09. change', 'Unknown'),
                'change_percent': quote.get('10. change percent', 'Unknown'),
                'volume': quote.get('06. volume', 'Unknown'),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch market data for {ticker}: {str(e)}")
            return None
    
    async def _fetch_news_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch recent news and sentiment data"""
        try:
            from backend.data.alpha_vantage import AlphaVantageClient
            
            client = AlphaVantageClient()
            news_data = await client.get_news_sentiment(ticker)
            
            # Process and summarize news
            recent_news = []
            if news_data and 'feed' in news_data:
                for item in news_data['feed'][:10]:  # Top 10 news items
                    recent_news.append({
                        'title': item.get('title', ''),
                        'summary': item.get('summary', ''),
                        'source': item.get('source', ''),
                        'time_published': item.get('time_published', ''),
                        'sentiment': item.get('overall_sentiment_label', 'Neutral')
                    })
            
            return {
                'recent_news': recent_news,
                'news_count': len(recent_news),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch news data for {ticker}: {str(e)}")
            return None
    
    async def _fetch_peer_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch peer comparison data"""
        try:
            # This would integrate with a service that provides peer data
            # For now, return placeholder structure
            
            return {
                'peers': ['PEER1', 'PEER2', 'PEER3'],
                'peer_metrics': {
                    'average_pe': 'Unknown',
                    'average_pb': 'Unknown',
                    'average_roe': 'Unknown',
                    'average_margin': 'Unknown'
                },
                'industry_averages': {
                    'pe_ratio': 'Unknown',
                    'profit_margin': 'Unknown',
                    'debt_to_equity': 'Unknown'
                },
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch peer data for {ticker}: {str(e)}")
            return None
    
    async def _fetch_analyst_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch analyst estimates and recommendations"""
        try:
            # Placeholder for analyst data integration
            return {
                'consensus_rating': 'Unknown',
                'price_target': 'Unknown',
                'eps_estimates': 'Unknown',
                'revenue_estimates': 'Unknown',
                'analyst_count': 'Unknown',
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch analyst data for {ticker}: {str(e)}")
            return None
    
    async def _fetch_sec_filings(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch recent SEC filings"""
        try:
            from backend.data.sec_edgar import SECEdgarClient
            
            client = SECEdgarClient()
            filings = await client.get_recent_filings(ticker, limit=5)
            
            return {
                'recent_filings': filings,
                'filing_count': len(filings) if filings else 0,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch SEC filings for {ticker}: {str(e)}")
            return None
    
    async def _fetch_technical_data(self, ticker: str) -> Optional[Dict[str, Any]]:
        """Fetch technical analysis indicators"""
        try:
            from backend.data.alpha_vantage import AlphaVantageClient
            
            client = AlphaVantageClient()
            
            # Fetch technical indicators
            sma = await client.get_sma(ticker, interval='daily', time_period=20)
            rsi = await client.get_rsi(ticker, interval='daily', time_period=14)
            
            return {
                'sma_20': sma,
                'rsi_14': rsi,
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch technical data for {ticker}: {str(e)}")
            return None
    
    async def _validate_and_enrich_context(
        self, 
        ticker: str, 
        raw_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate and enrich the gathered context data"""
        
        # Start with base context
        context = {
            'ticker': ticker,
            'generation_timestamp': datetime.now().isoformat(),
            'data_sources': []
        }
        
        # Process company information
        if raw_data.get('company_info'):
            company_info = raw_data['company_info']
            context.update({
                'company_name': company_info.get('company_name', f"{ticker} Inc."),
                'sector': company_info.get('sector', 'Unknown'),
                'industry': company_info.get('industry', 'Unknown'),
                'market_cap': company_info.get('market_cap', 'Unknown'),
                'business_description': company_info.get('description', 'Description not available'),
                'exchange': company_info.get('exchange', 'Unknown'),
                'employees': company_info.get('employees', 'Unknown')
            })
            context['data_sources'].append('company_info')
        
        # Process market data
        if raw_data.get('market_data'):
            market_data = raw_data['market_data']
            context.update({
                'current_price': market_data.get('current_price', 'Unknown'),
                'price_change': market_data.get('change', 'Unknown'),
                'price_change_percent': market_data.get('change_percent', 'Unknown'),
                'volume': market_data.get('volume', 'Unknown')
            })
            context['data_sources'].append('market_data')
        
        # Process financial data
        if raw_data.get('financial_data'):
            financial_data = raw_data['financial_data']
            context.update({
                'financial_statements': self._format_financial_statements(financial_data),
                'historical_data': self._format_historical_data(financial_data)
            })
            context['data_sources'].append('financial_data')
        
        # Process news data
        if raw_data.get('news_data'):
            news_data = raw_data['news_data']
            context.update({
                'recent_news': self._format_news_summary(news_data.get('recent_news', [])),
                'news_sentiment': self._analyze_news_sentiment(news_data.get('recent_news', []))
            })
            context['data_sources'].append('news_data')
        
        # Process peer data
        if raw_data.get('peer_data'):
            peer_data = raw_data['peer_data']
            context.update({
                'peer_data': self._format_peer_comparison(peer_data),
                'industry_averages': peer_data.get('industry_averages', {})
            })
            context['data_sources'].append('peer_data')
        
        # Process analyst data
        if raw_data.get('analyst_data'):
            analyst_data = raw_data['analyst_data']
            context.update({
                'analyst_estimates': self._format_analyst_estimates(analyst_data),
                'consensus_rating': analyst_data.get('consensus_rating', 'Unknown'),
                'price_target': analyst_data.get('price_target', 'Unknown')
            })
            context['data_sources'].append('analyst_data')
        
        # Process SEC filings
        if raw_data.get('sec_filings'):
            sec_data = raw_data['sec_filings']
            context.update({
                'recent_filings': self._format_sec_filings(sec_data.get('recent_filings', [])),
                'regulatory_updates': self._extract_regulatory_info(sec_data.get('recent_filings', []))
            })
            context['data_sources'].append('sec_filings')
        
        # Process technical data
        if raw_data.get('technical_data'):
            technical_data = raw_data['technical_data']
            context.update({
                'technical_indicators': self._format_technical_indicators(technical_data),
                'trend_analysis': self._analyze_technical_trends(technical_data)
            })
            context['data_sources'].append('technical_data')
        
        # Add fallback values for missing data
        context = self._add_fallback_values(context)
        
        return context
    
    def _format_financial_statements(self, financial_data: Dict[str, Any]) -> str:
        """Format financial statements for prompt consumption"""
        if not financial_data:
            return "Financial statements not available"
        
        # Create a formatted summary
        summary = "Financial Statements Summary:\n"
        
        if financial_data.get('income_statement'):
            summary += "- Income Statement: Available\n"
        if financial_data.get('balance_sheet'):
            summary += "- Balance Sheet: Available\n"
        if financial_data.get('cash_flow'):
            summary += "- Cash Flow Statement: Available\n"
        
        return summary
    
    def _format_historical_data(self, financial_data: Dict[str, Any]) -> str:
        """Format historical financial data"""
        if not financial_data:
            return "Historical data not available"
        
        return "Historical financial data available for analysis"
    
    def _format_news_summary(self, news_items: List[Dict[str, Any]]) -> str:
        """Format news items into a summary"""
        if not news_items:
            return "No recent news available"
        
        summary = f"Recent News Summary ({len(news_items)} items):\n"
        for i, item in enumerate(news_items[:5], 1):
            summary += f"{i}. {item.get('title', 'No title')}\n"
            if item.get('summary'):
                summary += f"   {item['summary'][:100]}...\n"
        
        return summary
    
    def _analyze_news_sentiment(self, news_items: List[Dict[str, Any]]) -> str:
        """Analyze overall news sentiment"""
        if not news_items:
            return "Neutral"
        
        sentiments = [item.get('sentiment', 'Neutral') for item in news_items]
        positive_count = sentiments.count('Positive')
        negative_count = sentiments.count('Negative')
        
        if positive_count > negative_count:
            return "Positive"
        elif negative_count > positive_count:
            return "Negative"
        else:
            return "Neutral"
    
    def _format_peer_comparison(self, peer_data: Dict[str, Any]) -> str:
        """Format peer comparison data"""
        if not peer_data:
            return "Peer comparison data not available"
        
        peers = peer_data.get('peers', [])
        return f"Peer companies: {', '.join(peers[:5])}" if peers else "No peer data available"
    
    def _format_analyst_estimates(self, analyst_data: Dict[str, Any]) -> str:
        """Format analyst estimates"""
        if not analyst_data:
            return "Analyst estimates not available"
        
        return f"Consensus Rating: {analyst_data.get('consensus_rating', 'Unknown')}"
    
    def _format_sec_filings(self, filings: List[Dict[str, Any]]) -> str:
        """Format SEC filings summary"""
        if not filings:
            return "No recent SEC filings available"
        
        summary = f"Recent SEC Filings ({len(filings)} items):\n"
        for filing in filings[:3]:
            summary += f"- {filing.get('form_type', 'Unknown')}: {filing.get('filing_date', 'Unknown date')}\n"
        
        return summary
    
    def _extract_regulatory_info(self, filings: List[Dict[str, Any]]) -> str:
        """Extract regulatory information from filings"""
        if not filings:
            return "No regulatory updates available"
        
        return "Recent regulatory filings available for review"
    
    def _format_technical_indicators(self, technical_data: Dict[str, Any]) -> str:
        """Format technical indicators"""
        if not technical_data:
            return "Technical indicators not available"
        
        return "Technical analysis indicators available"
    
    def _analyze_technical_trends(self, technical_data: Dict[str, Any]) -> str:
        """Analyze technical trends"""
        if not technical_data:
            return "Trend analysis not available"
        
        return "Technical trend analysis available"
    
    def _add_fallback_values(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Add fallback values for missing required fields"""
        
        required_fields = {
            'company_name': f"{context.get('ticker', 'UNKNOWN')} Inc.",
            'sector': 'Unknown',
            'market_cap': 'Unknown',
            'current_price': 'Unknown',
            'business_description': 'Business description not available',
            'recent_news': 'Recent news not available',
            'financial_statements': 'Financial data not available',
            'historical_data': 'Historical data not available',
            'peer_data': 'Peer data not available',
            'industry_averages': 'Industry averages not available',
            'quarterly_results': 'Quarterly results not available',
            'guidance': 'Guidance not available'
        }
        
        for field, fallback_value in required_fields.items():
            if field not in context or not context[field]:
                context[field] = fallback_value
        
        return context
    
    def _get_fallback_context(self, ticker: str) -> Dict[str, Any]:
        """Generate fallback context when data gathering fails"""
        
        return {
            'ticker': ticker,
            'company_name': f"{ticker} Inc.",
            'sector': 'Unknown',
            'market_cap': 'Unknown',
            'current_price': 'Unknown',
            'business_description': 'Business description not available - data gathering failed',
            'recent_news': 'Recent news not available - data gathering failed',
            'financial_statements': 'Financial data not available - data gathering failed',
            'historical_data': 'Historical data not available - data gathering failed',
            'peer_data': 'Peer data not available - data gathering failed',
            'industry_averages': 'Industry averages not available - data gathering failed',
            'quarterly_results': 'Quarterly results not available - data gathering failed',
            'guidance': 'Guidance not available - data gathering failed',
            'analyst_estimates': 'Analyst estimates not available - data gathering failed',
            'technical_indicators': 'Technical indicators not available - data gathering failed',
            'recent_filings': 'SEC filings not available - data gathering failed',
            'generation_timestamp': datetime.now().isoformat(),
            'data_sources': [],
            'status': 'fallback',
            'message': 'Using fallback context due to data gathering failure'
        }
    
    def _is_cached_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return (datetime.now() - cache_time).total_seconds() < self.cache_ttl

# Global instance
data_pipeline_integrator = DataPipelineIntegrator()