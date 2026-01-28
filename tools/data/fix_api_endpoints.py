#!/usr/bin/env python3
"""
Fix API endpoint mismatches between frontend and backend
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.core.auth import get_current_active_user
from app.models.user import User
from app.schemas.report import ReportRequest, ReportResponse
import uuid
from datetime import datetime

# Create the missing progress endpoint
reports_router = APIRouter(prefix="/api/v1/reports", tags=["reports"])

# Global storage for progress (should be Redis/DB in production)
progress_storage = {}
active_reports = {}

@reports_router.post("/generate")
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Generate stock research report - matches frontend expectation"""
    
    # Generate report ID
    report_id = f"{current_user.id}_{request.ticker}_{int(datetime.now().timestamp())}"
    
    # Initialize progress tracking
    progress_storage[report_id] = {
        "progress": 0,
        "stage": "initializing",
        "message": "Starting report generation...",
        "status": "in_progress",
        "activity_log": ["Report generation initiated"],
        "ticker": request.ticker,
        "user_id": current_user.id
    }
    
    # Start background task
    background_tasks.add_task(process_report_generation, report_id, request)
    
    return ReportResponse(
        report_id=report_id,
        status="initiated",
        message="Report generation started",
        websocket_url=f"/ws/reports/{report_id}"
    )

@reports_router.get("/progress/{report_id}")
async def get_report_progress(
    report_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get report generation progress - MISSING ENDPOINT ADDED"""
    
    if report_id not in progress_storage:
        raise HTTPException(status_code=404, detail="Report not found")
    
    progress_data = progress_storage[report_id]
    
    # Verify user owns this report
    if progress_data.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "progress": progress_data.get("progress", 0),
        "stage": progress_data.get("stage", "unknown"),
        "message": progress_data.get("message", "Processing..."),
        "status": progress_data.get("status", "in_progress"),
        "activity_log": progress_data.get("activity_log", []),
        "ticker": progress_data.get("ticker", "")
    }

@reports_router.get("/{report_id}")
async def get_report(
    report_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get completed report data - matches frontend expectation"""
    
    if report_id not in active_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report_data = active_reports[report_id]
    
    # Verify user owns this report
    if report_data.get("user_id") != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return report_data

async def process_report_generation(report_id: str, request: ReportRequest):
    """Background task for report generation"""
    try:
        # Import here to avoid circular imports
        from real_kiro_agents import REAL_KIRO_AGENTS
        import asyncio
        
        ticker = request.ticker
        
        # Update progress: Starting
        progress_storage[report_id].update({
            "progress": 10,
            "stage": "launching_agents",
            "message": f"Launching 8 Kiro CLI agents for {ticker}...",
            "activity_log": progress_storage[report_id]["activity_log"] + [
                f"🚀 Starting analysis for {ticker}",
                f"📝 Launching 8 parallel Kiro CLI agents..."
            ]
        })
        
        # Execute Kiro agents in parallel
        tasks = []
        for section_id, agent in REAL_KIRO_AGENTS.items():
            task = asyncio.create_task(
                agent.generate_analysis(ticker, progress_storage, report_id)
            )
            tasks.append((section_id, task))
        
        # Update progress: Executing
        progress_storage[report_id].update({
            "progress": 25,
            "stage": "executing_analysis",
            "message": "Kiro CLI agents processing...",
        })
        
        # Wait for all agents to complete
        results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)
        
        # Combine results
        all_sections = {}
        for i, (section_id, _) in enumerate(tasks):
            if i < len(results) and not isinstance(results[i], Exception):
                all_sections[section_id] = results[i]
        
        # Update progress: Compiling
        progress_storage[report_id].update({
            "progress": 85,
            "stage": "compiling_report",
            "message": "Compiling final report...",
        })
        
        # Create final report
        final_report = {
            "report_id": report_id,
            "ticker": ticker,
            "title": f"{ticker} - Comprehensive Stock Analysis Report",
            "sections": all_sections,
            "generated_at": datetime.now().isoformat(),
            "user_id": progress_storage[report_id]["user_id"]
        }
        
        # Store completed report
        active_reports[report_id] = final_report
        
        # Update progress: Complete
        progress_storage[report_id].update({
            "progress": 100,
            "stage": "completed",
            "status": "completed",
            "message": "Report generation complete!",
            "activity_log": progress_storage[report_id]["activity_log"] + [
                "✅ All sections completed",
                "📄 Report compiled successfully",
                "🎉 Ready for download"
            ]
        })
        
    except Exception as e:
        # Handle errors
        progress_storage[report_id].update({
            "progress": 0,
            "stage": "error",
            "status": "error",
            "message": f"Error: {str(e)}",
            "activity_log": progress_storage[report_id]["activity_log"] + [
                f"❌ Error occurred: {str(e)}"
            ]
        })

if __name__ == "__main__":
    print("API endpoint fixes created. Add this router to your main FastAPI app.")
