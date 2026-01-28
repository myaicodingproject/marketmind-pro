import asyncio
from typing import Dict, List, Any, Tuple
from datetime import datetime
from .models import ValidationResult, ValidationLevel, ValidationStatus, ReportSection

class CrossSectionValidator:
    """Validates consistency across report sections: financial consistency ±5%, narrative coherence, price target alignment"""
    
    def __init__(self):
        self.tolerance = 0.05  # ±5% tolerance for financial consistency
        
    async def validate_cross_sections(self, sections: Dict[ReportSection, Dict[str, Any]]) -> ValidationResult:
        """Validate consistency across all report sections"""
        issues = []
        warnings = []
        scores = {}
        
        # Financial consistency validation
        financial_score = await self._validate_financial_consistency(sections, issues, warnings)
        scores['financial_consistency'] = financial_score
        
        # Narrative coherence validation
        narrative_score = await self._validate_narrative_coherence(sections, issues, warnings)
        scores['narrative_coherence'] = narrative_score
        
        # Price target alignment validation
        price_target_score = await self._validate_price_target_alignment(sections, issues, warnings)
        scores['price_target_alignment'] = price_target_score
        
        # Investment thesis consistency
        thesis_score = await self._validate_investment_thesis_consistency(sections, issues, warnings)
        scores['thesis_consistency'] = thesis_score
        
        # Calculate overall score
        overall_score = sum(scores.values()) / len(scores)
        
        # Determine status
        status = ValidationStatus.PASSED if overall_score >= 0.8 else ValidationStatus.FAILED
        if 0.7 <= overall_score < 0.8:
            status = ValidationStatus.RETRY
            
        return ValidationResult(
            level=ValidationLevel.CROSS_SECTION,
            section=None,
            status=status,
            score=overall_score,
            issues=issues,
            warnings=warnings,
            metadata=scores,
            timestamp=datetime.utcnow()
        )
    
    async def _validate_financial_consistency(self, sections: Dict[ReportSection, Dict[str, Any]], issues: List[str], warnings: List[str]) -> float:
        """Validate financial data consistency across sections with ±5% tolerance"""
        score = 1.0
        
        # Extract financial metrics from different sections
        exec_summary = sections.get(ReportSection.EXECUTIVE_SUMMARY, {})
        financial_analysis = sections.get(ReportSection.FINANCIAL_ANALYSIS, {})
        valuation_analysis = sections.get(ReportSection.VALUATION_ANALYSIS, {})
        
        # Check revenue consistency
        revenue_consistency = await self._check_metric_consistency(
            'revenue', exec_summary, financial_analysis, valuation_analysis
        )
        if not revenue_consistency[0]:
            issues.append(f"Revenue inconsistency: {revenue_consistency[1]}")
            score -= 0.3
            
        # Check profit margin consistency
        margin_consistency = await self._check_metric_consistency(
            'profit_margin', exec_summary, financial_analysis, valuation_analysis
        )
        if not margin_consistency[0]:
            issues.append(f"Profit margin inconsistency: {margin_consistency[1]}")
            score -= 0.2
            
        # Check growth rate consistency
        growth_consistency = await self._check_metric_consistency(
            'growth_rate', exec_summary, financial_analysis, valuation_analysis
        )
        if not growth_consistency[0]:
            warnings.append(f"Growth rate variance: {growth_consistency[1]}")
            score -= 0.1
            
        # Check valuation multiples consistency
        pe_consistency = await self._check_metric_consistency(
            'pe_ratio', exec_summary, financial_analysis, valuation_analysis
        )
        if not pe_consistency[0]:
            issues.append(f"P/E ratio inconsistency: {pe_consistency[1]}")
            score -= 0.2
            
        return max(0.0, score)
    
    async def _check_metric_consistency(self, metric: str, *sections) -> Tuple[bool, str]:
        """Check if a specific metric is consistent across sections"""
        values = []
        section_names = []
        
        for i, section in enumerate(sections):
            if not section:
                continue
                
            # Extract metric value from different possible locations
            value = None
            if metric in section.get('key_metrics', {}):
                value = section['key_metrics'][metric]
            elif metric in section.get('financial_data', {}):
                value = section['financial_data'][metric]
            elif metric in section.get('valuation_metrics', {}):
                value = section['valuation_metrics'][metric]
                
            if value is not None:
                values.append(float(value))
                section_names.append(f"Section_{i+1}")
                
        if len(values) < 2:
            return True, "Insufficient data for comparison"
            
        # Check if all values are within tolerance
        base_value = values[0]
        for i, value in enumerate(values[1:], 1):
            variance = abs(value - base_value) / base_value if base_value != 0 else abs(value)
            if variance > self.tolerance:
                return False, f"{metric}: {section_names[0]}={base_value:.2f}, {section_names[i]}={value:.2f} (variance: {variance:.1%})"
                
        return True, "Consistent"
    
    async def _validate_narrative_coherence(self, sections: Dict[ReportSection, Dict[str, Any]], issues: List[str], warnings: List[str]) -> float:
        """Validate narrative coherence across sections"""
        score = 1.0
        
        # Extract key themes and sentiments
        exec_summary_text = sections.get(ReportSection.EXECUTIVE_SUMMARY, {}).get('text', '')
        company_analysis_text = sections.get(ReportSection.COMPANY_ANALYSIS, {}).get('text', '')
        investment_thesis_text = sections.get(ReportSection.INVESTMENT_THESIS, {}).get('text', '')
        
        # Check sentiment consistency
        exec_sentiment = self._extract_sentiment(exec_summary_text)
        thesis_sentiment = self._extract_sentiment(investment_thesis_text)
        
        if abs(exec_sentiment - thesis_sentiment) > 0.3:
            issues.append(f"Sentiment mismatch between executive summary ({exec_sentiment:.2f}) and investment thesis ({thesis_sentiment:.2f})")
            score -= 0.4
            
        # Check key theme consistency
        exec_themes = self._extract_key_themes(exec_summary_text)
        company_themes = self._extract_key_themes(company_analysis_text)
        
        theme_overlap = len(exec_themes.intersection(company_themes)) / len(exec_themes.union(company_themes)) if exec_themes.union(company_themes) else 0
        
        if theme_overlap < 0.3:
            warnings.append(f"Low theme consistency between sections: {theme_overlap:.1%} overlap")
            score -= 0.2
            
        return max(0.0, score)
    
    async def _validate_price_target_alignment(self, sections: Dict[ReportSection, Dict[str, Any]], issues: List[str], warnings: List[str]) -> float:
        """Validate price target alignment across sections"""
        score = 1.0
        
        # Extract price targets from different sections
        exec_price_target = sections.get(ReportSection.EXECUTIVE_SUMMARY, {}).get('price_target')
        valuation_price_target = sections.get(ReportSection.VALUATION_ANALYSIS, {}).get('price_target')
        
        if exec_price_target and valuation_price_target:
            variance = abs(exec_price_target - valuation_price_target) / valuation_price_target
            
            if variance > self.tolerance:
                issues.append(f"Price target mismatch: Executive Summary ${exec_price_target:.2f} vs Valuation Analysis ${valuation_price_target:.2f} (variance: {variance:.1%})")
                score -= 0.5
            elif variance > self.tolerance / 2:
                warnings.append(f"Minor price target variance: {variance:.1%}")
                score -= 0.1
                
        # Check rating consistency
        exec_rating = sections.get(ReportSection.EXECUTIVE_SUMMARY, {}).get('rating')
        valuation_rating = sections.get(ReportSection.VALUATION_ANALYSIS, {}).get('recommendation')
        
        if exec_rating and valuation_rating and exec_rating.lower() != valuation_rating.lower():
            issues.append(f"Rating inconsistency: Executive Summary '{exec_rating}' vs Valuation Analysis '{valuation_rating}'")
            score -= 0.3
            
        return max(0.0, score)
    
    async def _validate_investment_thesis_consistency(self, sections: Dict[ReportSection, Dict[str, Any]], issues: List[str], warnings: List[str]) -> float:
        """Validate investment thesis consistency with analysis"""
        score = 1.0
        
        thesis_text = sections.get(ReportSection.INVESTMENT_THESIS, {}).get('text', '')
        risk_text = sections.get(ReportSection.RISK_ASSESSMENT, {}).get('text', '')
        
        # Extract bullish/bearish points
        thesis_sentiment = self._extract_sentiment(thesis_text)
        risk_sentiment = self._extract_sentiment(risk_text)
        
        # Risk section should be more negative than thesis
        if risk_sentiment >= thesis_sentiment:
            warnings.append("Risk assessment sentiment not appropriately cautious compared to investment thesis")
            score -= 0.2
            
        # Check for balanced perspective
        if thesis_sentiment > 0.8:
            warnings.append("Investment thesis may be overly optimistic - consider more balanced view")
            score -= 0.1
        elif thesis_sentiment < 0.2:
            warnings.append("Investment thesis may be overly pessimistic")
            score -= 0.1
            
        return max(0.0, score)
    
    def _extract_sentiment(self, text: str) -> float:
        """Extract sentiment score from text (simplified implementation)"""
        positive_words = ['growth', 'strong', 'excellent', 'positive', 'bullish', 'opportunity', 'upside', 'buy']
        negative_words = ['risk', 'decline', 'weak', 'negative', 'bearish', 'concern', 'downside', 'sell']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        total_words = len(text.split())
        if total_words == 0:
            return 0.5
            
        sentiment = (positive_count - negative_count) / total_words
        return max(0.0, min(1.0, 0.5 + sentiment * 10))  # Normalize to 0-1
    
    def _extract_key_themes(self, text: str) -> set:
        """Extract key themes from text (simplified implementation)"""
        themes = set()
        text_lower = text.lower()
        
        # Financial themes
        if any(word in text_lower for word in ['revenue', 'sales', 'income']):
            themes.add('financial_performance')
        if any(word in text_lower for word in ['growth', 'expansion', 'increase']):
            themes.add('growth')
        if any(word in text_lower for word in ['market', 'competition', 'industry']):
            themes.add('market_position')
        if any(word in text_lower for word in ['technology', 'innovation', 'digital']):
            themes.add('technology')
        if any(word in text_lower for word in ['risk', 'challenge', 'concern']):
            themes.add('risks')
            
        return themes