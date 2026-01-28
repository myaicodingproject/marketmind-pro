"""
Kiro Chart Pipeline Service
Comprehensive chart generation using Kiro CLI for MarketMind Pro
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
import subprocess
import tempfile
from datetime import datetime

from ..core.config import settings
from .error_handler import ErrorHandler
from .kiro_engine import KiroEngine

logger = logging.getLogger(__name__)

class KiroChartPipeline:
    """
    Comprehensive chart generation pipeline using Kiro CLI
    Generates professional Chart.js configurations for financial visualizations
    """
    
    def __init__(self):
        self.kiro_engine = KiroEngine()
        self.error_handler = ErrorHandler()
        self.chart_prompts = {
            'financial_trends': '.kiro/prompts/chart-financial-trends.md',
            'valuation_comparison': '.kiro/prompts/chart-valuation-comparison.md',
            'risk_assessment': '.kiro/prompts/chart-risk-assessment.md',
            'peer_analysis': '.kiro/prompts/chart-peer-analysis.md'
        }
        
    async def generate_comprehensive_charts(
        self, 
        ticker: str, 
        financial_data: Dict[str, Any],
        chart_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive chart suite for a company
        
        Args:
            ticker: Stock ticker symbol
            financial_data: Complete financial dataset
            chart_types: Specific chart types to generate (optional)
            
        Returns:
            Dictionary containing all generated charts
        """
        try:
            if chart_types is None:
                chart_types = ['financial_trends', 'valuation_comparison', 'risk_assessment', 'peer_analysis']
            
            logger.info(f"Starting comprehensive chart generation for {ticker}")
            
            # Prepare data for chart generation
            chart_data = await self._prepare_chart_data(ticker, financial_data)
            
            # Generate charts concurrently
            chart_tasks = []
            for chart_type in chart_types:
                task = self._generate_chart_type(chart_type, ticker, chart_data)
                chart_tasks.append(task)
            
            # Execute all chart generation tasks
            chart_results = await asyncio.gather(*chart_tasks, return_exceptions=True)
            
            # Process results and handle errors
            charts = {}
            for i, result in enumerate(chart_results):
                chart_type = chart_types[i]
                if isinstance(result, Exception):
                    logger.error(f"Error generating {chart_type} chart: {result}")
                    charts[chart_type] = self._create_fallback_chart(chart_type)
                else:
                    charts[chart_type] = result
            
            # Add metadata
            charts['metadata'] = {
                'ticker': ticker,
                'generated_at': datetime.utcnow().isoformat(),
                'chart_count': len([c for c in charts.values() if c is not None]),
                'generation_time': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Chart generation completed for {ticker}: {len(charts)} charts")
            return charts
            
        except Exception as e:
            logger.error(f"Error in comprehensive chart generation: {e}")
            return await self.error_handler.handle_chart_generation_error(ticker, str(e))
    
    async def _generate_chart_type(
        self, 
        chart_type: str, 
        ticker: str, 
        chart_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate specific chart type using Kiro CLI"""
        try:
            prompt_path = self.chart_prompts.get(chart_type)
            if not prompt_path:
                raise ValueError(f"Unknown chart type: {chart_type}")
            
            # Prepare input data for Kiro
            input_data = {
                'ticker': ticker,
                'chart_type': chart_type,
                'financial_data': chart_data.get('financial_data', {}),
                'valuation_data': chart_data.get('valuation_data', {}),
                'risk_data': chart_data.get('risk_data', {}),
                'peer_data': chart_data.get('peer_data', [])
            }
            
            # Execute Kiro CLI with chart prompt
            chart_config = await self.kiro_engine.execute_prompt(
                prompt_path=prompt_path,
                input_data=input_data,
                output_format='json'
            )
            
            # Validate and process chart configuration
            validated_config = await self._validate_chart_config(chart_config, chart_type)
            
            return validated_config
            
        except Exception as e:
            logger.error(f"Error generating {chart_type} chart: {e}")
            raise
    
    async def _prepare_chart_data(self, ticker: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare and structure data for chart generation"""
        try:
            chart_data = {
                'financial_data': {},
                'valuation_data': {},
                'risk_data': {},
                'peer_data': []
            }
            
            # Extract financial statement data
            if 'income_statement' in financial_data:
                chart_data['financial_data']['income_statement'] = financial_data['income_statement']
            
            if 'balance_sheet' in financial_data:
                chart_data['financial_data']['balance_sheet'] = financial_data['balance_sheet']
            
            # Extract valuation data
            if 'overview' in financial_data:
                overview = financial_data['overview']
                chart_data['valuation_data']['overview'] = {
                    'PERatio': overview.get('PERatio', 'N/A'),
                    'PriceToBookRatio': overview.get('PriceToBookRatio', 'N/A'),
                    'PriceToSalesRatioTTM': overview.get('PriceToSalesRatioTTM', 'N/A'),
                    'EVToEBITDA': overview.get('EVToEBITDA', 'N/A'),
                    'PEGRatio': overview.get('PEGRatio', 'N/A')
                }
            
            # Prepare risk assessment data
            chart_data['risk_data'] = {
                'balance_sheet': chart_data['financial_data'].get('balance_sheet', {}),
                'income_statement': chart_data['financial_data'].get('income_statement', {}),
                'overview': financial_data.get('overview', {})
            }
            
            # Add peer data if available
            if 'peer_data' in financial_data:
                chart_data['peer_data'] = financial_data['peer_data']
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error preparing chart data: {e}")
            raise
    
    async def _validate_chart_config(self, config: Dict[str, Any], chart_type: str) -> Dict[str, Any]:
        """Validate Chart.js configuration"""
        try:
            if not isinstance(config, dict):
                raise ValueError("Chart configuration must be a dictionary")
            
            # Basic Chart.js structure validation
            required_fields = ['type', 'data', 'options']
            
            for chart_name, chart_config in config.items():
                if chart_name == 'metadata':
                    continue
                    
                if not isinstance(chart_config, dict):
                    continue
                
                # Validate required Chart.js fields
                for field in required_fields:
                    if field not in chart_config:
                        logger.warning(f"Missing required field '{field}' in {chart_name}")
                
                # Validate data structure
                if 'data' in chart_config:
                    data = chart_config['data']
                    if 'labels' not in data or 'datasets' not in data:
                        logger.warning(f"Invalid data structure in {chart_name}")
            
            # Add chart type metadata
            config['chart_type'] = chart_type
            config['validated_at'] = datetime.utcnow().isoformat()
            
            return config
            
        except Exception as e:
            logger.error(f"Error validating chart config: {e}")
            return self._create_fallback_chart(chart_type)
    
    def _create_fallback_chart(self, chart_type: str) -> Dict[str, Any]:
        """Create fallback chart when generation fails"""
        fallback_charts = {
            'financial_trends': {
                'revenue_trends': {
                    'type': 'line',
                    'data': {
                        'labels': ['Data', 'Not', 'Available'],
                        'datasets': [{
                            'label': 'Revenue Trends',
                            'data': [0, 0, 0],
                            'borderColor': '#6B7280',
                            'backgroundColor': 'rgba(107, 114, 128, 0.1)'
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': 'Revenue Trends - Data Unavailable'
                            }
                        }
                    }
                }
            },
            'valuation_comparison': {
                'valuation_multiples': {
                    'type': 'bar',
                    'data': {
                        'labels': ['P/E', 'P/B', 'P/S'],
                        'datasets': [{
                            'label': 'Valuation Metrics',
                            'data': [0, 0, 0],
                            'backgroundColor': '#6B7280'
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': 'Valuation Analysis - Data Unavailable'
                            }
                        }
                    }
                }
            },
            'risk_assessment': {
                'risk_profile': {
                    'type': 'radar',
                    'data': {
                        'labels': ['Debt', 'Liquidity', 'Profitability'],
                        'datasets': [{
                            'label': 'Risk Profile',
                            'data': [50, 50, 50],
                            'borderColor': '#6B7280',
                            'backgroundColor': 'rgba(107, 114, 128, 0.2)'
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': 'Risk Assessment - Data Unavailable'
                            }
                        }
                    }
                }
            },
            'peer_analysis': {
                'peer_comparison': {
                    'type': 'bar',
                    'data': {
                        'labels': ['Company'],
                        'datasets': [{
                            'label': 'Peer Comparison',
                            'data': [0],
                            'backgroundColor': '#6B7280'
                        }]
                    },
                    'options': {
                        'responsive': True,
                        'plugins': {
                            'title': {
                                'display': True,
                                'text': 'Peer Analysis - Data Unavailable'
                            }
                        }
                    }
                }
            }
        }
        
        return fallback_charts.get(chart_type, {})
    
    async def generate_chart_for_report_section(
        self, 
        ticker: str, 
        section: str, 
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate charts specific to report section"""
        section_chart_mapping = {
            'executive_summary': ['valuation_comparison'],
            'company_overview': ['financial_trends'],
            'financial_analysis': ['financial_trends'],
            'valuation_analysis': ['valuation_comparison', 'peer_analysis'],
            'risk_assessment': ['risk_assessment']
        }
        
        chart_types = section_chart_mapping.get(section, [])
        if not chart_types:
            return {}
        
        return await self.generate_comprehensive_charts(ticker, financial_data, chart_types)
    
    async def validate_chart_data_quality(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data quality for chart generation"""
        quality_report = {
            'overall_quality': 'good',
            'missing_data': [],
            'data_issues': [],
            'recommendations': []
        }
        
        try:
            # Check for required financial data
            required_sections = ['income_statement', 'balance_sheet', 'overview']
            for section in required_sections:
                if section not in financial_data:
                    quality_report['missing_data'].append(section)
            
            # Check income statement data quality
            if 'income_statement' in financial_data:
                income_data = financial_data['income_statement']
                if 'annualReports' not in income_data or len(income_data['annualReports']) < 3:
                    quality_report['data_issues'].append('Insufficient historical income data')
            
            # Determine overall quality
            if len(quality_report['missing_data']) > 1:
                quality_report['overall_quality'] = 'poor'
            elif len(quality_report['missing_data']) > 0 or len(quality_report['data_issues']) > 0:
                quality_report['overall_quality'] = 'fair'
            
            return quality_report
            
        except Exception as e:
            logger.error(f"Error validating chart data quality: {e}")
            return {
                'overall_quality': 'poor',
                'error': str(e)
            }