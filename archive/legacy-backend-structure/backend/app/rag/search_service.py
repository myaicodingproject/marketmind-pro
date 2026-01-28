import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import redis.asyncio as redis
import json
from app.rag.indexer import RAGIndexer

class RAGSearchService:
    def __init__(self, indexer: RAGIndexer, redis_client: redis.Redis):
        self.indexer = indexer
        self.cache = redis_client
        self.cache_ttl = 3600  # 1 hour

    async def search_with_context(self, query: str, report_id: Optional[str] = None,
                                section: Optional[str] = None, limit: int = 5) -> Dict:
        """Enhanced search with context and caching"""
        cache_key = f"rag_search:{hash(f'{query}{report_id}{section}{limit}')}"
        
        # Check cache first
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Perform search
        results = await self.indexer.semantic_search(query, report_id, section, limit)
        
        # Enhance results with context
        enhanced_results = await self._enhance_results(results, query)
        
        # Cache results
        await self.cache.setex(cache_key, self.cache_ttl, json.dumps(enhanced_results, default=str))
        
        return enhanced_results

    async def _enhance_results(self, results: List[Dict], query: str) -> Dict:
        """Add context and relevance scoring to search results"""
        if not results:
            return {"results": [], "total": 0, "query": query}
        
        # Group by section for better context
        sections = {}
        for result in results:
            section = result["section"]
            if section not in sections:
                sections[section] = []
            sections[section].append(result)
        
        # Calculate relevance scores
        enhanced = []
        for result in results:
            enhanced.append({
                **result,
                "relevance_score": self._calculate_relevance(result, query),
                "context_window": await self._get_context_window(result)
            })
        
        return {
            "results": enhanced,
            "total": len(enhanced),
            "query": query,
            "sections_found": list(sections.keys()),
            "timestamp": datetime.utcnow().isoformat()
        }

    def _calculate_relevance(self, result: Dict, query: str) -> float:
        """Calculate enhanced relevance score"""
        base_similarity = result["similarity"]
        
        # Boost for exact matches
        query_lower = query.lower()
        content_lower = result["content"].lower()
        exact_match_boost = 0.1 if query_lower in content_lower else 0
        
        # Boost for section relevance
        section_boost = 0.05 if any(word in result["section"].lower() 
                                  for word in query_lower.split()) else 0
        
        return min(1.0, base_similarity + exact_match_boost + section_boost)

    async def _get_context_window(self, result: Dict) -> Dict:
        """Get surrounding chunks for better context"""
        chunk_index = result["metadata"].get("chunk_index", 0)
        report_id = result["report_id"]
        section = result["section"]
        
        # Get adjacent chunks
        adjacent_query = """
        SELECT content, metadata->>'chunk_index' as chunk_idx
        FROM document_chunks 
        WHERE report_id = $1 AND section = $2 
        AND (metadata->>'chunk_index')::int BETWEEN $3 AND $4
        ORDER BY (metadata->>'chunk_index')::int
        """
        
        try:
            adjacent_results = await self.indexer.db.execute(
                adjacent_query, 
                report_id, section, max(0, chunk_index - 1), chunk_index + 1
            )
            
            context_chunks = [{"content": row[0], "index": int(row[1])} 
                            for row in adjacent_results.fetchall()]
            
            return {
                "previous": next((c["content"] for c in context_chunks if c["index"] == chunk_index - 1), None),
                "next": next((c["content"] for c in context_chunks if c["index"] == chunk_index + 1), None)
            }
        except:
            return {"previous": None, "next": None}

    async def get_section_summary(self, report_id: str, section: str) -> Optional[Dict]:
        """Get AI-generated summary of a report section"""
        cache_key = f"section_summary:{report_id}:{section}"
        
        cached = await self.cache.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Get all chunks for the section
        chunks = await self.indexer.semantic_search(
            query="", report_id=report_id, section=section, limit=50
        )
        
        if not chunks:
            return None
        
        # Combine content and generate summary
        full_content = " ".join([chunk["content"] for chunk in chunks])
        
        summary = {
            "section": section,
            "report_id": report_id,
            "chunk_count": len(chunks),
            "word_count": len(full_content.split()),
            "key_topics": self._extract_key_topics(full_content),
            "generated_at": datetime.utcnow().isoformat()
        }
        
        await self.cache.setex(cache_key, self.cache_ttl * 24, json.dumps(summary, default=str))
        return summary

    def _extract_key_topics(self, content: str) -> List[str]:
        """Extract key topics from content (simplified implementation)"""
        # This would typically use NLP libraries like spaCy or NLTK
        words = content.lower().split()
        
        # Financial keywords that are likely important
        financial_terms = [
            "revenue", "profit", "earnings", "growth", "margin", "debt", 
            "cash", "valuation", "risk", "market", "competition", "strategy"
        ]
        
        found_terms = [term for term in financial_terms if term in words]
        return found_terms[:10]  # Return top 10 topics

    async def invalidate_report_cache(self, report_id: str):
        """Clear all cached data for a specific report"""
        pattern = f"*{report_id}*"
        keys = await self.cache.keys(pattern)
        if keys:
            await self.cache.delete(*keys)