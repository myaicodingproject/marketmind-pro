# Risk Assessment Charts Generation

## Context
You are generating Chart.js configuration for risk assessment visualizations in MarketMind Pro. Create professional radar and gauge charts that show comprehensive risk profiles.

## Input Data Structure
```json
{
  "ticker": "AAPL",
  "risk_data": {
    "balance_sheet": {
      "totalDebt": "123000000000",
      "totalAssets": "352755000000",
      "currentAssets": "143566000000",
      "currentLiabilities": "145308000000"
    },
    "income_statement": {
      "interestExpense": "3933000000",
      "ebitda": "123136000000"
    },
    "overview": {
      "Beta": "1.29",
      "DividendYield": "0.0043"
    }
  }
}
```

## Required Output
Generate Chart.js configuration for risk assessment with:

1. **Risk Profile Radar Chart**
   - 6 dimensions: Debt Management, Liquidity, Profitability, Volatility, Interest Coverage, Dividend Stability
   - Normalized 0-100 scoring
   - Color-coded risk levels

2. **Risk Metrics Gauge Charts**
   - Individual risk indicators
   - Traffic light color system
   - Clear risk level indicators

## Chart Configuration Template
```json
{
  "risk_profile": {
    "type": "radar",
    "data": {
      "labels": ["Debt Management", "Liquidity", "Profitability", "Volatility", "Interest Coverage", "Dividend Stability"],
      "datasets": [{
        "label": "Risk Score",
        "data": [75, 85, 90, 60, 95, 80],
        "borderColor": "#3B82F6",
        "backgroundColor": "rgba(59, 130, 246, 0.2)",
        "pointBackgroundColor": "#3B82F6"
      }]
    },
    "options": {
      "responsive": true,
      "plugins": {
        "title": {
          "display": true,
          "text": "Risk Assessment Profile"
        }
      },
      "scales": {
        "r": {
          "beginAtZero": true,
          "max": 100,
          "ticks": {
            "stepSize": 20
          }
        }
      }
    }
  }
}
```

## Risk Scoring Methodology
1. **Debt Management (0-100)**
   - Debt-to-Assets ratio analysis
   - 100 = Low debt, 0 = High debt risk

2. **Liquidity (0-100)**
   - Current ratio and quick ratio
   - 100 = Excellent liquidity, 0 = Poor liquidity

3. **Profitability (0-100)**
   - ROE, ROA, profit margins
   - 100 = High profitability, 0 = Low/negative

4. **Volatility (0-100)**
   - Beta analysis and price volatility
   - 100 = Low volatility, 0 = High volatility

5. **Interest Coverage (0-100)**
   - EBITDA/Interest expense ratio
   - 100 = Strong coverage, 0 = Weak coverage

6. **Dividend Stability (0-100)**
   - Dividend yield and payout consistency
   - 100 = Stable dividends, 0 = Unstable/none

## Color Coding
- **Green (#10B981)**: Low Risk (Score 80-100)
- **Yellow (#F59E0B)**: Medium Risk (Score 50-79)
- **Red (#EF4444)**: High Risk (Score 0-49)

## Instructions
1. Calculate risk scores using financial ratios
2. Normalize all scores to 0-100 scale
3. Apply appropriate color coding
4. Include detailed tooltips explaining each metric
5. Add risk level indicators
6. Ensure radar chart is properly scaled
7. Include summary risk assessment

## Output Format
Return only valid JSON with chart configurations. No additional text or explanations.