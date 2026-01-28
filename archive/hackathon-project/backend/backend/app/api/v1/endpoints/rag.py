"""API endpoint to trigger 10-K fetch and RAG storage"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.ticker_to_rag_service import TickerToRAGService

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

class TickerRequest(BaseModel):
    ticker: str

@router.post("/process-ticker")
async def process_ticker_for_rag(request: TickerRequest):
    """Fetch 10-K report for ticker and store in RAG"""
    service = TickerToRAGService()
    result = await service.process_ticker_for_rag(request.ticker.upper())
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result
