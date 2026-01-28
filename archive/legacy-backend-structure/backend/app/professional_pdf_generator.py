"""
Professional PDF Generator for MarketMind Pro
Replaces the awful ReportLab implementation with WeasyPrint + professional templates
"""

import json
import re
from typing import Dict, Any, List
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
from weasyprint import HTML, CSS
import tempfile
import os

class ContentCleaner:
    """Cleans raw AI-generated content for professional presentation"""
    
    def __init__(self):
        # Patterns to remove AI system messages and debug text
        self.removal_patterns = [
            r'Invoking \d+ subagents in parallel \(using tool: [^)]+\)',
            r'Searching the web for: [^\n]+\(using tool: web_search\)',
            r'using tool: [^\n]+',
            r'> I\'ll [^\n]+',
            r'\d+: \+ \d+:',  # Line numbers like "192: + 193:"
            r'■{10,}',  # Multiple bullet symbols
            r'━{10,}',  # Multiple dash symbols
            r'References:\s*\[\d+\][^\n]*\n',  # Reference citations
        ]
    
    def clean_content(self, content: str) -> str:
        """Remove AI artifacts and clean formatting"""
        if not content:
            return ""
        
        # Remove AI system messages
        for pattern in self.removal_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Clean markdown formatting
        content = re.sub(r'^#{1,6}\s+', '', content, flags=re.MULTILINE)  # Remove markdown headers
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)  # Italic
        content = re.sub(r'- ', '• ', content)  # Convert dashes to bullets
        
        # Clean up spacing
        content = re.sub(r'\n{3,}', '\n\n', content)  # Multiple newlines
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces
        
        return content.strip()
    
    def extract_key_metrics(self, content: str) -> Dict[str, str]:
        """Extract key financial metrics from executive summary"""
        metrics = {}
        
        # Extract price targets
        price_match = re.search(r'Price Target:\s*\$?(\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if price_match:
            metrics['price_target'] = f"${price_match.group(1)}"
        
        # Extract current price
        current_match = re.search(r'Current Price:\s*[~$]*(\d+(?:\.\d+)?)', content, re.IGNORECASE)
        if current_match:
            metrics['current_price'] = f"${current_match.group(1)}"
        
        # Extract recommendation
        rec_match = re.search(r'Investment Recommendation:\s*(\w+)', content, re.IGNORECASE)
        if rec_match:
            metrics['recommendation'] = rec_match.group(1).upper()
        
        # Extract market cap
        mcap_match = re.search(r'Market Capitalization:\s*\$?([\d.]+)\s*(trillion|billion)', content, re.IGNORECASE)
        if mcap_match:
            metrics['market_cap'] = f"${mcap_match.group(1)} {mcap_match.group(2)}"
        
        return metrics
    
    def structure_section(self, section_key: str, section_data: Dict[str, Any]) -> Dict[str, Any]:
        """Structure section data for template rendering"""
        title = section_data.get('title', '').replace('_', ' ').title()
        content = self.clean_content(section_data.get('content', ''))
        
        structured = {
            'title': title,
            'content': content,
            'subsections': []
        }
        
        # Extract key metrics for executive summary
        if section_key == 'executive_summary':
            structured['key_metrics'] = self.extract_key_metrics(content)
        
        # Split content into subsections for better formatting
        if '##' in content:
            parts = content.split('##')
            structured['content'] = parts[0].strip()
            for part in parts[1:]:
                if part.strip():
                    lines = part.strip().split('\n', 1)
                    sub_title = lines[0].strip()
                    sub_content = lines[1] if len(lines) > 1 else ""
                    structured['subsections'].append({
                        'title': sub_title,
                        'content': sub_content.strip()
                    })
        
        return structured
    
    def clean_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean entire report data structure"""
        cleaned = {
            'ticker': report_data.get('ticker', 'UNKNOWN'),
            'title': report_data.get('title', 'Stock Analysis Report'),
            'generated_date': report_data.get('generated_date', ''),
            'sections': {}
        }
        
        sections = report_data.get('sections', {})
        for section_key, section_data in sections.items():
            cleaned['sections'][section_key] = self.structure_section(section_key, section_data)
        
        return cleaned


class ProfessionalPDFGenerator:
    """Professional PDF generator using WeasyPrint and Jinja2 templates"""
    
    def __init__(self):
        self.content_cleaner = ContentCleaner()
        self.template_dir = Path(__file__).parent / "templates"
        self.css_dir = Path(__file__).parent / "static" / "css"
        
        # Create directories if they don't exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.css_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
        
        self._create_template()
        self._create_css()
    
    def _create_template(self):
        """Create professional HTML template"""
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="report-styles.css">
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page">
        <div class="header">
            <div class="logo">MarketMind Pro</div>
            <div class="tagline">The Mind Behind Smart Investing</div>
        </div>
        
        <div class="cover-content">
            <h1 class="report-title">{{ ticker }} - Comprehensive Stock Analysis</h1>
            <div class="report-subtitle">Institutional Investment Research Report</div>
            
            {% if sections.executive_summary and sections.executive_summary.key_metrics %}
            <div class="key-metrics-summary">
                {% set metrics = sections.executive_summary.key_metrics %}
                {% if metrics.recommendation %}
                <div class="metric-item">
                    <span class="metric-label">Recommendation:</span>
                    <span class="recommendation {{ metrics.recommendation.lower() }}">{{ metrics.recommendation }}</span>
                </div>
                {% endif %}
                {% if metrics.price_target %}
                <div class="metric-item">
                    <span class="metric-label">Price Target:</span>
                    <span class="metric-value">{{ metrics.price_target }}</span>
                </div>
                {% endif %}
                {% if metrics.current_price %}
                <div class="metric-item">
                    <span class="metric-label">Current Price:</span>
                    <span class="metric-value">{{ metrics.current_price }}</span>
                </div>
                {% endif %}
            </div>
            {% endif %}
        </div>
        
        <div class="cover-footer">
            <div class="generated-date">Generated: {{ generated_date or "January 25, 2026" }}</div>
            <div class="disclaimer">This report is for institutional investment research purposes only.</div>
        </div>
    </div>
    
    <!-- Table of Contents -->
    <div class="page-break"></div>
    <div class="toc-page">
        <h2>Table of Contents</h2>
        <div class="toc-list">
            {% for section_key, section in sections.items() %}
            <div class="toc-item">
                <span class="toc-title">{{ loop.index }}. {{ section.title }}</span>
                <span class="toc-dots"></span>
                <span class="toc-page">{{ loop.index + 2 }}</span>
            </div>
            {% endfor %}
        </div>
    </div>
    
    <!-- Report Sections -->
    {% for section_key, section in sections.items() %}
    <div class="page-break"></div>
    <div class="report-section">
        <div class="section-header">
            <h2 class="section-title">{{ section.title }}</h2>
            <div class="section-divider"></div>
        </div>
        
        {% if section_key == 'executive_summary' and section.key_metrics %}
        <div class="executive-summary-metrics">
            {% set metrics = section.key_metrics %}
            <div class="metrics-grid">
                {% if metrics.recommendation %}
                <div class="metric-card">
                    <div class="metric-label">Investment Recommendation</div>
                    <div class="metric-value recommendation {{ metrics.recommendation.lower() }}">
                        {{ metrics.recommendation }}
                    </div>
                </div>
                {% endif %}
                {% if metrics.price_target %}
                <div class="metric-card">
                    <div class="metric-label">12-Month Price Target</div>
                    <div class="metric-value price-target">{{ metrics.price_target }}</div>
                </div>
                {% endif %}
                {% if metrics.current_price %}
                <div class="metric-card">
                    <div class="metric-label">Current Price</div>
                    <div class="metric-value">{{ metrics.current_price }}</div>
                </div>
                {% endif %}
                {% if metrics.market_cap %}
                <div class="metric-card">
                    <div class="metric-label">Market Capitalization</div>
                    <div class="metric-value">{{ metrics.market_cap }}</div>
                </div>
                {% endif %}
            </div>
        </div>
        {% endif %}
        
        <div class="section-content">
            {{ section.content | replace('\n', '<br>') | safe }}
        </div>
        
        {% if section.subsections %}
        {% for subsection in section.subsections %}
        <div class="subsection">
            <h3 class="subsection-title">{{ subsection.title }}</h3>
            <div class="subsection-content">
                {{ subsection.content | replace('\n', '<br>') | safe }}
            </div>
        </div>
        {% endfor %}
        {% endif %}
    </div>
    {% endfor %}
    
    <!-- Footer -->
    <div class="report-footer">
        <div class="footer-content">
            <div class="footer-left">
                <strong>MarketMind Pro</strong> - AI-Powered Stock Research Platform
            </div>
            <div class="footer-right">
                Generated: {{ generated_date or "January 25, 2026" }}
            </div>
        </div>
        <div class="footer-disclaimer">
            <p><strong>Important Disclaimer:</strong> This report is generated using AI analysis and is for informational purposes only. 
            Past performance does not guarantee future results. Please consult with a qualified financial advisor before making investment decisions.</p>
        </div>
    </div>
</body>
</html>'''
        
        template_path = self.template_dir / "stock_report.html"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def _create_css(self):
        """Create professional CSS styling"""
        css_content = '''/* Professional Stock Research Report Styles */

@page {
    size: A4;
    margin: 0.75in;
    @top-center {
        content: "MarketMind Pro - Institutional Research";
        font-family: 'Times New Roman', serif;
        font-size: 10pt;
        color: #666;
    }
    @bottom-center {
        content: "Page " counter(page);
        font-family: 'Times New Roman', serif;
        font-size: 10pt;
        color: #666;
    }
}

/* Color Variables */
:root {
    --primary-blue: #1e3a8a;
    --secondary-blue: #3b82f6;
    --accent-gold: #f59e0b;
    --text-dark: #1f2937;
    --text-light: #6b7280;
    --border-light: #e5e7eb;
    --success-green: #10b981;
    --warning-red: #ef4444;
}

/* Base Typography */
body {
    font-family: 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.4;
    color: var(--text-dark);
    margin: 0;
    padding: 0;
}

h1, h2, h3, h4, h5, h6 {
    font-family: Arial, sans-serif;
    font-weight: bold;
    margin-top: 0;
    margin-bottom: 12pt;
}

h1 { font-size: 24pt; color: var(--primary-blue); }
h2 { font-size: 18pt; color: var(--primary-blue); }
h3 { font-size: 14pt; color: var(--secondary-blue); }

/* Page Breaks */
.page-break {
    page-break-before: always;
}

/* Cover Page */
.cover-page {
    height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    text-align: center;
    background: linear-gradient(135deg, var(--primary-blue) 0%, var(--secondary-blue) 100%);
    color: white;
    padding: 2in;
    margin: -0.75in;
}

.header .logo {
    font-size: 36pt;
    font-weight: bold;
    margin-bottom: 8pt;
}

.header .tagline {
    font-size: 14pt;
    font-style: italic;
    opacity: 0.9;
}

.cover-content {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.report-title {
    font-size: 32pt;
    font-weight: bold;
    margin-bottom: 16pt;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.report-subtitle {
    font-size: 16pt;
    margin-bottom: 32pt;
    opacity: 0.9;
}

.key-metrics-summary {
    background: rgba(255,255,255,0.1);
    border-radius: 8px;
    padding: 24pt;
    margin: 24pt 0;
}

.metric-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8pt;
    font-size: 14pt;
}

.metric-label {
    font-weight: bold;
}

.recommendation.buy { color: var(--success-green); }
.recommendation.sell { color: var(--warning-red); }
.recommendation.hold { color: var(--accent-gold); }

.cover-footer {
    font-size: 12pt;
    opacity: 0.8;
}

/* Table of Contents */
.toc-page {
    padding-top: 1in;
}

.toc-list {
    margin-top: 24pt;
}

.toc-item {
    display: flex;
    align-items: baseline;
    margin-bottom: 12pt;
    font-size: 12pt;
}

.toc-title {
    font-weight: bold;
}

.toc-dots {
    flex-grow: 1;
    border-bottom: 1px dotted var(--text-light);
    margin: 0 8pt;
    height: 1px;
}

.toc-page {
    font-weight: bold;
}

/* Report Sections */
.report-section {
    margin-bottom: 32pt;
}

.section-header {
    margin-bottom: 24pt;
}

.section-title {
    color: var(--primary-blue);
    border-bottom: 2px solid var(--primary-blue);
    padding-bottom: 8pt;
}

.section-divider {
    height: 2px;
    background: linear-gradient(to right, var(--primary-blue), transparent);
    margin-top: 8pt;
}

/* Executive Summary Metrics */
.executive-summary-metrics {
    background: #f8fafc;
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 16pt;
    margin-bottom: 24pt;
}

.metrics-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 16pt;
}

.metric-card {
    text-align: center;
    padding: 12pt;
    background: white;
    border-radius: 4px;
    border: 1px solid var(--border-light);
}

.metric-card .metric-label {
    font-size: 10pt;
    color: var(--text-light);
    text-transform: uppercase;
    font-weight: bold;
    margin-bottom: 4pt;
}

.metric-card .metric-value {
    font-size: 18pt;
    font-weight: bold;
    color: var(--text-dark);
}

.metric-card .metric-value.recommendation.buy {
    color: var(--success-green);
}

.metric-card .metric-value.price-target {
    color: var(--secondary-blue);
}

/* Content Formatting */
.section-content {
    margin-bottom: 16pt;
    text-align: justify;
}

.subsection {
    margin-bottom: 16pt;
}

.subsection-title {
    color: var(--secondary-blue);
    font-size: 12pt;
    margin-bottom: 8pt;
    border-left: 3px solid var(--secondary-blue);
    padding-left: 8pt;
}

.subsection-content {
    margin-left: 11pt;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 16pt 0;
    font-size: 10pt;
}

th, td {
    border: 1px solid var(--border-light);
    padding: 6pt 8pt;
    text-align: left;
}

th {
    background: var(--primary-blue);
    color: white;
    font-weight: bold;
}

tr:nth-child(even) {
    background: #f8fafc;
}

/* Lists */
ul, ol {
    margin: 8pt 0;
    padding-left: 20pt;
}

li {
    margin-bottom: 4pt;
}

/* Footer */
.report-footer {
    margin-top: 32pt;
    padding-top: 16pt;
    border-top: 2px solid var(--primary-blue);
}

.footer-content {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8pt;
    font-size: 10pt;
}

.footer-disclaimer {
    font-size: 9pt;
    color: var(--text-light);
    text-align: justify;
}

/* Print Optimizations */
@media print {
    .page-break {
        page-break-before: always;
    }
    
    .cover-page {
        page-break-after: always;
    }
    
    .toc-page {
        page-break-after: always;
    }
}

/* Utility Classes */
.text-center { text-align: center; }
.text-right { text-align: right; }
.font-bold { font-weight: bold; }
.text-blue { color: var(--primary-blue); }
.text-green { color: var(--success-green); }
.text-red { color: var(--warning-red); }
'''
        
        css_path = self.css_dir / "report-styles.css"
        with open(css_path, 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def generate_pdf(self, report_data: Dict[str, Any], output_path: str) -> str:
        """Generate professional PDF from report data"""
        try:
            # Clean and structure the report data
            cleaned_data = self.content_cleaner.clean_report(report_data)
            
            # Load and render template
            template = self.jinja_env.get_template('stock_report.html')
            html_content = template.render(**cleaned_data)
            
            # Create temporary HTML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_html:
                temp_html.write(html_content)
                temp_html_path = temp_html.name
            
            try:
                # Generate PDF with WeasyPrint
                css_path = str(self.css_dir / "report-styles.css")
                HTML(filename=temp_html_path).write_pdf(
                    output_path,
                    stylesheets=[CSS(filename=css_path)]
                )
                
                return output_path
                
            finally:
                # Clean up temporary file
                os.unlink(temp_html_path)
                
        except Exception as e:
            raise Exception(f"PDF generation failed: {str(e)}")


# Integration function to replace the awful ReportLab implementation
def generate_professional_pdf(ticker: str, report_data: Dict[str, Any], output_path: str = None) -> str:
    """
    Generate professional institutional-quality PDF report
    
    Args:
        ticker: Stock ticker symbol
        report_data: Report data structure with sections
        output_path: Output file path (optional)
    
    Returns:
        Path to generated PDF file
    """
    if output_path is None:
        output_path = f"/mnt/c/kiro/MarketMind_Report_{ticker}_Professional.pdf"
    
    generator = ProfessionalPDFGenerator()
    return generator.generate_pdf(report_data, output_path)


if __name__ == "__main__":
    # Test with GOOGL report data
    import requests
    
    try:
        # Get the GOOGL report data
        response = requests.get("http://localhost:8000/api/v1/reports/prod_report_GOOGL_1769350746")
        if response.status_code == 200:
            report_data = response.json()
            
            # Generate professional PDF
            output_path = generate_professional_pdf("GOOGL", report_data)
            print(f"✅ Professional PDF generated: {output_path}")
            
            # Check file size
            import os
            file_size = os.path.getsize(output_path)
            print(f"📄 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
        else:
            print(f"❌ Failed to get report data: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
