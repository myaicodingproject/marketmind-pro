"""
Enhanced MarketMind Pro PDF Generation Service
Professional HTML to PDF conversion with advanced chart rendering and error handling
"""

import asyncio
import os
import base64
import logging
import json
from typing import Dict, Any, Optional, List
from pyppeteer import launch
from jinja2 import Template
import tempfile
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

class EnhancedPuppeteerPDFService:
    """Enhanced PDF service with robust error handling and chart optimization"""
    
    def __init__(self):
        self.browser = None
        self._browser_lock = asyncio.Lock()
        self.browser_args = [
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--disable-web-security',
            '--allow-running-insecure-content',
            '--disable-features=VizDisplayCompositor',
            '--disable-extensions',
            '--disable-plugins',
            '--disable-images',  # Disable image loading for faster rendering
            '--disable-javascript',  # Disable JS for security and speed
            '--virtual-time-budget=30000'  # Set virtual time budget
        ]
        
    async def initialize(self):
        """Initialize Puppeteer browser with enhanced error handling"""
        async with self._browser_lock:
            if not self.browser:
                try:
                    logger.info("Initializing enhanced Puppeteer browser...")
                    self.browser = await launch(
                        headless=True,
                        args=self.browser_args,
                        options={
                            'timeout': 60000,
                            'handleSIGINT': False,
                            'handleSIGTERM': False,
                            'handleSIGHUP': False
                        }
                    )
                    logger.info("Enhanced Puppeteer browser initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Puppeteer browser: {e}")
                    raise RuntimeError(f"Browser initialization failed: {e}")
    
    async def close(self):
        """Close browser safely with enhanced cleanup"""
        async with self._browser_lock:
            if self.browser:
                try:
                    pages = await self.browser.pages()
                    for page in pages:
                        try:
                            await page.close()
                        except Exception as e:
                            logger.warning(f"Error closing page: {e}")
                    
                    await self.browser.close()
                    logger.info("Enhanced Puppeteer browser closed successfully")
                except Exception as e:
                    logger.error(f"Error closing browser: {e}")
                finally:
                    self.browser = None
    
    async def generate_pdf(self, html_content: str, output_path: str, options: Dict[str, Any] = None) -> str:
        """Generate PDF with enhanced error handling and chart optimization"""
        await self.initialize()
        
        # Enhanced PDF options for professional output
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
            'headerTemplate': '<div style="font-size:10px; width:100%; text-align:center; color:#666; margin-top:0.5in;">MarketMind Pro - Professional Financial Analysis</div>',
            'footerTemplate': '<div style="font-size:10px; width:100%; text-align:center; color:#666; margin-bottom:0.5in;"><span class="pageNumber"></span> of <span class="totalPages"></span></div>',
            'timeout': 60000
        }
        
        if options:
            default_options.update(options)
        
        page = None
        temp_html_file = None
        
        try:
            # Create temporary HTML file for better rendering
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(html_content)
                temp_html_file = f.name
            
            page = await self.browser.newPage()
            
            # Enhanced page settings for better rendering
            await page.setViewport({'width': 1200, 'height': 800})
            await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            # Load HTML content from file for better resource handling
            file_url = f'file://{os.path.abspath(temp_html_file)}'
            await page.goto(file_url, {
                'waitUntil': 'networkidle0',
                'timeout': 30000
            })
            
            # Wait for page to be fully rendered
            await page.waitForSelector('body', {'timeout': 10000})
            
            # Additional wait for any dynamic content
            await asyncio.sleep(3)
            
            # Optimize for chart rendering
            await self._optimize_charts_for_pdf(page)
            
            logger.info("Generating PDF with enhanced options...")
            
            # Generate PDF with enhanced error handling
            pdf_buffer = await page.pdf(default_options)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer)
            
            # Verify file was created and has content
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                logger.info(f"Enhanced PDF generated successfully: {output_path} ({os.path.getsize(output_path):,} bytes)")
                return output_path
            else:
                raise RuntimeError("Generated PDF is empty or corrupted")
            
        except Exception as e:
            logger.error(f"Error generating enhanced PDF: {e}")
            raise RuntimeError(f"PDF generation failed: {e}")
        finally:
            # Cleanup
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.warning(f"Error closing page: {e}")
            
            if temp_html_file and os.path.exists(temp_html_file):
                try:
                    os.unlink(temp_html_file)
                except Exception as e:
                    logger.warning(f"Error removing temp file: {e}")
    
    async def _optimize_charts_for_pdf(self, page):
        """Optimize charts and images for PDF rendering"""
        try:
            # Wait for any chart libraries to finish rendering
            await page.evaluate('''
                () => {
                    // Wait for any chart animations to complete
                    return new Promise((resolve) => {
                        setTimeout(resolve, 2000);
                    });
                }
            ''')
            
            # Ensure all images are loaded
            await page.evaluate('''
                () => {
                    const images = Array.from(document.images);
                    return Promise.all(images.map(img => {
                        if (img.complete) return Promise.resolve();
                        return new Promise((resolve, reject) => {
                            img.addEventListener('load', resolve);
                            img.addEventListener('error', reject);
                        });
                    }));
                }
            ''')
            
            logger.info("Chart optimization completed")
            
        except Exception as e:
            logger.warning(f"Chart optimization failed: {e}")

class EnhancedHTMLReportGenerator:
    """Enhanced HTML generator with improved styling and chart support"""
    
    def __init__(self):
        self.template = self._get_enhanced_template()
    
    def _get_enhanced_template(self) -> Template:
        """Enhanced HTML template with professional styling and chart optimization"""
        template_str = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <style>
        @page {
            size: A4;
            margin: 1in 0.75in;
        }
        
        * {
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            margin: 0;
            padding: 0;
            background: white;
        }
        
        /* Enhanced Cover Page */
        .cover-page {
            page-break-after: always;
            text-align: center;
            padding-top: 2in;
            background: linear-gradient(135deg, #1f4e79 0%, #2e75b6 100%);
            color: white;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            position: relative;
        }
        
        .cover-page::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="0.5"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
            opacity: 0.3;
        }
        
        .cover-title {
            font-size: 48px;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            z-index: 1;
        }
        
        .cover-subtitle {
            font-size: 24px;
            font-weight: 300;
            margin-bottom: 40px;
            opacity: 0.9;
            z-index: 1;
        }
        
        .cover-company {
            font-size: 20px;
            font-weight: 500;
            opacity: 0.8;
            z-index: 1;
        }
        
        .cover-date {
            margin-top: 2in;
            font-size: 16px;
            opacity: 0.7;
            z-index: 1;
        }
        
        /* Enhanced Section Styling */
        .section {
            page-break-before: always;
            margin-bottom: 30px;
            padding: 20px 0;
        }
        
        .section:first-of-type {
            page-break-before: auto;
        }
        
        .section-title {
            font-size: 32px;
            font-weight: 700;
            color: #1f4e79;
            border-bottom: 4px solid #2e75b6;
            padding-bottom: 15px;
            margin-bottom: 25px;
            position: relative;
        }
        
        .section-title::after {
            content: '';
            position: absolute;
            bottom: -4px;
            left: 0;
            width: 80px;
            height: 4px;
            background: #1f4e79;
        }
        
        .subsection-title {
            font-size: 22px;
            font-weight: 600;
            color: #2e75b6;
            margin-top: 30px;
            margin-bottom: 15px;
            border-left: 4px solid #2e75b6;
            padding-left: 15px;
        }
        
        .content {
            font-size: 14px;
            line-height: 1.8;
            text-align: justify;
            margin-bottom: 20px;
        }
        
        .content p {
            margin-bottom: 15px;
        }
        
        .content ul, .content ol {
            margin: 15px 0;
            padding-left: 25px;
        }
        
        .content li {
            margin-bottom: 8px;
        }
        
        /* Enhanced Key Metrics Grid */
        .key-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left: 5px solid #2e75b6;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            transition: transform 0.2s;
            text-align: center;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
        }
        
        .metric-value {
            font-size: 32px;
            font-weight: 700;
            color: #1f4e79;
            margin-bottom: 8px;
            display: block;
        }
        
        .metric-label {
            font-size: 14px;
            color: #666;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        /* Enhanced Table Styling */
        .metric-table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-radius: 12px;
            overflow: hidden;
        }
        
        .metric-table th {
            background: linear-gradient(135deg, #1f4e79 0%, #2e75b6 100%);
            color: white;
            padding: 18px 15px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-table td {
            padding: 15px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 13px;
        }
        
        .metric-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .metric-table tr:hover {
            background-color: #e3f2fd;
        }
        
        /* Enhanced Chart Container */
        .chart-container {
            text-align: center;
            margin: 40px 0;
            page-break-inside: avoid;
            background: #fafafa;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        
        .chart-image {
            max-width: 100%;
            height: auto;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .chart-title {
            margin-top: 15px;
            font-weight: 600;
            color: #1f4e79;
            font-size: 16px;
        }
        
        /* Enhanced Table of Contents */
        .toc {
            page-break-after: always;
            padding: 40px 0;
        }
        
        .toc-title {
            font-size: 36px;
            font-weight: 700;
            color: #1f4e79;
            margin-bottom: 40px;
            text-align: center;
            border-bottom: 3px solid #2e75b6;
            padding-bottom: 20px;
        }
        
        .toc-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 0;
            border-bottom: 2px dotted #ccc;
            font-size: 16px;
            transition: background-color 0.2s;
        }
        
        .toc-item:hover {
            background-color: #f8f9fa;
            padding-left: 10px;
        }
        
        .toc-section {
            font-weight: 600;
            color: #1f4e79;
        }
        
        .toc-page {
            font-weight: 700;
            color: #2e75b6;
            background: #e3f2fd;
            padding: 5px 10px;
            border-radius: 20px;
            min-width: 30px;
            text-align: center;
        }
        
        /* Enhanced Highlight Boxes */
        .highlight-box {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-left: 5px solid #2196f3;
            padding: 25px;
            margin: 25px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .warning-box {
            background: linear-gradient(135deg, #fff3e0 0%, #ffcc02 100%);
            border-left: 5px solid #ff9800;
            padding: 25px;
            margin: 25px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .success-box {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-left: 5px solid #4caf50;
            padding: 25px;
            margin: 25px 0;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        /* Print Optimizations */
        @media print {
            .chart-container {
                break-inside: avoid;
                -webkit-break-inside: avoid;
            }
            
            .metric-card {
                break-inside: avoid;
                -webkit-break-inside: avoid;
            }
            
            .section {
                break-inside: avoid;
                -webkit-break-inside: avoid;
            }
            
            .highlight-box, .warning-box, .success-box {
                break-inside: avoid;
                -webkit-break-inside: avoid;
            }
        }
        
        /* Page Break Controls */
        .page-break {
            page-break-before: always;
        }
        
        .no-break {
            page-break-inside: avoid;
        }
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page">
        <div class="cover-title">{{ title }}</div>
        <div class="cover-subtitle">{{ subtitle }}</div>
        <div class="cover-company">{{ company_name }}</div>
        <div class="cover-date">Generated on {{ date }}</div>
    </div>
    
    <!-- Table of Contents -->
    <div class="toc">
        <div class="toc-title">Table of Contents</div>
        {% for section in sections %}
        <div class="toc-item">
            <span class="toc-section">{{ section.title }}</span>
            <span class="toc-page">{{ section.page }}</span>
        </div>
        {% endfor %}
    </div>
    
    <!-- Report Sections -->
    {% for section in sections %}
    <div class="section no-break">
        <div class="section-title">{{ section.title }}</div>
        
        {% if section.key_metrics %}
        <div class="key-metrics">
            {% for metric in section.key_metrics %}
            <div class="metric-card no-break">
                <div class="metric-value">{{ metric.value }}</div>
                <div class="metric-label">{{ metric.label }}</div>
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if section.content %}
        <div class="content">{{ section.content | safe }}</div>
        {% endif %}
        
        {% if section.tables %}
        {% for table in section.tables %}
        <table class="metric-table no-break">
            <thead>
                <tr>
                    {% for header in table.headers %}
                    <th>{{ header }}</th>
                    {% endfor %}
                </tr>
            </thead>
            <tbody>
                {% for row in table.rows %}
                <tr>
                    {% for cell in row %}
                    <td>{{ cell }}</td>
                    {% endfor %}
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% endfor %}
        {% endif %}
        
        {% if section.charts %}
        {% for chart in section.charts %}
        <div class="chart-container no-break">
            <img src="data:image/png;base64,{{ chart.data }}" alt="{{ chart.title }}" class="chart-image">
            <div class="chart-title">{{ chart.title }}</div>
        </div>
        {% endfor %}
        {% endif %}
    </div>
    {% endfor %}
</body>
</html>
        """
        return Template(template_str)
    
    def generate_html(self, report_data: Dict[str, Any]) -> str:
        """Generate enhanced HTML from report data"""
        # Process content for better formatting
        if 'sections' in report_data:
            for section in report_data['sections']:
                if 'content' in section and section['content']:
                    content = section['content']
                    if isinstance(content, str) and not content.startswith('<'):
                        # Convert plain text to HTML paragraphs
                        paragraphs = content.split('\n\n')
                        formatted_content = ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
                        section['content'] = formatted_content
        
        return self.template.render(**report_data)
    
    def add_chart_data(self, report_data: Dict[str, Any], chart_images: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Add chart data to report sections"""
        if not chart_images:
            return report_data
        
        # Add charts to appropriate sections
        for i, chart in enumerate(chart_images):
            section_index = min(i, len(report_data.get('sections', [])) - 1)
            if section_index >= 0 and 'sections' in report_data:
                if 'charts' not in report_data['sections'][section_index]:
                    report_data['sections'][section_index]['charts'] = []
                report_data['sections'][section_index]['charts'].append(chart)
        
        return report_data
    
    def optimize_for_pdf(self, html_content: str) -> str:
        """Optimize HTML content for PDF generation"""
        # Add PDF-specific optimizations
        optimizations = [
            # Ensure proper page breaks
            ('<div class="section">', '<div class="section no-break">'),
            # Optimize image loading
            ('loading="lazy"', ''),
            # Remove any JavaScript
            ('<script', '<!-- <script'),
            ('</script>', '</script> -->'),
        ]
        
        for old, new in optimizations:
            html_content = html_content.replace(old, new)
        
        return html_content