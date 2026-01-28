# 🏗️ CLEAN SYSTEM REBUILD PLAN
## MarketMind Pro - Unified Report System (No Patches)

---

## 🎯 PHILOSOPHY: BUILD A SYSTEM, NOT PATCHES

**Current Problem:**
- Multiple PDF generators (professional_pdf_generator.py, ultra_pdf_generator.py, etc.)
- Regex hacks to clean content
- Separate styling for web and PDF
- Fragmented architecture

**New Approach:**
- **Single source of truth** for content and styling
- **Clean data flow** from Kiro CLI → Database → Rendering
- **Unified templates** for web and PDF
- **No regex hacks** - proper data structures

---

## 🏛️ SYSTEM ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────┐
│                    KIRO CLI AGENTS                          │
│              (Generate Raw Content)                         │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              ENHANCED PIPELINE                              │
│   (Polish with GPT-4o-mini + Store in PostgreSQL)          │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              UNIFIED REPORT SERVICE                         │
│   • Clean data structures (Pydantic models)                 │
│   • Extract structured data (tables, metrics, charts)       │
│   • Generate chart images (Plotly)                          │
│   • Store everything in database                            │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ↓
        ┌────────────┴────────────┐
        │                         │
        ↓                         ↓
┌──────────────┐          ┌──────────────┐
│   WEB VIEW   │          │   PDF VIEW   │
│              │          │              │
│ • React      │          │ • WeasyPrint │
│ • Recharts   │          │ • Same CSS   │
│ • Interactive│          │ • Static     │
└──────────────┘          └──────────────┘
```

---

## 📋 PHASE 1: CLEAN DATA ARCHITECTURE (4 hours)

### **Goal:** Proper data structures, no regex hacks

### **1.1 Enhanced Data Models (1 hour)**

**File:** `enhanced_models.py` (UPDATE)

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime

class TableData(BaseModel):
    """Structured table data"""
    headers: List[str]
    rows: List[List[str]]
    caption: Optional[str] = None
    table_type: str = "financial"  # financial, metrics, comparison

class ChartData(BaseModel):
    """Structured chart data"""
    chart_type: str  # line, bar, pie, scatter, heatmap
    title: str
    data: Dict[str, List]  # {x: [...], y: [...]}
    config: Dict = {}  # Colors, labels, etc.

class MetricData(BaseModel):
    """Key metric data"""
    label: str
    value: float
    unit: str  # $, %, B, M
    change: Optional[float] = None
    trend: Optional[str] = None  # up, down, stable

class ReportSection(BaseModel):
    """Enhanced section with structured data"""
    section_type: str
    title: str
    content: str  # Clean markdown
    tables: List[TableData] = []
    charts: List[ChartData] = []
    metrics: List[MetricData] = []
    raw_content: str  # Original from Kiro CLI
    polished_content: Optional[str] = None
    
class EnhancedReport(BaseModel):
    """Complete report with all data"""
    id: int
    ticker: str
    title: str
    sections: Dict[str, ReportSection]
    generated_at: datetime
    chart_images: Dict[str, Dict[str, bytes]] = {}  # Section → Chart → PNG
```

**Why This Matters:**
- ✅ Clean data structures
- ✅ No string parsing needed
- ✅ Type-safe
- ✅ Easy to query and transform

---

### **1.2 Content Parser Service (2 hours)**

**File:** `content_parser_service.py` (NEW - REPLACE data_extraction_service.py)

```python
class ContentParserService:
    """Parse Kiro CLI output into structured data"""
    
    def parse_section(self, content: str) -> ReportSection:
        """Parse section content into structured data"""
        return ReportSection(
            content=self.extract_clean_text(content),
            tables=self.extract_tables(content),
            charts=self.identify_chart_opportunities(content),
            metrics=self.extract_metrics(content)
        )
    
    def extract_tables(self, content: str) -> List[TableData]:
        """Extract markdown tables to structured data"""
        # Use markdown parser (not regex)
        import markdown
        from markdown.extensions.tables import TableExtension
        
        md = markdown.Markdown(extensions=[TableExtension()])
        # Parse properly, return TableData objects
    
    def extract_metrics(self, content: str) -> List[MetricData]:
        """Extract key metrics to structured data"""
        # Use NLP or structured patterns
        # Return MetricData objects
    
    def identify_chart_opportunities(self, content: str) -> List[ChartData]:
        """Identify where charts should be generated"""
        # Look for time series data
        # Look for comparisons
        # Look for distributions
        # Return ChartData configs
```

**Why This Matters:**
- ✅ Proper parsing (not regex hacks)
- ✅ Returns structured data
- ✅ Reusable across system
- ✅ Testable

---

### **1.3 Update Enhanced Pipeline (1 hour)**

**File:** `enhanced_service.py` (UPDATE)

```python
async def process_raw_section(self, report_id, section_type, raw_content, ...):
    """Process section through complete pipeline"""
    
    # 1. Parse content into structured data
    parsed_section = content_parser.parse_section(raw_content)
    
    # 2. Polish text content (GPT-4o-mini)
    polished_content = await polishing_service.polish(parsed_section.content)
    
    # 3. Generate charts from structured data
    chart_images = await chart_service.generate_images(parsed_section.charts)
    
    # 4. Store everything in database
    await db_service.store_section(
        report_id,
        section_type,
        parsed_section,
        polished_content,
        chart_images
    )
```

**Why This Matters:**
- ✅ Clean pipeline
- ✅ Each step has single responsibility
- ✅ No hacks or workarounds
- ✅ Proper data flow

---

## 📋 PHASE 2: UNIFIED RENDERING ENGINE (3 hours)

### **Goal:** Single template system for web and PDF

### **2.1 Template Service (2 hours)**

**File:** `template_service.py` (NEW)

```python
class TemplateService:
    """Unified template rendering for web and PDF"""
    
    def __init__(self):
        self.jinja_env = Environment(
            loader=FileSystemLoader('app/templates')
        )
    
    def render_section(self, section: ReportSection, format: str) -> str:
        """Render section for web or PDF"""
        template = self.jinja_env.get_template('section.html')
        
        return template.render(
            section=section,
            format=format,  # 'web' or 'pdf'
            tables=section.tables,
            metrics=section.metrics,
            chart_placeholders=section.charts  # Web: Recharts, PDF: images
        )
    
    def render_report(self, report: EnhancedReport, format: str) -> str:
        """Render complete report"""
        template = self.jinja_env.get_template('report.html')
        
        return template.render(
            report=report,
            format=format,
            css_files=self.get_css_files(format)
        )
    
    def get_css_files(self, format: str) -> List[str]:
        """Get appropriate CSS files"""
        base_css = [
            'typography.css',
            'colors.css',
            'tables.css',
            'sections.css',
            'markdown.css'
        ]
        
        if format == 'pdf':
            base_css.append('print.css')
        
        return base_css
```

**Why This Matters:**
- ✅ Single template system
- ✅ Format-aware rendering
- ✅ No duplication
- ✅ Easy to maintain

---

### **2.2 Unified Templates (1 hour)**

**File:** `app/templates/section.html` (NEW)

```html
<div class="report-section">
  <div class="section-header">
    <h2 class="section-title">{{ section.title }}</h2>
  </div>
  
  <div class="section-content markdown-content">
    <!-- Clean content (no markdown symbols) -->
    {{ section.content | safe }}
  </div>
  
  <!-- Metrics Cards -->
  {% if section.metrics %}
  <div class="metrics-grid">
    {% for metric in section.metrics %}
    <div class="metric-card">
      <div class="metric-label">{{ metric.label }}</div>
      <div class="metric-value">{{ metric.value }}{{ metric.unit }}</div>
      {% if metric.change %}
      <div class="metric-change {{ 'positive' if metric.change > 0 else 'negative' }}">
        {{ metric.change }}%
      </div>
      {% endif %}
    </div>
    {% endfor %}
  </div>
  {% endif %}
  
  <!-- Tables -->
  {% if section.tables %}
  {% for table in section.tables %}
  <table class="financial-table">
    <thead>
      <tr>
        {% for header in table.headers %}
        <th>{{ header }}</th>
        {% endfor %}
      </tr>
    </thead>
    <tbody>
      {% for row in table.rows %}
      <tr>
        {% for cell in row %}
        <td class="{{ 'numeric' if cell | is_numeric else '' }}">
          {{ cell }}
        </td>
        {% endfor %}
      </tr>
      {% endfor %}
    </tbody>
  </table>
  {% endfor %}
  {% endif %}
  
  <!-- Charts -->
  {% if format == 'web' %}
    <!-- Web: Recharts component placeholder -->
    <div class="chart-placeholder" data-section="{{ section.section_type }}">
      <!-- React will render Recharts here -->
    </div>
  {% else %}
    <!-- PDF: Static images -->
    {% for chart in section.charts %}
    <div class="chart-container">
      <h3>{{ chart.title }}</h3>
      <img src="data:image/png;base64,{{ chart.image }}" 
           alt="{{ chart.title }}"
           class="chart-image">
    </div>
    {% endfor %}
  {% endif %}
</div>
```

**Why This Matters:**
- ✅ Same structure for web and PDF
- ✅ Format-aware (web vs PDF)
- ✅ Clean, no hacks
- ✅ Professional output

---

## 📋 PHASE 3: CHART GENERATION SYSTEM (4 hours)

### **Goal:** Professional chart images for PDF, data for web

### **3.1 Chart Image Service (3 hours)**

**File:** `chart_image_service.py` (NEW - CLEAN)

```python
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import base64
from io import BytesIO

class ChartImageService:
    """Generate professional chart images"""
    
    def __init__(self):
        # Use same colors as frontend CSS
        self.colors = {
            'primary': '#2563eb',
            'success': '#10b981',
            'danger': '#ef4444',
            'gray': '#6b7280'
        }
        
        self.layout_defaults = {
            'font': {'family': 'Inter, sans-serif', 'size': 12},
            'plot_bgcolor': 'white',
            'paper_bgcolor': 'white',
            'width': 800,
            'height': 400,
            'margin': {'l': 60, 'r': 40, 't': 60, 'b': 60}
        }
    
    def generate_revenue_chart(self, data: ChartData) -> bytes:
        """Generate revenue trend chart"""
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.data['years'],
            y=data.data['revenue'],
            mode='lines+markers',
            line=dict(color=self.colors['primary'], width=3),
            marker=dict(size=8),
            name='Revenue'
        ))
        fig.update_layout(**self.layout_defaults, title=data.title)
        return self._fig_to_png(fig)
    
    def generate_margin_chart(self, data: ChartData) -> bytes:
        """Generate margin comparison chart"""
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=data.data['metrics'],
            y=data.data['values'],
            marker_color=self.colors['primary']
        ))
        fig.update_layout(**self.layout_defaults, title=data.title)
        return self._fig_to_png(fig)
    
    def _fig_to_png(self, fig) -> bytes:
        """Convert plotly figure to PNG bytes"""
        img_bytes = fig.to_image(format='png', scale=2)
        return base64.b64encode(img_bytes).decode('utf-8')
```

**Why This Matters:**
- ✅ Clean, focused service
- ✅ Uses same colors as frontend
- ✅ Professional quality
- ✅ Reusable

---

### **3.2 Integrate with Report Generation (1 hour)**

**File:** `complete_production_system.py` (UPDATE)

```python
async def generate_report(ticker: str):
    """Clean report generation flow"""
    
    # 1. Generate content with Kiro CLI
    raw_sections = await kiro_service.generate_all_sections(ticker)
    
    # 2. Process through enhanced pipeline
    enhanced_report_id = await enhanced_service.create_enhanced_report(ticker)
    
    for section_name, raw_content in raw_sections.items():
        # Parse into structured data
        parsed = content_parser.parse_section(raw_content)
        
        # Polish content
        polished = await polishing_service.polish(parsed.content)
        
        # Generate chart images
        chart_images = {}
        for chart_config in parsed.charts:
            image = await chart_service.generate_image(chart_config)
            chart_images[chart_config.title] = image
        
        # Store everything
        await enhanced_service.store_section(
            enhanced_report_id,
            section_name,
            parsed,
            polished,
            chart_images
        )
    
    # 3. Retrieve complete report
    report = await enhanced_service.get_enhanced_report(enhanced_report_id)
    
    # 4. Generate outputs
    html = template_service.render_report(report, format='web')
    pdf = template_service.render_report(report, format='pdf')
    
    return report
```

**Why This Matters:**
- ✅ Clear flow
- ✅ No hacks
- ✅ Single pipeline
- ✅ Proper data handling

---

## 📋 PHASE 4: UNIFIED RENDERING (3 hours)

### **Goal:** Same templates for web and PDF

### **4.1 CSS System (1 hour)**

**Files:** Already created by subagents
- `typography.css`
- `colors.css`
- `tables.css`
- `sections.css`
- `markdown.css`

**NEW:** `print.css`
```css
@media print {
  /* Page setup */
  @page {
    size: Letter;
    margin: 1in;
    
    @top-center {
      content: "MarketMind Pro";
      font-size: 10pt;
      color: #6b7280;
    }
    
    @bottom-right {
      content: "Page " counter(page);
      font-size: 10pt;
    }
  }
  
  /* Typography for print */
  body {
    font-family: Georgia, Times, serif;
    font-size: 11pt;
    line-height: 1.4;
  }
  
  h1, h2, h3 {
    font-family: Inter, sans-serif;
  }
  
  /* Page breaks */
  .report-section {
    page-break-before: always;
  }
  
  table {
    page-break-inside: avoid;
  }
  
  .chart-container {
    page-break-inside: avoid;
  }
  
  /* Hide interactive elements */
  .interactive-only {
    display: none;
  }
}
```

---

### **4.2 Template System (2 hours)**

**File:** `app/templates/report.html` (NEW)

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>{{ report.ticker }} - Investment Analysis Report</title>
  
  <!-- Load all CSS -->
  {% for css_file in css_files %}
  <style>
    {{ load_css(css_file) }}
  </style>
  {% endfor %}
</head>
<body>
  <!-- Cover Page (PDF only) -->
  {% if format == 'pdf' %}
  <div class="cover-page">
    <h1>{{ report.ticker }} Investment Analysis</h1>
    <p class="report-date">{{ report.generated_at | format_date }}</p>
    <p class="report-by">MarketMind Pro</p>
  </div>
  
  <!-- Table of Contents -->
  <div class="toc">
    <h2>Table of Contents</h2>
    <ul>
      {% for section_name, section in report.sections.items() %}
      <li>{{ section.title }}</li>
      {% endfor %}
    </ul>
  </div>
  {% endif %}
  
  <!-- Report Sections -->
  {% for section_name, section in report.sections.items() %}
    {{ render_section(section, format) }}
  {% endfor %}
</body>
</html>
```

---

## 📋 PHASE 5: CLEAN INTEGRATION (2 hours)

### **Goal:** Remove old systems, use new clean architecture

### **5.1 Remove Old Code (30 min)**

**Delete/Archive:**
- `professional_pdf_generator.py` (old, hacky)
- `ultra_pdf_generator.py` (if exists)
- All regex cleanup code
- Duplicate PDF generators

**Keep:**
- `enhanced_service.py` (update)
- `database_service.py` (keep)
- `polishing_service.py` (keep)

---

### **5.2 Update Main System (1 hour)**

**File:** `complete_production_system.py` (SIMPLIFY)

```python
# Clean imports
from enhanced_service import enhanced_service
from template_service import template_service
from chart_image_service import chart_service

@app.post("/api/v1/reports/generate")
async def generate_report(request: ReportRequest):
    """Clean report generation"""
    
    # Generate through enhanced pipeline
    report = await enhanced_service.generate_complete_report(
        ticker=request.ticker
    )
    
    # Store in database (already done by enhanced_service)
    
    # Return report ID
    return {
        "report_id": f"report_{report.id}",
        "status": "completed"
    }

@app.get("/api/v1/reports/{report_id}")
async def get_report(report_id: str):
    """Get report data for web view"""
    report = await enhanced_service.get_report(report_id)
    
    # Return structured data for React
    return {
        "sections": report.sections,
        "chart_data": report.chart_data,  # For Recharts
        "metadata": report.metadata
    }

@app.get("/api/v1/reports/{report_id}/pdf")
async def download_pdf(report_id: str):
    """Generate and download PDF"""
    report = await enhanced_service.get_report(report_id)
    
    # Render HTML with PDF format
    html = template_service.render_report(report, format='pdf')
    
    # Convert to PDF
    pdf_bytes = HTML(string=html).write_pdf(
        stylesheets=[CSS(string=css) for css in template_service.get_css()]
    )
    
    return Response(content=pdf_bytes, media_type='application/pdf')
```

**Why This Matters:**
- ✅ Clean, simple code
- ✅ No hacks or workarounds
- ✅ Easy to understand
- ✅ Maintainable

---

### **5.3 Testing & Validation (30 min)**

**Test Cases:**
1. Generate new report
2. Verify data stored in database
3. Check web view renders correctly
4. Download PDF and verify:
   - Styling matches web
   - Tables formatted correctly
   - Charts appear as images
   - Cover page and TOC present
   - Headers/footers on pages

---

## 📋 PHASE 6: DOCUMENTATION (2 hours)

### **Goal:** Document the clean system

### **6.1 Architecture Documentation (1 hour)**

**File:** `SYSTEM_ARCHITECTURE.md` (NEW)

```markdown
# System Architecture

## Data Flow:
Kiro CLI → Enhanced Pipeline → Database → Template Service → Web/PDF

## Components:
- enhanced_service.py: Main orchestration
- content_parser_service.py: Parse content to structured data
- chart_image_service.py: Generate chart images
- template_service.py: Render HTML for web/PDF
- database_service.py: PostgreSQL storage

## No Hacks:
- No regex content cleanup
- No duplicate styling
- No patched code
- Clean architecture
```

---

### **6.2 Developer Guide (1 hour)**

**File:** `DEVELOPER_GUIDE.md` (NEW)

```markdown
# Developer Guide

## Adding New Chart Type:
1. Add ChartData config in content_parser_service.py
2. Implement generation in chart_image_service.py
3. Add Recharts component for web
4. Done - works in both web and PDF

## Updating Styling:
1. Edit CSS file (e.g., colors.css)
2. Rebuild frontend
3. Restart backend
4. Both web and PDF updated

## No Regex Hacks:
- Use Pydantic models for data
- Use proper parsers (markdown library)
- Use structured data throughout
```

---

## ✅ SYSTEM PRINCIPLES

### **1. Single Source of Truth**
- One CSS system (not two)
- One template system (not two)
- One data model (Pydantic)

### **2. Clean Data Flow**
```
Raw Content → Structured Data → Storage → Rendering
```

### **3. No Hacks**
- No regex cleanup
- No string manipulation
- Proper parsing libraries
- Type-safe data structures

### **4. Format-Aware**
- Templates know if rendering for web or PDF
- Appropriate output for each
- Same data, different presentation

### **5. Maintainable**
- Clear code structure
- Single responsibility
- Easy to test
- Well-documented

---

## 📊 COMPARISON: OLD vs NEW

| Aspect | Old System (Patches) | New System (Clean) |
|--------|---------------------|-------------------|
| **PDF Generators** | 3+ different files | 1 unified service |
| **Styling** | Separate web/PDF | Shared CSS |
| **Content Cleanup** | Regex hacks | Proper parsing |
| **Data Structure** | Strings | Pydantic models |
| **Templates** | Duplicated | Unified |
| **Charts** | None in PDF | Both web & PDF |
| **Maintainability** | ❌ Hard | ✅ Easy |
| **Code Quality** | ⚠️ Patched | ✅ Clean |
| **Architecture** | ❌ Fragmented | ✅ Unified |

---

## 🎯 IMPLEMENTATION ORDER

### **Day 1: Foundation (6 hours)**
1. Phase 1.1: Enhanced data models (1h)
2. Phase 1.2: Content parser service (2h)
3. Phase 1.3: Update enhanced pipeline (1h)
4. Phase 2.1: Template service (2h)

### **Day 2: Rendering (5 hours)**
1. Phase 2.2: Unified templates (1h)
2. Phase 4.1: CSS system + print.css (1h)
3. Phase 3.1: Chart image service (3h)

### **Day 3: Integration (3 hours)**
1. Phase 3.2: Integrate charts (1h)
2. Phase 5: Clean integration (2h)

### **Day 4: Documentation (2 hours)**
1. Phase 6: Complete documentation (2h)

**Total: 16 hours** (revised from 14h for proper rebuild)

---

## 🚀 SUCCESS CRITERIA

### **Architecture:**
- ✅ No duplicate code
- ✅ No regex hacks
- ✅ Clean data flow
- ✅ Single source of truth
- ✅ Proper separation of concerns

### **Output Quality:**
- ✅ Web and PDF styling consistent
- ✅ Professional tables in both
- ✅ Charts in both (interactive web, static PDF)
- ✅ Institutional-quality appearance
- ✅ Fast generation (< 10 minutes total)

### **Maintainability:**
- ✅ Easy to update styling (one place)
- ✅ Easy to add chart types
- ✅ Easy to modify templates
- ✅ Well-documented
- ✅ Type-safe with Pydantic

---

## 📝 ACCEPTANCE CRITERIA

**Before Starting Next Phase:**
- [ ] Previous phase complete
- [ ] Tests passing
- [ ] Code reviewed
- [ ] No hacks or workarounds
- [ ] Documentation updated

**Before Deployment:**
- [ ] All phases complete
- [ ] Full system testing
- [ ] Performance validated
- [ ] Documentation complete
- [ ] Old code removed/archived

---

## 🎉 FINAL DELIVERABLE

**A Clean, Professional System:**
- Unified architecture
- Consistent styling
- Professional charts
- Easy to maintain
- No patches or hacks
- Institutional-quality output

**Status:** Ready to implement
**Approach:** Clean rebuild, not patches
**Timeline:** 16 hours (4 days)
**Quality:** Production-grade system

---

**Version:** 2.0 (Clean System)
**Date:** 2026-01-27
**Approved:** Pending
