"""
MarketMind Pro PDF Generator - Core Module
Production-ready PDF generation with charts, tables, and professional styling
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas
from io import BytesIO
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

class MarketMindPDFGenerator:
    def __init__(self, output_path="report.pdf"):
        self.output_path = output_path
        self.doc = SimpleDocTemplate(output_path, pagesize=A4, 
                                   rightMargin=72, leftMargin=72,
                                   topMargin=72, bottomMargin=18)
        self.styles = getSampleStyleSheet()
        self.story = []
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for professional formatting"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=TA_CENTER,
            textColor=colors.HexColor('#1f4e79')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceBefore=20,
            spaceAfter=12,
            textColor=colors.HexColor('#2e75b6')
        ))
        
        self.styles.add(ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=11,
            spaceAfter=12,
            alignment=TA_JUSTIFY
        ))

    def add_cover_page(self, title, subtitle, company_name, date=None):
        """Add professional cover page"""
        if date is None:
            date = datetime.now().strftime("%B %d, %Y")
            
        # Logo placeholder
        self.story.append(Spacer(1, 2*inch))
        
        # Title
        title_para = Paragraph(title, self.styles['CustomTitle'])
        self.story.append(title_para)
        self.story.append(Spacer(1, 0.5*inch))
        
        # Subtitle
        subtitle_para = Paragraph(subtitle, self.styles['Heading3'])
        self.story.append(subtitle_para)
        self.story.append(Spacer(1, 2*inch))
        
        # Company info
        company_para = Paragraph(f"<b>{company_name}</b>", self.styles['Normal'])
        self.story.append(company_para)
        
        date_para = Paragraph(date, self.styles['Normal'])
        self.story.append(date_para)
        
        self.story.append(PageBreak())

    def add_table_of_contents(self, sections):
        """Add table of contents"""
        self.story.append(Paragraph("Table of Contents", self.styles['CustomTitle']))
        self.story.append(Spacer(1, 0.3*inch))
        
        toc_data = []
        for i, section in enumerate(sections, 1):
            toc_data.append([f"{i}. {section['title']}", f"Page {section.get('page', i+2)}"])
        
        toc_table = Table(toc_data, colWidths=[4*inch, 1*inch])
        toc_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ]))
        
        self.story.append(toc_table)
        self.story.append(PageBreak())

    def create_chart(self, data, chart_type='line', title='Chart', width=6, height=4):
        """Create matplotlib chart and return as image"""
        plt.figure(figsize=(width, height))
        plt.style.use('seaborn-v0_8')
        
        if chart_type == 'line':
            plt.plot(data['x'], data['y'], linewidth=2, color='#2e75b6')
        elif chart_type == 'bar':
            plt.bar(data['x'], data['y'], color='#2e75b6', alpha=0.8)
        elif chart_type == 'pie':
            plt.pie(data['values'], labels=data['labels'], autopct='%1.1f%%')
        
        plt.title(title, fontsize=14, fontweight='bold', color='#1f4e79')
        plt.tight_layout()
        
        # Save to BytesIO
        img_buffer = BytesIO()
        plt.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
        img_buffer.seek(0)
        plt.close()
        
        return img_buffer

    def add_chart(self, data, chart_type='line', title='Chart', caption=''):
        """Add chart to PDF"""
        img_buffer = self.create_chart(data, chart_type, title)
        
        # Create temporary file for ReportLab
        temp_path = f"temp_chart_{datetime.now().timestamp()}.png"
        with open(temp_path, 'wb') as f:
            f.write(img_buffer.getvalue())
        
        # Add to story
        img = Image(temp_path, width=5*inch, height=3.5*inch)
        self.story.append(img)
        
        if caption:
            caption_para = Paragraph(f"<i>{caption}</i>", self.styles['Normal'])
            self.story.append(caption_para)
        
        self.story.append(Spacer(1, 0.2*inch))
        
        # Cleanup
        os.remove(temp_path)

    def add_professional_table(self, data, headers, title=''):
        """Add professionally formatted table"""
        if title:
            title_para = Paragraph(title, self.styles['SectionHeader'])
            self.story.append(title_para)
        
        # Prepare table data
        table_data = [headers] + data
        
        # Create table
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e75b6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            
            # Body styling
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*inch))

    def generate(self):
        """Generate the final PDF"""
        self.doc.build(self.story)
        return self.output_path