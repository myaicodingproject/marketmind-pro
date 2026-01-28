"""
MarketMind Pro Production API Router
Centralized routing for all API endpoints
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, JSONResponse
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
import os

from app.core.production_config import settings
from app.services.financial_data import financial_service
from app.services.websocket_report_service import WebSocketReportService
from app.api.websocket_endpoints import websocket_manager
from real_kiro_agents import REAL_KIRO_AGENTS
from quality_gate_system import QualityGateSystem
from simple_pdf_generator import generate_institutional_pdf

logger = logging.getLogger(__name__)

# Create main router
api_router = APIRouter(prefix="/api/v1")

# Sub-routers for different features
financial_router = APIRouter(prefix="/financial", tags=["Financial Data"])
reports_router = APIRouter(prefix="/reports", tags=["Reports"])
admin_router = APIRouter(prefix="/admin", tags=["Administration"])
websocket_router = APIRouter(prefix="/ws", tags=["WebSocket"])

# Storage (in production, use Redis or database)
active_reports: Dict[str, Dict[str, Any]] = {}
completed_reports: Dict[str, Dict[str, Any]] = {}

# Services
quality_system = QualityGateSystem()
websocket_service = WebSocketReportService()

# Request/Response Models
from pydantic import BaseModel

class ReportRequest(BaseModel):
    ticker: str
    report_type: Optional[str] = "comprehensive"
    quality_level: Optional[str] = "production"
    include_pdf: Optional[bool] = True
    sections: Optional[List[str]] = None

class ReportResponse(BaseModel):
    report_id: str
    status: str
    message: str
    websocket_url: str
    status_url: str

class ReportStatus(BaseModel):
    id: str
    ticker: str
    status: str
    progress: float
    current_section: Optional[str] = None
    sections_completed: List[str] = []
    created_at: str
    completed_at: Optional[str] = None
    error: Optional[str] = None

# Financial Data Endpoints
@financial_router.get("/stock/{ticker}")
async def get_stock_data(ticker: str):
    """Get real-time stock data"""
    try:
        data = await financial_service.get_stock_data(ticker.upper())
        if not data:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
        return data
    except Exception as e:
        logger.error(f"Financial data error for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/comprehensive/{ticker}")
async def get_comprehensive_data(ticker: str):
    """Get comprehensive financial data including metrics and statements"""
    try:
        data = await financial_service.get_comprehensive_data(ticker.upper())
        if not data:
            raise HTTPException(status_code=404, detail=f"No comprehensive data found for {ticker}")
        return data
    except Exception as e:
        logger.error(f"Comprehensive data error for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@financial_router.get("/metrics/{ticker}")
async def get_financial_metrics(ticker: str):
    """Get key financial metrics and ratios"""
    try:
        data = await financial_service.get_financial_metrics(ticker.upper())
        if not data:
            raise HTTPException(status_code=404, detail=f"No metrics found for {ticker}")
        return data
    except Exception as e:
        logger.error(f"Metrics error for {ticker}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Report Generation Endpoints
@reports_router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks
):
    """Generate a comprehensive stock analysis report"""
    try:
        # Validate ticker
        if not request.ticker or len(request.ticker) > 10:
            raise HTTPException(status_code=400, detail="Invalid ticker symbol")
        
        # Check concurrent report limit
        if len(active_reports) >= settings.MAX_CONCURRENT_REPORTS:
            raise HTTPException(
                status_code=429, 
                detail=f"Maximum concurrent reports ({settings.MAX_CONCURRENT_REPORTS}) reached"
            )
        
        # Generate unique report ID
        report_id = f"{request.ticker}_{int(datetime.now().timestamp())}"
        
        # Initialize report tracking
        active_reports[report_id] = {
            "id": report_id,
            "ticker": request.ticker.upper(),
            "status": "initializing",
            "progress": 0.0,
            "created_at": datetime.now().isoformat(),
            "sections_completed": [],
            "current_section": None,
            "request": request.dict()
        }
        
        # Start report generation in background
        background_tasks.add_task(
            process_report_generation,
            report_id,
            request
        )
        
        return ReportResponse(
            report_id=report_id,
            status="started",
            message=f"Report generation started for {request.ticker.upper()}",
            websocket_url=f"/ws/{report_id}",
            status_url=f"/api/v1/reports/{report_id}/status"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@reports_router.get("/{report_id}/status", response_model=ReportStatus)
async def get_report_status(report_id: str):
    """Get current status of report generation"""
    if report_id in active_reports:
        report = active_reports[report_id]
        return ReportStatus(**report)
    elif report_id in completed_reports:
        report = completed_reports[report_id]
        return ReportStatus(**report)
    else:
        raise HTTPException(status_code=404, detail="Report not found")

@reports_router.get("/{report_id}/data")
async def get_report_data(report_id: str):
    """Get the generated report data"""
    if report_id not in completed_reports:
        raise HTTPException(status_code=404, detail="Report not found or not completed")
    
    report = completed_reports[report_id]
    if report["status"] != "completed":
        raise HTTPException(status_code=400, detail="Report not completed successfully")
    
    return {
        "report_id": report_id,
        "ticker": report["ticker"],
        "data": report.get("data", {}),
        "quality_metrics": report.get("quality_metrics", {}),
        "completed_at": report["completed_at"]
    }

@reports_router.get("/{report_id}/download")
async def download_report(report_id: str):
    """Download the PDF report"""
    if report_id not in completed_reports:
        raise HTTPException(status_code=404, detail="Report not found or not completed")
    
    report = completed_reports[report_id]
    if "pdf_path" not in report or not report["pdf_path"]:
        raise HTTPException(status_code=404, detail="PDF not available for this report")
    
    pdf_path = report["pdf_path"]
    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found on disk")
    
    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"MarketMind_Pro_{report['ticker']}_{report_id}.pdf"
    )

@reports_router.delete("/{report_id}")
async def cancel_report(report_id: str):
    """Cancel an active report or delete a completed one"""
    deleted = False
    
    if report_id in active_reports:
        # Cancel active report
        active_reports[report_id]["status"] = "cancelled"
        await websocket_manager.broadcast_to_client(report_id, {
            "type": "cancelled",
            "status": "Report generation cancelled"
        })
        del active_reports[report_id]
        deleted = True
    
    if report_id in completed_reports:
        # Delete completed report and PDF
        report = completed_reports[report_id]
        if "pdf_path" in report and os.path.exists(report["pdf_path"]):
            try:
                os.remove(report["pdf_path"])
            except Exception as e:
                logger.warning(f"Failed to delete PDF {report['pdf_path']}: {e}")
        del completed_reports[report_id]
        deleted = True
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {"message": f"Report {report_id} deleted successfully"}

# Admin Endpoints
@admin_router.get("/reports")
async def list_all_reports():
    """List all reports (admin only)"""
    return {
        "active_reports": list(active_reports.values()),
        "completed_reports": list(completed_reports.values()),
        "statistics": {
            "total_active": len(active_reports),
            "total_completed": len(completed_reports),
            "success_rate": calculate_success_rate()
        }
    }

@admin_router.get("/system/status")
async def get_system_status():
    """Get comprehensive system status"""
    try:
        # Test financial service
        financial_status = "healthy"
        try:
            test_data = await financial_service.get_stock_data("AAPL")
            if not test_data:
                financial_status = "degraded"
        except Exception:
            financial_status = "unhealthy"
        
        return {
            "status": "operational",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "financial_data": financial_status,
                "report_generation": "healthy",
                "quality_system": "healthy",
                "websocket": "healthy"
            },
            "metrics": {
                "active_reports": len(active_reports),
                "completed_reports": len(completed_reports),
                "success_rate": calculate_success_rate(),
                "uptime": "N/A"  # Would implement proper uptime tracking
            },
            "limits": {
                "max_concurrent_reports": settings.MAX_CONCURRENT_REPORTS,
                "report_timeout_minutes": settings.REPORT_TIMEOUT_MINUTES
            }
        }
    except Exception as e:
        logger.error(f"System status check failed: {e}")
        raise HTTPException(status_code=503, detail=f"System status unavailable: {e}")

@admin_router.post("/system/cleanup")
async def cleanup_old_reports():
    """Clean up old completed reports"""
    cleaned = 0
    cutoff_time = datetime.now().timestamp() - (24 * 60 * 60)  # 24 hours ago
    
    to_remove = []
    for report_id, report in completed_reports.items():
        try:
            created_timestamp = datetime.fromisoformat(report["created_at"]).timestamp()
            if created_timestamp < cutoff_time:
                # Delete PDF if exists
                if "pdf_path" in report and os.path.exists(report["pdf_path"]):
                    os.remove(report["pdf_path"])
                to_remove.append(report_id)
                cleaned += 1
        except Exception as e:
            logger.warning(f"Error cleaning report {report_id}: {e}")
    
    for report_id in to_remove:
        del completed_reports[report_id]
    
    return {
        "message": f"Cleaned up {cleaned} old reports",
        "remaining_reports": len(completed_reports)
    }

# Helper Functions
def calculate_success_rate() -> float:
    """Calculate report generation success rate"""
    if not completed_reports:
        return 100.0
    
    successful = sum(1 for report in completed_reports.values() 
                    if report.get("status") == "completed")
    return (successful / len(completed_reports)) * 100.0

async def process_report_generation(report_id: str, request: ReportRequest):
    """Background task for report generation with real-time updates"""
    try:
        logger.info(f"Starting report generation for {report_id}")
        
        # Update status: gathering data
        active_reports[report_id].update({
            "status": "gathering_data",
            "progress": 10.0,
            "current_section": "data_collection"
        })
        
        await websocket_manager.broadcast_to_client(report_id, {
            "type": "progress",
            "progress": 10.0,
            "status": "Gathering financial data...",
            "current_section": "data_collection"
        })
        
        # Get comprehensive financial data
        financial_data = await financial_service.get_comprehensive_data(request.ticker)
        if not financial_data:
            raise Exception(f"No financial data available for {request.ticker}")
        
        # Update progress: AI analysis
        active_reports[report_id].update({
            "status": "ai_analysis",
            "progress": 25.0,
            "current_section": "ai_processing"
        })
        
        await websocket_manager.broadcast_to_client(report_id, {
            "type": "progress",
            "progress": 25.0,
            "status": "Running AI analysis...",
            "current_section": "ai_processing"
        })
        
        # Generate report sections
        sections = request.sections or [
            "executive_summary",
            "financial_analysis", 
            "market_analysis",
            "competitive_analysis",
            "risk_assessment",
            "valuation_analysis"
        ]
        
        report_data = {}
        section_progress_step = 50.0 / len(sections)
        
        for i, section in enumerate(sections):
            progress = 25.0 + (i + 1) * section_progress_step
            
            active_reports[report_id].update({
                "current_section": section,
                "progress": progress
            })
            
            await websocket_manager.broadcast_to_client(report_id, {
                "type": "progress",
                "progress": progress,
                "status": f"Generating {section.replace('_', ' ').title()}...",
                "current_section": section
            })
            
            # Generate section using appropriate agent
            section_data = await generate_section_with_agent(
                section, request.ticker, financial_data
            )
            
            report_data[section] = section_data
            active_reports[report_id]["sections_completed"].append(section)
        
        # Quality validation
        active_reports[report_id].update({
            "status": "quality_check",
            "progress": 85.0,
            "current_section": "quality_validation"
        })
        
        await websocket_manager.broadcast_to_client(report_id, {
            "type": "progress",
            "progress": 85.0,
            "status": "Running quality checks...",
            "current_section": "quality_validation"
        })
        
        quality_results = await quality_system.validate_report(report_data)
        report_data["quality_metrics"] = quality_results
        
        # Generate PDF if requested
        pdf_path = None
        if request.include_pdf:
            active_reports[report_id].update({
                "status": "generating_pdf",
                "progress": 95.0,
                "current_section": "pdf_generation"
            })
            
            await websocket_manager.broadcast_to_client(report_id, {
                "type": "progress",
                "progress": 95.0,
                "status": "Generating PDF report...",
                "current_section": "pdf_generation"
            })
            
            pdf_path = generate_institutional_pdf(request.ticker, report_data)
        
        # Complete the report
        completed_report = {
            "id": report_id,
            "ticker": request.ticker.upper(),
            "status": "completed",
            "progress": 100.0,
            "created_at": active_reports[report_id]["created_at"],
            "completed_at": datetime.now().isoformat(),
            "sections_completed": list(report_data.keys()),
            "data": report_data,
            "pdf_path": pdf_path,
            "quality_metrics": quality_results
        }
        
        completed_reports[report_id] = completed_report
        if report_id in active_reports:
            del active_reports[report_id]
        
        # Send completion notification
        await websocket_manager.broadcast_to_client(report_id, {
            "type": "completed",
            "progress": 100.0,
            "status": "Report completed successfully!",
            "download_url": f"/api/v1/reports/{report_id}/download" if pdf_path else None,
            "data_url": f"/api/v1/reports/{report_id}/data"
        })
        
        logger.info(f"Report {report_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Report generation failed for {report_id}: {e}")
        
        # Update with error
        error_report = {
            "id": report_id,
            "ticker": request.ticker.upper(),
            "status": "failed",
            "progress": 0.0,
            "error": str(e),
            "created_at": active_reports[report_id]["created_at"],
            "failed_at": datetime.now().isoformat(),
            "sections_completed": active_reports[report_id].get("sections_completed", [])
        }
        
        completed_reports[report_id] = error_report
        if report_id in active_reports:
            del active_reports[report_id]
        
        await websocket_manager.broadcast_to_client(report_id, {
            "type": "error",
            "status": "Report generation failed",
            "error": str(e)
        })

async def generate_section_with_agent(section: str, ticker: str, financial_data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate a report section using the appropriate Kiro agent"""
    try:
        # Map sections to agents
        agent_mapping = {
            "executive_summary": "section_1_agent",
            "financial_analysis": "section_2_agent", 
            "market_analysis": "section_3_agent",
            "competitive_analysis": "section_4_agent",
            "risk_assessment": "section_5_agent",
            "valuation_analysis": "section_6_agent"
        }
        
        agent_name = agent_mapping.get(section, "section_1_agent")
        
        if agent_name in REAL_KIRO_AGENTS:
            agent = REAL_KIRO_AGENTS[agent_name]
            return await agent.generate_analysis(ticker, financial_data)
        else:
            # Fallback content
            return {
                "title": section.replace("_", " ").title(),
                "content": f"Analysis for {section} of {ticker}",
                "key_points": [f"Key insight for {section}"],
                "generated_at": datetime.now().isoformat()
            }
    except Exception as e:
        logger.error(f"Error generating section {section}: {e}")
        return {
            "title": section.replace("_", " ").title(),
            "content": f"Error generating {section}: {str(e)}",
            "error": True,
            "generated_at": datetime.now().isoformat()
        }

# Include all routers in the main API router
api_router.include_router(financial_router)
api_router.include_router(reports_router)
api_router.include_router(admin_router)