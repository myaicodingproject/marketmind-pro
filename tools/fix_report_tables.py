"""
Fix table usage in demo report - only use tables for actual data, not narrative
"""
import json
import re

def should_be_table(text):
    """Determine if text should be a table based on content"""
    # Tables should be used for:
    # 1. Key-value pairs with metrics
    # 2. Comparison data (analyst ratings, peer comparison)
    # 3. Financial data
    
    # NOT for:
    # - Long narrative paragraphs
    # - Descriptive text
    # - Single sentences
    
    # Check if it's a metric/data pattern
    has_numbers = bool(re.search(r'\d+[%$B]|\d+\.\d+', text))
    has_colon = ':' in text
    is_short = len(text) < 200
    
    return has_numbers and (has_colon or is_short)

def convert_to_proper_html(text):
    """Convert text to HTML with proper table usage"""
    lines = text.strip().split('\n\n')
    html_parts = []
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Check if it's a heading (short line, no period at end)
        if len(line) < 80 and not line.endswith('.') and not line.endswith(':'):
            html_parts.append(f'<h3>{line}</h3>')
            
        # Check if it's a list
        elif line.startswith('- ') or line.startswith('• '):
            items = [item.strip('- •').strip() for item in line.split('\n') if item.strip()]
            html_parts.append('<ul>')
            for item in items:
                html_parts.append(f'<li>{item}</li>')
            html_parts.append('</ul>')
            
        # Check if it should be a table (key: value pattern)
        elif ':' in line and should_be_table(line):
            parts = line.split(':', 1)
            if len(parts) == 2:
                html_parts.append('<table class="data-table">')
                html_parts.append('<tr>')
                html_parts.append(f'<td><strong>{parts[0].strip()}</strong></td>')
                html_parts.append(f'<td>{parts[1].strip()}</td>')
                html_parts.append('</tr>')
                html_parts.append('</table>')
        
        # Otherwise, it's a paragraph
        else:
            html_parts.append(f'<p>{line}</p>')
    
    return '\n\n'.join(html_parts)

# Load demo report
with open('/mnt/c/kiro/data/demo_report_avgo.json') as f:
    report = json.load(f)

print("🔧 Fixing table usage in all sections...\n")

# Note: The current content is already in HTML format
# We need to identify which tables should remain and which should be converted to paragraphs

# For now, let's create a guide for what should be tables
table_guidelines = {
    "executive_summary": [
        "Business model breakdown (Semiconductor/Software split)",
        "Financial metrics (Revenue, AI revenue, FCF, etc.)",
        "Analyst ratings (Firm names and targets)",
        "Investment verdict (Target price, upside, risk)"
    ],
    "company_history": [
        "Key milestones timeline",
        "Major acquisitions with values"
    ],
    "leadership": [
        "CEO compensation breakdown",
        "Key controversies list"
    ],
    "business_model": [
        "Revenue breakdown by segment",
        "Cost structure metrics",
        "Competitor comparison"
    ],
    "market_position": [
        "Market share data",
        "Geographic revenue split"
    ],
    "competitive_advantages": [
        "Moat strength ratings",
        "Patent/R&D metrics"
    ],
    "market_size": [
        "TAM/SAM/SOM breakdown",
        "Growth projections"
    ],
    "financial_analysis": [
        "Revenue trend (multi-year)",
        "Margin metrics",
        "Cash flow breakdown"
    ],
    "valuation_analysis": [
        "Valuation multiples",
        "DCF assumptions",
        "Peer comparison metrics"
    ]
}

print("📋 TABLE USAGE GUIDELINES:\n")
for section, guidelines in table_guidelines.items():
    print(f"\n{section.replace('_', ' ').title()}:")
    for guideline in guidelines:
        print(f"  ✅ {guideline}")

print("\n\n💡 RECOMMENDATION:")
print("Tables should ONLY be used for:")
print("  1. Numeric data and metrics")
print("  2. Comparison data (analyst ratings, peer comparison)")
print("  3. Key-value pairs (Revenue: $51.6B)")
print("\nNOT for:")
print("  ❌ Long narrative paragraphs")
print("  ❌ Descriptive text")
print("  ❌ Story-telling content")

print("\n\n🎯 To fix the current report:")
print("The content needs to be rewritten with proper structure.")
print("Current HTML has too many tables for narrative content.")
