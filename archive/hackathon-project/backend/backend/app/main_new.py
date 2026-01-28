from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.shared.utils.logging import setup_logging
from app.shared.utils.exceptions import (
    http_exception_handler,
    validation_exception_handler,
    marketmind_exception_handler,
    general_exception_handler,
    MarketMindException
)

# Import process management
from app.core.process_manager import process_manager
from app.core.queue_manager import queue_manager
from app.services.kiro_process_service import kiro_process_service

# Import routers
from app.api.reports import router as reports_router
from app.features.charts.router import router as charts_router
from app.features.reports.router import router as new_reports_router

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="MarketMind Pro API",
    description="AI-Powered Stock Research Platform - Backend API with Robust Process Management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(MarketMindException, marketmind_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(reports_router, prefix="/api")
app.include_router(new_reports_router, prefix="/api/v2")  # New process-managed reports
app.include_router(charts_router, prefix="/api")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MarketMind Pro API",
        "version": "1.0.0",
        "status": "active",
        "features": [
            "Robust Process Management",
            "Queue-based Report Generation", 
            "Memory Leak Prevention",
            "Resource Monitoring",
            "Auto-restart on Failures"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with process metrics"""
    try:
        # Get process manager metrics
        process_metrics = process_manager.get_metrics()
        queue_status = await queue_manager.get_queue_status()
        service_metrics = kiro_process_service.get_service_metrics()
        
        return {
            "status": "healthy",
            "environment": settings.environment,
            "debug": settings.debug,
            "process_manager": process_metrics,
            "queue_manager": queue_status,
            "kiro_service": service_metrics
        }
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return {
            "status": "degraded",
            "error": str(e),
            "environment": settings.environment
        }

@app.on_event("startup")
async def startup_event():
    """Startup event handler - Initialize process management"""
    logger.info("MarketMind Pro API starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    try:
        # Start process management services
        logger.info("Initializing process management services...")
        
        await process_manager.start()
        logger.info("✓ Process Manager started")
        
        await queue_manager.start()
        logger.info("✓ Queue Manager started")
        
        await kiro_process_service.start()
        logger.info("✓ Kiro Process Service started")
        
        logger.info("🚀 All process management services initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize process management: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler - Cleanup process management"""
    logger.info("MarketMind Pro API shutting down...")
    
    try:
        # Stop process management services
        logger.info("Stopping process management services...")
        
        await kiro_process_service.stop()
        logger.info("✓ Kiro Process Service stopped")
        
        await queue_manager.stop()
        logger.info("✓ Queue Manager stopped")
        
        await process_manager.stop()
        logger.info("✓ Process Manager stopped")
        
        logger.info("🛑 All process management services stopped cleanly")
        
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )