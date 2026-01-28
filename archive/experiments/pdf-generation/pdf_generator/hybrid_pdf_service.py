"""
Hybrid MarketMind Pro PDF Generation Service
Professional HTML to PDF conversion with Puppeteer primary and WeasyPrint fallback
"""

import asyncio
import os
import base64
import logging
import json
from typing import Dict, Any, Optional, List
from datetime import datetime
import tempfile

# Import both PDF engines
try:
    from pyppeteer import launch
    PUPPETEER_AVAILABLE = True
except ImportError:
    PUPPETEER_AVAILABLE = False

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False

from jinja2 import Template

logger = logging.getLogger(__name__)

class HybridPDFService:
    """Hybrid PDF service with multiple rendering engines"""
    
    def __init__(self):
        self.browser = None
        self._browser_lock = asyncio.Lock()
        self.puppeteer_available = PUPPETEER_AVAILABLE
        self.weasyprint_available = WEASYPRINT_AVAILABLE
        
        logger.info(f"PDF Service initialized - Puppeteer: {self.puppeteer_available}, WeasyPrint: {self.weasyprint_available}")
    
    async def generate_pdf(self, html_content: str, output_path: str, options: Dict[str, Any] = None) -> str:
        """Generate PDF using the best available method"""
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Try Puppeteer first (best quality)
        if self.puppeteer_available:
            try:
                logger.info("Attempting PDF generation with Puppeteer...")
                return await self._generate_with_puppeteer(html_content, output_path, options)
            except Exception as e:
                logger.warning(f"Puppeteer failed: {e}, falling back to WeasyPrint")
        
        # Fallback to WeasyPrint
        if self.weasyprint_available:
            try:
                logger.info("Attempting PDF generation with WeasyPrint...")
                return await self._generate_with_weasyprint(html_content, output_path, options)
            except Exception as e:
                logger.warning(f"WeasyPrint failed: {e}, using HTML fallback")
        
        # Final fallback - save as HTML
        logger.info("Using HTML fallback...")
        return await self._generate_html_fallback(html_content, output_path)
    
    async def _generate_with_puppeteer(self, html_content: str, output_path: str, options: Dict[str, Any] = None) -> str:
        """Generate PDF using Puppeteer"""
        async with self._browser_lock:
            if not self.browser:
                self.browser = await launch(
                    headless=True,
                    args=[
                        '--no-sandbox',
                        '--disable-setuid-sandbox',
                        '--disable-dev-shm-usage',
                        '--disable-gpu',
                        '--disable-web-security'
                    ],
                    options={'timeout': 30000}
                )
        
        default_options = {
            'format': 'A4',
            'printBackground': True,
            'preferCSSPageSize': True,
            'margin': {
                'top': '1in',
                'right': '0.75in',
                'bottom': '1in',
                'left': '0.75in'
            },
            'displayHeaderFooter': True,
            'headerTemplate': '<div style="font-size:10px; width:100%; text-align:center; color:#666;">MarketMind Pro Report</div>',
            'footerTemplate': '<div style="font-size:10px; width:100%; text-align:center; color:#666;"><span class="pageNumber"></span> of <span class="totalPages"></span></div>'
        }
        
        if options:
            default_options.update(options)
        
        page = None
        temp_file = None
        
        try:
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_file = f.name
            
            page = await self.browser.newPage()
            await page.setViewport({'width': 1200, 'height': 800})
            
            # Load from file
            file_url = f'file://{os.path.abspath(temp_file)}'
            await page.goto(file_url, {'waitUntil': 'networkidle0', 'timeout': 20000})
            
            # Wait for rendering
            await page.waitForSelector('body', {'timeout': 5000})
            await asyncio.sleep(2)
            
            # Generate PDF
            pdf_buffer = await page.pdf(default_options)
            
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                logger.info(f"Puppeteer PDF generated: {output_path} ({os.path.getsize(output_path):,} bytes)")
                return output_path
            else:
                raise RuntimeError("Generated PDF is empty")
                
        finally:
            if page:
                try:
                    await page.close()
                except:
                    pass
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
    
    async def _generate_with_weasyprint(self, html_content: str, output_path: str, options: Dict[str, Any] = None) -> str:
        """Generate PDF using WeasyPrint"""
        
        # WeasyPrint-optimized CSS
        weasyprint_css = """
        @page {
            size: A4;
            margin: 1in 0.75in;
            @top-center {
                content: "MarketMind Pro Report";
                font-size: 10px;
                color: #666;
            }
            @bottom-center {
                content: counter(page) " of " counter(pages);
                font-size: 10px;
                color: #666;
            }
        }
        
        body {
            font-family: 'DejaVu Sans', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        .cover-page {
            page-break-after: always;
            text-align: center;
            padding-top: 3in;
            background: linear-gradient(135deg, #1f4e79 0%, #2e75b6 100%);
            color: white;
            height: 100vh;
        }
        
        .section {
            page-break-before: always;
            margin-bottom: 30px;
        }
        
        .section:first-of-type {
            page-break-before: auto;
        }
        
        .no-break {
            page-break-inside: avoid;
        }
        
        .key-metrics {
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            margin: 25px 0;
        }
        
        .metric-card {
            flex: 1;
            min-width: 200px;
            background: #f8f9fa;
            border-left: 5px solid #2e75b6;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        
        .metric-value {
            font-size: 24px;
            font-weight: bold;
            color: #1f4e79;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 12px;
            color: #666;
            font-weight: 500;
        }
        
        .highlight-box, .warning-box, .success-box {
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            page-break-inside: avoid;
        }
        
        .highlight-box {
            background: #e3f2fd;
            border-left: 5px solid #2196f3;
        }
        
        .warning-box {
            background: #fff3e0;
            border-left: 5px solid #ff9800;
        }
        
        .success-box {
            background: #e8f5e8;
            border-left: 5px solid #4caf50;
        }
        """
        
        # Add WeasyPrint CSS to HTML
        html_with_css = html_content.replace(
            '</style>',
            weasyprint_css + '</style>'
        )
        
        try:
            # Generate PDF with WeasyPrint
            html_doc = weasyprint.HTML(string=html_with_css)
            html_doc.write_pdf(output_path)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                logger.info(f"WeasyPrint PDF generated: {output_path} ({os.path.getsize(output_path):,} bytes)")
                return output_path
            else:
                raise RuntimeError("Generated PDF is empty")
                
        except Exception as e:
            logger.error(f"WeasyPrint generation failed: {e}")
            raise
    
    async def _generate_html_fallback(self, html_content: str, output_path: str) -> str:
        """Generate HTML fallback when PDF generation fails"""
        html_path = output_path.replace('.pdf', '.html')
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"HTML fallback generated: {html_path}")
        return html_path
    
    async def close(self):
        """Close browser if open"""
        async with self._browser_lock:
            if self.browser:
                try:
                    await self.browser.close()
                    logger.info("Browser closed")
                except:
                    pass
                finally:
                    self.browser = None

class ProductionPDFGenerator:
    """Production-ready PDF generator with comprehensive error handling"""
    
    def __init__(self):
        self.pdf_service = HybridPDFService()
        self.html_generator = self._create_html_generator()
    
    def _create_html_generator(self):
        """Create HTML generator with production template"""
        from enhanced_pdf_service import EnhancedHTMLReportGenerator
        return EnhancedHTMLReportGenerator()
    
    async def generate_report_pdf(self, report_data: Dict[str, Any], output_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate PDF report with comprehensive error handling"""
        
        start_time = datetime.now()
        result = {
            'success': False,
            'output_path': None,
            'file_size': 0,
            'generation_time': 0,
            'method_used': None,
            'error': None
        }
        
        try:
            # Generate HTML content
            html_content = self.html_generator.generate_html(report_data)
            html_content = self.html_generator.optimize_for_pdf(html_content)
            
            # Generate PDF
            final_path = await self.pdf_service.generate_pdf(html_content, output_path, options)
            
            # Update result
            result['success'] = True
            result['output_path'] = final_path
            result['file_size'] = os.path.getsize(final_path) if os.path.exists(final_path) else 0
            result['generation_time'] = (datetime.now() - start_time).total_seconds()
            
            # Determine method used
            if final_path.endswith('.pdf'):
                if self.pdf_service.puppeteer_available:
                    result['method_used'] = 'puppeteer'
                elif self.pdf_service.weasyprint_available:
                    result['method_used'] = 'weasyprint'
                else:
                    result['method_used'] = 'unknown'
            else:
                result['method_used'] = 'html_fallback'
            
            logger.info(f"PDF generation completed: {result['method_used']} in {result['generation_time']:.2f}s")
            
        except Exception as e:
            result['error'] = str(e)
            result['generation_time'] = (datetime.now() - start_time).total_seconds()
            logger.error(f"PDF generation failed: {e}")
        
        return result
    
    async def close(self):
        """Close PDF service"""
        await self.pdf_service.close()