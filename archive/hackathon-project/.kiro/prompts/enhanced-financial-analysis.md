# Enhanced Financial Analysis Generator (Section 3/6)

## Role
You are a senior financial analyst specializing in comprehensive financial modeling with RAG-enhanced document processing and advanced projection capabilities.

## Task
Generate a comprehensive 8-page financial analysis as Section 3 of 6 parallel report sections, integrating RAG context for historical analysis and forward projections.

## Progress Tracking
**Section**: 3/6 - Financial Analysis
**Estimated Time**: 90-120 seconds
**Dependencies**: RAG financial statements, earnings data, peer benchmarks
**Output**: 8 pages + financial model + sensitivity analysis

## Input Data Integration
- **RAG Financial Data**: {rag_10k_financials} | {rag_10q_financials} | {rag_earnings_financials}
- **Historical Context**: {rag_3year_trends} | {rag_management_commentary} | {rag_guidance_tracking}
- **Peer Benchmarks**: {web_peer_financials} | {api_industry_metrics} | {rag_competitive_analysis}
- **Backend APIs**: {api_financial_statements} | {api_ratio_analysis} | {api_projection_models}

## Enhanced Output Structure

### FINANCIAL ANALYSIS - SECTION 3

#### Historical Performance Analysis (Pages 1-3)
**Three-Year Income Statement Progression** (RAG-Enhanced)
```
INCOME STATEMENT ANALYSIS           FY 2021    FY 2022    FY 2023    CAGR    Trend
Revenue
├─ Total Revenue                    $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
├─ Product Revenue                  $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
├─ Service Revenue                  $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
└─ Other Revenue                    $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]

Cost Structure
├─ Cost of Revenue                  $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
├─ Gross Profit                     $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
├─ Gross Margin %                   [%]%       [%]%       [%]%       [bps]   [↑/↓/→]

Operating Expenses
├─ R&D Expenses                     $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
├─ Sales & Marketing                $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
├─ General & Administrative         $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
├─ Total OpEx                       $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
└─ OpEx as % of Revenue             [%]%       [%]%       [%]%       [bps]   [↑/↓/→]

Profitability
├─ Operating Income                 $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
├─ Operating Margin %               [%]%       [%]%       [%]%       [bps]   [↑/↓/→]
├─ Net Income                       $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
├─ Net Margin %                     [%]%       [%]%       [%]%       [bps]   [↑/↓/→]
└─ EPS (Diluted)                    $[amt]     $[amt]     $[amt]     [%]%    [↑/↓/→]
```
*Source: [RAG citations from 10-K/10-Q with specific page numbers]*

**Management Commentary Integration** (RAG-Extracted)
- **Revenue Drivers**: "[Direct quote from latest earnings call about revenue performance]"
- **Margin Evolution**: "[Management explanation of margin trends from MD&A]"
- **Cost Management**: "[Management commentary on operational efficiency initiatives]"
- **Investment Priorities**: "[CapEx and R&D investment strategy from management]"

**Balance Sheet Strength Analysis** (Pages 4-5)
```
BALANCE SHEET EVOLUTION             FY 2021    FY 2022    FY 2023    Change   Quality
Assets
├─ Cash & Cash Equivalents          $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Short-term Investments           $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Accounts Receivable              $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Inventory                        $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Total Current Assets             $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ PP&E (Net)                       $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Intangible Assets                $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
└─ Total Assets                     $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]

Liabilities & Equity
├─ Accounts Payable                 $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Short-term Debt                  $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Total Current Liabilities        $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Long-term Debt                   $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Total Liabilities                $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
└─ Shareholders' Equity             $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]

Key Ratios
├─ Current Ratio                    [x]        [x]        [x]        [Δ]      [H/M/L]
├─ Quick Ratio                      [x]        [x]        [x]        [Δ]      [H/M/L]
├─ Debt-to-Equity                   [x]        [x]        [x]        [Δ]      [H/M/L]
├─ Interest Coverage                [x]        [x]        [x]        [Δ]      [H/M/L]
└─ Asset Turnover                   [x]        [x]        [x]        [Δ]      [H/M/L]
```

#### Cash Flow Analysis (RAG-Enhanced)
```
CASH FLOW STATEMENT                 FY 2021    FY 2022    FY 2023    CAGR     Quality
Operating Activities
├─ Net Income                       $[amt]     $[amt]     $[amt]     [%]%     
├─ Depreciation & Amortization      $[amt]     $[amt]     $[amt]     [%]%     
├─ Working Capital Changes          $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ Other Operating Activities       $[amt]     $[amt]     $[amt]     [%]%     
└─ Operating Cash Flow              $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]

Investing Activities
├─ Capital Expenditures             $[amt]     $[amt]     $[amt]     [%]%     
├─ Acquisitions                     $[amt]     $[amt]     $[amt]     [%]%     
├─ Asset Sales                      $[amt]     $[amt]     $[amt]     [%]%     
└─ Investing Cash Flow              $[amt]     $[amt]     $[amt]     [%]%     

Financing Activities
├─ Debt Issuance/(Repayment)        $[amt]     $[amt]     $[amt]     [%]%     
├─ Share Repurchases                $[amt]     $[amt]     $[amt]     [%]%     
├─ Dividends Paid                   $[amt]     $[amt]     $[amt]     [%]%     
└─ Financing Cash Flow              $[amt]     $[amt]     $[amt]     [%]%     

Free Cash Flow Analysis
├─ Operating Cash Flow              $[amt]     $[amt]     $[amt]     [%]%     
├─ Capital Expenditures             $[amt]     $[amt]     $[amt]     [%]%     
├─ Free Cash Flow                   $[amt]     $[amt]     $[amt]     [%]%     [H/M/L]
├─ FCF Margin %                     [%]%       [%]%       [%]%       [bps]    
├─ FCF per Share                    $[amt]     $[amt]     $[amt]     [%]%     
└─ FCF Yield %                      [%]%       [%]%       [%]%       [bps]    
```

#### Peer Comparison Analysis (Pages 6-7)
**Financial Metrics Benchmarking** (Web-Enhanced)
```
PEER COMPARISON MATRIX              Company    Peer 1     Peer 2     Peer 3     Industry   Percentile
Revenue Growth (3Y CAGR)           [%]%       [%]%       [%]%       [%]%       [%]%       [X]th
Gross Margin (TTM)                 [%]%       [%]%       [%]%       [%]%       [%]%       [X]th
Operating Margin (TTM)             [%]%       [%]%       [%]%       [%]%       [%]%       [X]th
Net Margin (TTM)                   [%]%       [%]%       [%]%       [%]%       [%]%       [X]th
ROE (TTM)                          [%]%       [%]%       [%]%       [%]%       [%]%       [X]th
ROA (TTM)                          [%]%       [%]%       [%]%       [%]%       [%]%       [X]th
ROIC (TTM)                         [%]%       [%]%       [%]%       [%]%       [%]%       [X]th
Debt/Equity                        [x]        [x]        [x]        [x]        [x]        [X]th
Current Ratio                      [x]        [x]        [x]        [x]        [x]        [X]th
FCF Yield                          [%]%       [%]%       [%]%       [%]%       [%]%       [X]th
```

#### Forward Projections (Page 8)
**Three-Year Financial Model** (RAG-Guided)
```
PROJECTION MODEL                    FY 2024E   FY 2025E   FY 2026E   Assumptions
Revenue Projections
├─ Total Revenue                    $[amt]     $[amt]     $[amt]     [Growth assumptions from RAG]
├─ Revenue Growth %                 [%]%       [%]%       [%]%       [Management guidance integration]
├─ Segment A Revenue                $[amt]     $[amt]     $[amt]     [Segment-specific drivers]
├─ Segment B Revenue                $[amt]     $[amt]     $[amt]     [Segment-specific drivers]

Profitability Projections
├─ Gross Profit                     $[amt]     $[amt]     $[amt]     [Margin expansion/contraction]
├─ Gross Margin %                   [%]%       [%]%       [%]%       [Cost structure evolution]
├─ Operating Income                 $[amt]     $[amt]     $[amt]     [Operating leverage assumptions]
├─ Operating Margin %               [%]%       [%]%       [%]%       [Efficiency improvements]
├─ Net Income                       $[amt]     $[amt]     $[amt]     [Tax rate assumptions]
├─ EPS (Diluted)                    $[amt]     $[amt]     $[amt]     [Share count projections]

Cash Flow Projections
├─ Operating Cash Flow              $[amt]     $[amt]     $[amt]     [Working capital assumptions]
├─ Capital Expenditures             $[amt]     $[amt]     $[amt]     [Management CapEx guidance]
├─ Free Cash Flow                   $[amt]     $[amt]     $[amt]     [FCF conversion assumptions]
├─ FCF per Share                    $[amt]     $[amt]     $[amt]     [Per share metrics]
```

**Key Modeling Assumptions** (RAG-Supported)
- **Revenue Growth**: [Management guidance] + [Market expansion] + [New products]
- **Margin Evolution**: [Cost synergies] + [Pricing power] + [Mix shift]
- **Investment Requirements**: [CapEx as % of revenue] based on [management commentary]
- **Working Capital**: [Historical patterns] + [Business model changes]

## Progress Tracking Integration
```python
progress_updates = [
    {"stage": "historical_analysis", "percent": 15, "message": "Processing 3-year financial statements"},
    {"stage": "ratio_analysis", "percent": 30, "message": "Calculating financial ratios and trends"},
    {"stage": "peer_benchmarking", "percent": 50, "message": "Benchmarking against peer group"},
    {"stage": "projection_modeling", "percent": 75, "message": "Building forward projection model"},
    {"stage": "sensitivity_analysis", "percent": 90, "message": "Running sensitivity scenarios"},
    {"stage": "completion", "percent": 100, "message": "Financial analysis completed"}
]
```

## RAG Financial Data Validation
**Source Reconciliation Matrix**
```
Financial Statement Item    10-K Value    10-Q Value    Earnings Call    Variance    Status
Total Revenue              $[amt]        $[amt]        $[amt]           [%]%        ✓/⚠/✗
Operating Income           $[amt]        $[amt]        $[amt]           [%]%        ✓/⚠/✗
Net Income                 $[amt]        $[amt]        $[amt]           [%]%        ✓/⚠/✗
Cash Flow from Operations  $[amt]        $[amt]        $[amt]           [%]%        ✓/⚠/✗
```

## Backend API Integration
```json
{
  "section_id": "financial_analysis",
  "completion_status": "completed",
  "output_pages": 8,
  "financial_model": {
    "revenue_cagr_3y": "[percentage]",
    "operating_margin_trend": "[improving/stable/declining]",
    "fcf_yield_current": "[percentage]",
    "peer_ranking": "[X] of [Y] peers"
  },
  "projection_confidence": "[High/Medium/Low]",
  "data_quality_score": "[X/100]"
}
```

## Quality Assurance Framework
- [ ] All financial data reconciled across RAG sources
- [ ] Peer comparisons use consistent time periods and methodologies
- [ ] Projections based on management guidance and historical trends
- [ ] Sensitivity analysis covers key variable ranges
- [ ] All calculations verified for mathematical accuracy
- [ ] Management commentary properly integrated and attributed
- [ ] Industry benchmarks current and relevant

Generate the complete Section 3 content with comprehensive financial modeling and RAG integration.