# Leadership Timeline Visualization Prompt

You are creating a timeline visualization showing key leadership changes and strategic milestones over the past 5 years.

## Timeline Elements

### 1. Leadership Changes
- CEO appointments/departures
- C-Suite executive changes
- Board director appointments
- Key management promotions
- Succession events

### 2. Strategic Milestones
- Major strategic initiatives launched
- Significant acquisitions or divestitures
- Organizational restructuring
- Crisis management events
- Performance turning points

### 3. Context Events
- Market conditions during changes
- Company performance correlation
- Stakeholder reactions
- Regulatory or compliance events

## Output Format

Return JSON timeline data:

```json
{
  "timeline_type": "leadership_changes",
  "time_period": "2019-2024",
  "events": [
    {
      "date": "2023-06-15",
      "type": "executive_appointment",
      "title": "New CFO Appointed",
      "description": "Jane Smith appointed as CFO",
      "impact": "Positive",
      "category": "C-Suite",
      "details": "Brought 15 years experience from Fortune 500"
    },
    {
      "date": "2022-03-10",
      "type": "strategic_milestone",
      "title": "Digital Transformation Initiative",
      "description": "Launched $500M digital transformation",
      "impact": "Transformational",
      "category": "Strategy",
      "leader": "CTO Name"
    }
  ],
  "performance_correlation": {
    "stock_performance": "Timeline correlation with stock price",
    "key_metrics": "Revenue, margins, market share changes"
  }
}
```

Include both leadership changes and their strategic impact on company performance.