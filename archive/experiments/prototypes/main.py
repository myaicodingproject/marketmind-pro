from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
import asyncio
import json
from pipeline_orchestrator import PipelineOrchestrator, TaskStatus
from typing import Dict, Any

app = FastAPI(title="MarketMind Pro Pipeline Orchestrator", version="1.0.0")

# Global orchestrator instance
orchestrator = PipelineOrchestrator()
websocket_clients = set()

@app.websocket("/ws/pipeline/{pipeline_id}")
async def websocket_endpoint(websocket: WebSocket, pipeline_id: str):
    """WebSocket endpoint for real-time pipeline updates"""
    await websocket.accept()
    websocket_clients.add(websocket)
    orchestrator.clients = websocket_clients
    
    try:
        while True:
            # Keep connection alive and send heartbeat
            await asyncio.sleep(30)
            await websocket.send(json.dumps({"type": "heartbeat", "timestamp": "now"}))
    except WebSocketDisconnect:
        websocket_clients.discard(websocket)

@app.post("/api/v1/pipeline/execute")
async def execute_pipeline(request: Dict[str, Any]):
    """Execute the complete 4-stage pipeline"""
    symbol = request.get("symbol")
    analysis_type = request.get("analysis_type", "comprehensive")
    
    if not symbol:
        raise HTTPException(status_code=400, detail="Symbol is required")
    
    try:
        # Execute pipeline asynchronously
        result = await orchestrator.execute_pipeline(symbol, analysis_type)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline execution failed: {str(e)}")

@app.get("/api/v1/pipeline/progress/{pipeline_id}")
async def get_pipeline_progress(pipeline_id: str):
    """Get current progress of a pipeline"""
    progress = orchestrator.get_progress(pipeline_id)
    if not progress:
        raise HTTPException(status_code=404, detail="Pipeline not found")
    
    return {
        "pipeline_id": pipeline_id,
        "stage": progress.stage.value if progress.stage else None,
        "progress": progress.progress,
        "status": progress.status.value,
        "message": progress.message,
        "timestamp": progress.timestamp.isoformat(),
        "errors": progress.errors or []
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "pipeline-orchestrator",
        "active_pipelines": len(orchestrator.progress),
        "websocket_clients": len(websocket_clients)
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)