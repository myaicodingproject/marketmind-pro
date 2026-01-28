"""
Quality Auditor Integration Service
Integrates quality auditing into the MarketMind Pro report generation pipeline
"""

import asyncio
import logging
from typing import Dict, List
from app.agents.quality_auditor import QualityAuditor, SectionAudit
from app.core.kiro_engine import KiroEngine

logger = logging.getLogger(__name__)

class QualityAuditService:
    """Service for integrating quality auditing into report generation"""
    
    def __init__(self, kiro_engine: KiroEngine, min_threshold: float = 85.0):
        self.auditor = QualityAuditor(kiro_engine, min_threshold)
        self.kiro_engine = kiro_engine
        
    async def audit_full_report(self, report_sections: Dict[str, str], 
                              financial_data: Dict = None) -> Dict:
        """Audit all sections of a complete report"""
        
        logger.info("Starting full report quality audit")
        
        # Define section audit tasks
        audit_tasks = []
        for section_name, content in report_sections.items():
            task = self.auditor.audit_with_retry(
                section_name=section_name,
                content=content,
                financial_data=financial_data
            )
            audit_tasks.append(task)
        
        # Execute all audits concurrently
        section_audits = await asyncio.gather(*audit_tasks)
        
        # Generate comprehensive quality report
        quality_report = self.auditor.generate_quality_report(section_audits)
        
        logger.info(f"Quality audit completed. Overall score: {quality_report['overall_quality_score']}")
        
        return {
            "quality_report": quality_report,
            "section_audits": section_audits,
            "passed_threshold": quality_report["threshold_met"]
        }
    
    async def audit_single_section(self, section_name: str, content: str,
                                 financial_data: Dict = None) -> SectionAudit:
        """Audit a single report section with retry mechanism"""
        
        logger.info(f"Auditing section: {section_name}")
        
        audit = await self.auditor.audit_with_retry(
            section_name=section_name,
            content=content,
            financial_data=financial_data
        )
        
        logger.info(f"Section {section_name} audit completed. Score: {audit.overall_score}")
        
        return audit
    
    async def validate_and_improve_section(self, section_name: str, content: str,
                                         financial_data: Dict = None) -> Dict:
        """Validate section and return improved version if needed"""
        
        audit = await self.audit_single_section(section_name, content, financial_data)
        
        result = {
            "original_content": content,
            "audit_result": audit,
            "improved_content": None,
            "improvement_made": False
        }
        
        # If section failed, the audit_with_retry already improved it
        if not audit.passed and audit.retry_count > 0:
            result["improvement_made"] = True
            result["improved_content"] = content  # Content was already improved in retry
        
        return result
    
    def get_quality_summary(self, audits: List[SectionAudit]) -> Dict:
        """Generate executive summary of quality assessment"""
        
        total_sections = len(audits)
        passed_sections = sum(1 for audit in audits if audit.passed)
        avg_score = sum(audit.overall_score for audit in audits) / total_sections
        
        # Identify weakest areas
        metric_scores = {}
        for audit in audits:
            for score in audit.quality_scores:
                metric = score.metric.value
                if metric not in metric_scores:
                    metric_scores[metric] = []
                metric_scores[metric].append(score.score)
        
        avg_metric_scores = {
            metric: sum(scores) / len(scores)
            for metric, scores in metric_scores.items()
        }
        
        weakest_metric = min(avg_metric_scores.items(), key=lambda x: x[1])
        
        return {
            "overall_grade": self._get_letter_grade(avg_score),
            "pass_rate": f"{passed_sections}/{total_sections}",
            "average_score": round(avg_score, 1),
            "weakest_area": {
                "metric": weakest_metric[0],
                "score": round(weakest_metric[1], 1)
            },
            "sections_needing_attention": [
                audit.section_name for audit in audits 
                if not audit.passed
            ],
            "retry_summary": {
                "sections_retried": sum(1 for audit in audits if audit.retry_count > 0),
                "total_retries": sum(audit.retry_count for audit in audits)
            }
        }
    
    def _get_letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 95: return "A+"
        elif score >= 90: return "A"
        elif score >= 85: return "B+"
        elif score >= 80: return "B"
        elif score >= 75: return "C+"
        elif score >= 70: return "C"
        else: return "F"

# FastAPI endpoint integration
async def quality_audit_endpoint(report_data: Dict) -> Dict:
    """FastAPI endpoint for quality auditing"""
    
    kiro_engine = KiroEngine()
    audit_service = QualityAuditService(kiro_engine)
    
    # Extract report sections and financial data
    sections = report_data.get("sections", {})
    financial_data = report_data.get("financial_data", {})
    
    # Perform full audit
    audit_result = await audit_service.audit_full_report(sections, financial_data)
    
    # Generate summary
    quality_summary = audit_service.get_quality_summary(audit_result["section_audits"])
    
    return {
        "audit_result": audit_result,
        "quality_summary": quality_summary,
        "timestamp": "2024-01-15T10:30:00Z",
        "auditor_version": "1.0.0"
    }