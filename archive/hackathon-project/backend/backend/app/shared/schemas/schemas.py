from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

# User schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

# Company schemas
class CompanyBase(BaseModel):
    ticker: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None
    market_cap: Optional[str] = None
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    extra_data: Optional[Dict[str, Any]] = None

class Company(CompanyBase):
    id: int
    extra_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Report schemas
class ReportBase(BaseModel):
    title: str
    report_type: str = "comprehensive"

class ReportCreate(BaseModel):
    ticker: str
    report_type: str = "comprehensive"

class Report(ReportBase):
    id: int
    user_id: int
    company_id: int
    status: str
    progress: int
    content: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# Token schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Chart schemas
class ChartRequest(BaseModel):
    financial_data: Dict[str, Any] = Field(..., description="Financial data for chart generation")
    chart_types: Optional[List[str]] = Field(None, description="Specific chart types to generate")
    
class ChartResponse(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    charts: Dict[str, Dict[str, Any]] = Field(..., description="Generated chart configurations")
    generated_at: datetime = Field(default_factory=datetime.now, description="Chart generation timestamp")
    chart_count: int = Field(..., description="Number of charts generated")

class ChartSummaryResponse(BaseModel):
    ticker: str = Field(..., description="Stock ticker symbol")
    available_charts: List[str] = Field(..., description="List of available chart types")
    data_quality: Dict[str, str] = Field(..., description="Data quality assessment for each chart")
    date_range: Dict[str, str] = Field(default_factory=dict, description="Date range of available data")
    last_updated: str = Field(..., description="Last data update timestamp")