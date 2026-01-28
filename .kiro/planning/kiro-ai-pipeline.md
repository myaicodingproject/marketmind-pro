# Kiro AI Pipeline Specifications

## 100% Kiro-Powered Architecture

### Core Philosophy
**All AI processing through Kiro CLI - Zero external LLM dependencies**
- No OpenAI API calls
- No Claude API calls  
- No other AI services
- Pure Kiro CLI for ALL AI processing

## Custom Kiro Prompts Library

### Core Analysis Prompts

#### 1. Company Narrative Analysis
**Prompt:** `@analyze-company-narrative`
**Purpose:** Extract business story, competitive position, and strategic direction
**Input:** Company ticker, basic financial data, recent news
**Output:** Structured narrative analysis with key themes and insights

```markdown
# @analyze-company-narrative Prompt Template
Analyze [TICKER] company narrative including:
1. Business model and value proposition
2. Competitive advantages and moats
3. Strategic direction and vision
4. Market position and differentiation
5. Key success factors and risks

Format output as structured JSON with sections for each analysis area.
```

#### 2. Executive Summary Generation
**Prompt:** `@create-executive-summary`
**Purpose:** Generate investment thesis and key recommendations
**Input:** Company analysis, financial metrics, market data
**Output:** 2-page executive summary with price targets and ratings

```markdown
# @create-executive-summary Prompt Template
Create executive summary for [TICKER] including:
1. Investment thesis (Buy/Hold/Sell with rationale)
2. Price target with methodology
3. Key catalysts and risks
4. Financial highlights
5. Peer comparison summary

Format as professional investment summary matching institutional standards.
```

#### 3. Financial Model Building
**Prompt:** `@build-financial-model`
**Purpose:** Create DCF and valuation models
**Input:** Historical financials, growth assumptions, market data
**Output:** Detailed financial projections and valuation analysis

```markdown
# @build-financial-model Prompt Template
Build comprehensive financial model for [TICKER]:
1. 3-year historical analysis
2. 3-year forward projections
3. DCF valuation with sensitivity analysis
4. Key ratio analysis and trends
5. Peer valuation comparison

Include detailed assumptions and methodology.
```

#### 4. Market Position Analysis
**Prompt:** `@analyze-market-position`
**Purpose:** Assess competitive landscape and market dynamics
**Input:** Industry data, competitor information, market trends
**Output:** Market analysis with TAM/SAM/SOM projections

```markdown
# @analyze-market-position Prompt Template
Analyze [TICKER] market position:
1. Total Addressable Market (TAM) sizing
2. Serviceable Addressable Market (SAM) analysis
3. Competitive landscape mapping
4. Market share trends and projections
5. Industry growth drivers and headwinds

Provide quantitative analysis where possible.
```

### Advanced Analysis Prompts

#### 5. Intrinsic Value Calculation
**Prompt:** `@calculate-intrinsic-value`
**Purpose:** Multiple valuation methodologies
**Input:** Financial model, peer data, market conditions
**Output:** Intrinsic value range with confidence intervals

#### 6. Peer Comparison Analysis
**Prompt:** `@compare-peer-companies`
**Purpose:** Detailed competitive benchmarking
**Input:** Company and peer financial data
**Output:** Comprehensive peer analysis with rankings

#### 7. Business Quality Assessment
**Prompt:** `@assess-business-quality`
**Purpose:** Evaluate competitive moats and sustainability
**Input:** Business model, financial metrics, industry dynamics
**Output:** Quality score with supporting analysis

#### 8. Price Target Generation
**Prompt:** `@generate-price-targets`
**Purpose:** Calculate target prices using multiple methods
**Input:** Valuation models, peer multiples, growth projections
**Output:** Price target range with methodology breakdown

### Chart Data Extraction Prompts

#### 9. Chart Data Extraction
**Prompt:** `@extract-chart-data`
**Purpose:** Extract and format data for visualization
**Input:** Financial data, analysis results
**Output:** JSON formatted data ready for Chart.js

```markdown
# @extract-chart-data Prompt Template
Extract chart data for [TICKER] visualization:
1. Revenue growth trends (5-year historical + 3-year projected)
2. Margin analysis (gross, operating, net)
3. Peer comparison metrics
4. Valuation multiples over time
5. Market share evolution

Format as Chart.js compatible JSON with proper labels and colors.
```

#### 10. Chart Configuration Generation
**Prompt:** `@generate-chart-config`
**Purpose:** Create Chart.js configurations
**Input:** Chart data, styling requirements
**Output:** Complete Chart.js configuration objects

```markdown
# @generate-chart-config Prompt Template
Generate Chart.js configuration for [CHART_TYPE]:
1. Data series with proper formatting
2. Color scheme matching brand guidelines
3. Responsive design settings
4. Interactive features (hover, click)
5. Professional styling and annotations

Output complete Chart.js config object.
```

## Kiro Integration Architecture

### Backend Integration
```python
# Pure Kiro CLI Integration
import subprocess
import json
import asyncio

class KiroStockEngine:
    def __init__(self):
        self.kiro_path = "/usr/local/bin/kiro-cli"
        self.prompts_path = "/mnt/c/kiro/.kiro/prompts"
    
    async def execute_prompt(self, prompt_name: str, context: dict) -> dict:
        """Execute Kiro prompt with context data"""
        try:
            # Prepare context file
            context_file = f"/tmp/kiro_context_{prompt_name}.json"
            with open(context_file, 'w') as f:
                json.dump(context, f)
            
            # Execute Kiro CLI command
            result = subprocess.run([
                self.kiro_path, "chat", 
                f"@{prompt_name}",
                "--context-file", context_file
            ], capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                return self.parse_kiro_output(result.stdout)
            else:
                raise Exception(f"Kiro execution failed: {result.stderr}")
                
        except Exception as e:
            print(f"Error executing {prompt_name}: {e}")
            return {"error": str(e)}
    
    def parse_kiro_output(self, output: str) -> dict:
        """Parse Kiro CLI output into structured data"""
        try:
            # Try to parse as JSON first
            return json.loads(output)
        except json.JSONDecodeError:
            # Fallback to text parsing
            return {"content": output, "type": "text"}
    
    async def generate_full_report(self, ticker: str) -> dict:
        """Generate complete stock report using Kiro pipeline"""
        
        # Step 1: Company narrative analysis
        narrative_context = {"ticker": ticker, "analysis_type": "narrative"}
        narrative = await self.execute_prompt("analyze-company-narrative", narrative_context)
        
        # Step 2: Financial model building
        financial_context = {"ticker": ticker, "narrative": narrative}
        financial_model = await self.execute_prompt("build-financial-model", financial_context)
        
        # Step 3: Market position analysis
        market_context = {"ticker": ticker, "financial_data": financial_model}
        market_analysis = await self.execute_prompt("analyze-market-position", market_context)
        
        # Step 4: Valuation analysis
        valuation_context = {
            "ticker": ticker,
            "financial_model": financial_model,
            "market_analysis": market_analysis
        }
        valuation = await self.execute_prompt("calculate-intrinsic-value", valuation_context)
        
        # Step 5: Executive summary
        summary_context = {
            "ticker": ticker,
            "narrative": narrative,
            "financial_model": financial_model,
            "market_analysis": market_analysis,
            "valuation": valuation
        }
        executive_summary = await self.execute_prompt("create-executive-summary", summary_context)
        
        # Step 6: Chart data extraction
        chart_context = {
            "ticker": ticker,
            "all_analysis": {
                "narrative": narrative,
                "financial": financial_model,
                "market": market_analysis,
                "valuation": valuation
            }
        }
        chart_data = await self.execute_prompt("extract-chart-data", chart_context)
        
        return {
            "ticker": ticker,
            "executive_summary": executive_summary,
            "narrative_analysis": narrative,
            "financial_model": financial_model,
            "market_analysis": market_analysis,
            "valuation_analysis": valuation,
            "chart_data": chart_data,
            "generated_at": datetime.utcnow().isoformat()
        }
```

### Report Generation Workflow
```python
class ReportGenerator:
    def __init__(self):
        self.kiro_engine = KiroStockEngine()
        self.chart_generator = ChartGenerator()
        self.pdf_generator = PDFGenerator()
    
    async def generate_report(self, ticker: str, user_id: str) -> dict:
        """Main report generation workflow"""
        
        # Step 1: Generate analysis using Kiro
        analysis = await self.kiro_engine.generate_full_report(ticker)
        
        # Step 2: Generate charts
        charts = await self.chart_generator.create_charts(analysis["chart_data"])
        
        # Step 3: Compile report
        report = {
            "id": f"{ticker}_{user_id}_{int(time.time())}",
            "ticker": ticker,
            "user_id": user_id,
            "sections": {
                "executive_summary": analysis["executive_summary"],
                "company_overview": analysis["narrative_analysis"],
                "financial_analysis": analysis["financial_model"],
                "market_analysis": analysis["market_analysis"],
                "valuation_analysis": analysis["valuation_analysis"]
            },
            "charts": charts,
            "metadata": {
                "generated_at": analysis["generated_at"],
                "generation_time": "5-8 minutes",
                "page_count": "25-30 pages"
            }
        }
        
        # Step 4: Cache report
        await self.cache_report(report)
        
        return report
```

## Quality Assurance Prompts

### Validation and Review
**Prompt:** `@validate-analysis-quality`
**Purpose:** Quality control for generated analysis
**Input:** Complete analysis sections
**Output:** Quality score and improvement suggestions

**Prompt:** `@cross-check-financials`
**Purpose:** Validate financial calculations
**Input:** Financial model and source data
**Output:** Accuracy verification and corrections

## Performance Optimization

### Prompt Caching
- Cache frequently used prompt results
- Implement smart cache invalidation
- Pre-generate analysis for popular stocks

### Parallel Processing
- Execute independent prompts in parallel
- Optimize prompt dependencies
- Implement timeout handling

### Error Handling
- Graceful degradation for prompt failures
- Retry logic with exponential backoff
- Fallback to cached or simplified analysis

*Last Updated: 2026-01-21*
