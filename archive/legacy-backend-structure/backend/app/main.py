from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os
import asyncio
import httpx
from typing import Dict, Any

from app.core.config import settings
from app.core.database import init_db
from app.core.unified_api import create_unified_api
from app.core.auth import get_current_active_user
from app.features.auth.models import User
from app.features.auth.router import router as auth_router
from app.features.reports.router import router as reports_router
from app.features.companies.router import router as companies_router
from app.api.queue_routes import router as queue_router
from app.api.chart_routes import router as chart_router

# Create logs directory
os.makedirs("logs", exist_ok=True)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global unified API instance
unified_api = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global unified_api
    
    # Startup
    logger.info("Starting MarketMind Pro API with Core Integration and Queue System")
    
    # Initialize database
    await init_db()
    
    # Initialize unified API system
    unified_api = create_unified_api(app)
    await unified_api.initialize()
    
    # Initialize queue system maintenance
    from app.core.queue_recovery import scheduled_maintenance
    asyncio.create_task(scheduled_maintenance())
    
    logger.info("MarketMind Pro API fully initialized with queue system")
    
    yield
    
    # Shutdown
    logger.info("Shutting down MarketMind Pro API")
    if unified_api:
        await unified_api.shutdown()

app = FastAPI(
    title="MarketMind Pro API",
    description="AI-Powered Stock Research Platform with Advanced Queue System",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Feature routers (legacy support)
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(companies_router, prefix="/api/companies", tags=["companies"])
app.include_router(queue_router, prefix="/api", tags=["queue"])
app.include_router(chart_router, prefix="/api", tags=["charts"])

# The unified API routes are automatically added by the UnifiedAPI class

@app.post("/api/v1/reports/{report_id}/pdf")
async def generate_report_pdf(
    report_id: str, 
    request: Dict[str, Any], 
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user)
):
    """Generate PDF report using enhanced Puppeteer service"""
    try:
        # Check if user owns this report
        if not report_id.startswith(f"{current_user.id}_"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Validate report exists
        if not report_id:
            raise HTTPException(status_code=400, detail="Report ID is required")
        
        # Forward request to PDF generator service with enhanced error handling
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"http://localhost:8002/api/v1/reports/{report_id}/pdf",
                json=request,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"PDF generation started for report {report_id}, job_id: {result.get('job_id')}")
                return result
            else:
                error_detail = response.text
                logger.error(f"PDF service error for report {report_id}: {error_detail}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"PDF generation failed: {error_detail}"
                )
                
    except httpx.TimeoutException:
        logger.error(f"Timeout connecting to PDF service for report {report_id}")
        raise HTTPException(
            status_code=504,
            detail="PDF generation service timeout"
        )
    except httpx.RequestError as e:
        logger.error(f"Error connecting to PDF service for report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="PDF generation service unavailable"
        )
    except Exception as e:
        logger.error(f"Unexpected error generating PDF for report {report_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF generation failed: {str(e)}"
        )

@app.get("/api/v1/reports/{report_id}/pdf/status/{job_id}")
async def get_pdf_status(
    report_id: str, 
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get PDF generation status"""
    try:
        # Check if user owns this report
        if not report_id.startswith(f"{current_user.id}_"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8002/api/v1/status/{job_id}",
                timeout=10.0
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Status check failed: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Error connecting to PDF service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="PDF generation service unavailable"
        )

@app.get("/api/v1/reports/{report_id}/pdf/download/{job_id}")
async def download_pdf(
    report_id: str, 
    job_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Download generated PDF"""
    try:
        # Check if user owns this report
        if not report_id.startswith(f"{current_user.id}_"):
            raise HTTPException(status_code=403, detail="Access denied")
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"http://localhost:8002/api/v1/download/{job_id}",
                timeout=30.0
            )
            
            if response.status_code == 200:
                from fastapi.responses import Response
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=report_{report_id}.pdf"}
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Download failed: {response.text}"
                )
                
    except httpx.RequestError as e:
        logger.error(f"Error connecting to PDF service: {str(e)}")
        raise HTTPException(
            status_code=503,
            detail="PDF generation service unavailable"
        )

@app.get("/api/system/status")
async def system_status():
    """Get comprehensive system status including queue health"""
    from app.core.queue_system import QueueManager
    from app.core.queue_recovery import QueueRecoveryManager
    
    try:
        queue_manager = QueueManager("redis://localhost:6379/0")
        recovery_manager = QueueRecoveryManager("redis://localhost:6379/0")
        
        queue_stats = await queue_manager.get_queue_stats()
        recovery_status = await recovery_manager.get_recovery_status()
        
        return {
            "api_status": "healthy",
            "queue_stats": queue_stats,
            "recovery_status": recovery_status,
            "timestamp": queue_stats["timestamp"]
        }
    except Exception as e:
        logger.error(f"Error getting system status: {str(e)}")
        return {
            "api_status": "healthy",
            "queue_status": "error",
            "error": str(e)
        }