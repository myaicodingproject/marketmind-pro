from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.shared.database.connection import get_db
from app.shared.schemas.schemas import Company, CompanyCreate, User
from app.shared.utils.auth import get_current_user
from app.shared.models.models import Company as CompanyModel

router = APIRouter(prefix="/companies", tags=["companies"])

@router.get("/", response_model=List[Company])
async def get_companies(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all companies"""
    companies = db.query(CompanyModel).offset(skip).limit(limit).all()
    return companies

@router.get("/{ticker}", response_model=Company)
async def get_company_by_ticker(
    ticker: str,
    db: Session = Depends(get_db)
):
    """Get company by ticker symbol"""
    company = db.query(CompanyModel).filter(
        CompanyModel.ticker == ticker.upper()
    ).first()
    
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company not found"
        )
    
    return company

@router.post("/", response_model=Company, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new company (admin only for now)"""
    # Check if company already exists
    existing_company = db.query(CompanyModel).filter(
        CompanyModel.ticker == company_data.ticker.upper()
    ).first()
    
    if existing_company:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Company with this ticker already exists"
        )
    
    company = CompanyModel(
        ticker=company_data.ticker.upper(),
        name=company_data.name,
        sector=company_data.sector,
        industry=company_data.industry,
        market_cap=company_data.market_cap,
        description=company_data.description,
        extra_data=company_data.extra_data
    )
    
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company

@router.get("/search/{query}")
async def search_companies(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Search companies by ticker or name"""
    companies = db.query(CompanyModel).filter(
        (CompanyModel.ticker.ilike(f"%{query.upper()}%")) |
        (CompanyModel.name.ilike(f"%{query}%"))
    ).limit(limit).all()
    
    return companies