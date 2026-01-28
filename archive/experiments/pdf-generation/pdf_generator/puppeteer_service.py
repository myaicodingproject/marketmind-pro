"""
Enhanced Puppeteer PDF Generation Service
Professional HTML to PDF conversion with chart optimization and error handling
"""

import asyncio
import os
import base64
import logging
from typing import Dict, Any, Optional, List
from pyppeteer import launch
from jinja2 import Template
import json

logger = logging.getLogger(__name__)

class PuppeteerPDFService:
    def __init__(self):
        self.browser = None
        self._browser_lock = asyncio.Lock()
        
    async def initialize(self):
        """Initialize Puppeteer browser with enhanced options"""
        async with self._browser_lock:
            if not self.browser:
                try:
                    self.browser = await launch(
                        headless=True,
                        args=[
                            '--no-sandbox',
                            '--disable-setuid-sandbox',
                            '--disable-dev-shm-usage',
                            '--disable-gpu',
                            '--disable-web-security',
                            '--allow-running-insecure-content'
                        ],
                        options={'timeout': 30000}
                    )
                    logger.info("Puppeteer browser initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize Puppeteer browser: {e}")
                    raise
    
    async def close(self):
        """Close browser safely"""
        async with self._browser_lock:
            if self.browser:
                try:
                    await self.browser.close()
                    logger.info("Puppeteer browser closed")
                except Exception as e:
                    logger.error(f"Error closing browser: {e}")
                finally:
                    self.browser = None
    
    async def generate_pdf(self, html_content: str, output_path: str, options: Dict[str, Any] = None) -> str:
        """Generate PDF from HTML content with enhanced error handling"""
        await self.initialize()
        
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
            'headerTemplate': '<div style="font-size:10px; width:100%; text-align:center; color:#666; margin-top:0.5in;">MarketMind Pro Report</div>',
            'footerTemplate': '<div style="font-size:10px; width:100%; text-align:center; color:#666; margin-bottom:0.5in;"><span class="pageNumber"></span> of <span class="totalPages"></span></div>'
        }
        
        if options:
            default_options.update(options)
        
        page = None
        try:
            page = await self.browser.newPage()
            
            # Set viewport for consistent rendering
            await page.setViewport({'width': 1200, 'height': 800})
            
            # Set content and wait for rendering
            await page.setContent(html_content, {'waitUntil': 'networkidle0', 'timeout': 30000})
            
            # Wait for charts and images to load
            await page.waitForSelector('body', {'timeout': 10000})
            await asyncio.sleep(2)  # Additional wait for chart rendering
            
            # Generate PDF
            pdf_buffer = await page.pdf(default_options)
            
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write to file
            with open(output_path, 'wb') as f:
                f.write(pdf_buffer)
            
            logger.info(f"PDF generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise
        finally:
            if page:
                try:
                    await page.close()
                except Exception as e:
                    logger.error(f"Error closing page: {e}")

class HTMLReportGenerator:
    def __init__(self):
        self.template = self._get_enhanced_template()
    
    def _get_enhanced_template(self) -> Template:
        """Get enhanced HTML template with professional styling and chart optimization"""
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
        
        .cover-page {
            page-break-after: always;
            text-align: center;
            padding-top: 3in;
            background: linear-gradient(135deg, #1f4e79 0%, #2e75b6 100%);
            color: white;
            height: 100vh;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
        }
        
        .cover-title {
            font-size: 42px;
            font-weight: 700;
            margin-bottom: 20px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .cover-subtitle {
            font-size: 28px;
            font-weight: 300;
            margin-bottom: 40px;
            opacity: 0.9;
        }
        
        .cover-company {
            font-size: 20px;
            font-weight: 500;
            opacity: 0.8;
        }
        
        .cover-date {
            margin-top: 2in;
            font-size: 16px;
            opacity: 0.7;
        }
        
        .section {
            page-break-before: always;
            margin-bottom: 30px;
            padding: 20px 0;
        }
        
        .section:first-of-type {
            page-break-before: auto;
        }
        
        .section-title {
            font-size: 28px;
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
            width: 60px;
            height: 4px;
            background: #1f4e79;
        }
        
        .subsection-title {
            font-size: 20px;
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
        
        .metric-table {
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 8px;
            overflow: hidden;
        }
        
        .metric-table th {
            background: linear-gradient(135deg, #1f4e79 0%, #2e75b6 100%);
            color: white;
            padding: 15px 12px;
            text-align: left;
            font-weight: 600;
            font-size: 14px;
        }
        
        .metric-table td {
            padding: 12px;
            border-bottom: 1px solid #e0e0e0;
            font-size: 13px;
        }
        
        .metric-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .metric-table tr:hover {
            background-color: #e3f2fd;
        }
        
        .chart-container {
            text-align: center;
            margin: 35px 0;
            page-break-inside: avoid;
            background: #fafafa;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        
        .chart-image {
            max-width: 100%;
            height: auto;
            border-radius: 4px;
        }
        
        .chart-title {
            margin-top: 15px;
            font-weight: 600;
            color: #1f4e79;
            font-size: 16px;
        }
        
        .key-metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 20px;
            margin: 25px 0;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            border-left: 5px solid #2e75b6;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
        }
        
        .metric-value {
            font-size: 28px;
            font-weight: 700;
            color: #1f4e79;
            margin-bottom: 5px;
        }
        
        .metric-label {
            font-size: 14px;
            color: #666;
            font-weight: 500;
        }
        
        .toc {
            page-break-after: always;
            padding: 40px 0;
        }
        
        .toc-title {
            font-size: 32px;
            font-weight: 700;
            color: #1f4e79;
            margin-bottom: 40px;
            text-align: center;
        }
        
        .toc-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 2px dotted #ccc;
            font-size: 16px;
        }
        
        .toc-item:hover {
            background-color: #f8f9fa;
        }
        
        .toc-section {
            font-weight: 600;
            color: #1f4e79;
        }
        
        .toc-page {
            font-weight: 700;
            color: #2e75b6;
        }
        
        .page-break {
            page-break-before: always;
        }
        
        .highlight-box {
            background: #e3f2fd;
            border-left: 5px solid #2196f3;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        
        .warning-box {
            background: #fff3e0;
            border-left: 5px solid #ff9800;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        
        .success-box {
            background: #e8f5e8;
            border-left: 5px solid #4caf50;
            padding: 20px;
            margin: 20px 0;
            border-radius: 4px;
        }
        
        @media print {
            .chart-container {
                break-inside: avoid;
            }
            
            .metric-card {
                break-inside: avoid;
            }
            
            .section {
                break-inside: avoid;
            }
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
    <div class="section">
        <div class="section-title">{{ section.title }}</div>
        
        {% if section.key_metrics %}
        <div class="key-metrics">
            {% for metric in section.key_metrics %}
            <div class="metric-card">
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
        <table class="metric-table">
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
        <div class="chart-container">
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
        """Generate HTML from report data with enhanced formatting"""
        # Process content for better formatting
        if 'sections' in report_data:
            for section in report_data['sections']:
                if 'content' in section and section['content']:
                    # Convert plain text to HTML paragraphs
                    content = section['content']
                    if isinstance(content, str):
                        # Split by double newlines and wrap in paragraphs
                        paragraphs = content.split('\n\n')
                        formatted_content = ''.join(f'<p>{p.strip()}</p>' for p in paragraphs if p.strip())
                        section['content'] = formatted_content
        
        return self.template.render(**report_data)
    
    def encode_chart_image(self, image_path: str) -> str:
        """Encode chart image to base64 with error handling"""
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding chart image {image_path}: {e}")
            return ""
    
    def optimize_charts_for_pdf(self, charts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize chart data for PDF rendering"""
        optimized_charts = []
        for chart in charts:
            if 'data' in chart and chart['data']:
                # Ensure chart data is properly encoded
                if not chart['data'].startswith('data:image'):
                    chart['data'] = f"data:image/png;base64,{chart['data']}"
                optimized_charts.append(chart)
        return optimized_charts