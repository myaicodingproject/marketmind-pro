# PDF Quality Validation Implementation

## Minimal Quality Validation System

```python
import PyPDF2
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
import re

class PDFQualityValidator:
    def __init__(self):
        self.min_score = 85
        self.quality_criteria = {
            'structure': 25,    # TOC, bookmarks, navigation
            'typography': 20,   # Font consistency, sizing
            'content': 25,      # Completeness, accuracy
            'technical': 15,    # PDF standards compliance
            'accessibility': 15 # Screen reader compatibility
        }
    
    def validate_report(self, pdf_path):
        scores = {
            'structure': self._check_structure(pdf_path),
            'typography': self._check_typography(pdf_path),
            'content': self._check_content(pdf_path),
            'technical': self._check_technical(pdf_path),
            'accessibility': self._check_accessibility(pdf_path)
        }
        
        total_score = sum(scores[k] * self.quality_criteria[k] / 100 
                         for k in scores)
        
        return {
            'total_score': total_score,
            'category_scores': scores,
            'passed': total_score >= self.min_score,
            'issues': self._identify_issues(scores)
        }
    
    def _check_structure(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Check for bookmarks/outline
            has_bookmarks = len(reader.outline) > 0
            
            # Check page count (15-40 pages for institutional reports)
            page_count = len(reader.pages)
            page_score = 100 if 15 <= page_count <= 40 else 70
            
            # Check for metadata
            has_metadata = bool(reader.metadata)
            
            structure_score = (
                (40 if has_bookmarks else 0) +
                (page_score * 0.4) +
                (20 if has_metadata else 0)
            )
            
            return min(100, structure_score)
    
    def _check_typography(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            font_sizes = []
            fonts_used = set()
            
            for page in pdf.pages[:5]:  # Sample first 5 pages
                for char in page.chars:
                    font_sizes.append(char['size'])
                    fonts_used.add(char['fontname'])
            
            # Check font consistency (max 4 different fonts)
            font_consistency = 100 if len(fonts_used) <= 4 else 70
            
            # Check font size range (9-14pt for body text)
            appropriate_sizes = [s for s in font_sizes if 9 <= s <= 14]
            size_score = (len(appropriate_sizes) / len(font_sizes)) * 100
            
            return (font_consistency * 0.6 + size_score * 0.4)
    
    def _check_content(self, pdf_path):
        with pdfplumber.open(pdf_path) as pdf:
            text = ""
            table_count = 0
            
            for page in pdf.pages:
                text += page.extract_text() or ""
                tables = page.extract_tables()
                table_count += len(tables) if tables else 0
            
            # Check for required sections
            required_sections = [
                'executive summary', 'financial analysis', 
                'valuation', 'risk', 'recommendation'
            ]
            
            sections_found = sum(1 for section in required_sections 
                               if section.lower() in text.lower())
            section_score = (sections_found / len(required_sections)) * 100
            
            # Check for adequate tables (minimum 5)
            table_score = 100 if table_count >= 5 else (table_count / 5) * 100
            
            # Check word count (institutional reports: 8000-15000 words)
            word_count = len(text.split())
            word_score = 100 if 8000 <= word_count <= 15000 else 70
            
            return (section_score * 0.5 + table_score * 0.3 + word_score * 0.2)
    
    def _check_technical(self, pdf_path):
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Check PDF version (should be 1.4 or higher)
            version_ok = reader.pdf_header.decode().find('1.') != -1
            
            # Check for encryption (should be None for accessibility)
            not_encrypted = not reader.is_encrypted
            
            # Check for form fields (interactive elements)
            has_forms = any(page.get('/Annots') for page in reader.pages)
            
            technical_score = (
                (40 if version_ok else 0) +
                (40 if not_encrypted else 0) +
                (20 if has_forms else 0)
            )
            
            return technical_score
    
    def _check_accessibility(self, pdf_path):
        # Basic accessibility checks
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            
            # Check for tagged PDF structure
            has_structure = '/StructTreeRoot' in reader.trailer.get('/Root', {})
            
            # Check metadata for accessibility info
            metadata = reader.metadata or {}
            has_title = '/Title' in metadata
            has_author = '/Author' in metadata
            
            accessibility_score = (
                (60 if has_structure else 0) +
                (20 if has_title else 0) +
                (20 if has_author else 0)
            )
            
            return accessibility_score
    
    def _identify_issues(self, scores):
        issues = []
        for category, score in scores.items():
            if score < 80:
                issues.append(f"Low {category} score: {score:.1f}")
        return issues

# Institutional PDF Generator
class InstitutionalPDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        from reportlab.lib.styles import ParagraphStyle
        
        # Institutional typography standards
        self.styles.add(ParagraphStyle(
            name='InstitutionalHeading',
            parent=self.styles['Heading1'],
            fontName='Helvetica-Bold',
            fontSize=14,
            spaceAfter=12,
            textColor=colors.black
        ))
        
        self.styles.add(ParagraphStyle(
            name='FinancialData',
            fontName='Courier',
            fontSize=9,
            alignment=1,  # Center alignment
            spaceAfter=6
        ))
    
    def create_institutional_table(self, data, headers):
        # Professional table styling for financial data
        table = Table([headers] + data)
        table.setStyle(TableStyle([
            # Header styling
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#2E4057')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('BOTTOMPADDING', (0,0), (-1,0), 12),
            
            # Data styling
            ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#F8F9FA')),
            ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
            ('FONTSIZE', (0,1), (-1,-1), 9),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            
            # Alternating row colors
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#F8F9FA')])
        ]))
        
        return table
    
    def generate_report(self, content_data, output_path):
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            topMargin=72,
            bottomMargin=72,
            leftMargin=54,
            rightMargin=54
        )
        
        story = []
        
        # Add institutional-quality content
        for section in content_data:
            if section['type'] == 'heading':
                story.append(Paragraph(section['text'], self.styles['InstitutionalHeading']))
            elif section['type'] == 'paragraph':
                story.append(Paragraph(section['text'], self.styles['Normal']))
            elif section['type'] == 'table':
                story.append(self.create_institutional_table(
                    section['data'], section['headers']
                ))
        
        doc.build(story)
        return output_path

# Usage Example
def validate_and_improve_pdf(pdf_path):
    validator = PDFQualityValidator()
    results = validator.validate_report(pdf_path)
    
    if results['passed']:
        print(f"✅ PDF Quality Score: {results['total_score']:.1f}/100")
        return True
    else:
        print(f"❌ PDF Quality Score: {results['total_score']:.1f}/100")
        print("Issues found:")
        for issue in results['issues']:
            print(f"  - {issue}")
        return False
```

## Quality Gate Integration

```python
# Minimal integration for MarketMind Pro
def generate_with_quality_gates(symbol, options):
    # Generate initial report
    pdf_path = generate_base_report(symbol, options)
    
    # Validate quality
    validator = PDFQualityValidator()
    quality_results = validator.validate_report(pdf_path)
    
    # Retry if quality is insufficient
    if not quality_results['passed']:
        pdf_path = regenerate_with_improvements(symbol, options, quality_results)
        quality_results = validator.validate_report(pdf_path)
    
    return pdf_path, quality_results

def regenerate_with_improvements(symbol, options, quality_issues):
    # Focus improvements on failing categories
    improvements = {
        'structure': add_bookmarks_and_toc,
        'typography': standardize_fonts,
        'content': enhance_content_depth,
        'technical': optimize_pdf_structure,
        'accessibility': add_accessibility_features
    }
    
    for category, score in quality_issues['category_scores'].items():
        if score < 80:
            improvements[category](symbol, options)
    
    return generate_base_report(symbol, options)
```