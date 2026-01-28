# UI/UX Design Specifications

## Visual Analysis from AVGO Report PDF

### Color Palette (Extracted from PDF)
```css
:root {
  /* Primary Colors */
  --primary-blue: #4A90E2;
  --primary-green: #7ED321;
  --primary-purple: #9013FE;
  --primary-orange: #F5A623;
  --primary-red: #D0021B;
  
  /* Secondary Colors */
  --light-blue: #E8F4FD;
  --light-green: #F0F9E8;
  --light-gray: #F8F9FA;
  --dark-gray: #333333;
  --medium-gray: #666666;
  
  /* Chart Colors */
  --chart-nvidia: #76B900;
  --chart-broadcom: #4A90E2;
  --chart-amd: #ED1C24;
  --chart-intel: #0071C5;
}
```

### Typography System
```css
/* Font Hierarchy */
.report-title { 
  font-size: 24px; 
  font-weight: 700; 
  color: var(--dark-gray);
}

.section-header { 
  font-size: 18px; 
  font-weight: 600; 
  color: var(--dark-gray);
}

.subsection-header { 
  font-size: 16px; 
  font-weight: 500; 
  color: var(--medium-gray);
}

.body-text { 
  font-size: 14px; 
  font-weight: 400; 
  line-height: 1.6;
}

.chart-label { 
  font-size: 12px; 
  font-weight: 500;
}
```

## Component Specifications

### 1. Timeline Component (Page 15 Style)
**Visual Requirements:**
- Vertical timeline with colored circles (blue, green, purple, red, orange)
- Event cards with icons and descriptions positioned left/right alternating
- Clean typography with professional spacing
- Smooth animations on scroll
- Responsive design for mobile

```typescript
interface TimelineEvent {
  year: number;
  title: string;
  description: string;
  type: 'founding' | 'ipo' | 'acquisition' | 'milestone';
  icon: string;
  color: string;
}
```

### 2. Data Table Component (Page 30 Style)
**Visual Requirements:**
- Blue header background (#4A90E2)
- Alternating row colors (white/light gray)
- Right-aligned numbers with proper formatting
- Percentage formatting with % symbol
- Hover effects on rows
- Professional typography

```typescript
interface DataTableProps {
  headers: string[];
  rows: Array<{[key: string]: string | number}>;
  highlightColumn?: number;
  showPercentages?: boolean;
}
```

### 3. Business Model Canvas (Page 35 Style)
**Visual Requirements:**
- Colored rectangular sections (green, pink, blue, orange, purple)
- Clear section labels and bullet-point content
- Professional grid layout
- Hover effects with expanded details
- Flow diagrams with connecting arrows

```typescript
interface BusinessCanvasProps {
  sections: Array<{
    title: string;
    content: string[];
    color: string;
    position: {x: number, y: number, width: number, height: number};
  }>;
}
```

### 4. Chart Components

#### A. Bar Chart (Page 40 Style)
**Visual Requirements:**
- Blue gradient bars with company comparisons
- Clean axis labels and data points
- Toggle buttons for different views (market cap vs revenue)
- Explanatory text boxes below charts
- Responsive design for mobile

```typescript
interface BarChartProps {
  data: Array<{company: string, value: number}>;
  color: string;
  showToggle?: boolean;
  annotations?: string[];
}
```

#### B. Line Chart (Page 45 Style)
**Visual Requirements:**
- Multi-colored trend lines (purple, blue, red)
- Data points with circles at each value
- Legend with company names and colors
- Warning/risk callout boxes with yellow background
- Dual-axis support for different metrics

```typescript
interface LineChartProps {
  data: Array<{year: number, companies: {[key: string]: number}}>;
  colors: {[company: string]: string};
  showRiskWarning?: boolean;
  annotations?: Array<{text: string, type: 'warning' | 'info'}>;
}
```

#### C. Pie Chart (Page 50 Style)
**Visual Requirements:**
- Colorful pie charts with percentage labels
- Company tabs for switching between different analyses
- Horizontal bar charts for detailed breakdowns
- Professional color scheme matching brand colors
- Interactive hover effects

```typescript
interface PieChartProps {
  data: Array<{label: string, value: number, color: string}>;
  showPercentages: boolean;
  centerLabel?: string;
  interactive?: boolean;
}
```

#### D. Combined Chart (Page 60 Style)
**Visual Requirements:**
- Bar + Line combination charts
- Dual Y-axis for different metrics (bars vs line)
- Color-coded data series
- Professional annotations and labels
- Responsive scaling

```typescript
interface CombinedChartProps {
  barData: number[];
  lineData: number[];
  labels: string[];
  dualAxis: boolean;
  colors: {bars: string, line: string};
}
```

## Layout Specifications

### Report Viewer Layout
```css
.report-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  background: white;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

.report-section {
  margin-bottom: 40px;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  background: white;
}

.chart-container {
  background: var(--light-gray);
  padding: 20px;
  border-radius: 8px;
  margin: 20px 0;
  min-height: 400px;
}

.section-divider {
  height: 1px;
  background: var(--medium-gray);
  margin: 30px 0;
  opacity: 0.3;
}
```

### Mobile Responsive Design
```css
@media (max-width: 768px) {
  .report-container { 
    padding: 10px; 
    max-width: 100%;
  }
  
  .chart-container { 
    overflow-x: auto;
    min-width: 300px;
    padding: 15px;
  }
  
  .timeline-event { 
    width: 100%;
    margin-bottom: 20px;
  }
  
  .data-table {
    font-size: 12px;
    overflow-x: auto;
  }
  
  .business-canvas {
    flex-direction: column;
    gap: 15px;
  }
}
```

## Interactive Features

### Chart Interactions
- **Hover tooltips** with detailed data and formatting
- **Click to drill down** into specific metrics or time periods
- **Toggle between different views** (market cap vs revenue, growth vs margins)
- **Zoom and pan** for detailed analysis of time series
- **Export individual charts** as PNG or SVG

### Report Navigation
- **Sticky table of contents** on the left sidebar
- **Progress indicator** showing reading progress through report
- **Quick jump to sections** with smooth scrolling
- **Search within report** with highlighting
- **Bookmark specific sections** for later reference

### Export Features
- **PDF export** with preserved formatting and charts
- **Print-friendly** layouts with proper page breaks
- **Share specific sections** via URL or social media
- **Save to dashboard** for comparison with other reports
- **Email report** with customizable summary

## Animation Guidelines

### Micro-interactions
```css
/* Smooth transitions for all interactive elements */
.interactive-element {
  transition: all 0.2s ease-in-out;
}

/* Chart animations */
.chart-enter {
  animation: slideInUp 0.6s ease-out;
}

/* Loading states */
.loading-skeleton {
  animation: pulse 1.5s ease-in-out infinite;
}

/* Hover effects */
.hover-lift:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}
```

### Performance Considerations
- **Lazy loading** for charts and heavy content
- **Virtual scrolling** for long reports
- **Progressive image loading** for chart exports
- **Debounced search** to avoid excessive API calls
- **Cached chart configurations** for faster rendering

*Last Updated: 2026-01-21*
