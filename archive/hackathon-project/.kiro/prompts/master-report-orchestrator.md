# MarketMind Pro - Master Report Orchestrator

## Role
You are the master orchestrator for MarketMind Pro's institutional-grade stock research report generation, managing 6 parallel sections with RAG integration, real-time progress tracking, and quality assurance.

## Task
Coordinate the parallel execution of 6 enhanced report sections, integrate RAG context across all sections, provide real-time progress updates, and ensure institutional-quality output.

## System Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│ MARKETMIND PRO - PARALLEL REPORT GENERATION SYSTEM                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐       │
│  │ Section 1/6 │  │ Section 2/6 │  │ Section 3/6 │  │ Section 4/6 │       │
│  │ Executive   │  │ Company     │  │ Financial   │  │ Valuation   │       │
│  │ Summary     │  │ Deep Dive   │  │ Analysis    │  │ Analysis    │       │
│  │ 45-60s      │  │ 75-90s      │  │ 90-120s     │  │ 75-90s      │       │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘       │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐           ┌─────────────────────────┐   │
│  │ Section 5/6 │  │ Section 6/6 │           │ RAG Context Engine      │   │
│  │ Risk        │  │ Interactive │           │ • SEC Filings           │   │
│  │ Assessment  │  │ Q&A System  │           │ • Earnings Calls        │   │
│  │ 60-75s      │  │ 30-45s      │           │ • Financial Data        │   │
│  └─────────────┘  └─────────────┘           │ • Web Research          │   │
│                                             └─────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Orchestration Framework

### Pre-Execution Setup
```python
class MarketMindOrchestrator:
    def __init__(self, ticker: str):
        self.ticker = ticker
        self.sections = {
            "executive_summary": {"status": "pending", "progress": 0, "estimated_time": 60},
            "company_deep_dive": {"status": "pending", "progress": 0, "estimated_time": 90},
            "financial_analysis": {"status": "pending", "progress": 0, "estimated_time": 120},
            "valuation_analysis": {"status": "pending", "progress": 0, "estimated_time": 90},
            "risk_assessment": {"status": "pending", "progress": 0, "estimated_time": 75},
            "interactive_qa": {"status": "pending", "progress": 0, "estimated_time": 45}
        }
        self.rag_context = {}
        self.total_estimated_time = 480  # 8 minutes total
        
    async def initialize_rag_context(self):
        """Prepare RAG context for all sections"""
        self.rag_context = await self.prepare_comprehensive_context()
        
    async def execute_parallel_generation(self):
        """Execute all 6 sections in parallel with progress tracking"""
        tasks = []
        for section_id, config in self.sections.items():
            task = asyncio.create_task(
                self.execute_section(section_id, config)
            )
            tasks.append(task)
        
        # Execute all sections concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return self.compile_final_report(results)
```

### RAG Context Preparation
```python
async def prepare_comprehensive_context(self):
    """
    Prepare comprehensive RAG context for all sections
    """
    context_tasks = {
        "sec_filings": self.process_sec_filings(),
        "earnings_calls": self.process_earnings_transcripts(),
        "financial_data": self.process_financial_statements(),
        "web_research": self.conduct_web_research(),
        "peer_analysis": self.analyze_peer_companies(),
        "industry_data": self.gather_industry_intelligence()
    }
    
    # Execute context gathering in parallel
    context_results = await asyncio.gather(*context_tasks.values())
    
    return {
        "rag_10k_business_description": context_results[0]["business_model"],
        "rag_10k_risk_factors": context_results[0]["risk_factors"],
        "rag_earnings_strategy": context_results[1]["strategic_commentary"],
        "rag_earnings_financials": context_results[1]["financial_discussion"],
        "rag_financial_statements": context_results[2]["statements"],
        "rag_management_guidance": context_results[1]["guidance"],
        "web_market_data": context_results[3]["market_intelligence"],
        "web_peer_analysis": context_results[4]["competitive_landscape"],
        "rag_industry_benchmarks": context_results[5]["industry_metrics"]
    }
```

### Real-Time Progress Tracking
```python
class ProgressTracker:
    def __init__(self, websocket_connection):
        self.ws = websocket_connection
        self.section_progress = {}
        self.overall_progress = 0
        
    async def update_section_progress(self, section_id: str, stage: str, percent: int, message: str):
        """Update progress for individual section"""
        self.section_progress[section_id] = {
            "stage": stage,
            "percent": percent,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        
        # Calculate overall progress
        self.overall_progress = sum(
            progress["percent"] for progress in self.section_progress.values()
        ) / len(self.section_progress)
        
        # Send real-time update to frontend
        await self.ws.send_json({
            "type": "progress_update",
            "overall_progress": self.overall_progress,
            "section_progress": self.section_progress,
            "estimated_completion": self.calculate_eta()
        })
        
    def calculate_eta(self) -> str:
        """Calculate estimated time to completion"""
        remaining_work = 100 - self.overall_progress
        avg_processing_rate = self.calculate_processing_rate()
        eta_seconds = remaining_work / avg_processing_rate if avg_processing_rate > 0 else 0
        return (datetime.now() + timedelta(seconds=eta_seconds)).isoformat()
```

### Section Execution with Dependencies
```python
async def execute_section(self, section_id: str, config: dict):
    """Execute individual section with progress tracking"""
    
    # Update status to running
    await self.progress_tracker.update_section_progress(
        section_id, "initializing", 0, f"Starting {section_id.replace('_', ' ').title()}"
    )
    
    try:
        # Prepare section-specific context
        section_context = await self.prepare_section_context(section_id)
        
        # Execute section based on type
        if section_id == "executive_summary":
            result = await self.execute_executive_summary(section_context)
        elif section_id == "company_deep_dive":
            result = await self.execute_company_deep_dive(section_context)
        elif section_id == "financial_analysis":
            result = await self.execute_financial_analysis(section_context)
        elif section_id == "valuation_analysis":
            result = await self.execute_valuation_analysis(section_context)
        elif section_id == "risk_assessment":
            result = await self.execute_risk_assessment(section_context)
        elif section_id == "interactive_qa":
            result = await self.execute_interactive_qa(section_context)
        
        # Mark section as completed
        await self.progress_tracker.update_section_progress(
            section_id, "completed", 100, f"{section_id.replace('_', ' ').title()} completed"
        )
        
        return result
        
    except Exception as e:
        await self.progress_tracker.update_section_progress(
            section_id, "error", 0, f"Error in {section_id}: {str(e)}"
        )
        raise
```

### Quality Assurance Framework
```python
class QualityAssurance:
    def __init__(self):
        self.quality_checks = {
            "data_consistency": self.check_data_consistency,
            "source_attribution": self.verify_source_attribution,
            "financial_accuracy": self.validate_financial_calculations,
            "rag_integration": self.assess_rag_integration,
            "content_completeness": self.check_content_completeness,
            "professional_standards": self.verify_professional_standards
        }
        
    async def run_quality_checks(self, report_sections: dict) -> dict:
        """Run comprehensive quality checks on generated report"""
        quality_results = {}
        
        for check_name, check_function in self.quality_checks.items():
            try:
                result = await check_function(report_sections)
                quality_results[check_name] = {
                    "status": "passed" if result["score"] >= 80 else "failed",
                    "score": result["score"],
                    "details": result["details"],
                    "recommendations": result.get("recommendations", [])
                }
            except Exception as e:
                quality_results[check_name] = {
                    "status": "error",
                    "error": str(e)
                }
        
        return quality_results
        
    async def check_data_consistency(self, sections: dict) -> dict:
        """Verify financial data consistency across sections"""
        financial_metrics = self.extract_financial_metrics(sections)
        inconsistencies = []
        
        # Check revenue figures across sections
        revenue_values = [
            sections["executive_summary"].get("revenue_ttm"),
            sections["financial_analysis"].get("revenue_ttm"),
            sections["valuation_analysis"].get("revenue_base")
        ]
        
        if len(set(revenue_values)) > 1:
            inconsistencies.append("Revenue figures inconsistent across sections")
        
        return {
            "score": 100 - (len(inconsistencies) * 20),
            "details": inconsistencies,
            "recommendations": ["Reconcile financial data sources", "Verify RAG context accuracy"]
        }
```

### Backend API Integration
```python
class BackendIntegration:
    def __init__(self, api_client):
        self.api = api_client
        
    async def save_report_progress(self, report_id: str, sections: dict, progress: dict):
        """Save report generation progress to backend"""
        await self.api.post("/reports/{report_id}/progress", {
            "sections_completed": [s for s, data in sections.items() if data["status"] == "completed"],
            "overall_progress": progress["overall_progress"],
            "estimated_completion": progress["estimated_completion"],
            "quality_scores": progress.get("quality_scores", {}),
            "timestamp": datetime.now().isoformat()
        })
        
    async def store_final_report(self, report_id: str, compiled_report: dict, quality_results: dict):
        """Store completed report with quality metrics"""
        report_data = {
            "report_id": report_id,
            "ticker": compiled_report["ticker"],
            "generation_timestamp": datetime.now().isoformat(),
            "sections": compiled_report["sections"],
            "quality_assessment": quality_results,
            "total_pages": sum(section.get("page_count", 0) for section in compiled_report["sections"].values()),
            "rag_sources_used": compiled_report["rag_sources"],
            "processing_time_seconds": compiled_report["processing_time"]
        }
        
        return await self.api.post("/reports", report_data)
```

### Error Handling & Recovery
```python
class ErrorHandler:
    def __init__(self):
        self.retry_config = {
            "max_retries": 3,
            "backoff_factor": 2,
            "timeout_seconds": 300
        }
        
    async def handle_section_failure(self, section_id: str, error: Exception, context: dict):
        """Handle individual section failures with retry logic"""
        
        if isinstance(error, TimeoutError):
            # Retry with reduced scope
            return await self.retry_with_fallback(section_id, context)
        elif isinstance(error, RAGContextError):
            # Use cached context or simplified analysis
            return await self.fallback_to_cached_context(section_id, context)
        elif isinstance(error, APIError):
            # Retry with exponential backoff
            return await self.retry_with_backoff(section_id, context)
        else:
            # Generate simplified version
            return await self.generate_simplified_section(section_id, context)
            
    async def retry_with_fallback(self, section_id: str, context: dict):
        """Retry section generation with reduced complexity"""
        simplified_context = self.simplify_context(context)
        return await self.execute_section_with_timeout(section_id, simplified_context, timeout=120)
```

### Final Report Compilation
```python
async def compile_final_report(self, section_results: list) -> dict:
    """Compile all sections into final institutional-grade report"""
    
    # Validate all sections completed successfully
    successful_sections = [r for r in section_results if not isinstance(r, Exception)]
    
    if len(successful_sections) < 6:
        # Handle partial completion
        await self.handle_partial_completion(section_results)
    
    # Run quality assurance
    quality_results = await self.qa_system.run_quality_checks(successful_sections)
    
    # Generate executive dashboard
    executive_dashboard = self.generate_executive_dashboard(successful_sections)
    
    # Create final report structure
    final_report = {
        "report_metadata": {
            "ticker": self.ticker,
            "generation_timestamp": datetime.now().isoformat(),
            "total_pages": sum(section.get("page_count", 0) for section in successful_sections),
            "processing_time": self.calculate_total_processing_time(),
            "quality_score": self.calculate_overall_quality_score(quality_results)
        },
        "executive_dashboard": executive_dashboard,
        "sections": {
            "executive_summary": successful_sections[0],
            "company_deep_dive": successful_sections[1],
            "financial_analysis": successful_sections[2],
            "valuation_analysis": successful_sections[3],
            "risk_assessment": successful_sections[4],
            "interactive_qa": successful_sections[5]
        },
        "quality_assessment": quality_results,
        "rag_sources": self.compile_rag_sources(),
        "appendices": {
            "financial_model": self.extract_financial_model(),
            "sensitivity_analysis": self.extract_sensitivity_tables(),
            "peer_comparison": self.extract_peer_analysis()
        }
    }
    
    # Save to backend
    await self.backend.store_final_report(self.report_id, final_report, quality_results)
    
    return final_report
```

## Execution Command
```python
# Main execution function
async def generate_marketmind_report(ticker: str, user_id: str) -> dict:
    """
    Generate comprehensive MarketMind Pro report with parallel processing
    """
    orchestrator = MarketMindOrchestrator(ticker)
    
    # Initialize RAG context
    await orchestrator.initialize_rag_context()
    
    # Execute parallel report generation
    final_report = await orchestrator.execute_parallel_generation()
    
    # Return completed report
    return final_report

# Usage
report = await generate_marketmind_report("AAPL", "user123")
```

## Performance Optimization
- **Parallel Processing**: All 6 sections execute concurrently
- **RAG Caching**: Context prepared once, shared across sections
- **Progressive Loading**: Sections display as completed
- **Memory Management**: Efficient context sharing and cleanup
- **Error Recovery**: Graceful degradation with fallback options

## Quality Standards
- **Institutional Grade**: Professional formatting and analysis depth
- **Data Accuracy**: Multi-source validation and reconciliation
- **Source Attribution**: Complete citation and transparency
- **Real-time Updates**: Live progress tracking and ETA calculation
- **Comprehensive Coverage**: 25-30 pages of detailed analysis

Execute this master orchestrator to generate complete MarketMind Pro reports with enhanced Kiro integration.