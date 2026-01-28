#!/usr/bin/env python3
"""
SYSTEMATIC DISPLAY & FORMATTING FIX
Fix frontend display and add proper formatting to both PDF and frontend
"""

import re
from typing import Dict, Any

class ContentFormatter:
    """Enhanced content formatter for both frontend and PDF display"""
    
    def __init__(self):
        self.formatting_rules = [
            # Headers
            (r'^## (.+)$', r'<h2 class="text-2xl font-bold text-gray-900 mb-4 border-b-2 border-blue-500 pb-2">\1</h2>'),
            (r'^### (.+)$', r'<h3 class="text-xl font-semibold text-gray-800 mb-3">\1</h3>'),
            (r'^#### (.+)$', r'<h4 class="text-lg font-medium text-gray-700 mb-2">\1</h4>'),
            
            # Bold text
            (r'\*\*(.+?)\*\*', r'<strong class="font-bold text-gray-900">\1</strong>'),
            
            # Bullet points
            (r'^- (.+)$', r'<li class="ml-4 mb-1 text-gray-700">• \1</li>'),
            
            # Tables (simple markdown tables)
            (r'\|(.+)\|', self._format_table_row),
            
            # Investment ratings
            (r'Rating: (BUY|SELL|HOLD)', r'<span class="inline-block px-3 py-1 rounded-full text-sm font-semibold bg-green-100 text-green-800">Rating: \1</span>'),
            
            # Price targets
            (r'Price Target: \$([0-9,]+\.?[0-9]*)', r'<span class="inline-block px-3 py-1 rounded-full text-sm font-semibold bg-blue-100 text-blue-800">Price Target: $\1</span>'),
            
            # Percentages
            (r'([0-9]+\.?[0-9]*%)', r'<span class="font-medium text-blue-600">\1</span>'),
            
            # Dollar amounts
            (r'\$([0-9,]+\.?[0-9]*[BMK]?)', r'<span class="font-medium text-green-600">$\1</span>'),
            
            # Line breaks and paragraphs
            (r'\n\n', '</p><p class="mb-4 text-gray-700 leading-relaxed">'),
            (r'^\s*$', ''),  # Remove empty lines
        ]
    
    def _format_table_row(self, match):
        """Format markdown table rows to HTML"""
        cells = [cell.strip() for cell in match.group(1).split('|')]
        if len(cells) < 2:
            return match.group(0)
        
        html_cells = []
        for cell in cells:
            if cell.strip():
                html_cells.append(f'<td class="px-4 py-2 border-b border-gray-200 text-sm">{cell}</td>')
        
        return f'<tr>{"".join(html_cells)}</tr>'
    
    def format_content(self, content: str) -> str:
        """Apply all formatting rules to content"""
        if not content:
            return ""
        
        # Start with paragraph wrapper
        formatted = f'<div class="prose max-w-none"><p class="mb-4 text-gray-700 leading-relaxed">{content}</p></div>'
        
        # Apply all formatting rules
        for pattern, replacement in self.formatting_rules:
            if callable(replacement):
                formatted = re.sub(pattern, replacement, formatted, flags=re.MULTILINE)
            else:
                formatted = re.sub(pattern, replacement, formatted, flags=re.MULTILINE)
        
        # Wrap tables
        if '<tr>' in formatted:
            formatted = re.sub(r'(<tr>.*?</tr>)', r'<table class="min-w-full bg-white border border-gray-200 rounded-lg overflow-hidden mb-4">\1</table>', formatted, flags=re.DOTALL)
        
        return formatted
    
    def format_report_data(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format entire report data structure"""
        if not report_data:
            return report_data
        
        # Format sections
        if 'sections' in report_data:
            for section_key, section_data in report_data['sections'].items():
                if isinstance(section_data, dict) and 'content' in section_data:
                    # Format the content
                    section_data['content'] = self.format_content(section_data['content'])
                    # Add formatted HTML version
                    section_data['html_content'] = section_data['content']
        
        # Format executive summary
        if 'executive_summary' in report_data:
            if isinstance(report_data['executive_summary'], str):
                report_data['executive_summary'] = self.format_content(report_data['executive_summary'])
            elif isinstance(report_data['executive_summary'], dict) and 'content' in report_data['executive_summary']:
                report_data['executive_summary']['content'] = self.format_content(report_data['executive_summary']['content'])
                report_data['executive_summary']['html_content'] = report_data['executive_summary']['content']
        
        return report_data

def test_formatter():
    """Test the content formatter"""
    formatter = ContentFormatter()
    
    test_content = """## Investment Recommendation: BUY
Price Target: $195.00 | Current Price: ~$178.50 | Upside Potential: 9.2%

### Key Investment Thesis
Alphabet Inc. represents a compelling investment opportunity driven by:

- **AI Integration**: Gemini AI rollout across Google services
- **Cloud Acceleration**: Google Cloud Platform gaining market share with 35%+ growth
- **YouTube Monetization**: Shorts and Connected TV driving revenue

### Financial Metrics
| Metric | Current | Target | Growth |
|--------|---------|--------|--------|
| Revenue | $307.4B | $340.2B | +10.7% |
| Operating Margin | 28.3% | 30.1% | +180 bps |

**Rating: BUY** with 12-month **Price Target: $195.00**"""

    formatted = formatter.format_content(test_content)
    print("✅ Formatted Content Preview:")
    print(formatted[:500] + "...")
    
    return formatted

if __name__ == "__main__":
    test_formatter()
