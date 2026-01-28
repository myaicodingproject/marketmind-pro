"""
Request/Response Models for Hybrid PDF Generation System
Pydantic models for API validation and documentation
"""

from pydantic import BaseModel, Field, validator
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

class EnhancementLevel(str, Enum):
    """Available enhancement levels"""
    KIRO_ONLY = "kiro_only"
    STANDARD = "standard" 
    PREMIUM = "premium"

class Priority(str, Enum):
    """Processing priority levels"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"

class TaskStatus(str, Enum):
    """Task status values"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class HybridReportRequest(BaseModel):
    """Request model for hybrid report generation"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL)", min_length=1, max_length=10)
    enhancement_level: EnhancementLevel = Field(
        default=EnhancementLevel.STANDARD,
        description="Enhancement level for report processing"
    )
    include_charts: bool = Field(default=True, description="Include charts in PDF")
    priority: Priority = Field(default=Priority.NORMAL, description="Processing priority")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        """Validate stock symbol format"""
        if not v.isalpha():
            raise ValueError('Symbol must contain only letters')
        return v.upper()

class HybridReportResponse(BaseModel):
    """Response model for hybrid report generation"""
    success: bool
    task_id: Optional[str] = None
    pdf_path: Optional[str] = None
    quality_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    enhancement_level: Optional[EnhancementLevel] = None
    generation_time: Optional[str] = None
    symbol: Optional[str] = None
    error: Optional[str] = None

class ServiceStatus(BaseModel):
    """Individual service status"""
    name: str
    status: str
    last_check: Optional[str] = None
    error: Optional[str] = None

class HealthCheckResponse(BaseModel):
    """Health check response model"""
    status: str = Field(..., description="Overall system status")
    timestamp: str = Field(..., description="Check timestamp")
    services: Dict[str, str] = Field(..., description="Individual service statuses")
    version: str = Field(default="2.0.0", description="API version")

class TaskStatusResponse(BaseModel):
    """Task status response model"""
    task_id: str
    status: TaskStatus
    progress: Optional[float] = Field(None, ge=0.0, le=100.0, description="Progress percentage")
    estimated_completion: Optional[str] = None
    error: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class CapabilityFeature(BaseModel):
    """Feature description for capabilities"""
    level: EnhancementLevel
    description: str
    features: List[str]
    estimated_time: str

class CapabilitiesResponse(BaseModel):
    """System capabilities response"""
    enhancement_levels: List[CapabilityFeature]
    supported_formats: List[str] = ["PDF"]
    max_concurrent_reports: int = 5
    average_generation_time: Dict[str, str]

class ErrorResponse(BaseModel):
    """Standard error response"""
    detail: str
    error_code: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())

# Validation schemas for internal use
class ReportSection(BaseModel):
    """Individual report section model"""
    title: str
    content: str
    enhanced: bool = False
    error: Optional[str] = None

class ReportData(BaseModel):
    """Internal report data structure"""
    symbol: str
    sections: Dict[str, ReportSection]
    generation_method: str
    timestamp: str
    enhancement_level: Optional[EnhancementLevel] = None