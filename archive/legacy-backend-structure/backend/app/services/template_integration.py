"""
Template Integration Service for MarketMind Pro
Integrates Handlebars templates with React components and data processing
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from .template_engine import template_engine
from .template_pipeline import data_pipeline

class TemplateIntegrationService:
    """Main service for template rendering and integration"""
    
    def __init__(self):
        self.template_dir = Path("templates/handlebars")
        self.react_template_dir = Path("frontend-react/src/components/templates")
        self.css_dir = Path("static/css")
        
        # Ensure directories exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.react_template_dir.mkdir(parents=True, exist_ok=True)
        self.css_dir.mkdir(parents=True, exist_ok=True)
    
    def render_report(self, ticker: str, raw_data: Dict[str, Any], 
                     template_type: str = "handlebars") -> str:
        """Render complete stock report using specified template system"""
        
        # Process data through pipeline
        processed_data = data_pipeline.process_report_data(ticker, raw_data)
        
        if template_type == "handlebars":
            return self._render_handlebars_report(processed_data)
        elif template_type == "react":
            return self._render_react_report(processed_data)
        else:
            raise ValueError(f"Unsupported template type: {template_type}")
    
    def _render_handlebars_report(self, data: Dict[str, Any]) -> str:
        """Render report using Handlebars template"""
        template_path = self.template_dir / "stock_report.hbs"
        
        if not template_path.exists():
            raise FileNotFoundError(f"Handlebars template not found: {template_path}")
        
        return template_engine.render(str(template_path), data)
    
    def _render_react_report(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for React component rendering"""
        return {
            "component": "ReportTemplate",
            "props": {
                "reportData": data
            },
            "styles": [
                "/static/css/institutional-report.css"
            ]
        }
    
    def render_section(self, section_name: str, section_data: Dict[str, Any],
                      template_type: str = "handlebars") -> str:
        """Render individual report section"""
        
        if template_type == "handlebars":
            template_path = self.template_dir / "sections" / f"{section_name}.hbs"
            return template_engine.render(str(template_path), section_data)
        elif template_type == "react":
            return self._render_react_section(section_name, section_data)
        else:
            raise ValueError(f"Unsupported template type: {template_type}")
    
    def _render_react_section(self, section_name: str, 
                             section_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare section data for React component rendering"""
        
        component_mapping = {
            "executive_summary": "ExecutiveSummary",
            "financial_analysis": "FinancialAnalysis", 
            "company_overview": "CompanyOverview",
            "valuation_analysis": "ValuationAnalysis",
            "risk_assessment": "RiskAssessment"
        }
        
        component_name = component_mapping.get(section_name, "GenericSection")
        
        return {
            "component": component_name,
            "props": {
                "data": section_data
            }
        }
    
    def get_template_data_schema(self, ticker: str) -> Dict[str, Any]:
        """Get the expected data schema for a ticker's template"""
        
        base_schema = {
            "ticker": "string",
            "company_name": "string", 
            "generated_date": "string",
            "title": "string",
            "sections": {
                "executive_summary": {
                    "title": "string",
                    "content": "string",
                    "key_metrics": {
                        "recommendation": "string",
                        "price_target": "string",
                        "current_price": "string",
                        "market_cap": "string",
                        "pe_ratio": "string",
                        "revenue_growth": "string"
                    }
                },
                "financial_analysis": {
                    "title": "string",
                    "content": "string",
                    "financial_metrics": {
                        "revenue": "array",
                        "profit_margins": "object",
                        "growth_rates": "object"
                    }
                },
                "company_overview": {
                    "title": "string",
                    "content": "string",
                    "subsections": "array"
                },
                "valuation_analysis": {
                    "title": "string", 
                    "content": "string",
                    "subsections": "array"
                },
                "risk_assessment": {
                    "title": "string",
                    "content": "string", 
                    "subsections": "array"
                }
            }
        }
        
        return base_schema
    
    def validate_template_data(self, ticker: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate template data against expected schema"""
        
        schema = self.get_template_data_schema(ticker)
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Basic validation
        required_fields = ["ticker", "company_name", "sections"]
        for field in required_fields:
            if field not in data:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Missing required field: {field}")
        
        # Section validation
        if "sections" in data:
            for section_name, section_data in data["sections"].items():
                if not isinstance(section_data, dict):
                    validation_result["errors"].append(
                        f"Section {section_name} must be an object"
                    )
                    continue
                
                if "title" not in section_data:
                    validation_result["warnings"].append(
                        f"Section {section_name} missing title"
                    )
                
                if "content" not in section_data:
                    validation_result["warnings"].append(
                        f"Section {section_name} missing content"
                    )
        
        return validation_result
    
    def create_sample_data(self, ticker: str) -> Dict[str, Any]:
        """Create sample data for testing templates"""
        
        sample_data = {
            "ticker": ticker,
            "company_name": f"{ticker} Corporation",
            "executive_summary": {
                "content": f"<p>{ticker} demonstrates strong fundamentals with consistent growth trajectory.</p>",
                "recommendation": "Buy",
                "price_target": "$150.00",
                "current_price": "$135.50"
            },
            "financial_analysis": {
                "content": "<p>Financial performance shows robust revenue growth and improving margins.</p>",
                "revenue": [
                    {"year": "2021", "value": "$100B", "growth": "15%"},
                    {"year": "2022", "value": "$115B", "growth": "15%"},
                    {"year": "2023", "value": "$132B", "growth": "15%"}
                ]
            },
            "company_overview": {
                "content": f"<p>{ticker} is a leading company in its sector with strong competitive advantages.</p>",
                "business_model": "Diversified revenue streams with recurring subscription components.",
                "competitive_analysis": "Strong moat with network effects and switching costs."
            },
            "valuation_analysis": {
                "content": "<p>Valuation analysis indicates the stock is attractively priced.</p>",
                "dcf_analysis": "DCF model suggests fair value of $155 per share.",
                "peer_comparison": "Trading at discount to peer group average."
            },
            "risk_assessment": {
                "content": "<p>Key risks include regulatory changes and competitive pressures.</p>",
                "risk_factors": "Regulatory risk, competitive risk, market risk.",
                "mitigation_strategies": "Diversification, compliance programs, innovation investment."
            }
        }
        
        return sample_data
    
    def export_template_config(self) -> Dict[str, Any]:
        """Export current template configuration"""
        
        config = {
            "template_engine": "handlebars",
            "version": "2.0",
            "created": datetime.now().isoformat(),
            "templates": {
                "handlebars": {
                    "main": "stock_report.hbs",
                    "sections": [
                        "executive_summary.hbs",
                        "financial_analysis.hbs", 
                        "company_overview.hbs",
                        "valuation_analysis.hbs",
                        "risk_assessment.hbs"
                    ]
                },
                "react": {
                    "main": "ReportTemplate.jsx",
                    "components": [
                        "CoverPage.jsx",
                        "ExecutiveSummary.jsx",
                        "FinancialAnalysis.jsx",
                        "CompanyOverview.jsx", 
                        "ValuationAnalysis.jsx",
                        "RiskAssessment.jsx"
                    ]
                }
            },
            "styles": [
                "institutional-report.css"
            ],
            "supported_tickers": ["GOOGL", "AAPL", "MSFT", "default"]
        }
        
        return config

# Global integration service instance
template_service = TemplateIntegrationService()