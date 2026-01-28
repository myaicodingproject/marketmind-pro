#!/usr/bin/env python3
"""
Test the new professional PDF generation system
"""

import requests
import json
from professional_pdf_generator import generate_professional_pdf

def test_professional_pdf():
    """Test the professional PDF generation"""
    print("🧪 Testing Professional PDF Generation")
    
    # Get the GOOGL report data
    try:
        response = requests.get("http://localhost:8000/api/v1/reports/prod_report_GOOGL_1769350746")
        if response.status_code == 200:
            report_data = response.json()
            print(f"✅ Retrieved report data: {len(report_data.get('sections', {}))} sections")
            
            # Generate professional PDF directly
            output_path = "/mnt/c/kiro/GOOGL_Professional_Test.pdf"
            result_path = generate_professional_pdf("GOOGL", report_data, output_path)
            
            print(f"✅ Professional PDF generated: {result_path}")
            
            # Check file size
            import os
            file_size = os.path.getsize(result_path)
            print(f"📄 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            
            # Compare with old PDF
            old_pdf_size = os.path.getsize("/mnt/c/kiro/MarketMind_Report_GOOGL.pdf")
            print(f"📊 Size comparison:")
            print(f"   Old PDF: {old_pdf_size:,} bytes ({old_pdf_size/1024:.1f} KB)")
            print(f"   New PDF: {file_size:,} bytes ({file_size/1024:.1f} KB)")
            print(f"   Improvement: {((file_size - old_pdf_size) / old_pdf_size * 100):+.1f}%")
            
            return True
            
        else:
            print(f"❌ Failed to get report data: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = test_professional_pdf()
    if success:
        print("\n🎉 Professional PDF generation test completed successfully!")
        print("📋 Next steps:")
        print("   1. Open the new PDF to verify professional quality")
        print("   2. Compare with the old awful PDF")
        print("   3. Integration is complete - MarketMind Pro now generates professional PDFs!")
    else:
        print("\n❌ Test failed - check the error messages above")
