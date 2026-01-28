"""
Convert existing HTML content to structured blocks
"""
import json
import re
from bs4 import BeautifulSoup

def html_to_blocks(html_content):
    """Convert HTML to structured blocks"""
    soup = BeautifulSoup(html_content, 'html.parser')
    blocks = []
    
    for element in soup.children:
        if element.name == 'p':
            blocks.append({
                'type': 'paragraph',
                'content': element.get_text()
            })
        elif element.name in ['h1', 'h2', 'h3', 'h4']:
            blocks.append({
                'type': 'heading',
                'level': int(element.name[1]),
                'content': element.get_text()
            })
        elif element.name == 'ul':
            items = [li.decode_contents() for li in element.find_all('li')]
            blocks.append({
                'type': 'list',
                'items': items
            })
        elif element.name == 'table':
            rows = []
            for tr in element.find_all('tr'):
                tds = tr.find_all('td')
                if len(tds) == 2:
                    rows.append({
                        'label': tds[0].get_text().strip(),
                        'value': tds[1].get_text().strip()
                    })
            if rows:
                blocks.append({
                    'type': 'table',
                    'rows': rows
                })
    
    return blocks

# Load current report
with open('/mnt/c/kiro/data/demo_report_avgo.json') as f:
    report = json.load(f)

print("🔄 Converting HTML to structured blocks...\n")

# Convert each section
structured_sections = {}
for section_key, section_data in report['sections'].items():
    html_content = section_data['content']
    blocks = html_to_blocks(html_content)
    
    structured_sections[section_key] = {
        'title': section_data['title'],
        'subtitle': section_data.get('subtitle', ''),
        'blocks': blocks
    }
    
    print(f"✅ {section_key}: {len(blocks)} blocks")

# Create new structured report
structured_report = {
    'report_id': report['report_id'],
    'ticker': report['ticker'],
    'company_name': report['company_name'],
    'title': report['title'],
    'generated_at': report['generated_at'],
    'status': report['status'],
    'quality_score': report['quality_score'],
    'statistics': report['statistics'],
    'sections': structured_sections,
    'chart_data': report['chart_data'],
    'metadata': report['metadata']
}

# Save structured version
with open('/mnt/c/kiro/data/demo_report_avgo_structured.json', 'w') as f:
    json.dump(structured_report, f, indent=2)

print(f"\n✅ Saved structured report to: demo_report_avgo_structured.json")
print(f"\nTotal blocks across all sections: {sum(len(s['blocks']) for s in structured_sections.values())}")
