from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime

class ValidationLevel(Enum):
    AGENT = "agent"
    CROSS_SECTION = "cross_section"
    REPORT = "report"

class ValidationStatus(Enum):
    PENDING = "pending"
    PASSED = "passed"
    FAILED = "failed"
    RETRY = "retry"
    MANUAL_REVIEW = "manual_review"

class ReportSection(Enum):
    EXECUTIVE_SUMMARY = "executive_summary"
    COMPANY_ANALYSIS = "company_analysis"
    FINANCIAL_ANALYSIS = "financial_analysis"
    VALUATION_ANALYSIS = "valuation_analysis"
    RISK_ASSESSMENT = "risk_assessment"
    INVESTMENT_THESIS = "investment_thesis"
    TECHNICAL_ANALYSIS = "technical_analysis"
    MARKET_ANALYSIS = "market_analysis"

@dataclass
class ValidationResult:
    level: ValidationLevel
    section: Optional[ReportSection]
    status: ValidationStatus
    score: float
    issues: List[str]
    warnings: List[str]
    metadata: Dict[str, Any]
    timestamp: datetime
    retry_count: int = 0

@dataclass
class QualityMetrics:
    completeness_score: float
    accuracy_score: float
    consistency_score: float
    format_score: float
    overall_score: float
    
@dataclass
class ReportQuality:
    ticker: str
    report_id: str
    section_results: Dict[ReportSection, ValidationResult]
    cross_section_result: ValidationResult
    report_level_result: ValidationResult
    overall_metrics: QualityMetrics
    requires_manual_review: bool
    total_validation_time: float