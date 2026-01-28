"""
Report Structure and Assembly System
Defines professional report templates and organization
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import json

@dataclass
class ReportSection:
    """Individual report section definition"""
    id: str
    title: str
    order: int
    pages: int
    required: bool = True
    template: str = "default"

@dataclass
class ReportMetadata:
    """Report metadata and versioning"""
    version: str
    generated_at: datetime
    ticker: str
    company_name: str
    report_type: str
    total_pages: int
    sections_count: int
    generation_time: Optional[float] = None

class ReportStructure:
    """Professional report structure definition"""
    
    EXECUTIVE_SUMMARY = ReportSection(
        id="executive_summary",
        title="Executive Summary",
        order=1,
        pages=2,
        template="executive_summary"
    )
    
    COMPANY_DEEP_DIVE = ReportSection(
        id="company_deep_dive", 
        title="Company Deep Dive",
        order=2,
        pages=5,
        template="company_analysis"
    )
    
    FINANCIAL_ANALYSIS = ReportSection(
        id="financial_analysis",
        title="Financial Analysis", 
        order=3,
        pages=8,
        template="financial_analysis"
    )
    
    VALUATION_ANALYSIS = ReportSection(
        id="valuation_analysis",
        title="Valuation Analysis",
        order=4, 
        pages=6,
        template="valuation_analysis"
    )
    
    RISK_ASSESSMENT = ReportSection(
        id="risk_assessment",
        title="Risk Assessment",
        order=5,
        pages=3,
        template="risk_assessment"
    )
    
    APPENDIX = ReportSection(
        id="appendix",
        title="Appendix & Data Sources",
        order=6,
        pages=2,
        required=False,
        template="appendix"
    )
    
    @classmethod
    def get_comprehensive_structure(cls) -> List[ReportSection]:
        """Get complete comprehensive report structure"""
        return [
            cls.EXECUTIVE_SUMMARY,
            cls.COMPANY_DEEP_DIVE, 
            cls.FINANCIAL_ANALYSIS,
            cls.VALUATION_ANALYSIS,
            cls.RISK_ASSESSMENT,
            cls.APPENDIX
        ]
    
    @classmethod
    def get_total_pages(cls) -> int:
        """Calculate total pages for comprehensive report"""
        return sum(section.pages for section in cls.get_comprehensive_structure())

class ReportTemplate:
    """Report template definitions"""
    
    EXECUTIVE_SUMMARY_TEMPLATE = {
        "sections": [
            {"title": "Investment Recommendation", "content_type": "recommendation"},
            {"title": "Key Financial Metrics", "content_type": "metrics_table"},
            {"title": "Price Target & Valuation", "content_type": "price_target"},
            {"title": "Key Catalysts & Risks", "content_type": "catalysts_risks"},
            {"title": "Investment Thesis Summary", "content_type": "thesis_summary"}
        ],
        "charts": ["price_performance", "key_metrics_comparison"],
        "styling": "executive"
    }
    
    COMPANY_ANALYSIS_TEMPLATE = {
        "sections": [
            {"title": "Business Model Overview", "content_type": "business_model"},
            {"title": "Competitive Position", "content_type": "competitive_analysis"},
            {"title": "Market Opportunity", "content_type": "market_analysis"},
            {"title": "Management Team", "content_type": "management_analysis"},
            {"title": "Recent Developments", "content_type": "news_analysis"}
        ],
        "charts": ["market_share", "competitive_positioning", "business_segments"],
        "styling": "analytical"
    }
    
    FINANCIAL_ANALYSIS_TEMPLATE = {
        "sections": [
            {"title": "Revenue Analysis", "content_type": "revenue_analysis"},
            {"title": "Profitability Metrics", "content_type": "profitability_analysis"},
            {"title": "Balance Sheet Strength", "content_type": "balance_sheet_analysis"},
            {"title": "Cash Flow Analysis", "content_type": "cash_flow_analysis"},
            {"title": "Financial Projections", "content_type": "projections"}
        ],
        "charts": ["revenue_trends", "profit_margins", "balance_sheet_metrics", "cash_flow_trends"],
        "styling": "financial"
    }
    
    VALUATION_ANALYSIS_TEMPLATE = {
        "sections": [
            {"title": "DCF Valuation Model", "content_type": "dcf_analysis"},
            {"title": "Peer Comparison Analysis", "content_type": "peer_analysis"},
            {"title": "Scenario Analysis", "content_type": "scenario_analysis"},
            {"title": "Valuation Summary", "content_type": "valuation_summary"}
        ],
        "charts": ["dcf_sensitivity", "peer_multiples", "valuation_scenarios"],
        "styling": "valuation"
    }
    
    RISK_ASSESSMENT_TEMPLATE = {
        "sections": [
            {"title": "Business Risks", "content_type": "business_risks"},
            {"title": "Financial Risks", "content_type": "financial_risks"},
            {"title": "Market & Industry Risks", "content_type": "market_risks"},
            {"title": "Risk Mitigation", "content_type": "risk_mitigation"}
        ],
        "charts": ["risk_matrix", "sensitivity_analysis"],
        "styling": "risk"
    }
    
    @classmethod
    def get_template(cls, template_name: str) -> Dict[str, Any]:
        """Get template by name"""
        templates = {
            "executive_summary": cls.EXECUTIVE_SUMMARY_TEMPLATE,
            "company_analysis": cls.COMPANY_ANALYSIS_TEMPLATE,
            "financial_analysis": cls.FINANCIAL_ANALYSIS_TEMPLATE,
            "valuation_analysis": cls.VALUATION_ANALYSIS_TEMPLATE,
            "risk_assessment": cls.RISK_ASSESSMENT_TEMPLATE
        }
        return templates.get(template_name, {})

class ReportAssembler:
    """Assembles report sections into final document"""
    
    def __init__(self):
        self.structure = ReportStructure()
        self.template = ReportTemplate()
    
    def assemble_report(self, sections_data: Dict[str, Any], metadata: ReportMetadata) -> Dict[str, Any]:
        """Assemble complete report from sections"""
        report_sections = self.structure.get_comprehensive_structure()
        
        assembled_report = {
            "metadata": {
                "version": metadata.version,
                "generated_at": metadata.generated_at.isoformat(),
                "ticker": metadata.ticker,
                "company_name": metadata.company_name,
                "report_type": metadata.report_type,
                "total_pages": metadata.total_pages,
                "sections_count": len(report_sections),
                "generation_time": metadata.generation_time
            },
            "sections": [],
            "charts": [],
            "styling": self._get_report_styling()
        }
        
        for section in report_sections:
            if section.id in sections_data:
                section_content = self._format_section(section, sections_data[section.id])
                assembled_report["sections"].append(section_content)
        
        return assembled_report
    
    def _format_section(self, section: ReportSection, content: Dict[str, Any]) -> Dict[str, Any]:
        """Format individual section with template"""
        template = self.template.get_template(section.template)
        
        return {
            "id": section.id,
            "title": section.title,
            "order": section.order,
            "pages": section.pages,
            "template": section.template,
            "content": content,
            "charts": template.get("charts", []),
            "styling": template.get("styling", "default")
        }
    
    def _get_report_styling(self) -> Dict[str, Any]:
        """Get professional report styling"""
        return {
            "theme": "institutional",
            "colors": {
                "primary": "#1f2937",
                "secondary": "#374151", 
                "accent": "#3b82f6",
                "success": "#10b981",
                "warning": "#f59e0b",
                "danger": "#ef4444"
            },
            "fonts": {
                "heading": "Inter, sans-serif",
                "body": "Inter, sans-serif",
                "mono": "JetBrains Mono, monospace"
            },
            "layout": {
                "page_size": "A4",
                "margins": {"top": 1, "bottom": 1, "left": 1, "right": 1},
                "header_height": 0.75,
                "footer_height": 0.5
            }
        }

class ReportVersioning:
    """Handle report versioning and metadata"""
    
    @staticmethod
    def create_metadata(ticker: str, company_name: str, report_type: str = "comprehensive") -> ReportMetadata:
        """Create report metadata"""
        structure = ReportStructure()
        
        return ReportMetadata(
            version="1.0.0",
            generated_at=datetime.now(),
            ticker=ticker.upper(),
            company_name=company_name,
            report_type=report_type,
            total_pages=structure.get_total_pages(),
            sections_count=len(structure.get_comprehensive_structure())
        )
    
    @staticmethod
    def update_generation_time(metadata: ReportMetadata, generation_time: float) -> ReportMetadata:
        """Update metadata with generation time"""
        metadata.generation_time = generation_time
        return metadata