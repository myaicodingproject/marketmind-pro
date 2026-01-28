"""
Enhanced PDF Generator - Phase 2 Integration Layer
Combines Kiro CLI report generation with OpenAI enhancement for hybrid system
"""

import json
import asyncio
from typing import Dict, Any, Optional
from pathlib import Path
import logging
from datetime import datetime

from professional_pdf_generator import generate_professional_pdf, ContentCleaner

logger = logging.getLogger(__name__)

class EnhancedPDFGenerator:
    """Hybrid PDF generator combining Kiro CLI with OpenAI enhancement"""
    
    def __init__(self):
        self.content_cleaner = ContentCleaner()
        
    async def generate_hybrid_report(
        self,
        symbol: str,
        enhancement_level: str = "standard",
        include_charts: bool = True
    ) -> Dict[str, Any]:
        """Generate enhanced PDF report using hybrid approach"""
        
        try:
            logger.info(f"Starting hybrid report generation for {symbol}")
            
            # Step 1: Generate base report with Kiro CLI
            kiro_report = await self._generate_kiro_base_report(symbol)
            
            # Step 2: Enhance content with OpenAI if requested
            if enhancement_level != "kiro_only":
                enhanced_report = await self._enhance_with_openai(
                    kiro_report, enhancement_level
                )
            else:
                enhanced_report = kiro_report
            
            # Step 3: Generate professional PDF
            pdf_path = await self._generate_pdf(enhanced_report, symbol, include_charts)
            
            # Step 4: Quality validation
            quality_score = await self._validate_quality(enhanced_report)
            
            return {
                "success": True,
                "pdf_path": pdf_path,
                "quality_score": quality_score,
                "enhancement_level": enhancement_level,
                "generation_time": datetime.now().isoformat(),
                "symbol": symbol
            }
            
        except Exception as e:
            logger.error(f"Hybrid report generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "symbol": symbol
            }
    
    async def _generate_kiro_base_report(self, symbol: str) -> Dict[str, Any]:
        """Generate base report using Kiro CLI agents"""
        
        # For Phase 2 integration, use mock data structure
        # In production, this would call the actual Kiro service
        mock_sections = {
            "executive_summary": {
                "content": f"Executive Summary for {symbol}: This is a comprehensive analysis of {symbol} stock...",
                "title": "Executive Summary"
            },
            "company_analysis": {
                "content": f"Company Analysis for {symbol}: Deep dive into business model and operations...",
                "title": "Company Analysis"
            },
            "financial_analysis": {
                "content": f"Financial Analysis for {symbol}: Revenue, profitability, and growth metrics...",
                "title": "Financial Analysis"
            },
            "valuation": {
                "content": f"Valuation Analysis for {symbol}: DCF model and peer comparison...",
                "title": "Valuation"
            },
            "risk_assessment": {
                "content": f"Risk Assessment for {symbol}: Key risks and mitigation strategies...",
                "title": "Risk Assessment"
            }
        }
        
        return {
            "symbol": symbol,
            "sections": mock_sections,
            "generation_method": "kiro_cli_mock",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _enhance_with_openai(
        self, 
        base_report: Dict[str, Any], 
        enhancement_level: str
    ) -> Dict[str, Any]:
        """Enhance Kiro report with OpenAI processing"""
        
        enhanced_sections = {}
        
        for section_name, section_data in base_report["sections"].items():
            if "error" in section_data:
                enhanced_sections[section_name] = section_data
                continue
                
            try:
                # Clean and enhance content
                cleaned_content = self.content_cleaner.clean_content(
                    section_data.get("content", "")
                )
                
                if enhancement_level == "premium":
                    enhanced_content = await self._premium_enhancement(
                        cleaned_content, section_name
                    )
                else:
                    enhanced_content = await self._standard_enhancement(
                        cleaned_content, section_name
                    )
                
                enhanced_sections[section_name] = {
                    **section_data,
                    "content": enhanced_content,
                    "enhanced": True
                }
                
            except Exception as e:
                logger.warning(f"Enhancement failed for {section_name}: {e}")
                enhanced_sections[section_name] = section_data
        
        return {
            **base_report,
            "sections": enhanced_sections,
            "enhancement_level": enhancement_level
        }
    
    async def _standard_enhancement(self, content: str, section_name: str) -> str:
        """Apply standard OpenAI enhancement"""
        # Placeholder for OpenAI enhancement logic
        # In production, this would call OpenAI API for content improvement
        return content
    
    async def _premium_enhancement(self, content: str, section_name: str) -> str:
        """Apply premium OpenAI enhancement with advanced features"""
        # Placeholder for premium enhancement logic
        return content
    
    async def _generate_pdf(
        self, 
        report_data: Dict[str, Any], 
        symbol: str,
        include_charts: bool
    ) -> str:
        """Generate professional PDF from enhanced report data"""
        
        try:
            # Ensure reports directory exists
            reports_dir = Path("reports")
            reports_dir.mkdir(exist_ok=True)
            
            # Convert to format expected by professional_pdf_generator
            formatted_data = self._format_for_pdf_generator(report_data)
            
            # Generate output path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = reports_dir / f"MarketMind_Hybrid_{symbol}_{timestamp}.pdf"
            
            # Generate PDF using existing professional generator
            pdf_path = generate_professional_pdf(
                symbol,
                formatted_data,
                output_path=str(output_path)
            )
            
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def _format_for_pdf_generator(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format enhanced report data for PDF generator"""
        
        sections = report_data.get("sections", {})
        
        # Format sections according to professional PDF generator expectations
        formatted_sections = {}
        
        for section_name, section_data in sections.items():
            formatted_sections[section_name] = {
                "title": section_name.replace("_", " ").title(),
                "content": section_data.get("content", ""),
                "subsections": []
            }
        
        return {
            "ticker": report_data["symbol"],
            "title": f"{report_data['symbol']} Stock Analysis Report",
            "generated_date": report_data.get("timestamp", datetime.now().isoformat()),
            "sections": formatted_sections
        }
    
    async def _validate_quality(self, report_data: Dict[str, Any]) -> float:
        """Validate report quality using simple heuristics"""
        
        try:
            sections = report_data.get("sections", {})
            
            # Simple quality scoring based on content presence
            total_sections = len(sections)
            valid_sections = sum(
                1 for section in sections.values() 
                if section.get("content") and len(section.get("content", "")) > 100
            )
            
            quality_score = valid_sections / total_sections if total_sections > 0 else 0.0
            
            return quality_score
            
        except Exception as e:
            logger.warning(f"Quality validation failed: {e}")
            return 0.0
    
    async def get_generation_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of ongoing generation task"""
        # Placeholder for task status tracking
        return {"status": "unknown", "task_id": task_id}