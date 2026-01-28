from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.shared.models.models import Report, Company, User
from app.shared.schemas.schemas import ReportCreate
from app.core.queue_manager import queue_manager, QueuePriority
from app.services.kiro_process_service import kiro_process_service
from .kiro_integration import KiroReportGenerator
from .structure import ReportVersioning
from typing import List, Dict, Any
import asyncio
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportsService:
    def __init__(self, db: Session):
        self.db = db
        self.kiro_generator = KiroReportGenerator()
    
    def get_or_create_company(self, ticker: str) -> Company:
        """Get existing company or create new one"""
        company = self.db.query(Company).filter(Company.ticker == ticker.upper()).first()
        if not company:
            company = Company(
                ticker=ticker.upper(),
                name=f"{ticker.upper()} Corporation",  # Placeholder
                sector="Unknown",
                industry="Unknown"
            )
            self.db.add(company)
            self.db.commit()
            self.db.refresh(company)
        return company
    
    def create_report(self, report_data: ReportCreate, user: User) -> Report:
        """Create a new report with professional structure"""
        company = self.get_or_create_company(report_data.ticker)
        
        # Create metadata using new versioning system
        metadata = ReportVersioning.create_metadata(
            ticker=company.ticker,
            company_name=company.name,
            report_type=report_data.report_type
        )
        
        report = Report(
            user_id=user.id,
            company_id=company.id,
            title=f"{company.ticker} - Comprehensive Analysis Report",
            status="pending",
            report_type=report_data.report_type,
            progress=0,
            content={"metadata": metadata.__dict__}  # Store initial metadata
        )
        
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report
    
    async def queue_report_generation(self, report_id: int, priority: str = "normal") -> Dict[str, Any]:
        """Queue report generation using the new queue system"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        try:
            # Map priority string to enum
            priority_map = {
                "low": QueuePriority.LOW,
                "normal": QueuePriority.NORMAL,
                "high": QueuePriority.HIGH,
                "urgent": QueuePriority.URGENT
            }
            queue_priority = priority_map.get(priority.lower(), QueuePriority.NORMAL)
            
            # Submit to queue
            request_id = await queue_manager.submit_request(
                user_id=str(report.user_id),
                ticker=report.company.ticker,
                request_type="comprehensive_report",
                priority=queue_priority,
                estimated_duration=300,  # 5 minutes
                callback=self._report_completion_callback
            )
            
            # Update report with request ID
            report.status = "queued"
            report.progress = 5
            report.external_id = request_id  # Store queue request ID
            self.db.commit()
            
            logger.info(f"Queued report generation for report_id {report_id} with request_id {request_id}")
            
            return {
                "report_id": report_id,
                "request_id": request_id,
                "status": "queued",
                "message": "Report generation has been queued"
            }
            
        except Exception as e:
            report.status = "failed"
            report.error_message = str(e)
            self.db.commit()
            logger.error(f"Error queuing report {report_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to queue report generation: {str(e)}"
            )
    
    async def generate_report_content_direct(self, report_id: int) -> Dict[str, Any]:
        """Generate report content directly using new comprehensive system"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        try:
            # Update status to processing
            report.status = "processing"
            report.progress = 10
            self.db.commit()
            
            company = report.company
            ticker = company.ticker
            
            # Prepare comprehensive company data
            company_data = {
                "ticker": ticker,
                "company_name": company.name,
                "sector": company.sector or "Technology",
                "industry": company.industry or "Software",
                "market_cap": getattr(company, 'market_cap', None) or "Unknown",
                "description": getattr(company, 'description', None) or f"{company.name} is a leading company in the {company.sector or 'technology'} sector.",
                "business_description": f"Comprehensive business analysis for {company.name}",
                "recent_news": "Latest market developments and company updates",
                "financial_statements": "Historical financial performance data",
                "historical_data": "Multi-year performance trends",
                "peer_data": "Industry peer comparison data",
                "industry_averages": "Sector benchmark metrics",
                "quarterly_results": "Recent quarterly earnings data",
                "guidance": "Management outlook and guidance"
            }
            
            report.progress = 30
            self.db.commit()
            
            # Generate comprehensive report using new system
            logger.info(f"Generating comprehensive report for {ticker} using new system")
            report_content = await self.kiro_generator.generate_comprehensive_report(ticker, company_data)
            
            report.progress = 90
            self.db.commit()
            
            # Update report with structured content
            report.content = report_content
            report.status = "completed"
            report.progress = 100
            self.db.commit()
            
            logger.info(f"Successfully generated comprehensive report for {ticker} (report_id: {report_id})")
            return report_content
            
        except Exception as e:
            report.status = "failed"
            report.error_message = str(e)
            self.db.commit()
            logger.error(f"Comprehensive report generation failed for {ticker} (report_id: {report_id}): {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Report generation failed: {str(e)}"
            )
    
    async def _report_completion_callback(self, queue_request):
        """Callback function for when queued report completes"""
        try:
            # Find the report by external_id (request_id)
            report = self.db.query(Report).filter(Report.external_id == queue_request.request_id).first()
            
            if not report:
                logger.error(f"Could not find report for request_id {queue_request.request_id}")
                return
                
            if queue_request.status.value == "completed" and queue_request.result:
                # Update report with results
                report_content = {
                    "sections": queue_request.result,
                    "metadata": {
                        "ticker": queue_request.ticker,
                        "generated_at": datetime.now().isoformat(),
                        "report_type": report.report_type,
                        "generation_method": "queued",
                        "processing_time": queue_request.actual_duration
                    }
                }
                
                report.content = report_content
                report.status = "completed"
                report.progress = 100
                
            elif queue_request.status.value == "failed":
                report.status = "failed"
                report.error_message = queue_request.error or "Report generation failed"
                
            elif queue_request.status.value == "cancelled":
                report.status = "cancelled"
                
            self.db.commit()
            logger.info(f"Updated report {report.id} with queue completion status: {queue_request.status.value}")
            
        except Exception as e:
            logger.error(f"Error in report completion callback: {e}")
    
    async def get_report_queue_status(self, report_id: int) -> Dict[str, Any]:
        """Get queue status for a report"""
        report = self.db.query(Report).filter(Report.id == report_id).first()
        if not report or not report.external_id:
            return {"status": "not_queued"}
            
        try:
            queue_status = await queue_manager.get_request_status(report.external_id)
            return queue_status or {"status": "not_found"}
        except Exception as e:
            logger.error(f"Error getting queue status for report {report_id}: {e}")
            return {"status": "error", "error": str(e)}
    
    async def cancel_report_generation(self, report_id: int, user: User) -> bool:
        """Cancel queued report generation"""
        report = self.get_report_by_id(report_id, user)
        
        if not report.external_id:
            return False
            
        try:
            success = await queue_manager.cancel_request(report.external_id, str(user.id))
            
            if success:
                report.status = "cancelled"
                self.db.commit()
                
            return success
            
        except Exception as e:
            logger.error(f"Error cancelling report {report_id}: {e}")
            return False
    
    def get_user_reports(self, user: User, skip: int = 0, limit: int = 100) -> List[Report]:
        """Get reports for a user"""
        return self.db.query(Report).filter(
            Report.user_id == user.id
        ).offset(skip).limit(limit).all()
    
    def get_report_by_id(self, report_id: int, user: User) -> Report:
        """Get specific report by ID"""
        report = self.db.query(Report).filter(
            Report.id == report_id,
            Report.user_id == user.id
        ).first()
        
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        
        return report
    
    def delete_report(self, report_id: int, user: User) -> bool:
        """Delete a report"""
        report = self.get_report_by_id(report_id, user)
        self.db.delete(report)
        self.db.commit()
        return True
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """Get service performance metrics"""
        try:
            return await kiro_process_service.get_service_metrics()
        except Exception as e:
            logger.error(f"Error getting service metrics: {e}")
            return {"error": str(e)}
    
    async def generate_pdf_report(self, report_id: int, user: User) -> str:
        """Generate PDF version of report"""
        report = self.get_report_by_id(report_id, user)
        
        if not report.content or report.status != "completed":
            raise HTTPException(
                status_code=400,
                detail="Report must be completed before PDF generation"
            )
        
        try:
            pdf_path = await self.kiro_generator.generate_pdf_report(
                report_data=report.content,
                ticker=report.company.ticker
            )
            
            # Update report with PDF path
            report.file_path = pdf_path
            self.db.commit()
            
            logger.info(f"Generated PDF for report {report_id}: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed for report {report_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"PDF generation failed: {str(e)}"
            )
    
    async def customize_report_template(self, report_id: int, customizations: Dict[str, Any], user: User) -> Dict[str, Any]:
        """Apply customizations to report template"""
        report = self.get_report_by_id(report_id, user)
        
        try:
            from .pdf_generator import ReportCustomization
            
            if report.content:
                customized_content = ReportCustomization.customize_template(
                    template_data=report.content,
                    customizations=customizations
                )
                
                # Update report with customized content
                report.content = customized_content
                self.db.commit()
                
                logger.info(f"Applied customizations to report {report_id}")
                return customized_content
            else:
                raise HTTPException(status_code=400, detail="Report has no content to customize")
                
        except Exception as e:
            logger.error(f"Report customization failed for report {report_id}: {e}")
            raise HTTPException(
                status_code=500,
                detail=f"Report customization failed: {str(e)}"
            )
    
    def get_available_customizations(self) -> Dict[str, Any]:
        """Get available report customization options"""
        from .pdf_generator import ReportCustomization
        return ReportCustomization.get_available_customizations()
    
    async def get_report_structure_info(self) -> Dict[str, Any]:
        """Get information about report structure and sections"""
        from .structure import ReportStructure
        
        structure = ReportStructure()
        sections = structure.get_comprehensive_structure()
        
        return {
            "total_pages": structure.get_total_pages(),
            "sections_count": len(sections),
            "sections": [
                {
                    "id": section.id,
                    "title": section.title,
                    "order": section.order,
                    "pages": section.pages,
                    "required": section.required,
                    "template": section.template
                }
                for section in sections
            ]
        }