#!/usr/bin/env python3
"""
ULTRA-SYSTEMATIC FORMATTING SOLUTION
Complete redesign of content formatting system
"""

import re
import json
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path

class ReportFormatter:
    """
    Ultra-systematic report formatter
    Single source of truth for all content formatting
    """
    
    def __init__(self):
        self.css_styles = self._load_institutional_styles()
        self.html_template = self._load_html_template()
    
    def process_report_json(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert raw JSON report to fully formatted content
        Returns both HTML and styled content for PDF
        """
        
        # Step 1: Clean raw content (remove line numbers, etc.)
        cleaned_data = self._clean_raw_content(report_data)
        
        # Step 2: Apply markdown-style formatting
        formatted_data = self._apply_markdown_formatting(cleaned_data)
        
        # Step 3: Generate HTML for frontend
        html_content = self._generate_html_content(formatted_data)
        
        # Step 4: Generate styled content for PDF
        pdf_content = self._generate_pdf_content(formatted_data)
        
        return {
            'raw_data': cleaned_data,
            'html_content': html_content,
            'pdf_content': pdf_content,
            'metadata': {
                'formatted_at': datetime.utcnow().isoformat(),
                'formatter_version': '2.0.0'
            }
        }
    
    def _clean_raw_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove AI artifacts and line numbers"""
        
        def clean_text(text: str) -> str:
            if not isinstance(text, str):
                return text
            
            # Remove line numbers and AI artifacts
            patterns = [
                r'\+ \d+:\s*\+ \d+:\s*',  # "+ 206: + 207:"
                r'\+ \d+:\s*-\s*',        # "+ 208: -"
                r'\+ \d+:\s*',            # "+ 209:"
                r'^\s*\d+:\s*\+\s*',      # "210: +"
                r'━{3,}',                 # Multiple dashes
                r'■{3,}',                 # Multiple bullets
            ]
            
            for pattern in patterns:
                text = re.sub(pattern, '', text, flags=re.MULTILINE)
            
            return text.strip()
        
        def process_dict(obj):
            if isinstance(obj, dict):
                return {k: process_dict(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [process_dict(item) for item in obj]
            elif isinstance(obj, str):
                return clean_text(obj)
            return obj
        
        return process_dict(data)
    
    def _apply_markdown_formatting(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply markdown-style formatting to content"""
        
        def format_text(text: str) -> str:
            if not isinstance(text, str):
                return text
            
            # Apply markdown-style formatting
            formatting_rules = [
                # Headers
                (r'^## (.+)$', r'<h2 class="report-h2">\1</h2>'),
                (r'^### (.+)$', r'<h3 class="report-h3">\1</h3>'),
                (r'^#### (.+)$', r'<h4 class="report-h4">\1</h4>'),
                
                # Bold text
                (r'\*\*(.+?)\*\*', r'<strong class="report-bold">\1</strong>'),
                
                # Investment ratings
                (r'Rating: (BUY|SELL|HOLD)', r'<span class="rating-badge rating-\1">\1</span>'),
                
                # Price targets
                (r'Price Target: \$([0-9,]+\.?[0-9]*)', r'<span class="price-target">Price Target: $\1</span>'),
                
                # Percentages
                (r'([0-9]+\.?[0-9]*%)', r'<span class="percentage">\1</span>'),
                
                # Dollar amounts
                (r'\$([0-9,]+\.?[0-9]*[BMK]?)', r'<span class="currency">$\1</span>'),
                
                # Bullet points
                (r'^- (.+)$', r'<li class="report-bullet">\1</li>'),
                
                # Line breaks
                (r'\n\n', '</p><p class="report-paragraph">'),
            ]
            
            # Wrap in paragraph
            formatted = f'<p class="report-paragraph">{text}</p>'
            
            # Apply formatting rules
            for pattern, replacement in formatting_rules:
                formatted = re.sub(pattern, replacement, formatted, flags=re.MULTILINE)
            
            # Wrap bullet points in lists
            if '<li class="report-bullet">' in formatted:
                formatted = re.sub(
                    r'(<li class="report-bullet">.*?</li>)',
                    r'<ul class="report-list">\1</ul>',
                    formatted,
                    flags=re.DOTALL
                )
            
            return formatted
        
        def process_content(obj):
            if isinstance(obj, dict):
                processed = {}
                for k, v in obj.items():
                    if k == 'content' and isinstance(v, str):
                        processed[k] = format_text(v)
                        processed[f'{k}_formatted'] = True
                    else:
                        processed[k] = process_content(v)
                return processed
            elif isinstance(obj, list):
                return [process_content(item) for item in obj]
            elif isinstance(obj, str) and len(obj) > 100:  # Long text content
                return format_text(obj)
            return obj
        
        return process_content(data)
    
    def _generate_html_content(self, formatted_data: Dict[str, Any]) -> str:
        """Generate complete HTML for frontend display"""
        
        html_sections = []
        
        # Process sections
        if 'sections' in formatted_data:
            for section_id, section_data in formatted_data['sections'].items():
                if isinstance(section_data, dict) and 'content' in section_data:
                    title = section_data.get('title', section_id.replace('_', ' ').title())
                    content = section_data['content']
                    
                    section_html = f'''
                    <div class="report-section" id="{section_id}">
                        <h2 class="section-title">{title}</h2>
                        <div class="section-content">
                            {content}
                        </div>
                    </div>
                    '''
                    html_sections.append(section_html)
        
        # Combine all sections
        full_html = f'''
        <div class="report-container">
            <div class="report-header">
                <h1 class="report-title">{formatted_data.get('symbol', 'Stock')} - Investment Analysis Report</h1>
                <div class="report-meta">
                    Generated: {datetime.now().strftime('%B %d, %Y')}
                </div>
            </div>
            <div class="report-body">
                {''.join(html_sections)}
            </div>
        </div>
        '''
        
        return full_html
    
    def _generate_pdf_content(self, formatted_data: Dict[str, Any]) -> str:
        """Generate styled content for PDF generation"""
        
        # Similar to HTML but with PDF-specific styling
        pdf_sections = []
        
        if 'sections' in formatted_data:
            for section_id, section_data in formatted_data['sections'].items():
                if isinstance(section_data, dict) and 'content' in section_data:
                    title = section_data.get('title', section_id.replace('_', ' ').title())
                    content = section_data['content']
                    
                    # Convert HTML classes to PDF-friendly styles
                    pdf_content = content.replace('class="', 'style="')
                    
                    section_pdf = f'''
                    <div class="pdf-section">
                        <h2 class="pdf-section-title">{title}</h2>
                        <div class="pdf-section-content">
                            {pdf_content}
                        </div>
                    </div>
                    '''
                    pdf_sections.append(section_pdf)
        
        return ''.join(pdf_sections)
    
    def _load_institutional_styles(self) -> str:
        """Load professional institutional CSS styles"""
        return '''
        .report-container {
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            color: #1a1a1a;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        .report-title {
            font-size: 28px;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .section-title {
            font-size: 22px;
            font-weight: bold;
            color: #1a1a1a;
            margin: 30px 0 15px 0;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 5px;
        }
        
        .report-paragraph {
            font-size: 16px;
            color: #1a1a1a;
            margin-bottom: 15px;
            line-height: 1.6;
        }
        
        .report-h2 {
            font-size: 20px;
            font-weight: bold;
            color: #1a1a1a;
            margin: 25px 0 10px 0;
        }
        
        .report-h3 {
            font-size: 18px;
            font-weight: bold;
            color: #1a1a1a;
            margin: 20px 0 8px 0;
        }
        
        .report-bold {
            font-weight: bold;
            color: #1a1a1a;
        }
        
        .rating-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 14px;
        }
        
        .rating-BUY {
            background-color: #10b981;
            color: white;
        }
        
        .rating-HOLD {
            background-color: #f59e0b;
            color: white;
        }
        
        .rating-SELL {
            background-color: #ef4444;
            color: white;
        }
        
        .price-target {
            font-weight: bold;
            color: #2563eb;
        }
        
        .percentage {
            font-weight: bold;
            color: #059669;
        }
        
        .currency {
            font-weight: bold;
            color: #059669;
        }
        
        .report-list {
            margin: 15px 0;
            padding-left: 20px;
        }
        
        .report-bullet {
            margin-bottom: 8px;
            color: #1a1a1a;
        }
        '''
    
    def _load_html_template(self) -> str:
        """Load HTML template for complete page"""
        return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>{styles}</style>
        </head>
        <body>
            {content}
        </body>
        </html>
        '''

# Test the new formatter
if __name__ == "__main__":
    formatter = ReportFormatter()
    
    # Test data
    test_data = {
        'symbol': 'MSFT',
        'sections': {
            'executive_summary': {
                'title': 'Executive Summary',
                'content': '''## Investment Recommendation: **BUY**

Price Target: $420.00 | Current Price: $380.50 | Upside Potential: 10.4%

### Key Investment Thesis
Microsoft represents a compelling investment opportunity driven by:

- **Cloud Leadership**: Azure growing 30%+ annually
- **AI Integration**: Copilot driving productivity gains  
- **Subscription Model**: Recurring revenue stability

Rating: BUY with 12-month target of $420.00'''
            }
        }
    }
    
    print("🧪 Testing Ultra-Systematic Formatter...")
    result = formatter.process_report_json(test_data)
    
    print("✅ HTML Content Generated:")
    print(result['html_content'][:500] + "...")
    
    print("\n✅ PDF Content Generated:")
    print(result['pdf_content'][:300] + "...")
