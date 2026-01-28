"""
Chart Data Processor - Transforms financial data for Chart.js visualization
"""
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ChartDataPoint:
    """Single data point for charts"""
    x: Union[str, float, datetime]
    y: Union[float, int]
    label: Optional[str] = None
    metadata: Optional[Dict] = None

@dataclass
class ChartDataset:
    """Chart.js dataset structure"""
    label: str
    data: List[Union[float, Dict]]
    backgroundColor: Optional[Union[str, List[str]]] = None
    borderColor: Optional[Union[str, List[str]]] = None
    borderWidth: int = 2
    fill: bool = False
    tension: float = 0.1
    pointRadius: int = 4
    pointHoverRadius: int = 6

@dataclass
class ChartConfig:
    """Complete Chart.js configuration"""
    type: str
    data: Dict
    options: Dict

class ChartDataProcessor:
    """Main processor for transforming financial data into Chart.js format"""
    
    # Color palettes for different chart types
    COLORS = {
        'primary': ['#3B82F6', '#EF4444', '#10B981', '#F59E0B', '#8B5CF6'],
        'revenue': '#10B981',
        'profit': '#3B82F6', 
        'loss': '#EF4444',
        'neutral': '#6B7280',
        'growth': '#059669',
        'decline': '#DC2626'
    }
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def process_revenue_trends(self, financial_data: Dict) -> ChartConfig:
        """Process revenue trend data for line chart"""
        try:
            datasets = []
            labels = []
            
            # Process annual revenue
            if 'income_statement' in financial_data and 'annualReports' in financial_data['income_statement']:
                annual_data = financial_data['income_statement']['annualReports']
                
                # Sort by fiscal year
                sorted_data = sorted(annual_data, key=lambda x: x.get('fiscalDateEnding', ''))
                
                revenue_data = []
                labels = []
                
                for report in sorted_data[-5:]:  # Last 5 years
                    fiscal_year = report.get('fiscalDateEnding', '')[:4]
                    revenue = self._safe_float(report.get('totalRevenue', 0)) / 1e9  # Convert to billions
                    
                    labels.append(fiscal_year)
                    revenue_data.append(round(revenue, 2))
                
                datasets.append(ChartDataset(
                    label='Annual Revenue (Billions)',
                    data=revenue_data,
                    borderColor=self.COLORS['revenue'],
                    backgroundColor=self.COLORS['revenue'] + '20',
                    fill=True
                ))
            
            # Process quarterly revenue if available
            if 'income_statement' in financial_data and 'quarterlyReports' in financial_data['income_statement']:
                quarterly_data = financial_data['income_statement']['quarterlyReports']
                
                quarterly_revenue = []
                quarterly_labels = []
                
                for report in sorted(quarterly_data, key=lambda x: x.get('fiscalDateEnding', ''))[-8:]:
                    quarter = report.get('fiscalDateEnding', '')
                    revenue = self._safe_float(report.get('totalRevenue', 0)) / 1e9
                    
                    quarterly_labels.append(quarter[:7])  # YYYY-MM format
                    quarterly_revenue.append(round(revenue, 2))
                
                if quarterly_revenue:
                    datasets.append(ChartDataset(
                        label='Quarterly Revenue (Billions)',
                        data=quarterly_revenue,
                        borderColor=self.COLORS['primary'][1],
                        backgroundColor=self.COLORS['primary'][1] + '20',
                        borderDash=[5, 5]
                    ))
            
            return ChartConfig(
                type='line',
                data={
                    'labels': labels,
                    'datasets': [self._dataset_to_dict(ds) for ds in datasets]
                },
                options=self._get_line_chart_options('Revenue Trends', 'Revenue (Billions USD)')
            )
            
        except Exception as e:
            self.logger.error(f"Error processing revenue trends: {e}")
            return self._get_error_chart("Revenue Trends", str(e))
    
    def process_profit_margins(self, financial_data: Dict) -> ChartConfig:
        """Process profit margin data for multi-line chart"""
        try:
            if 'income_statement' not in financial_data or 'annualReports' not in financial_data['income_statement']:
                return self._get_empty_chart("Profit Margins", "No income statement data available")
            
            annual_data = financial_data['income_statement']['annualReports']
            sorted_data = sorted(annual_data, key=lambda x: x.get('fiscalDateEnding', ''))
            
            labels = []
            gross_margins = []
            operating_margins = []
            net_margins = []
            
            for report in sorted_data[-5:]:
                fiscal_year = report.get('fiscalDateEnding', '')[:4]
                revenue = self._safe_float(report.get('totalRevenue', 0))
                
                if revenue > 0:
                    # Calculate margins
                    gross_profit = self._safe_float(report.get('grossProfit', 0))
                    operating_income = self._safe_float(report.get('operatingIncome', 0))
                    net_income = self._safe_float(report.get('netIncome', 0))
                    
                    gross_margin = (gross_profit / revenue) * 100
                    operating_margin = (operating_income / revenue) * 100
                    net_margin = (net_income / revenue) * 100
                    
                    labels.append(fiscal_year)
                    gross_margins.append(round(gross_margin, 2))
                    operating_margins.append(round(operating_margin, 2))
                    net_margins.append(round(net_margin, 2))
            
            datasets = [
                ChartDataset(
                    label='Gross Margin %',
                    data=gross_margins,
                    borderColor=self.COLORS['primary'][0],
                    backgroundColor=self.COLORS['primary'][0] + '20'
                ),
                ChartDataset(
                    label='Operating Margin %',
                    data=operating_margins,
                    borderColor=self.COLORS['primary'][1],
                    backgroundColor=self.COLORS['primary'][1] + '20'
                ),
                ChartDataset(
                    label='Net Margin %',
                    data=net_margins,
                    borderColor=self.COLORS['primary'][2],
                    backgroundColor=self.COLORS['primary'][2] + '20'
                )
            ]
            
            return ChartConfig(
                type='line',
                data={
                    'labels': labels,
                    'datasets': [self._dataset_to_dict(ds) for ds in datasets]
                },
                options=self._get_line_chart_options('Profit Margins', 'Margin (%)')
            )
            
        except Exception as e:
            self.logger.error(f"Error processing profit margins: {e}")
            return self._get_error_chart("Profit Margins", str(e))
    
    def process_valuation_multiples(self, financial_data: Dict, market_data: Dict = None) -> ChartConfig:
        """Process valuation multiples for bar chart"""
        try:
            if 'overview' not in financial_data:
                return self._get_empty_chart("Valuation Multiples", "No overview data available")
            
            overview = financial_data['overview']
            
            multiples = {}
            labels = []
            values = []
            colors = []
            
            # P/E Ratio
            pe_ratio = self._safe_float(overview.get('PERatio', 0))
            if pe_ratio > 0:
                multiples['P/E Ratio'] = pe_ratio
                colors.append(self._get_valuation_color(pe_ratio, 'pe'))
            
            # P/B Ratio
            pb_ratio = self._safe_float(overview.get('PriceToBookRatio', 0))
            if pb_ratio > 0:
                multiples['P/B Ratio'] = pb_ratio
                colors.append(self._get_valuation_color(pb_ratio, 'pb'))
            
            # P/S Ratio
            ps_ratio = self._safe_float(overview.get('PriceToSalesRatioTTM', 0))
            if ps_ratio > 0:
                multiples['P/S Ratio'] = ps_ratio
                colors.append(self._get_valuation_color(ps_ratio, 'ps'))
            
            # EV/EBITDA
            ev_ebitda = self._safe_float(overview.get('EVToEBITDA', 0))
            if ev_ebitda > 0:
                multiples['EV/EBITDA'] = ev_ebitda
                colors.append(self._get_valuation_color(ev_ebitda, 'ev_ebitda'))
            
            # PEG Ratio
            peg_ratio = self._safe_float(overview.get('PEGRatio', 0))
            if peg_ratio > 0:
                multiples['PEG Ratio'] = peg_ratio
                colors.append(self._get_valuation_color(peg_ratio, 'peg'))
            
            labels = list(multiples.keys())
            values = list(multiples.values())
            
            return ChartConfig(
                type='bar',
                data={
                    'labels': labels,
                    'datasets': [{
                        'label': 'Valuation Multiples',
                        'data': values,
                        'backgroundColor': colors,
                        'borderColor': colors,
                        'borderWidth': 1
                    }]
                },
                options=self._get_bar_chart_options('Valuation Multiples', 'Multiple')
            )
            
        except Exception as e:
            self.logger.error(f"Error processing valuation multiples: {e}")
            return self._get_error_chart("Valuation Multiples", str(e))
    
    def process_peer_comparison(self, company_data: Dict, peer_data: List[Dict]) -> ChartConfig:
        """Process peer comparison data for horizontal bar chart"""
        try:
            metrics = ['PERatio', 'PriceToBookRatio', 'PriceToSalesRatioTTM', 'ReturnOnEquityTTM']
            metric_labels = ['P/E Ratio', 'P/B Ratio', 'P/S Ratio', 'ROE %']
            
            companies = [company_data.get('overview', {}).get('Name', 'Company')]
            companies.extend([peer.get('overview', {}).get('Name', f'Peer {i+1}') 
                            for i, peer in enumerate(peer_data)])
            
            datasets = []
            
            for i, metric in enumerate(metrics):
                values = []
                
                # Company value
                company_value = self._safe_float(company_data.get('overview', {}).get(metric, 0))
                values.append(company_value)
                
                # Peer values
                for peer in peer_data:
                    peer_value = self._safe_float(peer.get('overview', {}).get(metric, 0))
                    values.append(peer_value)
                
                # Convert ROE to percentage
                if metric == 'ReturnOnEquityTTM':
                    values = [v * 100 if v else 0 for v in values]
                
                datasets.append({
                    'label': metric_labels[i],
                    'data': values,
                    'backgroundColor': self.COLORS['primary'][i % len(self.COLORS['primary'])],
                    'borderColor': self.COLORS['primary'][i % len(self.COLORS['primary'])],
                    'borderWidth': 1
                })
            
            return ChartConfig(
                type='bar',
                data={
                    'labels': companies,
                    'datasets': datasets
                },
                options=self._get_horizontal_bar_options('Peer Comparison', 'Value')
            )
            
        except Exception as e:
            self.logger.error(f"Error processing peer comparison: {e}")
            return self._get_error_chart("Peer Comparison", str(e))
    
    def process_risk_metrics(self, financial_data: Dict, market_data: Dict = None) -> ChartConfig:
        """Process risk metrics for radar chart"""
        try:
            overview = financial_data.get('overview', {})
            
            # Calculate risk metrics (normalized to 0-100 scale)
            metrics = {}
            
            # Debt-to-Equity (lower is better, invert scale)
            debt_to_equity = self._safe_float(overview.get('DebtToEquityRatio', 0))
            if debt_to_equity > 0:
                metrics['Debt Management'] = max(0, 100 - min(debt_to_equity * 10, 100))
            
            # Current Ratio (higher is better, cap at 100)
            current_ratio = self._safe_float(overview.get('CurrentRatio', 0))
            if current_ratio > 0:
                metrics['Liquidity'] = min(current_ratio * 25, 100)
            
            # ROE (higher is better)
            roe = self._safe_float(overview.get('ReturnOnEquityTTM', 0)) * 100
            if roe > 0:
                metrics['Profitability'] = min(roe * 2, 100)
            
            # Beta (lower volatility is better, invert)
            beta = self._safe_float(overview.get('Beta', 1))
            if beta > 0:
                metrics['Volatility'] = max(0, 100 - min(beta * 50, 100))
            
            # Interest Coverage (higher is better)
            # This would need to be calculated from income statement
            # For now, use a placeholder
            metrics['Interest Coverage'] = 75
            
            # Dividend Yield (moderate is good)
            div_yield = self._safe_float(overview.get('DividendYield', 0)) * 100
            if div_yield > 0:
                # Optimal range is 2-6%, score accordingly
                if 2 <= div_yield <= 6:
                    metrics['Dividend Stability'] = 100
                elif div_yield < 2:
                    metrics['Dividend Stability'] = div_yield * 25
                else:
                    metrics['Dividend Stability'] = max(0, 100 - (div_yield - 6) * 10)
            else:
                metrics['Dividend Stability'] = 0
            
            labels = list(metrics.keys())
            values = list(metrics.values())
            
            return ChartConfig(
                type='radar',
                data={
                    'labels': labels,
                    'datasets': [{
                        'label': 'Risk Profile',
                        'data': values,
                        'backgroundColor': self.COLORS['primary'][0] + '30',
                        'borderColor': self.COLORS['primary'][0],
                        'borderWidth': 2,
                        'pointBackgroundColor': self.COLORS['primary'][0],
                        'pointBorderColor': '#fff',
                        'pointHoverBackgroundColor': '#fff',
                        'pointHoverBorderColor': self.COLORS['primary'][0]
                    }]
                },
                options=self._get_radar_chart_options('Risk Assessment')
            )
            
        except Exception as e:
            self.logger.error(f"Error processing risk metrics: {e}")
            return self._get_error_chart("Risk Metrics", str(e))
    
    def _safe_float(self, value: Any) -> float:
        """Safely convert value to float"""
        if value is None or value == 'None' or value == '':
            return 0.0
        try:
            return float(value)
        except (ValueError, TypeError):
            return 0.0
    
    def _get_valuation_color(self, value: float, metric_type: str) -> str:
        """Get color based on valuation metric value"""
        # Define reasonable ranges for different metrics
        ranges = {
            'pe': {'low': 15, 'high': 25},
            'pb': {'low': 1, 'high': 3},
            'ps': {'low': 2, 'high': 5},
            'ev_ebitda': {'low': 10, 'high': 20},
            'peg': {'low': 0.5, 'high': 1.5}
        }
        
        if metric_type not in ranges:
            return self.COLORS['neutral']
        
        range_info = ranges[metric_type]
        
        if value <= range_info['low']:
            return self.COLORS['growth']  # Undervalued
        elif value >= range_info['high']:
            return self.COLORS['decline']  # Overvalued
        else:
            return self.COLORS['neutral']  # Fair value
    
    def _dataset_to_dict(self, dataset: ChartDataset) -> Dict:
        """Convert ChartDataset to dictionary"""
        return {
            'label': dataset.label,
            'data': dataset.data,
            'backgroundColor': dataset.backgroundColor,
            'borderColor': dataset.borderColor,
            'borderWidth': dataset.borderWidth,
            'fill': dataset.fill,
            'tension': dataset.tension,
            'pointRadius': dataset.pointRadius,
            'pointHoverRadius': dataset.pointHoverRadius
        }
    
    def _get_line_chart_options(self, title: str, y_axis_label: str) -> Dict:
        """Get standard line chart options"""
        return {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': title,
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'legend': {
                    'display': True,
                    'position': 'top'
                }
            },
            'scales': {
                'x': {
                    'display': True,
                    'title': {
                        'display': True,
                        'text': 'Year'
                    }
                },
                'y': {
                    'display': True,
                    'title': {
                        'display': True,
                        'text': y_axis_label
                    },
                    'beginAtZero': False
                }
            },
            'interaction': {
                'intersect': False,
                'mode': 'index'
            }
        }
    
    def _get_bar_chart_options(self, title: str, y_axis_label: str) -> Dict:
        """Get standard bar chart options"""
        return {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': title,
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'legend': {
                    'display': False
                }
            },
            'scales': {
                'x': {
                    'display': True
                },
                'y': {
                    'display': True,
                    'title': {
                        'display': True,
                        'text': y_axis_label
                    },
                    'beginAtZero': True
                }
            }
        }
    
    def _get_horizontal_bar_options(self, title: str, x_axis_label: str) -> Dict:
        """Get horizontal bar chart options"""
        return {
            'responsive': True,
            'maintainAspectRatio': False,
            'indexAxis': 'y',
            'plugins': {
                'title': {
                    'display': True,
                    'text': title,
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'legend': {
                    'display': True,
                    'position': 'top'
                }
            },
            'scales': {
                'x': {
                    'display': True,
                    'title': {
                        'display': True,
                        'text': x_axis_label
                    },
                    'beginAtZero': True
                },
                'y': {
                    'display': True
                }
            }
        }
    
    def _get_radar_chart_options(self, title: str) -> Dict:
        """Get radar chart options"""
        return {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'title': {
                    'display': True,
                    'text': title,
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'legend': {
                    'display': False
                }
            },
            'scales': {
                'r': {
                    'beginAtZero': True,
                    'max': 100,
                    'ticks': {
                        'stepSize': 20
                    }
                }
            }
        }
    
    def _get_error_chart(self, title: str, error_message: str) -> ChartConfig:
        """Return error chart configuration"""
        return ChartConfig(
            type='bar',
            data={
                'labels': ['Error'],
                'datasets': [{
                    'label': 'Error',
                    'data': [0],
                    'backgroundColor': self.COLORS['loss'],
                    'borderColor': self.COLORS['loss']
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
    
    def _get_empty_chart(self, title: str, message: str) -> ChartConfig:
        """Return empty chart configuration"""
        return ChartConfig(
            type='bar',
            data={
                'labels': ['No Data'],
                'datasets': [{
                    'label': 'No Data',
                    'data': [0],
                    'backgroundColor': self.COLORS['neutral'],
                    'borderColor': self.COLORS['neutral']
                }]
            },
            options={
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': f'{title} - {message}',
                        'font': {'size': 14}
                    }
                }
            }
        )