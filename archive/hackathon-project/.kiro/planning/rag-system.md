# RAG (Retrieval-Augmented Generation) System

## RAG Architecture Overview

### Multi-Source RAG Strategy
```
User Query → Vector Search → Context Retrieval → Kiro Processing → Enhanced Response
```

### RAG Data Sources
1. **SEC Filings** - 10-K, 10-Q, 8-K documents
2. **Financial Statements** - Income, Balance Sheet, Cash Flow
3. **News Articles** - Recent company news and market updates
4. **Analyst Reports** - Third-party research (where legally accessible)
5. **Company Documents** - Investor presentations, earnings calls
6. **Market Data** - Historical prices, trading volumes, ratios

## Vector Database Implementation

### Embedding Strategy
```python
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import numpy as np

class EmbeddingManager:
    def __init__(self):
        # Use financial domain-specific embedding model
        self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Can upgrade to finance-specific model
        
        # Initialize ChromaDB for vector storage
        self.chroma_client = chromadb.Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="/data/chroma_db"
        ))
        
        # Create collections for different data types
        self.collections = {
            'sec_filings': self.chroma_client.get_or_create_collection("sec_filings"),
            'financial_statements': self.chroma_client.get_or_create_collection("financial_statements"),
            'news_articles': self.chroma_client.get_or_create_collection("news_articles"),
            'company_docs': self.chroma_client.get_or_create_collection("company_docs")
        }
    
    async def create_embeddings(self, texts: list[str]) -> np.ndarray:
        """Create embeddings for text chunks"""
        return self.model.encode(texts)
    
    async def store_document_embeddings(self, collection_name: str, documents: list[dict]):
        """Store document embeddings in vector database"""
        collection = self.collections[collection_name]
        
        texts = [doc['content'] for doc in documents]
        embeddings = await self.create_embeddings(texts)
        
        collection.add(
            embeddings=embeddings.tolist(),
            documents=texts,
            metadatas=[doc['metadata'] for doc in documents],
            ids=[doc['id'] for doc in documents]
        )
```

### Document Processing Pipeline
```python
import PyPDF2
import re
from typing import List, Dict

class DocumentProcessor:
    def __init__(self):
        self.chunk_size = 1000  # Characters per chunk
        self.chunk_overlap = 200  # Overlap between chunks
    
    async def process_sec_filing(self, filing_content: str, company_ticker: str, filing_type: str) -> List[Dict]:
        """Process SEC filing into searchable chunks"""
        
        # Clean and normalize text
        cleaned_content = self._clean_text(filing_content)
        
        # Extract key sections
        sections = self._extract_sec_sections(cleaned_content, filing_type)
        
        # Create chunks with metadata
        chunks = []
        for section_name, section_content in sections.items():
            section_chunks = self._create_chunks(section_content)
            
            for i, chunk in enumerate(section_chunks):
                chunks.append({
                    'id': f"{company_ticker}_{filing_type}_{section_name}_{i}",
                    'content': chunk,
                    'metadata': {
                        'company_ticker': company_ticker,
                        'document_type': 'sec_filing',
                        'filing_type': filing_type,
                        'section': section_name,
                        'chunk_index': i
                    }
                })
        
        return chunks
    
    def _extract_sec_sections(self, content: str, filing_type: str) -> Dict[str, str]:
        """Extract key sections from SEC filings"""
        sections = {}
        
        if filing_type == '10-K':
            # Extract standard 10-K sections
            section_patterns = {
                'business': r'Item 1\..*?Business.*?(?=Item 2\.)',
                'risk_factors': r'Item 1A\..*?Risk Factors.*?(?=Item 1B\.)',
                'properties': r'Item 2\..*?Properties.*?(?=Item 3\.)',
                'legal_proceedings': r'Item 3\..*?Legal Proceedings.*?(?=Item 4\.)',
                'management_discussion': r'Item 7\..*?Management.*?Discussion.*?(?=Item 8\.)',
                'financial_statements': r'Item 8\..*?Financial Statements.*?(?=Item 9\.)'
            }
        elif filing_type == '10-Q':
            section_patterns = {
                'financial_statements': r'Part I.*?Item 1\..*?Financial Statements.*?(?=Item 2\.)',
                'management_discussion': r'Item 2\..*?Management.*?Discussion.*?(?=Item 3\.)',
                'controls': r'Item 4\..*?Controls and Procedures.*?(?=Part II)'
            }
        else:
            # Generic section extraction for other filing types
            section_patterns = {
                'full_content': content
            }
        
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
            if match:
                sections[section_name] = match.group(0)
        
        return sections
    
    def _create_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                sentence_end = text.rfind('.', start, end)
                if sentence_end > start + self.chunk_size // 2:
                    end = sentence_end + 1
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - self.chunk_overlap
        
        return chunks
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove page numbers and headers/footers
        text = re.sub(r'Page \d+ of \d+', '', text)
        text = re.sub(r'\n\s*\d+\s*\n', '\n', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace('–', '-').replace('—', '-')
        
        return text.strip()
```

## RAG Query Processing

### Intelligent Context Retrieval
```python
class RAGQueryProcessor:
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
        self.max_context_length = 4000  # Characters
    
    async def retrieve_relevant_context(self, query: str, company_ticker: str, context_types: List[str] = None) -> Dict[str, List[str]]:
        """Retrieve relevant context for a query"""
        
        # Create query embedding
        query_embedding = await self.embedding_manager.create_embeddings([query])
        
        # Default context types if not specified
        if not context_types:
            context_types = ['sec_filings', 'financial_statements', 'news_articles']
        
        relevant_context = {}
        
        for context_type in context_types:
            collection = self.embedding_manager.collections[context_type]
            
            # Search for relevant documents
            results = collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=5,
                where={"company_ticker": company_ticker} if company_ticker else None
            )
            
            # Extract and rank results
            context_chunks = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                if distance < 0.7:  # Similarity threshold
                    context_chunks.append({
                        'content': doc,
                        'metadata': metadata,
                        'relevance_score': 1 - distance,
                        'source': context_type
                    })
            
            relevant_context[context_type] = context_chunks
        
        return relevant_context
    
    async def prepare_kiro_context(self, query: str, company_ticker: str) -> str:
        """Prepare context for Kiro prompt"""
        
        # Retrieve relevant context
        context_data = await self.retrieve_relevant_context(query, company_ticker)
        
        # Build structured context string
        context_parts = []
        total_length = 0
        
        # Prioritize context types by relevance to query
        priority_order = self._determine_context_priority(query)
        
        for context_type in priority_order:
            if context_type in context_data:
                context_parts.append(f"\n## {context_type.replace('_', ' ').title()} Context:")
                
                for chunk in context_data[context_type]:
                    chunk_text = f"\n- {chunk['content'][:500]}..."
                    
                    if total_length + len(chunk_text) > self.max_context_length:
                        break
                    
                    context_parts.append(chunk_text)
                    total_length += len(chunk_text)
                
                if total_length > self.max_context_length:
                    break
        
        return ''.join(context_parts)
    
    def _determine_context_priority(self, query: str) -> List[str]:
        """Determine context priority based on query content"""
        query_lower = query.lower()
        
        # Financial analysis queries
        if any(term in query_lower for term in ['revenue', 'profit', 'margin', 'earnings', 'financial']):
            return ['financial_statements', 'sec_filings', 'news_articles', 'company_docs']
        
        # Risk analysis queries
        elif any(term in query_lower for term in ['risk', 'threat', 'challenge', 'competition']):
            return ['sec_filings', 'news_articles', 'financial_statements', 'company_docs']
        
        # Market/business queries
        elif any(term in query_lower for term in ['market', 'business', 'strategy', 'competitive']):
            return ['company_docs', 'sec_filings', 'news_articles', 'financial_statements']
        
        # Default priority
        else:
            return ['sec_filings', 'financial_statements', 'news_articles', 'company_docs']
```

## Kiro Integration with RAG

### Enhanced Kiro Prompts with RAG Context
```python
class RAGEnhancedKiroEngine:
    def __init__(self, kiro_engine, rag_processor: RAGQueryProcessor):
        self.kiro_engine = kiro_engine
        self.rag_processor = rag_processor
    
    async def execute_rag_enhanced_prompt(self, prompt_name: str, query: str, company_ticker: str, additional_context: dict = None) -> dict:
        """Execute Kiro prompt with RAG-enhanced context"""
        
        # Retrieve relevant context
        rag_context = await self.rag_processor.prepare_kiro_context(query, company_ticker)
        
        # Prepare enhanced context
        enhanced_context = {
            'query': query,
            'company_ticker': company_ticker,
            'rag_context': rag_context,
            **(additional_context or {})
        }
        
        # Execute Kiro prompt with enhanced context
        result = await self.kiro_engine.execute_prompt(prompt_name, enhanced_context)
        
        return result
    
    async def generate_contextual_analysis(self, company_ticker: str, analysis_type: str) -> dict:
        """Generate analysis with full RAG context"""
        
        analysis_queries = {
            'financial': f"Analyze the financial performance and trends for {company_ticker}",
            'competitive': f"Analyze the competitive position and market dynamics for {company_ticker}",
            'risk': f"Identify and analyze key risks and challenges for {company_ticker}",
            'valuation': f"Perform valuation analysis for {company_ticker} using multiple methodologies"
        }
        
        query = analysis_queries.get(analysis_type, f"Provide comprehensive analysis for {company_ticker}")
        
        return await self.execute_rag_enhanced_prompt(
            f"analyze-{analysis_type}",
            query,
            company_ticker
        )
```

## User-Specific RAG Context

### Personalized Context Management
```python
class PersonalizedRAGManager:
    def __init__(self, embedding_manager: EmbeddingManager):
        self.embedding_manager = embedding_manager
    
    async def create_user_context_collection(self, user_id: str):
        """Create personalized context collection for user"""
        collection_name = f"user_context_{user_id}"
        
        return self.embedding_manager.chroma_client.get_or_create_collection(
            collection_name,
            metadata={"user_id": user_id}
        )
    
    async def add_user_research_notes(self, user_id: str, company_ticker: str, notes: str):
        """Add user's research notes to their personal context"""
        collection = await self.create_user_context_collection(user_id)
        
        # Create embedding for notes
        embedding = await self.embedding_manager.create_embeddings([notes])
        
        # Store in user's personal collection
        collection.add(
            embeddings=embedding.tolist(),
            documents=[notes],
            metadatas=[{
                'user_id': user_id,
                'company_ticker': company_ticker,
                'content_type': 'user_notes',
                'created_at': datetime.now().isoformat()
            }],
            ids=[f"{user_id}_{company_ticker}_notes_{int(time.time())}"]
        )
    
    async def get_user_context(self, user_id: str, query: str, company_ticker: str) -> List[str]:
        """Retrieve user-specific context for enhanced personalization"""
        try:
            collection = await self.create_user_context_collection(user_id)
            
            query_embedding = await self.embedding_manager.create_embeddings([query])
            
            results = collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=3,
                where={"company_ticker": company_ticker}
            )
            
            return results['documents'][0] if results['documents'] else []
            
        except Exception as e:
            print(f"Error retrieving user context: {e}")
            return []
```

## RAG Performance Optimization

### Caching and Indexing Strategy
```python
class RAGPerformanceOptimizer:
    def __init__(self, cache_manager, embedding_manager):
        self.cache_manager = cache_manager
        self.embedding_manager = embedding_manager
    
    async def cache_frequent_queries(self, query: str, company_ticker: str, results: dict):
        """Cache frequently accessed RAG results"""
        cache_key = f"rag_query:{hash(query + company_ticker)}"
        await self.cache_manager.cache_kiro_result(cache_key, results, ttl=3600)
    
    async def get_cached_query_results(self, query: str, company_ticker: str) -> dict:
        """Retrieve cached RAG results"""
        cache_key = f"rag_query:{hash(query + company_ticker)}"
        return await self.cache_manager.get_cached_kiro_result(cache_key)
    
    async def precompute_company_embeddings(self, company_ticker: str):
        """Precompute and cache embeddings for popular companies"""
        # This would run as a background task
        # Precompute embeddings for all documents related to the company
        # Store in optimized format for faster retrieval
        pass
    
    async def optimize_vector_search(self):
        """Optimize vector database performance"""
        # Implement HNSW indexing for faster similarity search
        # Periodic index rebuilding
        # Query performance monitoring
        pass
```

## RAG Quality Assurance

### Context Relevance Validation
```python
class RAGQualityValidator:
    def __init__(self):
        self.relevance_threshold = 0.7
        self.context_diversity_threshold = 0.3
    
    async def validate_context_relevance(self, query: str, retrieved_context: List[dict]) -> dict:
        """Validate that retrieved context is relevant to the query"""
        
        relevance_scores = []
        for context in retrieved_context:
            # Calculate semantic similarity between query and context
            similarity = await self._calculate_semantic_similarity(query, context['content'])
            relevance_scores.append(similarity)
        
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        
        return {
            'average_relevance': avg_relevance,
            'meets_threshold': avg_relevance >= self.relevance_threshold,
            'individual_scores': relevance_scores
        }
    
    async def ensure_context_diversity(self, retrieved_context: List[dict]) -> bool:
        """Ensure retrieved context covers diverse aspects"""
        
        if len(retrieved_context) < 2:
            return True
        
        # Calculate diversity based on source types and content similarity
        source_types = set(ctx['metadata'].get('source', 'unknown') for ctx in retrieved_context)
        source_diversity = len(source_types) / len(retrieved_context)
        
        return source_diversity >= self.context_diversity_threshold
    
    async def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        # Implementation would use sentence transformers or similar
        # For now, return a placeholder
        return 0.8  # Placeholder
```

*Last Updated: 2026-01-22*
