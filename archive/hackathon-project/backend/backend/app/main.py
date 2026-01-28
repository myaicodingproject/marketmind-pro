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

# Import routers
from app.api.reports import router as reports_router
from app.features.charts.router import router as charts_router
from app.api.financial_routes import router as financial_router

# Setup logging
logger = setup_logging()

# Create FastAPI app
app = FastAPI(
    title="MarketMind Pro API",
    description="AI-Powered Stock Research Platform - Backend API",
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
app.include_router(reports_router, prefix="/api/reports", tags=["reports"])
app.include_router(charts_router, prefix="/api")
app.include_router(financial_router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "MarketMind Pro API",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.environment,
        "debug": settings.debug
    }

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger.info("MarketMind Pro API starting up...")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("MarketMind Pro API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )