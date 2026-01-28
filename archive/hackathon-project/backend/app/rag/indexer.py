import asyncio
import hashlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import openai
import asyncpg
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import tiktoken

@dataclass
class DocumentChunk:
    content: str
    metadata: Dict
    chunk_id: str
    embedding: Optional[List[float]] = None

class RAGIndexer:
    def __init__(self, openai_api_key: str, db_session: AsyncSession):
        openai.api_key = openai_api_key
        self.db = db_session
        self.encoder = tiktoken.get_encoding("cl100k_base")
        self.max_chunk_tokens = 512
        self.chunk_overlap = 50

    async def chunk_content(self, content: str, metadata: Dict) -> List[DocumentChunk]:
        """Split content into overlapping chunks optimized for embeddings"""
        tokens = self.encoder.encode(content)
        chunks = []
        
        for i in range(0, len(tokens), self.max_chunk_tokens - self.chunk_overlap):
            chunk_tokens = tokens[i:i + self.max_chunk_tokens]
            chunk_text = self.encoder.decode(chunk_tokens)
            
            chunk_id = hashlib.md5(f"{metadata.get('report_id', '')}{i}{chunk_text[:100]}".encode()).hexdigest()
            
            chunks.append(DocumentChunk(
                content=chunk_text.strip(),
                metadata={**metadata, "chunk_index": len(chunks), "token_count": len(chunk_tokens)},
                chunk_id=chunk_id
            ))
        
        return chunks

    async def generate_embeddings(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """Generate OpenAI embeddings for chunks"""
        texts = [chunk.content for chunk in chunks]
        
        response = await openai.Embedding.acreate(
            model="text-embedding-3-small",
            input=texts
        )
        
        for i, chunk in enumerate(chunks):
            chunk.embedding = response.data[i].embedding
        
        return chunks

    async def index_report_sections(self, report_id: str, sections: Dict[str, str]) -> int:
        """Index all sections of a report"""
        all_chunks = []
        
        for section_name, content in sections.items():
            if not content.strip():
                continue
                
            metadata = {
                "report_id": report_id,
                "section": section_name,
                "content_type": "report_section"
            }
            
            chunks = await self.chunk_content(content, metadata)
            all_chunks.extend(chunks)
        
        # Generate embeddings in batches
        embedded_chunks = await self.generate_embeddings(all_chunks)
        
        # Store in database
        await self._store_chunks(embedded_chunks)
        
        return len(embedded_chunks)

    async def _store_chunks(self, chunks: List[DocumentChunk]):
        """Store chunks with embeddings in pgvector"""
        query = """
        INSERT INTO document_chunks (chunk_id, content, metadata, embedding, report_id, section)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (chunk_id) DO UPDATE SET
            content = EXCLUDED.content,
            metadata = EXCLUDED.metadata,
            embedding = EXCLUDED.embedding,
            updated_at = NOW()
        """
        
        for chunk in chunks:
            await self.db.execute(
                text(query),
                chunk.chunk_id,
                chunk.content,
                chunk.metadata,
                chunk.embedding,
                chunk.metadata.get("report_id"),
                chunk.metadata.get("section")
            )
        
        await self.db.commit()

    async def semantic_search(self, query: str, report_id: Optional[str] = None, 
                            section: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Perform semantic search using pgvector"""
        # Generate query embedding
        response = await openai.Embedding.acreate(
            model="text-embedding-3-small",
            input=[query]
        )
        query_embedding = response.data[0].embedding
        
        # Build search query with filters
        where_clause = "WHERE 1=1"
        params = [query_embedding, limit]
        param_count = 2
        
        if report_id:
            param_count += 1
            where_clause += f" AND report_id = ${param_count}"
            params.append(report_id)
        
        if section:
            param_count += 1
            where_clause += f" AND section = ${param_count}"
            params.append(section)
        
        search_query = f"""
        SELECT chunk_id, content, metadata, section, report_id,
               1 - (embedding <=> $1::vector) as similarity
        FROM document_chunks
        {where_clause}
        ORDER BY embedding <=> $1::vector
        LIMIT $2
        """
        
        result = await self.db.execute(text(search_query), *params)
        rows = result.fetchall()
        
        return [
            {
                "chunk_id": row.chunk_id,
                "content": row.content,
                "metadata": row.metadata,
                "section": row.section,
                "report_id": row.report_id,
                "similarity": float(row.similarity)
            }
            for row in rows
        ]

    async def delete_report_index(self, report_id: str):
        """Remove all chunks for a specific report"""
        await self.db.execute(
            text("DELETE FROM document_chunks WHERE report_id = $1"),
            report_id
        )
        await self.db.commit()