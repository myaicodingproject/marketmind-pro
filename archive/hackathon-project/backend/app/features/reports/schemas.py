from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict, Any
from app.features.reports.models import ReportStatus, ReportType

class ReportRequest(BaseModel):
    ticker: str
    report_type: ReportType = ReportType.COMPREHENSIVE
    sections: Optional[List[str]] = None

class ReportResponse(BaseModel):
    id: int
    ticker: str
    company_name: str
    status: ReportStatus
    report_type: ReportType
    created_at: datetime
    completed_at: Optional[datetime]
    generation_time_seconds: Optional[int]
    
    class Config:
        from_attributes = True

class ReportDetail(ReportResponse):
    executive_summary: Optional[str]
    company_analysis: Optional[str]
    financial_analysis: Optional[str]
    valuation_analysis: Optional[str]
    risk_analysis: Optional[str]
    error_message: Optional[str]

class ReportProgress(BaseModel):
    report_id: int
    status: ReportStatus
    current_stage: str
    progress_percent: int
    estimated_completion: Optional[datetime]