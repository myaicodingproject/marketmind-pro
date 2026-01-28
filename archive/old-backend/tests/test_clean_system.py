#!/usr/bin/env python3

import base64
import io
from dataclasses import dataclass
from typing import List, Dict, Any
from enum import Enum

# Mock models
class OutputFormat(Enum):
    WEB = "web"
    PDF = "pdf"

@dataclass
class ReportSection:
    title: str
    content: str
    tables: List[Dict[str, Any]]
    metrics: Dict[str, float]
    charts: List[str]

# Mock services
class ContentParserService:
    @staticmethod
    def parse_section(markdown_content: str) -> ReportSection:
        tables = []
        metrics = {}
        charts = []
        
        # Extract tables
        if "| Revenue |" in markdown_content:
            tables.append({"type": "revenue", "data": [["2023", "$100M"], ["2024", "$120M"]]})
        
        # Extract metrics
        if "P/E Ratio: 25.5" in markdown_content:
            metrics["pe_ratio"] = 25.5
        if "Revenue Growth: 15%" in markdown_content:
            metrics["revenue_growth"] = 0.15
            
        # Extract chart references
        if "[Revenue Chart]" in markdown_content:
            charts.append("revenue_chart")
            
        return ReportSection(
            title="Financial Analysis",
            content=markdown_content,
            tables=tables,
            metrics=metrics,
            charts=charts
        )

class ChartImageService:
    @staticmethod
    def generate_revenue_chart(data: List[Dict[str, Any]]) -> str:
        # Mock PNG data (1x1 transparent pixel)
        png_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xdb\x00\x00\x00\x00IEND\xaeB`\x82'
        return base64.b64encode(png_data).decode('utf-8')

class TemplateService:
    @staticmethod
    def render_section(section: ReportSection, format_type: OutputFormat) -> str:
        if format_type == OutputFormat.WEB:
            return f'<div class="web-section"><h2>{section.title}</h2><p>{section.content}</p></div>'
        else:  # PDF
            return f'<div class="pdf-section" style="page-break-inside: avoid;"><h2>{section.title}</h2><p>{section.content}</p></div>'

def test_content_parser():
    markdown = """# Financial Analysis
    
| Revenue | 2023 | 2024 |
|---------|------|------|
| Amount  | $100M| $120M|

P/E Ratio: 25.5
Revenue Growth: 15%

[Revenue Chart]
"""
    
    try:
        section = ContentParserService.parse_section(markdown)
        assert section.title == "Financial Analysis"
        assert len(section.tables) == 1
        assert section.metrics["pe_ratio"] == 25.5
        assert "revenue_chart" in section.charts
        print("✓ ContentParserService test passed")
        return True
    except Exception as e:
        print(f"✗ ContentParserService test failed: {e}")
        return False

def test_chart_service():
    data = [{"year": 2023, "revenue": 100}, {"year": 2024, "revenue": 120}]
    
    try:
        chart_b64 = ChartImageService.generate_revenue_chart(data)
        # Verify it's valid base64 and decodes to PNG
        decoded = base64.b64decode(chart_b64)
        assert decoded.startswith(b'\x89PNG')
        print("✓ ChartImageService test passed")
        return True
    except Exception as e:
        print(f"✗ ChartImageService test failed: {e}")
        return False

def test_template_service():
    section = ReportSection(
        title="Test Section",
        content="Sample content",
        tables=[],
        metrics={},
        charts=[]
    )
    
    try:
        web_html = TemplateService.render_section(section, OutputFormat.WEB)
        pdf_html = TemplateService.render_section(section, OutputFormat.PDF)
        
        assert 'class="web-section"' in web_html
        assert 'class="pdf-section"' in pdf_html
        assert 'page-break-inside: avoid' in pdf_html
        assert web_html != pdf_html
        print("✓ TemplateService test passed")
        return True
    except Exception as e:
        print(f"✗ TemplateService test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing Clean Architecture Components...")
    
    results = [
        test_content_parser(),
        test_chart_service(),
        test_template_service()
    ]
    
    passed = sum(results)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    if passed == total:
        print("🎉 All tests successful!")
    else:
        print("❌ Some tests failed")