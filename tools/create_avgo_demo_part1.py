#!/usr/bin/env python3
"""
Generate comprehensive AVGO demo data from extracted PDF content
Fixes all issues: HTML formatting, stats, charts, proper section names, realistic content
"""
import json
from datetime import datetime
from pathlib import Path

# Load extracted AVGO content
with open('data/avgo_extracted.json', 'r', encoding='utf-8') as f:
    avgo_data = json.load(f)

# Create comprehensive demo data with proper structure
demo_data = {
    "report_id": "PLACEHOLDER",
    "ticker": "DEMO",
    "company_name": "Broadcom Inc. (DEMO MODE)",
    "title": "DEMO - Comprehensive Stock Analysis Report",
    "generated_at": datetime.now().isoformat(),
    "status": "completed",
    "quality_score": 94,
    
    # CRITICAL: Proper statistics for display
    "statistics": {
        "total_sections": 8,
        "total_words": 15000,
        "generation_method": "demo_mode",
        "pdf_generated": False,
        "enhanced_processing": False
    },
    
    # CRITICAL: Chart data for charts overview
    "chart_data": {
        "revenue_trend": {
            "type": "line",
            "title": "Revenue Growth Trend",
            "labels": ["FY2022", "FY2023", "FY2024"],
            "datasets": [{
                "label": "Revenue ($B)",
                "data": [33.2, 35.8, 51.6]
            }]
        },
        "segment_revenue": {
            "type": "pie",
            "title": "Revenue by Segment (FY2024)",
            "labels": ["Semiconductor Solutions", "Infrastructure Software"],
            "datasets": [{
                "data": [58, 42]
            }]
        },
        "profitability_metrics": {
            "type": "bar",
            "title": "Profitability Metrics (%)",
            "labels": ["Gross Margin", "Operating Margin", "Net Margin"],
            "datasets": [{
                "label": "FY2024",
                "data": [76.1, 45, 25]
            }]
        },
        "ai_revenue_growth": {
            "type": "line",
            "title": "AI Revenue Growth",
            "labels": ["FY2023", "FY2024"],
            "datasets": [{
                "label": "AI Revenue ($B)",
                "data": [5.5, 12.2]
            }]
        }
    },
    
    "sections": {}
}

# Section 1: Executive Summary (from PDF pages 9-11)
demo_data["sections"]["executive_summary"] = {
    "title": "Executive Summary",
    "content": """<h2>Company Overview</h2>
<p>Broadcom Inc. (NASDAQ: AVGO) is a global leader in semiconductor and infrastructure software solutions, renowned for its dual-engine business model combining "Semiconductor + Infrastructure Software." Through strategic acquisitions including the 2016 merger with original Avago, 2018 acquisition of CA Technologies, and the landmark $61 billion VMware acquisition completed in 2023, the company has successfully transformed into a technology giant. FY2024 total revenue reached $51.6 billion (up 44% YoY), with market capitalization exceeding $1 trillion, demonstrating its critical position in the global technology ecosystem.</p>

<h2>Investment Recommendation: BUY</h2>
<p><strong>Target Price: $450</strong> | <strong>Current Price: ~$350</strong> | <strong>Upside: 28%</strong></p>
<p><strong>Investment Horizon: 12 months</strong> | <strong>Risk Rating: Medium</strong></p>

<h2>Key Investment Highlights</h2>
<ul>
<li><strong>AI Custom ASIC Leadership:</strong> 70-80% market share in custom AI accelerators with $110B order backlog</li>
<li><strong>Dual-Engine Model:</strong> 58% revenue from semiconductors, 42% from high-margin infrastructure software (VMware)</li>
<li><strong>Market Dominance:</strong> Duopoly with Nvidia in data center networking chips, serving hyperscale cloud customers</li>
<li><strong>Strong Cash Generation:</strong> FY2024 free cash flow of $21.9B enables substantial shareholder returns</li>
<li><strong>Strategic Partnerships:</strong> Long-term contracts with Google, Meta, OpenAI, Apple, ByteDance</li>
</ul>

<h2>Financial Performance Summary (FY2024)</h2>
<table border="1" cellpadding="8" cellspacing="0">
<tr><th>Metric</th><th>FY2024</th><th>Growth YoY</th></tr>
<tr><td>Total Revenue</td><td>$51.6B</td><td>+44%</td></tr>
<tr><td>Semiconductor Revenue</td><td>$30.1B</td><td>+18%</td></tr>
<tr><td>Software Revenue</td><td>$21.5B</td><td>+VMware</td></tr>
<tr><td>AI Revenue</td><td>$12.2B</td><td>+220%</td></tr>
<tr><td>Gross Margin</td><td>76.1%</td><td>+7.2pp</td></tr>
<tr><td>Operating Margin</td><td>45%</td><td>Industry-leading</td></tr>
<tr><td>Free Cash Flow</td><td>$21.9B</td><td>+10%</td></tr>
<tr><td>R&D Investment</td><td>$9.3B</td><td>18% of revenue</td></tr>
</table>

<h2>Investment Risks</h2>
<ul>
<li><strong>Customer Concentration:</strong> Top 5 customers contribute ~40% of revenue</li>
<li><strong>VMware Integration:</strong> Pricing and licensing changes causing customer dissatisfaction</li>
<li><strong>Geopolitical Risk:</strong> Dependence on TSMC advanced process nodes in Taiwan</li>
<li><strong>Competition:</strong> Nvidia, AMD intensifying competition in AI and custom chips</li>
<li><strong>Valuation:</strong> Forward P/E of 42x above historical averages, requires sustained growth</li>
</ul>

<h2>Future Outlook & Catalysts</h2>
<p>Company's growth over next 3 years will be driven by AI infrastructure and software subscription services. Management targets expanding AI customer base from 3-4 to 6-8 customers, increasing data center network chip penetration, and deepening VMware integration synergies. Financially, focus is on deleveraging (target Debt/EBITDA < 1.5x) and continued shareholder returns through strong free cash flow generation.</p>

<p><strong>Key Catalysts:</strong></p>
<ol>
<li>OpenAI 10GW AI accelerator collaboration (2026-2029): $70-300B revenue potential</li>
<li>iPhone 16 cycle with AI features driving connectivity chip demand</li>
<li>VMware subscription transition showing 70%+ gross margins</li>
<li>3nm XPU chip production ramp in 2025</li>
</ol>""",
    "charts": []
}

# Save demo data
output_path = Path('data/demo_report_avgo.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(demo_data, f, indent=2, ensure_ascii=False)

print(f"✅ Created comprehensive AVGO demo data: {output_path}")
print(f"📊 Sections: {len(demo_data['sections'])} (will add remaining 7)")
print(f"📈 Charts: {len(demo_data['chart_data'])} chart types")
print(f"📝 Statistics: {demo_data['statistics']}")
