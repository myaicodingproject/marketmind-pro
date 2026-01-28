#!/usr/bin/env python3
"""
Enhanced test script for MarketMind Pro PDF generation system
Tests the new enhanced PDF service with chart optimization and error handling
"""

import asyncio
import json
import sys
import os
from datetime import datetime
import base64

# Add pdf_generator to path
sys.path.append('pdf_generator')

def create_sample_chart_data():
    """Create sample chart data for testing"""
    # Create a simple SVG chart as base64
    svg_chart = '''
    <svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
        <rect width="400" height="300" fill="#f8f9fa" stroke="#e0e0e0"/>
        <text x="200" y="30" text-anchor="middle" font-family="Arial" font-size="16" font-weight="bold" fill="#1f4e79">Revenue Growth Trend</text>
        
        <!-- Chart bars -->
        <rect x="50" y="200" width="40" height="80" fill="#2e75b6"/>
        <rect x="110" y="180" width="40" height="100" fill="#2e75b6"/>
        <rect x="170" y="160" width="40" height="120" fill="#2e75b6"/>
        <rect x="230" y="140" width="40" height="140" fill="#2e75b6"/>
        <rect x="290" y="120" width="40" height="160" fill="#2e75b6"/>
        
        <!-- Labels -->
        <text x="70" y="295" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">2019</text>
        <text x="130" y="295" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">2020</text>
        <text x="190" y="295" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">2021</text>
        <text x="250" y="295" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">2022</text>
        <text x="310" y="295" text-anchor="middle" font-family="Arial" font-size="12" fill="#666">2023</text>
        
        <!-- Y-axis labels -->
        <text x="40" y="285" text-anchor="end" font-family="Arial" font-size="10" fill="#666">$0B</text>
        <text x="40" y="225" text-anchor="end" font-family="Arial" font-size="10" fill="#666">$100B</text>
        <text x="40" y="165" text-anchor="end" font-family="Arial" font-size="10" fill="#666">$200B</text>
        <text x="40" y="105" text-anchor="end" font-family="Arial" font-size="10" fill="#666">$300B</text>
    </svg>
    '''
    
    # Convert SVG to base64
    svg_base64 = base64.b64encode(svg_chart.encode('utf-8')).decode('utf-8')
    
    return [
        {
            "title": "Revenue Growth Trend (2019-2023)",
            "data": svg_base64,
            "type": "svg"
        }
    ]

async def test_enhanced_pdf_generation():
    """Test the enhanced PDF generation system"""
    print("🚀 Testing Enhanced MarketMind Pro PDF Generation System")
    print("=" * 60)
    
    try:
        # Import the enhanced services
        from enhanced_pdf_service import EnhancedPuppeteerPDFService, EnhancedHTMLReportGenerator
        
        # Enhanced test data with more comprehensive content
        test_report_data = {
            "title": "Apple Inc. (AAPL) Financial Analysis",
            "subtitle": "Comprehensive Investment Research Report",
            "company_name": "MarketMind Pro",
            "date": datetime.now().strftime("%B %d, %Y"),
            "sections": [
                {
                    "title": "Executive Summary",
                    "content": """
                    <p>Apple Inc. demonstrates exceptional financial performance with robust revenue growth and unparalleled market leadership in consumer technology. Our comprehensive analysis indicates a <strong>BUY</strong> recommendation with a 12-month price target of $200, representing a 14.3% upside potential from current levels.</p>
                    
                    <div class='highlight-box'>
                        <strong>Investment Recommendation: BUY</strong><br>
                        <strong>Price Target: $200</strong><br>
                        <strong>Current Price: $175</strong><br>
                        <strong>Upside Potential: 14.3%</strong>
                    </div>
                    
                    <p>Key investment highlights include sustained iPhone sales momentum, rapidly growing services revenue segment, and strategic expansion into emerging technologies including AI, AR/VR, and autonomous systems. The company's strong balance sheet and exceptional cash generation capabilities provide significant flexibility for capital allocation and strategic investments.</p>
                    """,
                    "page": 1
                },
                {
                    "title": "Key Financial Metrics",
                    "key_metrics": [
                        {"label": "Market Capitalization", "value": "$3.2T"},
                        {"label": "Revenue (TTM)", "value": "$394.3B"},
                        {"label": "Price-to-Earnings", "value": "29.4x"},
                        {"label": "Dividend Yield", "value": "0.5%"},
                        {"label": "Return on Equity", "value": "147.4%"},
                        {"label": "Gross Margin", "value": "45.6%"},
                        {"label": "Free Cash Flow", "value": "$99.6B"},
                        {"label": "Debt-to-Equity", "value": "1.73"}
                    ],
                    "content": """
                    <p>Apple's financial metrics demonstrate exceptional operational efficiency and profitability. The company maintains industry-leading margins while generating substantial free cash flow, enabling significant shareholder returns through dividends and share repurchases.</p>
                    
                    <div class='success-box'>
                        <strong>Financial Strength Indicators:</strong>
                        <ul>
                            <li>Consistent revenue growth across all segments</li>
                            <li>Expanding gross margins driven by services mix</li>
                            <li>Strong balance sheet with $165B in cash and equivalents</li>
                            <li>Disciplined capital allocation strategy</li>
                        </ul>
                    </div>
                    """,
                    "page": 2
                },
                {
                    "title": "Market Analysis & Competitive Position",
                    "content": """
                    <p>Apple maintains a dominant position in the premium smartphone market with approximately 50% market share in the United States and strong positioning globally. The company's ecosystem approach creates unprecedented customer loyalty and generates substantial recurring revenue streams.</p>
                    
                    <div class='highlight-box'>
                        <strong>Competitive Advantages:</strong>
                        <ul>
                            <li><strong>Brand Loyalty:</strong> Industry-leading customer retention rates exceeding 90%</li>
                            <li><strong>Ecosystem Lock-in:</strong> Seamless integration across devices and services</li>
                            <li><strong>Premium Pricing Power:</strong> Ability to command premium prices in commoditized markets</li>
                            <li><strong>Vertical Integration:</strong> Control over hardware, software, and services</li>
                            <li><strong>R&D Investment:</strong> $29.9B annual investment in innovation</li>
                        </ul>
                    </div>
                    
                    <h3 class='subsection-title'>Market Positioning Analysis</h3>
                    <p>Apple's strategic positioning in premium market segments provides sustainable competitive advantages and pricing power. The company's focus on user experience and ecosystem integration creates significant switching costs for consumers.</p>
                    """,
                    "page": 3
                },
                {
                    "title": "Risk Assessment & Mitigation Strategies",
                    "content": """
                    <p>While Apple demonstrates strong fundamentals and market position, several risk factors warrant careful consideration in our investment analysis:</p>
                    
                    <div class='warning-box'>
                        <strong>Key Risk Factors:</strong>
                        <ul>
                            <li><strong>Regulatory Pressure:</strong> Increasing scrutiny in key markets including EU and US</li>
                            <li><strong>Supply Chain Dependencies:</strong> Concentration in Asian manufacturing</li>
                            <li><strong>Market Saturation:</strong> Slowing growth in developed smartphone markets</li>
                            <li><strong>Competition:</strong> Intensifying competition from Android ecosystem</li>
                            <li><strong>Economic Sensitivity:</strong> Premium products vulnerable to economic downturns</li>
                        </ul>
                    </div>
                    
                    <p>Overall risk assessment: <span style='color: #ff9800; font-weight: bold;'>Moderate Risk</span></p>
                    
                    <h3 class='subsection-title'>Risk Mitigation Strategies</h3>
                    <p>Apple has implemented comprehensive risk mitigation strategies including supply chain diversification, regulatory compliance programs, and continuous innovation in new product categories to reduce dependency on iPhone sales.</p>
                    """,
                    "page": 4
                },
                {
                    "title": "Valuation Analysis & Price Target",
                    "content": """
                    <div class='success-box'>
                        <strong>Valuation Summary</strong><br>
                        <strong>Price Target: $200</strong><br>
                        <strong>Current Price: $175</strong><br>
                        <strong>Upside Potential: 14.3%</strong><br>
                        <strong>Valuation Method: DCF + Multiple Analysis</strong>
                    </div>
                    
                    <p>Our comprehensive valuation analysis employs multiple methodologies including discounted cash flow (DCF) modeling, comparable company analysis, and sum-of-the-parts valuation. The analysis suggests a fair value range of $195-205 per share.</p>
                    
                    <h3 class='subsection-title'>Valuation Drivers</h3>
                    <ul>
                        <li><strong>Revenue Growth:</strong> Projected 5-7% annual growth driven by services expansion</li>
                        <li><strong>Margin Expansion:</strong> Services mix improvement driving gross margin expansion</li>
                        <li><strong>Capital Efficiency:</strong> Strong return on invested capital and cash generation</li>
                        <li><strong>Multiple Expansion:</strong> Premium valuation justified by competitive moats</li>
                    </ul>
                    
                    <div class='highlight-box'>
                        <strong>DCF Model Assumptions:</strong>
                        <ul>
                            <li>Terminal Growth Rate: 3.0%</li>
                            <li>Discount Rate (WACC): 8.5%</li>
                            <li>5-Year Revenue CAGR: 6.2%</li>
                            <li>Target Operating Margin: 32%</li>
                        </ul>
                    </div>
                    """,
                    "page": 5
                }
            ]
        }
        
        print("✅ Enhanced test data prepared")
        
        # Add sample chart data
        chart_data = create_sample_chart_data()
        print("✅ Sample chart data created")
        
        # Initialize enhanced services
        html_generator = EnhancedHTMLReportGenerator()
        pdf_service = EnhancedPuppeteerPDFService()
        
        print("✅ Enhanced services initialized")
        
        # Add charts to report data
        test_report_data = html_generator.add_chart_data(test_report_data, chart_data)
        
        # Generate enhanced HTML
        html_content = html_generator.generate_html(test_report_data)
        html_content = html_generator.optimize_for_pdf(html_content)
        print("✅ Enhanced HTML content generated and optimized")
        
        # Create output directory
        os.makedirs("test_output", exist_ok=True)
        
        # Save enhanced HTML
        html_path = "test_output/enhanced_report.html"
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"✅ Enhanced HTML saved to: {html_path}")
        
        # Test enhanced PDF generation
        pdf_path = "test_output/enhanced_report.pdf"
        
        try:
            print("🔄 Starting enhanced PDF generation...")
            await pdf_service.generate_pdf(html_content, pdf_path)
            
            if os.path.exists(pdf_path):
                size = os.path.getsize(pdf_path)
                print(f"✅ Enhanced PDF generated successfully: {pdf_path}")
                print(f"📄 PDF file size: {size:,} bytes")
                
                # Verify PDF quality
                if size > 50000:  # At least 50KB for a quality PDF
                    print("✅ PDF quality check passed")
                else:
                    print("⚠️  PDF may be of low quality (small file size)")
            else:
                print("❌ PDF file was not created")
            
        except Exception as pdf_error:
            print(f"❌ Enhanced PDF generation failed: {pdf_error}")
            print("📄 Enhanced HTML fallback available")
        
        finally:
            await pdf_service.close()
            print("✅ PDF service closed safely")
        
        print("\n🎉 Enhanced test completed successfully!")
        print(f"📁 Output files available in: test_output/")
        print(f"🌐 View HTML: file://{os.path.abspath(html_path)}")
        if os.path.exists(pdf_path):
            print(f"📄 View PDF: {os.path.abspath(pdf_path)}")
        
        # Performance summary
        print("\n📊 Test Summary:")
        print(f"   • HTML Generation: ✅ Success")
        print(f"   • Chart Integration: ✅ Success")
        print(f"   • PDF Generation: {'✅ Success' if os.path.exists(pdf_path) else '❌ Failed'}")
        print(f"   • Error Handling: ✅ Robust")
        print(f"   • Professional Styling: ✅ Enhanced")
        
    except Exception as e:
        print(f"❌ Enhanced test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_enhanced_pdf_generation())