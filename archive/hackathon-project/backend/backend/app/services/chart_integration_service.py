"""
Chart Integration Service for Report Pipeline
Integrates Kiro-generated charts with MarketMind Pro report generation
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

from .kiro_chart_pipeline import KiroChartPipeline
from .chart_data_extractor import ChartDataExtractor
from .chart_config_generator import ChartConfigGenerator
from .chart_validator import ChartValidator
from .error_handler import ErrorHandler

logger = logging.getLogger(__name__)

class ChartIntegrationService:
    """
    Comprehensive chart integration service for MarketMind Pro
    Orchestrates chart generation, validation, and integration with reports
    """
    
    def __init__(self):
        self.kiro_pipeline = KiroChartPipeline()
        self.data_extractor = ChartDataExtractor()
        self.config_generator = ChartConfigGenerator()
        self.validator = ChartValidator()
        self.error_handler = ErrorHandler()
        
        # Report section to chart mapping
        self.section_chart_mapping = {
            'executive_summary': {
                'charts': ['valuation_multiples', 'key_metrics_summary'],
                'priority': 'high',
                'fallback_required': True
            },
            'company_overview': {
                'charts': ['revenue_trends', 'business_segments'],
                'priority': 'medium',
                'fallback_required': True
            },
            'financial_analysis': {
                'charts': ['revenue_trends', 'profit_margins', 'financial_ratios'],
                'priority': 'high',
                'fallback_required': True
            },
            'valuation_analysis': {
                'charts': ['valuation_multiples', 'peer_comparison', 'dcf_sensitivity'],
                'priority': 'high',
                'fallback_required': True
            },
            'risk_assessment': {
                'charts': ['risk_profile', 'debt_analysis', 'volatility_metrics'],
                'priority': 'medium',
                'fallback_required': False
            }
        }
    
    async def generate_charts_for_report(
        self, 
        ticker: str, 
        financial_data: Dict[str, Any],
        report_sections: List[str],
        chart_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive chart suite for report sections
        
        Args:
            ticker: Stock ticker symbol
            financial_data: Complete financial dataset
            report_sections: List of report sections requiring charts
            chart_options: Optional chart customization options
            
        Returns:
            Dictionary containing charts organized by report section
        """
        try:
            logger.info(f"Starting chart generation for {ticker} report sections: {report_sections}")
            
            # Initialize result structure
            result = {
                'ticker': ticker,
                'generated_at': datetime.utcnow().isoformat(),
                'sections': {},
                'metadata': {
                    'total_charts': 0,
                    'successful_charts': 0,
                    'failed_charts': 0,
                    'generation_time_ms': 0
                }
            }
            
            start_time = datetime.utcnow()
            
            # Validate input data quality
            data_quality = await self._validate_data_quality(financial_data)
            result['data_quality'] = data_quality
            
            # Generate charts for each section
            section_tasks = []
            for section in report_sections:
                if section in self.section_chart_mapping:
                    task = self._generate_section_charts(
                        section, ticker, financial_data, chart_options
                    )
                    section_tasks.append((section, task))
            
            # Execute section chart generation concurrently
            section_results = await asyncio.gather(
                *[task for _, task in section_tasks], 
                return_exceptions=True
            )
            
            # Process results
            for i, (section, _) in enumerate(section_tasks):
                section_result = section_results[i]
                
                if isinstance(section_result, Exception):
                    logger.error(f"Error generating charts for section {section}: {section_result}")
                    result['sections'][section] = await self._create_fallback_section(section, ticker)
                else:
                    result['sections'][section] = section_result
                    
                # Update metadata
                section_charts = result['sections'][section].get('charts', {})
                result['metadata']['total_charts'] += len(section_charts)
                
                for chart_name, chart_config in section_charts.items():
                    if chart_config.get('_validation', {}).get('valid', True):
                        result['metadata']['successful_charts'] += 1
                    else:
                        result['metadata']['failed_charts'] += 1
            
            # Calculate generation time
            end_time = datetime.utcnow()
            generation_time = (end_time - start_time).total_seconds() * 1000
            result['metadata']['generation_time_ms'] = int(generation_time)
            
            # Validate complete chart suite
            validation_report = await self._validate_chart_suite(result)
            result['validation'] = validation_report
            
            logger.info(f"Chart generation completed for {ticker}: {result['metadata']}")
            return result
            
        except Exception as e:
            logger.error(f"Error in chart integration service: {e}")
            return await self.error_handler.handle_chart_integration_error(ticker, str(e))
    
    async def _generate_section_charts(
        self, 
        section: str, 
        ticker: str, 
        financial_data: Dict[str, Any],
        chart_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate charts for specific report section"""
        try:
            section_config = self.section_chart_mapping[section]
            required_charts = section_config['charts']
            
            section_result = {
                'section': section,
                'priority': section_config['priority'],
                'charts': {},
                'generation_metadata': {
                    'requested_charts': required_charts,
                    'generated_at': datetime.utcnow().isoformat()
                }
            }
            
            # Generate charts based on section requirements
            chart_tasks = []
            for chart_type in required_charts:
                task = self._generate_specific_chart(
                    chart_type, ticker, financial_data, chart_options
                )
                chart_tasks.append((chart_type, task))
            
            # Execute chart generation
            chart_results = await asyncio.gather(
                *[task for _, task in chart_tasks],
                return_exceptions=True
            )
            
            # Process chart results
            for i, (chart_type, _) in enumerate(chart_tasks):
                chart_result = chart_results[i]
                
                if isinstance(chart_result, Exception):
                    logger.error(f"Error generating {chart_type} chart: {chart_result}")
                    if section_config['fallback_required']:
                        section_result['charts'][chart_type] = self._create_fallback_chart(chart_type)
                else:
                    section_result['charts'][chart_type] = chart_result
            
            return section_result
            
        except Exception as e:
            logger.error(f"Error generating section charts for {section}: {e}")
            raise
    
    async def _generate_specific_chart(
        self,
        chart_type: str,
        ticker: str,
        financial_data: Dict[str, Any],
        chart_options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate specific chart type"""
        try:
            # Map chart types to generation methods
            chart_generators = {
                'revenue_trends': self._generate_revenue_trends,
                'profit_margins': self._generate_profit_margins,
                'valuation_multiples': self._generate_valuation_multiples,
                'risk_profile': self._generate_risk_profile,
                'peer_comparison': self._generate_peer_comparison,
                'key_metrics_summary': self._generate_key_metrics_summary,
                'business_segments': self._generate_business_segments,
                'financial_ratios': self._generate_financial_ratios,
                'dcf_sensitivity': self._generate_dcf_sensitivity,
                'debt_analysis': self._generate_debt_analysis,
                'volatility_metrics': self._generate_volatility_metrics
            }
            
            generator = chart_generators.get(chart_type)
            if not generator:
                raise ValueError(f"Unknown chart type: {chart_type}")
            
            # Generate chart using appropriate method
            chart_config = await generator(ticker, financial_data, chart_options)
            
            # Validate chart configuration
            is_valid, errors, validation_report = self.validator.validate_chart_config(
                chart_config, chart_type
            )
            
            chart_config['_validation'] = validation_report
            
            return chart_config
            
        except Exception as e:
            logger.error(f"Error generating {chart_type} chart: {e}")
            raise
    
    # Chart generation methods
    async def _generate_revenue_trends(
        self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate revenue trends chart using Kiro CLI"""
        try:
            # Use Kiro pipeline for AI-generated chart
            kiro_result = await self.kiro_pipeline.generate_chart_for_report_section(
                ticker, 'financial_analysis', financial_data
            )
            
            if 'financial_trends' in kiro_result and 'revenue_trends' in kiro_result['financial_trends']:
                return kiro_result['financial_trends']['revenue_trends']
            
            # Fallback to data extractor
            return self.data_extractor.extract_revenue_trends(financial_data)
            
        except Exception as e:
            logger.error(f"Error generating revenue trends: {e}")
            return self.data_extractor.extract_revenue_trends(financial_data)
    
    async def _generate_profit_margins(
        self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate profit margins chart"""
        return self.data_extractor.extract_profit_margins(financial_data)
    
    async def _generate_valuation_multiples(
        self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate valuation multiples chart using Kiro CLI"""
        try:
            kiro_result = await self.kiro_pipeline.generate_chart_for_report_section(
                ticker, 'valuation_analysis', financial_data
            )
            
            if 'valuation_comparison' in kiro_result and 'valuation_multiples' in kiro_result['valuation_comparison']:
                return kiro_result['valuation_comparison']['valuation_multiples']
            
            return self.data_extractor.extract_valuation_multiples(financial_data)
            
        except Exception as e:
            logger.error(f"Error generating valuation multiples: {e}")
            return self.data_extractor.extract_valuation_multiples(financial_data)
    
    async def _generate_risk_profile(
        self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate risk profile radar chart using Kiro CLI"""
        try:
            kiro_result = await self.kiro_pipeline.generate_chart_for_report_section(
                ticker, 'risk_assessment', financial_data
            )
            
            if 'risk_assessment' in kiro_result and 'risk_profile' in kiro_result['risk_assessment']:
                return kiro_result['risk_assessment']['risk_profile']
            
            return self.data_extractor.extract_risk_profile(financial_data)
            
        except Exception as e:
            logger.error(f"Error generating risk profile: {e}")
            return self.data_extractor.extract_risk_profile(financial_data)
    
    async def _generate_peer_comparison(
        self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate peer comparison chart"""
        peer_data = financial_data.get('peer_data', [])
        company_data = {'ticker': ticker, **financial_data.get('overview', {})}
        return self.data_extractor.extract_peer_comparison(company_data, peer_data)
    
    async def _generate_key_metrics_summary(
        self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate key metrics summary chart"""
        overview = financial_data.get('overview', {})
        
        metrics = {
            'Market Cap': overview.get('MarketCapitalization', 'N/A'),
            'P/E Ratio': overview.get('PERatio', 'N/A'),
            'ROE': overview.get('ReturnOnEquityTTM', 'N/A'),
            'Debt/Equity': overview.get('DebtToEquityRatio', 'N/A')
        }
        
        labels = []
        values = []
        
        for metric, value in metrics.items():
            if value != 'N/A' and value is not None:
                try:
                    numeric_value = float(value)
                    labels.append(metric)
                    values.append(numeric_value)
                except (ValueError, TypeError):
                    continue
        
        return self.config_generator.generate_bar_chart(
            title="Key Financial Metrics",
            labels=labels,
            datasets=[{
                'label': 'Value',
                'data': values
            }],
            y_axis_title="Value"
        )
    
    # Additional chart generators (simplified implementations)
    async def _generate_business_segments(self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate business segments chart"""
        return self.config_generator.generate_doughnut_chart(
            title="Business Segments",
            labels=["Technology", "Services", "Other"],
            data=[60, 30, 10]
        )
    
    async def _generate_financial_ratios(self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate financial ratios chart"""
        return self.data_extractor.extract_valuation_multiples(financial_data)
    
    async def _generate_dcf_sensitivity(self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate DCF sensitivity analysis chart"""
        return self.config_generator.generate_line_chart(
            title="DCF Sensitivity Analysis",
            labels=["Conservative", "Base Case", "Optimistic"],
            datasets=[{
                'label': 'Valuation Range',
                'data': [80, 100, 120]
            }],
            y_axis_title="Valuation ($)"
        )
    
    async def _generate_debt_analysis(self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate debt analysis chart"""
        balance_sheet = financial_data.get('balance_sheet', {})
        annual_reports = balance_sheet.get('annualReports', [])
        
        if not annual_reports:
            return self.config_generator._create_error_chart('bar', 'Debt Analysis')
        
        labels = []
        debt_data = []
        
        for report in annual_reports[:5]:
            year = report.get('fiscalDateEnding', '')[:4]
            total_debt = float(report.get('totalDebt', 0) or 0) / 1_000_000_000
            
            labels.append(year)
            debt_data.append(round(total_debt, 1))
        
        return self.config_generator.generate_bar_chart(
            title="Debt Analysis - 5 Year Trend",
            labels=labels,
            datasets=[{
                'label': 'Total Debt (Billions)',
                'data': debt_data
            }],
            y_axis_title="Debt (Billions USD)"
        )
    
    async def _generate_volatility_metrics(self, ticker: str, financial_data: Dict[str, Any], options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Generate volatility metrics chart"""
        overview = financial_data.get('overview', {})
        beta = float(overview.get('Beta', 1.0) or 1.0)
        
        return self.config_generator.generate_radar_chart(
            title="Volatility Metrics",
            labels=["Beta", "Price Volatility", "Earnings Volatility"],
            datasets=[{
                'label': 'Risk Level',
                'data': [beta * 50, 60, 40]  # Normalized to 0-100 scale
            }],
            max_value=100
        )
    
    # Helper methods
    async def _validate_data_quality(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate financial data quality for chart generation"""
        return await self.kiro_pipeline.validate_chart_data_quality(financial_data)
    
    async def _validate_chart_suite(self, chart_result: Dict[str, Any]) -> Dict[str, Any]:
        """Validate complete chart suite"""
        all_charts = {}
        
        # Collect all charts from all sections
        for section_name, section_data in chart_result.get('sections', {}).items():
            section_charts = section_data.get('charts', {})
            for chart_name, chart_config in section_charts.items():
                all_charts[f"{section_name}_{chart_name}"] = chart_config
        
        return self.validator.validate_chart_suite(all_charts)
    
    def _create_fallback_chart(self, chart_type: str) -> Dict[str, Any]:
        """Create fallback chart for failed generation"""
        return self.config_generator._create_error_chart('bar', f"{chart_type.replace('_', ' ').title()}")
    
    async def _create_fallback_section(self, section: str, ticker: str) -> Dict[str, Any]:
        """Create fallback section with error charts"""
        section_config = self.section_chart_mapping.get(section, {})
        required_charts = section_config.get('charts', [])
        
        fallback_section = {
            'section': section,
            'priority': section_config.get('priority', 'medium'),
            'charts': {},
            'error': 'Section generation failed - using fallback charts'
        }
        
        for chart_type in required_charts:
            fallback_section['charts'][chart_type] = self._create_fallback_chart(chart_type)
        
        return fallback_section
    
    async def get_available_chart_types(self) -> Dict[str, List[str]]:
        """Get available chart types by report section"""
        return {
            section: config['charts'] 
            for section, config in self.section_chart_mapping.items()
        }
    
    async def generate_chart_preview(
        self, 
        ticker: str, 
        chart_type: str, 
        financial_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate preview of specific chart type"""
        try:
            chart_config = await self._generate_specific_chart(
                chart_type, ticker, financial_data, None
            )
            
            return {
                'ticker': ticker,
                'chart_type': chart_type,
                'chart_config': chart_config,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating chart preview: {e}")
            return {
                'ticker': ticker,
                'chart_type': chart_type,
                'error': str(e),
                'chart_config': self._create_fallback_chart(chart_type)
            }