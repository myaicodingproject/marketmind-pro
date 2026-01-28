from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.features.companies.models import Company

router = APIRouter()

@router.get("/search/{ticker}")
async def search_company(ticker: str, db: AsyncSession = Depends(get_db)):
    """Search for company by ticker"""
    result = await db.execute(
        select(Company).where(Company.ticker == ticker.upper())
    )
    company = result.scalar_one_or_none()
    
    if not company:
        return {"ticker": ticker.upper(), "found": False}
    
    return {
        "ticker": company.ticker,
        "name": company.name,
        "sector": company.sector,
        "industry": company.industry,
        "found": True
    }