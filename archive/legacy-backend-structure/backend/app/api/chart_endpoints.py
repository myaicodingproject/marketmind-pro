# FastAPI Chart Generation Endpoints
# Integration with MarketMind Pro chart system

from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import json
import asyncio
from datetime import datetime

from app.services.chart_service import ChartGenerationService, ChartDataProcessor

router = APIRouter()
chart_service = ChartGenerationService()
data_processor = ChartDataProcessor()

class ChartGenerationRequest(BaseModel):
    report_id: str
    ticker: str
    chart_types: Optional[List[str]] = None
    report_data: Dict[str, Any]

class ChartResponse(BaseModel):
    success: bool
    charts: Dict[str, str]
    message: str
    generated_at: str

@router.post("/api/v1/charts/generate", response_model=ChartResponse)
async def generate_charts(request: ChartGenerationRequest):
    """Generate financial charts for a report"""
    try:
        print(f"🎯 Generating charts for {request.ticker} (Report: {request.report_id})")
        
        # Process report data for chart generation
        processed_data = data_processor.extract_financial_data(request.report_data)
        processed_data['ticker'] = request.ticker
        
        # Generate all charts
        charts = await chart_service.generate_financial_charts(processed_data)
        
        if not charts:
            raise HTTPException(status_code=500, detail="Failed to generate charts")
        
        print(f"✅ Generated {len(charts)} charts for {request.ticker}")
        
        return ChartResponse(
            success=True,
            charts=charts,
            message=f"Successfully generated {len(charts)} charts",
            generated_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        print(f"❌ Error generating charts: {e}")
        raise HTTPException(status_code=500, detail=f"Chart generation failed: {str(e)}")

@router.get("/api/v1/charts/{report_id}")
async def get_report_charts(report_id: str):
    """Get generated charts for a report"""
    try:
        # In production, this would fetch from database/cache
        # For now, return sample response
        return JSONResponse({
            "report_id": report_id,
            "charts_available": ["revenue_trend", "peer_comparison", "dcf_waterfall", "sensitivity_analysis"],
            "status": "available"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve charts: {str(e)}")

@router.post("/api/v1/charts/googl/demo")
async def generate_googl_demo_charts():
    """Generate demo charts for GOOGL using sample data"""
    try:
        print("🚀 Generating GOOGL demo charts...")
        
        # Sample GOOGL report data
        googl_data = {
            "ticker": "GOOGL",
            "title": "GOOGL - Comprehensive Stock Analysis Report",
            "chart_data": {
                "financial_performance": {
                    "revenue_trend": [
                        {"year": "2022", "revenue": 282836, "profit": 59972},
                        {"year": "2023", "revenue": 307394, "profit": 73795},
                        {"year": "2024", "revenue": 339700, "profit": 88300},
                        {"year": "2025E", "revenue": 375200, "profit": 98100},
                        {"year": "2026E", "revenue": 415800, "profit": 109200}
                    ],
                    "margins": [
                        {"metric": "Gross Margin", "value": 57.3},
                        {"metric": "Operating Margin", "value": 26.0},
                        {"metric": "Net Margin", "value": 24.0}
                    ]
                },
                "peer_comparison": {
                    "companies": [
                        {
                            "name": "GOOGL",
                            "pe_ratio": 24.1,
                            "ev_ebitda": 18.2,
                            "roe": 29.2,
                            "revenue_growth": 10.5,
                            "margin": 26.0
                        },
                        {
                            "name": "MSFT",
                            "pe_ratio": 28.5,
                            "ev_ebitda": 22.4,
                            "roe": 38.1,
                            "revenue_growth": 15.2,
                            "margin": 42.0
                        },
                        {
                            "name": "AMZN",
                            "pe_ratio": 35.2,
                            "ev_ebitda": 28.7,
                            "roe": 18.4,
                            "revenue_growth": 12.8,
                            "margin": 8.2
                        },
                        {
                            "name": "META",
                            "pe_ratio": 22.1,
                            "ev_ebitda": 16.8,
                            "roe": 26.8,
                            "revenue_growth": 22.7,
                            "margin": 29.5
                        }
                    ]
                },
                "dcf_analysis": {
                    "cash_flows": {
                        "2026E": 78.2,
                        "2027E": 89.1,
                        "2028E": 101.4,
                        "2029E": 113.8,
                        "2030E": 126.1
                    },
                    "terminal_value": 1856.0,
                    "discount_rate": 0.092,
                    "terminal_growth": 0.025
                }
            }
        }
        
        # Generate charts
        charts = await chart_service.generate_financial_charts(googl_data)
        
        if not charts:
            return JSONResponse({
                "success": False,
                "message": "No charts generated",
                "charts": {}
            })
        
        print(f"✅ Generated {len(charts)} demo charts for GOOGL")
        
        return JSONResponse({
            "success": True,
            "message": f"Generated {len(charts)} demo charts for GOOGL",
            "charts": charts,
            "chart_types": list(charts.keys()),
            "generated_at": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"❌ Error generating GOOGL demo charts: {e}")
        return JSONResponse({
            "success": False,
            "message": f"Failed to generate demo charts: {str(e)}",
            "charts": {}
        })

@router.get("/api/v1/charts/types")
async def get_available_chart_types():
    """Get list of available chart types"""
    return JSONResponse({
        "chart_types": {
            "chartjs_charts": [
                "revenue_trend",
                "peer_comparison", 
                "financial_trends",
                "segment_breakdown"
            ],
            "matplotlib_charts": [
                "dcf_waterfall",
                "sensitivity_analysis",
                "financial_metrics",
                "valuation_comparison"
            ]
        },
        "description": "Hybrid Chart.js + matplotlib financial chart system"
    })

@router.post("/api/v1/charts/custom")
async def generate_custom_chart(chart_config: Dict[str, Any]):
    """Generate custom chart with specific configuration"""
    try:
        chart_type = chart_config.get("type")
        data = chart_config.get("data", {})
        
        if chart_type == "dcf_waterfall":
            # Generate DCF waterfall chart
            result = await chart_service._create_dcf_waterfall_chart(data)
        elif chart_type == "sensitivity_heatmap":
            # Generate sensitivity analysis
            result = await chart_service._create_sensitivity_heatmap(data)
        elif chart_type == "peer_comparison":
            # Generate peer comparison
            result = await chart_service._create_peer_comparison_chart(data)
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported chart type: {chart_type}")
        
        if result:
            return JSONResponse({
                "success": True,
                "chart": result,
                "type": chart_type
            })
        else:
            raise HTTPException(status_code=500, detail="Chart generation failed")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom chart generation failed: {str(e)}")

# Health check endpoint
@router.get("/api/v1/charts/health")
async def chart_service_health():
    """Health check for chart generation service"""
    try:
        # Test basic chart generation
        test_data = {"ticker": "TEST"}
        
        # Quick test of matplotlib
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(4, 3))
        ax.plot([1, 2, 3], [1, 4, 2])
        plt.close(fig)
        
        return JSONResponse({
            "status": "healthy",
            "services": {
                "matplotlib": "available",
                "chart_service": "ready"
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return JSONResponse({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })