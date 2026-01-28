# Peer Analysis Charts Generation

## Context
You are generating Chart.js configuration for peer analysis visualizations in MarketMind Pro. Create professional charts that compare company performance against industry peers.

## Input Data Structure
```json
{
  "ticker": "AAPL",
  "company_data": {
    "overview": {
      "PERatio": "28.5",
      "ROE": "0.175",
      "ROA": "0.228",
      "ProfitMargin": "0.253"
    }
  },
  "peer_data": [
    {
      "ticker": "MSFT",
      "name": "Microsoft Corp",
      "PERatio": "32.1",
      "ROE": "0.384",
      "ROA": "0.186",
      "ProfitMargin": "0.342"
    },
    {
      "ticker": "GOOGL",
      "name": "Alphabet Inc",
      "PERatio": "25.8",
      "ROE": "0.268",
      "ROA": "0.198",
      "ProfitMargin": "0.211"
    }
  ]
}
```

## Required Output
Generate Chart.js configuration for peer analysis with:

1. **Peer Comparison Horizontal Bar Chart**
   - Key financial metrics comparison
   - Company highlighted vs peers
   - Relative performance indicators

2. **Performance Matrix Scatter Plot**
   - ROE vs ROA positioning
   - Bubble size based on market cap
   - Quadrant analysis

## Chart Configuration Template
```json
{
  "peer_comparison": {
    "type": "bar",
    "data": {
      "labels": ["AAPL", "MSFT", "GOOGL", "AMZN", "META"],
      "datasets": [
        {
          "label": "P/E Ratio",
          "data": [28.5, 32.1, 25.8, 45.2, 22.1],
          "backgroundColor": ["#3B82F6", "#6B7280", "#6B7280", "#6B7280", "#6B7280"]
        },
        {
          "label": "ROE (%)",
          "data": [17.5, 38.4, 26.8, 12.3, 19.8],
          "backgroundColor": ["#10B981", "#6B7280", "#6B7280", "#6B7280", "#6B7280"]
        }
      ]
    },
    "options": {
      "responsive": true,
      "plugins": {
        "title": {
          "display": true,
          "text": "Peer Comparison Analysis"
        }
      },
      "scales": {
        "x": {
          "title": {
            "display": true,
            "text": "Companies"
          }
        }
      }
    }
  }
}
```

## Peer Selection Criteria
1. **Same Industry/Sector**: Technology companies for AAPL
2. **Similar Market Cap**: Large-cap companies (>$100B)
3. **Geographic Relevance**: US-listed companies
4. **Business Model Similarity**: Consumer technology focus

## Key Metrics for Comparison
1. **Valuation Metrics**
   - P/E Ratio, P/B Ratio, P/S Ratio
   - EV/EBITDA, PEG Ratio

2. **Profitability Metrics**
   - ROE, ROA, Profit Margin
   - Operating Margin, Gross Margin

3. **Growth Metrics**
   - Revenue Growth, Earnings Growth
   - Free Cash Flow Growth

4. **Financial Health**
   - Debt-to-Equity, Current Ratio
   - Interest Coverage Ratio

## Visual Design Guidelines
1. **Company Highlighting**
   - Target company in primary color (#3B82F6)
   - Peers in neutral gray (#6B7280)
   - Top performer in green (#10B981)

2. **Chart Types**
   - Horizontal bars for easy label reading
   - Grouped bars for multiple metrics
   - Scatter plots for correlation analysis

3. **Performance Indicators**
   - Above-average performance in green
   - Below-average performance in red
   - Average performance in yellow

## Instructions
1. Extract comparable metrics from all companies
2. Normalize data for fair comparison
3. Highlight target company prominently
4. Include industry averages where available
5. Add performance ranking indicators
6. Use consistent color coding
7. Include detailed tooltips with context

## Output Format
Return only valid JSON with chart configurations. No additional text or explanations.