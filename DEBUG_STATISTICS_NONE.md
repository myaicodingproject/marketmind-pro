# Debug: Statistics Showing as None

## Problem
API returns `None` for statistics, quality_score, and generated_at even though the demo file has correct values.

## Investigation
1. ✅ Demo file (`data/demo_report_avgo.json`) has correct data
2. ✅ Backend logic preserves statistics correctly
3. ❌ API returns None for these fields

## Added Debug Logging
Added logging to:
1. `load_demo_data()` - Log what's loaded from file
2. `handle_demo_mode()` - Log before/after modifications
3. `get_report()` - Log what's being returned

## Next Steps
1. **Restart backend** with new debug logging
2. **Generate DEMO report**
3. **Check console output** for debug logs showing:
   - What was loaded from file
   - What's being stored
   - What's being returned by API

## Expected Debug Output
```
🎭 DEMO: Loaded demo data with keys: ['report_id', 'ticker', ...]
🎭 DEMO: statistics = {'total_sections': 9, 'total_words': 8268}
🎭 DEMO: quality_score = 94
🎭 DEMO: generated_at = 2026-01-28T11:06:51.563374
...
🎭 DEMO: Storing report with:
   statistics: {'total_sections': 9, 'total_words': 8268}
   quality_score: 94
...
📤 GET /api/v1/reports/prod_report_DEMO_xxx
   statistics: {'total_sections': 9, 'total_words': 8268}
   quality_score: 94
```

If any of these show `None`, we'll know exactly where the data is being lost.
