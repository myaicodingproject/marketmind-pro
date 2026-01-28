# Financial Trend Charts Generation

## Context
You are generating Chart.js configuration for financial trend visualizations in MarketMind Pro. Create professional, institutional-quality charts that show financial performance over time.

## Input Data Structure
```json
{
  "ticker": "AAPL",
  "financial_data": {
    "income_statement": {
      "annualReports": [
        {
          "fiscalDateEnding": "2023-09-30",
          "totalRevenue": "383285000000",
          "grossProfit": "169148000000",
          "operatingIncome": "114301000000",
          "netIncome": "96995000000"
        }
      ]
    }
  }
}
```

## Required Output
Generate Chart.js configuration for revenue and profit trends with:

1. **Revenue Trends Line Chart**
   - 5-year historical revenue data
   - Smooth line with gradient fill
   - Automatic scaling to billions
   - Professional color scheme

2. **Profit Margins Multi-Line Chart**
   - Gross, Operating, Net margins as percentages
   - Color-coded lines for each margin type
   - Trend analysis indicators

## Chart Configuration Template
```json
{
  "revenue_trends": {
    "type": "line",
    "data": {
      "labels": ["2019", "2020", "2021", "2022", "2023"],
      "datasets": [{
        "label": "Revenue (Billions)",
        "data": [260.2, 274.5, 365.8, 394.3, 383.3],
        "borderColor": "#10B981",
        "backgroundColor": "rgba(16, 185, 129, 0.1)",
        "fill": true,
        "tension": 0.4
      }]
    },
    "options": {
      "responsive": true,
      "plugins": {
        "title": {
          "display": true,
          "text": "Revenue Trends - 5 Year Analysis"
        }
      },
      "scales": {
        "y": {
          "beginAtZero": false,
          "title": {
            "display": true,
            "text": "Revenue (Billions USD)"
          }
        }
      }
    }
  }
}
```

## Instructions
1. Extract financial data from the last 5 years
2. Calculate revenue in billions with 1 decimal precision
3. Calculate margin percentages with 1 decimal precision
4. Use professional color palette: Green (#10B981) for revenue, Blue (#3B82F6) for gross margin, Orange (#F59E0B) for operating margin, Purple (#8B5CF6) for net margin
5. Include proper titles, labels, and formatting
6. Ensure responsive design and accessibility
7. Add trend indicators where appropriate

## Output Format
Return only valid JSON with chart configurations. No additional text or explanations.