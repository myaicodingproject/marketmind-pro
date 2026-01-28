"""
Handlebars Template Engine Service for MarketMind Pro
Converts from Jinja2 to Handlebars with React component integration
"""

import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
import pybars
from datetime import datetime

class HandlebarsTemplateEngine:
    def __init__(self):
        self.compiler = pybars.Compiler()
        self.templates = {}
        self.helpers = {}
        self._register_helpers()
    
    def _register_helpers(self):
        """Register custom Handlebars helpers"""
        
        def format_currency(this, value):
            if not value:
                return "$0.00"
            try:
                num = float(str(value).replace('$', '').replace(',', ''))
                return f"${num:,.2f}"
            except:
                return str(value)
        
        def format_percent(this, value):
            if not value:
                return "0.0%"
            try:
                num = float(str(value).replace('%', ''))
                return f"{num:.1f}%"
            except:
                return str(value)
        
        def format_date(this, value):
            if not value:
                return datetime.now().strftime("%B %d, %Y")
            return value
        
        def equals(this, a, b):
            return a == b
        
        def greater_than(this, a, b):
            try:
                return float(a) > float(b)
            except:
                return False
        
        def recommendation_class(this, recommendation):
            if not recommendation:
                return ""
            rec = str(recommendation).lower()
            if rec in ['buy', 'strong buy']:
                return "recommendation-buy"
            elif rec in ['sell', 'strong sell']:
                return "recommendation-sell"
            else:
                return "recommendation-hold"
        
        # Register helpers
        self.compiler.register_helper('formatCurrency', format_currency)
        self.compiler.register_helper('formatPercent', format_percent)
        self.compiler.register_helper('formatDate', format_date)
        self.compiler.register_helper('eq', equals)
        self.compiler.register_helper('gt', greater_than)
        self.compiler.register_helper('recommendation_class', recommendation_class)
    
    def load_template(self, template_path: str) -> str:
        """Load and compile Handlebars template"""
        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # Convert Jinja2 syntax to Handlebars
        template_content = self._convert_jinja_to_handlebars(template_content)
        
        compiled = self.compiler.compile(template_content)
        self.templates[template_path] = compiled
        return template_content
    
    def _convert_jinja_to_handlebars(self, content: str) -> str:
        """Convert Jinja2 template syntax to Handlebars"""
        
        # Convert variable syntax: {{ var }} stays the same
        # Convert loops: {% for item in items %} -> {{#each items}}
        content = re.sub(r'{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%}', r'{{#each \2}}', content)
        content = re.sub(r'{%\s*endfor\s*%}', r'{{/each}}', content)
        
        # Convert conditionals: {% if condition %} -> {{#if condition}}
        content = re.sub(r'{%\s*if\s+(.+?)\s*%}', r'{{#if \1}}', content)
        content = re.sub(r'{%\s*elif\s+(.+?)\s*%}', r'{{else if \1}}', content)
        content = re.sub(r'{%\s*else\s*%}', r'{{else}}', content)
        content = re.sub(r'{%\s*endif\s*%}', r'{{/if}}', content)
        
        # Convert filters: {{ value | filter }} -> {{filter value}}
        content = re.sub(r'{{\s*(.+?)\s*\|\s*safe\s*}}', r'{{{{\1}}}}', content)
        content = re.sub(r'{{\s*(.+?)\s*\|\s*(\w+)\s*}}', r'{{\2 \1}}', content)
        
        # Convert loop variables: loop.index -> @index
        content = re.sub(r'loop\.index', '@index', content)
        content = re.sub(r'loop\.first', '@first', content)
        content = re.sub(r'loop\.last', '@last', content)
        
        return content
    
    def render(self, template_path: str, data: Dict[str, Any]) -> str:
        """Render template with data"""
        if template_path not in self.templates:
            self.load_template(template_path)
        
        template = self.templates[template_path]
        return template(data)
    
    def render_section(self, section_name: str, section_data: Dict[str, Any]) -> str:
        """Render individual report section"""
        template_path = f"templates/sections/{section_name}.hbs"
        return self.render(template_path, section_data)

class TemplateDataProcessor:
    """Process and structure data for template rendering"""
    
    @staticmethod
    def process_googl_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process GOOGL report data for template rendering"""
        
        processed = {
            "ticker": "GOOGL",
            "company_name": "Alphabet Inc.",
            "generated_date": datetime.now().strftime("%B %d, %Y"),
            "title": "GOOGL - Comprehensive Stock Analysis",
            "sections": {}
        }
        
        # Process executive summary
        if "executive_summary" in raw_data:
            exec_data = raw_data["executive_summary"]
            processed["sections"]["executive_summary"] = {
                "title": "Executive Summary",
                "content": exec_data.get("content", ""),
                "key_metrics": {
                    "recommendation": exec_data.get("recommendation", "Hold"),
                    "price_target": exec_data.get("price_target", "$175.00"),
                    "current_price": exec_data.get("current_price", "$165.50"),
                    "market_cap": exec_data.get("market_cap", "$2.1T"),
                    "pe_ratio": exec_data.get("pe_ratio", "24.5"),
                    "revenue_growth": exec_data.get("revenue_growth", "12.3%")
                }
            }
        
        # Process financial analysis
        if "financial_analysis" in raw_data:
            fin_data = raw_data["financial_analysis"]
            processed["sections"]["financial_analysis"] = {
                "title": "Financial Analysis",
                "content": fin_data.get("content", ""),
                "financial_metrics": {
                    "revenue": fin_data.get("revenue", []),
                    "profit_margins": fin_data.get("profit_margins", {}),
                    "growth_rates": fin_data.get("growth_rates", {})
                }
            }
        
        # Process other sections
        section_mapping = {
            "company_overview": "Company Deep Dive",
            "valuation_analysis": "Valuation Analysis", 
            "risk_assessment": "Risk Assessment",
            "competitive_analysis": "Competitive Analysis"
        }
        
        for key, title in section_mapping.items():
            if key in raw_data:
                processed["sections"][key] = {
                    "title": title,
                    "content": raw_data[key].get("content", ""),
                    "subsections": raw_data[key].get("subsections", [])
                }
        
        return processed

# Global template engine instance
template_engine = HandlebarsTemplateEngine()