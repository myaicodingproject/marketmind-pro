"""
Professional PDF Generation System
Generates institutional-quality PDF reports with charts and styling
"""
from typing import Dict, List, Any, Optional
import json
import base64
from datetime import datetime
from pathlib import Path
import asyncio
import logging

logger = logging.getLogger(__name__)

class PDFGenerator:
    """Professional PDF report generator"""
    
    def __init__(self):
        self.output_dir = Path("reports/generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.template_dir = Path("backend/app/features/reports/templates")
    
    async def generate_pdf(self, report_data: Dict[str, Any], output_filename: str) -> str:
        """Generate professional PDF from report data"""
        try:
            # Create HTML content
            html_content = self._generate_html(report_data)
            
            # Generate PDF using headless browser approach
            pdf_path = await self._html_to_pdf(html_content, output_filename)
            
            logger.info(f"Generated PDF report: {pdf_path}")
            return pdf_path
            
        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise
    
    def _generate_html(self, report_data: Dict[str, Any]) -> str:
        """Generate HTML content for PDF conversion"""
        metadata = report_data.get("metadata", {})
        sections = report_data.get("sections", [])
        styling = report_data.get("styling", {})
        
        html_parts = [
            self._get_html_header(styling),
            self._generate_cover_page(metadata),
            self._generate_table_of_contents(sections),
        ]
        
        # Add each section
        for section in sections:
            html_parts.append(self._generate_section_html(section))
        
        html_parts.append(self._get_html_footer())
        
        return "\n".join(html_parts)
    
    def _get_html_header(self, styling: Dict[str, Any]) -> str:
        """Generate HTML header with professional styling"""
        colors = styling.get("colors", {})
        fonts = styling.get("fonts", {})
        
        return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MarketMind Pro - Stock Analysis Report</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: '{fonts.get("body", "Inter, sans-serif")}';
            line-height: 1.6;
            color: {colors.get("primary", "#1f2937")};
            background: white;
        }}
        
        .page {{
            width: 210mm;
            min-height: 297mm;
            padding: 20mm;
            margin: 0 auto;
            background: white;
            page-break-after: always;
        }}
        
        .page:last-child {{
            page-break-after: avoid;
        }}
        
        .header {{
            border-bottom: 2px solid {colors.get("accent", "#3b82f6")};
            padding-bottom: 10px;
            margin-bottom: 30px;
        }}
        
        .logo {{
            font-size: 24px;
            font-weight: 700;
            color: {colors.get("accent", "#3b82f6")};
        }}
        
        .subtitle {{
            font-size: 14px;
            color: {colors.get("secondary", "#374151")};
            margin-top: 5px;
        }}
        
        h1 {{
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 20px;
            color: {colors.get("primary", "#1f2937")};
        }}
        
        h2 {{
            font-size: 22px;
            font-weight: 600;
            margin: 25px 0 15px 0;
            color: {colors.get("primary", "#1f2937")};
            border-left: 4px solid {colors.get("accent", "#3b82f6")};
            padding-left: 15px;
        }}
        
        h3 {{
            font-size: 18px;
            font-weight: 600;
            margin: 20px 0 10px 0;
            color: {colors.get("secondary", "#374151")};
        }}
        
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        
        .metrics-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }}
        
        .metrics-table th {{
            background: {colors.get("accent", "#3b82f6")};
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: 600;
        }}
        
        .metrics-table td {{
            padding: 12px;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .metrics-table tr:nth-child(even) {{
            background: #f9fafb;
        }}
        
        .chart-container {{
            margin: 25px 0;
            text-align: center;
            page-break-inside: avoid;
        }}
        
        .chart-title {{
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 10px;
            color: {colors.get("secondary", "#374151")};
        }}
        
        .recommendation-box {{
            background: linear-gradient(135deg, {colors.get("success", "#10b981")}, {colors.get("accent", "#3b82f6")});
            color: white;
            padding: 20px;
            border-radius: 8px;
            margin: 20px 0;
            text-align: center;
        }}
        
        .recommendation-box h3 {{
            color: white;
            margin-bottom: 10px;
        }}
        
        .price-target {{
            font-size: 24px;
            font-weight: 700;
            margin: 10px 0;
        }}
        
        .risk-box {{
            background: #fef2f2;
            border-left: 4px solid {colors.get("danger", "#ef4444")};
            padding: 15px;
            margin: 15px 0;
        }}
        
        .footer {{
            position: fixed;
            bottom: 15mm;
            left: 20mm;
            right: 20mm;
            text-align: center;
            font-size: 12px;
            color: {colors.get("secondary", "#374151")};
            border-top: 1px solid #e5e7eb;
            padding-top: 10px;
        }}
        
        .page-number {{
            position: fixed;
            bottom: 10mm;
            right: 20mm;
            font-size: 12px;
            color: {colors.get("secondary", "#374151")};
        }}
        
        @media print {{
            .page {{
                margin: 0;
                box-shadow: none;
            }}
        }}
    </style>
</head>
<body>
"""
    
    def _generate_cover_page(self, metadata: Dict[str, Any]) -> str:
        """Generate professional cover page"""
        return f"""
<div class="page">
    <div class="header">
        <div class="logo">MarketMind Pro</div>
        <div class="subtitle">AI-Powered Stock Research Platform</div>
    </div>
    
    <div style="text-align: center; margin-top: 80px;">
        <h1 style="font-size: 36px; margin-bottom: 20px;">
            {metadata.get('company_name', 'Company')} ({metadata.get('ticker', 'TICKER')})
        </h1>
        <h2 style="font-size: 24px; color: #6b7280; margin-bottom: 40px;">
            Comprehensive Stock Analysis Report
        </h2>
        
        <div style="background: #f9fafb; padding: 30px; border-radius: 12px; margin: 40px 0;">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; text-align: left;">
                <div>
                    <strong>Report Date:</strong><br>
                    {datetime.fromisoformat(metadata.get('generated_at', datetime.now().isoformat())).strftime('%B %d, %Y')}
                </div>
                <div>
                    <strong>Report Type:</strong><br>
                    {metadata.get('report_type', 'Comprehensive').title()}
                </div>
                <div>
                    <strong>Total Pages:</strong><br>
                    {metadata.get('total_pages', 'N/A')}
                </div>
                <div>
                    <strong>Version:</strong><br>
                    {metadata.get('version', '1.0.0')}
                </div>
            </div>
        </div>
        
        <div style="margin-top: 60px; font-size: 14px; color: #6b7280;">
            <p><strong>Disclaimer:</strong> This report is generated by AI and is for informational purposes only. 
            It should not be considered as investment advice. Please consult with a qualified financial advisor 
            before making investment decisions.</p>
        </div>
    </div>
</div>
"""
    
    def _generate_table_of_contents(self, sections: List[Dict[str, Any]]) -> str:
        """Generate table of contents"""
        toc_items = []
        current_page = 3  # Start after cover and TOC
        
        for section in sections:
            toc_items.append(f"""
                <tr>
                    <td style="padding: 8px 0; border-bottom: 1px dotted #d1d5db;">
                        {section.get('title', 'Section')}
                    </td>
                    <td style="text-align: right; padding: 8px 0; border-bottom: 1px dotted #d1d5db;">
                        {current_page}
                    </td>
                </tr>
            """)
            current_page += section.get('pages', 1)
        
        return f"""
<div class="page">
    <div class="header">
        <div class="logo">MarketMind Pro</div>
        <div class="subtitle">Table of Contents</div>
    </div>
    
    <h1>Table of Contents</h1>
    
    <table style="width: 100%; margin-top: 30px;">
        {''.join(toc_items)}
    </table>
</div>
"""
    
    def _generate_section_html(self, section: Dict[str, Any]) -> str:
        """Generate HTML for individual section"""
        content = section.get('content', {})
        charts = section.get('charts', [])
        
        section_html = f"""
<div class="page">
    <div class="header">
        <div class="logo">MarketMind Pro</div>
        <div class="subtitle">{section.get('title', 'Section')}</div>
    </div>
    
    <h1>{section.get('title', 'Section')}</h1>
"""
        
        # Add content based on section type
        if section.get('id') == 'executive_summary':
            section_html += self._generate_executive_summary_content(content)
        elif section.get('id') == 'financial_analysis':
            section_html += self._generate_financial_content(content)
        else:
            section_html += self._generate_generic_content(content)
        
        # Add charts if available
        for chart_id in charts:
            if chart_id in content.get('charts', {}):
                section_html += self._generate_chart_html(chart_id, content['charts'][chart_id])
        
        section_html += "</div>"
        return section_html
    
    def _generate_executive_summary_content(self, content: Dict[str, Any]) -> str:
        """Generate executive summary specific content"""
        recommendation = content.get('recommendation', {})
        
        return f"""
    <div class="recommendation-box">
        <h3>Investment Recommendation</h3>
        <div class="price-target">{recommendation.get('rating', 'HOLD')}</div>
        <p>Price Target: ${recommendation.get('price_target', 'N/A')}</p>
        <p>Current Price: ${recommendation.get('current_price', 'N/A')}</p>
    </div>
    
    <h2>Key Investment Highlights</h2>
    <p>{content.get('investment_thesis', 'Investment thesis and key highlights will be displayed here.')}</p>
    
    <h2>Financial Snapshot</h2>
    <table class="metrics-table">
        <tr><th>Metric</th><th>Value</th><th>Industry Avg</th></tr>
        <tr><td>Revenue (TTM)</td><td>${content.get('revenue', 'N/A')}</td><td>${content.get('industry_revenue', 'N/A')}</td></tr>
        <tr><td>P/E Ratio</td><td>{content.get('pe_ratio', 'N/A')}</td><td>{content.get('industry_pe', 'N/A')}</td></tr>
        <tr><td>ROE</td><td>{content.get('roe', 'N/A')}%</td><td>{content.get('industry_roe', 'N/A')}%</td></tr>
    </table>
"""
    
    def _generate_financial_content(self, content: Dict[str, Any]) -> str:
        """Generate financial analysis specific content"""
        return f"""
    <h2>Revenue Analysis</h2>
    <p>{content.get('revenue_analysis', 'Revenue analysis and trends will be displayed here.')}</p>
    
    <h2>Profitability Metrics</h2>
    <table class="metrics-table">
        <tr><th>Metric</th><th>Current</th><th>1Y Ago</th><th>Change</th></tr>
        <tr><td>Gross Margin</td><td>{content.get('gross_margin', 'N/A')}%</td><td>{content.get('gross_margin_1y', 'N/A')}%</td><td>{content.get('gross_margin_change', 'N/A')}</td></tr>
        <tr><td>Operating Margin</td><td>{content.get('operating_margin', 'N/A')}%</td><td>{content.get('operating_margin_1y', 'N/A')}%</td><td>{content.get('operating_margin_change', 'N/A')}</td></tr>
        <tr><td>Net Margin</td><td>{content.get('net_margin', 'N/A')}%</td><td>{content.get('net_margin_1y', 'N/A')}%</td><td>{content.get('net_margin_change', 'N/A')}</td></tr>
    </table>
    
    <h2>Balance Sheet Strength</h2>
    <p>{content.get('balance_sheet_analysis', 'Balance sheet analysis will be displayed here.')}</p>
"""
    
    def _generate_generic_content(self, content: Dict[str, Any]) -> str:
        """Generate generic section content"""
        html = ""
        
        # Add main content
        if 'summary' in content:
            html += f"<p>{content['summary']}</p>"
        
        # Add key points if available
        if 'key_points' in content and isinstance(content['key_points'], list):
            html += "<h2>Key Points</h2><ul>"
            for point in content['key_points']:
                html += f"<li>{point}</li>"
            html += "</ul>"
        
        return html
    
    def _generate_chart_html(self, chart_id: str, chart_data: Dict[str, Any]) -> str:
        """Generate HTML for chart display"""
        return f"""
    <div class="chart-container">
        <div class="chart-title">{chart_data.get('title', chart_id.replace('_', ' ').title())}</div>
        <div style="background: #f9fafb; padding: 20px; border-radius: 8px; min-height: 300px; display: flex; align-items: center; justify-content: center;">
            <p style="color: #6b7280;">Chart: {chart_data.get('title', chart_id)} would be displayed here</p>
        </div>
    </div>
"""
    
    def _get_html_footer(self) -> str:
        """Generate HTML footer"""
        return """
    <div class="footer">
        <p>Generated by MarketMind Pro | AI-Powered Stock Research Platform</p>
        <p>This report is for informational purposes only and should not be considered as investment advice.</p>
    </div>
</body>
</html>
"""
    
    async def _html_to_pdf(self, html_content: str, output_filename: str) -> str:
        """Convert HTML to PDF using headless browser simulation"""
        # For now, save as HTML file (would use puppeteer/playwright in production)
        output_path = self.output_dir / f"{output_filename}.html"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Generated HTML report: {output_path}")
        return str(output_path)

class ReportCustomization:
    """Handle report template customization"""
    
    @staticmethod
    def customize_template(template_data: Dict[str, Any], customizations: Dict[str, Any]) -> Dict[str, Any]:
        """Apply customizations to report template"""
        customized = template_data.copy()
        
        # Apply styling customizations
        if 'styling' in customizations:
            customized.setdefault('styling', {}).update(customizations['styling'])
        
        # Apply section customizations
        if 'sections' in customizations:
            for section_id, section_custom in customizations['sections'].items():
                for section in customized.get('sections', []):
                    if section.get('id') == section_id:
                        section.update(section_custom)
        
        return customized
    
    @staticmethod
    def get_available_customizations() -> Dict[str, Any]:
        """Get available customization options"""
        return {
            "styling": {
                "themes": ["institutional", "modern", "classic"],
                "color_schemes": ["blue", "green", "purple", "gray"],
                "fonts": ["Inter", "Roboto", "Open Sans"]
            },
            "sections": {
                "executive_summary": {"optional_fields": ["risk_rating", "esg_score"]},
                "financial_analysis": {"chart_types": ["bar", "line", "area"]},
                "valuation_analysis": {"models": ["dcf", "peer_comparison", "asset_based"]}
            }
        }