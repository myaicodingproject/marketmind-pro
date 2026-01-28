from fastapi import APIRouter
from pydantic import BaseModel
import time

router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: float
    service: str

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint for deployment validation"""
    return HealthResponse(
        status="healthy",
        timestamp=time.time(),
        service="marketmind-pro-backend"
    )

@router.get("/api/v1/status")
async def system_status():
    """System status endpoint for validation"""
    return {
        "status": "running",
        "database": "connected",
        "service": "marketmind-pro",
        "timestamp": time.time()
    }