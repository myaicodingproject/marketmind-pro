from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from enum import Enum

class ChartType(str, Enum):
    LINE = "line"
    BAR = "bar"
    PIE = "pie"
    DOUGHNUT = "doughnut"
    AREA = "area"
    SCATTER = "scatter"
    CANDLESTICK = "candlestick"

class ChartDataPoint(BaseModel):
    x: Union[str, float, datetime]
    y: Union[float, int]
    label: Optional[str] = None

class ChartDataset(BaseModel):
    label: str
    data: List[Union[ChartDataPoint, float, int]]
    backgroundColor: Optional[Union[str, List[str]]] = None
    borderColor: Optional[Union[str, List[str]]] = None
    borderWidth: Optional[int] = 2
    fill: Optional[bool] = False
    tension: Optional[float] = 0.1

class ChartOptions(BaseModel):
    responsive: bool = True
    maintainAspectRatio: bool = False
    plugins: Optional[Dict[str, Any]] = None
    scales: Optional[Dict[str, Any]] = None
    animation: Optional[Dict[str, Any]] = None

class ChartConfig(BaseModel):
    type: ChartType
    data: Dict[str, Any]
    options: Optional[ChartOptions] = None

class ChartResponse(BaseModel):
    chart_id: str
    title: str
    description: Optional[str] = None
    chart_type: ChartType
    config: ChartConfig
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

class FinancialChartRequest(BaseModel):
    ticker: str
    chart_type: ChartType
    period: str = Field(default="1Y", description="Time period: 1M, 3M, 6M, 1Y, 2Y, 5Y")
    metrics: Optional[List[str]] = Field(default=None, description="Specific metrics to include")
    comparison_tickers: Optional[List[str]] = Field(default=None, description="Tickers for comparison")

class ValuationChartRequest(BaseModel):
    ticker: str
    valuation_methods: List[str] = Field(default=["dcf", "peer_comparison", "historical_multiples"])
    scenarios: Optional[List[str]] = Field(default=["base", "bull", "bear"])

class RiskChartRequest(BaseModel):
    ticker: str
    risk_metrics: List[str] = Field(default=["volatility", "beta", "var", "sharpe_ratio"])
    benchmark: Optional[str] = Field(default="SPY", description="Benchmark ticker for comparison")

class ChartCacheInfo(BaseModel):
    cache_key: str
    expires_at: datetime
    last_updated: datetime
    hit_count: int = 0