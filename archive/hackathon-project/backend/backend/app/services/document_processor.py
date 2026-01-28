"""
Advanced Document Processing Pipeline for SEC Filings and Financial Documents

This module provides comprehensive document processing capabilities including:
- PDF/HTML parsing and text extraction
- Document chunking and preprocessing for RAG
- Embedding generation with ChromaDB
- Semantic search and context retrieval
- Document classification and metadata extraction
"""

import asyncio
import re
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass
from enum import Enum

import httpx
import pandas as pd
from bs4 import BeautifulSoup
import chromadb
from chromadb.config import Settings

# Configure logging
logger = logging.getLogger(__name__)

class DocumentType(Enum):
    """Document type classification"""
    SEC_10K = "10-K"
    SEC_10Q = "10-Q" 
    SEC_8K = "8-K"
    SEC_DEF14A = "DEF 14A"
    FINANCIAL_STATEMENT = "financial_statement"
    EARNINGS_REPORT = "earnings_report"
    PRESS_RELEASE = "press_release"
    UNKNOWN = "unknown"

@dataclass
class DocumentChunk:
    """Document chunk for RAG processing"""
    id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    chunk_index: int = 0
    total_chunks: int = 1

@dataclass
class ProcessedDocument:
    """Processed document with metadata and chunks"""
    document_id: str
    ticker: str
    document_type: DocumentType
    title: str
    filing_date: Optional[str]
    url: Optional[str]
    raw_content: str
    processed_content: str
    chunks: List[DocumentChunk]
    metadata: Dict[str, Any]
    financial_tables: List[Dict[str, Any]]
    key_sections: Dict[str, str]

class DocumentProcessor:
    """Advanced document processor for SEC filings and financial documents"""
    
    def __init__(self, chroma_path: str = "./chroma_db"):
        self.chroma_path = Path(chroma_path)
        self.chroma_path.mkdir(exist_ok=True)
        
        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=Settings(anonymized_telemetry=False, allow_reset=False)
        )
        
        # Collections for different document types
        self.collections = {
            "sec_filings": self._get_or_create_collection("sec_filings_v2"),
            "financial_statements": self._get_or_create_collection("financial_statements_v2"),
            "earnings_reports": self._get_or_create_collection("earnings_reports_v2"),
            "general_documents": self._get_or_create_collection("general_documents_v2")
        }
        
        # HTTP client for document fetching
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "MarketMind-Pro/1.0 (Document Processor)"}
        )
        
        # Document classification patterns
        self.classification_patterns = {
            DocumentType.SEC_10K: [r"form\s*10-?k", r"annual\s*report"],
            DocumentType.SEC_10Q: [r"form\s*10-?q", r"quarterly\s*report"],
            DocumentType.SEC_8K: [r"form\s*8-?k", r"current\s*report"],
            DocumentType.SEC_DEF14A: [r"def\s*14a", r"proxy\s*statement"],
            DocumentType.FINANCIAL_STATEMENT: [r"financial\s*statement", r"balance\s*sheet", r"income\s*statement"],
            DocumentType.EARNINGS_REPORT: [r"earnings", r"quarterly\s*results"],
            DocumentType.PRESS_RELEASE: [r"press\s*release", r"news\s*release"]
        }
        
        logger.info("Document processor initialized")
    
    def _get_or_create_collection(self, name: str):
        """Get or create ChromaDB collection"""
        try:
            return self.client.get_collection(name=name)
        except ValueError:
            return self.client.create_collection(name=name)
    
    async def process_sec_filing(self, ticker: str, filing_url: str, filing_metadata: Dict) -> ProcessedDocument:
        """Process SEC filing document"""
        logger.info(f"Processing SEC filing for {ticker}: {filing_url}")
        
        # Fetch document content
        raw_content = await self._fetch_document_content(filing_url)
        
        # Extract and clean content
        processed_content = self._extract_text_from_html(raw_content)
        
        # Classify document
        doc_type = self._classify_document(processed_content, filing_metadata)
        
        # Extract key sections
        key_sections = self._extract_sec_sections(processed_content, doc_type)
        
        # Extract financial tables
        financial_tables = self._extract_financial_tables(raw_content)
        
        # Generate document ID
        doc_id = self._generate_document_id(ticker, doc_type, filing_metadata.get("filing_date", ""))
        
        # Create chunks for RAG
        chunks = self._create_document_chunks(
            processed_content, 
            ticker, 
            doc_type, 
            filing_metadata
        )
        
        # Create processed document
        processed_doc = ProcessedDocument(
            document_id=doc_id,
            ticker=ticker,
            document_type=doc_type,
            title=filing_metadata.get("form", "SEC Filing"),
            filing_date=filing_metadata.get("filing_date"),
            url=filing_url,
            raw_content=raw_content,
            processed_content=processed_content,
            chunks=chunks,
            metadata=filing_metadata,
            financial_tables=financial_tables,
            key_sections=key_sections
        )
        
        # Store in ChromaDB
        await self._store_document_in_chromadb(processed_doc)
        
        logger.info(f"Processed SEC filing {doc_id}: {len(chunks)} chunks, {len(financial_tables)} tables")
        return processed_doc
    
    async def process_financial_document(self, ticker: str, content: str, metadata: Dict) -> ProcessedDocument:
        """Process financial statement or earnings report"""
        logger.info(f"Processing financial document for {ticker}")
        
        # Classify document
        doc_type = self._classify_document(content, metadata)
        
        # Extract financial tables
        financial_tables = self._extract_financial_data_from_json(content)
        
        # Generate document ID
        doc_id = self._generate_document_id(ticker, doc_type, metadata.get("date", ""))
        
        # Create chunks
        chunks = self._create_document_chunks(content, ticker, doc_type, metadata)
        
        # Create processed document
        processed_doc = ProcessedDocument(
            document_id=doc_id,
            ticker=ticker,
            document_type=doc_type,
            title=metadata.get("title", "Financial Document"),
            filing_date=metadata.get("date"),
            url=None,
            raw_content=content,
            processed_content=content,
            chunks=chunks,
            metadata=metadata,
            financial_tables=financial_tables,
            key_sections={}
        )
        
        # Store in ChromaDB
        await self._store_document_in_chromadb(processed_doc)
        
        logger.info(f"Processed financial document {doc_id}: {len(chunks)} chunks")
        return processed_doc
    
    async def _fetch_document_content(self, url: str) -> str:
        """Fetch document content from URL"""
        try:
            response = await self.http_client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Failed to fetch document from {url}: {e}")
            raise
    
    def _extract_text_from_html(self, html_content: str) -> str:
        """Extract clean text from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def _classify_document(self, content: str, metadata: Dict) -> DocumentType:
        """Classify document type based on content and metadata"""
        content_lower = content.lower()
        
        # Check metadata first
        form_type = metadata.get("form", "").lower()
        title = metadata.get("title", "").lower()
        
        # Direct form type matching
        if "10-k" in form_type or "10k" in form_type:
            return DocumentType.SEC_10K
        elif "10-q" in form_type or "10q" in form_type:
            return DocumentType.SEC_10Q
        elif "8-k" in form_type or "8k" in form_type:
            return DocumentType.SEC_8K
        elif "def 14a" in form_type:
            return DocumentType.SEC_DEF14A
        
        # Pattern matching in content
        for doc_type, patterns in self.classification_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower) or re.search(pattern, title):
                    return doc_type
        
        return DocumentType.UNKNOWN
    
    def _extract_sec_sections(self, content: str, doc_type: DocumentType) -> Dict[str, str]:
        """Extract key sections from SEC filings"""
        sections = {}
        
        if doc_type == DocumentType.SEC_10K:
            # 10-K specific sections
            section_patterns = {
                "business": r"item\s*1\s*[\.\-\s]*business",
                "risk_factors": r"item\s*1a\s*[\.\-\s]*risk\s*factors",
                "properties": r"item\s*2\s*[\.\-\s]*properties",
                "legal_proceedings": r"item\s*3\s*[\.\-\s]*legal\s*proceedings",
                "management_discussion": r"item\s*7\s*[\.\-\s]*management",
                "financial_statements": r"item\s*8\s*[\.\-\s]*financial\s*statements"
            }
        elif doc_type == DocumentType.SEC_10Q:
            # 10-Q specific sections
            section_patterns = {
                "financial_statements": r"part\s*i\s*[\.\-\s]*financial\s*information",
                "management_discussion": r"item\s*2\s*[\.\-\s]*management",
                "legal_proceedings": r"item\s*1\s*[\.\-\s]*legal\s*proceedings"
            }
        else:
            return sections
        
        # Extract sections using patterns
        for section_name, pattern in section_patterns.items():
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                start_pos = match.start()
                # Find next section or end of document
                next_section = re.search(r"item\s*\d+", content[start_pos + 100:], re.IGNORECASE)
                if next_section:
                    end_pos = start_pos + 100 + next_section.start()
                    sections[section_name] = content[start_pos:end_pos].strip()
                else:
                    sections[section_name] = content[start_pos:start_pos + 5000].strip()
        
        return sections
    
    def _extract_financial_tables(self, html_content: str) -> List[Dict[str, Any]]:
        """Extract financial tables from HTML content"""
        soup = BeautifulSoup(html_content, 'html.parser')
        tables = []
        
        # Find all tables
        html_tables = soup.find_all('table')
        
        for i, table in enumerate(html_tables):
            try:
                # Convert to pandas DataFrame
                df = pd.read_html(str(table))[0]
                
                # Skip very small tables
                if df.shape[0] < 2 or df.shape[1] < 2:
                    continue
                
                # Check if it looks like a financial table
                if self._is_financial_table(df):
                    table_data = {
                        "table_id": f"table_{i}",
                        "data": df.to_dict('records'),
                        "columns": df.columns.tolist(),
                        "shape": df.shape,
                        "table_type": self._classify_financial_table(df)
                    }
                    tables.append(table_data)
            
            except Exception as e:
                logger.debug(f"Failed to parse table {i}: {e}")
                continue
        
        return tables
    
    def _extract_financial_data_from_json(self, json_content: str) -> List[Dict[str, Any]]:
        """Extract financial data from JSON content"""
        try:
            data = json.loads(json_content) if isinstance(json_content, str) else json_content
            tables = []
            
            # Handle different JSON structures
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, dict) and "annualReports" in value:
                        # Alpha Vantage format
                        df = pd.DataFrame(value["annualReports"])
                        if not df.empty:
                            tables.append({
                                "table_id": key,
                                "data": df.to_dict('records'),
                                "columns": df.columns.tolist(),
                                "shape": df.shape,
                                "table_type": key
                            })
            
            return tables
        
        except Exception as e:
            logger.debug(f"Failed to extract financial data from JSON: {e}")
            return []
    
    def _is_financial_table(self, df: pd.DataFrame) -> bool:
        """Check if DataFrame contains financial data"""
        # Look for financial keywords in columns or data
        financial_keywords = [
            'revenue', 'income', 'expense', 'asset', 'liability', 'equity',
            'cash', 'debt', 'profit', 'loss', 'earnings', 'dividend',
            'share', 'stock', 'million', 'thousand', '$'
        ]
        
        # Check column names
        columns_text = ' '.join(str(col).lower() for col in df.columns)
        
        # Check first few rows
        sample_text = ' '.join(str(val).lower() for val in df.iloc[:3].values.flatten() if pd.notna(val))
        
        combined_text = columns_text + ' ' + sample_text
        
        return any(keyword in combined_text for keyword in financial_keywords)
    
    def _classify_financial_table(self, df: pd.DataFrame) -> str:
        """Classify the type of financial table"""
        columns_text = ' '.join(str(col).lower() for col in df.columns)
        
        if any(term in columns_text for term in ['revenue', 'income', 'expense']):
            return 'income_statement'
        elif any(term in columns_text for term in ['asset', 'liability', 'equity']):
            return 'balance_sheet'
        elif any(term in columns_text for term in ['cash', 'operating', 'investing', 'financing']):
            return 'cash_flow'
        else:
            return 'other_financial'
    
    def _create_document_chunks(self, content: str, ticker: str, doc_type: DocumentType, metadata: Dict) -> List[DocumentChunk]:
        """Create document chunks for RAG processing"""
        # Chunk size and overlap parameters
        chunk_size = 1000
        chunk_overlap = 200
        
        # Split content into sentences for better chunking
        sentences = re.split(r'[.!?]+', content)
        
        chunks = []
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > chunk_size and current_chunk:
                # Create chunk
                chunk_id = f"{ticker}_{doc_type.value}_{chunk_index}"
                
                chunk_metadata = {
                    **metadata,
                    "ticker": ticker,
                    "document_type": doc_type.value,
                    "chunk_index": chunk_index,
                    "created_at": datetime.now().isoformat()
                }
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    content=current_chunk.strip(),
                    metadata=chunk_metadata,
                    chunk_index=chunk_index
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
                chunk_index += 1
            else:
                current_chunk += " " + sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunk_id = f"{ticker}_{doc_type.value}_{chunk_index}"
            chunk_metadata = {
                **metadata,
                "ticker": ticker,
                "document_type": doc_type.value,
                "chunk_index": chunk_index,
                "created_at": datetime.now().isoformat()
            }
            
            chunk = DocumentChunk(
                id=chunk_id,
                content=current_chunk.strip(),
                metadata=chunk_metadata,
                chunk_index=chunk_index
            )
            chunks.append(chunk)
        
        # Update total chunks count
        for chunk in chunks:
            chunk.total_chunks = len(chunks)
        
        return chunks
    
    async def _store_document_in_chromadb(self, document: ProcessedDocument):
        """Store processed document in ChromaDB"""
        # Determine collection based on document type
        if document.document_type in [DocumentType.SEC_10K, DocumentType.SEC_10Q, DocumentType.SEC_8K, DocumentType.SEC_DEF14A]:
            collection = self.collections["sec_filings"]
        elif document.document_type == DocumentType.FINANCIAL_STATEMENT:
            collection = self.collections["financial_statements"]
        elif document.document_type == DocumentType.EARNINGS_REPORT:
            collection = self.collections["earnings_reports"]
        else:
            collection = self.collections["general_documents"]
        
        # Prepare data for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for chunk in document.chunks:
            documents.append(chunk.content)
            metadatas.append(chunk.metadata)
            ids.append(chunk.id)
        
        # Store in ChromaDB
        try:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Stored {len(documents)} chunks in ChromaDB for document {document.document_id}")
        except Exception as e:
            logger.error(f"Failed to store document in ChromaDB: {e}")
            raise
    
    def _generate_document_id(self, ticker: str, doc_type: DocumentType, date: str) -> str:
        """Generate unique document ID"""
        content = f"{ticker}_{doc_type.value}_{date}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    async def search_documents(self, query: str, ticker: Optional[str] = None, 
                             doc_type: Optional[DocumentType] = None, 
                             n_results: int = 10) -> List[Dict[str, Any]]:
        """Search documents using semantic search"""
        results = []
        
        # Build where clause
        where_clause = {}
        if ticker:
            where_clause["ticker"] = ticker
        if doc_type:
            where_clause["document_type"] = doc_type.value
        
        # Search across relevant collections
        collections_to_search = []
        if not doc_type or doc_type in [DocumentType.SEC_10K, DocumentType.SEC_10Q, DocumentType.SEC_8K, DocumentType.SEC_DEF14A]:
            collections_to_search.append(("sec_filings", self.collections["sec_filings"]))
        if not doc_type or doc_type == DocumentType.FINANCIAL_STATEMENT:
            collections_to_search.append(("financial_statements", self.collections["financial_statements"]))
        if not doc_type or doc_type == DocumentType.EARNINGS_REPORT:
            collections_to_search.append(("earnings_reports", self.collections["earnings_reports"]))
        if not doc_type or doc_type == DocumentType.UNKNOWN:
            collections_to_search.append(("general_documents", self.collections["general_documents"]))
        
        for collection_name, collection in collections_to_search:
            try:
                search_results = collection.query(
                    query_texts=[query],
                    n_results=min(n_results, 100),  # ChromaDB limit
                    where=where_clause if where_clause else None
                )
                
                for i, doc in enumerate(search_results["documents"][0]):
                    results.append({
                        "collection": collection_name,
                        "content": doc,
                        "metadata": search_results["metadatas"][0][i],
                        "distance": search_results["distances"][0][i],
                        "id": search_results["ids"][0][i]
                    })
            
            except Exception as e:
                logger.error(f"Error searching {collection_name}: {e}")
        
        # Sort by relevance (distance)
        results.sort(key=lambda x: x["distance"])
        return results[:n_results]
    
    async def get_company_context(self, ticker: str, query: str = "", max_chunks: int = 20) -> str:
        """Get comprehensive context for a company for RAG"""
        if query:
            # Semantic search with query
            results = await self.search_documents(query, ticker=ticker, n_results=max_chunks)
        else:
            # Get recent documents for the ticker
            results = []
            for collection_name, collection in self.collections.items():
                try:
                    search_results = collection.get(
                        where={"ticker": ticker},
                        limit=max_chunks // len(self.collections)
                    )
                    
                    for i, doc in enumerate(search_results["documents"]):
                        results.append({
                            "collection": collection_name,
                            "content": doc,
                            "metadata": search_results["metadatas"][i],
                            "id": search_results["ids"][i],
                            "distance": 0.0  # No distance for direct retrieval
                        })
                
                except Exception as e:
                    logger.debug(f"No documents found in {collection_name} for {ticker}")
        
        # Format context for Kiro prompts
        context_sections = []
        
        # Group by document type
        by_doc_type = {}
        for result in results[:max_chunks]:
            doc_type = result["metadata"].get("document_type", "unknown")
            if doc_type not in by_doc_type:
                by_doc_type[doc_type] = []
            by_doc_type[doc_type].append(result)
        
        # Format each document type section
        for doc_type, docs in by_doc_type.items():
            section_header = f"=== {doc_type.upper().replace('_', ' ')} ==="
            context_sections.append(section_header)
            
            for doc in docs[:5]:  # Limit per document type
                content = doc["content"][:800]  # Limit chunk size
                metadata = doc["metadata"]
                
                chunk_info = f"[{metadata.get('filing_date', 'Unknown Date')}]"
                context_sections.append(f"{chunk_info} {content}...")
            
            context_sections.append("")  # Empty line between sections
        
        return "\n".join(context_sections)
    
    async def get_financial_tables_context(self, ticker: str) -> str:
        """Get financial tables context for analysis"""
        # Search for financial documents
        results = await self.search_documents(
            "financial statements income balance sheet cash flow",
            ticker=ticker,
            n_results=10
        )
        
        tables_context = []
        for result in results:
            metadata = result["metadata"]
            if "financial_tables" in metadata:
                tables_context.append(f"Financial Data from {metadata.get('filing_date', 'Unknown')}:")
                tables_context.append(result["content"][:500])
                tables_context.append("")
        
        return "\n".join(tables_context)
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get document processing statistics"""
        stats = {}
        
        for name, collection in self.collections.items():
            try:
                count = collection.count()
                stats[name] = count
            except Exception as e:
                stats[name] = f"Error: {e}"
        
        return {
            "collections": stats,
            "total_documents": sum(v for v in stats.values() if isinstance(v, int)),
            "chroma_path": str(self.chroma_path)
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        await self.http_client.aclose()

# Integration with Kiro CLI context preparation
class KiroContextPreparer:
    """Prepare context for Kiro CLI prompts using processed documents"""
    
    def __init__(self, document_processor: DocumentProcessor):
        self.doc_processor = document_processor
    
    async def prepare_company_analysis_context(self, ticker: str) -> Dict[str, str]:
        """Prepare comprehensive context for company analysis"""
        contexts = {}
        
        # Business overview context
        contexts["business_overview"] = await self.doc_processor.get_company_context(
            ticker, "business operations products services competitive position", 10
        )
        
        # Financial performance context
        contexts["financial_performance"] = await self.doc_processor.get_financial_tables_context(ticker)
        
        # Risk factors context
        contexts["risk_factors"] = await self.doc_processor.get_company_context(
            ticker, "risk factors uncertainties challenges", 8
        )
        
        # Recent developments context
        contexts["recent_developments"] = await self.doc_processor.get_company_context(
            ticker, "recent developments current events quarterly results", 6
        )
        
        return contexts
    
    async def prepare_valuation_context(self, ticker: str) -> str:
        """Prepare context specifically for valuation analysis"""
        return await self.doc_processor.get_company_context(
            ticker, "revenue earnings cash flow assets liabilities valuation metrics", 15
        )
    
    async def prepare_risk_assessment_context(self, ticker: str) -> str:
        """Prepare context for risk assessment"""
        return await self.doc_processor.get_company_context(
            ticker, "risk factors legal proceedings regulatory compliance market risks", 12
        )