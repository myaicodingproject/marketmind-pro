# Institutional Report Styling Guide

## Overview
Professional styling system based on Goldman Sachs, Morgan Stanley, and JP Morgan equity research report standards.

## Design Principles

### 1. Typography
**Based on research**: Professional financial reports use clean, readable sans-serif fonts with optimal spacing for long-form reading.

- **Primary Font**: Inter (fallback to system fonts)
- **Body Text**: 16px with 1.75 line-height for readability
- **Headings**: Progressive scale (20px → 24px → 30px)
- **Tables**: 14px for data density

### 2. Spacing System
**4px increment scale** for consistent rhythm:
- 4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px
- Based on best practices from modern design systems

### 3. Color Palette
**Professional & Accessible**:
- Primary Text: `#1a1a1a` (near-black for readability)
- Secondary Text: `#4a4a4a` (for supporting content)
- Accent: `#0066cc` (professional blue)
- Borders: `#e5e7eb` (subtle separation)

## Key Features

### Section Structure
```css
.report-section {
  max-width: 850px;        /* Optimal line length: 60-75 characters */
  padding: 2rem;           /* Generous whitespace */
  background: white;
  border: 1px solid #e5e7eb;
  box-shadow: subtle;
}
```

### Section Headers
```css
.section-header {
  border-bottom: 2px solid accent;  /* Clear visual separation */
  margin-bottom: 2rem;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.02em;  /* Tighter for large text */
}

.section-subtitle {
  font-size: 18px;
  font-weight: 500;
  color: secondary;
}
```

### Body Content
```css
.markdown-content p {
  line-height: 1.75;       /* Optimal for reading */
  text-align: justify;     /* Professional appearance */
  hyphens: auto;           /* Better text flow */
  margin-bottom: 1rem;
}

.markdown-content h3 {
  font-size: 20px;
  font-weight: 600;
  margin: 2rem 0 1rem;     /* Clear section breaks */
  letter-spacing: -0.01em;
}
```

### Tables
```css
.data-table {
  font-size: 14px;         /* Smaller for data density */
  border-collapse: collapse;
  margin: 1.5rem 0;
}

.data-table td {
  padding: 0.75rem 1rem;
  border: 1px solid #e5e7eb;
}

.data-table td:first-child {
  font-weight: 600;
  background: #f9fafb;     /* Subtle header column */
  width: 40%;
}
```

## Responsive Design

### Mobile Adjustments
```css
@media (max-width: 768px) {
  .report-section {
    padding: 1rem;
  }
  
  .section-title {
    font-size: 20px;       /* Smaller on mobile */
  }
  
  .markdown-content {
    font-size: 15px;       /* Slightly smaller body */
  }
  
  .data-table {
    font-size: 12px;       /* Compact tables */
  }
}
```

## Accessibility Features

### 1. Keyboard Navigation
- Focus states with 2px outline
- Proper tab order

### 2. High Contrast Mode
```css
@media (prefers-contrast: high) {
  --color-text-primary: #000000;
  --color-border: #000000;
}
```

### 3. Reduced Motion
```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

## Print Optimization

```css
@media print {
  .report-section {
    box-shadow: none;
    page-break-inside: avoid;
  }
  
  .section-header {
    page-break-after: avoid;
  }
  
  .data-table {
    page-break-inside: avoid;
  }
}
```

## Comparison: Before vs After

### Before (Basic Styling)
- Generic font sizes
- Inconsistent spacing
- Basic table styling
- No professional polish

### After (Institutional Styling)
- ✅ Professional typography scale
- ✅ Consistent 4px spacing system
- ✅ Institutional-grade tables
- ✅ Optimal readability (1.75 line-height)
- ✅ Professional color palette
- ✅ Responsive design
- ✅ Print-optimized
- ✅ Accessibility compliant

## Research Sources

Content was rephrased for compliance with licensing restrictions.

Based on best practices from:
1. **Typography**: Modern web typography guides emphasizing fluid type scales and optimal line heights (1.3-1.7x font size)
2. **Spacing**: Design system principles using 4px increment scales
3. **Financial Reports**: Equity research report templates and formatting standards
4. **Accessibility**: WCAG guidelines for contrast, focus states, and reduced motion

## Files

- **CSS**: `/mnt/c/kiro/frontend/react-app/src/styles/institutional-report.css`
- **Component**: `/mnt/c/kiro/frontend/react-app/src/components/ReportViewerPage.jsx`

## Testing

1. **Visual Check**: Generate DEMO report and review styling
2. **Responsive**: Test on mobile (< 768px)
3. **Print**: Use browser print preview
4. **Accessibility**: Test keyboard navigation (Tab key)
5. **Contrast**: Enable high contrast mode in OS

## Future Enhancements

- [ ] Add font loading optimization
- [ ] Implement dark mode variant
- [ ] Add more table styles (striped, bordered)
- [ ] Create PDF-specific styling
- [ ] Add animation for section transitions
