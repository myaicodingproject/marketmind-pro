"""
Quality Auditor Subagent for MarketMind Pro
Validates report sections against institutional standards
"""

import asyncio
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class QualityMetric(Enum):
    CONTENT_COMPLETENESS = "content_completeness"
    FINANCIAL_ACCURACY = "financial_accuracy"
    PROFESSIONAL_TONE = "professional_tone"
    STRUCTURE_COMPLIANCE = "structure_compliance"

@dataclass
class QualityScore:
    metric: QualityMetric
    score: float  # 0-100
    feedback: str
    passed: bool

@dataclass
class SectionAudit:
    section_name: str
    overall_score: float
    quality_scores: List[QualityScore]
    passed: bool
    retry_count: int = 0

class QualityAuditor:
    """AI agent for validating report sections against institutional standards"""
    
    def __init__(self, kiro_engine, min_threshold: float = 85.0, max_retries: int = 2):
        self.kiro_engine = kiro_engine
        self.min_threshold = min_threshold
        self.max_retries = max_retries
        
    async def audit_section(self, section_name: str, content: str, 
                          financial_data: Dict = None) -> SectionAudit:
        """Audit a single report section against quality standards"""
        
        quality_scores = await asyncio.gather(
            self._assess_content_completeness(section_name, content),
            self._assess_financial_accuracy(content, financial_data or {}),
            self._assess_professional_tone(content),
            self._assess_structure_compliance(section_name, content)
        )
        
        overall_score = sum(score.score for score in quality_scores) / len(quality_scores)
        passed = overall_score >= self.min_threshold
        
        return SectionAudit(
            section_name=section_name,
            overall_score=overall_score,
            quality_scores=quality_scores,
            passed=passed
        )
    
    async def audit_with_retry(self, section_name: str, content: str, 
                             financial_data: Dict = None) -> SectionAudit:
        """Audit section with auto-retry mechanism"""
        
        for attempt in range(self.max_retries + 1):
            audit = await self.audit_section(section_name, content, financial_data)
            audit.retry_count = attempt
            
            if audit.passed or attempt == self.max_retries:
                return audit
                
            # Generate improvement suggestions for retry
            content = await self._improve_content(content, audit.quality_scores)
            
        return audit
    
    async def _assess_content_completeness(self, section_name: str, content: str) -> QualityScore:
        """Assess if content meets completeness requirements"""
        
        prompt = f"""
        Evaluate content completeness for {section_name} section:
        
        Content: {content[:2000]}...
        
        Check for:
        - Required subsections present
        - Adequate detail level
        - Key metrics included
        - Proper data coverage
        
        Score 0-100 and provide specific feedback.
        Format: {{"score": 85, "feedback": "Missing risk factors analysis"}}
        """
        
        result = await self.kiro_engine.execute_prompt("quality-completeness", prompt)
        data = json.loads(result)
        
        return QualityScore(
            metric=QualityMetric.CONTENT_COMPLETENESS,
            score=data["score"],
            feedback=data["feedback"],
            passed=data["score"] >= self.min_threshold
        )
    
    async def _assess_financial_accuracy(self, content: str, financial_data: Dict) -> QualityScore:
        """Validate financial calculations and data accuracy"""
        
        prompt = f"""
        Validate financial accuracy in content:
        
        Content: {content[:2000]}...
        Reference Data: {json.dumps(financial_data, indent=2)[:1000]}...
        
        Check for:
        - Calculation accuracy
        - Data consistency
        - Proper financial terminology
        - Realistic projections
        
        Score 0-100 and identify any errors.
        Format: {{"score": 92, "feedback": "All calculations verified"}}
        """
        
        result = await self.kiro_engine.execute_prompt("quality-financial", prompt)
        data = json.loads(result)
        
        return QualityScore(
            metric=QualityMetric.FINANCIAL_ACCURACY,
            score=data["score"],
            feedback=data["feedback"],
            passed=data["score"] >= self.min_threshold
        )
    
    async def _assess_professional_tone(self, content: str) -> QualityScore:
        """Evaluate professional tone and institutional quality"""
        
        prompt = f"""
        Assess professional tone for institutional standards:
        
        Content: {content[:2000]}...
        
        Evaluate:
        - Professional language use
        - Objective analysis tone
        - Appropriate formality level
        - Clear, concise writing
        
        Score 0-100 based on institutional report standards.
        Format: {{"score": 88, "feedback": "Professional tone maintained throughout"}}
        """
        
        result = await self.kiro_engine.execute_prompt("quality-tone", prompt)
        data = json.loads(result)
        
        return QualityScore(
            metric=QualityMetric.PROFESSIONAL_TONE,
            score=data["score"],
            feedback=data["feedback"],
            passed=data["score"] >= self.min_threshold
        )
    
    async def _assess_structure_compliance(self, section_name: str, content: str) -> QualityScore:
        """Check structural compliance with institutional formats"""
        
        prompt = f"""
        Evaluate structure compliance for {section_name}:
        
        Content: {content[:2000]}...
        
        Check:
        - Proper section organization
        - Logical flow and transitions
        - Appropriate headings/subheadings
        - Standard institutional format
        
        Score 0-100 for structural quality.
        Format: {{"score": 90, "feedback": "Well-structured with clear sections"}}
        """
        
        result = await self.kiro_engine.execute_prompt("quality-structure", prompt)
        data = json.loads(result)
        
        return QualityScore(
            metric=QualityMetric.STRUCTURE_COMPLIANCE,
            score=data["score"],
            feedback=data["feedback"],
            passed=data["score"] >= self.min_threshold
        )
    
    async def _improve_content(self, content: str, quality_scores: List[QualityScore]) -> str:
        """Generate improved content based on quality feedback"""
        
        failed_metrics = [score for score in quality_scores if not score.passed]
        feedback_summary = "\n".join([f"- {score.metric.value}: {score.feedback}" 
                                    for score in failed_metrics])
        
        prompt = f"""
        Improve the following content based on quality feedback:
        
        Original Content: {content}
        
        Issues to Address:
        {feedback_summary}
        
        Generate improved version that addresses all feedback points.
        """
        
        return await self.kiro_engine.execute_prompt("quality-improvement", prompt)
    
    def generate_quality_report(self, audits: List[SectionAudit]) -> Dict:
        """Generate comprehensive quality assessment report"""
        
        total_score = sum(audit.overall_score for audit in audits) / len(audits)
        passed_sections = sum(1 for audit in audits if audit.passed)
        
        return {
            "overall_quality_score": round(total_score, 2),
            "sections_passed": f"{passed_sections}/{len(audits)}",
            "pass_rate": round((passed_sections / len(audits)) * 100, 1),
            "threshold_met": total_score >= self.min_threshold,
            "section_details": [
                {
                    "section": audit.section_name,
                    "score": audit.overall_score,
                    "passed": audit.passed,
                    "retries": audit.retry_count,
                    "metrics": [
                        {
                            "metric": score.metric.value,
                            "score": score.score,
                            "feedback": score.feedback
                        } for score in audit.quality_scores
                    ]
                } for audit in audits
            ]
        }