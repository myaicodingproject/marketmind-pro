"""
Enhanced Report Service - Orchestrates the complete pipeline
Parallel implementation alongside existing system
"""

import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from enhanced_models import (
    EnhancedReport, ReportSection, SectionType, ProcessingStatus,
    SectionPolishRequest, SectionMetadata
)
from database_service import db_service
from polishing_service import polishing_service
from content_parser_service import ContentParserService
from chart_image_service import ChartImageService

# Initialize services
content_parser_service = ContentParserService()
chart_image_service = ChartImageService()

logger = logging.getLogger(__name__)

class EnhancedReportService:
    def __init__(self):
        self.active_reports: Dict[int, EnhancedReport] = {}
    
    async def initialize(self):
        """Initialize all services"""
        await db_service.initialize()
        logger.info("🚀 Enhanced Report Service initialized")
    
    async def create_enhanced_report(self, ticker: str) -> int:
        """Create new enhanced report with full pipeline"""
        title = f"{ticker} - Enhanced Investment Analysis Report"
        report_id = await db_service.create_report(ticker, title)
        
        # Create in-memory report for tracking
        report = EnhancedReport(
            id=report_id,
            ticker=ticker,
            title=title,
            status=ProcessingStatus.PROCESSING
        )
        
        self.active_reports[report_id] = report
        logger.info(f"📝 Created enhanced report {report_id} for {ticker}")
        
        return report_id
    
    async def process_raw_section(
        self, 
        report_id: int, 
        section_type: SectionType, 
        raw_content: str,
        target_pages: int,
        processing_time: int
    ):
        """Process raw section through complete pipeline"""
        try:
            report = self.active_reports.get(report_id)
            if not report:
                logger.error(f"❌ Report {report_id} not found in active reports")
                return
            
            # 1) Parse content into structured ReportSection
            parsed_section = await content_parser_service.parse_section(
                raw_content, section_type, report.ticker
            )
            
            # Create section with parsed data
            section = ReportSection(
                report_id=report_id,
                section_type=section_type,
                status=ProcessingStatus.RAW_COMPLETE,
                raw_content=raw_content,
                parsed_content=parsed_section.content,
                charts=parsed_section.charts,
                metadata=SectionMetadata(
                    word_count=len(raw_content.split()),
                    target_pages=target_pages,
                    processing_time_seconds=processing_time
                )
            )
            
            # 2) Polish text content
            polish_request = SectionPolishRequest(
                section_type=section_type,
                raw_content=parsed_section.content,
                target_pages=target_pages,
                ticker=report.ticker
            )
            
            polish_response = await polishing_service.polish_section(polish_request)
            section.polished_content = polish_response.polished_content
            section.metadata.quality_score = polish_response.quality_score
            
            # 3) Generate chart images for each chart
            chart_images = []
            for chart in section.charts:
                image_data = await chart_image_service.generate_chart_image(chart)
                if image_data:
                    chart_images.append(image_data)
            
            # 4) Store section with structured data, polished content, and chart images
            section_id = await db_service.save_section(
                report_id, 
                section,
                chart_images=chart_images
            )
            section.id = section_id
            
            # Update status and add to in-memory report
            section.status = ProcessingStatus.POLISHED
            report.add_section(section)
            
            logger.info(f"✅ Processed section {section_type.value} with {len(chart_images)} charts")
            
            # Check if all sections are complete
            await self._check_report_completion(report_id)
            
        except Exception as e:
            logger.error(f"❌ Error processing raw section {section_type.value}: {e}")
    
    async def _polish_section(self, report_id: int, section: ReportSection):
        """Polish section using OpenAI and save results"""
        try:
            report = self.active_reports.get(report_id)
            if not report:
                return
            
            # Update status to polishing
            section.status = ProcessingStatus.POLISHING
            await db_service.save_section(report_id, section)
            
            logger.info(f"✨ Starting polishing for {section.section_type.value}")
            
            # Create polish request
            polish_request = SectionPolishRequest(
                section_type=section.section_type,
                raw_content=section.raw_content,
                target_pages=section.metadata.target_pages,
                ticker=report.ticker
            )
            
            # Polish with OpenAI
            polish_response = await polishing_service.polish_section(polish_request)
            
            # Update section with polished content
            section.polished_content = polish_response.polished_content
            section.status = ProcessingStatus.POLISHED
            section.metadata.quality_score = polish_response.quality_score
            section.metadata.polishing_time_seconds = polish_response.processing_time_seconds
            section.metadata.word_count = polish_response.word_count
            section.metadata.updated_at = datetime.now()
            
            # Save polished section
            await db_service.save_section(report_id, section)
            
            # Generate and save embedding for RAG
            if section.polished_content:
                embedding = await polishing_service.generate_embedding(section.polished_content)
                if embedding:
                    await db_service.save_embedding(section.id, embedding)
            
            # Update in-memory report
            report.add_section(section)
            
            logger.info(f"✅ Polished {section.section_type.value} - Quality: {polish_response.quality_score:.2f}")
            
            # Check if all sections are complete
            await self._check_report_completion(report_id)
            
        except Exception as e:
            logger.error(f"❌ Error polishing section {section.section_type.value}: {e}")
            # Mark as failed
            section.status = ProcessingStatus.FAILED
            await db_service.save_section(report_id, section)
    
    async def _check_report_completion(self, report_id: int):
        """Check if report is complete and update status"""
        try:
            report = self.active_reports.get(report_id)
            if not report:
                return
            
            # Check if all sections are polished or failed
            all_sections_done = all(
                section.status in [ProcessingStatus.POLISHED, ProcessingStatus.FAILED]
                for section in report.sections.values()
            )
            
            if all_sections_done:
                # Update report status
                polished_count = sum(
                    1 for section in report.sections.values() 
                    if section.status == ProcessingStatus.POLISHED
                )
                
                if polished_count >= 6:  # At least 6 out of 8 sections polished
                    report.status = ProcessingStatus.POLISHED
                    logger.info(f"🎉 Enhanced report {report_id} completed - {polished_count}/8 sections polished")
                else:
                    report.status = ProcessingStatus.FAILED
                    logger.warning(f"⚠️ Enhanced report {report_id} failed - only {polished_count}/8 sections polished")
                
                # Update statistics
                report.update_statistics()
                
                # Save final report status to database
                # (This would require updating the database service to save report status)
                
        except Exception as e:
            logger.error(f"❌ Error checking report completion: {e}")
    
    async def get_enhanced_report(self, report_id: int) -> Optional[EnhancedReport]:
        """Get enhanced report (from memory or database)"""
        # Try memory first
        if report_id in self.active_reports:
            return self.active_reports[report_id]
        
        # Fallback to database
        return await db_service.get_report(report_id)
    
    async def search_similar_content(self, query: str, limit: int = 5) -> List[Dict]:
        """Search for similar content using RAG"""
        try:
            # Generate embedding for query
            query_embedding = await polishing_service.generate_embedding(query)
            if not query_embedding:
                return []
            
            # Search similar sections
            return await db_service.search_similar_sections(query_embedding, limit)
            
        except Exception as e:
            logger.error(f"❌ Error searching similar content: {e}")
            return []
    
    def get_processing_status(self, report_id: int) -> Dict[str, Any]:
        """Get real-time processing status for frontend"""
        report = self.active_reports.get(report_id)
        if not report:
            return {"status": "not_found"}
        
        sections_status = {}
        for section_type, section in report.sections.items():
            sections_status[section_type.value] = {
                "status": section.status.value,
                "word_count": section.metadata.word_count,
                "quality_score": section.metadata.quality_score,
                "processing_time": section.metadata.processing_time_seconds,
                "polishing_time": section.metadata.polishing_time_seconds
            }
        
        return {
            "report_id": report_id,
            "ticker": report.ticker,
            "status": report.status.value,
            "sections": sections_status,
            "statistics": report.statistics.dict()
        }

# Global enhanced report service
enhanced_service = EnhancedReportService()
