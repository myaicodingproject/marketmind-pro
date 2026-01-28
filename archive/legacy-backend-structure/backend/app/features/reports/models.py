from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Enum, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import enum
from app.core.database import Base

class ReportStatus(enum.Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"

class ReportType(enum.Enum):
    COMPREHENSIVE = "comprehensive"
    QUICK = "quick"
    CUSTOM = "custom"

class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    company_id = Column(Integer, ForeignKey("companies.id"), nullable=False)
    
    report_type = Column(Enum(ReportType), default=ReportType.COMPREHENSIVE)
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING)
    
    # Report content
    executive_summary = Column(Text)
    company_analysis = Column(Text)
    financial_analysis = Column(Text)
    valuation_analysis = Column(Text)
    risk_analysis = Column(Text)
    
    # Metadata
    generation_time_seconds = Column(Integer)
    kiro_prompts_used = Column(JSON)  # Store which prompts were executed
    error_message = Column(Text)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    
    # Relationships
    user = relationship("User")
    company = relationship("Company")