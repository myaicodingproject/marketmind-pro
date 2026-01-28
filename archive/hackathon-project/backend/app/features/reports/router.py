from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.core.database import get_db
from app.features.reports.schemas import ReportRequest, ReportResponse, ReportDetail
from app.features.reports.service import ReportService
from app.features.reports.models import Report
from app.features.companies.models import Company

router = APIRouter()

@router.post("/generate", response_model=ReportResponse)
async def generate_report(
    request: ReportRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Generate a new stock analysis report"""
    # TODO: Add authentication dependency
    user_id = 1  # Placeholder
    
    # Create report
    report = await ReportService.create_report(db, user_id, request)
    
    # Start background generation
    background_tasks.add_task(ReportService.generate_report_content, db, report.id)
    
    # Get company name for response
    result = await db.execute(select(Company).where(Company.id == report.company_id))
    company = result.scalar_one()
    
    return ReportResponse(
        id=report.id,
        ticker=company.ticker,
        company_name=company.name,
        status=report.status,
        report_type=report.report_type,
        created_at=report.created_at,
        completed_at=report.completed_at,
        generation_time_seconds=report.generation_time_seconds
    )

@router.get("/{report_id}", response_model=ReportDetail)
async def get_report(report_id: int, db: AsyncSession = Depends(get_db)):
    """Get detailed report by ID"""
    result = await db.execute(
        select(Report, Company)
        .join(Company)
        .where(Report.id == report_id)
    )
    report_data = result.first()
    
    if not report_data:
        raise HTTPException(status_code=404, detail="Report not found")
    
    report, company = report_data
    
    return ReportDetail(
        id=report.id,
        ticker=company.ticker,
        company_name=company.name,
        status=report.status,
        report_type=report.report_type,
        created_at=report.created_at,
        completed_at=report.completed_at,
        generation_time_seconds=report.generation_time_seconds,
        executive_summary=report.executive_summary,
        company_analysis=report.company_analysis,
        financial_analysis=report.financial_analysis,
        valuation_analysis=report.valuation_analysis,
        risk_analysis=report.risk_analysis,
        error_message=report.error_message
    )

@router.get("/", response_model=List[ReportResponse])
async def list_reports(db: AsyncSession = Depends(get_db)):
    """List all reports for user"""
    # TODO: Add authentication and filter by user_id
    result = await db.execute(
        select(Report, Company)
        .join(Company)
        .order_by(Report.created_at.desc())
    )
    
    reports = []
    for report, company in result.all():
        reports.append(ReportResponse(
            id=report.id,
            ticker=company.ticker,
            company_name=company.name,
            status=report.status,
            report_type=report.report_type,
            created_at=report.created_at,
            completed_at=report.completed_at,
            generation_time_seconds=report.generation_time_seconds
        ))
    
    return reports