# Queue Monitoring and Management API

from fastapi import APIRouter, HTTPException, Depends, WebSocket, WebSocketDisconnect
from typing import Dict, List, Optional
from datetime import datetime
import logging

from app.core.queue_system import QueueManager, UserTier
from app.core.websocket_manager import websocket_manager
from app.core.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize queue manager
queue_manager = QueueManager("redis://localhost:6379/0")

@router.post("/reports/generate")
async def generate_report(
    ticker: str,
    user_tier: UserTier = UserTier.FREE,
    current_user: dict = Depends(get_current_user)
):
    """Generate a new stock report with queue management"""
    try:
        job_id = await queue_manager.enqueue_job(
            ticker=ticker.upper(),
            user_id=current_user["user_id"],
            user_tier=user_tier
        )
        
        return {
            "job_id": job_id,
            "status": "queued",
            "message": "Report generation started",
            "websocket_url": f"/ws/progress/{job_id}"
        }
    
    except ValueError as e:
        raise HTTPException(status_code=429, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating report: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/reports/{job_id}/status")
async def get_job_status(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get the current status of a report generation job"""
    job_status = await queue_manager.get_job_status(job_id)
    
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Verify job belongs to user (or user is admin)
    if job_status["user_id"] != current_user["user_id"] and not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied")
    
    return job_status

@router.delete("/reports/{job_id}")
async def cancel_job(
    job_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a queued or processing job"""
    success = await queue_manager.cancel_job(job_id, current_user["user_id"])
    
    if not success:
        raise HTTPException(status_code=400, detail="Cannot cancel job")
    
    return {"message": "Job cancelled successfully"}

@router.get("/queue/stats")
async def get_queue_stats(current_user: dict = Depends(get_current_user)):
    """Get comprehensive queue statistics"""
    stats = await queue_manager.get_queue_stats()
    
    # Add user-specific stats
    user_id = current_user["user_id"]
    user_stats = await _get_user_stats(user_id)
    stats["user_stats"] = user_stats
    
    return stats

@router.get("/admin/queue/management")
async def admin_queue_management(current_user: dict = Depends(get_current_user)):
    """Admin endpoint for queue management (requires admin privileges)"""
    if not current_user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Get detailed queue information
    stats = await queue_manager.get_queue_stats()
    
    # Get active jobs details
    active_jobs = await _get_active_jobs_details()
    
    # Get failed jobs in last 24 hours
    failed_jobs = await _get_recent_failed_jobs()
    
    return {
        "queue_stats": stats,
        "active_jobs": active_jobs,
        "recent_failures": failed_jobs,
        "system_health": await _get_system_health()
    }

@router.websocket("/ws/progress/{job_id}")
async def websocket_progress(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time progress updates"""
    await websocket_manager.connect(websocket, job_id)
    
    try:
        # Send initial job status
        job_status = await queue_manager.get_job_status(job_id)
        if job_status:
            await websocket.send_json({
                "type": "status",
                "data": job_status
            })
        
        # Keep connection alive and handle client messages
        while True:
            try:
                data = await websocket.receive_text()
                # Handle client messages if needed (e.g., ping/pong)
                if data == "ping":
                    await websocket.send_text("pong")
            except WebSocketDisconnect:
                break
    
    except Exception as e:
        logger.error(f"WebSocket error for job {job_id}: {str(e)}")
    
    finally:
        await websocket_manager.disconnect(websocket, job_id)

async def _get_user_stats(user_id: str) -> Dict:
    """Get user-specific queue statistics"""
    from app.core.queue_system import redis
    
    # Get user's active jobs
    active_jobs = await redis.smembers(f"user_active:{user_id}")
    
    # Get today's job count
    today = datetime.utcnow().date().isoformat()
    daily_count = await redis.get(f"user_daily:{user_id}:{today}")
    
    return {
        "active_jobs_count": len(active_jobs) if active_jobs else 0,
        "daily_jobs_count": int(daily_count) if daily_count else 0,
        "active_job_ids": [job.decode() for job in active_jobs] if active_jobs else []
    }

async def _get_active_jobs_details() -> List[Dict]:
    """Get detailed information about active jobs"""
    from app.core.queue_system import redis
    
    active_job_ids = await redis.smembers("active_jobs")
    jobs = []
    
    for job_id in active_job_ids:
        job_data = await redis.hgetall(f"job:{job_id.decode()}")
        if job_data:
            jobs.append({k.decode(): v.decode() for k, v in job_data.items()})
    
    return jobs

async def _get_recent_failed_jobs() -> List[Dict]:
    """Get failed jobs from the last 24 hours"""
    # This would require a more sophisticated tracking system
    # For now, return empty list
    return []

async def _get_system_health() -> Dict:
    """Get system health metrics"""
    import psutil
    
    return {
        "cpu_percent": psutil.cpu_percent(interval=1),
        "memory": {
            "percent": psutil.virtual_memory().percent,
            "available_gb": psutil.virtual_memory().available / (1024**3)
        },
        "disk": {
            "percent": psutil.disk_usage('/').percent,
            "free_gb": psutil.disk_usage('/').free / (1024**3)
        },
        "timestamp": datetime.utcnow().isoformat()
    }