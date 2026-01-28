#!/usr/bin/env python3
"""
TRACK B1: PostgreSQL + pgvector Schema Setup
Database schema for reports, sections, and RAG embeddings
"""

import asyncio
import asyncpg
import json
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class MarketMindDatabase:
    def __init__(self, connection_string: str = "postgresql://localhost/marketmind_pro"):
        self.connection_string = connection_string
        
    async def initialize_schema(self):
        """Initialize complete database schema with pgvector support"""
        
        conn = await asyncpg.connect(self.connection_string)
        
        try:
            # Enable pgvector extension
            await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Reports table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(100) UNIQUE NOT NULL,
                    ticker VARCHAR(10) NOT NULL,
                    title TEXT NOT NULL,
                    generation_method VARCHAR(50) NOT NULL,
                    generation_time FLOAT,
                    success_rate FLOAT,
                    overall_quality_score FLOAT,
                    quality_passed BOOLEAN,
                    pdf_filename TEXT,
                    statistics JSONB,
                    metadata JSONB,
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Report sections table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS report_sections (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(100) REFERENCES reports(report_id),
                    section_name VARCHAR(50) NOT NULL,
                    section_key VARCHAR(20) NOT NULL,
                    analysis TEXT NOT NULL,
                    key_insights JSONB,
                    metrics JSONB,
                    charts JSONB,
                    tables JSONB,
                    recommendations JSONB,
                    generated_by VARCHAR(50),
                    quality_score FLOAT,
                    word_count INTEGER,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Financial data table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS financial_data (
                    id SERIAL PRIMARY KEY,
                    ticker VARCHAR(10) NOT NULL,
                    data_type VARCHAR(50) NOT NULL,
                    data_source VARCHAR(50) NOT NULL,
                    raw_data JSONB NOT NULL,
                    processed_data JSONB,
                    fetched_at TIMESTAMP DEFAULT NOW(),
                    expires_at TIMESTAMP,
                    UNIQUE(ticker, data_type, data_source)
                );
            """)
            
            # RAG embeddings table with pgvector
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS rag_embeddings (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(100) REFERENCES reports(report_id),
                    section_name VARCHAR(50),
                    content_type VARCHAR(30) NOT NULL,
                    content_text TEXT NOT NULL,
                    content_metadata JSONB,
                    embedding vector(1536),
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Quality audit logs
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS quality_audits (
                    id SERIAL PRIMARY KEY,
                    report_id VARCHAR(100) REFERENCES reports(report_id),
                    section_name VARCHAR(50),
                    audit_type VARCHAR(30) NOT NULL,
                    quality_score FLOAT NOT NULL,
                    quality_details JSONB,
                    passed BOOLEAN NOT NULL,
                    audited_by VARCHAR(50),
                    audited_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Create indexes for performance
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_ticker ON reports(ticker);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_reports_created_at ON reports(created_at);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_sections_report_id ON report_sections(report_id);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_financial_ticker ON financial_data(ticker);")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_report_id ON rag_embeddings(report_id);")
            
            # Create vector similarity index
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_embeddings_vector ON rag_embeddings USING ivfflat (embedding vector_cosine_ops);")
            
            logger.info("✅ Database schema initialized successfully")
            
        finally:
            await conn.close()

    async def store_report(self, report_data: dict) -> str:
        """Store complete report with sections"""
        
        conn = await asyncpg.connect(self.connection_string)
        
        try:
            async with conn.transaction():
                # Insert main report
                report_id = await conn.fetchval("""
                    INSERT INTO reports (
                        report_id, ticker, title, generation_method, generation_time,
                        success_rate, overall_quality_score, quality_passed, 
                        pdf_filename, statistics, metadata
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                    RETURNING report_id
                """, 
                    report_data['report_id'],
                    report_data['ticker'],
                    report_data['title'],
                    report_data['generation_method'],
                    report_data.get('generation_time'),
                    report_data.get('success_rate'),
                    report_data.get('overall_quality_score'),
                    report_data.get('quality_passed'),
                    report_data.get('pdf_filename'),
                    json.dumps(report_data.get('statistics', {})),
                    json.dumps(report_data.get('metadata', {}))
                )
                
                # Insert sections
                sections = report_data.get('sections', {})
                for section_key, section_data in sections.items():
                    await conn.execute("""
                        INSERT INTO report_sections (
                            report_id, section_name, section_key, analysis,
                            key_insights, metrics, charts, tables, recommendations,
                            generated_by, quality_score, word_count
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
                    """,
                        report_id,
                        section_data.get('section_name'),
                        section_key,
                        section_data.get('analysis'),
                        json.dumps(section_data.get('key_insights', [])),
                        json.dumps(section_data.get('metrics', {})),
                        json.dumps(section_data.get('charts', [])),
                        json.dumps(section_data.get('tables', [])),
                        json.dumps(section_data.get('recommendations', [])),
                        section_data.get('generated_by'),
                        section_data.get('quality_score'),
                        len(section_data.get('analysis', '').split())
                    )
                
                logger.info(f"✅ Report {report_id} stored successfully")
                return report_id
                
        finally:
            await conn.close()

    async def get_report(self, report_id: str) -> dict:
        """Retrieve complete report with sections"""
        
        conn = await asyncpg.connect(self.connection_string)
        
        try:
            # Get main report
            report_row = await conn.fetchrow("""
                SELECT * FROM reports WHERE report_id = $1
            """, report_id)
            
            if not report_row:
                return None
            
            # Get sections
            section_rows = await conn.fetch("""
                SELECT * FROM report_sections WHERE report_id = $1
                ORDER BY section_key
            """, report_id)
            
            # Reconstruct report
            report = dict(report_row)
            report['sections'] = {}
            
            for section_row in section_rows:
                section_data = dict(section_row)
                section_key = section_data.pop('section_key')
                report['sections'][section_key] = section_data
            
            return report
            
        finally:
            await conn.close()

    async def store_financial_data(self, ticker: str, data_type: str, source: str, data: dict):
        """Store financial data with expiration"""
        
        conn = await asyncpg.connect(self.connection_string)
        
        try:
            await conn.execute("""
                INSERT INTO financial_data (ticker, data_type, data_source, raw_data, expires_at)
                VALUES ($1, $2, $3, $4, NOW() + INTERVAL '15 minutes')
                ON CONFLICT (ticker, data_type, data_source)
                DO UPDATE SET raw_data = $4, fetched_at = NOW(), expires_at = NOW() + INTERVAL '15 minutes'
            """, ticker, data_type, source, json.dumps(data))
            
        finally:
            await conn.close()

# Test database setup
if __name__ == "__main__":
    async def test_database():
        db = MarketMindDatabase()
        await db.initialize_schema()
        print("✅ Database schema created successfully")
    
    asyncio.run(test_database())
