#!/usr/bin/env python3
"""
Simplified Puppeteer PDF Test
Tests the new Puppeteer PDF engine without complex dependencies
"""

import asyncio
import time
import json
import tempfile
import os
from pathlib import Path
import subprocess

class SimplePuppeteerPDFService:
    """Simplified Puppeteer PDF service for testing"""
    
    def __init__(self):
        self.node_script_path = Path(__file__).parent / "app" / "services" / "puppeteer_generator.js"
        self.template_path = Path(__file__).parent / "templates" / "stock_report.html"
        self.css_path = Path(__file__).parent / "static" / "css" / "report-styles.css"
        
        self.pdf_options = {
            "format": "A4",
            "margin": {
                "top": "1in",
                "right": "0.75in", 
                "bottom": "1.25in",
                "left": "0.75in"
            },
            "printBackground": True,
            "preferCSSPageSize": True
        }
    
    async def generate_pdf(self, report_data, output_path):
        """Generate PDF using Puppeteer"""
        start_time = time.time()
        
        try:
            # Prepare data for Node.js script
            temp_data = {
                "report_data": report_data,
                "output_path": output_path,
                "pdf_options": self.pdf_options,
                "template_path": str(self.template_path),
                "css_path": str(self.css_path)
            }
            
            # Write temporary data file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(temp_data, temp_file, indent=2)
                temp_data_path = temp_file.name
            
            try:
                # Try to install puppeteer first
                print("🔧 Installing Puppeteer...")
                install_result = subprocess.run(
                    ['npm', 'install', 'puppeteer'],
                    cwd=str(Path(__file__).parent),
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                
                if install_result.returncode == 0:
                    print("✅ Puppeteer installed successfully")
                else:
                    print(f"⚠️  Puppeteer installation had warnings: {install_result.stderr[:200]}...")
                
                # Execute Puppeteer script
                print("🚀 Running Puppeteer PDF generation...")
                result = subprocess.run(
                    ['node', str(self.node_script_path), temp_data_path],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr if result.stderr else "Unknown error"
                    raise Exception(f"Node.js script failed: {error_msg}")
                
                # Verify PDF was created
                if not os.path.exists(output_path):
                    raise Exception(f"PDF generation failed: {result.stdout}")
                
                file_size = os.path.getsize(output_path)
                generation_time = time.time() - start_time
                
                print(f"✅ PDF generated in {generation_time:.2f}s, size: {file_size:,} bytes")
                return output_path
                
            finally:
                # Cleanup
                if os.path.exists(temp_data_path):
                    os.unlink(temp_data_path)
                    
        except Exception as e:
            raise Exception(f"Puppeteer PDF generation failed: {str(e)}")

async def test_puppeteer_pdf():
    """Test Puppeteer PDF generation"""
    
    print("🧪 Puppeteer PDF Engine Test")
    print("=" * 50)
    
    # Sample GOOGL report data
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
                
                Alphabet Inc. (GOOGL) represents a compelling investment opportunity driven by its dominant position in digital advertising, growing cloud computing business, and innovative AI capabilities.
                
                ## Key Investment Highlights
                
                • Market Leadership: Dominant position in search and digital advertising
                • AI Innovation: Leading development in artificial intelligence
                • Cloud Growth: Google Cloud Platform showing strong growth
                • Financial Strength: Strong balance sheet with $120B+ in cash
                • Diversification: Multiple revenue streams
                
                ## Key Risks
                
                • Regulatory scrutiny and potential antitrust actions
                • Increasing competition in cloud computing
                • Privacy regulations impacting advertising effectiveness
                • Economic downturn affecting advertising spending
                """
            },
            "financial_analysis": {
                "title": "Financial Analysis",
                "content": """
                Alphabet demonstrates strong financial performance across key metrics.
                
                ## Revenue Analysis
                
                | Year | Total Revenue | YoY Growth | Google Services | Google Cloud |
                |------|---------------|------------|----------------|--------------|
                | 2023 | $307.4B | 8.7% | $261.0B | $33.1B |
                | 2022 | $282.8B | 5.6% | $237.9B | $26.3B |
                | 2021 | $257.6B | 41.2% | $209.5B | $19.2B |
                
                ## Key Metrics
                
                • Gross Margin: 57.8% (2023) vs 56.9% (2022)
                • Operating Margin: 23.7% (2023) vs 21.3% (2022)
                • Net Margin: 20.9% (2023) vs 18.6% (2022)
                • Operating Cash Flow: $101.7B (2023)
                • Free Cash Flow: $73.9B (2023)
                """
            },
            "risk_assessment": {
                "title": "Risk Assessment",
                "content": """
                While Alphabet presents a compelling investment opportunity, several key risks could impact future performance.
                
                ## Regulatory and Legal Risks (High Impact)
                
                • Antitrust Actions: Multiple ongoing investigations in US and EU
                • Privacy Regulations: GDPR, CCPA affecting data collection
                • Content Liability: Potential changes to Section 230 protections
                
                ## Competitive Risks (Medium Impact)
                
                • AI Disruption: ChatGPT changing search behavior
                • Cloud Competition: Intense competition from AWS and Azure
                • Social Media Shift: TikTok capturing user attention
                
                ## Economic Risks (Medium Impact)
                
                • Advertising Cyclicality: Economic downturns reducing ad spending
                • Currency Fluctuations: International revenue exposure
                • Interest Rate Sensitivity: Higher rates affecting valuations
                
                **Overall Risk Rating: MODERATE**
                """
            }
        }
    }
    
    try:
        # Test PDF generation
        service = SimplePuppeteerPDFService()
        output_path = "/mnt/c/kiro/GOOGL_Puppeteer_Test.pdf"
        
        result_path = await service.generate_pdf(googl_report_data, output_path)
        
        if Path(result_path).exists():
            file_size = Path(result_path).stat().st_size
            
            print(f"✅ PDF generated successfully!")
            print(f"📁 File: {result_path}")
            print(f"📊 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Quality assessment
            if file_size > 50000:  # 50KB minimum
                print("✅ PDF quality check passed")
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

async def main():
    """Main test function"""
    print("🚀 Testing Puppeteer PDF Engine")
    print("=" * 50)
    
    result = await test_puppeteer_pdf()
    
    if result:
        print("\n" + "=" * 50)
        print("🎉 Test completed successfully!")
        print(f"📁 Generated PDF: {result}")
        
        # Compare with existing WeasyPrint version if available
        weasyprint_path = "/mnt/c/kiro/GOOGL_Enhanced_Professional.pdf"
        if Path(weasyprint_path).exists():
            puppeteer_size = Path(result).stat().st_size
            weasyprint_size = Path(weasyprint_path).stat().st_size
            
            print(f"\n📊 Quality Comparison:")
            print(f"Puppeteer PDF: {puppeteer_size:,} bytes")
            print(f"WeasyPrint PDF: {weasyprint_size:,} bytes")
            
            size_diff = ((puppeteer_size - weasyprint_size) / weasyprint_size) * 100
            print(f"Size difference: {size_diff:+.1f}%")
        
        print("=" * 50)
    else:
        print("\n❌ Test failed - PDF was not generated")

if __name__ == "__main__":
    asyncio.run(main())