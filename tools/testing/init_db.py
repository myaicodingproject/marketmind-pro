"""
Database initialization script for MarketMind Pro
Creates necessary tables including users table
"""
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
from app.core.database import Base
from app.features.auth.models import User
from app.features.reports.models import Report
from app.features.companies.models import Company

async def init_database():
    """Initialize database with all tables"""
    engine = create_async_engine(settings.DATABASE_URL)
    
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    
    await engine.dispose()
    print("Database initialized successfully!")

if __name__ == "__main__":
    asyncio.run(init_database())