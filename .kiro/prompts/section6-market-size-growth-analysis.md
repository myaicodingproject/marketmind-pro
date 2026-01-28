# Section 6: Market Size & Growth Potential Analysis

## Objective
Generate a comprehensive 4-page market analysis covering Total Addressable Market (TAM), Serviceable Addressable Market (SAM), market forecasts, and growth drivers for the target company.

## Context Variables
- **ticker**: Stock ticker symbol
- **company_name**: Full company name
- **sector**: Primary business sector
- **industry**: Specific industry classification
- **market_cap**: Current market capitalization
- **revenue**: Latest annual revenue
- **geographic_presence**: Key markets/regions

## Analysis Framework

### 1. Market Size Analysis (1 page)
**Total Addressable Market (TAM)**
- Define the total market opportunity globally
- Include market size in USD billions
- Identify key market segments
- Historical market size trends (5-year)

**Serviceable Addressable Market (SAM)**
- Addressable market given company's business model
- Geographic and product constraints
- Competitive positioning within SAM
- Market share analysis

### 2. Growth Forecasts & Trends (1 page)
**Market Growth Projections**
- 5-year CAGR forecasts by segment
- Key growth drivers and catalysts
- Seasonal and cyclical patterns
- Emerging market opportunities

**Industry Trends Analysis**
- Technology disruption impact
- Regulatory changes affecting growth
- Consumer behavior shifts
- Supply chain evolution

### 3. Competitive Landscape & Opportunity (1 page)
**Market Concentration**
- Top 5-10 players and market shares
- Competitive intensity analysis
- Barriers to entry assessment
- White space opportunities

**Strategic Positioning**
- Company's competitive advantages
- Market expansion potential
- Adjacent market opportunities
- Partnership and M&A potential

### 4. Strategic Roadmap & Expansion (1 page)
**Growth Strategy Assessment**
- Current expansion initiatives
- Geographic expansion potential
- Product/service diversification
- Digital transformation impact

**Investment Requirements**
- Capital allocation for growth
- R&D investment priorities
- Infrastructure scaling needs
- Timeline for market expansion

## Research Sources
Use these data sources for market research:
- Industry research reports (IBISWorld, Frost & Sullivan)
- Government economic data
- Trade association publications
- Company investor presentations
- Competitor annual reports
- Market research firms (Gartner, IDC, etc.)

## Chart Requirements
Generate data for these visualizations:

### Market Size Chart
```json
{
  "chart_type": "stacked_bar",
  "title": "Market Size Evolution (TAM vs SAM)",
  "data": {
    "years": ["2019", "2020", "2021", "2022", "2023"],
    "tam": [100, 110, 125, 140, 155],
    "sam": [25, 28, 32, 38, 42]
  }
}
```

### Growth Projection Graph
```json
{
  "chart_type": "line_chart",
  "title": "5-Year Market Growth Forecast",
  "data": {
    "years": ["2024", "2025", "2026", "2027", "2028"],
    "market_size": [165, 185, 210, 240, 275],
    "company_opportunity": [45, 52, 62, 75, 90]
  }
}
```

### Opportunity Matrix
```json
{
  "chart_type": "bubble_chart",
  "title": "Market Opportunity Matrix",
  "data": {
    "segments": [
      {"name": "Core Market", "size": 50, "growth": 8, "competition": 85},
      {"name": "Adjacent Market", "size": 30, "growth": 15, "competition": 60},
      {"name": "Emerging Market", "size": 15, "growth": 25, "competition": 30}
    ]
  }
}
```

## Output Format
Provide analysis in this structure:

```json
{
  "section_6_market_analysis": {
    "tam_analysis": {
      "total_market_size_usd_billions": 0,
      "historical_growth_cagr": 0,
      "key_segments": [],
      "geographic_breakdown": {}
    },
    "sam_analysis": {
      "serviceable_market_size": 0,
      "company_market_share": 0,
      "addressable_segments": [],
      "competitive_position": ""
    },
    "growth_forecasts": {
      "five_year_cagr": 0,
      "growth_drivers": [],
      "market_catalysts": [],
      "risk_factors": []
    },
    "competitive_landscape": {
      "market_concentration": "",
      "top_competitors": [],
      "barriers_to_entry": [],
      "white_space_opportunities": []
    },
    "strategic_roadmap": {
      "expansion_priorities": [],
      "investment_requirements": {},
      "timeline_milestones": [],
      "success_metrics": []
    },
    "charts": []
  }
}
```

## Quality Standards
- Use recent data (within 12 months)
- Cite specific sources and methodologies
- Provide conservative, base, and optimistic scenarios
- Include quantitative metrics with confidence intervals
- Address both organic and inorganic growth opportunities
- Consider macroeconomic factors and industry cycles