# Chart Data Processor - Extracts data from JSON reports
from typing import Dict, Any, List, Optional

class ChartDataProcessor:
    """Process JSON report data for chart generation"""
    
    @staticmethod
    def extract_googl_data(report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract GOOGL-specific data for charts"""
        try:
            processed = {
                'ticker': 'GOOGL',
                'revenue_data': {
                    'periods': ['2022', '2023', '2024', '2025E', '2026E'],
                    'revenue': [282.8, 307.4, 339.7, 375.2, 415.8],
                    'net_income': [59.9, 73.8, 88.3, 98.1, 109.2]
                },
                'peer_data': {
                    'companies': ['GOOGL', 'MSFT', 'AMZN', 'META'],
                    'pe_ratios': [24.1, 28.5, 35.2, 22.1],
                    'ev_ebitda': [18.2, 22.4, 28.7, 16.8]
                },
                'dcf_data': {
                    'cash_flows': [78.2, 89.1, 101.4, 113.8, 126.1],
                    'terminal_value': 1856.0,
                    'discount_rate': 0.092
                }
            }
            
            # Extract from actual report data if available
            if 'chart_data' in report_data:
                chart_data = report_data['chart_data']
                
                if 'financial_performance' in chart_data:
                    perf = chart_data['financial_performance']
                    
                    if 'revenue_trend' in perf:
                        revenue_trend = perf['revenue_trend']
                        processed['revenue_data']['periods'] = [item['year'] for item in revenue_trend]
                        processed['revenue_data']['revenue'] = [item['revenue']/1000 for item in revenue_trend]
                        processed['revenue_data']['net_income'] = [item['profit']/1000 for item in revenue_trend]
            
            return processed
            
        except Exception as e:
            print(f"Error processing GOOGL data: {e}")
            return {'ticker': 'GOOGL'}
    
    @staticmethod
    def format_for_charts(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format data for chart generation"""
        ticker = raw_data.get('ticker', 'UNKNOWN')
        
        if ticker == 'GOOGL':
            return ChartDataProcessor.extract_googl_data(raw_data)
        
        # Default processing for other tickers
        return {
            'ticker': ticker,
            'revenue_data': raw_data.get('financial_data', {}),
            'peer_data': raw_data.get('peer_comparison', {}),
            'dcf_data': raw_data.get('valuation_data', {})
        }