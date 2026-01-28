"""
Semantic Search and Context Retrieval System

This module provides advanced semantic search capabilities for financial documents:
- Multi-modal search (semantic + keyword + metadata)
- Context-aware retrieval for RAG
- Financial concept-based search
- Temporal and relevance ranking
- Query expansion and refinement
"""

import asyncio
import re
import json
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from datetime import datetime, timedelta
import logging

import numpy as np
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class SearchMode(Enum):
    """Search modes for different use cases"""
    SEMANTIC = "semantic"  # Pure semantic similarity
    HYBRID = "hybrid"      # Semantic + keyword + metadata
    KEYWORD = "keyword"    # Traditional keyword search
    FINANCIAL = "financial"  # Financial concept-focused
    TEMPORAL = "temporal"  # Time-aware search

@dataclass
class SearchResult:
    """Enhanced search result with rich metadata"""
    chunk_id: str
    content: str
    score: float
    metadata: Dict[str, Any]
    
    # Relevance metrics
    semantic_score: float = 0.0
    keyword_score: float = 0.0
    metadata_score: float = 0.0
    temporal_score: float = 0.0
    financial_relevance: float = 0.0
    
    # Context information
    document_type: str = ""
    ticker: str = ""
    filing_date: Optional[str] = None
    section_name: Optional[str] = None
    
    # Content analysis
    financial_concepts: List[str] = None
    key_numbers: List[str] = None
    
    def __post_init__(self):
        if self.financial_concepts is None:
            self.financial_concepts = []
        if self.key_numbers is None:
            self.key_numbers = []
        
        # Extract from metadata
        self.document_type = self.metadata.get('document_type', '')
        self.ticker = self.metadata.get('ticker', '')
        self.filing_date = self.metadata.get('filing_date')
        self.section_name = self.metadata.get('section_name')
        
        # Extract financial concepts and numbers from content
        self._extract_content_features()
    
    def _extract_content_features(self):
        """Extract financial concepts and key numbers from content"""
        content_lower = self.content.lower()
        
        # Financial concepts
        financial_terms = [
            'revenue', 'income', 'profit', 'loss', 'earnings', 'ebitda',
            'assets', 'liabilities', 'equity', 'debt', 'cash', 'dividend',
            'margin', 'ratio', 'valuation', 'growth', 'return', 'yield',
            'capex', 'opex', 'fcf', 'roe', 'roa', 'eps'
        ]
        
        self.financial_concepts = [term for term in financial_terms if term in content_lower]
        
        # Extract key numbers (dollar amounts, percentages, ratios)
        number_patterns = [
            r'\$[\d,]+\.?\d*[kmb]?',  # Dollar amounts
            r'\d+\.?\d*%',            # Percentages
            r'\d+\.?\d*x',            # Multiples
            r'\d+\.?\d*\s*million',   # Millions
            r'\d+\.?\d*\s*billion'    # Billions
        ]
        
        for pattern in number_patterns:
            matches = re.findall(pattern, content_lower)
            self.key_numbers.extend(matches)

class SemanticSearchEngine:
    """Advanced semantic search engine for financial documents"""
    
    def __init__(self, chroma_path: str = "./chroma_db", embedding_model: str = "all-MiniLM-L6-v2"):
        self.chroma_path = chroma_path
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False, allow_reset=False)
        )
        
        # Get collections
        self.collections = {
            "sec_filings": self._get_collection("sec_filings_v2"),
            "financial_statements": self._get_collection("financial_statements_v2"),
            "earnings_reports": self._get_collection("earnings_reports_v2"),
            "general_documents": self._get_collection("general_documents_v2")
        }
        
        # Initialize embedding model
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            self.embedding_model = None
        
        # Financial concept mappings
        self.financial_concept_groups = {
            'profitability': ['revenue', 'income', 'profit', 'earnings', 'margin', 'ebitda'],
            'liquidity': ['cash', 'current ratio', 'quick ratio', 'working capital'],
            'leverage': ['debt', 'leverage', 'debt to equity', 'interest coverage'],
            'efficiency': ['asset turnover', 'inventory turnover', 'receivables turnover'],
            'valuation': ['pe ratio', 'pb ratio', 'ev/ebitda', 'price to sales'],
            'growth': ['revenue growth', 'earnings growth', 'dividend growth'],
            'returns': ['roe', 'roa', 'roic', 'return on investment']
        }
        
        # Query expansion terms
        self.query_expansions = {
            'performance': ['results', 'metrics', 'kpis', 'financial performance'],
            'risk': ['risk factors', 'uncertainties', 'challenges', 'threats'],
            'strategy': ['business strategy', 'competitive position', 'market position'],
            'outlook': ['guidance', 'forecast', 'projections', 'future prospects']
        }
    
    def _get_collection(self, name: str):
        """Get ChromaDB collection"""
        try:
            return self.client.get_collection(name=name)
        except ValueError:
            logger.warning(f"Collection {name} not found")
            return None
    
    async def search(self, query: str, ticker: Optional[str] = None,
                    document_types: Optional[List[str]] = None,
                    date_range: Optional[Tuple[str, str]] = None,
                    search_mode: SearchMode = SearchMode.HYBRID,
                    max_results: int = 20) -> List[SearchResult]:
        """Main search method with multiple modes"""
        
        logger.info(f"Searching: '{query}' for {ticker or 'all tickers'} in mode {search_mode.value}")
        
        # Expand query if needed
        expanded_query = self._expand_query(query)
        
        # Build search filters
        filters = self._build_search_filters(ticker, document_types, date_range)
        
        # Execute search based on mode
        if search_mode == SearchMode.SEMANTIC:
            results = await self._semantic_search(expanded_query, filters, max_results)
        elif search_mode == SearchMode.HYBRID:
            results = await self._hybrid_search(expanded_query, filters, max_results)
        elif search_mode == SearchMode.KEYWORD:
            results = await self._keyword_search(query, filters, max_results)
        elif search_mode == SearchMode.FINANCIAL:
            results = await self._financial_search(query, filters, max_results)
        elif search_mode == SearchMode.TEMPORAL:
            results = await self._temporal_search(expanded_query, filters, max_results)
        else:
            results = await self._hybrid_search(expanded_query, filters, max_results)
        
        # Post-process and rank results
        results = self._post_process_results(results, query, search_mode)
        
        logger.info(f"Found {len(results)} results")
        return results[:max_results]
    
    def _expand_query(self, query: str) -> str:
        """Expand query with related terms"""
        expanded_terms = [query]
        query_lower = query.lower()
        
        # Add financial concept expansions
        for concept_group, terms in self.financial_concept_groups.items():
            if any(term in query_lower for term in terms):
                expanded_terms.extend(terms)
        
        # Add general expansions
        for key, expansions in self.query_expansions.items():
            if key in query_lower:
                expanded_terms.extend(expansions)
        
        return ' '.join(set(expanded_terms))
    
    def _build_search_filters(self, ticker: Optional[str], document_types: Optional[List[str]],
                             date_range: Optional[Tuple[str, str]]) -> Dict[str, Any]:
        """Build search filters for ChromaDB"""
        filters = {}
        
        if ticker:
            filters['ticker'] = ticker
        
        if document_types:
            filters['document_type'] = {"$in": document_types}
        
        if date_range:
            start_date, end_date = date_range
            filters['filing_date'] = {"$gte": start_date, "$lte": end_date}
        
        return filters
    
    async def _semantic_search(self, query: str, filters: Dict, max_results: int) -> List[SearchResult]:
        """Pure semantic similarity search"""
        results = []
        
        if not self.embedding_model:
            logger.warning("No embedding model available for semantic search")
            return results
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])[0]
        
        # Search across all collections
        for collection_name, collection in self.collections.items():
            if not collection:
                continue
            
            try:
                search_results = collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=min(max_results // len(self.collections), 50),
                    where=filters if filters else None
                )
                
                # Convert to SearchResult objects
                for i, doc in enumerate(search_results["documents"][0]):
                    result = SearchResult(
                        chunk_id=search_results["ids"][0][i],
                        content=doc,
                        score=1.0 - search_results["distances"][0][i],  # Convert distance to similarity
                        metadata=search_results["metadatas"][0][i],
                        semantic_score=1.0 - search_results["distances"][0][i]
                    )
                    results.append(result)
            
            except Exception as e:
                logger.error(f"Error in semantic search for {collection_name}: {e}")
        
        return results
    
    async def _hybrid_search(self, query: str, filters: Dict, max_results: int) -> List[SearchResult]:
        """Hybrid search combining semantic, keyword, and metadata signals"""
        # Get semantic results
        semantic_results = await self._semantic_search(query, filters, max_results * 2)
        
        # Get keyword results
        keyword_results = await self._keyword_search(query, filters, max_results)
        
        # Combine and deduplicate
        combined_results = {}
        
        # Add semantic results
        for result in semantic_results:
            combined_results[result.chunk_id] = result
        
        # Merge keyword results
        for result in keyword_results:
            if result.chunk_id in combined_results:
                # Combine scores
                existing = combined_results[result.chunk_id]
                existing.keyword_score = result.keyword_score
                existing.score = (existing.semantic_score * 0.6 + result.keyword_score * 0.4)
            else:
                combined_results[result.chunk_id] = result
        
        # Add metadata scoring
        for result in combined_results.values():
            result.metadata_score = self._calculate_metadata_score(result, query)
            result.score = (result.semantic_score * 0.5 + 
                          result.keyword_score * 0.3 + 
                          result.metadata_score * 0.2)
        
        return list(combined_results.values())
    
    async def _keyword_search(self, query: str, filters: Dict, max_results: int) -> List[SearchResult]:
        """Keyword-based search using text matching"""
        results = []
        query_terms = query.lower().split()
        
        # Search across all collections
        for collection_name, collection in self.collections.items():
            if not collection:
                continue
            
            try:
                # Get all documents matching filters
                all_docs = collection.get(
                    where=filters if filters else None,
                    limit=1000  # Reasonable limit for keyword search
                )
                
                # Score documents based on keyword matches
                for i, doc in enumerate(all_docs["documents"]):
                    doc_lower = doc.lower()
                    
                    # Calculate keyword score
                    keyword_score = 0.0
                    for term in query_terms:
                        if term in doc_lower:
                            # TF-IDF-like scoring
                            term_count = doc_lower.count(term)
                            keyword_score += term_count / len(doc_lower.split())
                    
                    if keyword_score > 0:
                        result = SearchResult(
                            chunk_id=all_docs["ids"][i],
                            content=doc,
                            score=keyword_score,
                            metadata=all_docs["metadatas"][i],
                            keyword_score=keyword_score
                        )
                        results.append(result)
            
            except Exception as e:
                logger.error(f"Error in keyword search for {collection_name}: {e}")
        
        return results
    
    async def _financial_search(self, query: str, filters: Dict, max_results: int) -> List[SearchResult]:
        """Financial concept-focused search"""
        # Identify financial concepts in query
        query_lower = query.lower()
        relevant_concepts = []
        
        for concept_group, terms in self.financial_concept_groups.items():
            if any(term in query_lower for term in terms):
                relevant_concepts.extend(terms)
        
        # Expand query with financial terms
        financial_query = query + " " + " ".join(relevant_concepts)
        
        # Perform hybrid search with financial bias
        results = await self._hybrid_search(financial_query, filters, max_results * 2)
        
        # Re-score based on financial relevance
        for result in results:
            result.financial_relevance = self._calculate_financial_relevance(result, relevant_concepts)
            result.score = (result.score * 0.7 + result.financial_relevance * 0.3)
        
        return results
    
    async def _temporal_search(self, query: str, filters: Dict, max_results: int) -> List[SearchResult]:
        """Time-aware search prioritizing recent documents"""
        results = await self._hybrid_search(query, filters, max_results * 2)
        
        # Add temporal scoring
        current_date = datetime.now()
        
        for result in results:
            filing_date_str = result.metadata.get('filing_date')
            if filing_date_str:
                try:
                    filing_date = datetime.fromisoformat(filing_date_str.replace('Z', '+00:00'))
                    days_old = (current_date - filing_date).days
                    
                    # Exponential decay for temporal relevance
                    result.temporal_score = np.exp(-days_old / 365.0)  # Half-life of 1 year
                    result.score = (result.score * 0.8 + result.temporal_score * 0.2)
                
                except Exception as e:
                    logger.debug(f"Failed to parse date {filing_date_str}: {e}")
                    result.temporal_score = 0.0
        
        return results
    
    def _calculate_metadata_score(self, result: SearchResult, query: str) -> float:
        """Calculate relevance score based on metadata"""
        score = 0.0
        query_lower = query.lower()
        
        # Document type relevance
        doc_type = result.metadata.get('document_type', '').lower()
        if 'financial' in query_lower and 'financial' in doc_type:
            score += 0.3
        elif 'risk' in query_lower and '10-k' in doc_type:
            score += 0.3
        elif 'earnings' in query_lower and ('10-q' in doc_type or 'earnings' in doc_type):
            score += 0.3
        
        # Section relevance
        section_name = result.metadata.get('section_name', '').lower()
        if section_name:
            if 'risk' in query_lower and 'risk' in section_name:
                score += 0.4
            elif 'management' in query_lower and 'management' in section_name:
                score += 0.4
            elif 'financial' in query_lower and 'financial' in section_name:
                score += 0.4
        
        # Chunk type relevance
        chunk_type = result.metadata.get('chunk_type', '').lower()
        if 'table' in chunk_type and any(term in query_lower for term in ['data', 'numbers', 'financial']):
            score += 0.2
        
        return min(score, 1.0)
    
    def _calculate_financial_relevance(self, result: SearchResult, relevant_concepts: List[str]) -> float:
        """Calculate financial relevance score"""
        content_lower = result.content.lower()
        
        # Count financial concept matches
        concept_matches = sum(1 for concept in relevant_concepts if concept in content_lower)
        concept_score = min(concept_matches / max(len(relevant_concepts), 1), 1.0)
        
        # Check for financial numbers
        number_patterns = [r'\$[\d,]+', r'\d+%', r'\d+\.?\d*\s*(million|billion)']
        number_matches = sum(len(re.findall(pattern, content_lower)) for pattern in number_patterns)
        number_score = min(number_matches / 10.0, 1.0)  # Normalize to 0-1
        
        # Check for financial statement indicators
        statement_indicators = ['consolidated', 'statement', 'balance sheet', 'income', 'cash flow']
        statement_matches = sum(1 for indicator in statement_indicators if indicator in content_lower)
        statement_score = min(statement_matches / len(statement_indicators), 1.0)
        
        return (concept_score * 0.5 + number_score * 0.3 + statement_score * 0.2)
    
    def _post_process_results(self, results: List[SearchResult], query: str, 
                             search_mode: SearchMode) -> List[SearchResult]:
        """Post-process and rank search results"""
        # Remove duplicates
        unique_results = {}
        for result in results:
            if result.chunk_id not in unique_results or result.score > unique_results[result.chunk_id].score:
                unique_results[result.chunk_id] = result
        
        results = list(unique_results.values())
        
        # Sort by score
        results.sort(key=lambda x: x.score, reverse=True)
        
        # Apply diversity filtering to avoid too many results from same document
        diverse_results = []
        doc_counts = {}
        max_per_doc = 3
        
        for result in results:
            doc_key = f"{result.ticker}_{result.document_type}"
            doc_count = doc_counts.get(doc_key, 0)
            
            if doc_count < max_per_doc:
                diverse_results.append(result)
                doc_counts[doc_key] = doc_count + 1
        
        return diverse_results
    
    async def get_context_for_analysis(self, ticker: str, analysis_type: str, 
                                     max_chunks: int = 15) -> str:
        """Get contextual information for specific analysis types"""
        
        # Define analysis-specific queries
        analysis_queries = {
            'business_overview': 'business operations products services competitive position market',
            'financial_performance': 'revenue income earnings financial results performance metrics',
            'risk_assessment': 'risk factors uncertainties challenges regulatory compliance',
            'valuation': 'valuation metrics ratios multiples dcf comparable companies',
            'growth_prospects': 'growth opportunities expansion strategy future outlook',
            'management_discussion': 'management discussion analysis md&a liquidity capital'
        }
        
        query = analysis_queries.get(analysis_type, analysis_type)
        
        # Search for relevant content
        results = await self.search(
            query=query,
            ticker=ticker,
            search_mode=SearchMode.FINANCIAL,
            max_results=max_chunks
        )
        
        # Format context
        context_sections = []
        
        # Group by document type and section
        grouped_results = {}
        for result in results:
            key = f"{result.document_type}_{result.section_name or 'general'}"
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].append(result)
        
        # Format each group
        for group_key, group_results in grouped_results.items():
            doc_type, section = group_key.split('_', 1)
            
            context_sections.append(f"=== {doc_type.upper()} - {section.upper().replace('_', ' ')} ===")
            
            for result in group_results[:3]:  # Limit per group
                # Add metadata context
                date_info = f"[{result.filing_date or 'Unknown Date'}]"
                score_info = f"(Relevance: {result.score:.2f})"
                
                context_sections.append(f"{date_info} {score_info}")
                context_sections.append(result.content[:800] + "...")
                context_sections.append("")
        
        return "\n".join(context_sections)
    
    async def find_similar_content(self, reference_content: str, ticker: Optional[str] = None,
                                  max_results: int = 10) -> List[SearchResult]:
        """Find content similar to a reference text"""
        if not self.embedding_model:
            return []
        
        # Generate embedding for reference content
        reference_embedding = self.embedding_model.encode([reference_content])[0]
        
        results = []
        filters = {'ticker': ticker} if ticker else {}
        
        # Search across collections
        for collection_name, collection in self.collections.items():
            if not collection:
                continue
            
            try:
                search_results = collection.query(
                    query_embeddings=[reference_embedding.tolist()],
                    n_results=max_results,
                    where=filters if filters else None
                )
                
                for i, doc in enumerate(search_results["documents"][0]):
                    result = SearchResult(
                        chunk_id=search_results["ids"][0][i],
                        content=doc,
                        score=1.0 - search_results["distances"][0][i],
                        metadata=search_results["metadatas"][0][i],
                        semantic_score=1.0 - search_results["distances"][0][i]
                    )
                    results.append(result)
            
            except Exception as e:
                logger.error(f"Error finding similar content in {collection_name}: {e}")
        
        # Sort by similarity
        results.sort(key=lambda x: x.score, reverse=True)
        return results[:max_results]
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        stats = {
            "collections": {},
            "embedding_model": str(self.embedding_model) if self.embedding_model else "None",
            "financial_concept_groups": len(self.financial_concept_groups),
            "query_expansions": len(self.query_expansions)
        }
        
        for name, collection in self.collections.items():
            if collection:
                try:
                    count = collection.count()
                    stats["collections"][name] = count
                except Exception as e:
                    stats["collections"][name] = f"Error: {e}"
            else:
                stats["collections"][name] = "Not available"
        
        return stats

# Utility functions
def format_search_results_for_display(results: List[SearchResult]) -> str:
    """Format search results for human-readable display"""
    if not results:
        return "No results found."
    
    formatted = []
    for i, result in enumerate(results, 1):
        header = f"{i}. {result.ticker} - {result.document_type}"
        if result.section_name:
            header += f" ({result.section_name})"
        
        score_info = f"Score: {result.score:.3f}"
        if result.filing_date:
            score_info += f" | Date: {result.filing_date}"
        
        content_preview = result.content[:200] + "..." if len(result.content) > 200 else result.content
        
        formatted.append(f"{header}\n{score_info}\n{content_preview}\n")
    
    return "\n".join(formatted)

def extract_key_insights(results: List[SearchResult]) -> Dict[str, Any]:
    """Extract key insights from search results"""
    insights = {
        "total_results": len(results),
        "avg_score": sum(r.score for r in results) / len(results) if results else 0,
        "document_types": {},
        "tickers": {},
        "date_range": {"earliest": None, "latest": None},
        "top_financial_concepts": {},
        "key_numbers": []
    }
    
    for result in results:
        # Count document types
        doc_type = result.document_type
        insights["document_types"][doc_type] = insights["document_types"].get(doc_type, 0) + 1
        
        # Count tickers
        ticker = result.ticker
        insights["tickers"][ticker] = insights["tickers"].get(ticker, 0) + 1
        
        # Track date range
        if result.filing_date:
            if not insights["date_range"]["earliest"] or result.filing_date < insights["date_range"]["earliest"]:
                insights["date_range"]["earliest"] = result.filing_date
            if not insights["date_range"]["latest"] or result.filing_date > insights["date_range"]["latest"]:
                insights["date_range"]["latest"] = result.filing_date
        
        # Aggregate financial concepts
        for concept in result.financial_concepts:
            insights["top_financial_concepts"][concept] = insights["top_financial_concepts"].get(concept, 0) + 1
        
        # Collect key numbers
        insights["key_numbers"].extend(result.key_numbers)
    
    # Sort by frequency
    insights["document_types"] = dict(sorted(insights["document_types"].items(), key=lambda x: x[1], reverse=True))
    insights["tickers"] = dict(sorted(insights["tickers"].items(), key=lambda x: x[1], reverse=True))
    insights["top_financial_concepts"] = dict(sorted(insights["top_financial_concepts"].items(), key=lambda x: x[1], reverse=True)[:10])
    
    return insights