#!/usr/bin/env python3
"""Generate demo PDF once from demo data"""
import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.template_service import TemplateService
from weasyprint import HTML

def generate_demo_pdf():
    """Generate demo PDF once and save for reuse"""
    
    # Load demo data
    demo_file = Path(__file__).parent.parent / "data" / "demo_report_aapl.json"
    with open(demo_file, 'r') as f:
        demo_data = json.load(f)
    
    print("📄 Loaded demo data")
    
    # Initialize template service
    template_service = TemplateService()
    print("✅ Template service initialized")
    
    # Render HTML
    html_content = template_service.render_report(demo_data, format='pdf')
    print("📝 HTML rendered")
    
    # Generate PDF
    pdf_bytes = HTML(string=html_content).write_pdf()
    print("🎨 PDF generated")
    
    # Save to file
    output_path = Path(__file__).parent.parent / "data" / "demo_report_aapl.pdf"
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"✅ Demo PDF saved: {output_path}")
    print(f"📊 PDF size: {len(pdf_bytes) / 1024:.1f} KB")

if __name__ == "__main__":
    generate_demo_pdf()
