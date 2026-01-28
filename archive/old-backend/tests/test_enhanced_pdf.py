#!/usr/bin/env python3
"""
Test the enhanced professional PDF generator with all fixes applied
"""

import requests
import json
from professional_pdf_generator import generate_professional_pdf
import os

def test_enhanced_pdf():
    """Test the enhanced PDF generation with all fixes"""
    print("🔧 Testing Enhanced Professional PDF Generator")
    print("=" * 60)
    
    # Get the GOOGL report data
    try:
        response = requests.get("http://localhost:8000/api/v1/reports/prod_report_GOOGL_1769350746")
        if response.status_code == 200:
            report_data = response.json()
            print(f"✅ Retrieved report data: {len(report_data.get('sections', {}))} sections")
            
            # Generate enhanced professional PDF
            output_path = "/mnt/c/kiro/GOOGL_Enhanced_Professional.pdf"
            result_path = generate_professional_pdf("GOOGL", report_data, output_path)
            
            print(f"✅ Enhanced PDF generated: {result_path}")
            
            # Check file size
            file_size = os.path.getsize(result_path)
            print(f"📄 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Compare with previous versions
            comparisons = [
                ("Original Awful", "/mnt/c/kiro/MarketMind_Report_GOOGL.pdf"),
                ("First Professional", "/mnt/c/kiro/MarketMind_Report_GOOGL_FINAL.pdf"),
                ("Enhanced Professional", result_path)
            ]
            
            print(f"\n📊 PDF Evolution Comparison:")
            for name, path in comparisons:
                if os.path.exists(path):
                    size = os.path.getsize(path)
                    print(f"   {name}: {size:,} bytes ({size/1024:.1f} KB)")
            
            return result_path
            
        else:
            print(f"❌ Failed to get report data: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def validate_pdf_quality(pdf_path):
    """Quick quality validation of the enhanced PDF"""
    print(f"\n🔍 Quality Validation: {os.path.basename(pdf_path)}")
    print("-" * 40)
    
    try:
        import PyPDF2
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader.pages)
            
            # Check first few pages for issues
            issues_found = 0
            checks_passed = 0
            
            for i in range(min(5, total_pages)):
                text = pdf_reader.pages[i].extract_text()
                
                # Check for fixed issues
                if '> #' not in text:
                    checks_passed += 1
                else:
                    issues_found += 1
                    print(f"   ❌ Page {i+1}: Still has markdown artifacts")
                
                if '|' not in text or 'Table' in text:
                    checks_passed += 1
                else:
                    issues_found += 1
                    print(f"   ❌ Page {i+1}: Raw table formatting")
                
                if 'Invoking' not in text and 'using tool:' not in text:
                    checks_passed += 1
                else:
                    issues_found += 1
                    print(f"   ❌ Page {i+1}: AI artifacts present")
            
            quality_score = (checks_passed / (checks_passed + issues_found)) * 100 if (checks_passed + issues_found) > 0 else 0
            
            print(f"   ✅ Checks passed: {checks_passed}")
            print(f"   ❌ Issues found: {issues_found}")
            print(f"   📊 Quality score: {quality_score:.1f}%")
            
            if quality_score >= 90:
                print(f"   🎉 EXCELLENT - Institutional quality achieved!")
            elif quality_score >= 75:
                print(f"   ✅ GOOD - Professional quality")
            elif quality_score >= 60:
                print(f"   ⚠️  FAIR - Needs improvement")
            else:
                print(f"   ❌ POOR - Major issues remain")
                
            return quality_score
            
    except Exception as e:
        print(f"   ❌ Validation error: {e}")
        return 0

if __name__ == "__main__":
    print("🚀 Enhanced PDF Generation Test")
    print("=" * 60)
    
    # Test enhanced PDF generation
    pdf_path = test_enhanced_pdf()
    
    if pdf_path:
        # Validate quality
        quality_score = validate_pdf_quality(pdf_path)
        
        print(f"\n🎯 RESULTS:")
        print(f"   📄 Enhanced PDF: {pdf_path}")
        print(f"   📊 Quality Score: {quality_score:.1f}%")
        
        if quality_score >= 90:
            print(f"   🎉 SUCCESS! Institutional-quality PDF achieved!")
            print(f"   📋 Ready for professional use")
        else:
            print(f"   ⚠️  Additional fixes may be needed")
            
        print(f"\n📥 Download the enhanced PDF:")
        print(f"   {pdf_path}")
        
    else:
        print(f"\n❌ Enhanced PDF generation failed")
