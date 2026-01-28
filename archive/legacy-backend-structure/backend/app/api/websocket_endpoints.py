"""
WebSocket API endpoints for real-time progress updates
"""

import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from typing import Optional
from app.core.websocket_progress_manager import progress_manager, ProgressStage

logger = logging.getLogger(__name__)
router = APIRouter()

@router.websocket("/ws/reports/{report_id}")
async def websocket_report_progress(websocket: WebSocket, report_id: str, user_id: Optional[str] = None):
    """WebSocket endpoint for real-time report generation progress"""
    
    try:
        # Connect to progress manager
        await progress_manager.connect(websocket, report_id, user_id)
        
        # Keep connection alive and handle messages
        while True:
            try:
                # Wait for messages from client
                data = await websocket.receive_text()
                message = json.loads(data)
                
                # Handle incoming message
                await progress_manager.handle_websocket_message(websocket, message)
                
            except WebSocketDisconnect:
                logger.info(f"WebSocket disconnected for report {report_id}")
                break
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON received from WebSocket for report {report_id}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON format"}
                })
            except Exception as e:
                logger.error(f"Error in WebSocket message handling: {str(e)}")
                await websocket.send_json({
                    "type": "error", 
                    "data": {"message": "Internal server error"}
                })
                break
    
    except Exception as e:
        logger.error(f"Error in WebSocket connection: {str(e)}")
    
    finally:
        # Clean up connection
        await progress_manager.disconnect(websocket)

@router.get("/api/reports/{report_id}/progress")
async def get_report_progress(report_id: str):
    """HTTP endpoint to get current progress for a report"""
    
    progress = progress_manager.get_report_progress(report_id)
    
    if not progress:
        raise HTTPException(status_code=404, detail="Report progress not found")
    
    return {
        "report_id": report_id,
        "progress": progress,
        "active_connections": progress_manager.get_active_connections_count(report_id)
    }

@router.post("/api/reports/{report_id}/progress")
async def update_report_progress(
    report_id: str,
    stage: str,
    progress: int,
    message: str,
    section_data: Optional[dict] = None,
    error_details: Optional[dict] = None
):
    """HTTP endpoint to update report progress (for internal use)"""
    
    try:
        progress_stage = ProgressStage(stage)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {stage}")
    
    if not 0 <= progress <= 100:
        raise HTTPException(status_code=400, detail="Progress must be between 0 and 100")
    
    await progress_manager.update_progress(
        report_id=report_id,
        stage=progress_stage,
        progress=progress,
        message=message,
        section_data=section_data,
        error_details=error_details
    )
    
    return {
        "success": True,
        "report_id": report_id,
        "stage": stage,
        "progress": progress,
        "message": message
    }

@router.post("/api/reports/{report_id}/sections/{section_name}/progress")
async def update_section_progress(
    report_id: str,
    section_name: str,
    section_progress: int,
    section_status: str,
    validation_results: Optional[dict] = None
):
    """HTTP endpoint to update section-specific progress"""
    
    if not 0 <= section_progress <= 100:
        raise HTTPException(status_code=400, detail="Section progress must be between 0 and 100")
    
    await progress_manager.update_section_progress(
        report_id=report_id,
        section_name=section_name,
        section_progress=section_progress,
        section_status=section_status,
        validation_results=validation_results
    )
    
    return {
        "success": True,
        "report_id": report_id,
        "section_name": section_name,
        "progress": section_progress,
        "status": section_status
    }

@router.post("/api/reports/{report_id}/quality-validation")
async def update_quality_validation(
    report_id: str,
    validation_stage: str,
    validation_progress: int,
    validation_results: dict
):
    """HTTP endpoint to update quality validation progress"""
    
    if not 0 <= validation_progress <= 100:
        raise HTTPException(status_code=400, detail="Validation progress must be between 0 and 100")
    
    await progress_manager.update_quality_validation(
        report_id=report_id,
        validation_stage=validation_stage,
        validation_progress=validation_progress,
        validation_results=validation_results
    )
    
    return {
        "success": True,
        "report_id": report_id,
        "validation_stage": validation_stage,
        "progress": validation_progress
    }

@router.post("/api/reports/{report_id}/complete")
async def complete_report(
    report_id: str,
    success: bool,
    report_url: Optional[str] = None,
    error_message: Optional[str] = None
):
    """HTTP endpoint to mark report as completed"""
    
    await progress_manager.report_completed(
        report_id=report_id,
        success=success,
        report_url=report_url,
        error_message=error_message
    )
    
    return {
        "success": True,
        "report_id": report_id,
        "completed": success,
        "report_url": report_url
    }

@router.get("/api/websocket/stats")
async def get_websocket_stats():
    """Get WebSocket connection statistics"""
    
    total_connections = sum(
        progress_manager.get_active_connections_count(report_id)
        for report_id in progress_manager.active_connections.keys()
    )
    
    return {
        "total_connections": total_connections,
        "active_reports": len(progress_manager.active_connections),
        "tracked_reports": len(progress_manager.report_progress)
    }