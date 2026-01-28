import asyncio
import re
from typing import Dict, List, Any
from datetime import datetime
from .models import ValidationResult, ValidationLevel, ValidationStatus, ReportSection, QualityMetrics

class AgentLevelValidator:
    """Validates individual report sections for completeness, data availability, format compliance, and chart validity"""
    
    def __init__(self):
        self.min_word_counts = {
            ReportSection.EXECUTIVE_SUMMARY: 800,
            ReportSection.COMPANY_ANALYSIS: 2000,
            ReportSection.FINANCIAL_ANALYSIS: 3200,
            ReportSection.VALUATION_ANALYSIS: 2400,
            ReportSection.RISK_ASSESSMENT: 1200,
            ReportSection.INVESTMENT_THESIS: 800,
            ReportSection.TECHNICAL_ANALYSIS: 1000,
            ReportSection.MARKET_ANALYSIS: 1500
        }
        
        self.required_fields = {
            ReportSection.EXECUTIVE_SUMMARY: ['price_target', 'rating', 'key_metrics', 'investment_highlights'],
            ReportSection.FINANCIAL_ANALYSIS: ['revenue_data', 'profit_margins', 'growth_rates', 'financial_ratios'],
            ReportSection.VALUATION_ANALYSIS: ['dcf_valuation', 'peer_comparison', 'price_targets', 'valuation_multiples'],
            ReportSection.RISK_ASSESSMENT: ['key_risks', 'risk_scores', 'mitigation_strategies']
        }
    
    async def validate_section(self, section: ReportSection, content: Dict[str, Any]) -> ValidationResult:
        """Validate a single report section"""
        issues = []
        warnings = []
        scores = {}
        
        # Content completeness validation
        completeness_score = await self._validate_completeness(section, content, issues, warnings)
        scores['completeness'] = completeness_score
        
        # Data availability validation
        data_score = await self._validate_data_availability(section, content, issues, warnings)
        scores['data_availability'] = data_score
        
        # Format compliance validation
        format_score = await self._validate_format_compliance(section, content, issues, warnings)
        scores['format_compliance'] = format_score
        
        # Chart validity validation
        chart_score = await self._validate_chart_validity(section, content, issues, warnings)
        scores['chart_validity'] = chart_score
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        
        # Determine status
        status = ValidationStatus.PASSED if overall_score >= 0.75 else ValidationStatus.FAILED
        if 0.6 <= overall_score < 0.75:
            status = ValidationStatus.RETRY
            
        return ValidationResult(
            level=ValidationLevel.AGENT,
            section=section,
            status=status,
            score=overall_score,
            issues=issues,
            warnings=warnings,
            metadata=scores,
            timestamp=datetime.utcnow()
        )
    
    async def _validate_completeness(self, section: ReportSection, content: Dict[str, Any], issues: List[str], warnings: List[str]) -> float:
        """Validate content completeness"""
        score = 1.0
        
        # Check word count
        text_content = content.get('text', '')
        word_count = len(text_content.split())
        min_words = self.min_word_counts.get(section, 500)
        
        if word_count < min_words * 0.8:
            issues.append(f"Content too short: {word_count} words (minimum: {min_words})")
            score -= 0.3
        elif word_count < min_words:
            warnings.append(f"Content slightly short: {word_count} words (target: {min_words})")
            score -= 0.1
            
        # Check required fields
        required_fields = self.required_fields.get(section, [])
        missing_fields = [field for field in required_fields if not content.get(field)]
        
        if missing_fields:
            issues.append(f"Missing required fields: {', '.join(missing_fields)}")
            score -= 0.2 * len(missing_fields) / len(required_fields)
            
        return max(0.0, score)
    
    async def _validate_data_availability(self, section: ReportSection, content: Dict[str, Any], issues: List[str], warnings: List[str]) -> float:
        """Validate data availability and quality"""
        score = 1.0
        
        # Check for financial data presence
        if section in [ReportSection.FINANCIAL_ANALYSIS, ReportSection.VALUATION_ANALYSIS]:
            financial_data = content.get('financial_data', {})
            
            if not financial_data:
                issues.append("No financial data available")
                score -= 0.5
            else:
                # Check data completeness
                required_years = 3
                available_years = len(financial_data.get('annual_data', {}))
                
                if available_years < required_years:
                    warnings.append(f"Limited historical data: {available_years} years (target: {required_years})")
                    score -= 0.2
                    
                # Check for null values
                null_percentage = self._calculate_null_percentage(financial_data)
                if null_percentage > 0.2:
                    issues.append(f"High percentage of missing data: {null_percentage:.1%}")
                    score -= 0.3
                    
        return max(0.0, score)
    
    async def _validate_format_compliance(self, section: ReportSection, content: Dict[str, Any], issues: List[str], warnings: List[str]) -> float:
        """Validate format compliance"""
        score = 1.0
        
        # Check text formatting
        text = content.get('text', '')
        
        # Check for proper headings
        if not re.search(r'^#{1,3}\s+', text, re.MULTILINE):
            warnings.append("No proper headings found")
            score -= 0.1
            
        # Check for bullet points or numbered lists
        if section != ReportSection.EXECUTIVE_SUMMARY and not re.search(r'^\s*[-*•]\s+|^\s*\d+\.\s+', text, re.MULTILINE):
            warnings.append("No structured lists found")
            score -= 0.1
            
        # Check for financial figures formatting
        if section in [ReportSection.FINANCIAL_ANALYSIS, ReportSection.VALUATION_ANALYSIS]:
            if not re.search(r'\$[\d,]+\.?\d*[KMB]?', text):
                warnings.append("No properly formatted financial figures found")
                score -= 0.2
                
        return max(0.0, score)
    
    async def _validate_chart_validity(self, section: ReportSection, content: Dict[str, Any], issues: List[str], warnings: List[str]) -> float:
        """Validate chart data and configuration"""
        score = 1.0
        charts = content.get('charts', [])
        
        if not charts and section in [ReportSection.FINANCIAL_ANALYSIS, ReportSection.VALUATION_ANALYSIS]:
            issues.append("No charts provided for data-heavy section")
            score -= 0.4
            return max(0.0, score)
            
        for i, chart in enumerate(charts):
            chart_issues = []
            
            # Check required chart properties
            if not chart.get('type'):
                chart_issues.append(f"Chart {i+1}: Missing chart type")
                
            if not chart.get('data'):
                chart_issues.append(f"Chart {i+1}: No data provided")
                
            if not chart.get('title'):
                chart_issues.append(f"Chart {i+1}: Missing title")
                
            # Validate data structure
            chart_data = chart.get('data', {})
            if chart_data:
                if not chart_data.get('labels'):
                    chart_issues.append(f"Chart {i+1}: Missing data labels")
                    
                datasets = chart_data.get('datasets', [])
                if not datasets:
                    chart_issues.append(f"Chart {i+1}: No datasets provided")
                else:
                    for j, dataset in enumerate(datasets):
                        if not dataset.get('data'):
                            chart_issues.append(f"Chart {i+1}, Dataset {j+1}: No data points")
                            
            if chart_issues:
                issues.extend(chart_issues)
                score -= 0.2
                
        return max(0.0, score)
    
    def _calculate_null_percentage(self, data: Dict[str, Any]) -> float:
        """Calculate percentage of null/missing values in financial data"""
        total_fields = 0
        null_fields = 0
        
        def count_nulls(obj):
            nonlocal total_fields, null_fields
            if isinstance(obj, dict):
                for value in obj.values():
                    if isinstance(value, (dict, list)):
                        count_nulls(value)
                    else:
                        total_fields += 1
                        if value is None or value == '' or value == 'N/A':
                            null_fields += 1
            elif isinstance(obj, list):
                for item in obj:
                    count_nulls(item)
                    
        count_nulls(data)
        return null_fields / total_fields if total_fields > 0 else 0.0