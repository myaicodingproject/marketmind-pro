import re
from typing import Dict, List, Optional, Any
import json

class DataExtractionService:
    """Intelligent parser for extracting structured data from markdown text"""
    
    def __init__(self):
        self.patterns = {
            'currency': r'\$(\d+(?:\.\d+)?)\s*([BMK]?)',
            'percentage': r'(\d+(?:\.\d+)?)%',
            'year': r'(20\d{2}[E]?)',
            'metric': r'([A-Za-z][A-Za-z\s&/]+?):\s*\$?(\d+(?:\.\d+)?)\s*([%BMK]?)',
            'growth': r'\(([+-]?\d+(?:\.\d+)?)%\s*(?:YoY|growth)?\)',
            'table_row': r'\|([^|]+)\|([^|]+)\|([^|]*)\|?',
            'comparison': r'vs\.?\s+([A-Z]{2,5})\s+(\d+(?:\.\d+)?)',
        }
    
    def extract_from_section(self, section_name: str, content: str) -> Dict[str, Any]:
        """Extract all relevant data from a section"""
        return {
            'tables': self.extract_tables(content),
            'metrics': self.extract_metrics(content),
            'comparisons': self.extract_comparisons(content),
            'projections': self.extract_projections(content),
            'scenarios': self.extract_scenarios(content)
        }
    
    def extract_tables(self, content: str) -> List[Dict]:
        """Extract markdown tables and convert to structured data"""
        tables = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines):
            if '|' in line and i + 1 < len(lines) and '---' in lines[i + 1]:
                # Found table header
                headers = [h.strip() for h in line.split('|')[1:-1]]
                rows = []
                
                # Extract table rows
                for j in range(i + 2, len(lines)):
                    if '|' not in lines[j] or lines[j].strip() == '':
                        break
                    row_data = [cell.strip() for cell in lines[j].split('|')[1:-1]]
                    if len(row_data) == len(headers):
                        row_dict = {}
                        for k, header in enumerate(headers):
                            value = row_data[k] if k < len(row_data) else ''
                            row_dict[header.lower().replace(' ', '_')] = self._parse_value(value)
                        rows.append(row_dict)
                
                if rows:
                    tables.append({'headers': headers, 'rows': rows})
        
        return tables
    
    def extract_metrics(self, content: str) -> List[Dict]:
        """Extract key metrics with values and units"""
        metrics = []
        
        for match in re.finditer(self.patterns['metric'], content, re.IGNORECASE):
            metric_name = match.group(1).strip()
            value = float(match.group(2))
            unit = match.group(3) if match.group(3) else ''
            
            # Look for growth rate nearby
            growth_match = re.search(self.patterns['growth'], 
                                   content[max(0, match.start()-50):match.end()+50])
            growth = float(growth_match.group(1)) if growth_match else None
            
            metrics.append({
                'name': metric_name,
                'value': value,
                'unit': unit,
                'growth': growth
            })
        
        return metrics
    
    def extract_comparisons(self, content: str) -> List[Dict]:
        """Extract peer comparisons and competitive data"""
        comparisons = []
        
        # Extract from tables first
        tables = self.extract_tables(content)
        for table in tables:
            if any('company' in h.lower() or 'ticker' in h.lower() for h in table['headers']):
                for row in table['rows']:
                    if 'company' in row or 'ticker' in row:
                        comparisons.append(row)
        
        # Extract inline comparisons
        for match in re.finditer(self.patterns['comparison'], content):
            ticker = match.group(1)
            value = float(match.group(2))
            comparisons.append({'ticker': ticker, 'value': value})
        
        return comparisons
    
    def extract_projections(self, content: str) -> List[Dict]:
        """Extract forward-looking estimates and projections"""
        projections = []
        
        # Find years with 'E' suffix
        year_matches = re.finditer(self.patterns['year'], content)
        for year_match in year_matches:
            year = year_match.group(1)
            if 'E' in year:
                # Look for associated values nearby
                context = content[max(0, year_match.start()-100):year_match.end()+100]
                
                currency_matches = re.finditer(self.patterns['currency'], context)
                for curr_match in currency_matches:
                    value = float(curr_match.group(1))
                    unit = curr_match.group(2)
                    
                    projections.append({
                        'year': year,
                        'value': value,
                        'unit': unit,
                        'type': 'estimate'
                    })
        
        return projections
    
    def extract_scenarios(self, content: str) -> List[Dict]:
        """Extract bull/base/bear scenarios"""
        scenarios = []
        scenario_keywords = ['bull', 'base', 'bear', 'optimistic', 'pessimistic', 'conservative']
        
        lines = content.lower().split('\n')
        for line in lines:
            for keyword in scenario_keywords:
                if keyword in line:
                    # Extract numerical values from this line
                    currency_matches = re.finditer(self.patterns['currency'], line)
                    percentage_matches = re.finditer(self.patterns['percentage'], line)
                    
                    scenario_data = {'scenario': keyword}
                    
                    for match in currency_matches:
                        scenario_data['price_target'] = float(match.group(1))
                        scenario_data['unit'] = match.group(2)
                    
                    for match in percentage_matches:
                        scenario_data['return'] = float(match.group(1))
                    
                    if len(scenario_data) > 1:  # More than just scenario name
                        scenarios.append(scenario_data)
        
        return scenarios
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse string value to appropriate type"""
        if not value_str or value_str == '-':
            return None
        
        # Try currency
        currency_match = re.match(self.patterns['currency'], value_str)
        if currency_match:
            base_value = float(currency_match.group(1))
            unit = currency_match.group(2)
            multiplier = {'B': 1e9, 'M': 1e6, 'K': 1e3}.get(unit, 1)
            return base_value * multiplier
        
        # Try percentage
        percentage_match = re.match(self.patterns['percentage'], value_str)
        if percentage_match:
            return float(percentage_match.group(1))
        
        # Try plain number
        try:
            return float(value_str.replace(',', ''))
        except ValueError:
            return value_str.strip()
    
    def generate_chart_data(self, section_name: str, extracted_data: Dict) -> Dict[str, Any]:
        """Generate chart-ready data structure from extracted data"""
        chart_data = {}
        
        if section_name == 'financial_analysis':
            chart_data = self._generate_financial_charts(extracted_data)
        elif section_name == 'valuation_analysis':
            chart_data = self._generate_valuation_charts(extracted_data)
        elif section_name == 'risk_assessment':
            chart_data = self._generate_risk_charts(extracted_data)
        elif section_name == 'executive_summary':
            chart_data = self._generate_summary_charts(extracted_data)
        
        return chart_data
    
    def _generate_financial_charts(self, data: Dict) -> Dict:
        """Generate financial analysis chart data"""
        charts = {}
        
        # Revenue trend from projections
        if data['projections']:
            revenue_data = [p for p in data['projections'] if 'revenue' in str(p).lower()]
            if revenue_data:
                charts['revenue_trend'] = revenue_data
        
        # Metrics for margin analysis
        if data['metrics']:
            margin_metrics = [m for m in data['metrics'] if 'margin' in m['name'].lower()]
            if margin_metrics:
                charts['margins'] = margin_metrics
        
        return charts
    
    def _generate_valuation_charts(self, data: Dict) -> Dict:
        """Generate valuation analysis chart data"""
        charts = {}
        
        # Peer comparison from comparisons
        if data['comparisons']:
            charts['peer_comparison'] = data['comparisons']
        
        # Scenarios for price targets
        if data['scenarios']:
            charts['scenarios'] = data['scenarios']
        
        return charts
    
    def _generate_risk_charts(self, data: Dict) -> Dict:
        """Generate risk assessment chart data"""
        charts = {}
        
        # Risk scenarios
        if data['scenarios']:
            charts['risk_scenarios'] = data['scenarios']
        
        return charts
    
    def _generate_summary_charts(self, data: Dict) -> Dict:
        """Generate executive summary chart data"""
        charts = {}
        
        # Key metrics
        if data['metrics']:
            charts['key_metrics'] = data['metrics'][:5]  # Top 5 metrics
        
        return charts