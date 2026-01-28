"""
Context Quality Validation and Filtering - Session A4.5
Ensures high-quality context for institutional-grade analysis
"""

import re
import json
import asyncio
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import numpy as np

logger = logging.getLogger(__name__)

class ContextQuality(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    ACCEPTABLE = "acceptable"
    POOR = "poor"
    REJECTED = "rejected"

@dataclass
class QualityMetrics:
    relevance_score: float
    completeness_score: float
    recency_score: float
    accuracy_score: float
    source_reliability: float
    overall_score: float
    quality_level: ContextQuality

@dataclass
class ValidationResult:
    passed: bool
    quality_metrics: QualityMetrics
    filtered_content: str
    issues_found: List[str]
    recommendations: List[str]

class FinancialDataValidator:
    """Validates financial data accuracy and consistency"""
    
    def __init__(self):
        # Financial metric patterns
        self.financial_patterns = {
            'revenue': r'(?:revenue|sales|net sales)[\s:]*\$?([0-9,]+\.?[0-9]*)\s*(?:million|billion|M|B)?',
            'net_income': r'(?:net income|profit|earnings)[\s:]*\$?([0-9,]+\.?[0-9]*)\s*(?:million|billion|M|B)?',
            'eps': r'(?:earnings per share|EPS)[\s:]*\$?([0-9]+\.?[0-9]*)',
            'pe_ratio': r'(?:P/E|price.to.earnings)[\s:]*([0-9]+\.?[0-9]*)',
            'market_cap': r'(?:market cap|market capitalization)[\s:]*\$?([0-9,]+\.?[0-9]*)\s*(?:million|billion|M|B)?'
        }
        
        # Date patterns
        self.date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}'
        ]
    
    def validate_financial_consistency(self, content: str) -> Tuple[bool, List[str]]:
        """Validate financial data consistency"""
        issues = []
        
        # Extract financial metrics
        extracted_metrics = {}
        for metric, pattern in self.financial_patterns.items():
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                extracted_metrics[metric] = matches
        
        # Check for inconsistencies
        if 'revenue' in extracted_metrics and 'net_income' in extracted_metrics:
            try:
                revenue_values = [float(v.replace(',', '')) for v in extracted_metrics['revenue']]
                income_values = [float(v.replace(',', '')) for v in extracted_metrics['net_income']]
                
                # Check if net income > revenue (impossible)
                for revenue, income in zip(revenue_values, income_values):
                    if income > revenue:
                        issues.append(f"Net income ({income}) cannot exceed revenue ({revenue})")
            except ValueError:
                issues.append("Unable to parse financial values for consistency check")
        
        # Check for reasonable P/E ratios
        if 'pe_ratio' in extracted_metrics:
            try:
                pe_values = [float(v) for v in extracted_metrics['pe_ratio']]
                for pe in pe_values:
                    if pe < 0 or pe > 1000:
                        issues.append(f"Unrealistic P/E ratio: {pe}")
            except ValueError:
                issues.append("Unable to parse P/E ratio values")
        
        return len(issues) == 0, issues
    
    def extract_dates(self, content: str) -> List[str]:
        """Extract dates from content"""
        dates = []
        for pattern in self.date_patterns:
            matches = re.findall(pattern, content)
            dates.extend(matches)
        return dates
    
    def validate_date_consistency(self, content: str) -> Tuple[bool, List[str]]:
        """Validate date consistency and recency"""
        issues = []
        dates = self.extract_dates(content)
        
        if not dates:
            issues.append("No dates found in financial content")
            return False, issues
        
        # Check for future dates
        current_date = datetime.now()
        for date_str in dates:
            try:
                # Simple date parsing (can be enhanced)
                if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    if date_obj > current_date:
                        issues.append(f"Future date found: {date_str}")
            except ValueError:
                continue
        
        return len(issues) == 0, issues

class ContextQualityValidator:
    """Validates and filters context for institutional-quality analysis"""
    
    def __init__(self):
        self.financial_validator = FinancialDataValidator()
        
        # Quality thresholds
        self.quality_thresholds = {
            ContextQuality.EXCELLENT: 0.9,
            ContextQuality.GOOD: 0.8,
            ContextQuality.ACCEPTABLE: 0.7,
            ContextQuality.POOR: 0.5
        }
        
        # Source reliability scores
        self.source_reliability = {
            'sec_filing': 1.0,
            'earnings_call': 0.95,
            'financial_data': 0.9,
            'company_profile': 0.85,
            'analyst_report': 0.8,
            'news_article': 0.6,
            'unknown': 0.3
        }
    
    async def validate_context(self, context_data: Dict[str, Any], 
                             ticker: str) -> ValidationResult:
        """Validate context quality and filter content"""
        
        issues_found = []
        recommendations = []
        
        # Calculate quality metrics
        relevance_score = await self._calculate_relevance_score(context_data, ticker)
        completeness_score = self._calculate_completeness_score(context_data)
        recency_score = self._calculate_recency_score(context_data)
        accuracy_score = await self._calculate_accuracy_score(context_data)
        source_reliability = self._calculate_source_reliability(context_data)
        
        # Calculate overall score
        weights = {
            'relevance': 0.3,
            'completeness': 0.2,
            'recency': 0.2,
            'accuracy': 0.2,
            'reliability': 0.1
        }
        
        overall_score = (
            relevance_score * weights['relevance'] +
            completeness_score * weights['completeness'] +
            recency_score * weights['recency'] +
            accuracy_score * weights['accuracy'] +
            source_reliability * weights['reliability']
        )
        
        # Determine quality level
        quality_level = self._determine_quality_level(overall_score)
        
        # Filter content based on quality
        filtered_content = await self._filter_content(context_data, quality_level)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            relevance_score, completeness_score, recency_score, 
            accuracy_score, source_reliability
        )
        
        quality_metrics = QualityMetrics(
            relevance_score=relevance_score,
            completeness_score=completeness_score,
            recency_score=recency_score,
            accuracy_score=accuracy_score,
            source_reliability=source_reliability,
            overall_score=overall_score,
            quality_level=quality_level
        )
        
        passed = quality_level != ContextQuality.REJECTED
        
        logger.info(f"Context validation for {ticker}: {quality_level.value} (score: {overall_score:.3f})")
        
        return ValidationResult(
            passed=passed,
            quality_metrics=quality_metrics,
            filtered_content=filtered_content,
            issues_found=issues_found,
            recommendations=recommendations
        )
    
    async def _calculate_relevance_score(self, context_data: Dict[str, Any], 
                                       ticker: str) -> float:
        """Calculate relevance score based on ticker mentions and financial terms"""
        
        context_sections = context_data.get('context_sections', {})
        if not context_sections:
            return 0.0
        
        total_content = ""
        for section in context_sections.values():
            total_content += section.get('content', '')
        
        if not total_content:
            return 0.0
        
        # Count ticker mentions
        ticker_mentions = len(re.findall(rf'\b{ticker}\b', total_content, re.IGNORECASE))
        
        # Count financial terms
        financial_terms = [
            'revenue', 'earnings', 'profit', 'cash flow', 'balance sheet',
            'income statement', 'financial performance', 'quarterly results',
            'annual report', 'SEC filing', 'market cap', 'valuation'
        ]
        
        financial_term_count = 0
        for term in financial_terms:
            financial_term_count += len(re.findall(rf'\b{term}\b', total_content, re.IGNORECASE))
        
        # Calculate relevance score
        content_length = len(total_content.split())
        ticker_density = ticker_mentions / max(content_length, 1) * 100
        financial_density = financial_term_count / max(content_length, 1) * 100
        
        # Normalize scores
        relevance_score = min(1.0, (ticker_density * 0.6 + financial_density * 0.4) / 10)
        
        return relevance_score
    
    def _calculate_completeness_score(self, context_data: Dict[str, Any]) -> float:
        """Calculate completeness score based on available data types"""
        
        context_sections = context_data.get('context_sections', {})
        
        # Expected data types for comprehensive analysis
        expected_types = {
            'sec_filing': 0.3,
            'financial_data': 0.25,
            'company_profile': 0.15,
            'earnings_call': 0.15,
            'analyst_report': 0.1,
            'market_data': 0.05
        }
        
        completeness_score = 0.0
        for data_type, weight in expected_types.items():
            if data_type in context_sections:
                section = context_sections[data_type]
                doc_count = section.get('document_count', 0)
                # Score based on document availability and count
                type_score = min(1.0, doc_count / 3)  # Optimal: 3+ documents per type
                completeness_score += type_score * weight
        
        return completeness_score
    
    def _calculate_recency_score(self, context_data: Dict[str, Any]) -> float:
        """Calculate recency score based on document dates"""
        
        context_sections = context_data.get('context_sections', {})
        current_date = datetime.now()
        
        all_dates = []
        
        for section in context_sections.values():
            content = section.get('content', '')
            dates = self.financial_validator.extract_dates(content)
            
            for date_str in dates:
                try:
                    if re.match(r'\d{4}-\d{2}-\d{2}', date_str):
                        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                        all_dates.append(date_obj)
                except ValueError:
                    continue
        
        if not all_dates:
            return 0.5  # Neutral score if no dates found
        
        # Calculate average age of documents
        avg_age_days = sum((current_date - date).days for date in all_dates) / len(all_dates)
        
        # Score based on recency (higher score for more recent data)
        if avg_age_days <= 90:  # Within 3 months
            return 1.0
        elif avg_age_days <= 365:  # Within 1 year
            return 0.8
        elif avg_age_days <= 730:  # Within 2 years
            return 0.6
        else:
            return 0.3
    
    async def _calculate_accuracy_score(self, context_data: Dict[str, Any]) -> float:
        """Calculate accuracy score based on data validation"""
        
        context_sections = context_data.get('context_sections', {})
        
        total_content = ""
        for section in context_sections.values():
            total_content += section.get('content', '')
        
        if not total_content:
            return 0.0
        
        # Validate financial consistency
        financial_consistent, financial_issues = self.financial_validator.validate_financial_consistency(total_content)
        
        # Validate date consistency
        date_consistent, date_issues = self.financial_validator.validate_date_consistency(total_content)
        
        # Calculate accuracy score
        accuracy_score = 1.0
        
        if not financial_consistent:
            accuracy_score -= 0.3 * len(financial_issues) / 10  # Penalize financial inconsistencies
        
        if not date_consistent:
            accuracy_score -= 0.2 * len(date_issues) / 5  # Penalize date issues
        
        return max(0.0, accuracy_score)
    
    def _calculate_source_reliability(self, context_data: Dict[str, Any]) -> float:
        """Calculate source reliability score"""
        
        context_sections = context_data.get('context_sections', {})
        
        if not context_sections:
            return 0.0
        
        total_documents = 0
        weighted_reliability = 0.0
        
        for source_type, section in context_sections.items():
            doc_count = section.get('document_count', 0)
            reliability = self.source_reliability.get(source_type, 0.3)
            
            total_documents += doc_count
            weighted_reliability += reliability * doc_count
        
        if total_documents == 0:
            return 0.0
        
        return weighted_reliability / total_documents
    
    def _determine_quality_level(self, overall_score: float) -> ContextQuality:
        """Determine quality level based on overall score"""
        
        if overall_score >= self.quality_thresholds[ContextQuality.EXCELLENT]:
            return ContextQuality.EXCELLENT
        elif overall_score >= self.quality_thresholds[ContextQuality.GOOD]:
            return ContextQuality.GOOD
        elif overall_score >= self.quality_thresholds[ContextQuality.ACCEPTABLE]:
            return ContextQuality.ACCEPTABLE
        elif overall_score >= self.quality_thresholds[ContextQuality.POOR]:
            return ContextQuality.POOR
        else:
            return ContextQuality.REJECTED
    
    async def _filter_content(self, context_data: Dict[str, Any], 
                            quality_level: ContextQuality) -> str:
        """Filter and optimize content based on quality level"""
        
        context_sections = context_data.get('context_sections', {})
        
        if quality_level == ContextQuality.REJECTED:
            return "Context quality insufficient for analysis."
        
        # Filter based on quality level
        filtered_sections = {}
        
        for source_type, section in context_sections.items():
            source_reliability = self.source_reliability.get(source_type, 0.3)
            
            # Apply filtering based on quality level
            if quality_level == ContextQuality.EXCELLENT:
                # Keep all high-quality sources
                if source_reliability >= 0.8:
                    filtered_sections[source_type] = section
            elif quality_level == ContextQuality.GOOD:
                # Keep good sources
                if source_reliability >= 0.7:
                    filtered_sections[source_type] = section
            elif quality_level == ContextQuality.ACCEPTABLE:
                # Keep acceptable sources
                if source_reliability >= 0.6:
                    filtered_sections[source_type] = section
            else:  # POOR
                # Keep only the most reliable sources
                if source_reliability >= 0.9:
                    filtered_sections[source_type] = section
        
        # Build filtered content
        content_parts = []
        for source_type, section in filtered_sections.items():
            content_parts.append(f"[{source_type.upper()}]\n{section['content']}")
        
        return "\n\n".join(content_parts)
    
    def _generate_recommendations(self, relevance_score: float, completeness_score: float,
                                recency_score: float, accuracy_score: float,
                                source_reliability: float) -> List[str]:
        """Generate recommendations for improving context quality"""
        
        recommendations = []
        
        if relevance_score < 0.7:
            recommendations.append("Improve context relevance by including more ticker-specific and financial content")
        
        if completeness_score < 0.7:
            recommendations.append("Add more diverse data sources (SEC filings, earnings calls, analyst reports)")
        
        if recency_score < 0.7:
            recommendations.append("Include more recent financial data and documents")
        
        if accuracy_score < 0.8:
            recommendations.append("Verify financial data consistency and accuracy")
        
        if source_reliability < 0.8:
            recommendations.append("Prioritize high-reliability sources (SEC filings, official company data)")
        
        return recommendations

class MultiSourceContextAggregator:
    """Aggregates context from multiple sources with quality weighting"""
    
    def __init__(self, validator: ContextQualityValidator):
        self.validator = validator
    
    async def aggregate_contexts(self, contexts: List[Dict[str, Any]], 
                               ticker: str) -> Dict[str, Any]:
        """Aggregate multiple contexts with quality weighting"""
        
        if not contexts:
            return {}
        
        # Validate each context
        validated_contexts = []
        for context in contexts:
            validation_result = await self.validator.validate_context(context, ticker)
            if validation_result.passed:
                validated_contexts.append({
                    'context': context,
                    'validation': validation_result
                })
        
        if not validated_contexts:
            logger.warning(f"No valid contexts found for {ticker}")
            return {}
        
        # Sort by quality score
        validated_contexts.sort(
            key=lambda x: x['validation'].quality_metrics.overall_score,
            reverse=True
        )
        
        # Aggregate contexts with quality weighting
        aggregated_sections = {}
        total_weight = 0
        
        for ctx_data in validated_contexts:
            context = ctx_data['context']
            quality_score = ctx_data['validation'].quality_metrics.overall_score
            
            context_sections = context.get('context_sections', {})
            
            for source_type, section in context_sections.items():
                if source_type not in aggregated_sections:
                    aggregated_sections[source_type] = {
                        'content': [],
                        'document_count': 0,
                        'token_count': 0,
                        'quality_scores': []
                    }
                
                # Weight content by quality
                weighted_content = f"[Quality: {quality_score:.2f}] {section['content']}"
                aggregated_sections[source_type]['content'].append(weighted_content)
                aggregated_sections[source_type]['document_count'] += section.get('document_count', 0)
                aggregated_sections[source_type]['token_count'] += section.get('token_count', 0)
                aggregated_sections[source_type]['quality_scores'].append(quality_score)
            
            total_weight += quality_score
        
        # Finalize aggregated sections
        final_sections = {}
        for source_type, section_data in aggregated_sections.items():
            final_sections[source_type] = {
                'content': '\n\n'.join(section_data['content']),
                'document_count': section_data['document_count'],
                'token_count': section_data['token_count'],
                'avg_quality_score': sum(section_data['quality_scores']) / len(section_data['quality_scores'])
            }
        
        return {
            'ticker': ticker,
            'analysis_type': 'aggregated',
            'context_sections': final_sections,
            'total_tokens': sum(section['token_count'] for section in final_sections.values()),
            'total_documents': sum(section['document_count'] for section in final_sections.values()),
            'avg_quality_score': total_weight / len(validated_contexts),
            'source_count': len(validated_contexts),
            'generated_at': datetime.now().isoformat()
        }

# Global instances
context_validator = ContextQualityValidator()
context_aggregator = MultiSourceContextAggregator(context_validator)