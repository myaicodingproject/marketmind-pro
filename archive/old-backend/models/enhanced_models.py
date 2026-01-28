"""Enhanced Pydantic models for MarketMind Pro stock research platform."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Literal
from pydantic import BaseModel, Field, validator
from uuid import UUID, uuid4
from enum import Enum


class SectionType(str, Enum):
    """Report section types"""
    EXECUTIVE_SUMMARY = "executive_summary"
    COMPANY_ANALYSIS = "company_analysis"
    FINANCIAL_ANALYSIS = "financial_analysis"
    VALUATION_ANALYSIS = "valuation_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    MARKET_ANALYSIS = "market_analysis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    INVESTMENT_THESIS = "investment_thesis"


class ProcessingStatus(str, Enum):
    """Report processing status"""
    PENDING = "pending"
    PROCESSING = "processing"
    POLISHING = "polishing"
    POLISHED = "polished"
    COMPLETED = "completed"
    FAILED = "failed"


class SectionMetadata(BaseModel):
    """Metadata for section processing"""
    section_type: str
    word_count: int = 0
    processing_time: float = 0.0
    polished: bool = False


class SectionPolishRequest(BaseModel):
    """Request for section polishing"""
    section_type: str
    content: str
    context: Optional[Dict[str, Any]] = None


class SectionPolishResponse(BaseModel):
    """Response from section polishing"""
    section_type: str
    polished_content: str
    improvements: List[str] = []
    word_count: int = 0


class TableData(BaseModel):
    """Data structure for report tables."""
    headers: List[str] = Field(..., description="Column headers")
    rows: List[List[str]] = Field(..., description="Table row data")
    caption: Optional[str] = Field(None, description="Table caption")
    table_type: Literal["financial", "comparison", "metrics", "timeline"] = Field(..., description="Type of table")

    @validator('rows')
    def validate_rows(cls, v, values):
        if 'headers' in values and v:
            header_count = len(values['headers'])
            for row in v:
                if len(row) != header_count:
                    raise ValueError(f"Row length {len(row)} doesn't match header count {header_count}")
        return v


class ChartData(BaseModel):
    """Data structure for report charts."""
    chart_type: Literal["line", "bar", "pie", "scatter", "timeline"] = Field(..., description="Chart type")
    title: str = Field(..., description="Chart title")
    data: Dict[str, Any] = Field(..., description="Chart data dictionary")
    config: Dict[str, Any] = Field(default_factory=dict, description="Chart configuration options")


class MetricData(BaseModel):
    """Data structure for key metrics."""
    label: str = Field(..., description="Metric label")
    value: str = Field(..., description="Metric value")
    unit: Optional[str] = Field(None, description="Unit of measurement")
    change: Optional[str] = Field(None, description="Change from previous period")
    trend: Optional[Literal["up", "down", "flat"]] = Field(None, description="Trend direction")


class ReportSection(BaseModel):
    """Individual report section with content and visualizations."""
    section_type: Literal["executive_summary", "company_analysis", "financial_analysis", 
                         "valuation", "risk_assessment", "appendix"] = Field(..., description="Section type")
    title: str = Field(..., description="Section title")
    content: str = Field(..., description="Main section content")
    tables: List[TableData] = Field(default_factory=list, description="Section tables")
    charts: List[ChartData] = Field(default_factory=list, description="Section charts")
    metrics: List[MetricData] = Field(default_factory=list, description="Key metrics")
    raw_content: Optional[str] = Field(None, description="Raw AI-generated content")
    polished_content: Optional[str] = Field(None, description="Quality-audited content")

    @validator('content')
    def validate_content(cls, v):
        if len(v.strip()) < 100:
            raise ValueError("Section content must be at least 100 characters")
        return v


class EnhancedReport(BaseModel):
    """Complete stock research report with all sections and metadata."""
    id: int = Field(..., description="Unique report identifier")
    ticker: str = Field(..., description="Stock ticker symbol")
    title: str = Field(..., description="Report title")
    sections: Dict[str, ReportSection] = Field(default_factory=dict, description="Report sections by type")
    generated_at: datetime = Field(default_factory=datetime.utcnow, description="Generation timestamp")
    chart_images: Dict[str, Dict[str, str]] = Field(default_factory=dict, description="Chart images by section and title")
    status: ProcessingStatus = Field(default=ProcessingStatus.PROCESSING, description="Report processing status")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    @validator('ticker')
    def validate_ticker(cls, v):
        return v.upper().strip()

    @validator('sections')
    def validate_sections(cls, v):
        required_sections = {"executive_summary", "company_analysis", "financial_analysis", "valuation"}
        if not required_sections.issubset(v.keys()):
            missing = required_sections - v.keys()
            raise ValueError(f"Missing required sections: {missing}")
        return v

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v)
        }