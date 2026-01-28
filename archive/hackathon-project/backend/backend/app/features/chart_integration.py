"""
Chart Integration - Connects chart generation with report pipeline
"""
import asyncio
import json
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from .charts.service import chart_service
from .reports.service import ReportService

logger = logging.getLogger(__name__)

class ChartReportIntegration:
    """Integrates chart generation with report generation pipeline"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def generate_charts_for_report(self, ticker: str, financial_data: Dict, 
                                       report_sections: List[str] = None) -> Dict[str, Any]:
        """
        Generate charts for report sections
        Returns chart data organized by report section
        """
        try:
            self.logger.info(f"Generating charts for report: {ticker}")
            
            # Determine which charts to generate based on report sections
            chart_types = self._get_chart_types_for_sections(report_sections or ["all"])
            
            # Generate company charts
            charts = await chart_service.generate_company_charts(ticker, financial_data)
            
            # Filter charts based on requested types
            if chart_types and "all" not in chart_types:
                filtered_charts = {k: v for k, v in charts.items() if k in chart_types}
                charts = filtered_charts
            
            # Serialize charts for report integration
            serialized_charts = chart_service.serialize_charts_for_api(charts)
            
            # Organize charts by report section
            organized_charts = self._organize_charts_by_section(serialized_charts)
            
            # Add chart metadata
            chart_metadata = {
                'generated_at': datetime.now().isoformat(),
                'ticker': ticker,
                'chart_count': len(serialized_charts),
                'sections': list(organized_charts.keys())
            }
            
            return {
                'charts': organized_charts,
                'metadata': chart_metadata,
                'raw_charts': serialized_charts  # For direct access
            }
            
        except Exception as e:
            self.logger.error(f"Chart generation for report failed: {e}")
            return {
                'charts': {},
                'metadata': {'error': str(e)},
                'raw_charts': {}
            }
    
    async def generate_peer_charts_for_report(self, ticker: str, company_data: Dict,
                                            peer_tickers: List[str], peer_data: List[Dict]) -> Dict:
        """Generate peer comparison charts for report"""
        try:
            self.logger.info(f"Generating peer comparison charts for report: {ticker}")
            
            # Generate peer comparison chart
            peer_chart = await chart_service.generate_peer_comparison_chart(
                ticker, company_data, peer_tickers, peer_data
            )
            
            # Serialize chart
            serialized_chart = chart_service.serialize_charts_for_api({'peer_comparison': peer_chart})
            
            return {
                'peer_comparison': serialized_chart['peer_comparison'],
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'company': ticker,
                    'peers': peer_tickers,
                    'comparison_metrics': ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'ROE %']
                }
            }
            
        except Exception as e:
            self.logger.error(f"Peer comparison chart generation failed: {e}")
            return {'error': str(e)}
    
    def _get_chart_types_for_sections(self, sections: List[str]) -> List[str]:
        """Map report sections to chart types"""
        section_chart_mapping = {
            'executive_summary': ['valuation_multiples'],
            'company_overview': ['revenue_trends'],
            'financial_analysis': ['revenue_trends', 'profit_margins'],
            'valuation_analysis': ['valuation_multiples', 'peer_comparison'],
            'risk_assessment': ['risk_metrics'],
            'all': ['revenue_trends', 'profit_margins', 'valuation_multiples', 'risk_metrics']
        }
        
        chart_types = set()
        for section in sections:
            if section in section_chart_mapping:
                chart_types.update(section_chart_mapping[section])
        
        return list(chart_types)
    
    def _organize_charts_by_section(self, charts: Dict[str, Dict]) -> Dict[str, Dict]:
        """Organize charts by report section"""
        section_organization = {
            'executive_summary': {
                'charts': [],
                'description': 'Key performance indicators and valuation metrics'
            },
            'financial_analysis': {
                'charts': [],
                'description': 'Revenue trends and profitability analysis'
            },
            'valuation_analysis': {
                'charts': [],
                'description': 'Valuation multiples and peer comparison'
            },
            'risk_assessment': {
                'charts': [],
                'description': 'Risk metrics and financial stability indicators'
            }
        }
        
        # Map charts to sections
        chart_section_mapping = {
            'revenue_trends': ['financial_analysis'],
            'profit_margins': ['financial_analysis'],
            'valuation_multiples': ['executive_summary', 'valuation_analysis'],
            'risk_metrics': ['risk_assessment'],
            'peer_comparison': ['valuation_analysis']
        }
        
        for chart_name, chart_config in charts.items():
            sections = chart_section_mapping.get(chart_name, ['financial_analysis'])
            
            for section in sections:
                if section in section_organization:
                    section_organization[section]['charts'].append({
                        'name': chart_name,
                        'title': self._get_chart_title(chart_name),
                        'config': chart_config,
                        'description': self._get_chart_description(chart_name)
                    })
        
        # Remove empty sections
        return {k: v for k, v in section_organization.items() if v['charts']}
    
    def _get_chart_title(self, chart_name: str) -> str:
        """Get display title for chart"""
        titles = {
            'revenue_trends': 'Revenue Growth Trends',
            'profit_margins': 'Profitability Margins',
            'valuation_multiples': 'Valuation Metrics',
            'risk_metrics': 'Risk Assessment Profile',
            'peer_comparison': 'Peer Comparison Analysis'
        }
        return titles.get(chart_name, chart_name.replace('_', ' ').title())
    
    def _get_chart_description(self, chart_name: str) -> str:
        """Get description for chart"""
        descriptions = {
            'revenue_trends': 'Historical revenue performance showing growth trajectory over the past 5 years',
            'profit_margins': 'Profitability analysis including gross, operating, and net margins',
            'valuation_multiples': 'Key valuation ratios including P/E, P/B, P/S, and EV/EBITDA',
            'risk_metrics': 'Comprehensive risk assessment across multiple financial stability dimensions',
            'peer_comparison': 'Comparative analysis against industry peers across key financial metrics'
        }
        return descriptions.get(chart_name, 'Financial analysis chart')
    
    async def validate_chart_data_for_report(self, ticker: str, financial_data: Dict) -> Dict:
        """Validate that financial data is sufficient for chart generation"""
        try:
            # Get chart data summary
            summary = await chart_service.get_chart_data_summary(ticker, financial_data)
            
            # Assess data completeness
            completeness_score = len(summary.get('available_charts', [])) / 4 * 100  # 4 main chart types
            
            # Assess data quality
            quality_scores = summary.get('data_quality', {})
            avg_quality = len([q for q in quality_scores.values() if q == 'good']) / max(len(quality_scores), 1)
            
            return {
                'is_valid': completeness_score >= 50,  # At least 50% of charts available
                'completeness_score': completeness_score,
                'quality_score': avg_quality * 100,
                'available_charts': summary.get('available_charts', []),
                'missing_charts': [
                    chart for chart in ['revenue_trends', 'profit_margins', 'valuation_multiples', 'risk_metrics']
                    if chart not in summary.get('available_charts', [])
                ],
                'recommendations': self._get_data_recommendations(summary)
            }
            
        except Exception as e:
            self.logger.error(f"Chart data validation failed: {e}")
            return {
                'is_valid': False,
                'error': str(e),
                'completeness_score': 0,
                'quality_score': 0
            }
    
    def _get_data_recommendations(self, summary: Dict) -> List[str]:
        """Get recommendations for improving chart data"""
        recommendations = []
        
        available_charts = summary.get('available_charts', [])
        
        if 'revenue_trends' not in available_charts:
            recommendations.append("Income statement data needed for revenue trend analysis")
        
        if 'profit_margins' not in available_charts:
            recommendations.append("Detailed income statement data needed for margin analysis")
        
        if 'valuation_multiples' not in available_charts:
            recommendations.append("Company overview data with valuation ratios needed")
        
        if 'risk_metrics' not in available_charts:
            recommendations.append("Balance sheet and overview data needed for risk assessment")
        
        return recommendations

# Global integration instance
chart_integration = ChartReportIntegration()