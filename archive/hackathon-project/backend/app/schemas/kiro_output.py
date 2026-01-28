from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from enum import Enum

class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    SCATTER = "scatter"

class RecommendationType(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    HOLD = "HOLD"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"

class ChartData(BaseModel):
    type: ChartType
    title: str
    data: Dict[str, Any]
    labels: List[str]

class TableData(BaseModel):
    title: str
    headers: List[str]
    rows: List[List[Any]]

class Metric(BaseModel):
    name: str
    value: Any
    unit: Optional[str] = None
    change: Optional[float] = None

class Recommendation(BaseModel):
    type: RecommendationType
    confidence: float = Field(ge=0, le=1)
    reasoning: str
    price_target: Optional[float] = None

class KiroOutput(BaseModel):
    analysis: str = Field(min_length=1)
    key_insights: List[str] = Field(min_items=1)
    metrics: List[Metric]
    charts: List[ChartData] = Field(default_factory=list)
    tables: List[TableData] = Field(default_factory=list)
    recommendations: List[Recommendation] = Field(default_factory=list)

    @validator('key_insights')
    def validate_insights(cls, v):
        if not v or all(not insight.strip() for insight in v):
            raise ValueError('At least one non-empty insight required')
        return v

    class Config:
        schema_extra = {
            "example": {
                "analysis": "AAPL shows strong fundamentals with revenue growth of 8.2%",
                "key_insights": ["Strong iPhone sales", "Services revenue growing"],
                "metrics": [{"name": "P/E Ratio", "value": 28.5, "unit": "x"}],
                "charts": [{"type": "line", "title": "Revenue Trend", "data": {}, "labels": []}],
                "tables": [{"title": "Financials", "headers": ["Year", "Revenue"], "rows": []}],
                "recommendations": [{"type": "BUY", "confidence": 0.85, "reasoning": "Strong growth"}]
            }
        }