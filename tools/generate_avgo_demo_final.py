#!/usr/bin/env python3
import json
from datetime import datetime

# Load extracted chapters
with open('data/avgo_chapters_extracted.json', 'r', encoding='utf-8') as f:
    chapters = json.load(f)

# Create complete demo data
demo = {
    "report_id": "PLACEHOLDER",
    "ticker": "DEMO",
    "company_name": "Broadcom Inc. (DEMO MODE)",
    "title": "DEMO - Comprehensive Stock Analysis Report",
    "generated_at": datetime.now().isoformat(),
    "status": "completed",
    "quality_score": 94,
    "statistics": {
        "total_sections": 8,
        "total_words": 15000,
        "generation_method": "demo_mode",
        "pdf_generated": False
    },
    "chart_data": {
        "revenue_trend": {
            "labels": ["FY2022", "FY2023", "FY2024"],
            "data": [33.2, 35.8, 51.6]
        },
        "segment_revenue": {
            "labels": ["Semiconductor", "Software"],
            "data": [58, 42]
        },
        "ai_growth": {
            "labels": ["FY2023", "FY2024"],
            "data": [5.5, 12.2]
        }
    },
    "sections": {}
}

# Add all 8 sections with HTML formatting
sections_map = {
    "executive_summary": "Executive Summary",
    "company_history": "Chapter 1: Company History and Evolution",
    "leadership": "Chapter 2: Company Leadership",
    "business_model": "Chapter 3: Business Model",
    "market_position": "Chapter 4: Market Position",
    "competitive_advantages": "Chapter 5: Competitive Advantages",
    "market_size": "Chapter 6: Market Size (TAM/SAM/SOM)",
    "financial_analysis": "Chapter 7: Financial Analysis"
}

for key, title in sections_map.items():
    # Convert text to HTML paragraphs
    text = chapters.get(key, "Content not available")
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    html_content = "<h2>" + title + "</h2>\n"
    for p in paragraphs[:10]:  # Limit to first 10 paragraphs
        html_content += f"<p>{p}</p>\n"
    
    demo["sections"][key] = {
        "title": title,
        "content": html_content,
        "charts": []
    }

# Save
with open('data/demo_report_avgo.json', 'w', encoding='utf-8') as f:
    json.dump(demo, f, indent=2, ensure_ascii=False)

print("✅ Created demo_report_avgo.json")
print(f"   Sections: {len(demo['sections'])}")
print(f"   Charts: {len(demo['chart_data'])}")
print(f"   Stats: {demo['statistics']}")
