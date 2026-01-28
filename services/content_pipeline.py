#!/usr/bin/env python3
"""
MarketMind Pro - Content Pipeline System
Systematic approach to clean content at every stage
"""

import re
from typing import Dict, Any, List
from pathlib import Path

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
        ]
    
    def format_content(self, content: str) -> str:
        """Apply all formatting rules to content"""
        if not content:
            return ""
        
        # Start with paragraph wrapper with explicit text color
        formatted = f'<div class="prose max-w-none text-gray-900" style="color: #1f2937;"><p class="mb-4 text-gray-700 leading-relaxed" style="color: #374151;">{content}</p></div>'
        
        # Apply all formatting rules
        for pattern, replacement in self.formatting_rules:
            formatted = re.sub(pattern, replacement, formatted, flags=re.MULTILINE)
        
        return formatted

class ContentPipeline:
    """Centralized content processing pipeline"""
    
    def __init__(self):
        self.cleaning_rules = [
            # Line number patterns (the main issue)
            (r'\+ \d+:\s*\+ \d+:\s*', ''),
            (r'\+ \d+:\s*-\s*', '- '),
            (r'\+ \d+:\s*', ''),
            (r'^\s*\d+:\s*\+\s*\d+:\s*', ''),
            (r'^\s*\d+:\s*\+\s*', ''),
            
            # AI system messages
            (r'Invoking \d+ subagents.*?\)', ''),
            (r'Searching the web for:.*?\)', ''),
            (r'using tool: [^\n]+', ''),
            (r'> I\'ll [^\n]+', ''),
            (r'> [^\n]*', ''),
            
            # Formatting cleanup
            (r'\n{3,}', '\n\n'),
            (r'[ \t]+', ' '),
            (r'^\s+', ''),
            (r'\s+$', ''),
        ]
    
    def clean_content(self, content: str) -> str:
        """Apply all cleaning rules systematically"""
        if not content:
            return ""
        
        for pattern, replacement in self.cleaning_rules:
            content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
        
        return content.strip()
    
    def process_report_data(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Clean all content in report data structure"""
        cleaned_data = {}
        
        for key, value in report_data.items():
            if isinstance(value, str):
                cleaned_data[key] = self.clean_content(value)
            elif isinstance(value, dict):
                cleaned_data[key] = self.process_report_data(value)
            elif isinstance(value, list):
                cleaned_data[key] = [
                    self.clean_content(item) if isinstance(item, str) 
                    else self.process_report_data(item) if isinstance(item, dict)
                    else item
                    for item in value
                ]
            else:
                cleaned_data[key] = value
        
        return cleaned_data

# Global pipeline instance
CONTENT_PIPELINE = ContentPipeline()

def clean_ai_content(content: str) -> str:
    """Global function for cleaning AI-generated content"""
    return CONTENT_PIPELINE.clean_content(content)

def clean_report_data(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """Global function for cleaning and formatting report data"""
    pipeline = ContentPipeline()
    formatter = ContentFormatter()
    
    def process_content(content):
        if isinstance(content, str):
            cleaned = pipeline.clean_content(content)
            return {
                'content': cleaned,
                'html_content': formatter.format_content(cleaned)
            }
        return content
    
    def process_data(data):
        if isinstance(data, dict):
            processed = {}
            for key, value in data.items():
                if key == 'content' and isinstance(value, str):
                    # Process content fields specially
                    cleaned = pipeline.clean_content(value)
                    processed[key] = cleaned
                    processed['html_content'] = formatter.format_content(cleaned)
                elif isinstance(value, str) and len(value) > 100:  # Likely content
                    cleaned = pipeline.clean_content(value)
                    processed[key] = cleaned
                    processed[f'{key}_html'] = formatter.format_content(cleaned)
                elif isinstance(value, (dict, list)):
                    processed[key] = process_data(value)
                else:
                    processed[key] = value
            return processed
        elif isinstance(data, list):
            return [process_data(item) for item in data]
        else:
            return data
    
    return process_data(report_data)

if __name__ == "__main__":
    # Test the pipeline
    test_content = """+ 206: + 207: Asset Turnover Analysis: + 208: - Asset Turnover: 1.05x + 209: - Inventory Turnover: 59.3x"""
    print("BEFORE:", repr(test_content))
    print("AFTER:", repr(clean_ai_content(test_content)))
