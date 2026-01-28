#!/usr/bin/env python3
"""
Simple test for Puppeteer PDF service
"""

import asyncio
import os
import sys
sys.path.append('pdf_generator')

from puppeteer_service import PuppeteerPDFService, HTMLReportGenerator

async def test_puppeteer_service():
    """Test basic Puppeteer functionality"""
    print("🧪 Testing Puppeteer PDF Service")
    print("=" * 40)
    
    # Test data
    test_data = {
        "title": "Test Report - AAPL",
        "subtitle": "Sample Financial Analysis",
        "company_name": "MarketMind Pro",
        "date": "January 24, 2025",
        "sections": [
            {
                "title": "Executive Summary",
                "content": "<p>This is a test report to verify PDF generation functionality.</p>",
                "page": 1
            },
            {
                "title": "Key Metrics",
                "key_metrics": [
                    {"label": "Revenue", "value": "$394.3B"},
                    {"label": "Net Income", "value": "$99.8B"},
                    {"label": "P/E Ratio", "value": "28.5"},
                    {"label": "Market Cap", "value": "$3.0T"}
                ],
                "page": 2
            }
        ]
    }
    
    try:
        # Initialize services
        pdf_service = PuppeteerPDFService()
        html_generator = HTMLReportGenerator()
        
        print("1. Generating HTML content...")
        html_content = html_generator.generate_html(test_data)
        print("✅ HTML generated successfully")
        
        print("2. Converting HTML to PDF...")
        output_path = "test_output.pdf"
        
        result_path = await pdf_service.generate_pdf(html_content, output_path)
        
        if os.path.exists(result_path):
            file_size = os.path.getsize(result_path)
            print(f"✅ PDF generated successfully: {result_path}")
            print(f"   File size: {file_size} bytes")
            
            # Cleanup
            await pdf_service.close()
            
            return True
        else:
            print("❌ PDF file not created")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_puppeteer_service())
    
    if success:
        print("\n🎉 Puppeteer service test passed!")
    else:
        print("\n❌ Puppeteer service test failed!")
        
    print("\nNote: This test creates a basic PDF to verify functionality.")
    print("For full testing, run the PDF generator API and use test_pdf_generation.py")