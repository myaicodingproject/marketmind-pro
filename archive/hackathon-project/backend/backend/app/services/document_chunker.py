"""
Advanced Document Chunking and Embedding System for RAG

This module provides intelligent document chunking strategies optimized for financial documents:
- Semantic chunking based on content structure
- Overlapping chunks for context preservation
- Financial table-aware chunking
- Metadata-rich chunk generation
- Embedding optimization for ChromaDB
"""

import re
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import hashlib
from datetime import datetime
import logging

import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class ChunkType(Enum):
    """Types of document chunks"""
    PARAGRAPH = "paragraph"
    SECTION = "section"
    TABLE = "table"
    LIST = "list"
    FINANCIAL_DATA = "financial_data"
    REGULATORY_TEXT = "regulatory_text"
    EXECUTIVE_SUMMARY = "executive_summary"

@dataclass
class DocumentChunk:
    """Enhanced document chunk with rich metadata"""
    id: str
    content: str
    chunk_type: ChunkType
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None
    
    # Position information
    chunk_index: int = 0
    total_chunks: int = 1
    start_position: int = 0
    end_position: int = 0
    
    # Content metrics
    word_count: int = 0
    sentence_count: int = 0
    
    # Financial context
    contains_numbers: bool = False
    contains_financial_terms: bool = False
    financial_concepts: List[str] = None
    
    def __post_init__(self):
        if self.financial_concepts is None:
            self.financial_concepts = []
        
        # Calculate metrics
        self.word_count = len(self.content.split())
        self.sentence_count = len(re.findall(r'[.!?]+', self.content))
        self.contains_numbers = bool(re.search(r'\d+', self.content))
        
        # Check for financial terms
        financial_terms = [
            'revenue', 'income', 'profit', 'loss', 'earnings', 'ebitda',
            'assets', 'liabilities', 'equity', 'debt', 'cash', 'dividend',
            'margin', 'ratio', 'valuation', 'growth', 'return', 'yield'
        ]
        
        content_lower = self.content.lower()
        self.financial_concepts = [term for term in financial_terms if term in content_lower]
        self.contains_financial_terms = len(self.financial_concepts) > 0

class DocumentChunker:
    """Advanced document chunker for financial documents"""
    
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        # Initialize sentence transformer for embeddings
        try:
            self.embedding_model = SentenceTransformer(embedding_model)
            logger.info(f"Loaded embedding model: {embedding_model}")
        except Exception as e:
            logger.warning(f"Failed to load embedding model: {e}")
            self.embedding_model = None
        
        # Chunking parameters
        self.chunk_size = 1000  # Target chunk size in characters
        self.chunk_overlap = 200  # Overlap between chunks
        self.min_chunk_size = 100  # Minimum viable chunk size
        self.max_chunk_size = 2000  # Maximum chunk size
        
        # Financial document patterns
        self.section_patterns = {
            'executive_summary': [
                r'executive\s+summary', r'summary', r'overview',
                r'highlights', r'key\s+points'
            ],
            'business_description': [
                r'business\s+description', r'our\s+business', r'company\s+overview',
                r'operations', r'products\s+and\s+services'
            ],
            'financial_performance': [
                r'financial\s+performance', r'results\s+of\s+operations',
                r'financial\s+results', r'revenue', r'earnings'
            ],
            'risk_factors': [
                r'risk\s+factors', r'risks?', r'uncertainties',
                r'forward.looking\s+statements'
            ],
            'management_discussion': [
                r'management.s\s+discussion', r'md&a', r'analysis\s+of',
                r'liquidity\s+and\s+capital'
            ]
        }
        
        # Financial table indicators
        self.table_indicators = [
            r'consolidated\s+statements?',
            r'balance\s+sheet',
            r'income\s+statement',
            r'cash\s+flow',
            r'statement\s+of\s+operations',
            r'financial\s+position'
        ]
    
    def chunk_document(self, content: str, document_metadata: Dict[str, Any]) -> List[DocumentChunk]:
        """Main document chunking method"""
        logger.info(f"Chunking document: {document_metadata.get('document_id', 'unknown')}")
        
        # Preprocess content
        processed_content = self._preprocess_content(content)
        
        # Identify document structure
        structure = self._analyze_document_structure(processed_content)
        
        # Create chunks based on structure
        chunks = []
        
        # Handle different content types
        if structure['has_sections']:
            chunks.extend(self._chunk_by_sections(processed_content, document_metadata, structure))
        else:
            chunks.extend(self._chunk_by_paragraphs(processed_content, document_metadata))
        
        # Handle tables separately
        if structure['has_tables']:
            table_chunks = self._chunk_tables(processed_content, document_metadata)
            chunks.extend(table_chunks)
        
        # Generate embeddings
        if self.embedding_model:
            chunks = self._generate_embeddings(chunks)
        
        # Post-process chunks
        chunks = self._post_process_chunks(chunks)
        
        logger.info(f"Created {len(chunks)} chunks from document")
        return chunks
    
    def _preprocess_content(self, content: str) -> str:
        """Preprocess document content"""
        # Normalize whitespace
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        
        # Fix common formatting issues
        content = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', content)
        
        # Normalize financial notation
        content = re.sub(r'\$\s*(\d)', r'$\1', content)
        content = re.sub(r'(\d)\s*%', r'\1%', content)
        
        return content.strip()
    
    def _analyze_document_structure(self, content: str) -> Dict[str, Any]:
        """Analyze document structure to inform chunking strategy"""
        structure = {
            'has_sections': False,
            'has_tables': False,
            'has_lists': False,
            'section_count': 0,
            'table_count': 0,
            'avg_paragraph_length': 0,
            'document_type': 'unknown'
        }
        
        # Check for sections
        section_matches = 0
        for patterns in self.section_patterns.values():
            for pattern in patterns:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                section_matches += matches
        
        structure['section_count'] = section_matches
        structure['has_sections'] = section_matches > 2
        
        # Check for tables
        table_matches = 0
        for pattern in self.table_indicators:
            matches = len(re.findall(pattern, content, re.IGNORECASE))
            table_matches += matches
        
        structure['table_count'] = table_matches
        structure['has_tables'] = table_matches > 0
        
        # Check for lists
        list_patterns = [r'^\s*[\d\w]\.\s', r'^\s*•\s', r'^\s*-\s']
        list_matches = sum(len(re.findall(pattern, content, re.MULTILINE)) for pattern in list_patterns)
        structure['has_lists'] = list_matches > 5
        
        # Calculate average paragraph length
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if paragraphs:
            structure['avg_paragraph_length'] = sum(len(p) for p in paragraphs) / len(paragraphs)
        
        return structure
    
    def _chunk_by_sections(self, content: str, metadata: Dict, structure: Dict) -> List[DocumentChunk]:
        """Chunk document by identified sections"""
        chunks = []
        
        # Find section boundaries
        section_boundaries = []
        
        for section_name, patterns in self.section_patterns.items():
            for pattern in patterns:
                matches = list(re.finditer(pattern, content, re.IGNORECASE))
                for match in matches:
                    section_boundaries.append({
                        'position': match.start(),
                        'name': section_name,
                        'pattern': pattern
                    })
        
        # Sort by position
        section_boundaries.sort(key=lambda x: x['position'])
        
        # Create section chunks
        for i, boundary in enumerate(section_boundaries):
            start_pos = boundary['position']
            
            # Find end position (next section or end of document)
            if i + 1 < len(section_boundaries):
                end_pos = section_boundaries[i + 1]['position']
            else:
                end_pos = len(content)
            
            section_content = content[start_pos:end_pos].strip()
            
            # Skip very short sections
            if len(section_content) < self.min_chunk_size:
                continue
            
            # If section is too long, split it further
            if len(section_content) > self.max_chunk_size:
                sub_chunks = self._split_large_section(section_content, metadata, boundary['name'])
                chunks.extend(sub_chunks)
            else:
                chunk = self._create_chunk(
                    content=section_content,
                    chunk_type=ChunkType.SECTION,
                    metadata=metadata,
                    additional_metadata={
                        'section_name': boundary['name'],
                        'section_pattern': boundary['pattern']
                    },
                    start_pos=start_pos,
                    end_pos=end_pos
                )
                chunks.append(chunk)
        
        return chunks
    
    def _chunk_by_paragraphs(self, content: str, metadata: Dict) -> List[DocumentChunk]:
        """Chunk document by paragraphs with overlap"""
        chunks = []
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        current_chunk = ""
        current_start = 0
        chunk_index = 0
        
        for i, paragraph in enumerate(paragraphs):
            # Check if adding this paragraph would exceed chunk size
            if len(current_chunk) + len(paragraph) > self.chunk_size and current_chunk:
                # Create chunk
                chunk = self._create_chunk(
                    content=current_chunk.strip(),
                    chunk_type=ChunkType.PARAGRAPH,
                    metadata=metadata,
                    chunk_index=chunk_index,
                    start_pos=current_start
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                current_chunk = overlap_text + " " + paragraph
                current_start = self._find_content_position(content, overlap_text)
                chunk_index += 1
            else:
                if not current_chunk:
                    current_start = self._find_content_position(content, paragraph)
                current_chunk += " " + paragraph if current_chunk else paragraph
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                content=current_chunk.strip(),
                chunk_type=ChunkType.PARAGRAPH,
                metadata=metadata,
                chunk_index=chunk_index
            )
            chunks.append(chunk)
        
        return chunks
    
    def _chunk_tables(self, content: str, metadata: Dict) -> List[DocumentChunk]:
        """Extract and chunk financial tables"""
        chunks = []
        
        # Find table-like structures
        table_patterns = [
            r'(consolidated\s+statements?[^\n]*\n(?:[^\n]*\n){3,20})',
            r'(balance\s+sheet[^\n]*\n(?:[^\n]*\n){3,20})',
            r'(income\s+statement[^\n]*\n(?:[^\n]*\n){3,20})'
        ]
        
        for i, pattern in enumerate(table_patterns):
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            
            for j, match in enumerate(matches):
                table_content = match.group(1).strip()
                
                if len(table_content) > self.min_chunk_size:
                    chunk = self._create_chunk(
                        content=table_content,
                        chunk_type=ChunkType.TABLE,
                        metadata=metadata,
                        additional_metadata={
                            'table_index': j,
                            'table_pattern': pattern
                        },
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    chunks.append(chunk)
        
        return chunks
    
    def _split_large_section(self, section_content: str, metadata: Dict, section_name: str) -> List[DocumentChunk]:
        """Split large sections into smaller chunks"""
        chunks = []
        
        # Split by sentences for more natural breaks
        sentences = re.split(r'[.!?]+', section_content)
        
        current_chunk = ""
        chunk_index = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunk = self._create_chunk(
                    content=current_chunk.strip(),
                    chunk_type=ChunkType.SECTION,
                    metadata=metadata,
                    additional_metadata={
                        'section_name': section_name,
                        'sub_chunk_index': chunk_index
                    }
                )
                chunks.append(chunk)
                
                # Start new chunk with overlap
                overlap_text = self._get_overlap_text(current_chunk, self.chunk_overlap)
                current_chunk = overlap_text + " " + sentence
                chunk_index += 1
            else:
                current_chunk += " " + sentence if current_chunk else sentence
        
        # Add final chunk
        if current_chunk.strip():
            chunk = self._create_chunk(
                content=current_chunk.strip(),
                chunk_type=ChunkType.SECTION,
                metadata=metadata,
                additional_metadata={
                    'section_name': section_name,
                    'sub_chunk_index': chunk_index
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, content: str, chunk_type: ChunkType, metadata: Dict, 
                     additional_metadata: Dict = None, chunk_index: int = 0,
                     start_pos: int = 0, end_pos: int = 0) -> DocumentChunk:
        """Create a document chunk with rich metadata"""
        
        # Generate chunk ID
        chunk_id = self._generate_chunk_id(content, metadata, chunk_index)
        
        # Combine metadata
        chunk_metadata = {
            **metadata,
            'chunk_type': chunk_type.value,
            'created_at': datetime.now().isoformat(),
            'chunk_size': len(content)
        }
        
        if additional_metadata:
            chunk_metadata.update(additional_metadata)
        
        return DocumentChunk(
            id=chunk_id,
            content=content,
            chunk_type=chunk_type,
            metadata=chunk_metadata,
            chunk_index=chunk_index,
            start_position=start_pos,
            end_position=end_pos if end_pos > 0 else start_pos + len(content)
        )
    
    def _generate_chunk_id(self, content: str, metadata: Dict, chunk_index: int) -> str:
        """Generate unique chunk ID"""
        ticker = metadata.get('ticker', 'unknown')
        doc_type = metadata.get('document_type', 'unknown')
        doc_id = metadata.get('document_id', 'unknown')
        
        # Create hash of content for uniqueness
        content_hash = hashlib.md5(content.encode()).hexdigest()[:8]
        
        return f"{ticker}_{doc_type}_{doc_id}_{chunk_index}_{content_hash}"
    
    def _get_overlap_text(self, text: str, overlap_size: int) -> str:
        """Get overlap text from end of current chunk"""
        if len(text) <= overlap_size:
            return text
        
        # Try to break at sentence boundary
        overlap_text = text[-overlap_size:]
        sentence_break = overlap_text.find('. ')
        
        if sentence_break > 0:
            return overlap_text[sentence_break + 2:]
        
        return overlap_text
    
    def _find_content_position(self, full_content: str, search_text: str) -> int:
        """Find position of text in full content"""
        pos = full_content.find(search_text)
        return pos if pos >= 0 else 0
    
    def _generate_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Generate embeddings for chunks"""
        if not self.embedding_model:
            logger.warning("No embedding model available")
            return chunks
        
        try:
            # Extract content for embedding
            contents = [chunk.content for chunk in chunks]
            
            # Generate embeddings in batches
            batch_size = 32
            for i in range(0, len(contents), batch_size):
                batch_contents = contents[i:i + batch_size]
                batch_embeddings = self.embedding_model.encode(batch_contents)
                
                # Assign embeddings to chunks
                for j, embedding in enumerate(batch_embeddings):
                    chunk_idx = i + j
                    if chunk_idx < len(chunks):
                        chunks[chunk_idx].embedding = embedding.tolist()
            
            logger.info(f"Generated embeddings for {len(chunks)} chunks")
        
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
        
        return chunks
    
    def _post_process_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Post-process chunks for quality and consistency"""
        processed_chunks = []
        
        for chunk in chunks:
            # Skip very short chunks
            if len(chunk.content) < self.min_chunk_size:
                continue
            
            # Update total chunks count
            chunk.total_chunks = len(chunks)
            
            # Enhance metadata based on content analysis
            chunk.metadata.update({
                'word_count': chunk.word_count,
                'sentence_count': chunk.sentence_count,
                'contains_numbers': chunk.contains_numbers,
                'contains_financial_terms': chunk.contains_financial_terms,
                'financial_concepts': chunk.financial_concepts
            })
            
            processed_chunks.append(chunk)
        
        return processed_chunks

# Utility functions for chunk analysis
def analyze_chunk_quality(chunks: List[DocumentChunk]) -> Dict[str, Any]:
    """Analyze the quality of generated chunks"""
    if not chunks:
        return {"error": "No chunks to analyze"}
    
    stats = {
        "total_chunks": len(chunks),
        "avg_chunk_size": sum(len(c.content) for c in chunks) / len(chunks),
        "chunk_types": {},
        "financial_chunks": sum(1 for c in chunks if c.contains_financial_terms),
        "chunks_with_numbers": sum(1 for c in chunks if c.contains_numbers),
        "avg_word_count": sum(c.word_count for c in chunks) / len(chunks),
        "chunks_with_embeddings": sum(1 for c in chunks if c.embedding is not None)
    }
    
    # Count chunk types
    for chunk in chunks:
        chunk_type = chunk.chunk_type.value
        stats["chunk_types"][chunk_type] = stats["chunk_types"].get(chunk_type, 0) + 1
    
    return stats

def find_similar_chunks(target_chunk: DocumentChunk, all_chunks: List[DocumentChunk], 
                       top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
    """Find similar chunks using embedding similarity"""
    if not target_chunk.embedding:
        return []
    
    similarities = []
    target_embedding = np.array(target_chunk.embedding)
    
    for chunk in all_chunks:
        if chunk.id == target_chunk.id or not chunk.embedding:
            continue
        
        chunk_embedding = np.array(chunk.embedding)
        similarity = np.dot(target_embedding, chunk_embedding) / (
            np.linalg.norm(target_embedding) * np.linalg.norm(chunk_embedding)
        )
        similarities.append((chunk, similarity))
    
    # Sort by similarity and return top k
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_k]