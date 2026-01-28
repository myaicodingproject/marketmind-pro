"""
3-Tier Quality System for MarketMind Pro
Ensures institutional-grade quality across all 8 report sections
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class QualityTier(Enum):
    AGENT_LEVEL = "agent_level"
    CROSS_SECTION = "cross_section" 
    REPORT_LEVEL = "report_level"

class QualityStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    RETRY_NEEDED = "retry_needed"
    MANUAL_REVIEW = "manual_review"

@dataclass
class QualityResult:
    tier: QualityTier
    section: Optional[str]
    score: float
    status: QualityStatus
    issues: List[str]
    suggestions: List[str]
    timestamp: datetime

class Tier1AgentValidator:
    """Agent-Level Validation - Individual section quality"""
    
    def __init__(self):
        self.min_word_count = {
            "section1": 800,  # Executive Summary - 3 pages
            "section2": 800,  # Leadership - 3 pages  
            "section3": 1000, # Business Model - 4 pages
            "section4": 1200, # Market Position - 5 pages
            "section5": 1000, # Competitive Advantages - 4 pages
            "section6": 1000, # Market Size - 4 pages
            "section7": 1400, # Financial & Valuation - 7 pages
        }
    
    async def validate_section(self, section_id: str, content: Dict[str, Any]) -> QualityResult:
        """Validate individual section quality"""
        issues = []
        score = 100.0
        
        # Content completeness check
        if not content.get('content'):
            issues.append("Missing main content")
            score -= 30
        elif len(content['content'].split()) < self.min_word_count.get(section_id, 800):
            issues.append(f"Content too short: {len(content['content'].split())} words")
            score -= 20
            
        # Data availability check
        if not content.get('key_metrics'):
            issues.append("Missing key metrics")
            score -= 15
            
        # Chart data validity
        if not content.get('charts') or len(content.get('charts', [])) == 0:
            issues.append("Missing chart data")
            score -= 15
            
        # Format compliance
        if not content.get('title') or not content.get('summary'):
            issues.append("Missing required formatting elements")
            score -= 10
            
        # Professional language check
        if content.get('content') and self._check_professional_language(content['content']):
            issues.append("Non-professional language detected")
            score -= 10
            
        status = QualityStatus.PASSED if score >= 80 else QualityStatus.RETRY_NEEDED
        
        return QualityResult(
            tier=QualityTier.AGENT_LEVEL,
            section=section_id,
            score=max(0, score),
            status=status,
            issues=issues,
            suggestions=self._generate_suggestions(issues),
            timestamp=datetime.now()
        )
    
    def _check_professional_language(self, content: str) -> bool:
        """Check for unprofessional language"""
        unprofessional_words = ['maybe', 'probably', 'i think', 'i believe', 'seems like']
        content_lower = content.lower()
        return any(word in content_lower for word in unprofessional_words)
    
    def _generate_suggestions(self, issues: List[str]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        for issue in issues:
            if "too short" in issue:
                suggestions.append("Add more detailed analysis and supporting data")
            elif "Missing" in issue:
                suggestions.append("Ensure all required components are included")
            elif "language" in issue:
                suggestions.append("Use definitive, professional language")
        return suggestions

class Tier2CrossSectionValidator:
    """Cross-Section Validation - Consistency between sections"""
    
    async def validate_consistency(self, all_sections: Dict[str, Dict[str, Any]]) -> QualityResult:
        """Validate consistency across sections"""
        issues = []
        score = 100.0
        
        # Financial metrics consistency (±5% tolerance)
        financial_consistency = self._check_financial_consistency(all_sections)
        if not financial_consistency['passed']:
            issues.extend(financial_consistency['issues'])
            score -= 25
            
        # Price target alignment
        price_alignment = self._check_price_target_alignment(all_sections)
        if not price_alignment['passed']:
            issues.extend(price_alignment['issues'])
            score -= 20
            
        # Narrative coherence
        narrative_coherence = self._check_narrative_coherence(all_sections)
        if not narrative_coherence['passed']:
            issues.extend(narrative_coherence['issues'])
            score -= 15
            
        # Timeline consistency
        timeline_consistency = self._check_timeline_consistency(all_sections)
        if not timeline_consistency['passed']:
            issues.extend(timeline_consistency['issues'])
            score -= 10
            
        status = QualityStatus.PASSED if score >= 80 else QualityStatus.RETRY_NEEDED
        
        return QualityResult(
            tier=QualityTier.CROSS_SECTION,
            section=None,
            score=max(0, score),
            status=status,
            issues=issues,
            suggestions=self._generate_cross_section_suggestions(issues),
            timestamp=datetime.now()
        )
    
    def _check_financial_consistency(self, sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Check financial metrics consistency across sections"""
        issues = []
        
        # Extract financial metrics from different sections
        exec_metrics = sections.get('section1', {}).get('key_metrics', {})
        financial_metrics = sections.get('section7', {}).get('key_metrics', {})
        
        # Check P/E ratio consistency
        exec_pe = exec_metrics.get('pe_ratio')
        fin_pe = financial_metrics.get('pe_ratio')
        
        if exec_pe and fin_pe:
            variance = abs(exec_pe - fin_pe) / max(exec_pe, fin_pe)
            if variance > 0.05:  # 5% tolerance
                issues.append(f"P/E ratio inconsistency: {exec_pe} vs {fin_pe}")
        
        return {'passed': len(issues) == 0, 'issues': issues}
    
    def _check_price_target_alignment(self, sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Check price target alignment between executive summary and valuation"""
        issues = []
        
        exec_target = sections.get('section1', {}).get('price_target')
        val_target = sections.get('section7', {}).get('price_target')
        
        if exec_target and val_target:
            variance = abs(exec_target - val_target) / max(exec_target, val_target)
            if variance > 0.10:  # 10% tolerance for price targets
                issues.append(f"Price target mismatch: {exec_target} vs {val_target}")
        
        return {'passed': len(issues) == 0, 'issues': issues}
    
    def _check_narrative_coherence(self, sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Check for contradictory statements across sections"""
        issues = []
        
        # Extract investment recommendations
        exec_rec = sections.get('section1', {}).get('recommendation', '').lower()
        val_rec = sections.get('section7', {}).get('recommendation', '').lower()
        
        if exec_rec and val_rec and exec_rec != val_rec:
            issues.append(f"Conflicting recommendations: {exec_rec} vs {val_rec}")
        
        return {'passed': len(issues) == 0, 'issues': issues}
    
    def _check_timeline_consistency(self, sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Check timeline consistency across sections"""
        issues = []
        # Implementation for timeline checks
        return {'passed': len(issues) == 0, 'issues': issues}
    
    def _generate_cross_section_suggestions(self, issues: List[str]) -> List[str]:
        """Generate suggestions for cross-section issues"""
        suggestions = []
        for issue in issues:
            if "inconsistency" in issue or "mismatch" in issue:
                suggestions.append("Review and align financial metrics across sections")
            elif "Conflicting" in issue:
                suggestions.append("Ensure consistent investment thesis throughout report")
        return suggestions

class Tier3ReportValidator:
    """Report-Level Validation - Overall quality and professional standards"""
    
    async def validate_report(self, all_sections: Dict[str, Dict[str, Any]], 
                            tier1_results: List[QualityResult],
                            tier2_result: QualityResult) -> QualityResult:
        """Final report-level validation"""
        issues = []
        
        # Calculate overall quality score
        tier1_avg = sum(r.score for r in tier1_results) / len(tier1_results)
        tier2_score = tier2_result.score
        overall_score = (tier1_avg * 0.6) + (tier2_score * 0.4)
        
        # Professional standards check
        prof_check = self._check_professional_standards(all_sections)
        if not prof_check['passed']:
            issues.extend(prof_check['issues'])
            overall_score -= 10
            
        # Executive summary alignment
        exec_alignment = self._check_executive_alignment(all_sections)
        if not exec_alignment['passed']:
            issues.extend(exec_alignment['issues'])
            overall_score -= 5
            
        status = QualityStatus.PASSED if overall_score >= 80 else QualityStatus.FAILED
        
        return QualityResult(
            tier=QualityTier.REPORT_LEVEL,
            section=None,
            score=max(0, overall_score),
            status=status,
            issues=issues,
            suggestions=self._generate_report_suggestions(issues, overall_score),
            timestamp=datetime.now()
        )
    
    def _check_professional_standards(self, sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Check overall professional standards"""
        issues = []
        
        # Check for consistent formatting
        for section_id, section in sections.items():
            if not section.get('title') or not section.get('summary'):
                issues.append(f"Section {section_id} missing professional formatting")
        
        return {'passed': len(issues) == 0, 'issues': issues}
    
    def _check_executive_alignment(self, sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Check if executive summary aligns with detailed sections"""
        issues = []
        # Implementation for executive alignment checks
        return {'passed': len(issues) == 0, 'issues': issues}
    
    def _generate_report_suggestions(self, issues: List[str], score: float) -> List[str]:
        """Generate report-level improvement suggestions"""
        suggestions = []
        if score < 80:
            suggestions.append("Overall quality below threshold - review all sections")
        if issues:
            suggestions.append("Address specific formatting and alignment issues")
        return suggestions

class QualityOrchestrator:
    """Main orchestrator for the 3-tier quality system"""
    
    def __init__(self):
        self.tier1_validator = Tier1AgentValidator()
        self.tier2_validator = Tier2CrossSectionValidator()
        self.tier3_validator = Tier3ReportValidator()
        self.max_retries = 3
    
    async def validate_report(self, all_sections: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Run complete 3-tier validation"""
        start_time = datetime.now()
        
        # Tier 1: Agent-level validation
        tier1_results = []
        for section_id, section_data in all_sections.items():
            result = await self.tier1_validator.validate_section(section_id, section_data)
            tier1_results.append(result)
        
        # Tier 2: Cross-section validation
        tier2_result = await self.tier2_validator.validate_consistency(all_sections)
        
        # Tier 3: Report-level validation
        tier3_result = await self.tier3_validator.validate_report(
            all_sections, tier1_results, tier2_result
        )
        
        # Determine overall status
        failed_sections = [r for r in tier1_results if r.status != QualityStatus.PASSED]
        overall_passed = (
            len(failed_sections) == 0 and 
            tier2_result.status == QualityStatus.PASSED and
            tier3_result.status == QualityStatus.PASSED
        )
        
        validation_time = (datetime.now() - start_time).total_seconds()
        
        return {
            'overall_passed': overall_passed,
            'overall_score': tier3_result.score,
            'tier1_results': [self._result_to_dict(r) for r in tier1_results],
            'tier2_result': self._result_to_dict(tier2_result),
            'tier3_result': self._result_to_dict(tier3_result),
            'failed_sections': [r.section for r in failed_sections],
            'retry_needed': len(failed_sections) > 0 or tier2_result.status == QualityStatus.RETRY_NEEDED,
            'validation_time_seconds': validation_time,
            'timestamp': datetime.now().isoformat()
        }
    
    async def validate_with_retries(self, all_sections: Dict[str, Dict[str, Any]], 
                                  regenerate_callback) -> Dict[str, Any]:
        """Validate with auto-retry mechanism"""
        for attempt in range(self.max_retries + 1):
            logger.info(f"Quality validation attempt {attempt + 1}")
            
            result = await self.validate_report(all_sections)
            
            if result['overall_passed']:
                result['attempts'] = attempt + 1
                return result
            
            if attempt < self.max_retries:
                # Regenerate failed sections
                failed_sections = result['failed_sections']
                if failed_sections:
                    logger.info(f"Regenerating failed sections: {failed_sections}")
                    await regenerate_callback(failed_sections)
            else:
                # Max retries reached - flag for manual review
                result['status'] = 'manual_review_required'
                result['attempts'] = self.max_retries + 1
                logger.warning("Max retries reached - flagging for manual review")
        
        return result
    
    def _result_to_dict(self, result: QualityResult) -> Dict[str, Any]:
        """Convert QualityResult to dictionary"""
        return {
            'tier': result.tier.value,
            'section': result.section,
            'score': result.score,
            'status': result.status.value,
            'issues': result.issues,
            'suggestions': result.suggestions,
            'timestamp': result.timestamp.isoformat()
        }

# Quality system instance
quality_orchestrator = QualityOrchestrator()
