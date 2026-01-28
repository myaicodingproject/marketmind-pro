from fastapi import APIRouter
from app.api.v1.endpoints import reports, health
from app.features.charts.router import router as charts_router

api_router = APIRouter()

api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(charts_router, prefix="/charts", tags=["charts"])