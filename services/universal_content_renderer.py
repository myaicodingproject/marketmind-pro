"""
Universal Content Renderer - Single source of truth for frontend and PDF
"""

class ContentBlock:
    """Base class for content blocks"""
    def to_html(self):
        raise NotImplementedError
    
    def to_react_props(self):
        raise NotImplementedError

class Paragraph(ContentBlock):
    def __init__(self, content):
        self.content = content
    
    def to_html(self):
        return f'<p>{self.content}</p>'
    
    def to_react_props(self):
        return {'type': 'paragraph', 'content': self.content}

class Heading(ContentBlock):
    def __init__(self, content, level=3):
        self.content = content
        self.level = level
    
    def to_html(self):
        return f'<h{self.level}>{self.content}</h{self.level}>'
    
    def to_react_props(self):
        return {'type': 'heading', 'level': self.level, 'content': self.content}

class List(ContentBlock):
    def __init__(self, items):
        self.items = items
    
    def to_html(self):
        items_html = ''.join([f'<li>{item}</li>' for item in self.items])
        return f'<ul>{items_html}</ul>'
    
    def to_react_props(self):
        return {'type': 'list', 'items': self.items}

class Table(ContentBlock):
    def __init__(self, rows):
        self.rows = rows  # [{'label': '...', 'value': '...'}]
    
    def to_html(self):
        rows_html = ''
        for row in self.rows:
            rows_html += f'''<tr>
<td><strong>{row['label']}</strong></td>
<td>{row['value']}</td>
</tr>'''
        return f'<table class="data-table">{rows_html}</table>'
    
    def to_react_props(self):
        return {'type': 'table', 'rows': self.rows}

class Chart(ContentBlock):
    def __init__(self, chart_id, chart_type):
        self.chart_id = chart_id
        self.chart_type = chart_type
    
    def to_html(self):
        # Placeholder for PDF - actual chart image will be inserted
        return f'<div class="chart-placeholder" data-chart-id="{self.chart_id}"></div>'
    
    def to_react_props(self):
        return {'type': 'chart', 'chartId': self.chart_id, 'chartType': self.chart_type}


def render_to_html(blocks):
    """Render blocks to HTML for PDF"""
    html_parts = []
    for block in blocks:
        html_parts.append(block.to_html())
    return '\n\n'.join(html_parts)


def render_to_react_data(blocks):
    """Render blocks to React props for frontend"""
    return [block.to_react_props() for block in blocks]


# Example: Executive Summary structure
executive_summary_blocks = [
    Paragraph("Broadcom Inc. (NASDAQ: AVGO) has emerged as a dominant force in the global technology ecosystem, with a market capitalization exceeding $1 trillion as of late 2024. The company's strategic transformation—driven by disciplined M&A and deep technological integration—has positioned it at the heart of two high-growth megatrends: artificial intelligence (AI) infrastructure and enterprise software."),
    
    Heading("Dual-Engine Business Model"),
    
    Paragraph("Broadcom operates a unique \"dual-engine\" model that balances cyclical semiconductor revenue with recurring software income:"),
    
    Table([
        {'label': 'Semiconductor Solutions', 'value': '58% of FY2024 revenue ($30.1B)'},
        {'label': 'Infrastructure Software', 'value': '42% of FY2024 revenue ($21.5B)'}
    ]),
    
    Paragraph("This structure provides resilience: semiconductors fuel explosive growth during tech upcycles, while software delivers stable, high-margin recurring cash flow."),
    
    Heading("Market Leadership & Strategic Positioning"),
    
    Paragraph("Broadcom is a leader in mission-critical niches:"),
    
    List([
        "<strong>AI Custom ASICs:</strong> Commands an estimated 70–80% market share in custom AI chips, working closely with hyperscalers like Google, Meta, Microsoft, OpenAI, and ByteDance.",
        "<strong>Data Center Networking:</strong> Forms a duopoly with NVIDIA in high-speed Ethernet switches, essential for scaling AI clusters.",
        "<strong>Geographic Focus:</strong> ~55% of revenue comes from North America, reflecting deep ties with U.S. tech giants."
    ]),
    
    Chart("confidence_gauge", "gauge"),
    Chart("risk_gauge", "gauge"),
]

if __name__ == "__main__":
    print("🔧 Universal Content Renderer\n")
    
    # Test HTML rendering
    html = render_to_html(executive_summary_blocks)
    print("HTML Output (first 500 chars):")
    print(html[:500])
    print("\n" + "="*70 + "\n")
    
    # Test React data
    react_data = render_to_react_data(executive_summary_blocks)
    print("React Data (first 2 blocks):")
    import json
    print(json.dumps(react_data[:2], indent=2))
    
    print("\n✅ Universal renderer working!")
