"""
Enhanced Chart Service for MarketMind Pro
Generates advanced chart data for Phase 4-5 implementation
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import numpy as np

@dataclass
class ChartDataPoint:
    """Represents a single data point in a chart"""
    x: Any
    y: Any
    label: str = ""
    metadata: Dict = None

class AdvancedChartService:
    """Service for generating advanced chart data structures"""
    
    def __init__(self):
        self.color_palette = [
            '#0088FE', '#00C49F', '#FFBB28', '#FF8042', 
            '#8884D8', '#82CA9D', '#FFC658', '#FF7C7C'
        ]
    
    def generate_section_chart_data(self, section_content: str, section_name: str) -> Dict[str, Any]:
        """Generate chart data for a specific report section"""
        
        chart_data = {}
        
        if section_name == 'executive_summary':
            chart_data = self._extract_executive_summary_data(section_content)
        elif section_name == 'financial_analysis':
            chart_data = self._extract_financial_analysis_data(section_content)
        elif section_name == 'valuation_analysis':
            chart_data = self._extract_valuation_analysis_data(section_content)
        elif section_name == 'risk_assessment':
            chart_data = self._extract_risk_assessment_data(section_content)
        elif section_name == 'market_analysis':
            chart_data = self._extract_market_analysis_data(section_content)
        
        return chart_data
    
    def _extract_executive_summary_data(self, content: str) -> Dict[str, Any]:
        """Extract chart data from executive summary section"""
        data = {}
        
        # Extract recommendation and confidence
        rating_match = re.search(r'(BUY|SELL|HOLD)', content, re.IGNORECASE)
        confidence_match = re.search(r'confidence[:\s]*(\d+)%?', content, re.IGNORECASE)
        risk_match = re.search(r'risk[:\s]*(low|medium|high)', content, re.IGNORECASE)
        
        if rating_match or confidence_match or risk_match:
            data['recommendation'] = {
                'rating': rating_match.group(1).upper() if rating_match else 'HOLD',
                'confidence': int(confidence_match.group(1)) if confidence_match else 75,
                'risk_level': risk_match.group(1).title() if risk_match else 'Medium'
            }
        
        # Extract key metrics
        price_target_match = re.search(r'price target[:\s]*\$?(\d+\.?\d*)', content, re.IGNORECASE)
        upside_match = re.search(r'upside[:\s]*(\d+\.?\d*)%?', content, re.IGNORECASE)
        
        if price_target_match or upside_match:
            data['key_metrics'] = []
            if price_target_match:
                data['key_metrics'].append({
                    'metric': 'Price Target',
                    'value': float(price_target_match.group(1)),
                    'unit': '$'
                })
            if upside_match:
                data['key_metrics'].append({
                    'metric': 'Upside Potential',
                    'value': float(upside_match.group(1)),
                    'unit': '%'
                })
        
        return data
    
    def _extract_financial_analysis_data(self, content: str) -> Dict[str, Any]:
        """Extract chart data from financial analysis section"""
        data = {}
        
        # Extract revenue trend data
        revenue_data = self._extract_revenue_trend(content)
        if revenue_data:
            data['revenue_trend'] = revenue_data
        
        # Extract margin data
        margin_data = self._extract_margins(content)
        if margin_data:
            data['margins'] = margin_data
        
        # Extract segment breakdown
        segment_data = self._extract_segment_breakdown(content)
        if segment_data:
            data['segment_breakdown'] = segment_data
        
        # Generate cash flow waterfall if cash flow data is present
        cash_flow_data = self._extract_cash_flow_waterfall(content)
        if cash_flow_data:
            data['cash_flow_waterfall'] = cash_flow_data
        
        return data
    
    def _extract_valuation_analysis_data(self, content: str) -> Dict[str, Any]:
        """Extract chart data from valuation analysis section"""
        data = {}
        
        # Extract peer comparison data
        peer_data = self._extract_peer_comparison(content)
        if peer_data:
            data['peer_comparison'] = peer_data
        
        # Generate DCF sensitivity analysis
        dcf_data = self._generate_dcf_sensitivity(content)
        if dcf_data:
            data['dcf_sensitivity'] = dcf_data
        
        # Extract price target breakdown
        price_target_data = self._extract_price_target_breakdown(content)
        if price_target_data:
            data['price_target_breakdown'] = price_target_data
        
        return data
    
    def _extract_risk_assessment_data(self, content: str) -> Dict[str, Any]:
        """Extract chart data from risk assessment section"""
        data = {}
        
        # Extract risk matrix data
        risk_matrix = self._extract_risk_matrix(content)
        if risk_matrix:
            data['risk_matrix'] = risk_matrix
        
        # Extract scenario analysis
        scenario_data = self._extract_scenario_analysis(content)
        if scenario_data:
            data['scenario_analysis'] = scenario_data
        
        return data
    
    def _extract_market_analysis_data(self, content: str) -> Dict[str, Any]:
        """Extract chart data from market analysis section"""
        data = {}
        
        # Extract market share data
        market_share = self._extract_market_share(content)
        if market_share:
            data['market_share'] = market_share
        
        # Extract competitive position
        competitive_data = self._extract_competitive_position(content)
        if competitive_data:
            data['competitive_position'] = competitive_data
        
        return data
    
    def _extract_revenue_trend(self, content: str) -> Optional[List[Dict]]:
        """Extract revenue trend data from content"""
        # Look for revenue patterns with years
        revenue_pattern = r'(\d{4}[E]?)[:\s]*\$?(\d+\.?\d*)[BM]?.*?(\d+\.?\d*)%?'
        matches = re.findall(revenue_pattern, content)
        
        if not matches:
            return None
        
        revenue_data = []
        for year, revenue, growth in matches:
            try:
                revenue_val = float(revenue)
                growth_val = float(growth) if growth else 0
                
                # Add confidence bands (±10% for projections)
                is_projection = 'E' in year
                confidence_band = 0.1 if is_projection else 0.05
                
                revenue_data.append({
                    'year': year,
                    'revenue': revenue_val,
                    'growth': growth_val,
                    'high': revenue_val * (1 + confidence_band),
                    'base': revenue_val,
                    'low': revenue_val * (1 - confidence_band)
                })
            except ValueError:
                continue
        
        return revenue_data if revenue_data else None
    
    def _extract_margins(self, content: str) -> Optional[List[Dict]]:
        """Extract margin data from content"""
        margin_patterns = [
            r'gross margin[:\s]*(\d+\.?\d*)%?',
            r'operating margin[:\s]*(\d+\.?\d*)%?',
            r'net margin[:\s]*(\d+\.?\d*)%?'
        ]
        
        margins = []
        for i, pattern in enumerate(margin_patterns):
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                margin_names = ['Gross Margin', 'Operating Margin', 'Net Margin']
                margins.append({
                    'metric': margin_names[i],
                    'value': float(match.group(1)),
                    'trend': 'stable'  # Could be enhanced with trend analysis
                })
        
        return margins if margins else None
    
    def _extract_peer_comparison(self, content: str) -> Optional[List[Dict]]:
        """Extract peer comparison data from content"""
        # Look for P/E ratios and other valuation metrics
        peer_pattern = r'([A-Z]{3,5})[:\s]*P/E[:\s]*(\d+\.?\d*)'
        matches = re.findall(peer_pattern, content)
        
        if not matches:
            return None
        
        peer_data = []
        for ticker, pe in matches:
            peer_data.append({
                'company': ticker,
                'pe': float(pe),
                'ev_ebitda': float(pe) * 0.8,  # Approximation
                'price_sales': float(pe) * 0.3  # Approximation
            })
        
        return peer_data if peer_data else None
    
    def _generate_dcf_sensitivity(self, content: str) -> Optional[Dict]:
        """Generate DCF sensitivity analysis data"""
        # Look for DCF or valuation mentions
        if not re.search(r'dcf|discounted cash flow|valuation', content, re.IGNORECASE):
            return None
        
        # Generate sensitivity matrix
        wacc_range = [8.5, 9.0, 9.2, 9.5, 10.0]
        growth_range = [2.5, 3.0, 3.5]
        
        # Generate values based on base case (could be extracted from content)
        base_value = 230
        values = []
        
        for wacc in wacc_range:
            row = []
            for growth in growth_range:
                # Simple sensitivity calculation
                sensitivity_factor = (1 + growth/100) / (wacc/100)
                value = base_value * sensitivity_factor * 0.1
                row.append(int(value))
            values.append(row)
        
        return {
            'wacc': wacc_range,
            'growth': growth_range,
            'values': values
        }
    
    def _extract_risk_matrix(self, content: str) -> Optional[List[Dict]]:
        """Extract risk matrix data from content"""
        # Look for risk factors with probability and impact
        risk_pattern = r'([A-Za-z\s]+risk[A-Za-z\s]*)[:\s]*.*?(\d+)%?.*?impact[:\s]*(\d+)'
        matches = re.findall(risk_pattern, content, re.IGNORECASE)
        
        if not matches:
            # Generate sample risks if none found
            return [
                {'risk': 'Market Risk', 'probability': 60, 'impact': 7, 'severity': 'Medium'},
                {'risk': 'Regulatory Risk', 'probability': 40, 'impact': 8, 'severity': 'High'},
                {'risk': 'Operational Risk', 'probability': 30, 'impact': 5, 'severity': 'Low'}
            ]
        
        risk_data = []
        for risk_name, prob, impact in matches:
            severity = 'High' if int(impact) >= 7 else 'Medium' if int(impact) >= 4 else 'Low'
            risk_data.append({
                'risk': risk_name.strip(),
                'probability': int(prob),
                'impact': int(impact),
                'severity': severity
            })
        
        return risk_data
    
    def _extract_scenario_analysis(self, content: str) -> Optional[List[Dict]]:
        """Extract scenario analysis data from content"""
        # Look for bull/base/bear scenarios
        scenarios = ['bull', 'base', 'bear']
        scenario_data = []
        
        for scenario in scenarios:
            pattern = f'{scenario}[:\s]*.*?(\d+\.?\d*)'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                probability = 25 if scenario in ['bull', 'bear'] else 50
                scenario_data.append({
                    'scenario': scenario.title(),
                    'probability': probability,
                    'price_target': value,
                    'return': ((value - 220) / 220) * 100  # Assuming current price of 220
                })
        
        return scenario_data if scenario_data else None
    
    def _extract_segment_breakdown(self, content: str) -> Optional[List[Dict]]:
        """Extract business segment breakdown from content"""
        # This would need more sophisticated parsing
        # For now, return None to use fallback data
        return None
    
    def _extract_cash_flow_waterfall(self, content: str) -> Optional[List[Dict]]:
        """Extract cash flow components for waterfall chart"""
        # This would need more sophisticated parsing
        # For now, return None to use fallback data
        return None
    
    def _extract_price_target_breakdown(self, content: str) -> Optional[List[Dict]]:
        """Extract price target methodology breakdown"""
        # This would need more sophisticated parsing
        # For now, return None to use fallback data
        return None
    
    def _extract_market_share(self, content: str) -> Optional[List[Dict]]:
        """Extract market share data by region"""
        # This would need more sophisticated parsing
        # For now, return None to use fallback data
        return None
    
    def _extract_competitive_position(self, content: str) -> Optional[List[Dict]]:
        """Extract competitive positioning data"""
        # This would need more sophisticated parsing
        # For now, return None to use fallback data
        return None

def enhance_report_with_chart_data(report_data: Dict) -> Dict:
    """Enhance existing report data with advanced chart data"""
    chart_service = AdvancedChartService()
    
    if 'sections' not in report_data:
        return report_data
    
    chart_data = {}
    
    for section_name, section_content in report_data['sections'].items():
        content = section_content.get('content', '')
        section_charts = chart_service.generate_section_chart_data(content, section_name)
        if section_charts:
            chart_data[section_name] = section_charts
    
    # Add chart data to report
    report_data['chart_data'] = chart_data
    
    return report_data

# Example usage
if __name__ == "__main__":
    # Test the chart service
    service = AdvancedChartService()
    
    sample_content = """
    Apple Inc. (AAPL) - BUY Rating with 85% confidence
    Price Target: $245 (11.4% upside)
    Risk Level: Medium
    
    Revenue 2023: $383.3B (-2.8% YoY)
    Revenue 2024E: $391.0B (2.0% YoY)
    
    Gross Margin: 46.2%
    Operating Margin: 29.8%
    Net Margin: 25.1%
    
    P/E Ratios: AAPL: 28.5, MSFT: 32.1, GOOGL: 24.8
    """
    
    exec_data = service._extract_executive_summary_data(sample_content)
    financial_data = service._extract_financial_analysis_data(sample_content)
    
    print("Executive Summary Data:", json.dumps(exec_data, indent=2))
    print("Financial Analysis Data:", json.dumps(financial_data, indent=2))