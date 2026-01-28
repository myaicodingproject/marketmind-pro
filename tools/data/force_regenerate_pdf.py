#!/usr/bin/env python3
"""
Force regenerate the GOOGL PDF with professional generator
"""

import requests
import json
from professional_pdf_generator import generate_professional_pdf

def force_regenerate_pdf():
    """Force regenerate the GOOGL PDF"""
    print("🔄 Force regenerating GOOGL PDF with professional generator...")
    
    # Get report data
    response = requests.get("http://localhost:8000/api/v1/reports/prod_report_GOOGL_1769350746")
    if response.status_code == 200:
        report_data = response.json()
        
        # Generate new professional PDF
        output_path = "/mnt/c/kiro/MarketMind_Report_GOOGL_FINAL.pdf"
        result_path = generate_professional_pdf("GOOGL", report_data, output_path)
        
        print(f"✅ New professional PDF: {result_path}")
        
        # Check file size
        import os
        file_size = os.path.getsize(result_path)
        print(f"📄 File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        return result_path
    else:
        print(f"❌ Failed to get report data: {response.status_code}")
        return None

if __name__ == "__main__":
    pdf_path = force_regenerate_pdf()
    if pdf_path:
        print(f"\n🎉 SUCCESS! Professional PDF generated at:")
        print(f"   {pdf_path}")
        print(f"\n📋 Next steps:")
        print(f"   1. Download this file: {pdf_path}")
        print(f"   2. Compare with old awful PDF")
        print(f"   3. Professional PDF generation is working!")
    else:
        print("\n❌ Failed to generate PDF")
