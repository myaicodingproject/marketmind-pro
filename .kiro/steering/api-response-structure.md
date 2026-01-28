# API Response Structure Standards

## CRITICAL: Frontend Data Contract

### Problem That Was Fixed
The frontend expects report data at the **TOP LEVEL** of the response, but the backend was only putting it in the `metadata` object. This caused statistics, quality score, and dates to show as 0/null.

### Required Response Structure

**ALL report endpoints MUST return data at BOTH locations:**

```json
{
  "report_id": "...",
  "ticker": "AVGO",
  "title": "...",
  "sections": {...},
  "chart_data": {...},
  
  // ✅ REQUIRED: Top-level fields for frontend
  "statistics": {
    "total_sections": 9,
    "total_words": 8268
  },
  "quality_score": 94,
  "generated_at": "2026-01-28T11:06:51.563374",
  
  // ✅ ALSO in metadata for backwards compatibility
  "metadata": {
    "quality_score": 94,
    "total_sections": 9,
    "generated_at": "2026-01-28T11:06:51.563374",
    "is_demo": true
  }
}
```

### Frontend Dependencies

The React frontend (`ReportViewerPage.jsx`) expects:

```javascript
// These MUST exist at top level:
report.statistics.total_sections  // Used in sidebar stats
report.statistics.total_words     // Used in sidebar stats
report.quality_score              // Used in sidebar stats
report.generated_at               // Used in header date display
```

### Backend Implementation Rules

#### Rule 1: Demo Mode Data Loading
When loading demo data in `handle_demo_mode()`:

```python
# ✅ CORRECT: Preserve top-level fields
demo_data = load_demo_data()  # Already has statistics, quality_score, generated_at
demo_data['report_id'] = report_id
demo_data['generated_at'] = datetime.now().isoformat()

# DON'T overwrite existing statistics/quality_score unless missing
if 'statistics' not in demo_data:
    demo_data['statistics'] = {...}
```

#### Rule 2: API Response Formatting
In `get_report_data()` endpoint:

```python
# ✅ CORRECT: Return fields at BOTH top level AND metadata
return {
    'report_id': report_id,
    'ticker': legacy_report.get('ticker'),
    'sections': sections,
    'chart_data': legacy_report.get('chart_data', {}),
    
    # TOP LEVEL (required by frontend)
    'statistics': legacy_report.get('statistics', {...}),
    'quality_score': legacy_report.get('quality_score', 0),
    'generated_at': legacy_report.get('generated_at'),
    
    # METADATA (backwards compatibility)
    'metadata': {
        'quality_score': legacy_report.get('quality_score', 0),
        'total_sections': len(sections),
        'generated_at': legacy_report.get('generated_at'),
        'is_demo': legacy_report.get('metadata', {}).get('is_demo', False)
    }
}
```

#### Rule 3: Demo Data File Structure
`data/demo_report_avgo.json` MUST have:

```json
{
  "report_id": "...",
  "ticker": "AVGO",
  "company_name": "Broadcom Inc.",
  "generated_at": "2026-01-28T11:06:51.563374",
  "status": "completed",
  
  "statistics": {
    "total_sections": 9,
    "total_words": 8268
  },
  
  "quality_score": 94,
  
  "sections": {...},
  "chart_data": {...},
  
  "metadata": {
    "is_demo": true,
    "processing_time": 10
  }
}
```

### Common Mistakes to Avoid

❌ **WRONG**: Only putting data in metadata
```python
return {
    'metadata': {
        'quality_score': 94,  # Frontend can't find this!
        'total_sections': 9
    }
}
```

❌ **WRONG**: Overwriting demo file statistics
```python
# This destroys the correct data from demo file
demo_data['statistics'] = {
    'total_sections': 8,  # Wrong! Demo has 9
    'total_words': 2500   # Wrong! Demo has 8268
}
```

❌ **WRONG**: Using different field names
```python
return {
    'stats': {...},        # Frontend expects 'statistics'
    'score': 94,          # Frontend expects 'quality_score'
    'created_at': '...'   # Frontend expects 'generated_at'
}
```

### Testing Checklist

When modifying report endpoints, verify:

- [ ] `curl http://localhost:8000/api/v1/reports/{id}` returns `statistics` at top level
- [ ] `curl http://localhost:8000/api/v1/reports/{id}` returns `quality_score` at top level
- [ ] `curl http://localhost:8000/api/v1/reports/{id}` returns `generated_at` at top level
- [ ] Frontend sidebar shows "Sections: 9" (not 0)
- [ ] Frontend sidebar shows "Words: 8,268" (not 0)
- [ ] Frontend sidebar shows "Quality: 94%" (not 0%)
- [ ] Frontend header shows valid date (not "Invalid Date")

### Debug Commands

```bash
# Check demo file structure
python3 -c "import json; print(json.load(open('data/demo_report_avgo.json'))['statistics'])"

# Check API response structure
curl -s http://localhost:8000/api/v1/reports/{id} | python3 -m json.tool | grep -A5 "statistics\|quality_score"

# Test frontend display
# Generate DEMO report and check sidebar stats
```

### Related Files

- **Backend**: `/mnt/c/kiro/complete_production_system.py`
  - `handle_demo_mode()` - Line ~140
  - `get_report_data()` - Line ~432
  
- **Frontend**: `/mnt/c/kiro/frontend/react-app/src/components/ReportViewerPage.jsx`
  - Sidebar stats display - Line ~297-300
  
- **Demo Data**: `/mnt/c/kiro/data/demo_report_avgo.json`

### Version History

- **2026-01-28**: Fixed statistics showing as 0 by ensuring top-level fields in API response
- **Issue**: Frontend expected `report.statistics` but backend only returned `report.metadata.quality_score`
- **Solution**: Return data at BOTH top level AND metadata for compatibility
