#!/usr/bin/env python3
"""
Content Cleaner Utility - Remove line numbers and AI artifacts from generated content
"""

import re

def clean_ai_content(content: str) -> str:
    """Clean AI-generated content by removing line numbers and artifacts"""
    if not content:
        return ""
    
    # Remove line number patterns
    content = re.sub(r'\+ \d+:\s*\+ \d+:\s*', '', content)  # "+ 206: + 207:"
    content = re.sub(r'\+ \d+:\s*-\s*', '- ', content)  # "+ 208: -" becomes "-"
    content = re.sub(r'\+ \d+:\s*', '', content)  # Any "+ number:"
    content = re.sub(r'^\s*\d+:\s*\+\s*\d+:\s*', '', content, flags=re.MULTILINE)
    content = re.sub(r'^\s*\d+:\s*\+\s*', '', content, flags=re.MULTILINE)
    
    # Remove AI system messages
    content = re.sub(r'Invoking \d+ subagents in parallel \(using tool: [^)]+\)', '', content)
    content = re.sub(r'Searching the web for: [^\n]+\(using tool: web_search\)', '', content)
    content = re.sub(r'using tool: [^\n]+', '', content)
    content = re.sub(r'> I\'ll [^\n]+', '', content)
    content = re.sub(r'> [^\n]*', '', content, flags=re.MULTILINE)
    
    # Clean up spacing
    content = re.sub(r'\n{3,}', '\n\n', content)  # Multiple newlines to double
    content = re.sub(r'[ \t]+', ' ', content)  # Multiple spaces to single
    content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)  # Leading whitespace
    content = re.sub(r'\s+$', '', content, flags=re.MULTILINE)  # Trailing whitespace
    
    return content.strip()

if __name__ == "__main__":
    # Test the cleaner
    test_content = """+ 206: + 207: Asset Turnover Analysis: + 208: - Asset Turnover: 1.05x + 209: - Inventory Turnover: 59.3x + 210: - Receivables Turnover: 13.1x + 211: - Payables Turnover: 6.2x + 212: + 213: Supply Chain Efficiency: + 214: - Inventory Days: 6 days (industry-leading) + 215: - Cash Conversion Cycle: -25 days + 216: - Supplier Payment Terms: 59 days average + 217: + 218:"""
    
    print("BEFORE:")
    print(test_content)
    print("\n" + "="*50 + "\n")
    print("AFTER:")
    print(clean_ai_content(test_content))
