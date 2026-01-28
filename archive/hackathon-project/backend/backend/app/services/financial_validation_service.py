"""
Financial Data Validation and Error Handling Service
"""
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import re
import pandas as pd
from pydantic import BaseModel, validator
import numpy as np

logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom validation error"""
    pass

class DataQualityMetrics(BaseModel):
    """Data quality assessment metrics"""
    completeness_score: float  # 0-100
    accuracy_score: float      # 0-100
    consistency_score: float   # 0-100
    timeliness_score: float    # 0-100
    overall_score: float       # 0-100
    issues: List[str] = []
    warnings: List[str] = []

class FinancialDataValidator:
    """Validates and cleans financial data from various sources"""
    
    def __init__(self):
        self.symbol_pattern = re.compile(r'^[A-Z]{1,5}$')
        self.required_price_fields = ['price', 'volume', 'timestamp']
        self.required_company_fields = ['symbol', 'name', 'sector']
        
    def validate_symbol(self, symbol: str) -> bool:
        """Validate stock symbol format"""
        if not symbol or not isinstance(symbol, str):
            return False
        
        symbol = symbol.upper().strip()
        return bool(self.symbol_pattern.match(symbol))
    
    def validate_price_data(self, price_data: Dict) -> Dict[str, Any]:
        """Validate and clean price data"""
        validation_result = {
            'is_valid': True,
            'cleaned_data': {},
            'issues': [],
            'warnings': []
        }
        
        try:
            # Check required fields
            missing_fields = [field for field in self.required_price_fields 
                            if field not in price_data or price_data[field] is None]
            
            if missing_fields:
                validation_result['issues'].append(f"Missing required fields: {missing_fields}")
                validation_result['is_valid'] = False
                return validation_result
            
            cleaned_data = {}
            
            # Validate and clean price
            price = price_data.get('price')
            if isinstance(price, (int, float)) and price > 0:
                cleaned_data['price'] = float(price)
            else:
                validation_result['issues'].append("Invalid price value")
                validation_result['is_valid'] = False
            
            # Validate and clean volume
            volume = price_data.get('volume')
            if isinstance(volume, (int, float)) and volume >= 0:
                cleaned_data['volume'] = int(volume)
            else:
                validation_result['warnings'].append("Invalid or missing volume data")
                cleaned_data['volume'] = 0
            
            # Validate change and change_percent
            change = price_data.get('change')
            if isinstance(change, (int, float)):
                cleaned_data['change'] = float(change)
            
            change_percent = price_data.get('change_percent')
            if isinstance(change_percent, (int, float)):
                cleaned_data['change_percent'] = float(change_percent)
            
            # Validate market cap
            market_cap = price_data.get('market_cap')
            if isinstance(market_cap, (int, float)) and market_cap > 0:
                cleaned_data['market_cap'] = float(market_cap)
            
            # Validate timestamp
            timestamp = price_data.get('timestamp')
            if isinstance(timestamp, datetime):
                cleaned_data['timestamp'] = timestamp
            elif isinstance(timestamp, str):
                try:
                    cleaned_data['timestamp'] = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    validation_result['warnings'].append("Invalid timestamp format")
                    cleaned_data['timestamp'] = datetime.now()
            else:
                cleaned_data['timestamp'] = datetime.now()
            
            validation_result['cleaned_data'] = cleaned_data
            
        except Exception as e:
            logger.error(f"Error validating price data: {e}")
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def validate_financial_metrics(self, metrics: Dict) -> Dict[str, Any]:
        """Validate financial metrics and ratios"""
        validation_result = {
            'is_valid': True,
            'cleaned_data': {},
            'issues': [],
            'warnings': []
        }
        
        try:
            cleaned_data = {}
            
            # Define reasonable ranges for financial metrics
            metric_ranges = {
                'pe_ratio': (0, 1000),
                'pb_ratio': (0, 100),
                'debt_to_equity': (0, 10),
                'roe': (-100, 100),
                'roa': (-100, 100),
                'profit_margin': (-100, 100),
                'operating_margin': (-100, 100),
                'gross_margin': (-100, 100)
            }
            
            for metric, value in metrics.items():
                if value is None or value == '':
                    continue
                
                try:
                    numeric_value = float(value)
                    
                    # Check if value is within reasonable range
                    if metric in metric_ranges:
                        min_val, max_val = metric_ranges[metric]
                        if not (min_val <= numeric_value <= max_val):
                            validation_result['warnings'].append(
                                f"{metric} value {numeric_value} outside expected range [{min_val}, {max_val}]"
                            )
                    
                    cleaned_data[metric] = numeric_value
                    
                except (ValueError, TypeError):
                    validation_result['warnings'].append(f"Could not convert {metric} to numeric value")
            
            validation_result['cleaned_data'] = cleaned_data
            
        except Exception as e:
            logger.error(f"Error validating financial metrics: {e}")
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def validate_historical_data(self, hist_data: pd.DataFrame) -> Dict[str, Any]:
        """Validate historical price data"""
        validation_result = {
            'is_valid': True,
            'cleaned_data': None,
            'issues': [],
            'warnings': []
        }
        
        try:
            if hist_data.empty:
                validation_result['is_valid'] = False
                validation_result['issues'].append("Historical data is empty")
                return validation_result
            
            # Check required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            missing_columns = [col for col in required_columns if col not in hist_data.columns]
            
            if missing_columns:
                validation_result['issues'].append(f"Missing columns: {missing_columns}")
                validation_result['is_valid'] = False
                return validation_result
            
            cleaned_data = hist_data.copy()
            
            # Remove rows with all NaN values
            cleaned_data = cleaned_data.dropna(how='all')
            
            # Validate price relationships (High >= Low, etc.)
            invalid_prices = (
                (cleaned_data['High'] < cleaned_data['Low']) |
                (cleaned_data['Close'] < 0) |
                (cleaned_data['Volume'] < 0)
            )
            
            if invalid_prices.any():
                validation_result['warnings'].append(
                    f"Found {invalid_prices.sum()} rows with invalid price relationships"
                )
                # Remove invalid rows
                cleaned_data = cleaned_data[~invalid_prices]
            
            # Check for extreme price movements (>50% in one day)
            if len(cleaned_data) > 1:
                price_changes = cleaned_data['Close'].pct_change().abs()
                extreme_changes = price_changes > 0.5
                
                if extreme_changes.any():
                    validation_result['warnings'].append(
                        f"Found {extreme_changes.sum()} days with extreme price movements (>50%)"
                    )
            
            # Fill missing values with forward fill
            cleaned_data = cleaned_data.fillna(method='ffill')
            
            validation_result['cleaned_data'] = cleaned_data
            
        except Exception as e:
            logger.error(f"Error validating historical data: {e}")
            validation_result['is_valid'] = False
            validation_result['issues'].append(f"Validation error: {str(e)}")
        
        return validation_result
    
    def assess_data_quality(self, data: Dict, data_type: str) -> DataQualityMetrics:
        """Assess overall data quality"""
        try:
            completeness_score = self._calculate_completeness_score(data, data_type)
            accuracy_score = self._calculate_accuracy_score(data, data_type)
            consistency_score = self._calculate_consistency_score(data, data_type)
            timeliness_score = self._calculate_timeliness_score(data, data_type)
            
            overall_score = (completeness_score + accuracy_score + consistency_score + timeliness_score) / 4
            
            issues = []
            warnings = []
            
            if completeness_score < 70:
                issues.append("Low data completeness")
            if accuracy_score < 70:
                issues.append("Low data accuracy")
            if consistency_score < 70:
                warnings.append("Data consistency issues detected")
            if timeliness_score < 70:
                warnings.append("Data may be stale")
            
            return DataQualityMetrics(
                completeness_score=completeness_score,
                accuracy_score=accuracy_score,
                consistency_score=consistency_score,
                timeliness_score=timeliness_score,
                overall_score=overall_score,
                issues=issues,
                warnings=warnings
            )
            
        except Exception as e:
            logger.error(f"Error assessing data quality: {e}")
            return DataQualityMetrics(
                completeness_score=0,
                accuracy_score=0,
                consistency_score=0,
                timeliness_score=0,
                overall_score=0,
                issues=[f"Quality assessment failed: {str(e)}"]
            )
    
    def _calculate_completeness_score(self, data: Dict, data_type: str) -> float:
        """Calculate data completeness score"""
        if data_type == 'price':
            required_fields = self.required_price_fields
        elif data_type == 'company':
            required_fields = self.required_company_fields
        else:
            required_fields = []
        
        if not required_fields:
            return 100.0
        
        present_fields = sum(1 for field in required_fields if field in data and data[field] is not None)
        return (present_fields / len(required_fields)) * 100
    
    def _calculate_accuracy_score(self, data: Dict, data_type: str) -> float:
        """Calculate data accuracy score"""
        # This is a simplified accuracy assessment
        # In production, you'd implement more sophisticated accuracy checks
        
        accuracy_issues = 0
        total_checks = 0
        
        if data_type == 'price':
            # Check if price is reasonable (not negative, not extremely high)
            price = data.get('price')
            if price is not None:
                total_checks += 1
                if price <= 0 or price > 100000:  # Arbitrary upper limit
                    accuracy_issues += 1
            
            # Check volume
            volume = data.get('volume')
            if volume is not None:
                total_checks += 1
                if volume < 0:
                    accuracy_issues += 1
        
        if total_checks == 0:
            return 100.0
        
        return ((total_checks - accuracy_issues) / total_checks) * 100
    
    def _calculate_consistency_score(self, data: Dict, data_type: str) -> float:
        """Calculate data consistency score"""
        # This would implement cross-field consistency checks
        # For now, return a default score
        return 90.0
    
    def _calculate_timeliness_score(self, data: Dict, data_type: str) -> float:
        """Calculate data timeliness score"""
        timestamp = data.get('timestamp') or data.get('last_updated')
        
        if not timestamp:
            return 50.0  # No timestamp available
        
        if isinstance(timestamp, str):
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            except:
                return 50.0
        
        if isinstance(timestamp, datetime):
            age_hours = (datetime.now() - timestamp.replace(tzinfo=None)).total_seconds() / 3600
            
            # Score based on data age
            if age_hours < 1:
                return 100.0
            elif age_hours < 24:
                return 90.0
            elif age_hours < 168:  # 1 week
                return 70.0
            else:
                return 30.0
        
        return 50.0

class FinancialDataErrorHandler:
    """Handles errors and provides fallback mechanisms for financial data"""
    
    def __init__(self):
        self.validator = FinancialDataValidator()
    
    async def handle_api_error(self, error: Exception, source: str, symbol: str) -> Dict[str, Any]:
        """Handle API errors and provide fallback data if possible"""
        error_info = {
            'source': source,
            'symbol': symbol,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'timestamp': datetime.now().isoformat(),
            'fallback_data': None,
            'retry_recommended': False
        }
        
        # Determine if retry is recommended based on error type
        if 'timeout' in str(error).lower() or 'connection' in str(error).lower():
            error_info['retry_recommended'] = True
        elif 'rate limit' in str(error).lower() or 'quota' in str(error).lower():
            error_info['retry_recommended'] = True
            error_info['retry_delay'] = 60  # seconds
        
        logger.error(f"API error from {source} for {symbol}: {error}")
        
        return error_info
    
    def merge_data_sources(self, data_sources: Dict[str, Any]) -> Dict[str, Any]:
        """Merge data from multiple sources, prioritizing by reliability"""
        merged_data = {}
        
        # Define source priority (higher number = higher priority)
        source_priority = {
            'yahoo_finance': 3,
            'alpha_vantage': 2,
            'sec_edgar': 1
        }
        
        # Sort sources by priority
        sorted_sources = sorted(data_sources.items(), 
                              key=lambda x: source_priority.get(x[0], 0), 
                              reverse=True)
        
        for source_name, source_data in sorted_sources:
            if isinstance(source_data, Exception) or not source_data:
                continue
            
            # Merge non-null values, prioritizing higher-priority sources
            for key, value in source_data.items():
                if value is not None and (key not in merged_data or merged_data[key] is None):
                    merged_data[key] = value
        
        return merged_data

# Global instances
financial_validator = FinancialDataValidator()
financial_error_handler = FinancialDataErrorHandler()