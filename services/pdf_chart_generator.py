"""
Professional PDF Generator with Charts
Converts report HTML + chart data to institutional-quality PDF
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO
import base64
from typing import Dict, Any, List
import numpy as np

# Set professional style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 10

class ChartImageGenerator:
    """Generate chart images for PDF embedding"""
    
    @staticmethod
    def generate_gauge_chart(value: float, title: str, color: str = '#0088FE') -> str:
        """Generate gauge chart as base64 image"""
        fig, ax = plt.subplots(figsize=(4, 3))
        
        # Create gauge
        theta = np.linspace(0, np.pi, 100)
        r = np.ones_like(theta)
        
        ax = plt.subplot(111, projection='polar')
        ax.plot(theta, r, color='#e5e7eb', linewidth=20)
        
        # Fill to value
        value_theta = np.linspace(0, np.pi * (value / 100), 100)
        ax.plot(value_theta, r[:len(value_theta)], color=color, linewidth=20)
        
        # Add value text
        ax.text(np.pi/2, 0.5, f'{value}%', ha='center', va='center', 
                fontsize=20, fontweight='bold')
        
        ax.set_ylim(0, 1)
        ax.axis('off')
        plt.title(title, fontsize=12, fontweight='bold', pad=20)
        
        return ChartImageGenerator._fig_to_base64(fig)
    
    @staticmethod
    def generate_bar_chart(data: List[Dict], x_key: str, y_key: str, title: str) -> str:
        """Generate bar chart as base64 image"""
        fig, ax = plt.subplots(figsize=(8, 4))
        
        x_values = [str(item[x_key]) for item in data]
        y_values = [float(item[y_key]) for item in data]
        
        bars = ax.bar(range(len(x_values)), y_values, color='#0088FE', alpha=0.8)
        ax.set_xticks(range(len(x_values)))
        ax.set_xticklabels(x_values)
        
        # Add value labels on bars
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(i, height,
                   f'{height:.1f}',
                   ha='center', va='bottom', fontsize=9)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(x_key.replace('_', ' ').title(), fontsize=11)
        ax.set_ylabel(y_key.replace('_', ' ').title(), fontsize=11)
        ax.grid(axis='y', alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return ChartImageGenerator._fig_to_base64(fig)
    
    @staticmethod
    def generate_line_chart(data: List[Dict], x_key: str, y_key: str, title: str) -> str:
        """Generate line chart as base64 image"""
        fig, ax = plt.subplots(figsize=(8, 4))
        
        x_values = [str(item[x_key]) for item in data]
        y_values = [float(item[y_key]) for item in data]
        
        ax.plot(range(len(x_values)), y_values, marker='o', linewidth=2, 
                markersize=8, color='#0088FE')
        ax.set_xticks(range(len(x_values)))
        ax.set_xticklabels(x_values)
        
        # Add value labels
        for i, (x, y) in enumerate(zip(range(len(x_values)), y_values)):
            ax.text(i, y, f'{y:.1f}', ha='center', va='bottom', fontsize=9)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.set_xlabel(x_key.replace('_', ' ').title(), fontsize=11)
        ax.set_ylabel(y_key.replace('_', ' ').title(), fontsize=11)
        ax.grid(alpha=0.3)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        return ChartImageGenerator._fig_to_base64(fig)
    
    @staticmethod
    def generate_pie_chart(data: List[Dict], label_key: str, value_key: str, title: str) -> str:
        """Generate pie chart as base64 image"""
        fig, ax = plt.subplots(figsize=(6, 6))
        
        labels = [item[label_key] for item in data]
        values = [item[value_key] for item in data]
        
        colors = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8']
        
        wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                           colors=colors, startangle=90)
        
        # Style text
        for text in texts:
            text.set_fontsize(10)
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        plt.tight_layout()
        
        return ChartImageGenerator._fig_to_base64(fig)
    
    @staticmethod
    def generate_heatmap(data: Dict, title: str) -> str:
        """Generate heatmap for DCF sensitivity"""
        fig, ax = plt.subplots(figsize=(8, 5))
        
        values = np.array(data['values'])
        
        im = ax.imshow(values, cmap='RdYlGn', aspect='auto')
        
        # Set ticks
        ax.set_xticks(np.arange(len(data['growth'])))
        ax.set_yticks(np.arange(len(data['wacc'])))
        ax.set_xticklabels([f"{g}%" for g in data['growth']])
        ax.set_yticklabels([f"{w}%" for w in data['wacc']])
        
        # Add value annotations
        for i in range(len(data['wacc'])):
            for j in range(len(data['growth'])):
                text = ax.text(j, i, f'${values[i, j]:.0f}',
                             ha="center", va="center", color="black", fontsize=9)
        
        ax.set_xlabel('Growth Rate', fontsize=11, fontweight='bold')
        ax.set_ylabel('WACC', fontsize=11, fontweight='bold')
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        
        plt.colorbar(im, ax=ax, label='Price Target ($)')
        plt.tight_layout()
        
        return ChartImageGenerator._fig_to_base64(fig)
    
    @staticmethod
    def _fig_to_base64(fig) -> str:
        """Convert matplotlib figure to base64 string"""
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        return f'data:image/png;base64,{img_base64}'


def blocks_to_html(blocks):
    """Convert structured blocks to HTML"""
    html_parts = []
    
    for block in blocks:
        block_type = block.get('type')
        
        if block_type == 'paragraph':
            html_parts.append(f"<p>{block['content']}</p>")
        
        elif block_type == 'heading':
            level = block.get('level', 3)
            html_parts.append(f"<h{level}>{block['content']}</h{level}>")
        
        elif block_type == 'list':
            items_html = ''.join([f"<li>{item}</li>" for item in block['items']])
            html_parts.append(f"<ul>{items_html}</ul>")
        
        elif block_type == 'table':
            rows_html = ''
            for row in block['rows']:
                rows_html += f'''<tr>
<td><strong>{row['label']}</strong></td>
<td>{row['value']}</td>
</tr>'''
            html_parts.append(f'<table class="data-table">{rows_html}</table>')
        
        elif block_type == 'chart':
            # Chart placeholder - will be replaced with actual chart image
            html_parts.append(f'<div class="chart-placeholder" data-chart-id="{block.get("chartId", "")}"></div>')
    
    return '\n\n'.join(html_parts)


def generate_pdf_with_charts(report_data: Dict[str, Any]) -> bytes:
    """Generate complete PDF with embedded charts"""
    from weasyprint import HTML
    
    chart_gen = ChartImageGenerator()
    chart_data = report_data.get('chart_data', {})
    sections = report_data.get('sections', {})
    ticker = report_data.get('ticker', 'Report')
    company_name = report_data.get('company_name', ticker)
    
    # Generate chart images
    chart_images = {}
    
    # Executive Summary Charts
    if 'executive_summary' in chart_data:
        exec_data = chart_data['executive_summary']
        if 'recommendation' in exec_data:
            rec = exec_data['recommendation']
            chart_images['confidence_gauge'] = chart_gen.generate_gauge_chart(
                rec['confidence'], 'Investment Confidence', '#0088FE'
            )
            risk_value = {'Low': 25, 'Medium': 50, 'High': 75}.get(rec['risk_level'], 50)
            risk_color = {'Low': '#00C49F', 'Medium': '#FFBB28', 'High': '#FF8042'}.get(rec['risk_level'], '#FFBB28')
            chart_images['risk_gauge'] = chart_gen.generate_gauge_chart(
                risk_value, 'Risk Level', risk_color
            )
    
    # Financial Analysis Charts
    if 'financial_analysis' in chart_data:
        fin_data = chart_data['financial_analysis']
        if 'revenue_trend' in fin_data:
            chart_images['revenue_trend'] = chart_gen.generate_line_chart(
                fin_data['revenue_trend'], 'year', 'revenue', 'Revenue Trend'
            )
        if 'segment_breakdown' in fin_data:
            chart_images['segment_pie'] = chart_gen.generate_pie_chart(
                fin_data['segment_breakdown'], 'segment', 'revenue', 'Revenue by Segment'
            )
    
    # Valuation Charts
    if 'valuation_analysis' in chart_data:
        val_data = chart_data['valuation_analysis']
        if 'peer_comparison' in val_data:
            chart_images['peer_comparison'] = chart_gen.generate_bar_chart(
                val_data['peer_comparison'], 'company', 'pe', 'P/E Ratio Comparison'
            )
        if 'dcf_sensitivity' in val_data:
            chart_images['dcf_heatmap'] = chart_gen.generate_heatmap(
                val_data['dcf_sensitivity'], 'DCF Sensitivity Analysis'
            )
    
    # Build HTML with embedded charts
    html_content = build_pdf_html(report_data, chart_images)
    
    # Convert to PDF
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes


def build_pdf_html(report_data: Dict, chart_images: Dict[str, str]) -> str:
    """Build complete HTML for PDF with embedded charts"""
    
    ticker = report_data.get('ticker', 'Report')
    company_name = report_data.get('company_name', ticker)
    sections = report_data.get('sections', {})
    statistics = report_data.get('statistics', {})
    quality_score = report_data.get('quality_score', 0)
    
    html = f'''<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        {get_pdf_css()}
    </style>
</head>
<body>
    <!-- Cover Page -->
    <div class="cover-page">
        <h1 class="cover-title">{company_name}</h1>
        <h2 class="cover-subtitle">({ticker})</h2>
        <h3 class="cover-type">Comprehensive Investment Analysis Report</h3>
        
        <div class="cover-stats">
            <div class="stat-box">
                <div class="stat-label">Sections</div>
                <div class="stat-value">{statistics.get('total_sections', 9)}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Total Words</div>
                <div class="stat-value">{statistics.get('total_words', 0):,}</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Quality Score</div>
                <div class="stat-value">{quality_score}%</div>
            </div>
        </div>
        
        <div class="cover-footer">
            <p>Generated by MarketMind Pro</p>
            <p>AI-Powered Stock Research Platform</p>
        </div>
    </div>
    
    <!-- Table of Contents -->
    <div class="toc-page">
        <h2>Table of Contents</h2>
        <ul class="toc-list">
'''
    
    # Add TOC entries
    for i, (key, section) in enumerate(sections.items(), 1):
        title = section.get('title', key.replace('_', ' ').title())
        html += f'            <li><span class="toc-number">{i}.</span> {title}</li>\n'
    
    html += '''        </ul>
    </div>
    
    <!-- Report Sections -->
'''
    
    # Add each section with charts
    for section_key, section_data in sections.items():
        title = section_data.get('title', section_key.replace('_', ' ').title())
        subtitle = section_data.get('subtitle', '')
        
        # Check if using structured blocks or HTML content
        if 'blocks' in section_data:
            # New structured format
            content = blocks_to_html(section_data['blocks'])
        else:
            # Old HTML format (fallback)
            content = section_data.get('content', '')
        
        html += f'''
    <div class="section">
        <h2 class="section-title">{title}</h2>
        {f'<p class="section-subtitle">{subtitle}</p>' if subtitle else ''}
        
        <!-- Section Charts -->
'''
        
        # Add relevant charts for this section
        if section_key == 'executive_summary':
            if 'confidence_gauge' in chart_images:
                html += f'<div class="chart-row"><img src="{chart_images["confidence_gauge"]}" class="chart-img" /></div>\n'
            if 'risk_gauge' in chart_images:
                html += f'<div class="chart-row"><img src="{chart_images["risk_gauge"]}" class="chart-img" /></div>\n'
        
        elif section_key == 'financial_analysis':
            if 'revenue_trend' in chart_images:
                html += f'<div class="chart-row"><img src="{chart_images["revenue_trend"]}" class="chart-img" /></div>\n'
            if 'segment_pie' in chart_images:
                html += f'<div class="chart-row"><img src="{chart_images["segment_pie"]}" class="chart-img" /></div>\n'
        
        elif section_key == 'valuation_analysis':
            if 'peer_comparison' in chart_images:
                html += f'<div class="chart-row"><img src="{chart_images["peer_comparison"]}" class="chart-img" /></div>\n'
            if 'dcf_heatmap' in chart_images:
                html += f'<div class="chart-row"><img src="{chart_images["dcf_heatmap"]}" class="chart-img" /></div>\n'
        
        html += f'''
        <!-- Section Content -->
        <div class="section-content">
            {content}
        </div>
    </div>
'''
    
    html += '''
</body>
</html>
'''
    
    return html


def get_pdf_css() -> str:
    """Professional CSS for PDF generation"""
    return '''
        @page {
            size: A4;
            margin: 2cm 2cm 3cm 2cm;
            
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 9pt;
                color: #6b7280;
            }
            
            @bottom-right {
                content: "MarketMind Pro";
                font-size: 9pt;
                color: #6b7280;
            }
        }
        
        body {
            font-family: 'Inter', 'Arial', sans-serif;
            font-size: 11pt;
            line-height: 1.6;
            color: #1a1a1a;
        }
        
        /* Cover Page */
        .cover-page {
            page-break-after: always;
            text-align: center;
            padding-top: 8cm;
        }
        
        .cover-title {
            font-size: 28pt;
            font-weight: 700;
            color: #0066cc;
            margin-bottom: 0.5cm;
        }
        
        .cover-subtitle {
            font-size: 20pt;
            font-weight: 600;
            color: #4a4a4a;
            margin-bottom: 1cm;
        }
        
        .cover-type {
            font-size: 14pt;
            color: #6b7280;
            margin-bottom: 3cm;
        }
        
        .cover-stats {
            display: flex;
            justify-content: center;
            gap: 2cm;
            margin-bottom: 4cm;
        }
        
        .stat-box {
            text-align: center;
        }
        
        .stat-label {
            font-size: 10pt;
            color: #6b7280;
            margin-bottom: 0.3cm;
        }
        
        .stat-value {
            font-size: 18pt;
            font-weight: 700;
            color: #0066cc;
        }
        
        .cover-footer {
            color: #6b7280;
            font-size: 10pt;
        }
        
        /* Table of Contents */
        .toc-page {
            page-break-after: always;
            padding-top: 2cm;
        }
        
        .toc-page h2 {
            font-size: 18pt;
            font-weight: 700;
            color: #0066cc;
            border-bottom: 2pt solid #0066cc;
            padding-bottom: 0.3cm;
            margin-bottom: 1cm;
        }
        
        .toc-list {
            list-style: none;
            padding: 0;
        }
        
        .toc-list li {
            padding: 0.3cm 0;
            border-bottom: 1pt solid #e5e7eb;
            font-size: 11pt;
        }
        
        .toc-number {
            display: inline-block;
            width: 1.5cm;
            font-weight: 600;
            color: #0066cc;
        }
        
        /* Sections */
        .section {
            page-break-before: always;
            margin-bottom: 1cm;
        }
        
        .section-title {
            font-size: 16pt;
            font-weight: 700;
            color: #0066cc;
            border-bottom: 2pt solid #0066cc;
            padding-bottom: 0.3cm;
            margin-bottom: 0.5cm;
        }
        
        .section-subtitle {
            font-size: 12pt;
            font-weight: 500;
            color: #4a4a4a;
            font-style: italic;
            margin-bottom: 0.8cm;
        }
        
        .section-content h3 {
            font-size: 13pt;
            font-weight: 600;
            margin-top: 0.8cm;
            margin-bottom: 0.4cm;
            color: #1a1a1a;
        }
        
        .section-content p {
            margin-bottom: 0.4cm;
            text-align: justify;
        }
        
        .section-content ul {
            margin: 0.4cm 0;
            padding-left: 1cm;
        }
        
        .section-content li {
            margin-bottom: 0.2cm;
        }
        
        /* Tables */
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 0.5cm 0;
            font-size: 10pt;
        }
        
        table td {
            padding: 0.2cm 0.3cm;
            border: 1pt solid #e5e7eb;
            vertical-align: top;
        }
        
        table td:first-child {
            font-weight: 600;
            background-color: #f9fafb;
            width: 40%;
        }
        
        /* Charts */
        .chart-row {
            margin: 0.8cm 0;
            text-align: center;
            page-break-inside: avoid;
        }
        
        .chart-img {
            max-width: 100%;
            height: auto;
        }
    '''


if __name__ == "__main__":
    # Test chart generation
    gen = ChartImageGenerator()
    
    # Test gauge
    img = gen.generate_gauge_chart(94, "Test Gauge", "#0088FE")
    print(f"✅ Generated gauge chart: {len(img)} bytes")
    
    # Test bar chart
    data = [
        {"year": "2022", "revenue": 33.2},
        {"year": "2023", "revenue": 35.8},
        {"year": "2024", "revenue": 51.6}
    ]
    img = gen.generate_bar_chart(data, "year", "revenue", "Revenue Trend")
    print(f"✅ Generated bar chart: {len(img)} bytes")
    
    print("\n✅ Chart generator ready!")
