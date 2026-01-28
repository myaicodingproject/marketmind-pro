"""
FastAPI routes for Quality Auditor functionality
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, List, Optional
import logging

from app.services.quality_audit_service import QualityAuditService
from app.core.kiro_engine import KiroEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/quality", tags=["Quality Auditor"])

class SectionAuditRequest(BaseModel):
    section_name: str
    content: str
    financial_data: Optional[Dict] = None

class FullReportAuditRequest(BaseModel):
    sections: Dict[str, str]
    financial_data: Optional[Dict] = None
    ticker: Optional[str] = None

class QualityResponse(BaseModel):
    success: bool
    audit_result: Dict
    quality_summary: Dict
    timestamp: str

@router.post("/audit/section", response_model=Dict)
async def audit_section(request: SectionAuditRequest):
    """Audit a single report section"""
    
    try:
        kiro_engine = KiroEngine()
        audit_service = QualityAuditService(kiro_engine)
        
        audit = await audit_service.audit_single_section(
            section_name=request.section_name,
            content=request.content,
            financial_data=request.financial_data
        )
        
        return {
            "success": True,
            "section_name": request.section_name,
            "overall_score": audit.overall_score,
            "passed": audit.passed,
            "retry_count": audit.retry_count,
            "quality_metrics": [
                {
                    "metric": score.metric.value,
                    "score": score.score,
                    "feedback": score.feedback,
                    "passed": score.passed
                } for score in audit.quality_scores
            ]
        }
        
    except Exception as e:
        logger.error(f"Section audit failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Audit failed: {str(e)}")

@router.post("/audit/full-report", response_model=QualityResponse)
async def audit_full_report(request: FullReportAuditRequest):
    """Audit complete report with all sections"""
    
    try:
        kiro_engine = KiroEngine()
        audit_service = QualityAuditService(kiro_engine)
        
        # Perform full audit
        audit_result = await audit_service.audit_full_report(
            report_sections=request.sections,
            financial_data=request.financial_data
        )
        
        # Generate quality summary
        quality_summary = audit_service.get_quality_summary(audit_result["section_audits"])
        
        return QualityResponse(
            success=True,
            audit_result=audit_result["quality_report"],
            quality_summary=quality_summary,
            timestamp="2024-01-15T10:30:00Z"
        )
        
    except Exception as e:
        logger.error(f"Full report audit failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Full audit failed: {str(e)}")

@router.post("/validate-and-improve/{section_name}")
async def validate_and_improve_section(section_name: str, request: Dict):
    """Validate section and return improved version if needed"""
    
    try:
        kiro_engine = KiroEngine()
        audit_service = QualityAuditService(kiro_engine)
        
        result = await audit_service.validate_and_improve_section(
            section_name=section_name,
            content=request["content"],
            financial_data=request.get("financial_data")
        )
        
        return {
            "success": True,
            "section_name": section_name,
            "original_score": result["audit_result"].overall_score,
            "passed_audit": result["audit_result"].passed,
            "improvement_made": result["improvement_made"],
            "improved_content": result["improved_content"],
            "quality_feedback": [
                {
                    "metric": score.metric.value,
                    "score": score.score,
                    "feedback": score.feedback
                } for score in result["audit_result"].quality_scores
            ]
        }
        
    except Exception as e:
        logger.error(f"Section validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@router.get("/standards")
async def get_quality_standards():
    """Get current quality standards and thresholds"""
    
    return {
        "minimum_threshold": 85.0,
        "quality_metrics": [
            {
                "name": "content_completeness",
                "description": "Ensures all required sections and data are present",
                "weight": 25
            },
            {
                "name": "financial_accuracy", 
                "description": "Validates calculations and data consistency",
                "weight": 25
            },
            {
                "name": "professional_tone",
                "description": "Assesses institutional-grade writing quality",
                "weight": 25
            },
            {
                "name": "structure_compliance",
                "description": "Checks format and organizational standards",
                "weight": 25
            }
        ],
        "grading_scale": {
            "A+": "95-100",
            "A": "90-94",
            "B+": "85-89", 
            "B": "80-84",
            "C+": "75-79",
            "C": "70-74",
            "F": "Below 70"
        },
        "retry_policy": {
            "max_retries": 2,
            "auto_improvement": True
        }
    }

@router.get("/health")
async def quality_auditor_health():
    """Health check for Quality Auditor service"""
    
    try:
        # Test Kiro engine connectivity
        kiro_engine = KiroEngine()
        test_result = await kiro_engine.execute_prompt(
            "quality-completeness", 
            "Test prompt for health check"
        )
        
        return {
            "status": "healthy",
            "kiro_engine": "connected",
            "auditor_version": "1.0.0",
            "timestamp": "2024-01-15T10:30:00Z"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-15T10:30:00Z"
        }