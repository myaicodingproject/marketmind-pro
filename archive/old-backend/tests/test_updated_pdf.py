#!/usr/bin/env python3
"""
Test script for the updated professional PDF generator
"""

from professional_pdf_generator import generate_professional_pdf

# Test data with markdown tables and various formatting
test_report_data = {
    "ticker": "TEST",
    "title": "Test Stock Analysis Report",
    "generated_date": "January 25, 2026",
    "sections": {
        "executive_summary": {
            "title": "Executive Summary",
            "content": """
## Investment Recommendation: BUY
## Price Target: $150.00
## Current Price: $120.50

This is a comprehensive analysis of TEST stock with strong fundamentals and growth prospects.

Key highlights include:
• Strong revenue growth of 15% YoY
• Expanding market share in core segments
• Robust balance sheet with low debt levels
• Experienced management team

## Financial Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Revenue | $10.5B | $12.1B |
| EPS | $5.25 | $6.80 |
| P/E Ratio | 22.9x | 22.1x |
| ROE | 18.5% | 20.2% |

The company demonstrates strong operational efficiency and market positioning.
            """
        },
        "financial_analysis": {
            "title": "Financial Analysis",
            "content": """
## Revenue Analysis

The company has shown consistent revenue growth over the past three years:

| Year | Revenue | Growth |
|------|---------|--------|
| 2024 | $10.5B | 15.2% |
| 2023 | $9.1B | 12.8% |
| 2022 | $8.1B | 10.5% |

## Profitability Metrics

Strong margins across all key metrics:
• Gross Margin: 45.2%
• Operating Margin: 18.7%
• Net Margin: 12.3%

The company maintains industry-leading profitability through operational excellence and strategic positioning.

## Balance Sheet Strength

| Item | Amount | % of Total |
|------|--------|------------|
| Cash & Equivalents | $2.1B | 15.2% |
| Total Assets | $13.8B | 100.0% |
| Total Debt | $1.9B | 13.8% |
| Shareholders' Equity | $8.2B | 59.4% |

The balance sheet reflects conservative financial management with strong liquidity position.
            """
        }
    }
}

def main():
    """Test the updated PDF generator"""
    try:
        print("🧪 Testing updated professional PDF generator...")
        
        # Generate PDF
        output_path = generate_professional_pdf("TEST", test_report_data, "test_updated_report.pdf")
        
        print(f"✅ PDF generated successfully: {output_path}")
        
        # Check file size
        import os
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"📄 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            if file_size > 1000:  # At least 1KB
                print("✅ File size looks good")
            else:
                print("⚠️  File size seems small, check content")
        else:
            print("❌ PDF file not found")
            
    except Exception as e:
        print(f"❌ Error generating PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()