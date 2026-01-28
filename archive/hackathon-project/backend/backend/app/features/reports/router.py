from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from app.shared.database.connection import get_db
from app.shared.schemas.schemas import Report, ReportCreate, User
from app.shared.utils.auth import get_current_user
from app.features.reports.service import ReportsService
from app.core.queue_manager import queue_manager

router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def create_report(
    report_data: ReportCreate,
    priority: str = "normal",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new stock analysis report and queue for generation"""
    reports_service = ReportsService(db)
    
    # Create report record
    report = reports_service.create_report(report_data, current_user)
    
    # Queue for generation
    result = await reports_service.queue_report_generation(report.id, priority)
    
    return {
        "report_id": report.id,
        "request_id": result["request_id"],
        "ticker": report_data.ticker,
        "status": "queued",
        "message": "Report generation has been queued",
        "estimated_completion": "5-8 minutes"
    }

@router.post("/{report_id}/generate-direct", response_model=Dict[str, Any])
async def generate_report_direct(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate report directly (for testing/admin use)"""
    reports_service = ReportsService(db)
    
    # Verify user owns the report
    report = reports_service.get_report_by_id(report_id, current_user)
    
    # Generate directly
    result = await reports_service.generate_report_content_direct(report_id)
    
    return {
        "report_id": report_id,
        "status": "completed",
        "result": result
    }

@router.get("/", response_model=List[Report])
async def get_reports(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all reports for the current user"""
    reports_service = ReportsService(db)
    return reports_service.get_user_reports(current_user, skip, limit)

@router.get("/{report_id}", response_model=Report)
async def get_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific report by ID"""
    reports_service = ReportsService(db)
    return reports_service.get_report_by_id(report_id, current_user)

@router.get("/{report_id}/status", response_model=Dict[str, Any])
async def get_report_status(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed status of a report generation"""
    reports_service = ReportsService(db)
    
    # Verify user owns the report
    report = reports_service.get_report_by_id(report_id, current_user)
    
    # Get queue status if available
    queue_status = await reports_service.get_report_queue_status(report_id)
    
    return {
        "report_id": report_id,
        "database_status": report.status,
        "progress": report.progress,
        "queue_status": queue_status,
        "created_at": report.created_at.isoformat(),
        "updated_at": report.updated_at.isoformat() if report.updated_at else None,
        "error_message": report.error_message
    }

@router.get("/{report_id}/progress")
async def get_report_progress(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get report generation progress (legacy endpoint)"""
    reports_service = ReportsService(db)
    report = reports_service.get_report_by_id(report_id, current_user)
    
    return {
        "report_id": report.id,
        "status": report.status,
        "progress": report.progress,
        "error_message": report.error_message
    }

@router.post("/{report_id}/cancel", response_model=Dict[str, Any])
async def cancel_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Cancel a queued report generation"""
    reports_service = ReportsService(db)
    
    success = await reports_service.cancel_report_generation(report_id, current_user)
    
    return {
        "report_id": report_id,
        "cancelled": success,
        "message": "Report generation cancelled" if success else "Could not cancel report"
    }

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a report"""
    reports_service = ReportsService(db)
    reports_service.delete_report(report_id, current_user)

@router.post("/{report_id}/regenerate", response_model=Dict[str, Any])
async def regenerate_report(
    report_id: int,
    priority: str = "normal",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Regenerate report content"""
    reports_service = ReportsService(db)
    report = reports_service.get_report_by_id(report_id, current_user)
    
    # Reset report status
    report.status = "pending"
    report.progress = 0
    report.error_message = None
    report.external_id = None  # Clear old request ID
    db.commit()
    
    # Queue for regeneration
    result = await reports_service.queue_report_generation(report.id, priority)
    
    return {
        "report_id": report.id,
        "request_id": result["request_id"],
        "status": "queued",
        "message": "Report regeneration has been queued"
    }

@router.get("/queue/status", response_model=Dict[str, Any])
async def get_queue_status():
    """Get overall queue status (admin endpoint)"""
    return await queue_manager.get_queue_status()

@router.get("/user/queue-status", response_model=Dict[str, Any])
async def get_user_queue_status(
    current_user: User = Depends(get_current_user)
):
    """Get queue status for current user"""
    return await queue_manager.get_user_status(str(current_user.id))

@router.get("/metrics/service", response_model=Dict[str, Any])
async def get_service_metrics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get service performance metrics (admin endpoint)"""
    reports_service = ReportsService(db)
    return await reports_service.get_service_metrics()

@router.post("/{report_id}/pdf", response_model=Dict[str, Any])
async def generate_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate PDF version of report"""
    reports_service = ReportsService(db)
    pdf_path = await reports_service.generate_pdf_report(report_id, current_user)
    
    return {
        "message": "PDF generated successfully",
        "pdf_path": pdf_path,
        "download_url": f"/reports/{report_id}/download"
    }

@router.get("/{report_id}/download")
async def download_pdf(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download PDF report"""
    reports_service = ReportsService(db)
    report = reports_service.get_report_by_id(report_id, current_user)
    
    if not report.file_path:
        raise HTTPException(status_code=404, detail="PDF not available")
    
    return FileResponse(
        path=report.file_path,
        filename=f"{report.company.ticker}_report.pdf",
        media_type="application/pdf"
    )

@router.post("/{report_id}/customize", response_model=Dict[str, Any])
async def customize_report(
    report_id: int,
    customizations: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Apply customizations to report template"""
    reports_service = ReportsService(db)
    result = await reports_service.customize_report_template(report_id, customizations, current_user)
    
    return {
        "message": "Report customized successfully",
        "customized_content": result
    }

@router.get("/customizations/available", response_model=Dict[str, Any])
async def get_available_customizations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available report customization options"""
    reports_service = ReportsService(db)
    return reports_service.get_available_customizations()

@router.get("/structure/info", response_model=Dict[str, Any])
async def get_report_structure(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get information about report structure and sections"""
    reports_service = ReportsService(db)
    return await reports_service.get_report_structure_info()