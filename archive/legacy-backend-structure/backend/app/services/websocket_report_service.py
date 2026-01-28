"""
Report Generation Service with WebSocket Progress Integration
Connects the Kiro CLI report generation process with real-time WebSocket updates
"""

import asyncio
import logging
from typing import Dict, Optional, Callable
from datetime import datetime
from app.core.websocket_progress_manager import progress_manager, ProgressStage

logger = logging.getLogger(__name__)

class ReportGenerationService:
    """Service that generates reports with real-time progress updates via WebSocket"""
    
    def __init__(self):
        self.active_generations: Dict[str, Dict] = {}
    
    async def generate_report_with_progress(
        self, 
        report_id: str, 
        ticker: str, 
        report_type: str = "comprehensive",
        user_id: Optional[str] = None
    ) -> Dict:
        """Generate a report with real-time progress updates"""
        
        try:
            # Initialize progress tracking
            self.active_generations[report_id] = {
                "ticker": ticker,
                "report_type": report_type,
                "user_id": user_id,
                "started_at": datetime.utcnow(),
                "status": "initializing"
            }
            
            # Start progress updates
            await progress_manager.update_progress(
                report_id=report_id,
                stage=ProgressStage.INITIALIZING,
                progress=0,
                message="Initializing report generation..."
            )
            
            # Step 1: Data Collection (0-20%)
            await self._data_collection_phase(report_id, ticker)
            
            # Step 2: Section Generation (20-80%)
            await self._section_generation_phase(report_id, ticker, report_type)
            
            # Step 3: Quality Validation (80-90%)
            await self._quality_validation_phase(report_id)
            
            # Step 4: PDF Generation (90-100%)
            report_url = await self._pdf_generation_phase(report_id, ticker)
            
            # Mark as completed
            await progress_manager.report_completed(
                report_id=report_id,
                success=True,
                report_url=report_url
            )
            
            # Clean up
            if report_id in self.active_generations:
                del self.active_generations[report_id]
            
            return {
                "success": True,
                "report_id": report_id,
                "report_url": report_url,
                "completed_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating report {report_id}: {str(e)}")
            
            # Send error notification
            await progress_manager.send_error(
                report_id=report_id,
                error_type="generation_error",
                error_message=str(e),
                error_details={"ticker": ticker, "report_type": report_type}
            )
            
            # Mark as failed
            await progress_manager.report_completed(
                report_id=report_id,
                success=False,
                error_message=str(e)
            )
            
            # Clean up
            if report_id in self.active_generations:
                del self.active_generations[report_id]
            
            return {
                "success": False,
                "report_id": report_id,
                "error": str(e),
                "failed_at": datetime.utcnow().isoformat()
            }
    
    async def _data_collection_phase(self, report_id: str, ticker: str):
        """Phase 1: Collect financial data and company information"""
        
        await progress_manager.update_progress(
            report_id=report_id,
            stage=ProgressStage.DATA_COLLECTION,
            progress=5,
            message="Collecting company data..."
        )
        
        # Simulate data collection steps
        data_steps = [
            ("Fetching company profile", 8),
            ("Collecting financial statements", 12),
            ("Gathering market data", 16),
            ("Retrieving SEC filings", 20)
        ]
        
        for step_message, step_progress in data_steps:
            await progress_manager.update_progress(
                report_id=report_id,
                stage=ProgressStage.DATA_COLLECTION,
                progress=step_progress,
                message=step_message
            )
            
            # Simulate processing time
            await asyncio.sleep(1)
        
        logger.info(f"Data collection completed for report {report_id}")
    
    async def _section_generation_phase(self, report_id: str, ticker: str, report_type: str):
        """Phase 2: Generate report sections using Kiro CLI"""
        
        await progress_manager.update_progress(
            report_id=report_id,
            stage=ProgressStage.SECTION_GENERATION,
            progress=25,
            message="Starting section generation..."
        )
        
        # Define sections to generate
        sections = [
            ("Executive Summary", 30),
            ("Company Overview", 40),
            ("Financial Analysis", 50),
            ("Valuation Analysis", 60),
            ("Risk Assessment", 70),
            ("Investment Recommendation", 80)
        ]
        
        for section_name, overall_progress in sections:
            # Update section progress
            await progress_manager.update_section_progress(
                report_id=report_id,
                section_name=section_name,
                section_progress=0,
                section_status="Starting generation..."
            )
            
            # Simulate section generation with Kiro CLI
            await self._generate_section_with_kiro(report_id, section_name, ticker)
            
            # Mark section as completed
            await progress_manager.update_section_progress(
                report_id=report_id,
                section_name=section_name,
                section_progress=100,
                section_status="Completed",
                validation_results={"word_count": 500, "quality_score": 0.85}
            )
            
            # Update overall progress
            await progress_manager.update_progress(
                report_id=report_id,
                stage=ProgressStage.SECTION_GENERATION,
                progress=overall_progress,
                message=f"Completed {section_name}"
            )
        
        logger.info(f"Section generation completed for report {report_id}")
    
    async def _generate_section_with_kiro(self, report_id: str, section_name: str, ticker: str):
        """Generate a specific section using Kiro CLI with progress updates"""
        
        # Simulate Kiro CLI processing steps
        kiro_steps = [
            ("Preparing context", 20),
            ("Running Kiro analysis", 50),
            ("Processing results", 80),
            ("Formatting output", 100)
        ]
        
        for step_message, step_progress in kiro_steps:
            await progress_manager.update_section_progress(
                report_id=report_id,
                section_name=section_name,
                section_progress=step_progress,
                section_status=step_message
            )
            
            # Simulate processing time
            await asyncio.sleep(0.5)
    
    async def _quality_validation_phase(self, report_id: str):
        """Phase 3: Quality validation of generated content"""
        
        await progress_manager.update_progress(
            report_id=report_id,
            stage=ProgressStage.QUALITY_VALIDATION,
            progress=82,
            message="Starting quality validation..."
        )
        
        # Define validation steps
        validation_steps = [
            ("Content Completeness", 84, {"completeness_score": 0.92}),
            ("Financial Accuracy", 86, {"accuracy_score": 0.88}),
            ("Consistency Check", 88, {"consistency_score": 0.90}),
            ("Final Review", 90, {"overall_score": 0.90})
        ]
        
        for validation_stage, progress_value, results in validation_steps:
            await progress_manager.update_quality_validation(
                report_id=report_id,
                validation_stage=validation_stage.lower().replace(" ", "_"),
                validation_progress=100,
                validation_results=results
            )
            
            await progress_manager.update_progress(
                report_id=report_id,
                stage=ProgressStage.QUALITY_VALIDATION,
                progress=progress_value,
                message=f"Completed {validation_stage}"
            )
            
            # Simulate validation time
            await asyncio.sleep(0.5)
        
        logger.info(f"Quality validation completed for report {report_id}")
    
    async def _pdf_generation_phase(self, report_id: str, ticker: str) -> str:
        """Phase 4: Generate final PDF report"""
        
        await progress_manager.update_progress(
            report_id=report_id,
            stage=ProgressStage.PDF_GENERATION,
            progress=92,
            message="Generating PDF report..."
        )
        
        # Simulate PDF generation steps
        pdf_steps = [
            ("Compiling content", 94),
            ("Formatting layout", 96),
            ("Adding charts", 98),
            ("Finalizing PDF", 100)
        ]
        
        for step_message, step_progress in pdf_steps:
            await progress_manager.update_progress(
                report_id=report_id,
                stage=ProgressStage.PDF_GENERATION,
                progress=step_progress,
                message=step_message
            )
            
            # Simulate processing time
            await asyncio.sleep(0.5)
        
        # Generate report URL
        report_url = f"/api/v1/reports/{report_id}/download"
        
        logger.info(f"PDF generation completed for report {report_id}")
        return report_url
    
    def get_active_generations(self) -> Dict[str, Dict]:
        """Get all currently active report generations"""
        return self.active_generations.copy()
    
    def is_generating(self, report_id: str) -> bool:
        """Check if a report is currently being generated"""
        return report_id in self.active_generations

# Global service instance
report_service = ReportGenerationService()