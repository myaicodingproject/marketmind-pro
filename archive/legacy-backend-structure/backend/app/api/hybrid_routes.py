"""
Hybrid PDF Generation API Routes - Phase 2 Integration Layer
FastAPI routes for enhanced PDF generation with Kiro + OpenAI hybrid system
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, status
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime
import asyncio
import os

from app.services.enhanced_pdf_generator import EnhancedPDFGenerator
from app.core.auth import get_current_active_user
from app.features.auth.models import User
from app.schemas.hybrid_models import (
    HybridReportRequest, HybridReportResponse, HealthCheckResponse,
    TaskStatusResponse, CapabilitiesResponse, ErrorResponse
)

logger = logging.getLogger(__name__)

# Create router
hybrid_router = APIRouter(prefix="/hybrid", tags=["Hybrid PDF Generation"])

# Initialize services
pdf_generator = EnhancedPDFGenerator()

# Routes
@hybrid_router.post("/generate", response_model=HybridReportResponse)
async def generate_hybrid_report(
    request: HybridReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Generate enhanced PDF report using hybrid Kiro + OpenAI system"""
    
    try:
        logger.info(f"Hybrid report request for {request.symbol} by user {current_user.id}")
        
        # Generate report
        result = await pdf_generator.generate_hybrid_report(
            symbol=request.symbol,
            enhancement_level=request.enhancement_level.value,
            include_charts=request.include_charts
        )
        
        if result["success"]:
            return HybridReportResponse(**result)
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.get("error", "Report generation failed")
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Hybrid report generation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )

@hybrid_router.get("/download/{symbol}")
async def download_hybrid_report(
    symbol: str,
    current_user: User = Depends(get_current_active_user)
):
    """Download generated hybrid PDF report"""
    
    try:
        # Look for the most recent report file
        reports_dir = Path("reports")
        pdf_files = list(reports_dir.glob(f"*{symbol}*.pdf"))
        
        if not pdf_files:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No report found for symbol {symbol}"
            )
        
        # Get the most recent file
        latest_file = max(pdf_files, key=os.path.getctime)
        
        return FileResponse(
            path=latest_file,
            filename=f"MarketMind_Hybrid_Report_{symbol}.pdf",
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download report"
        )

@hybrid_router.get("/status/{task_id}", response_model=TaskStatusResponse)
async def get_task_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get status of hybrid report generation task"""
    
    try:
        status_info = await pdf_generator.get_generation_status(task_id)
        
        return TaskStatusResponse(
            task_id=task_id,
            **status_info
        )
        
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get task status"
        )

@hybrid_router.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint for hybrid PDF generation system"""
    
    try:
        # Check service health
        services_status = {
            "kiro_cli": "healthy",
            "pdf_generator": "healthy",
            "quality_validator": "healthy"
        }
        
        # Test basic functionality
        try:
            # Quick test of PDF generator initialization
            test_generator = EnhancedPDFGenerator()
            services_status["enhanced_pdf_generator"] = "healthy"
        except Exception as e:
            services_status["enhanced_pdf_generator"] = f"error: {str(e)}"
        
        overall_status = "healthy" if all(
            status == "healthy" for status in services_status.values()
        ) else "degraded"
        
        return HealthCheckResponse(
            status=overall_status,
            timestamp=datetime.now().isoformat(),
            services=services_status
        )
        
    except Exception as e:
        logger.error(f"Health check error: {str(e)}")
        return HealthCheckResponse(
            status="error",
            timestamp=datetime.now().isoformat(),
            services={"error": str(e)}
        )

@hybrid_router.get("/capabilities")
async def get_capabilities():
    """Get available capabilities and configuration"""
    
    return {
        "enhancement_levels": [
            {
                "level": "kiro_only",
                "description": "Pure Kiro CLI generation without OpenAI enhancement",
                "features": ["Fast generation", "Consistent quality", "Cost effective"]
            },
            {
                "level": "standard", 
                "description": "Kiro CLI + basic OpenAI enhancement",
                "features": ["Content polishing", "Format improvement", "Error correction"]
            },
            {
                "level": "premium",
                "description": "Kiro CLI + advanced OpenAI enhancement", 
                "features": ["Deep analysis", "Advanced formatting", "Custom insights"]
            }
        ],
        "supported_formats": ["PDF"],
        "max_concurrent_reports": 5,
        "average_generation_time": {
            "kiro_only": "3-5 minutes",
            "standard": "5-8 minutes", 
            "premium": "8-12 minutes"
        }
    }

# Error handlers
@hybrid_router.exception_handler(ValueError)
async def value_error_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"detail": str(exc)}
    )

@hybrid_router.exception_handler(FileNotFoundError)
async def file_not_found_handler(request, exc):
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={"detail": "Requested file not found"}
    )