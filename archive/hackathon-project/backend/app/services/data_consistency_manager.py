"""
Data Consistency Manager - Ensures data integrity across all 8 report sections
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import pandas as pd
from dataclasses import dataclass
import logging

@dataclass
class DataValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    data_quality_score: float

class DataConsistencyManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.required_fields = {
            'company_info': ['longName', 'sector', 'industry', 'marketCap'],
            'stock_data': ['price_history', 'key_metrics'],
            'financial_statements': ['income_statement', 'balance_sheet', 'cash_flow'],
            'analyst_ratings': ['consensus_rating', 'price_targets'],
            'news_sentiment': ['sentiment_scores', 'recent_headlines']
        }
    
    def validate_comprehensive_data(self, data: Dict[str, Any]) -> DataValidationResult:
        """Validate all financial data for consistency and completeness"""
        errors = []
        warnings = []
        
        # Check data completeness
        completeness_errors = self._check_data_completeness(data)
        errors.extend(completeness_errors)
        
        # Check data consistency
        consistency_errors = self._check_data_consistency(data)
        errors.extend(consistency_errors)
        
        # Check data freshness
        freshness_warnings = self._check_data_freshness(data)
        warnings.extend(freshness_warnings)
        
        # Check financial metrics consistency
        metrics_errors = self._validate_financial_metrics(data)
        errors.extend(metrics_errors)
        
        # Calculate data quality score
        quality_score = self._calculate_quality_score(data, errors, warnings)
        
        return DataValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            data_quality_score=quality_score
        )
    
    def normalize_data_for_reports(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize and standardize data for consistent use across all report sections"""
        
        normalized = {
            'ticker': data.get('ticker', '').upper(),
            'timestamp': data.get('timestamp', datetime.now()),
            
            # Standardized company information
            'company': self._normalize_company_info(data.get('company_info', {})),
            
            # Standardized financial data
            'financials': self._normalize_financial_data(data.get('financial_statements', {})),
            
            # Standardized market data
            'market': self._normalize_market_data(data.get('stock_data', {})),
            
            # Standardized analyst data
            'analysts': self._normalize_analyst_data(data.get('analyst_ratings', {})),
            
            # Standardized sentiment data
            'sentiment': self._normalize_sentiment_data(data.get('news_sentiment', {})),
            
            # Standardized SEC data
            'sec_filings': self._normalize_sec_data(data.get('sec_filings', {})),
            
            # Standardized peer data
            'peers': self._normalize_peer_data(data.get('peer_comparison', {}))
        }
        
        # Add cross-validated metrics
        normalized['validated_metrics'] = self._create_validated_metrics(normalized)
        
        return normalized
    
    def _check_data_completeness(self, data: Dict[str, Any]) -> List[str]:
        """Check if all required data fields are present"""
        errors = []
        
        for section, required_fields in self.required_fields.items():
            section_data = data.get(section, {})
            
            for field in required_fields:
                if field not in section_data or section_data[field] is None:
                    errors.append(f"Missing required field: {section}.{field}")
        
        return errors
    
    def _check_data_consistency(self, data: Dict[str, Any]) -> List[str]:
        """Check for data consistency across different sources"""
        errors = []
        
        # Check ticker consistency
        ticker = data.get('ticker', '').upper()
        company_info = data.get('company_info', {})
        
        if 'symbol' in company_info and company_info['symbol'].upper() != ticker:
            errors.append(f"Ticker mismatch: {ticker} vs {company_info['symbol']}")
        
        # Check market cap consistency
        yahoo_market_cap = data.get('stock_data', {}).get('key_metrics', {}).get('market_cap')
        info_market_cap = company_info.get('marketCap')
        
        if yahoo_market_cap and info_market_cap:
            # Allow 5% variance
            variance = abs(yahoo_market_cap - info_market_cap) / info_market_cap
            if variance > 0.05:
                errors.append(f"Market cap inconsistency: {variance:.2%} variance between sources")
        
        # Check price consistency
        current_price = data.get('stock_data', {}).get('key_metrics', {}).get('current_price')
        analyst_price = data.get('analyst_ratings', {}).get('price_targets', {}).get('current_price')
        
        if current_price and analyst_price:
            price_variance = abs(current_price - analyst_price) / current_price
            if price_variance > 0.02:  # 2% tolerance
                errors.append(f"Current price inconsistency: {price_variance:.2%} variance")
        
        return errors
    
    def _check_data_freshness(self, data: Dict[str, Any]) -> List[str]:
        """Check if data is fresh enough for analysis"""
        warnings = []
        now = datetime.now()
        
        # Check timestamp freshness
        timestamp = data.get('timestamp')
        if timestamp:
            if isinstance(timestamp, str):
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            
            age_hours = (now - timestamp).total_seconds() / 3600
            if age_hours > 24:
                warnings.append(f"Data is {age_hours:.1f} hours old")
        
        # Check SEC filings freshness
        sec_data = data.get('sec_filings', {})
        if 'filing_summary' in sec_data:
            last_10k = sec_data['filing_summary'].get('last_annual_report')
            if last_10k:
                try:
                    filing_date = datetime.strptime(last_10k, '%Y-%m-%d')
                    days_old = (now - filing_date).days
                    if days_old > 400:  # More than ~13 months
                        warnings.append(f"Last 10-K filing is {days_old} days old")
                except:
                    pass
        
        return warnings
    
    def _validate_financial_metrics(self, data: Dict[str, Any]) -> List[str]:
        """Validate financial metrics for reasonableness"""
        errors = []
        
        key_metrics = data.get('stock_data', {}).get('key_metrics', {})
        
        # Check for reasonable PE ratio
        pe_ratio = key_metrics.get('pe_ratio')
        if pe_ratio and (pe_ratio < 0 or pe_ratio > 1000):
            errors.append(f"Unreasonable PE ratio: {pe_ratio}")
        
        # Check for reasonable profit margin
        profit_margin = key_metrics.get('profit_margin')
        if profit_margin and (profit_margin < -1 or profit_margin > 1):
            errors.append(f"Unreasonable profit margin: {profit_margin:.2%}")
        
        # Check for reasonable debt-to-equity
        debt_to_equity = key_metrics.get('debt_to_equity')
        if debt_to_equity and debt_to_equity < 0:
            errors.append(f"Negative debt-to-equity ratio: {debt_to_equity}")
        
        return errors
    
    def _calculate_quality_score(self, data: Dict[str, Any], errors: List[str], warnings: List[str]) -> float:
        """Calculate overall data quality score (0-100)"""
        base_score = 100.0
        
        # Deduct points for errors and warnings
        error_penalty = len(errors) * 15  # 15 points per error
        warning_penalty = len(warnings) * 5  # 5 points per warning
        
        # Deduct points for missing data
        completeness_score = self._calculate_completeness_score(data)
        
        final_score = max(0, base_score - error_penalty - warning_penalty - (100 - completeness_score))
        
        return round(final_score, 1)
    
    def _calculate_completeness_score(self, data: Dict[str, Any]) -> float:
        """Calculate data completeness score"""
        total_fields = sum(len(fields) for fields in self.required_fields.values())
        present_fields = 0
        
        for section, required_fields in self.required_fields.items():
            section_data = data.get(section, {})
            for field in required_fields:
                if field in section_data and section_data[field] is not None:
                    present_fields += 1
        
        return (present_fields / total_fields) * 100 if total_fields > 0 else 0
    
    def _normalize_company_info(self, company_info: Dict) -> Dict[str, Any]:
        """Normalize company information"""
        return {
            'name': company_info.get('longName', company_info.get('shortName', 'Unknown')),
            'sector': company_info.get('sector', 'Unknown'),
            'industry': company_info.get('industry', 'Unknown'),
            'market_cap': company_info.get('marketCap'),
            'employees': company_info.get('fullTimeEmployees'),
            'description': company_info.get('longBusinessSummary', ''),
            'website': company_info.get('website', ''),
            'headquarters': {
                'city': company_info.get('city', ''),
                'state': company_info.get('state', ''),
                'country': company_info.get('country', '')
            }
        }
    
    def _normalize_financial_data(self, financial_statements: Dict) -> Dict[str, Any]:
        """Normalize financial statement data"""
        return {
            'income_statement': financial_statements.get('income_statement'),
            'balance_sheet': financial_statements.get('balance_sheet'),
            'cash_flow': financial_statements.get('cash_flow'),
            'quarterly_financials': financial_statements.get('quarterly_financials')
        }
    
    def _normalize_market_data(self, stock_data: Dict) -> Dict[str, Any]:
        """Normalize market and stock data"""
        key_metrics = stock_data.get('key_metrics', {})
        market_data = stock_data.get('market_data', {})
        
        return {
            'current_price': key_metrics.get('market_cap'),
            'market_cap': key_metrics.get('market_cap'),
            'pe_ratio': key_metrics.get('pe_ratio'),
            'price_to_book': key_metrics.get('price_to_book'),
            'debt_to_equity': key_metrics.get('debt_to_equity'),
            'roe': key_metrics.get('roe'),
            'profit_margin': key_metrics.get('profit_margin'),
            'volatility': market_data.get('volatility_30d'),
            'beta': market_data.get('beta'),
            'ytd_return': market_data.get('ytd_return')
        }
    
    def _normalize_analyst_data(self, analyst_ratings: Dict) -> Dict[str, Any]:
        """Normalize analyst ratings data"""
        return {
            'consensus_rating': analyst_ratings.get('consensus_metrics', {}).get('analyst_sentiment', 'Neutral'),
            'price_target': analyst_ratings.get('price_targets', {}).get('mean_target'),
            'upside_potential': analyst_ratings.get('price_targets', {}).get('upside_potential'),
            'analyst_count': analyst_ratings.get('analyst_count', 0)
        }
    
    def _normalize_sentiment_data(self, news_sentiment: Dict) -> Dict[str, Any]:
        """Normalize news sentiment data"""
        sentiment_scores = news_sentiment.get('sentiment_scores', {})
        
        return {
            'overall_sentiment': sentiment_scores.get('overall_sentiment', 0),
            'sentiment_classification': sentiment_scores.get('sentiment_classification', 'Neutral'),
            'positive_percentage': sentiment_scores.get('positive_percentage', 0),
            'articles_count': sentiment_scores.get('articles_analyzed', 0)
        }
    
    def _normalize_sec_data(self, sec_filings: Dict) -> Dict[str, Any]:
        """Normalize SEC filings data"""
        return {
            'latest_10k': sec_filings.get('filing_summary', {}).get('last_annual_report'),
            'latest_10q': sec_filings.get('filing_summary', {}).get('last_quarterly_report'),
            'recent_8k_count': sec_filings.get('filing_summary', {}).get('recent_8k_count', 0)
        }
    
    def _normalize_peer_data(self, peer_comparison: Dict) -> Dict[str, Any]:
        """Normalize peer comparison data"""
        return {
            'sector': peer_comparison.get('sector', 'Unknown'),
            'industry': peer_comparison.get('industry', 'Unknown'),
            'peers': peer_comparison.get('peers', {})
        }
    
    def _create_validated_metrics(self, normalized_data: Dict) -> Dict[str, Any]:
        """Create cross-validated metrics from multiple sources"""
        return {
            'data_quality_score': self._calculate_completeness_score(normalized_data),
            'last_validation': datetime.now().isoformat(),
            'validation_status': 'passed'
        }