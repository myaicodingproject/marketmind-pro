"""
Database Service - PostgreSQL with pgvector for RAG
Parallel implementation alongside existing system
"""

import asyncpg
import json
import logging
import time
from typing import List, Dict, Optional, Any
from datetime import datetime
from models.enhanced_models import EnhancedReport, ReportSection, TableData, ChartData, MetricData

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, connection_string: str = "postgresql://postgres:postgres@localhost:5432/marketmind"):
        self.connection_string = connection_string
        self.pool = None
    
    async def initialize(self):
        """Initialize database connection pool and create tables"""
        try:
            # Try to connect to PostgreSQL
            self.pool = await asyncpg.create_pool(self.connection_string)
            await self.create_tables()
            logger.info("✅ Database service initialized")
        except Exception as e:
            logger.warning(f"⚠️ Database initialization failed: {e}")
            logger.warning("🔄 Running without database - using in-memory storage")
            self.pool = None  # Disable database operations
    
    async def create_tables(self):
        """Create database tables if they don't exist"""
        async with self.pool.acquire() as conn:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
            
            # Reports table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS enhanced_reports (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(10) NOT NULL,
                    title TEXT NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    statistics JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    
                    -- Legacy compatibility
                    html_content TEXT,
                    pdf_content TEXT,
                    pdf_filename VARCHAR(255),
                    chart_data JSONB
                )
            """)
            
            # Report sections table with structured data columns
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS report_sections (
                    id SERIAL PRIMARY KEY,
                    report_id INTEGER REFERENCES enhanced_reports(id) ON DELETE CASCADE,
                    section_type VARCHAR(50) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending',
                    raw_content TEXT,
                    polished_content TEXT,
                    tables_data JSONB DEFAULT '[]',
                    charts_data JSONB DEFAULT '[]',
                    metrics_data JSONB DEFAULT '[]',
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    UNIQUE(report_id, section_type)
                )
            """)
            
            # Chart images table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS chart_images (
                    id SERIAL PRIMARY KEY,
                    report_id INTEGER REFERENCES enhanced_reports(id) ON DELETE CASCADE,
                    section_type VARCHAR(50) NOT NULL,
                    chart_name VARCHAR(100) NOT NULL,
                    image_data TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Section embeddings table for RAG
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS section_embeddings (
                    id SERIAL PRIMARY KEY,
                    section_id INTEGER REFERENCES report_sections(id) ON DELETE CASCADE,
                    embedding vector(1536),  -- OpenAI embedding dimension
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_ticker ON enhanced_reports(ticker)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_sections_report_id ON report_sections(report_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_sections_type ON report_sections(section_type)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_chart_images_report ON chart_images(report_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON section_embeddings USING ivfflat (embedding vector_cosine_ops)")
    
    async def create_report(self, ticker: str, title: str) -> int:
        """Create a new enhanced report"""
        if not self.pool:
            logger.warning("⚠️ Database not available, using fallback ID")
            return int(time.time())  # Use timestamp as fallback ID
            
        async with self.pool.acquire() as conn:
            report_id = await conn.fetchval("""
                INSERT INTO enhanced_reports (ticker, title, status)
                VALUES ($1, $2, 'processing')
                RETURNING id
            """, ticker, title)
            
            logger.info(f"📝 Created enhanced report {report_id} for {ticker}")
            return report_id
    
    async def save_section(self, report_id: int, section_type: str, section: ReportSection, polished_content: str, chart_images: Dict) -> int:
        """Save or update a report section with structured data"""
        if not self.pool:
            logger.warning("⚠️ Database not available, skipping section save")
            return 0
            
        async with self.pool.acquire() as conn:
            # Serialize structured data to JSON
            tables_json = json.dumps([table.dict() for table in section.tables])
            charts_json = json.dumps([chart.dict() for chart in section.charts])
            metrics_json = json.dumps([metric.dict() for metric in section.metrics])
            
            section_id = await conn.fetchval("""
                INSERT INTO report_sections (
                    report_id, section_type, raw_content, polished_content,
                    tables_data, charts_data, metrics_data
                ) VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (report_id, section_type) 
                DO UPDATE SET
                    raw_content = EXCLUDED.raw_content,
                    polished_content = EXCLUDED.polished_content,
                    tables_data = EXCLUDED.tables_data,
                    charts_data = EXCLUDED.charts_data,
                    metrics_data = EXCLUDED.metrics_data,
                    updated_at = NOW()
                RETURNING id
            """, 
            report_id, section_type, section.content, polished_content,
            tables_json, charts_json, metrics_json
            )
            
            # Save chart images
            for chart_name, image_data in chart_images.items():
                await conn.execute("""
                    INSERT INTO chart_images (report_id, section_type, chart_name, image_data)
                    VALUES ($1, $2, $3, $4)
                    ON CONFLICT (report_id, section_type, chart_name)
                    DO UPDATE SET image_data = EXCLUDED.image_data
                """, report_id, section_type, chart_name, image_data)
            
            logger.info(f"💾 Saved section {section_type} for report {report_id}")
            return section_id
    
    async def get_report(self, report_id: int) -> Optional[EnhancedReport]:
        """Get enhanced report with all sections, deserializing JSON data back to Pydantic models"""
        if not self.pool:
            return None
            
        async with self.pool.acquire() as conn:
            # Get report
            report_row = await conn.fetchrow("""
                SELECT * FROM enhanced_reports WHERE id = $1
            """, report_id)
            
            if not report_row:
                return None
            
            # Get sections with structured data
            section_rows = await conn.fetch("""
                SELECT * FROM report_sections WHERE report_id = $1
            """, report_id)
            
            # Get chart images
            chart_rows = await conn.fetch("""
                SELECT section_type, chart_name, image_data 
                FROM chart_images WHERE report_id = $1
            """, report_id)
            
            # Build chart images dict
            chart_images = {}
            for row in chart_rows:
                section_key = f"{row['section_type']}_{row['chart_name']}"
                chart_images[section_key] = row['image_data']
            
            # Build sections dict
            sections = {}
            for section_row in section_rows:
                # Deserialize JSON data back to Pydantic models
                tables = [TableData(**table_data) for table_data in json.loads(section_row['tables_data'] or '[]')]
                charts = [ChartData(**chart_data) for chart_data in json.loads(section_row['charts_data'] or '[]')]
                metrics = [MetricData(**metric_data) for metric_data in json.loads(section_row['metrics_data'] or '[]')]
                
                section = ReportSection(
                    section_type=section_row['section_type'],
                    title=section_row['section_type'].replace('_', ' ').title(),
                    content=section_row['raw_content'] or '',
                    tables=tables,
                    charts=charts,
                    metrics=metrics,
                    raw_content=section_row['raw_content'],
                    polished_content=section_row['polished_content']
                )
                sections[section_row['section_type']] = section
            
            # Build enhanced report
            report = EnhancedReport(
                id=report_row['id'],
                ticker=report_row['ticker'],
                title=report_row['title'],
                sections=sections,
                generated_at=report_row['created_at'],
                chart_images=chart_images
            )
            
            return report
    
    async def save_embedding(self, section_id: int, embedding: List[float]):
        """Save section embedding for RAG"""
        async with self.pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO section_embeddings (section_id, embedding)
                VALUES ($1, $2)
                ON CONFLICT (section_id) 
                DO UPDATE SET embedding = EXCLUDED.embedding
            """, section_id, embedding)
    
    async def search_similar_sections(self, embedding: List[float], limit: int = 5) -> List[Dict]:
        """Search for similar sections using vector similarity"""
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("""
                SELECT 
                    rs.section_type,
                    rs.polished_content,
                    er.ticker,
                    (se.embedding <=> $1) as similarity
                FROM section_embeddings se
                JOIN report_sections rs ON se.section_id = rs.id
                JOIN enhanced_reports er ON rs.report_id = er.id
                WHERE rs.status = 'polished'
                ORDER BY similarity
                LIMIT $2
            """, embedding, limit)
            
            return [dict(row) for row in rows]
    
    async def close(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()

# Global database service instance
db_service = DatabaseService()
