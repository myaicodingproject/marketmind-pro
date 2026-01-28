"""
Quick fix for demo report tables - convert narrative tables to proper HTML
"""
import json
import re

def fix_table_content(html_content):
    """Convert inappropriate tables to paragraphs/lists"""
    
    # Pattern to find tables
    table_pattern = r'<table[^>]*>(.*?)</table>'
    
    def should_keep_table(table_html):
        """Determine if table should remain a table"""
        # Keep if it has multiple rows (comparison data)
        row_count = table_html.count('<tr>')
        if row_count > 2:
            return True
            
        # Keep if it contains numbers/metrics
        has_numbers = bool(re.search(r'\$\d+|\d+%|\d+\.\d+[BM]', table_html))
        is_short = len(table_html) < 500
        
        return has_numbers and is_short
    
    def table_to_html(table_html):
        """Convert table to appropriate HTML"""
        # Extract content from table cells
        cells = re.findall(r'<td[^>]*>(.*?)</td>', table_html, re.DOTALL)
        
        if len(cells) == 2:
            # Two-cell table: check if it's a key-value pair
            key = re.sub(r'<[^>]+>', '', cells[0]).strip()
            value = re.sub(r'<[^>]+>', '', cells[1]).strip()
            
            # If value is long (>100 chars), make it a paragraph
            if len(value) > 100:
                return f'<p><strong>{key}:</strong> {value}</p>'
            # If it has numbers, keep as table
            elif re.search(r'\d', value):
                return table_html  # Keep original
            else:
                return f'<p><strong>{key}:</strong> {value}</p>'
        
        return table_html  # Keep original for multi-row tables
    
    # Process each table
    def replace_table(match):
        table_html = match.group(0)
        
        if should_keep_table(table_html):
            return table_html  # Keep as table
        else:
            return table_to_html(table_html)  # Convert to paragraph
    
    # Replace tables
    fixed_html = re.sub(table_pattern, replace_table, html_content, flags=re.DOTALL)
    
    # Clean up inline styles (keep only class)
    fixed_html = re.sub(r' style="[^"]*"', '', fixed_html)
    
    return fixed_html

# Load report
with open('/mnt/c/kiro/data/demo_report_avgo.json') as f:
    report = json.load(f)

print("🔧 Fixing table usage in all sections...\n")

# Fix each section
for section_key in report['sections']:
    original_content = report['sections'][section_key]['content']
    original_tables = original_content.count('<table')
    
    # Apply fixes
    fixed_content = fix_table_content(original_content)
    new_tables = fixed_content.count('<table')
    
    report['sections'][section_key]['content'] = fixed_content
    
    print(f"✅ {section_key}: {original_tables} → {new_tables} tables")

# Save fixed report
with open('/mnt/c/kiro/data/demo_report_avgo.json', 'w') as f:
    json.dump(report, f, indent=2)

print("\n✅ All sections fixed and saved!")
print("\nTables now only used for:")
print("  • Multi-row comparison data")
print("  • Numeric metrics and statistics")
print("  • Short key-value pairs with numbers")
