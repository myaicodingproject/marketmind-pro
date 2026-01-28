from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
import logging

from app.features.reports.models import Report, ReportStatus
from app.features.companies.models import Company
from app.features.reports.schemas import ReportRequest
from app.services.kiro_service import KiroService

logger = logging.getLogger(__name__)

class ReportService:
    @staticmethod
    async def create_report(db: AsyncSession, user_id: int, request: ReportRequest) -> Report:
        """Create a new report and initiate generation"""
        
        # Get or create company
        company = await ReportService._get_or_create_company(db, request.ticker)
        
        # Create report record
        report = Report(
            user_id=user_id,
            company_id=company.id,
            report_type=request.report_type,
            status=ReportStatus.PENDING
        )
        
        db.add(report)
        await db.commit()
        await db.refresh(report)
        
        return report
    
    @staticmethod
    async def generate_report_content(db: AsyncSession, report_id: int):
        """Generate report content using Kiro CLI"""
        
        # Get report
        result = await db.execute(
            select(Report).where(Report.id == report_id)
        )
        report = result.scalar_one_or_none()
        if not report:
            raise ValueError(f"Report {report_id} not found")
        
        # Get company info
        result = await db.execute(
            select(Company).where(Company.id == report.company_id)
        )
        company = result.scalar_one()
        
        try:
            # Update status
            report.status = ReportStatus.GENERATING
            await db.commit()
            
            start_time = datetime.utcnow()
            
            # Generate analysis using Kiro CLI
            logger.info(f"Starting Kiro analysis for {company.ticker}")
            analysis_results = await KiroService.generate_comprehensive_analysis(company.ticker)
            
            # Update report with results
            report.executive_summary = analysis_results.get("executive_summary", {}).get("content", "")
            report.company_analysis = analysis_results.get("company_overview", {}).get("content", "")
            report.financial_analysis = analysis_results.get("financial_analysis", {}).get("content", "")
            report.valuation_analysis = analysis_results.get("valuation_dcf", {}).get("content", "")
            report.risk_analysis = analysis_results.get("risk_assessment", {}).get("content", "")
            
            # Update metadata
            end_time = datetime.utcnow()
            report.generation_time_seconds = int((end_time - start_time).total_seconds())
            report.completed_at = end_time
            report.status = ReportStatus.COMPLETED
            report.kiro_prompts_used = list(analysis_results.keys())
            
            await db.commit()
            logger.info(f"Report {report_id} completed successfully")
            
        except Exception as e:
            logger.error(f"Report generation failed for {report_id}: {str(e)}")
            report.status = ReportStatus.FAILED
            report.error_message = str(e)
            await db.commit()
            raise
    
    @staticmethod
    async def _get_or_create_company(db: AsyncSession, ticker: str) -> Company:
        """Get existing company or create new one"""
        result = await db.execute(
            select(Company).where(Company.ticker == ticker.upper())
        )
        company = result.scalar_one_or_none()
        
        if not company:
            company = Company(
                ticker=ticker.upper(),
                name=f"{ticker.upper()} Company"  # Will be updated by Kiro analysis
            )
            db.add(company)
            await db.commit()
            await db.refresh(company)
        
        return company