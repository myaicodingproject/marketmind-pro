"""
Chart Service - Main service for chart data generation and management
"""
import asyncio
import json
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from .processor import ChartDataProcessor, ChartConfig
from .validator import ChartDataValidator, validate_chart_data
from ..reports.service import ReportService

logger = logging.getLogger(__name__)

class ChartService:
    """Main service for chart data generation and management"""
    
    def __init__(self):
        self.processor = ChartDataProcessor()
        self.validator = ChartDataValidator()
        self.logger = logging.getLogger(__name__)
    
    async def generate_company_charts(self, ticker: str, financial_data: Dict) -> Dict[str, ChartConfig]:
        """
        Generate all chart configurations for a company
        Returns dictionary of chart_name -> ChartConfig
        """
        try:
            self.logger.info(f"Generating charts for {ticker}")
            
            # Validate input data
            is_valid, errors, cleaned_data = validate_chart_data(financial_data)
            if not is_valid:
                self.logger.error(f"Data validation failed for {ticker}: {errors}")
                return self._get_error_charts(errors)
            
            charts = {}
            
            # Generate revenue trends chart
            try:
                charts['revenue_trends'] = self.processor.process_revenue_trends(cleaned_data)
                self.logger.debug(f"Generated revenue trends chart for {ticker}")
            except Exception as e:
                self.logger.error(f"Failed to generate revenue trends for {ticker}: {e}")
                charts['revenue_trends'] = self._get_error_chart("Revenue Trends", str(e))
            
            # Generate profit margins chart
            try:
                charts['profit_margins'] = self.processor.process_profit_margins(cleaned_data)
                self.logger.debug(f"Generated profit margins chart for {ticker}")
            except Exception as e:
                self.logger.error(f"Failed to generate profit margins for {ticker}: {e}")
                charts['profit_margins'] = self._get_error_chart("Profit Margins", str(e))
            
            # Generate valuation multiples chart
            try:
                charts['valuation_multiples'] = self.processor.process_valuation_multiples(cleaned_data)
                self.logger.debug(f"Generated valuation multiples chart for {ticker}")
            except Exception as e:
                self.logger.error(f"Failed to generate valuation multiples for {ticker}: {e}")
                charts['valuation_multiples'] = self._get_error_chart("Valuation Multiples", str(e))
            
            # Generate risk metrics chart
            try:
                charts['risk_metrics'] = self.processor.process_risk_metrics(cleaned_data)
                self.logger.debug(f"Generated risk metrics chart for {ticker}")
            except Exception as e:
                self.logger.error(f"Failed to generate risk metrics for {ticker}: {e}")
                charts['risk_metrics'] = self._get_error_chart("Risk Metrics", str(e))
            
            self.logger.info(f"Generated {len(charts)} charts for {ticker}")
            return charts
            
        except Exception as e:
            self.logger.error(f"Chart generation failed for {ticker}: {e}")
            return self._get_error_charts([f"Chart generation error: {str(e)}"])
    
    async def generate_peer_comparison_chart(self, company_ticker: str, company_data: Dict, 
                                           peer_tickers: List[str], peer_data: List[Dict]) -> ChartConfig:
        """Generate peer comparison chart"""
        try:
            self.logger.info(f"Generating peer comparison chart for {company_ticker} vs {peer_tickers}")
            
            # Validate company data
            is_valid, errors, cleaned_company_data = validate_chart_data(company_data)
            if not is_valid:
                self.logger.error(f"Company data validation failed: {errors}")
                return self._get_error_chart("Peer Comparison", f"Company data invalid: {errors[0]}")
            
            # Validate peer data
            cleaned_peer_data = []
            for i, peer in enumerate(peer_data):
                peer_valid, peer_errors, cleaned_peer = validate_chart_data(peer)
                if peer_valid:
                    cleaned_peer_data.append(cleaned_peer)
                else:
                    self.logger.warning(f"Peer {i} data validation failed: {peer_errors}")
            
            if not cleaned_peer_data:
                return self._get_error_chart("Peer Comparison", "No valid peer data available")
            
            chart = self.processor.process_peer_comparison(cleaned_company_data, cleaned_peer_data)
            self.logger.info(f"Generated peer comparison chart for {company_ticker}")
            return chart
            
        except Exception as e:
            self.logger.error(f"Peer comparison chart generation failed: {e}")
            return self._get_error_chart("Peer Comparison", str(e))
    
    async def generate_time_series_chart(self, ticker: str, data_type: str, 
                                       financial_data: Dict, periods: int = 5) -> ChartConfig:
        """Generate time series chart for specific data type"""
        try:
            self.logger.info(f"Generating {data_type} time series chart for {ticker}")
            
            if data_type == 'revenue':
                return self.processor.process_revenue_trends(financial_data)
            elif data_type == 'margins':
                return self.processor.process_profit_margins(financial_data)
            else:
                return self._get_error_chart("Time Series", f"Unsupported data type: {data_type}")
                
        except Exception as e:
            self.logger.error(f"Time series chart generation failed: {e}")
            return self._get_error_chart("Time Series", str(e))
    
    def serialize_charts_for_api(self, charts: Dict[str, ChartConfig]) -> Dict[str, Dict]:
        """Serialize chart configurations for API response"""
        try:
            serialized = {}
            
            for chart_name, chart_config in charts.items():
                serialized[chart_name] = {
                    'type': chart_config.type,
                    'data': self.validator.sanitize_for_json(chart_config.data),
                    'options': self.validator.sanitize_for_json(chart_config.options)
                }
            
            return serialized
            
        except Exception as e:
            self.logger.error(f"Chart serialization failed: {e}")
            return {}
    
    def validate_chart_request(self, request_data: Dict) -> tuple[bool, List[str]]:
        """Validate chart generation request"""
        errors = []
        
        if 'ticker' not in request_data:
            errors.append("Ticker is required")
        
        if 'chart_types' in request_data:
            valid_types = ['revenue_trends', 'profit_margins', 'valuation_multiples', 
                          'risk_metrics', 'peer_comparison']
            for chart_type in request_data['chart_types']:
                if chart_type not in valid_types:
                    errors.append(f"Invalid chart type: {chart_type}")
        
        return len(errors) == 0, errors
    
    async def get_chart_data_summary(self, ticker: str, financial_data: Dict) -> Dict:
        """Get summary of available chart data"""
        try:
            summary = {
                'ticker': ticker,
                'available_charts': [],
                'data_quality': {},
                'date_range': {},
                'last_updated': datetime.now().isoformat()
            }
            
            # Check data availability for each chart type
            if self._has_revenue_data(financial_data):
                summary['available_charts'].append('revenue_trends')
                summary['data_quality']['revenue_trends'] = 'good'
            
            if self._has_margin_data(financial_data):
                summary['available_charts'].append('profit_margins')
                summary['data_quality']['profit_margins'] = 'good'
            
            if self._has_valuation_data(financial_data):
                summary['available_charts'].append('valuation_multiples')
                summary['data_quality']['valuation_multiples'] = 'good'
            
            if self._has_risk_data(financial_data):
                summary['available_charts'].append('risk_metrics')
                summary['data_quality']['risk_metrics'] = 'good'
            
            # Get date ranges
            if 'income_statement' in financial_data and 'annualReports' in financial_data['income_statement']:
                reports = financial_data['income_statement']['annualReports']
                if reports:
                    dates = [r.get('fiscalDateEnding', '') for r in reports if r.get('fiscalDateEnding')]
                    if dates:
                        summary['date_range']['start'] = min(dates)
                        summary['date_range']['end'] = max(dates)
            
            return summary
            
        except Exception as e:
            self.logger.error(f"Chart data summary failed for {ticker}: {e}")
            return {'ticker': ticker, 'error': str(e)}
    
    def _has_revenue_data(self, data: Dict) -> bool:
        """Check if data contains revenue information"""
        return (
            'income_statement' in data and 
            'annualReports' in data['income_statement'] and
            len(data['income_statement']['annualReports']) > 0 and
            any(r.get('totalRevenue') for r in data['income_statement']['annualReports'])
        )
    
    def _has_margin_data(self, data: Dict) -> bool:
        """Check if data contains margin calculation data"""
        if not self._has_revenue_data(data):
            return False
        
        reports = data['income_statement']['annualReports']
        return any(
            r.get('grossProfit') or r.get('operatingIncome') or r.get('netIncome')
            for r in reports
        )
    
    def _has_valuation_data(self, data: Dict) -> bool:
        """Check if data contains valuation metrics"""
        if 'overview' not in data:
            return False
        
        overview = data['overview']
        valuation_fields = ['PERatio', 'PriceToBookRatio', 'PriceToSalesRatioTTM', 'EVToEBITDA']
        return any(overview.get(field) for field in valuation_fields)
    
    def _has_risk_data(self, data: Dict) -> bool:
        """Check if data contains risk metrics"""
        if 'overview' not in data:
            return False
        
        overview = data['overview']
        risk_fields = ['DebtToEquityRatio', 'CurrentRatio', 'Beta', 'ReturnOnEquityTTM']
        return any(overview.get(field) for field in risk_fields)
    
    def _get_error_chart(self, title: str, error_message: str) -> ChartConfig:
        """Get error chart configuration"""
        return ChartConfig(
            type='bar',
            data={
                'labels': ['Error'],
                'datasets': [{
                    'label': 'Error',
                    'data': [0],
                    'backgroundColor': '#EF4444',
                    'borderColor': '#EF4444'
                }]
            },
            options={
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'{title} - Error: {error_message}',
                        'font': {'size': 14}
                    }
                }
            }
        )
    
    def _get_error_charts(self, errors: List[str]) -> Dict[str, ChartConfig]:
        """Get error charts for all chart types"""
        error_message = "; ".join(errors[:3])  # Limit error message length
        
        return {
            'revenue_trends': self._get_error_chart("Revenue Trends", error_message),
            'profit_margins': self._get_error_chart("Profit Margins", error_message),
            'valuation_multiples': self._get_error_chart("Valuation Multiples", error_message),
            'risk_metrics': self._get_error_chart("Risk Metrics", error_message)
        }

# Global service instance
chart_service = ChartService()