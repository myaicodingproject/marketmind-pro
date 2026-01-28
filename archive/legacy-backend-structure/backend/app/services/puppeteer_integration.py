"""
Puppeteer PDF Integration Service
Replaces WeasyPrint with superior Puppeteer-based PDF generation
"""

import asyncio
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .puppeteer_pdf_service import PuppeteerPDFService
from ..core.monitoring import performance_monitor

class PuppeteerPDFIntegration:
    """Integration service for Puppeteer PDF generation"""
    
    def __init__(self):
        self.pdf_service = PuppeteerPDFService()
        self.performance_target = 6.0  # 4-6 second target
        
    async def generate_report_pdf(
        self, 
        ticker: str, 
        report_data: Dict[str, Any], 
        output_path: Optional[str] = None
    ) -> str:
        """
        Generate institutional-quality PDF report using Puppeteer
        
        Args:
            ticker: Stock ticker symbol
            report_data: Complete report data structure
            output_path: Optional custom output path
            
        Returns:
            Path to generated PDF file
        """
        start_time = time.time()
        
        try:
            # Prepare output path
            if output_path is None:
                timestamp = int(time.time())
                output_path = f"/mnt/c/kiro/reports/MarketMind_Report_{ticker}_Puppeteer_{timestamp}.pdf"
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Clean and structure report data
            structured_data = self._structure_report_data(ticker, report_data)
            
            # Generate PDF using Puppeteer
            result_path = await self.pdf_service.generate_pdf(structured_data, output_path)
            
            # Performance monitoring
            generation_time = time.time() - start_time
            await self._log_performance(ticker, generation_time, result_path)
            
            return result_path
            
        except Exception as e:
            error_time = time.time() - start_time
            await self._log_error(ticker, str(e), error_time)
            raise Exception(f"Puppeteer PDF generation failed for {ticker}: {str(e)}")
    
    def _structure_report_data(self, ticker: str, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure report data for Puppeteer template"""
        
        # Extract sections from report data
        sections = {}
        raw_sections = report_data.get('sections', {})
        
        # Define section order and titles
        section_mapping = {
            'executive_summary': 'Executive Summary',
            'company_deep_dive': 'Company Deep Dive', 
            'financial_analysis': 'Financial Analysis',
            'valuation_analysis': 'Valuation Analysis',
            'competitive_analysis': 'Competitive Analysis',
            'risk_assessment': 'Risk Assessment'
        }
        
        # Process each section
        for section_key, section_title in section_mapping.items():
            if section_key in raw_sections:
                section_data = raw_sections[section_key]
                sections[section_key] = {
                    'title': section_title,
                    'content': self._clean_section_content(section_data.get('content', '')),
                    'subsections': self._extract_subsections(section_data.get('content', ''))
                }
        
        # Structure final data
        structured_data = {
            'ticker': ticker.upper(),
            'title': f"{ticker.upper()} - Comprehensive Stock Analysis",
            'generated_date': datetime.now().strftime('%B %d, %Y'),
            'sections': sections
        }
        
        return structured_data
    
    def _clean_section_content(self, content: str) -> str:
        """Clean section content for PDF rendering"""
        if not content:
            return ""
        
        # Remove AI artifacts and system messages
        import re
        
        cleaning_patterns = [
            r'Invoking \d+ subagents in parallel.*?\n',
            r'Searching the web for:.*?\n',
            r'using tool:.*?\n',
            r'> I\'ll.*?\n',
            r'> .*?\n',
            r'\d+: \+ \d+:.*?\n',
            r'■{3,}',
            r'━{3,}',
            r'References:\s*\[\d+\].*?\n',
            r'\[.*?\]\(.*?\)',
            r'```[^`]*```',
            r'`[^`]+`',
            r'^\s*[-=]{3,}\s*$',
            r'^\s*\*\s*\*\s*\*\s*$'
        ]
        
        for pattern in cleaning_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Clean up whitespace
        content = re.sub(r'\n{3,}', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        content = content.strip()
        
        return content
    
    def _extract_subsections(self, content: str) -> list:
        """Extract subsections from content"""
        if not content:
            return []
        
        import re
        subsections = []
        
        # Look for markdown-style headers
        sections = re.split(r'\n## ', content)
        
        for i, section in enumerate(sections[1:], 1):  # Skip first split
            lines = section.split('\n', 1)
            if len(lines) >= 2:
                title = lines[0].strip()
                content_part = lines[1].strip()
                
                if title and content_part:
                    subsections.append({
                        'title': title,
                        'content': self._clean_section_content(content_part)
                    })
        
        return subsections
    
    async def _log_performance(self, ticker: str, generation_time: float, output_path: str):
        """Log performance metrics"""
        try:
            file_size = Path(output_path).stat().st_size
            
            performance_data = {
                'ticker': ticker,
                'generation_time': generation_time,
                'file_size': file_size,
                'target_met': generation_time <= self.performance_target,
                'timestamp': datetime.now().isoformat()
            }
            
            # Log to performance monitor
            await performance_monitor.log_pdf_generation(performance_data)
            
            # Console output
            status = "✅" if generation_time <= self.performance_target else "⚠️"
            print(f"{status} PDF generated for {ticker}: {generation_time:.2f}s, {file_size:,} bytes")
            
        except Exception as e:
            print(f"⚠️ Performance logging failed: {e}")
    
    async def _log_error(self, ticker: str, error: str, elapsed_time: float):
        """Log generation errors"""
        try:
            error_data = {
                'ticker': ticker,
                'error': error,
                'elapsed_time': elapsed_time,
                'timestamp': datetime.now().isoformat()
            }
            
            await performance_monitor.log_pdf_error(error_data)
            print(f"❌ PDF generation failed for {ticker} after {elapsed_time:.2f}s: {error}")
            
        except Exception as e:
            print(f"⚠️ Error logging failed: {e}")


# Retry mechanism for robustness
class PuppeteerPDFWithRetry:
    """Puppeteer PDF service with retry mechanism"""
    
    def __init__(self, max_retries: int = 3):
        self.integration = PuppeteerPDFIntegration()
        self.max_retries = max_retries
    
    async def generate_report_pdf(
        self, 
        ticker: str, 
        report_data: Dict[str, Any], 
        output_path: Optional[str] = None
    ) -> str:
        """Generate PDF with retry mechanism"""
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                print(f"🔄 PDF generation attempt {attempt + 1}/{self.max_retries} for {ticker}")
                
                result = await self.integration.generate_report_pdf(ticker, report_data, output_path)
                
                if attempt > 0:
                    print(f"✅ PDF generation succeeded on attempt {attempt + 1}")
                
                return result
                
            except Exception as e:
                last_error = e
                print(f"❌ Attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    print(f"⏳ Waiting {wait_time}s before retry...")
                    await asyncio.sleep(wait_time)
        
        # All attempts failed
        raise Exception(f"PDF generation failed after {self.max_retries} attempts. Last error: {str(last_error)}")


# Factory function for easy integration
def create_puppeteer_pdf_service(with_retry: bool = True) -> PuppeteerPDFIntegration:
    """Create Puppeteer PDF service instance"""
    if with_retry:
        return PuppeteerPDFWithRetry()
    else:
        return PuppeteerPDFIntegration()


# Compatibility function to replace WeasyPrint calls
async def generate_professional_pdf(ticker: str, report_data: Dict[str, Any], output_path: str = None) -> str:
    """
    Drop-in replacement for WeasyPrint PDF generation
    
    Args:
        ticker: Stock ticker symbol
        report_data: Report data structure
        output_path: Output file path (optional)
    
    Returns:
        Path to generated PDF file
    """
    service = create_puppeteer_pdf_service(with_retry=True)
    return await service.generate_report_pdf(ticker, report_data, output_path)