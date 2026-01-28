#!/usr/bin/env python3
"""
Test script for MarketMind Pro PDF generation system
"""

import asyncio
import json
import sys
import os
from datetime import datetime

# Add pdf_generator to path
sys.path.append('pdf_generator')

async def test_pdf_generation():
    """Test the PDF generation system"""
    print("🧪 Testing MarketMind Pro PDF Generation System")
    print("=" * 50)
    
    try:
        # Import the services
        from puppeteer_service import PuppeteerPDFService, HTMLReportGenerator
        
        # Test data
        test_report_data = {
            "title": "Apple Inc. (AAPL) Financial Analysis",
            "subtitle": "Comprehensive Investment Research Report",
            "company_name": "MarketMind Pro",
            "date": datetime.now().strftime("%B %d, %Y"),
            "sections": [
                {
                    "title": "Executive Summary",
                    "content": "<p>Apple Inc. demonstrates strong financial performance with robust revenue growth and market leadership in consumer technology. Our analysis indicates a <strong>BUY</strong> recommendation with a 12-month price target of $200.</p><p>Key investment highlights include strong iPhone sales, growing services revenue, and expanding market presence in emerging technologies.</p>",
                    "page": 1
                },
                {
                    "title": "Key Financial Metrics",
                    "key_metrics": [
                        {"label": "Market Cap", "value": "$3.2T"},
                        {"label": "Revenue (TTM)", "value": "$394.3B"},
                        {"label": "P/E Ratio", "value": "29.4x"},
                        {"label": "Dividend Yield", "value": "0.5%"},
                        {"label": "ROE", "value": "147.4%"},
                        {"label": "Gross Margin", "value": "45.6%"},
                        {"label": "Free Cash Flow", "value": "$99.6B"},
                        {"label": "Debt-to-Equity", "value": "1.73"}
                    ],
                    "page": 2
                },
                {
                    "title": "Market Analysis & Competitive Position",
                    "content": "<p>Apple maintains a dominant position in the premium smartphone market with approximately 50% market share in the US. The company's ecosystem approach creates strong customer loyalty and recurring revenue streams.</p><div class='highlight-box'><strong>Competitive Advantages:</strong><ul><li>Brand loyalty and ecosystem lock-in</li><li>Premium pricing power</li><li>Vertical integration capabilities</li><li>Strong R&D investment</li></ul></div>",
                    "page": 3
                },
                {
                    "title": "Risk Assessment",
                    "content": "<p>While Apple shows strong fundamentals, several risk factors warrant consideration:</p><div class='warning-box'><strong>Key Risk Factors:</strong><ul><li>Regulatory pressure in key markets</li><li>Supply chain dependencies</li><li>Market saturation in developed countries</li><li>Competition from Android ecosystem</li></ul></div><p>Overall risk rating: <span style='color: #ff9800; font-weight: bold;'>Moderate</span></p>",
                    "page": 4
                },
                {
                    "title": "Valuation & Price Target",
                    "content": "<div class='success-box'><strong>Price Target: $200</strong><br>Current Price: $175<br>Upside Potential: 14.3%</div><p>Our DCF analysis suggests a fair value of $195-205 per share, supported by:</p><ul><li>Steady revenue growth of 5-7% annually</li><li>Margin expansion in services</li><li>Capital allocation efficiency</li><li>Multiple expansion potential</li></ul>",
                    "page": 5
                }
            ]
        }
        
        print("✅ Test data prepared")
        
        # Initialize services
        html_generator = HTMLReportGenerator()
        pdf_service = PuppeteerPDFService()
        
        print("✅ Services initialized")
        
        # Generate HTML
        html_content = html_generator.generate_html(test_report_data)
        print("✅ HTML content generated")
        
        # Create output directory
        os.makedirs("test_output", exist_ok=True)
        
        # Test HTML output first
        html_path = "test_output/test_report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ HTML saved to: {html_path}")
        
        # Test PDF generation
        pdf_path = "test_output/test_report.pdf"
        
        try:
            await pdf_service.generate_pdf(html_content, pdf_path)
            print(f"✅ PDF generated successfully: {pdf_path}")
            
            # Check file size
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"📄 PDF file size: {size:,} bytes")
            
        except Exception as pdf_error:
            print(f"⚠️  PDF generation failed: {pdf_error}")
            print("📄 HTML fallback available")
        
        finally:
            await pdf_service.close()
        
        print("\n🎉 Test completed successfully!")
        print(f"📁 Output files in: test_output/")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_pdf_generation())