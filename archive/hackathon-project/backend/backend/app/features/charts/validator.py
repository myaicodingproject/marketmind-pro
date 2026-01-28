"""
Chart Data Validation - Validates and sanitizes data for chart generation
"""
from typing import Dict, List, Any, Optional, Tuple
import logging
from datetime import datetime
import json

logger = logging.getLogger(__name__)

class ChartDataValidator:
    """Validates financial data before chart processing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def validate_financial_data(self, data: Dict) -> Tuple[bool, List[str], Dict]:
        """
        Validate financial data structure and content
        Returns: (is_valid, errors, cleaned_data)
        """
        errors = []
        cleaned_data = {}
        
        try:
            # Validate overview data
            if 'overview' in data:
                overview_valid, overview_errors, clean_overview = self._validate_overview(data['overview'])
                if overview_errors:
                    errors.extend([f"Overview: {err}" for err in overview_errors])
                cleaned_data['overview'] = clean_overview
            
            # Validate income statement
            if 'income_statement' in data:
                income_valid, income_errors, clean_income = self._validate_income_statement(data['income_statement'])
                if income_errors:
                    errors.extend([f"Income Statement: {err}" for err in income_errors])
                cleaned_data['income_statement'] = clean_income
            
            # Validate balance sheet
            if 'balance_sheet' in data:
                balance_valid, balance_errors, clean_balance = self._validate_balance_sheet(data['balance_sheet'])
                if balance_errors:
                    errors.extend([f"Balance Sheet: {err}" for err in balance_errors])
                cleaned_data['balance_sheet'] = clean_balance
            
            # Validate cash flow
            if 'cash_flow' in data:
                cash_valid, cash_errors, clean_cash = self._validate_cash_flow(data['cash_flow'])
                if cash_errors:
                    errors.extend([f"Cash Flow: {err}" for err in cash_errors])
                cleaned_data['cash_flow'] = clean_cash
            
            # Validate market data
            if 'daily_prices' in data:
                market_valid, market_errors, clean_market = self._validate_market_data(data['daily_prices'])
                if market_errors:
                    errors.extend([f"Market Data: {err}" for err in market_errors])
                cleaned_data['daily_prices'] = clean_market
            
            is_valid = len(errors) == 0
            return is_valid, errors, cleaned_data
            
        except Exception as e:
            self.logger.error(f"Validation error: {e}")
            return False, [f"Validation exception: {str(e)}"], {}
    
    def _validate_overview(self, overview: Dict) -> Tuple[bool, List[str], Dict]:
        """Validate company overview data"""
        errors = []
        cleaned = {}
        
        required_fields = ['Symbol', 'Name']
        numeric_fields = [
            'PERatio', 'PriceToBookRatio', 'PriceToSalesRatioTTM', 
            'ReturnOnEquityTTM', 'Beta', 'DividendYield', 'DebtToEquityRatio',
            'CurrentRatio', 'EVToEBITDA', 'PEGRatio'
        ]
        
        # Check required fields
        for field in required_fields:
            if field not in overview or not overview[field]:
                errors.append(f"Missing required field: {field}")
            else:
                cleaned[field] = str(overview[field]).strip()
        
        # Validate and clean numeric fields
        for field in numeric_fields:
            if field in overview:
                cleaned_value = self._clean_numeric_value(overview[field])
                if cleaned_value is not None:
                    cleaned[field] = cleaned_value
                else:
                    self.logger.warning(f"Invalid numeric value for {field}: {overview[field]}")
        
        # Copy other string fields
        string_fields = ['Exchange', 'Sector', 'Industry', 'Country', 'Currency', 'Description']
        for field in string_fields:
            if field in overview and overview[field]:
                cleaned[field] = str(overview[field]).strip()
        
        return len(errors) == 0, errors, cleaned
    
    def _validate_income_statement(self, income_data: Dict) -> Tuple[bool, List[str], Dict]:
        """Validate income statement data"""
        errors = []
        cleaned = {}
        
        # Validate annual reports
        if 'annualReports' in income_data:
            annual_valid, annual_errors, clean_annual = self._validate_financial_reports(
                income_data['annualReports'], 'annual'
            )
            if annual_errors:
                errors.extend(annual_errors)
            cleaned['annualReports'] = clean_annual
        
        # Validate quarterly reports
        if 'quarterlyReports' in income_data:
            quarterly_valid, quarterly_errors, clean_quarterly = self._validate_financial_reports(
                income_data['quarterlyReports'], 'quarterly'
            )
            if quarterly_errors:
                errors.extend(quarterly_errors)
            cleaned['quarterlyReports'] = clean_quarterly
        
        return len(errors) == 0, errors, cleaned
    
    def _validate_balance_sheet(self, balance_data: Dict) -> Tuple[bool, List[str], Dict]:
        """Validate balance sheet data"""
        return self._validate_income_statement(balance_data)  # Same structure
    
    def _validate_cash_flow(self, cash_data: Dict) -> Tuple[bool, List[str], Dict]:
        """Validate cash flow data"""
        return self._validate_income_statement(cash_data)  # Same structure
    
    def _validate_financial_reports(self, reports: List[Dict], report_type: str) -> Tuple[bool, List[str], List[Dict]]:
        """Validate financial reports (annual/quarterly)"""
        errors = []
        cleaned_reports = []
        
        if not isinstance(reports, list):
            errors.append(f"Reports must be a list, got {type(reports)}")
            return False, errors, []
        
        for i, report in enumerate(reports):
            if not isinstance(report, dict):
                errors.append(f"Report {i} must be a dictionary")
                continue
            
            cleaned_report = {}
            
            # Validate fiscal date
            if 'fiscalDateEnding' in report:
                date_valid = self._validate_date(report['fiscalDateEnding'])
                if date_valid:
                    cleaned_report['fiscalDateEnding'] = report['fiscalDateEnding']
                else:
                    errors.append(f"Invalid fiscal date in report {i}: {report['fiscalDateEnding']}")
            
            # Clean numeric fields
            numeric_fields = [
                'totalRevenue', 'grossProfit', 'operatingIncome', 'netIncome',
                'totalAssets', 'totalLiabilities', 'totalShareholderEquity',
                'operatingCashflow', 'capitalExpenditures', 'freeCashFlow'
            ]
            
            for field in numeric_fields:
                if field in report:
                    cleaned_value = self._clean_numeric_value(report[field])
                    if cleaned_value is not None:
                        cleaned_report[field] = cleaned_value
            
            if cleaned_report:  # Only add if we have some valid data
                cleaned_reports.append(cleaned_report)
        
        return len(errors) == 0, errors, cleaned_reports
    
    def _validate_market_data(self, market_data: Dict) -> Tuple[bool, List[str], Dict]:
        """Validate market/price data"""
        errors = []
        cleaned = {}
        
        if 'Time Series (Daily)' in market_data:
            time_series = market_data['Time Series (Daily)']
            cleaned_series = {}
            
            for date, price_data in time_series.items():
                # Validate date format
                if not self._validate_date(date):
                    errors.append(f"Invalid date format: {date}")
                    continue
                
                # Clean price data
                cleaned_price_data = {}
                price_fields = ['1. open', '2. high', '3. low', '4. close', '5. volume']
                
                for field in price_fields:
                    if field in price_data:
                        cleaned_value = self._clean_numeric_value(price_data[field])
                        if cleaned_value is not None:
                            cleaned_price_data[field] = cleaned_value
                
                if cleaned_price_data:
                    cleaned_series[date] = cleaned_price_data
            
            cleaned['Time Series (Daily)'] = cleaned_series
        
        return len(errors) == 0, errors, cleaned
    
    def _clean_numeric_value(self, value: Any) -> Optional[float]:
        """Clean and validate numeric values"""
        if value is None or value == 'None' or value == '':
            return None
        
        try:
            # Handle string representations
            if isinstance(value, str):
                # Remove common formatting
                cleaned = value.replace(',', '').replace('$', '').replace('%', '').strip()
                if cleaned == '' or cleaned.lower() in ['none', 'null', 'n/a']:
                    return None
                return float(cleaned)
            
            # Handle numeric types
            if isinstance(value, (int, float)):
                if value == 0:
                    return 0.0
                return float(value)
            
            return None
            
        except (ValueError, TypeError):
            return None
    
    def _validate_date(self, date_str: str) -> bool:
        """Validate date string format"""
        if not isinstance(date_str, str):
            return False
        
        # Common date formats
        formats = ['%Y-%m-%d', '%Y-%m', '%Y']
        
        for fmt in formats:
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                continue
        
        return False
    
    def validate_chart_config(self, config: Dict) -> Tuple[bool, List[str]]:
        """Validate Chart.js configuration"""
        errors = []
        
        # Check required fields
        if 'type' not in config:
            errors.append("Chart type is required")
        elif config['type'] not in ['line', 'bar', 'radar', 'pie', 'doughnut', 'scatter']:
            errors.append(f"Invalid chart type: {config['type']}")
        
        if 'data' not in config:
            errors.append("Chart data is required")
        else:
            data_valid, data_errors = self._validate_chart_data(config['data'])
            errors.extend(data_errors)
        
        if 'options' not in config:
            errors.append("Chart options are required")
        
        return len(errors) == 0, errors
    
    def _validate_chart_data(self, data: Dict) -> Tuple[bool, List[str]]:
        """Validate chart data structure"""
        errors = []
        
        if 'labels' not in data:
            errors.append("Chart labels are required")
        elif not isinstance(data['labels'], list):
            errors.append("Chart labels must be a list")
        
        if 'datasets' not in data:
            errors.append("Chart datasets are required")
        elif not isinstance(data['datasets'], list):
            errors.append("Chart datasets must be a list")
        else:
            for i, dataset in enumerate(data['datasets']):
                if not isinstance(dataset, dict):
                    errors.append(f"Dataset {i} must be a dictionary")
                    continue
                
                if 'data' not in dataset:
                    errors.append(f"Dataset {i} missing data field")
                elif not isinstance(dataset['data'], list):
                    errors.append(f"Dataset {i} data must be a list")
                
                if 'label' not in dataset:
                    errors.append(f"Dataset {i} missing label field")
        
        return len(errors) == 0, errors
    
    def sanitize_for_json(self, data: Any) -> Any:
        """Sanitize data for JSON serialization"""
        if isinstance(data, dict):
            return {k: self.sanitize_for_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.sanitize_for_json(item) for item in data]
        elif isinstance(data, (int, float)):
            # Handle NaN and infinity
            if str(data).lower() in ['nan', 'inf', '-inf']:
                return None
            return data
        elif isinstance(data, str):
            return data
        elif data is None:
            return None
        else:
            return str(data)

def validate_chart_data(financial_data: Dict, chart_type: str = None) -> Tuple[bool, List[str], Dict]:
    """
    Main validation function for chart data
    """
    validator = ChartDataValidator()
    return validator.validate_financial_data(financial_data)