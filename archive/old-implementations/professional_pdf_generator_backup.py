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
            r'> [^\n]*',  # Remove all > prefixed lines
            r'\d+: \+ \d+:',  # Line numbers like "192: + 193:"
            r'■{3,}',  # Multiple bullet symbols
            r'━{3,}',  # Multiple dash symbols
            r'References:\s*\[\d+\][^\n]*\n',  # Reference citations
            r'\[.*?\]\(.*?\)',  # Markdown links
            r'```[^`]*```',  # Code blocks
            r'`[^`]+`',  # Inline code
            r'^\s*\|.*\|\s*$',  # Table rows with pipes
            r'^\s*\|[-\s:]+\|\s*$',  # Table separator rows
            r'^\s*[-=]{3,}\s*$',  # Horizontal rules
            r'^\s*\*\s*\*\s*\*\s*$',  # Asterisk separators
        ]
    
    def clean_content(self, content: str) -> str:
        """Remove AI artifacts and clean formatting"""
        if not content:
            return ""
        
        # Remove AI system messages first
        for pattern in self.removal_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE | re.IGNORECASE)
        
        # Remove lines starting with > (AI messages)
        content = re.sub(r'^>\s*.*$', '', content, flags=re.MULTILINE)
        
        # Clean markdown headers - remove # symbols but keep the text
        content = re.sub(r'^#{1,6}\s+(.+)$', r'\1', content, flags=re.MULTILINE)
        
        # Clean markdown formatting
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)  # Bold
        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)  # Italic
        content = re.sub(r'__(.+?)__', r'<strong>\1</strong>', content)  # Alternative bold
        content = re.sub(r'_(.+?)_', r'<em>\1</em>', content)  # Alternative italic
        
        # Clean bullet points - standardize to HTML bullets
        content = re.sub(r'^\s*[-•*]\s+', '• ', content, flags=re.MULTILINE)
        content = re.sub(r'^\s*\d+\.\s+', '• ', content, flags=re.MULTILINE)  # Convert numbered lists
        
        # Remove raw markdown table formatting
        lines = content.split('\n')
        cleaned_lines = []
        for line in lines:
            # Skip table separator lines and empty table rows
            if re.match(r'^\s*\|[-\s:]+\|\s*$', line) or re.match(r'^\s*\|\s*\|\s*$', line):
                continue
            # Convert table rows to simple text
            if '|' in line and line.count('|') >= 2:
                # Extract table cell content
                cells = [cell.strip() for cell in line.split('|')[1:-1]]
                if any(cell for cell in cells):  # Only if there's actual content
                    cleaned_lines.append(' | '.join(cells))
            else:
                cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
        
        # Clean up spacing and formatting
        content = re.sub(r'\n{3,}', '\n\n', content)  # Multiple newlines to double
        content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single
        content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)  # Leading whitespace
        content = re.sub(r'\s+$', '', content, flags=re.MULTILINE)  # Trailing whitespace
        
        # Remove empty lines at start and end
        content = content.strip()
        
        return content
    
    def convert_markdown_tables(self, content: str) -> str:
        """Convert markdown tables to HTML tables"""
        if not content or '|' not in content:
            return content
        
        lines = content.split('\n')
        result_lines = []
        in_table = False
        table_rows = []
        
        for line in lines:
            stripped = line.strip()
            
            # Check if this line looks like a table row
            if '|' in stripped and stripped.count('|') >= 2:
                if not in_table:
                    in_table = True
                    table_rows = []
                
                # Clean up the row
                cells = [cell.strip() for cell in stripped.split('|')]
                # Remove empty cells at start/end
                if cells and not cells[0]:
                    cells = cells[1:]
                if cells and not cells[-1]:
                    cells = cells[:-1]
                
                # Skip separator rows (like |---|---|)
                if cells and all(re.match(r'^-+$', cell.strip()) for cell in cells if cell.strip()):
                    continue
                
                table_rows.append(cells)
            else:
                # End of table
                if in_table and table_rows:
                    result_lines.append(self._create_html_table(table_rows))
                    table_rows = []
                    in_table = False
                
                result_lines.append(line)
        
        # Handle table at end of content
        if in_table and table_rows:
            result_lines.append(self._create_html_table(table_rows))
        
        return '\n'.join(result_lines)
    
    def _create_html_table(self, rows: List[List[str]]) -> str:
        """Create HTML table from rows"""
        if not rows:
            return ""
        
        html = ['<table class="data-table">']
        
        # First row as header
        if rows:
            html.append('  <thead>')
            html.append('    <tr>')
            for cell in rows[0]:
                html.append(f'      <th>{cell}</th>')
            html.append('    </tr>')
            html.append('  </thead>')
        
        # Remaining rows as body
        if len(rows) > 1:
            html.append('  <tbody>')
            for row in rows[1:]:
                html.append('    <tr>')
                for cell in row:
                    html.append(f'      <td>{cell}</td>')
                html.append('    </tr>')
            html.append('  </tbody>')
        
        html.append('</table>')
        return '\n'.join(html)
    
    def format_paragraphs(self, content: str) -> str:
        """Format content into proper paragraphs"""
        if not content:
            return ""
        
        # Split into paragraphs (double newlines)
        paragraphs = re.split(r'\n\s*\n', content)
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Check if it's a list item
            if re.match(r'^[•\-\*]\s+', para):
                # Handle lists
                list_items = []
                for line in para.split('\n'):
                    line = line.strip()
                    if re.match(r'^[•\-\*]\s+', line):
                        item = re.sub(r'^[•\-\*]\s+', '', line)
                        list_items.append(f'  <li>{item}</li>')
                
                if list_items:
                    formatted_paragraphs.append('<ul>')
                    formatted_paragraphs.extend(list_items)
                    formatted_paragraphs.append('</ul>')
            else:
                # Regular paragraph
                # Replace single newlines with spaces, but preserve intentional breaks
                para = re.sub(r'\n(?!\s*[•\-\*])', ' ', para)
                formatted_paragraphs.append(f'<p>{para}</p>')
        
        return '\n'.join(formatted_paragraphs)
    
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
            structured['content'] = self._format_paragraphs(parts[0].strip())
            for part in parts[1:]:
                if part.strip():
                    lines = part.strip().split('\n', 1)
                    sub_title = lines[0].strip()
                    sub_content = lines[1] if len(lines) > 1 else ""
                    structured['subsections'].append({
                        'title': sub_title,
                        'content': self._format_paragraphs(sub_content.strip())
                    })
        else:
            structured['content'] = self._format_paragraphs(content)
        
        return structured
    
    def _format_paragraphs(self, content: str) -> str:
        """Format content into proper paragraphs with consistent spacing"""
        if not content:
            return ""
        
        # Split into paragraphs (double newlines or bullet points)
        paragraphs = re.split(r'\n\s*\n', content)
        formatted_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
                
            # Handle bullet point lists
            if '•' in para:
                lines = para.split('\n')
                bullet_items = []
                current_item = ""
                
                for line in lines:
                    line = line.strip()
                    if line.startswith('•'):
                        if current_item:
                            bullet_items.append(current_item.strip())
                        current_item = line[1:].strip()  # Remove bullet
                    else:
                        current_item += " " + line
                
                if current_item:
                    bullet_items.append(current_item.strip())
                
                if bullet_items:
                    formatted_list = '<ul>' + ''.join(f'<li>{item}</li>' for item in bullet_items) + '</ul>'
                    formatted_paragraphs.append(formatted_list)
            else:
                # Regular paragraph - ensure proper spacing
                para = re.sub(r'\s+', ' ', para)  # Normalize whitespace
                formatted_paragraphs.append(f'<p>{para}</p>')
        
        return '\n\n'.join(formatted_paragraphs)
    
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
        
        # Add custom filters
        self.jinja_env.filters['format_content'] = self._format_content_filter
        
        self._create_template()
        self._create_css()
    
    def _format_content_filter(self, content: str) -> str:
        """Jinja2 filter for formatting content with tables and paragraphs"""
        if not content:
            return ""
        
        # Convert markdown tables to HTML
        content = self.content_cleaner.convert_markdown_tables(content)
        
        # Format paragraphs
        content = self.content_cleaner.format_paragraphs(content)
        
        return content
    
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
            {{ section.content | safe }}
        </div>
        
        {% if section.subsections %}
        {% for subsection in section.subsections %}
        <div class="subsection">
            <h3 class="subsection-title">{{ subsection.title }}</h3>
            <div class="subsection-content">
                {{ subsection.content | safe }}
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
    margin: 1in 0.75in 1.25in 0.75in;
    @top-center {
        content: "MarketMind Pro - Institutional Research";
        font-family: Arial, sans-serif;
        font-size: 9pt;
        color: #666;
        margin-bottom: 0.25in;
    }
    @bottom-center {
        content: "Page " counter(page) " of " counter(pages);
        font-family: Arial, sans-serif;
        font-size: 9pt;
        color: #666;
        margin-top: 0.25in;
    }
}

@page:first {
    @top-center { content: none; }
    @bottom-center { content: none; }
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
    --background-light: #f8fafc;
}

/* Base Typography */
body {
    font-family: 'Times New Roman', serif;
    font-size: 11pt;
    line-height: 1.6;
    color: var(--text-dark);
    margin: 0;
    padding: 0;
}

p {
    margin: 0 0 12pt 0;
    text-align: justify;
    orphans: 2;
    widows: 2;
}

h1, h2, h3, h4, h5, h6 {
    font-family: Arial, sans-serif;
    font-weight: bold;
    margin: 18pt 0 12pt 0;
    page-break-after: avoid;
    orphans: 3;
    widows: 3;
}

h1 { 
    font-size: 24pt; 
    color: var(--primary-blue);
    line-height: 1.2;
}
h2 { 
    font-size: 18pt; 
    color: var(--primary-blue);
    line-height: 1.3;
}
h3 { 
    font-size: 14pt; 
    color: var(--secondary-blue);
    line-height: 1.4;
}

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
    margin: -1in -0.75in -1.25in -0.75in;
    page-break-after: always;
}

.header .logo {
    font-size: 36pt;
    font-weight: bold;
    margin-bottom: 8pt;
    font-family: Arial, sans-serif;
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
    line-height: 1.1;
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

.recommendation.buy { color: #22c55e; }
.recommendation.sell { color: #ef4444; }
.recommendation.hold { color: #f59e0b; }

.cover-footer {
    font-size: 12pt;
    opacity: 0.8;
}

/* Table of Contents */
.toc-page {
    padding-top: 0.5in;
    page-break-after: always;
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

/* Report Sections */
.report-section {
    margin-bottom: 32pt;
    page-break-inside: avoid;
}

.section-header {
    margin-bottom: 24pt;
    page-break-after: avoid;
}

.section-title {
    color: var(--primary-blue);
    border-bottom: 2px solid var(--primary-blue);
    padding-bottom: 8pt;
    margin-bottom: 0;
}

.section-divider {
    height: 2px;
    background: linear-gradient(to right, var(--primary-blue), transparent);
    margin-top: 8pt;
}

/* Executive Summary Metrics */
.executive-summary-metrics {
    background: var(--background-light);
    border: 1px solid var(--border-light);
    border-radius: 8px;
    padding: 16pt;
    margin: 0 0 24pt 0;
    page-break-inside: avoid;
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
    display: block;
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
    margin: 0 0 16pt 0;
    text-align: justify;
    line-height: 1.6;
}

.section-content p {
    margin-bottom: 12pt;
    line-height: 1.5;
    text-align: justify;
}

.section-content ul {
    margin: 12pt 0;
    padding-left: 20pt;
    list-style-type: disc;
}

.section-content li {
    margin-bottom: 6pt;
    line-height: 1.4;
    text-align: justify;
}

.subsection {
    margin: 0 0 20pt 0;
    page-break-inside: avoid;
}

.subsection-title {
    color: var(--secondary-blue);
    font-size: 12pt;
    margin: 16pt 0 8pt 0;
    border-left: 3px solid var(--secondary-blue);
    padding-left: 8pt;
    page-break-after: avoid;
}

.subsection-content {
    margin-left: 11pt;
    line-height: 1.6;
}

.subsection-content p {
    margin-bottom: 10pt;
    line-height: 1.4;
    text-align: justify;
}

.subsection-content ul {
    margin: 10pt 0;
    padding-left: 18pt;
    list-style-type: disc;
}

.subsection-content li {
    margin-bottom: 4pt;
    text-align: justify;
}

/* Tables */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 16pt 0;
    font-size: 10pt;
    page-break-inside: avoid;
}

th, td {
    border: 1px solid var(--border-light);
    padding: 8pt 10pt;
    text-align: left;
    vertical-align: top;
}

th {
    background: var(--primary-blue);
    color: white;
    font-weight: bold;
    font-family: Arial, sans-serif;
    page-break-after: avoid;
}

tr:nth-child(even) {
    background: var(--background-light);
}

td {
    line-height: 1.4;
}

/* Numeric columns */
td:last-child,
td.numeric {
    text-align: right;
    font-family: 'Courier New', monospace;
}

/* Data Tables (converted from markdown) */
.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 16pt 0;
    font-size: 10pt;
    border: 2px solid var(--primary-blue);
    page-break-inside: avoid;
}

.data-table th {
    background: var(--primary-blue);
    color: white;
    font-weight: bold;
    padding: 8pt 12pt;
    text-align: center;
    border: 1px solid var(--primary-blue);
    font-family: Arial, sans-serif;
}

.data-table td {
    padding: 8pt 12pt;
    border: 1px solid var(--border-light);
    text-align: left;
    line-height: 1.4;
}

.data-table tbody tr:nth-child(even) {
    background: var(--background-light);
}

.data-table tbody tr:hover {
    background: #e2e8f0;
}

/* Lists */
ul, ol {
    margin: 12pt 0;
    padding-left: 24pt;
}

li {
    margin-bottom: 6pt;
    line-height: 1.5;
}

ul li {
    list-style-type: disc;
}

ol li {
    list-style-type: decimal;
}

/* Nested lists */
ul ul, ol ol, ul ol, ol ul {
    margin: 6pt 0;
}

/* Footer */
.report-footer {
    margin-top: 32pt;
    padding-top: 16pt;
    border-top: 2px solid var(--primary-blue);
    page-break-inside: avoid;
}

.footer-content {
    display: flex;
    justify-content: space-between;
    margin-bottom: 8pt;
    font-size: 10pt;
    font-family: Arial, sans-serif;
}

.footer-disclaimer {
    font-size: 9pt;
    color: var(--text-light);
    text-align: justify;
    line-height: 1.4;
    margin-top: 8pt;
}

/* Strong and emphasis */
strong, b {
    font-weight: bold;
    color: var(--text-dark);
}

em, i {
    font-style: italic;
}

/* Blockquotes */
blockquote {
    margin: 16pt 24pt;
    padding: 12pt 16pt;
    background: var(--background-light);
    border-left: 4px solid var(--secondary-blue);
    font-style: italic;
}

/* Code blocks */
code, pre {
    font-family: 'Courier New', monospace;
    font-size: 10pt;
    background: var(--background-light);
    padding: 2pt 4pt;
    border-radius: 2px;
}

pre {
    padding: 12pt;
    margin: 12pt 0;
    overflow-x: auto;
    white-space: pre-wrap;
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
    
    .report-section {
        page-break-inside: avoid;
    }
    
    .subsection {
        page-break-inside: avoid;
    }
    
    table {
        page-break-inside: avoid;
    }
    
    h1, h2, h3 {
        page-break-after: avoid;
    }
}

/* Utility Classes */
.text-center { text-align: center; }
.text-right { text-align: right; }
.text-left { text-align: left; }
.font-bold { font-weight: bold; }
.text-blue { color: var(--primary-blue); }
.text-green { color: var(--success-green); }
.text-red { color: var(--warning-red); }
.no-break { page-break-inside: avoid; }
.break-before { page-break-before: always; }
.break-after { page-break-after: always; }
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
