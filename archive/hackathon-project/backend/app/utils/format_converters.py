import json
from typing import Dict, Any, List
from ..utils.kiro_validator import KiroOutputValidator

def convert_to_chart_js_format(chart_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert standardized chart data to Chart.js format"""
    return {
        "type": chart_data["type"],
        "data": {
            "labels": chart_data["labels"],
            "datasets": [{
                "label": chart_data["title"],
                "data": list(chart_data["data"].values()) if isinstance(chart_data["data"], dict) else chart_data["data"]
            }]
        },
        "options": {
            "responsive": True,
            "plugins": {
                "title": {
                    "display": True,
                    "text": chart_data["title"]
                }
            }
        }
    }

def export_to_pdf_format(report: Dict[str, Any]) -> Dict[str, Any]:
    """Convert report to PDF-friendly format"""
    return {
        "title": f"Stock Analysis Report - {report.get('ticker', 'N/A')}",
        "sections": [
            {
                "title": "Executive Summary",
                "content": report["analysis"][:500] + "..." if len(report["analysis"]) > 500 else report["analysis"]
            },
            {
                "title": "Key Insights",
                "content": "\n".join([f"• {insight}" for insight in report["key_insights"]])
            },
            {
                "title": "Financial Metrics",
                "content": format_metrics_table(report["metrics"])
            }
        ],
        "charts": [convert_to_chart_js_format(chart) for chart in report["charts"]],
        "recommendations": format_recommendations(report["recommendations"])
    }

def format_metrics_table(metrics: List[Dict[str, Any]]) -> str:
    """Format metrics as a table string"""
    if not metrics:
        return "No metrics available"
    
    table = "| Metric | Value | Unit |\n|--------|-------|------|\n"
    for metric in metrics:
        unit = metric.get("unit", "")
        table += f"| {metric['name']} | {metric['value']} | {unit} |\n"
    return table

def format_recommendations(recommendations: List[Dict[str, Any]]) -> str:
    """Format recommendations as readable text"""
    if not recommendations:
        return "No recommendations available"
    
    formatted = []
    for rec in recommendations:
        text = f"**{rec['type']}** (Confidence: {rec['confidence']:.0%})\n{rec['reasoning']}"
        if rec.get("price_target"):
            text += f"\nPrice Target: ${rec['price_target']:.2f}"
        formatted.append(text)
    
    return "\n\n".join(formatted)

# Test utilities
def create_sample_output() -> Dict[str, Any]:
    """Create sample output for testing"""
    return {
        "analysis": "Apple Inc. demonstrates strong financial performance with consistent revenue growth.",
        "key_insights": [
            "iPhone revenue increased 15% YoY",
            "Services segment showing strong growth",
            "Strong balance sheet with $165B cash"
        ],
        "metrics": [
            {"name": "P/E Ratio", "value": 28.5, "unit": "x"},
            {"name": "Revenue Growth", "value": 8.2, "unit": "%"},
            {"name": "Market Cap", "value": 2800, "unit": "B"}
        ],
        "charts": [
            {
                "type": "line",
                "title": "Revenue Trend",
                "data": {"2021": 365, "2022": 394, "2023": 383},
                "labels": ["2021", "2022", "2023"]
            }
        ],
        "tables": [
            {
                "title": "Key Financials",
                "headers": ["Year", "Revenue", "Net Income"],
                "rows": [["2023", "383B", "97B"], ["2022", "394B", "100B"]]
            }
        ],
        "recommendations": [
            {
                "type": "BUY",
                "confidence": 0.85,
                "reasoning": "Strong fundamentals and growth prospects",
                "price_target": 200.0
            }
        ]
    }