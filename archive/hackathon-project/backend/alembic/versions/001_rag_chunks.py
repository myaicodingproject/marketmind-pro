"""RAG document chunks table with pgvector support

Revision ID: rag_chunks_001
Revises: base
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers
revision = 'rag_chunks_001'
down_revision = 'base'
branch_labels = None
depends_on = None

def upgrade():
    # Enable pgvector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create document_chunks table
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('chunk_id', sa.String(64), unique=True, nullable=False, index=True),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('metadata', JSONB, nullable=False, default={}),
        sa.Column('embedding', sa.Text, nullable=False),  # vector(1536) for OpenAI embeddings
        sa.Column('report_id', sa.String(50), nullable=False, index=True),
        sa.Column('section', sa.String(100), nullable=False, index=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    
    # Add vector column after table creation
    op.execute('ALTER TABLE document_chunks ALTER COLUMN embedding TYPE vector(1536) USING embedding::vector(1536)')
    
    # Create indexes for efficient similarity search
    op.execute('CREATE INDEX idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)')
    op.create_index('idx_document_chunks_report_section', 'document_chunks', ['report_id', 'section'])
    op.create_index('idx_document_chunks_metadata', 'document_chunks', ['metadata'], postgresql_using='gin')

def downgrade():
    op.drop_table('document_chunks')
    op.execute('DROP EXTENSION IF EXISTS vector')