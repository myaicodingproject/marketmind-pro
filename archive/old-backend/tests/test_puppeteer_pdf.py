#!/usr/bin/env python3
"""
Test Puppeteer PDF Engine with GOOGL Report
Generates PDF and compares quality with WeasyPrint version
"""

import asyncio
import time
import json
import requests
from pathlib import Path
import sys
import os

# Add app directory to path
sys.path.append('/mnt/c/kiro')
sys.path.append('/mnt/c/kiro/app')

from app.services.puppeteer_integration import generate_professional_pdf

async def test_puppeteer_pdf_generation():
    """Test Puppeteer PDF generation with GOOGL data"""
    
    print("🚀 Testing Puppeteer PDF Engine")
    print("=" * 50)
    
    # Sample GOOGL report data (structured for testing)
    googl_report_data = {
        "ticker": "GOOGL",
        "title": "Alphabet Inc. - Comprehensive Stock Analysis",
        "generated_date": "January 25, 2026",
        "sections": {
            "executive_summary": {
                "title": "Executive Summary",
                "content": """
                **Investment Recommendation: BUY**
                **Price Target: $195.00**
                **Current Price: $178.50**
                **Upside Potential: 9.2%**
                
                Alphabet Inc. (GOOGL) represents a compelling investment opportunity driven by its dominant position in digital advertising, growing cloud computing business, and innovative AI capabilities. The company's diversified revenue streams and strong financial position provide resilience in various market conditions.
                
                ## Key Investment Highlights
                
                • **Market Leadership**: Dominant position in search and digital advertising with 90%+ market share
                • **AI Innovation**: Leading development in artificial intelligence and machine learning technologies
                • **Cloud Growth**: Google Cloud Platform showing strong growth trajectory with 35% YoY revenue increase
                • **Financial Strength**: Strong balance sheet with $120B+ in cash and cash equivalents
                • **Diversification**: Multiple revenue streams reducing dependency on core advertising business
                
                ## Key Risks
                
                • Regulatory scrutiny and potential antitrust actions
                • Increasing competition in cloud computing from AWS and Microsoft Azure
                • Privacy regulations impacting advertising effectiveness
                • Economic downturn affecting advertising spending
                """
            },
            "company_deep_dive": {
                "title": "Company Deep Dive",
                "content": """
                Alphabet Inc., the parent company of Google, is a multinational technology conglomerate headquartered in Mountain View, California. Founded in 2015 as a holding company for Google and its subsidiaries, Alphabet has evolved into one of the world's most valuable companies.
                
                ## Business Segments
                
                **Google Services** (85% of revenue)
                • Search advertising
                • YouTube advertising  
                • Google Network advertising
                • Google Play Store
                • Hardware products
                
                **Google Cloud** (10% of revenue)
                • Infrastructure as a Service (IaaS)
                • Platform as a Service (PaaS)
                • Software as a Service (SaaS)
                • AI and machine learning services
                
                **Other Bets** (5% of revenue)
                • Waymo (autonomous vehicles)
                • Verily (life sciences)
                • Wing (drone delivery)
                • Fiber (internet services)
                
                ## Competitive Advantages
                
                • **Data Moat**: Vast amounts of user data enabling superior targeting
                • **Network Effects**: More users attract more advertisers and vice versa
                • **Technical Excellence**: World-class engineering and AI capabilities
                • **Financial Resources**: Ability to invest heavily in R&D and acquisitions
                • **Brand Recognition**: Trusted global brand with billions of users
                """
            },
            "financial_analysis": {
                "title": "Financial Analysis",
                "content": """
                Alphabet demonstrates strong financial performance across key metrics, with consistent revenue growth and improving profitability margins.
                
                ## Revenue Analysis (Last 3 Years)
                
                | Year | Total Revenue | YoY Growth | Google Services | Google Cloud | Other Bets |
                |------|---------------|------------|----------------|--------------|------------|
                | 2023 | $307.4B | 8.7% | $261.0B | $33.1B | $1.3B |
                | 2022 | $282.8B | 5.6% | $237.9B | $26.3B | $1.1B |
                | 2021 | $257.6B | 41.2% | $209.5B | $19.2B | $0.8B |
                
                ## Profitability Metrics
                
                • **Gross Margin**: 57.8% (2023) vs 56.9% (2022)
                • **Operating Margin**: 23.7% (2023) vs 21.3% (2022)  
                • **Net Margin**: 20.9% (2023) vs 18.6% (2022)
                • **ROE**: 24.5% (2023) vs 22.1% (2022)
                • **ROA**: 16.8% (2023) vs 15.2% (2022)
                
                ## Cash Flow Analysis
                
                • **Operating Cash Flow**: $101.7B (2023) vs $91.5B (2022)
                • **Free Cash Flow**: $73.9B (2023) vs $65.2B (2022)
                • **Cash and Cash Equivalents**: $120.3B as of Q4 2023
                
                The company maintains exceptional cash generation capabilities, providing flexibility for strategic investments and shareholder returns.
                """
            },
            "valuation_analysis": {
                "title": "Valuation Analysis", 
                "content": """
                Our comprehensive valuation analysis employs multiple methodologies to arrive at a fair value estimate for Alphabet shares.
                
                ## Discounted Cash Flow (DCF) Analysis
                
                **Base Case Assumptions:**
                • Revenue CAGR (2024-2028): 12.5%
                • Terminal Growth Rate: 3.0%
                • Weighted Average Cost of Capital (WACC): 9.2%
                • Tax Rate: 21%
                
                **DCF Valuation Results:**
                • Present Value of FCF (2024-2028): $425B
                • Terminal Value: $1,850B
                • Enterprise Value: $2,275B
                • Equity Value: $2,395B
                • **Fair Value per Share: $195.00**
                
                ## Relative Valuation Analysis
                
                | Multiple | GOOGL | Peer Average | Premium/Discount |
                |----------|-------|--------------|------------------|
                | P/E (2024E) | 22.5x | 25.8x | -12.8% |
                | EV/EBITDA | 14.2x | 16.9x | -16.0% |
                | P/S | 5.1x | 6.8x | -25.0% |
                | PEG Ratio | 1.8x | 2.2x | -18.2% |
                
                ## Sum-of-the-Parts Valuation
                
                • Google Services: $1,950B (15x EBITDA)
                • Google Cloud: $280B (8x Revenue)
                • Other Bets: $45B (3x Revenue)
                • **Total Equity Value: $2,275B**
                • **Value per Share: $185.00**
                
                Our target price of $195.00 represents the midpoint of our DCF and relative valuation ranges.
                """
            },
            "competitive_analysis": {
                "title": "Competitive Analysis",
                "content": """
                Alphabet operates in highly competitive markets but maintains strong competitive positions across its core business segments.
                
                ## Search Engine Market
                
                **Market Share (Global)**
                • Google: 91.9%
                • Bing: 3.0%
                • Yahoo: 1.2%
                • Baidu: 1.0%
                • Others: 2.9%
                
                Google's dominance in search provides a significant competitive moat through network effects and data advantages.
                
                ## Cloud Computing Market
                
                **Market Share (Global IaaS)**
                • Amazon Web Services: 32%
                • Microsoft Azure: 23%
                • **Google Cloud: 10%**
                • Alibaba Cloud: 4%
                • Others: 31%
                
                While Google Cloud is the third-largest provider, it faces intense competition from AWS and Azure.
                
                ## Digital Advertising Market
                
                **Market Share (Global Digital Ad Spend)**
                • **Google: 28.6%**
                • Meta: 20.5%
                • Amazon: 7.8%
                • Microsoft: 2.5%
                • Others: 40.6%
                
                ## Competitive Strengths
                
                • **Technical Innovation**: Leading AI and machine learning capabilities
                • **Scale Advantages**: Massive infrastructure and data resources
                • **Ecosystem Integration**: Seamless integration across Google products
                • **Financial Resources**: Ability to invest heavily in growth areas
                
                ## Competitive Threats
                
                • **AI Competition**: Microsoft's partnership with OpenAI and ChatGPT integration
                • **Cloud Competition**: Aggressive pricing and feature development by AWS and Azure
                • **Regulatory Pressure**: Antitrust investigations and potential breakup scenarios
                • **Privacy Changes**: iOS privacy updates impacting advertising effectiveness
                """
            },
            "risk_assessment": {
                "title": "Risk Assessment",
                "content": """
                While Alphabet presents a compelling investment opportunity, several key risks could impact future performance.
                
                ## Regulatory and Legal Risks (High Impact)
                
                • **Antitrust Actions**: Multiple ongoing investigations in US and EU
                • **Privacy Regulations**: GDPR, CCPA, and similar laws affecting data collection
                • **Content Liability**: Potential changes to Section 230 protections
                • **Tax Policy Changes**: International tax coordination efforts
                
                ## Competitive Risks (Medium Impact)
                
                • **AI Disruption**: ChatGPT and other AI tools changing search behavior
                • **Cloud Competition**: Intense competition from AWS and Microsoft Azure
                • **Social Media Shift**: TikTok and other platforms capturing user attention
                • **Apple Privacy Changes**: iOS updates reducing advertising effectiveness
                
                ## Economic and Market Risks (Medium Impact)
                
                • **Advertising Cyclicality**: Economic downturns reducing ad spending
                • **Currency Fluctuations**: International revenue exposure to FX changes
                • **Interest Rate Sensitivity**: Higher rates affecting growth stock valuations
                • **Recession Risk**: Potential economic slowdown impacting growth
                
                ## Operational Risks (Low Impact)
                
                • **Key Personnel Risk**: Dependence on key executives and engineers
                • **Cybersecurity Threats**: Data breaches and security incidents
                • **Technology Disruption**: Emergence of new technologies
                • **Execution Risk**: Challenges in new business development
                
                ## Risk Mitigation Factors
                
                • **Diversified Revenue Streams**: Reducing dependence on single business
                • **Strong Balance Sheet**: Financial flexibility to weather challenges
                • **Innovation Culture**: Continuous investment in R&D and new technologies
                • **Global Presence**: Geographic diversification reducing regional risks
                
                **Overall Risk Rating: MODERATE**
                
                The company's strong competitive position and financial resources provide significant downside protection.
                """
            }
        }
    }
    
    try:
        # Test Puppeteer PDF generation
        print("📄 Generating PDF using Puppeteer engine...")
        start_time = time.time()
        
        output_path = "/mnt/c/kiro/GOOGL_Puppeteer_Test.pdf"
        result_path = await generate_professional_pdf("GOOGL", googl_report_data, output_path)
        
        generation_time = time.time() - start_time
        
        # Verify PDF was created
        if Path(result_path).exists():
            file_size = Path(result_path).stat().st_size
            
            print(f"✅ PDF generated successfully!")
            print(f"📁 File: {result_path}")
            print(f"⏱️  Generation time: {generation_time:.2f} seconds")
            print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Performance assessment
            if generation_time <= 6.0:
                print(f"🎯 Performance target met! ({generation_time:.2f}s ≤ 6.0s)")
            else:
                print(f"⚠️  Performance target missed ({generation_time:.2f}s > 6.0s)")
            
            # Quality assessment
            if file_size > 50000:  # 50KB minimum for quality PDF
                print("✅ PDF quality check passed (file size indicates proper content)")
            else:
                print("⚠️  PDF quality concern (file size too small)")
                
            return result_path
            
        else:
            print("❌ PDF file was not created")
            return None
            
    except Exception as e:
        print(f"❌ PDF generation failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

async def compare_with_weasyprint():
    """Compare Puppeteer vs WeasyPrint if available"""
    print("\n" + "=" * 50)
    print("📊 Quality Comparison")
    print("=" * 50)
    
    puppeteer_path = "/mnt/c/kiro/GOOGL_Puppeteer_Test.pdf"
    weasyprint_path = "/mnt/c/kiro/GOOGL_Enhanced_Professional.pdf"
    
    if Path(puppeteer_path).exists() and Path(weasyprint_path).exists():
        puppeteer_size = Path(puppeteer_path).stat().st_size
        weasyprint_size = Path(weasyprint_path).stat().st_size
        
        print(f"Puppeteer PDF: {puppeteer_size:,} bytes")
        print(f"WeasyPrint PDF: {weasyprint_size:,} bytes")
        
        size_diff = ((puppeteer_size - weasyprint_size) / weasyprint_size) * 100
        print(f"Size difference: {size_diff:+.1f}%")
        
        if puppeteer_size > weasyprint_size:
            print("✅ Puppeteer PDF is larger (likely more content/better quality)")
        else:
            print("ℹ️  WeasyPrint PDF is larger")
            
    else:
        print("⚠️  Cannot compare - one or both PDFs missing")

async def install_puppeteer():
    """Install Puppeteer if not available"""
    print("🔧 Installing Puppeteer...")
    
    try:
        # Check if package.json exists
        package_json_path = Path("/mnt/c/kiro/package.json")
        if not package_json_path.exists():
            # Create basic package.json
            package_data = {
                "name": "marketmind-pdf-generator",
                "version": "1.0.0",
                "description": "PDF generation for MarketMind Pro",
                "dependencies": {
                    "puppeteer": "^21.0.0"
                }
            }
            
            with open(package_json_path, 'w') as f:
                json.dump(package_data, f, indent=2)
            
            print("📦 Created package.json")
        
        # Install Puppeteer
        import subprocess
        result = subprocess.run(
            ['npm', 'install'], 
            cwd='/mnt/c/kiro',
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Puppeteer installed successfully")
            return True
        else:
            print(f"❌ Puppeteer installation failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Installation error: {e}")
        return False

async def main():
    """Main test function"""
    print("🧪 Puppeteer PDF Engine Test Suite")
    print("=" * 50)
    
    # Install Puppeteer if needed
    await install_puppeteer()
    
    # Test PDF generation
    result = await test_puppeteer_pdf_generation()
    
    if result:
        # Compare with existing WeasyPrint version
        await compare_with_weasyprint()
        
        print("\n" + "=" * 50)
        print("🎉 Test completed successfully!")
        print(f"📁 Generated PDF: {result}")
        print("=" * 50)
    else:
        print("\n❌ Test failed - PDF was not generated")

if __name__ == "__main__":
    asyncio.run(main())