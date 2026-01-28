"""
Reports API Endpoints with Kiro Integration
Provides REST API for report generation and management
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import uuid

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.services.report_generator import report_generator
from app.services.data_pipeline_integrator import data_pipeline_integrator
from app.services.websocket_manager import websocket_manager
from app.services.kiro_engine import kiro_engine
from app.worker.tasks import generate_report_task
from app.core.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()

# Request/Response Models
class ReportGenerationRequest(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol", min_length=1, max_length=10)
    report_type: str = Field(default="comprehensive", description="Type of report to generate")
    sections: Optional[List[str]] = Field(default=None, description="Specific sections to include")
    priority: str = Field(default="normal", description="Generation priority (low, normal, high)")

class ReportGenerationResponse(BaseModel):
    report_id: str
    ticker: str
    status: str
    message: str
    estimated_completion_time: Optional[str] = None
    progress_url: str
    websocket_url: str

class ReportStatusResponse(BaseModel):
    report_id: str
    ticker: str
    status: str
    progress: int
    message: str
    sections_completed: int
    total_sections: int
    estimated_time_remaining: Optional[int] = None
    error: Optional[str] = None

class ReportResponse(BaseModel):
    report_id: str
    ticker: str
    status: str
    report: Dict[str, Any]
    generation_time: float
    timestamp: str

@router.post("/generate", response_model=ReportGenerationResponse)
async def generate_report(
    request: ReportGenerationRequest,
    background_tasks: BackgroundTasks,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Generate a comprehensive stock research report
    
    This endpoint initiates the report generation process using Kiro CLI integration.
    The process runs asynchronously with real-time progress updates via WebSocket.
    """
    
    try:
        logger.info(f"Report generation requested for {request.ticker} by user {current_user.get('id')}")
        
        # Generate unique report ID
        report_id = str(uuid.uuid4())
        
        # Validate ticker format
        ticker = request.ticker.upper().strip()
        if not ticker.isalpha() or len(ticker) > 10:
            raise HTTPException(
                status_code=400,
                detail="Invalid ticker format. Must be 1-10 alphabetic characters."
            )
        
        # Prepare company data using data pipeline
        try:
            company_data = await data_pipeline_integrator.prepare_comprehensive_context(ticker)
        except Exception as e:
            logger.warning(f"Data pipeline preparation failed for {ticker}: {str(e)}")
            # Use fallback context
            company_data = {
                'ticker': ticker,
                'company_name': f"{ticker} Inc.",
                'sector': 'Unknown',
                'market_cap': 'Unknown',
                'current_price': 'Unknown',
                'business_description': 'Data gathering in progress...',
                'recent_news': 'News data being collected...',
                'financial_statements': 'Financial data being processed...',
                'historical_data': 'Historical analysis in progress...',
                'peer_data': 'Peer comparison being prepared...',
                'industry_averages': 'Industry data being analyzed...',
                'quarterly_results': 'Quarterly data being processed...',
                'guidance': 'Guidance information being collected...'
            }
        
        # Queue the report generation task
        if request.priority == "high":
            # Generate synchronously for high priority
            background_tasks.add_task(
                _generate_report_sync,
                ticker,
                company_data,
                current_user.get('id'),
                report_id
            )
        else:
            # Queue with Celery for normal/low priority
            generate_report_task.delay(
                ticker=ticker,
                company_data=company_data,
                user_id=current_user.get('id'),
                report_id=report_id
            )
        
        # Estimate completion time (5-8 minutes typical)
        estimated_completion = datetime.now().isoformat()
        
        return ReportGenerationResponse(
            report_id=report_id,
            ticker=ticker,
            status="queued",
            message=f"Report generation started for {ticker}",
            estimated_completion_time=estimated_completion,
            progress_url=f"/api/reports/{report_id}/status",
            websocket_url=f"/ws/reports/{report_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to initiate report generation for {request.ticker}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to initiate report generation: {str(e)}"
        )

@router.get("/{report_id}/status", response_model=ReportStatusResponse)
async def get_report_status(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get the current status of a report generation"""
    
    try:
        # Check report generator status
        status = report_generator.get_generation_status(report_id)
        
        if not status:
            # Check Celery task status
            from app.worker.tasks import celery_app
            task_result = celery_app.AsyncResult(report_id)
            
            if task_result.state == 'PENDING':
                return ReportStatusResponse(
                    report_id=report_id,
                    ticker="Unknown",
                    status="queued",
                    progress=0,
                    message="Report is queued for generation",
                    sections_completed=0,
                    total_sections=4
                )
            elif task_result.state == 'PROGRESS':
                meta = task_result.info or {}
                return ReportStatusResponse(
                    report_id=report_id,
                    ticker=meta.get('ticker', 'Unknown'),
                    status="generating",
                    progress=meta.get('current', 0),
                    message=meta.get('status', 'Generating report...'),
                    sections_completed=0,
                    total_sections=4
                )
            elif task_result.state == 'SUCCESS':
                result = task_result.result
                return ReportStatusResponse(
                    report_id=report_id,
                    ticker=result.get('ticker', 'Unknown'),
                    status="completed",
                    progress=100,
                    message="Report generation completed",
                    sections_completed=4,
                    total_sections=4
                )
            elif task_result.state == 'FAILURE':
                return ReportStatusResponse(
                    report_id=report_id,
                    ticker="Unknown",
                    status="failed",
                    progress=-1,
                    message="Report generation failed",
                    sections_completed=0,
                    total_sections=4,
                    error=str(task_result.info)
                )
            else:
                raise HTTPException(status_code=404, detail="Report not found")
        
        # Return status from report generator
        return ReportStatusResponse(
            report_id=report_id,
            ticker=status.get('ticker', 'Unknown'),
            status=status.get('status', 'unknown'),
            progress=status.get('progress', 0),
            message=status.get('status_message', 'Processing...'),
            sections_completed=0,  # Would need to calculate from status
            total_sections=4,
            error=status.get('error')
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get status for report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get report status: {str(e)}"
        )

@router.get("/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Retrieve a completed report"""
    
    try:
        # Check report generator first
        status = report_generator.get_generation_status(report_id)
        
        if status and status.get('status') == 'completed' and 'report' in status:
            return ReportResponse(
                report_id=report_id,
                ticker=status['ticker'],
                status="completed",
                report=status['report'],
                generation_time=(status['end_time'] - status['start_time']).total_seconds(),
                timestamp=status['end_time'].isoformat()
            )
        
        # Check Celery task result
        from app.worker.tasks import celery_app
        task_result = celery_app.AsyncResult(report_id)
        
        if task_result.state == 'SUCCESS':
            result = task_result.result
            return ReportResponse(
                report_id=report_id,
                ticker=result.get('ticker', 'Unknown'),
                status="completed",
                report=result.get('result', {}).get('report', {}),
                generation_time=result.get('result', {}).get('generation_time', 0),
                timestamp=result.get('completion_time', datetime.now().isoformat())
            )
        elif task_result.state in ['PENDING', 'PROGRESS']:
            raise HTTPException(
                status_code=202,
                detail="Report is still being generated"
            )
        elif task_result.state == 'FAILURE':
            raise HTTPException(
                status_code=500,
                detail=f"Report generation failed: {task_result.info}"
            )
        else:
            raise HTTPException(status_code=404, detail="Report not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve report: {str(e)}"
        )

@router.delete("/{report_id}")
async def delete_report(
    report_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a report and cancel generation if in progress"""
    
    try:
        # Cancel Celery task if running
        from app.worker.tasks import celery_app
        celery_app.control.revoke(report_id, terminate=True)
        
        # Remove from report generator tracking
        if report_id in report_generator.active_generations:
            del report_generator.active_generations[report_id]
        
        return {"message": f"Report {report_id} deleted successfully"}
        
    except Exception as e:
        logger.error(f"Failed to delete report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete report: {str(e)}"
        )

@router.get("/")
async def list_reports(
    current_user: Dict[str, Any] = Depends(get_current_user),
    limit: int = 10,
    offset: int = 0
):
    """List reports for the current user"""
    
    try:
        # This would typically query a database
        # For now, return active generations
        active_reports = []
        
        for report_id, status in report_generator.active_generations.items():
            if status.get('user_id') == current_user.get('id'):
                active_reports.append({
                    'report_id': report_id,
                    'ticker': status.get('ticker'),
                    'status': status.get('status'),
                    'progress': status.get('progress', 0),
                    'created_at': status.get('start_time', datetime.now()).isoformat()
                })
        
        return {
            'reports': active_reports[offset:offset+limit],
            'total': len(active_reports),
            'limit': limit,
            'offset': offset
        }
        
    except Exception as e:
        logger.error(f"Failed to list reports: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list reports: {str(e)}"
        )

@router.websocket("/ws/{report_id}")
async def websocket_endpoint(websocket: WebSocket, report_id: str):
    """WebSocket endpoint for real-time report generation updates"""
    
    try:
        # Handle WebSocket connection with report subscription
        await websocket_manager.connection_manager.connect(websocket)
        connection_id = list(websocket_manager.connection_manager.active_connections.keys())[-1]
        
        # Subscribe to report updates
        await websocket_manager.connection_manager.subscribe_to_report(connection_id, report_id)
        
        # Keep connection alive and handle client messages
        await websocket_manager.handle_websocket_connection(websocket)
        
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for report {report_id}")
    except Exception as e:
        logger.error(f"WebSocket error for report {report_id}: {str(e)}")

@router.get("/system/status")
async def get_system_status(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Get system status for Kiro integration"""
    
    try:
        # Validate Kiro setup
        kiro_status = await kiro_engine.validate_setup()
        
        # Get WebSocket stats
        ws_stats = websocket_manager.get_stats()
        
        # Get active generation count
        active_generations = len(report_generator.active_generations)
        
        return {
            'kiro_integration': kiro_status,
            'websocket_connections': ws_stats,
            'active_generations': active_generations,
            'system_health': 'healthy' if kiro_status.get('status') == 'success' else 'degraded',
            'timestamp': datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get system status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get system status: {str(e)}"
        )

# Helper functions
async def _generate_report_sync(
    ticker: str,
    company_data: Dict[str, Any],
    user_id: str,
    report_id: str
):
    """Generate report synchronously for high priority requests"""
    
    try:
        await report_generator.generate_comprehensive_report(
            ticker=ticker,
            company_data=company_data,
            user_id=user_id,
            report_id=report_id
        )
    except Exception as e:
        logger.error(f"Sync report generation failed for {ticker}: {str(e)}")