# FastAPI Chart Endpoints
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
from app.services.hybrid_chart_service import HybridChartService

router = APIRouter()
chart_service = HybridChartService()

class ChartRequest(BaseModel):
    ticker: str
    report_data: Dict[str, Any]

@router.post("/api/v1/charts/generate")
async def generate_charts(request: ChartRequest):
    """Generate financial charts for a report"""
    try:
        print(f"🎯 Generating charts for {request.ticker}")
        
        charts = await chart_service.generate_all_charts(request.report_data)
        
        return JSONResponse({
            "success": True,
            "ticker": request.ticker,
            "charts": charts,
            "chart_count": len(charts),
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Chart generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/charts/googl/demo")
async def generate_googl_demo():
    """Generate demo charts for GOOGL"""
    try:
        googl_data = {
            "ticker": "GOOGL",
            "financial_data": {
                "revenue": [282.8, 307.4, 339.7, 375.2, 415.8],
                "net_income": [59.9, 73.8, 88.3, 98.1, 109.2]
            }
        }
        
        charts = await chart_service.generate_all_charts(googl_data)
        
        return JSONResponse({
            "success": True,
            "message": f"Generated {len(charts)} demo charts for GOOGL",
            "charts": charts,
            "chart_types": list(charts.keys())
        })
        
    except Exception as e:
        return JSONResponse({
            "success": False,
            "error": str(e)
        })

@router.get("/api/v1/charts/health")
async def chart_health():
    """Health check for chart service"""
    try:
        # Test matplotlib
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot([1, 2, 3], [1, 4, 2])
        plt.close(fig)
        
        return JSONResponse({
            "status": "healthy",
            "services": {
                "matplotlib": "available",
                "hybrid_service": "ready"
            }
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e)
        })