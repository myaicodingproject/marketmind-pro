# Valuation Comparison Charts Generation

## Context
You are generating Chart.js configuration for valuation analysis visualizations in MarketMind Pro. Create professional charts that compare valuation metrics and peer analysis.

## Input Data Structure
```json
{
  "ticker": "AAPL",
  "valuation_data": {
    "overview": {
      "PERatio": "28.5",
      "PriceToBookRatio": "45.2",
      "PriceToSalesRatioTTM": "7.8",
      "EVToEBITDA": "22.1",
      "PEGRatio": "2.1"
    }
  },
  "peer_data": [
    {
      "ticker": "MSFT",
      "PERatio": "32.1",
      "PriceToBookRatio": "12.8"
    }
  ]
}
```

## Required Output
Generate Chart.js configuration for valuation analysis with:

1. **Valuation Multiples Bar Chart**
   - P/E, P/B, P/S, EV/EBITDA, PEG ratios
   - Color-coded bars (green=undervalued, yellow=fair, red=overvalued)
   - Industry benchmark lines

2. **Peer Comparison Horizontal Bar Chart**
   - Key metrics vs 3-5 industry peers
   - Relative positioning visualization
   - Standardized scaling

## Chart Configuration Template
```json
{
  "valuation_multiples": {
    "type": "bar",
    "data": {
      "labels": ["P/E Ratio", "P/B Ratio", "P/S Ratio", "EV/EBITDA", "PEG Ratio"],
      "datasets": [{
        "label": "Current Valuation",
        "data": [28.5, 45.2, 7.8, 22.1, 2.1],
        "backgroundColor": ["#F59E0B", "#EF4444", "#10B981", "#EF4444", "#F59E0B"]
      }]
    },
    "options": {
      "responsive": true,
      "plugins": {
        "title": {
          "display": true,
          "text": "Valuation Multiples Analysis"
        }
      }
    }
  }
}
```

## Color Coding Rules
- **Green (#10B981)**: Undervalued (P/E < 20, P/B < 3, P/S < 5)
- **Yellow (#F59E0B)**: Fair Value (P/E 20-30, P/B 3-5, P/S 5-10)
- **Red (#EF4444)**: Overvalued (P/E > 30, P/B > 5, P/S > 10)

## Instructions
1. Extract valuation ratios from financial data
2. Apply color coding based on valuation ranges
3. Include peer comparison data when available
4. Use horizontal bars for peer comparison
5. Add industry benchmark lines where applicable
6. Format numbers with appropriate precision
7. Include tooltips with detailed explanations

## Output Format
Return only valid JSON with chart configurations. No additional text or explanations.