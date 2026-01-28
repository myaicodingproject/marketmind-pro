"""
Chart Data Extraction and Formatting Service
Extracts and formats financial data for Chart.js visualization
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
import json
import math

logger = logging.getLogger(__name__)

class ChartDataExtractor:
    """
    Extracts and formats financial data for chart generation
    Handles data transformation, validation, and Chart.js formatting
    """
    
    def __init__(self):
        self.color_palette = {
            'primary': '#3B82F6',      # Blue
            'success': '#10B981',      # Green
            'warning': '#F59E0B',      # Orange
            'danger': '#EF4444',       # Red
            'purple': '#8B5CF6',       # Purple
            'neutral': '#6B7280',      # Gray
            'growth': '#059669',       # Dark Green
            'decline': '#DC2626'       # Dark Red
        }
    
    def extract_revenue_trends(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract revenue trend data for line chart"""
        try:
            income_statement = financial_data.get('income_statement', {})
            annual_reports = income_statement.get('annualReports', [])
            
            if not annual_reports:
                return self._create_empty_revenue_chart()
            
            # Sort by fiscal year (most recent first)
            sorted_reports = sorted(
                annual_reports, 
                key=lambda x: x.get('fiscalDateEnding', ''), 
                reverse=True
            )[:5]  # Last 5 years
            
            # Extract data
            labels = []
            revenue_data = []
            
            for report in reversed(sorted_reports):  # Reverse to show chronological order
                fiscal_date = report.get('fiscalDateEnding', '')
                revenue = report.get('totalRevenue', '0')
                
                if fiscal_date and revenue != 'None':
                    year = fiscal_date[:4]
                    revenue_billions = self._convert_to_billions(revenue)
                    
                    labels.append(year)
                    revenue_data.append(revenue_billions)
            
            return {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Revenue (Billions USD)',
                        'data': revenue_data,
                        'borderColor': self.color_palette['success'],
                        'backgroundColor': f"{self.color_palette['success']}20",
                        'fill': True,
                        'tension': 0.4,
                        'pointRadius': 6,
                        'pointHoverRadius': 8
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Revenue Trends - 5 Year Analysis',
                            'font': {'size': 16, 'weight': 'bold'}
                        },
                        'legend': {
                            'display': True,
                            'position': 'top'
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': False,
                            'title': {
                                'display': True,
                                'text': 'Revenue (Billions USD)'
                            },
                            'grid': {
                                'color': '#E5E7EB'
                            }
                        },
                        'x': {
                            'title': {
                                'display': True,
                                'text': 'Fiscal Year'
                            },
                            'grid': {
                                'color': '#E5E7EB'
                            }
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting revenue trends: {e}")
            return self._create_empty_revenue_chart()
    
    def extract_profit_margins(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract profit margin data for multi-line chart"""
        try:
            income_statement = financial_data.get('income_statement', {})
            annual_reports = income_statement.get('annualReports', [])
            
            if not annual_reports:
                return self._create_empty_margins_chart()
            
            # Sort by fiscal year
            sorted_reports = sorted(
                annual_reports, 
                key=lambda x: x.get('fiscalDateEnding', ''), 
                reverse=True
            )[:5]
            
            labels = []
            gross_margins = []
            operating_margins = []
            net_margins = []
            
            for report in reversed(sorted_reports):
                fiscal_date = report.get('fiscalDateEnding', '')
                total_revenue = float(report.get('totalRevenue', 0) or 0)
                
                if fiscal_date and total_revenue > 0:
                    year = fiscal_date[:4]
                    
                    # Calculate margins
                    gross_profit = float(report.get('grossProfit', 0) or 0)
                    operating_income = float(report.get('operatingIncome', 0) or 0)
                    net_income = float(report.get('netIncome', 0) or 0)
                    
                    gross_margin = (gross_profit / total_revenue) * 100
                    operating_margin = (operating_income / total_revenue) * 100
                    net_margin = (net_income / total_revenue) * 100
                    
                    labels.append(year)
                    gross_margins.append(round(gross_margin, 1))
                    operating_margins.append(round(operating_margin, 1))
                    net_margins.append(round(net_margin, 1))
            
            return {
                'type': 'line',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'Gross Margin (%)',
                            'data': gross_margins,
                            'borderColor': self.color_palette['primary'],
                            'backgroundColor': f"{self.color_palette['primary']}20",
                            'tension': 0.4
                        },
                        {
                            'label': 'Operating Margin (%)',
                            'data': operating_margins,
                            'borderColor': self.color_palette['warning'],
                            'backgroundColor': f"{self.color_palette['warning']}20",
                            'tension': 0.4
                        },
                        {
                            'label': 'Net Margin (%)',
                            'data': net_margins,
                            'borderColor': self.color_palette['purple'],
                            'backgroundColor': f"{self.color_palette['purple']}20",
                            'tension': 0.4
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Profit Margins Analysis',
                            'font': {'size': 16, 'weight': 'bold'}
                        }
                    },
                    'scales': {
                        'y': {
                            'title': {
                                'display': True,
                                'text': 'Margin (%)'
                            }
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting profit margins: {e}")
            return self._create_empty_margins_chart()
    
    def extract_valuation_multiples(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract valuation multiples for bar chart"""
        try:
            overview = financial_data.get('overview', {})
            
            metrics = {
                'P/E Ratio': overview.get('PERatio', 'N/A'),
                'P/B Ratio': overview.get('PriceToBookRatio', 'N/A'),
                'P/S Ratio': overview.get('PriceToSalesRatioTTM', 'N/A'),
                'EV/EBITDA': overview.get('EVToEBITDA', 'N/A'),
                'PEG Ratio': overview.get('PEGRatio', 'N/A')
            }
            
            labels = []
            values = []
            colors = []
            
            for metric, value in metrics.items():
                if value != 'N/A' and value != 'None' and value is not None:
                    try:
                        numeric_value = float(value)
                        labels.append(metric)
                        values.append(numeric_value)
                        colors.append(self._get_valuation_color(metric, numeric_value))
                    except (ValueError, TypeError):
                        continue
            
            return {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Valuation Multiples',
                        'data': values,
                        'backgroundColor': colors,
                        'borderColor': colors,
                        'borderWidth': 1
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Valuation Multiples Analysis',
                            'font': {'size': 16, 'weight': 'bold'}
                        },
                        'legend': {
                            'display': False
                        }
                    },
                    'scales': {
                        'y': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': 'Multiple Value'
                            }
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting valuation multiples: {e}")
            return self._create_empty_valuation_chart()
    
    def extract_risk_profile(self, financial_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract risk assessment data for radar chart"""
        try:
            balance_sheet = financial_data.get('balance_sheet', {})
            income_statement = financial_data.get('income_statement', {})
            overview = financial_data.get('overview', {})
            
            # Get latest annual reports
            bs_reports = balance_sheet.get('annualReports', [])
            is_reports = income_statement.get('annualReports', [])
            
            if not bs_reports or not is_reports:
                return self._create_empty_risk_chart()
            
            latest_bs = bs_reports[0]
            latest_is = is_reports[0]
            
            # Calculate risk scores (0-100, higher is better/safer)
            risk_scores = {
                'Debt Management': self._calculate_debt_score(latest_bs),
                'Liquidity': self._calculate_liquidity_score(latest_bs),
                'Profitability': self._calculate_profitability_score(latest_is, latest_bs),
                'Volatility': self._calculate_volatility_score(overview),
                'Interest Coverage': self._calculate_interest_coverage_score(latest_is),
                'Dividend Stability': self._calculate_dividend_score(overview)
            }
            
            labels = list(risk_scores.keys())
            data = list(risk_scores.values())
            
            return {
                'type': 'radar',
                'data': {
                    'labels': labels,
                    'datasets': [{
                        'label': 'Risk Score (0-100)',
                        'data': data,
                        'borderColor': self.color_palette['primary'],
                        'backgroundColor': f"{self.color_palette['primary']}30",
                        'pointBackgroundColor': self.color_palette['primary'],
                        'pointBorderColor': '#fff',
                        'pointHoverBackgroundColor': '#fff',
                        'pointHoverBorderColor': self.color_palette['primary']
                    }]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Risk Assessment Profile',
                            'font': {'size': 16, 'weight': 'bold'}
                        }
                    },
                    'scales': {
                        'r': {
                            'beginAtZero': True,
                            'max': 100,
                            'ticks': {
                                'stepSize': 20
                            },
                            'pointLabels': {
                                'font': {'size': 12}
                            }
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting risk profile: {e}")
            return self._create_empty_risk_chart()
    
    def extract_peer_comparison(self, company_data: Dict[str, Any], peer_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract peer comparison data for horizontal bar chart"""
        try:
            if not peer_data:
                return self._create_empty_peer_chart()
            
            # Combine company with peers
            all_companies = [company_data] + peer_data
            
            labels = []
            pe_ratios = []
            roe_values = []
            colors = []
            
            for i, company in enumerate(all_companies):
                ticker = company.get('ticker', company.get('Symbol', 'Unknown'))
                labels.append(ticker)
                
                # Extract P/E ratio
                pe_ratio = company.get('PERatio', company.get('overview', {}).get('PERatio', 'N/A'))
                try:
                    pe_ratios.append(float(pe_ratio) if pe_ratio != 'N/A' else 0)
                except (ValueError, TypeError):
                    pe_ratios.append(0)
                
                # Extract ROE
                roe = company.get('ROE', company.get('overview', {}).get('ReturnOnEquityTTM', 'N/A'))
                try:
                    roe_percent = float(roe) * 100 if roe != 'N/A' else 0
                    roe_values.append(roe_percent)
                except (ValueError, TypeError):
                    roe_values.append(0)
                
                # Color coding (first company is target, others are peers)
                if i == 0:
                    colors.append(self.color_palette['primary'])
                else:
                    colors.append(self.color_palette['neutral'])
            
            return {
                'type': 'bar',
                'data': {
                    'labels': labels,
                    'datasets': [
                        {
                            'label': 'P/E Ratio',
                            'data': pe_ratios,
                            'backgroundColor': colors,
                            'borderColor': colors,
                            'borderWidth': 1
                        }
                    ]
                },
                'options': {
                    'responsive': True,
                    'maintainAspectRatio': False,
                    'indexAxis': 'y',  # Horizontal bars
                    'plugins': {
                        'title': {
                            'display': True,
                            'text': 'Peer Comparison - P/E Ratios',
                            'font': {'size': 16, 'weight': 'bold'}
                        }
                    },
                    'scales': {
                        'x': {
                            'beginAtZero': True,
                            'title': {
                                'display': True,
                                'text': 'P/E Ratio'
                            }
                        }
                    }
                }
            }
            
        except Exception as e:
            logger.error(f"Error extracting peer comparison: {e}")
            return self._create_empty_peer_chart()
    
    # Helper methods
    def _convert_to_billions(self, value: str) -> float:
        """Convert string value to billions"""
        try:
            numeric_value = float(value)
            return round(numeric_value / 1_000_000_000, 1)
        except (ValueError, TypeError):
            return 0.0
    
    def _get_valuation_color(self, metric: str, value: float) -> str:
        """Get color based on valuation metric value"""
        if metric == 'P/E Ratio':
            if value < 20:
                return self.color_palette['success']  # Undervalued
            elif value < 30:
                return self.color_palette['warning']  # Fair
            else:
                return self.color_palette['danger']   # Overvalued
        elif metric == 'P/B Ratio':
            if value < 3:
                return self.color_palette['success']
            elif value < 5:
                return self.color_palette['warning']
            else:
                return self.color_palette['danger']
        else:
            return self.color_palette['primary']
    
    def _calculate_debt_score(self, balance_sheet: Dict[str, Any]) -> int:
        """Calculate debt management score (0-100)"""
        try:
            total_debt = float(balance_sheet.get('totalDebt', 0) or 0)
            total_assets = float(balance_sheet.get('totalAssets', 1) or 1)
            
            debt_ratio = total_debt / total_assets
            # Lower debt ratio = higher score
            score = max(0, min(100, (1 - debt_ratio) * 100))
            return int(score)
        except:
            return 50  # Default neutral score
    
    def _calculate_liquidity_score(self, balance_sheet: Dict[str, Any]) -> int:
        """Calculate liquidity score (0-100)"""
        try:
            current_assets = float(balance_sheet.get('currentAssets', 0) or 0)
            current_liabilities = float(balance_sheet.get('currentLiabilities', 1) or 1)
            
            current_ratio = current_assets / current_liabilities
            # Higher current ratio = higher score (capped at 100)
            score = min(100, current_ratio * 50)
            return int(score)
        except:
            return 50
    
    def _calculate_profitability_score(self, income_statement: Dict[str, Any], balance_sheet: Dict[str, Any]) -> int:
        """Calculate profitability score (0-100)"""
        try:
            net_income = float(income_statement.get('netIncome', 0) or 0)
            total_assets = float(balance_sheet.get('totalAssets', 1) or 1)
            
            roa = (net_income / total_assets) * 100
            # Higher ROA = higher score
            score = min(100, max(0, roa * 5))  # Scale ROA to 0-100
            return int(score)
        except:
            return 50
    
    def _calculate_volatility_score(self, overview: Dict[str, Any]) -> int:
        """Calculate volatility score (0-100)"""
        try:
            beta = float(overview.get('Beta', 1) or 1)
            # Lower beta = higher score (less volatile)
            score = max(0, min(100, (2 - beta) * 50))
            return int(score)
        except:
            return 50
    
    def _calculate_interest_coverage_score(self, income_statement: Dict[str, Any]) -> int:
        """Calculate interest coverage score (0-100)"""
        try:
            ebitda = float(income_statement.get('ebitda', 0) or 0)
            interest_expense = float(income_statement.get('interestExpense', 1) or 1)
            
            coverage_ratio = ebitda / interest_expense
            # Higher coverage = higher score
            score = min(100, coverage_ratio * 10)
            return int(score)
        except:
            return 50
    
    def _calculate_dividend_score(self, overview: Dict[str, Any]) -> int:
        """Calculate dividend stability score (0-100)"""
        try:
            dividend_yield = float(overview.get('DividendYield', 0) or 0)
            # Moderate dividend yield is good (2-6%)
            if 0.02 <= dividend_yield <= 0.06:
                score = 80
            elif dividend_yield > 0:
                score = 60
            else:
                score = 40  # No dividend
            return score
        except:
            return 50
    
    # Fallback chart methods
    def _create_empty_revenue_chart(self) -> Dict[str, Any]:
        """Create empty revenue chart"""
        return {
            'type': 'line',
            'data': {
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Revenue',
                    'data': [0],
                    'borderColor': self.color_palette['neutral']
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
    
    def _create_empty_margins_chart(self) -> Dict[str, Any]:
        """Create empty margins chart"""
        return {
            'type': 'line',
            'data': {
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Margins',
                    'data': [0],
                    'borderColor': self.color_palette['neutral']
                }]
            },
            'options': {
                'responsive': True,
                'plugins': {
                    'title': {
                        'display': True,
                        'text': 'Profit Margins - Data Unavailable'
                    }
                }
            }
        }
    
    def _create_empty_valuation_chart(self) -> Dict[str, Any]:
        """Create empty valuation chart"""
        return {
            'type': 'bar',
            'data': {
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Valuation',
                    'data': [0],
                    'backgroundColor': self.color_palette['neutral']
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
    
    def _create_empty_risk_chart(self) -> Dict[str, Any]:
        """Create empty risk chart"""
        return {
            'type': 'radar',
            'data': {
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Risk',
                    'data': [50],
                    'borderColor': self.color_palette['neutral']
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
    
    def _create_empty_peer_chart(self) -> Dict[str, Any]:
        """Create empty peer chart"""
        return {
            'type': 'bar',
            'data': {
                'labels': ['No Data Available'],
                'datasets': [{
                    'label': 'Peer Comparison',
                    'data': [0],
                    'backgroundColor': self.color_palette['neutral']
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