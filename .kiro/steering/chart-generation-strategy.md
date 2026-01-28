# Chart Generation Strategy

## Overview
Charts should be dynamically selected based on company characteristics and data availability, not shown blindly for all companies.

## Current State

### Demo Mode
- **Static charts** in `data/demo_report_avgo.json`
- Shows all chart types to demonstrate capabilities
- Appropriate for AVGO (growth tech company with stable cash flows)

### Production Mode
- Charts generated in `generate_chart_data()` function
- Currently shows all chart types regardless of company
- Based on section content but not context-aware

## Smart Chart Generation System

### 1. Company Type Detection

Automatically classify companies into types:

```python
CompanyType:
- GROWTH_TECH: High growth (>20%), high P/E (>30)
- VALUE: Low P/E (<15), stable business
- DIVIDEND: High yield (>3%), mature company
- CYCLICAL: High volatility (beta >1.5)
- TURNAROUND: Negative growth, restructuring
```

### 2. Chart Relevance Scoring

Each chart has a relevance score per company type:

- **ESSENTIAL (3)**: Must show, core to understanding
- **RECOMMENDED (2)**: Show if data quality is good
- **OPTIONAL (1)**: Show only if user requests

### 3. Chart Relevance by Company Type

#### Growth Tech (e.g., AVGO, NVDA)
**Essential:**
- Revenue trend
- TAM/SAM/SOM
- Peer comparison
- Key metrics

**Recommended:**
- DCF sensitivity
- Market share
- Segment breakdown

**Optional:**
- Dividend history
- Cash flow waterfall

#### Value Companies
**Essential:**
- Margins
- Cash flow waterfall
- DCF sensitivity
- Peer comparison

**Recommended:**
- Dividend history

**Optional:**
- TAM/SAM/SOM

#### Dividend Companies
**Essential:**
- Dividend history
- Cash flow waterfall

**Recommended:**
- Margins
- Peer comparison

**Optional:**
- DCF sensitivity

### 4. Data Quality Checks

Only show charts if we have sufficient data:

```python
DCF Sensitivity requires:
- Cash flow projections (3+ years)
- WACC calculation
- Growth rate estimates

Peer Comparison requires:
- 3+ comparable companies
- Valuation multiples available

Segment Breakdown requires:
- Revenue by segment
- At least 2 segments
```

## Implementation

### For Demo Mode (Current)
```python
# Keep comprehensive charts
# Shows all capabilities
# Use realistic AVGO-specific data
chart_data = {
    "executive_summary": {...},
    "financial_analysis": {...},
    "valuation_analysis": {...},  # DCF appropriate for AVGO
    "risk_assessment": {...},
    "market_analysis": {...}
}
```

### For Production (Recommended)
```python
from services.smart_chart_generator import generate_smart_chart_data

# Detect company type and generate relevant charts
chart_data = generate_smart_chart_data(
    ticker=ticker,
    sections=sections,
    financial_data=financial_data
)

# Result: Only relevant, high-quality charts
```

## Chart Types and When to Use

### Always Show
1. **Revenue Trend** - Universal metric
2. **Key Metrics** - Company-specific KPIs
3. **Recommendation** - Investment thesis

### Conditional Charts

#### DCF Sensitivity
- ✅ Show for: Mature companies with predictable cash flows
- ❌ Skip for: Early-stage, unprofitable, highly cyclical
- **AVGO**: ✅ Appropriate (stable, profitable, predictable)

#### TAM/SAM/SOM
- ✅ Show for: Growth companies, new markets
- ❌ Skip for: Mature, saturated markets
- **AVGO**: ✅ Appropriate (AI market expanding rapidly)

#### Dividend History
- ✅ Show for: Dividend-paying companies
- ❌ Skip for: Growth companies reinvesting all cash
- **AVGO**: ⚠️ Optional (pays dividends but not primary focus)

#### Peer Comparison
- ✅ Show for: Companies with clear peers
- ❌ Skip for: Unique business models
- **AVGO**: ✅ Appropriate (NVDA, AMD, QCOM comparable)

#### Risk Matrix
- ✅ Show for: All companies
- Focus areas vary by type

#### Scenario Analysis
- ✅ Show for: Cyclical, high-uncertainty companies
- ❌ Skip for: Stable, predictable businesses
- **AVGO**: ✅ Appropriate (AI market uncertainty)

## Best Practices

### 1. Chart Selection
- Start with company type detection
- Check data availability
- Apply relevance scoring
- Generate only high-confidence charts

### 2. Chart Quality
- Ensure data is recent (<90 days)
- Verify calculations are correct
- Include data sources
- Add explanatory notes

### 3. User Experience
- Show most important charts first
- Allow users to request additional charts
- Explain why certain charts are shown/hidden
- Provide chart metadata

### 4. Demo vs Production
- **Demo**: Show comprehensive charts (demonstrates capabilities)
- **Production**: Show relevant charts (better user experience)

## Future Enhancements

### Phase 1: Smart Selection (Recommended)
- Implement company type detection
- Add data quality checks
- Apply relevance scoring

### Phase 2: User Preferences
- Allow users to request specific charts
- Save chart preferences per user
- Custom chart configurations

### Phase 3: AI-Powered Selection
- Use LLM to analyze company and suggest charts
- Generate custom charts based on unique characteristics
- Explain chart selection reasoning

## Testing

### Verify Chart Appropriateness
```bash
# Test company type detection
python3 services/smart_chart_generator.py

# Check chart relevance for AVGO
# Expected: Growth Tech → DCF, TAM/SAM, Peer Comparison

# Check chart relevance for dividend stock (e.g., T)
# Expected: Dividend History, Cash Flow, Margins
```

### Quality Checklist
- [ ] Charts match company type
- [ ] Data quality is sufficient
- [ ] Calculations are accurate
- [ ] Charts are readable
- [ ] Explanations are clear

## Related Files
- `/mnt/c/kiro/services/smart_chart_generator.py` - Smart selection logic
- `/mnt/c/kiro/complete_production_system.py` - Current chart generation
- `/mnt/c/kiro/data/demo_report_avgo.json` - Demo chart data
- `/mnt/c/kiro/frontend/react-app/src/components/ReportCharts.jsx` - Chart display
- `/mnt/c/kiro/frontend/react-app/src/components/charts/AdvancedCharts.jsx` - Chart components

## Common Chart Issues & Fixes

### Issue 1: DCF Sensitivity showing "undefined%"
**Problem**: Chart's `tickFormatter` was accessing array indices with decimal values (e.g., `data.growth[0.5]` returns `undefined`)

**Solution**: 
```javascript
// ❌ WRONG
tickFormatter={(value) => `${data.growth[value]}%`}

// ✅ CORRECT
tickFormatter={(value) => `${data.growth[Math.round(value)]}%`}
ticks={[0, 1, 2]}  // Explicit tick positions
```

**Files Modified**: `/mnt/c/kiro/frontend/react-app/src/components/charts/AdvancedCharts.jsx`

### Issue 2: Market Share Chart showing "No Data"
**Problem**: Chart component expected different field names than what data provided

**Expected by Chart**:
```javascript
{
  region: "AI Custom ASICs",
  share: 75,
  growth: 220
}
```

**What We Had**:
```javascript
{
  segment: "AI Custom ASICs",
  broadcom: 75,
  competitors: 25
}
```

**Solution**: Match data structure to chart expectations
```python
# In demo_report_avgo.json
"market_share": [
    {"region": "AI Custom ASICs", "share": 75, "growth": 220},
    {"region": "Data Center Networking", "share": 45, "growth": 35}
]
```

### Issue 3: Double Percentage Signs (10.0%%)
**Problem**: Data included "%" but chart component also adds "%"

**Solution**: Provide numeric data, let chart format it
```python
# ✅ CORRECT - Numbers only
"wacc": [8.0, 8.5, 9.0, 9.5, 10.0]
"growth": [10.0, 12.0, 15.0]

# ❌ WRONG - Don't include % in data
"wacc": ["8.0%", "8.5%", "9.0%"]
```

## Chart Data Structure Best Practices

### 1. Always Match Component Expectations
Before creating chart data, check what the chart component expects:
```javascript
// Check the component's dataKey props
<XAxis dataKey="region" />  // Expects "region" field
<Bar dataKey="share" />     // Expects "share" field
```

### 2. Use Numeric Values for Formatting
Let chart components handle formatting:
```python
# ✅ GOOD
{"value": 75, "label": "Market Share"}

# ❌ BAD
{"value": "75%", "label": "Market Share"}
```

### 3. Provide Complete Data
Ensure all required fields are present:
```python
# ✅ COMPLETE
{"region": "North America", "share": 55, "growth": 12}

# ❌ INCOMPLETE (missing growth)
{"region": "North America", "share": 55}
```

### 4. Test with Console Logs
When charts don't display, check browser console:
```javascript
console.log('Chart data:', chartData);
console.log('Expected fields:', Object.keys(chartData[0]));
```

### 5. Handle Array Index Access Safely
When using array indices in formatters:
```javascript
// ✅ SAFE
tickFormatter={(value) => `${data[Math.round(value)]}`}

// ❌ UNSAFE (can get undefined)
tickFormatter={(value) => `${data[value]}`}
```

## Testing Checklist for New Charts

- [ ] Data structure matches component's dataKey props
- [ ] All required fields are present
- [ ] Numeric values are numbers, not strings
- [ ] No duplicate formatting (e.g., adding % when chart adds it)
- [ ] Array access uses Math.round() for safety
- [ ] Test in browser console for errors
- [ ] Hard refresh browser after frontend rebuild

## Debugging Chart Issues

1. **Check API Response**:
```bash
curl -s http://localhost:8000/api/v1/reports/{id} | python3 -m json.tool | grep -A20 "chart_data"
```

2. **Check Browser Console** (F12 → Console):
   - Look for "undefined" errors
   - Check what data the chart received

3. **Verify Data Structure**:
```python
# In Python
import json
with open('data/demo_report_avgo.json') as f:
    data = json.load(f)
print(json.dumps(data['chart_data']['section_name'], indent=2))
```

4. **Check Component Props**:
   - Open chart component file
   - Find all `dataKey` props
   - Ensure data has those exact field names

## Related Files
- `/mnt/c/kiro/services/smart_chart_generator.py` - Smart selection logic
- `/mnt/c/kiro/complete_production_system.py` - Current chart generation
- `/mnt/c/kiro/data/demo_report_avgo.json` - Demo chart data
- `/mnt/c/kiro/frontend/react-app/src/components/ReportCharts.jsx` - Chart display

## Summary

**Current Approach**: Show all charts
**Recommended Approach**: Smart selection based on company type and data quality
**For AVGO Demo**: Current comprehensive charts are appropriate
**For Production**: Implement smart selection for better UX
