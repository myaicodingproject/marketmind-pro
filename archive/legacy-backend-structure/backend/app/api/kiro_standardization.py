from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any
import logging

from ..core.kiro_processor import KiroOutputProcessor
from ..schemas.kiro_output import KiroOutput

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/kiro", tags=["kiro-standardization"])

class ProcessRequest(BaseModel):
    raw_outputs: Dict[str, str]
    ticker: str

class ProcessResponse(BaseModel):
    success: bool
    report: Dict[str, Any]
    errors: Dict[str, str] = {}

@router.post("/process", response_model=ProcessResponse)
async def process_kiro_outputs(request: ProcessRequest):
    """Process and standardize Kiro CLI outputs"""
    processor = KiroOutputProcessor()
    
    try:
        # Process all outputs
        processed = await processor.process_batch_outputs(request.raw_outputs)
        
        # Validate completeness
        is_complete = processor.validate_report_completeness(processed)
        
        # Merge into final report
        final_report = processor.merge_report_sections(processed)
        final_report["ticker"] = request.ticker
        final_report["complete"] = is_complete
        
        # Collect errors
        errors = {
            section: data.get("error_message", "")
            for section, data in processed.items()
            if data.get("error")
        }
        
        return ProcessResponse(
            success=is_complete,
            report=final_report,
            errors=errors
        )
        
    except Exception as e:
        logger.error(f"Failed to process Kiro outputs: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate")
async def validate_single_output(output: Dict[str, Any]):
    """Validate a single Kiro CLI output against schema"""
    try:
        validated = KiroOutput(**output)
        return {"valid": True, "formatted": validated.dict()}
    except Exception as e:
        return {"valid": False, "error": str(e)}

@router.get("/schema")
async def get_schema():
    """Get the JSON schema for Kiro CLI outputs"""
    return KiroOutput.schema()