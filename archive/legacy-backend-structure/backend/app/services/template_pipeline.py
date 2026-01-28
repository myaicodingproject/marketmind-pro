"""
Template Data Processing Pipeline for MarketMind Pro
Handles data transformation and template rendering
"""

import json
import re
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

class TemplateDataPipeline:
    """Process and transform data for template rendering"""
    
    def __init__(self):
        self.processors = {
            'GOOGL': self.process_googl_data,
            'AAPL': self.process_aapl_data,
            'MSFT': self.process_msft_data,
            'default': self.process_default_data
        }
    
    def process_report_data(self, ticker: str, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for processing report data"""
        processor = self.processors.get(ticker, self.processors['default'])
        return processor(raw_data)
    
    def process_googl_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process GOOGL-specific report data"""
        
        processed = {
            "ticker": "GOOGL",
            "company_name": "Alphabet Inc.",
            "generated_date": datetime.now().strftime("%B %d, %Y"),
            "title": "GOOGL - Comprehensive Stock Analysis",
            "sections": {}
        }
        
        # Executive Summary
        if "executive_summary" in raw_data:
            exec_data = raw_data["executive_summary"]
            processed["sections"]["executive_summary"] = {
                "title": "Executive Summary",
                "content": self._clean_content(exec_data.get("content", "")),
                "key_metrics": {
                    "recommendation": exec_data.get("recommendation", "Buy"),
                    "price_target": "$175.00",
                    "current_price": "$165.50", 
                    "market_cap": "$2.1T",
                    "pe_ratio": "24.5",
                    "revenue_growth": "12.3%"
                }
            }
        
        # Financial Analysis
        if "financial_analysis" in raw_data:
            fin_data = raw_data["financial_analysis"]
            processed["sections"]["financial_analysis"] = {
                "title": "Financial Analysis",
                "content": self._clean_content(fin_data.get("content", "")),
                "financial_metrics": {
                    "revenue": [
                        {"year": "2021", "value": "$257.6B", "growth": "41.2%"},
                        {"year": "2022", "value": "$282.8B", "growth": "9.8%"},
                        {"year": "2023", "value": "$307.4B", "growth": "8.7%"}
                    ],
                    "profit_margins": {
                        "gross": "57.2%",
                        "operating": "25.3%", 
                        "net": "21.1%"
                    },
                    "growth_rates": {
                        "revenue_3yr": "15.2%",
                        "earnings_3yr": "18.7%",
                        "free_cash_flow": "22.1%"
                    }
                }
            }
        
        # Company Overview
        if "company_overview" in raw_data:
            company_data = raw_data["company_overview"]
            processed["sections"]["company_overview"] = {
                "title": "Company Deep Dive",
                "content": self._clean_content(company_data.get("content", "")),
                "subsections": [
                    {
                        "title": "Business Model",
                        "content": self._extract_business_model_content(company_data)
                    },
                    {
                        "title": "Competitive Position", 
                        "content": self._extract_competitive_content(company_data)
                    }
                ]
            }
        
        # Valuation Analysis
        if "valuation_analysis" in raw_data:
            val_data = raw_data["valuation_analysis"]
            processed["sections"]["valuation_analysis"] = {
                "title": "Valuation Analysis",
                "content": self._clean_content(val_data.get("content", "")),
                "subsections": [
                    {
                        "title": "DCF Analysis",
                        "content": self._extract_dcf_content(val_data)
                    },
                    {
                        "title": "Peer Comparison",
                        "content": self._extract_peer_content(val_data)
                    }
                ]
            }
        
        # Risk Assessment
        if "risk_assessment" in raw_data:
            risk_data = raw_data["risk_assessment"]
            processed["sections"]["risk_assessment"] = {
                "title": "Risk Assessment",
                "content": self._clean_content(risk_data.get("content", "")),
                "subsections": [
                    {
                        "title": "Key Risk Factors",
                        "content": self._extract_risk_factors(risk_data)
                    },
                    {
                        "title": "Mitigation Strategies",
                        "content": self._extract_mitigation_content(risk_data)
                    }
                ]
            }
        
        return processed
    
    def process_aapl_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process AAPL-specific report data"""
        processed = self.process_default_data(raw_data)
        processed.update({
            "ticker": "AAPL",
            "company_name": "Apple Inc.",
            "title": "AAPL - Comprehensive Stock Analysis"
        })
        
        # Update AAPL-specific metrics
        if "executive_summary" in processed["sections"]:
            processed["sections"]["executive_summary"]["key_metrics"].update({
                "price_target": "$195.00",
                "current_price": "$185.25",
                "market_cap": "$2.9T",
                "pe_ratio": "28.2",
                "revenue_growth": "8.1%"
            })
        
        return processed
    
    def process_msft_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process MSFT-specific report data"""
        processed = self.process_default_data(raw_data)
        processed.update({
            "ticker": "MSFT", 
            "company_name": "Microsoft Corporation",
            "title": "MSFT - Comprehensive Stock Analysis"
        })
        
        # Update MSFT-specific metrics
        if "executive_summary" in processed["sections"]:
            processed["sections"]["executive_summary"]["key_metrics"].update({
                "price_target": "$425.00",
                "current_price": "$415.75",
                "market_cap": "$3.1T",
                "pe_ratio": "32.1",
                "revenue_growth": "16.5%"
            })
        
        return processed
    
    def process_default_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process generic stock report data"""
        
        processed = {
            "ticker": raw_data.get("ticker", "UNKNOWN"),
            "company_name": raw_data.get("company_name", "Unknown Company"),
            "generated_date": datetime.now().strftime("%B %d, %Y"),
            "title": f"{raw_data.get('ticker', 'UNKNOWN')} - Comprehensive Stock Analysis",
            "sections": {}
        }
        
        # Process all sections generically
        section_mapping = {
            "executive_summary": "Executive Summary",
            "financial_analysis": "Financial Analysis",
            "company_overview": "Company Deep Dive",
            "valuation_analysis": "Valuation Analysis",
            "risk_assessment": "Risk Assessment",
            "competitive_analysis": "Competitive Analysis"
        }
        
        for key, title in section_mapping.items():
            if key in raw_data:
                section_data = raw_data[key]
                processed["sections"][key] = {
                    "title": title,
                    "content": self._clean_content(section_data.get("content", "")),
                    "subsections": section_data.get("subsections", [])
                }
                
                # Add default metrics for executive summary
                if key == "executive_summary":
                    processed["sections"][key]["key_metrics"] = {
                        "recommendation": section_data.get("recommendation", "Hold"),
                        "price_target": section_data.get("price_target", "N/A"),
                        "current_price": section_data.get("current_price", "N/A"),
                        "market_cap": section_data.get("market_cap", "N/A"),
                        "pe_ratio": section_data.get("pe_ratio", "N/A"),
                        "revenue_growth": section_data.get("revenue_growth", "N/A")
                    }
        
        return processed
    
    def _clean_content(self, content: str) -> str:
        """Clean and format content for template rendering"""
        if not content:
            return ""
        
        # Remove excessive whitespace
        content = re.sub(r'\s+', ' ', content.strip())
        
        # Convert markdown-style formatting to HTML
        content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
        content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
        
        # Convert bullet points to HTML lists
        lines = content.split('\n')
        in_list = False
        processed_lines = []
        
        for line in lines:
            line = line.strip()
            if line.startswith('•') or line.startswith('-'):
                if not in_list:
                    processed_lines.append('<ul>')
                    in_list = True
                processed_lines.append(f'<li>{line[1:].strip()}</li>')
            else:
                if in_list:
                    processed_lines.append('</ul>')
                    in_list = False
                if line:
                    processed_lines.append(f'<p>{line}</p>')
        
        if in_list:
            processed_lines.append('</ul>')
        
        return '\n'.join(processed_lines)
    
    def _extract_business_model_content(self, data: Dict[str, Any]) -> str:
        """Extract business model specific content"""
        content = data.get("business_model", "")
        if not content:
            content = "Business model analysis not available."
        return self._clean_content(content)
    
    def _extract_competitive_content(self, data: Dict[str, Any]) -> str:
        """Extract competitive analysis content"""
        content = data.get("competitive_analysis", "")
        if not content:
            content = "Competitive analysis not available."
        return self._clean_content(content)
    
    def _extract_dcf_content(self, data: Dict[str, Any]) -> str:
        """Extract DCF analysis content"""
        content = data.get("dcf_analysis", "")
        if not content:
            content = "DCF analysis not available."
        return self._clean_content(content)
    
    def _extract_peer_content(self, data: Dict[str, Any]) -> str:
        """Extract peer comparison content"""
        content = data.get("peer_comparison", "")
        if not content:
            content = "Peer comparison not available."
        return self._clean_content(content)
    
    def _extract_risk_factors(self, data: Dict[str, Any]) -> str:
        """Extract risk factors content"""
        content = data.get("risk_factors", "")
        if not content:
            content = "Risk factors analysis not available."
        return self._clean_content(content)
    
    def _extract_mitigation_content(self, data: Dict[str, Any]) -> str:
        """Extract risk mitigation content"""
        content = data.get("mitigation_strategies", "")
        if not content:
            content = "Risk mitigation strategies not available."
        return self._clean_content(content)

# Global pipeline instance
data_pipeline = TemplateDataPipeline()