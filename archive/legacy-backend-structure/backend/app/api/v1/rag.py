from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from app.rag.indexer import RAGIndexer
from app.rag.search_service import RAGSearchService
from app.core.deps import get_db_session, get_redis_client
from app.core.config import settings

router = APIRouter(prefix="/api/v1/rag", tags=["RAG"])

class IndexRequest(BaseModel):
    report_id: str = Field(..., description="Unique report identifier")
    sections: Dict[str, str] = Field(..., description="Report sections to index")

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Search query")
    report_id: Optional[str] = Field(None, description="Filter by specific report")
    section: Optional[str] = Field(None, description="Filter by specific section")
    limit: int = Field(5, ge=1, le=20, description="Maximum results to return")

class SearchResponse(BaseModel):
    results: List[Dict]
    total: int
    query: str
    sections_found: List[str]
    timestamp: str

@router.post("/index", response_model=Dict[str, int])
async def index_report(
    request: IndexRequest,
    background_tasks: BackgroundTasks,
    db_session = Depends(get_db_session)
):
    """Index a report's sections for semantic search"""
    try:
        indexer = RAGIndexer(settings.OPENAI_API_KEY, db_session)
        
        # Index in background for better performance
        background_tasks.add_task(
            _index_report_background,
            indexer,
            request.report_id,
            request.sections
        )
        
        return {
            "message": "Indexing started",
            "report_id": request.report_id,
            "sections_count": len(request.sections)
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Indexing failed: {str(e)}")

async def _index_report_background(indexer: RAGIndexer, report_id: str, sections: Dict[str, str]):
    """Background task for report indexing"""
    try:
        chunks_created = await indexer.index_report_sections(report_id, sections)
        print(f"Successfully indexed {chunks_created} chunks for report {report_id}")
    except Exception as e:
        print(f"Background indexing failed for {report_id}: {str(e)}")

@router.post("/search", response_model=SearchResponse)
async def semantic_search(
    request: SearchRequest,
    db_session = Depends(get_db_session),
    redis_client = Depends(get_redis_client)
):
    """Perform semantic search across indexed reports"""
    try:
        indexer = RAGIndexer(settings.OPENAI_API_KEY, db_session)
        search_service = RAGSearchService(indexer, redis_client)
        
        results = await search_service.search_with_context(
            query=request.query,
            report_id=request.report_id,
            section=request.section,
            limit=request.limit
        )
        
        return SearchResponse(**results)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/reports/{report_id}/sections/{section}/summary")
async def get_section_summary(
    report_id: str,
    section: str,
    db_session = Depends(get_db_session),
    redis_client = Depends(get_redis_client)
):
    """Get AI-generated summary of a specific report section"""
    try:
        indexer = RAGIndexer(settings.OPENAI_API_KEY, db_session)
        search_service = RAGSearchService(indexer, redis_client)
        
        summary = await search_service.get_section_summary(report_id, section)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Section not found or not indexed")
        
        return summary
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {str(e)}")

@router.delete("/reports/{report_id}")
async def delete_report_index(
    report_id: str,
    db_session = Depends(get_db_session),
    redis_client = Depends(get_redis_client)
):
    """Remove all indexed content for a specific report"""
    try:
        indexer = RAGIndexer(settings.OPENAI_API_KEY, db_session)
        search_service = RAGSearchService(indexer, redis_client)
        
        # Delete from database
        await indexer.delete_report_index(report_id)
        
        # Clear cache
        await search_service.invalidate_report_cache(report_id)
        
        return {"message": f"Successfully deleted index for report {report_id}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")

@router.get("/health")
async def rag_health_check(
    db_session = Depends(get_db_session),
    redis_client = Depends(get_redis_client)
):
    """Health check for RAG system components"""
    try:
        # Test database connection
        await db_session.execute("SELECT 1")
        
        # Test Redis connection
        await redis_client.ping()
        
        # Test OpenAI API (simple call)
        import openai
        openai.api_key = settings.OPENAI_API_KEY
        
        return {
            "status": "healthy",
            "components": {
                "database": "connected",
                "redis": "connected", 
                "openai": "configured"
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Health check failed: {str(e)}")