"""
Enhanced MarketMind Pro PDF Generation API
Production-ready PDF generation service with hybrid rendering engines
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import asyncio
import uuid
from datetime import datetime
import os
import json
import sys
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from hybrid_pdf_service import ProductionPDFGenerator
    PDF_SERVICE_AVAILABLE = True
    logger = logging.getLogger(__name__)
    logger.info("Enhanced hybrid PDF service loaded successfully")
except ImportError as e:
    print(f"Import error: {e}")
    PDF_SERVICE_AVAILABLE = False
    
    # Fallback PDF generator
    class ProductionPDFGenerator:
        async def generate_report_pdf(self, report_data, output_path, options=None):
            return {
                'success': False,
                'output_path': None,
                'file_size': 0,
                'generation_time': 0,
                'method_used': 'fallback',
                'error': 'PDF service not available'
            }
        
        async def close(self):
            pass

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="MarketMind Pro Enhanced PDF Generator", 
    version="2.0.0",
    description="Professional PDF generation with hybrid rendering engines"
)

# In-memory storage for demo (use Redis in production)
generation_status = {}

# Global enhanced PDF service
pdf_generator = ProductionPDFGenerator()

class ReportRequest(BaseModel):
    symbol: str
    analysis_data: Dict[str, Any]
    report_type: str = "institutional"
    output_format: str = "pdf"
    include_charts: bool = True
    include_tables: bool = True

class GenerationStatus(BaseModel):
    job_id: str
    status: str  # pending, processing, completed, failed
    progress: int  # 0-100
    message: str
    file_path: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

@app.post("/api/v1/reports/{report_id}/pdf")
async def generate_report_pdf(report_id: str, request: ReportRequest, background_tasks: BackgroundTasks):
    """Generate PDF report using enhanced hybrid rendering system"""
    job_id = str(uuid.uuid4())
    
    # Initialize status
    generation_status[job_id] = GenerationStatus(
        job_id=job_id,
        status="pending",
        progress=0,
        message="Enhanced PDF generation queued",
        created_at=datetime.now()
    )
    
    # Start background generation with enhanced system
    background_tasks.add_task(generate_enhanced_pdf_background, job_id, report_id, request)
    
    return {
        "job_id": job_id, 
        "report_id": report_id, 
        "status": "queued", 
        "message": "Enhanced PDF generation started with hybrid rendering"
    }

async def generate_enhanced_pdf_background(job_id: str, report_id: str, request: ReportRequest):
    """Enhanced background task using hybrid PDF generation system"""
    try:
        # Update status
        generation_status[job_id].status = "processing"
        generation_status[job_id].progress = 10
        generation_status[job_id].message = "Initializing enhanced PDF generation system"
        
        # Create output directory
        output_dir = "generated_reports"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"report_{report_id}_{job_id}.pdf")
        
        # Progress updates
        generation_status[job_id].progress = 25
        generation_status[job_id].message = "Building professional report structure with enhanced styling"
        
        # Prepare enhanced report data
        report_data = {
            "title": f"{request.symbol} Financial Analysis Report",
            "subtitle": f"Comprehensive Investment Research & Market Analysis",
            "company_name": "MarketMind Pro",
            "date": datetime.now().strftime("%B %d, %Y"),
            "sections": []
        }
        
        # Process analysis data into enhanced sections
        if request.analysis_data:
            sections = _process_enhanced_analysis_data(request.analysis_data, request.symbol)
            report_data["sections"] = sections
        
        generation_status[job_id].progress = 50
        generation_status[job_id].message = "Generating enhanced HTML with professional charts and styling"
        
        # Enhanced PDF options for institutional quality
        pdf_options = {
            'format': 'A4',
            'printBackground': True,
            'preferCSSPageSize': True,
            'margin': {
                'top': '1in',
                'right': '0.75in',
                'bottom': '1in',
                'left': '0.75in'
            },
            'displayHeaderFooter': True,
            'headerTemplate': f'<div style="font-size:10px; width:100%; text-align:center; color:#666; padding:10px;">MarketMind Pro - {request.symbol} Professional Analysis Report</div>',
            'footerTemplate': '<div style="font-size:10px; width:100%; text-align:center; color:#666; padding:10px;"><span class="pageNumber"></span> of <span class="totalPages"></span></div>'
        }
        
        generation_status[job_id].progress = 75
        generation_status[job_id].message = "Converting to PDF with hybrid rendering system"
        
        # Generate PDF with enhanced hybrid system
        if PDF_SERVICE_AVAILABLE:
            try:
                result = await pdf_generator.generate_report_pdf(report_data, output_path, pdf_options)
                
                if result['success']:
                    generation_status[job_id].message = f"PDF generated successfully using {result['method_used']} engine"
                    generation_status[job_id].file_path = result['output_path']
                else:
                    generation_status[job_id].message = f"PDF generation failed: {result.get('error', 'Unknown error')}"
                    generation_status[job_id].status = "failed"
                    generation_status[job_id].completed_at = datetime.now()
                    return
                    
            except Exception as pdf_error:
                # Enhanced fallback with detailed error logging
                logger.error(f"Enhanced PDF generation failed: {pdf_error}")
                html_path = output_path.replace('.pdf', '.html')
                
                # Generate HTML fallback
                html_content = pdf_generator.html_generator.generate_html(report_data)
                with open(html_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                
                generation_status[job_id].file_path = html_path
                generation_status[job_id].message = f"PDF generation failed, professional HTML saved. Error: {str(pdf_error)}"
        else:
            # Fallback when service not available
            html_path = output_path.replace('.pdf', '.html')
            html_content = "<html><body><h1>PDF Service Not Available</h1><p>Please check system configuration.</p></body></html>"
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            generation_status[job_id].file_path = html_path
            generation_status[job_id].message = "Enhanced PDF service unavailable, basic HTML generated"
        
        generation_status[job_id].progress = 100
        generation_status[job_id].status = "completed"
        generation_status[job_id].completed_at = datetime.now()
        
        logger.info(f"Enhanced PDF generation completed for job {job_id}")
        
    except Exception as e:
        generation_status[job_id].status = "failed"
        generation_status[job_id].message = f"Enhanced PDF generation failed: {str(e)}"
        generation_status[job_id].completed_at = datetime.now()
        logger.error(f"Enhanced PDF generation error for job {job_id}: {e}")

def _process_enhanced_analysis_data(analysis_data: Dict[str, Any], symbol: str) -> List[Dict[str, Any]]:
    """Process analysis data into enhanced HTML sections with better formatting"""
    sections = []
    
    # Executive Summary with enhanced formatting
    if "executive_summary" in analysis_data:
        content = analysis_data["executive_summary"]
        if isinstance(content, str):
            # Add highlight boxes for key points
            if "recommendation" in content.lower():
                content = content.replace("Recommendation:", '<div class="highlight-box"><strong>Investment Recommendation:</strong>')
                content += "</div>"
        
        sections.append({
            "title": "Executive Summary",
            "content": content,
            "page": len(sections) + 1
        })
    
    # Enhanced Financial Metrics with better visualization
    if "financial_metrics" in analysis_data:
        metrics = analysis_data["financial_metrics"]
        key_metrics = []
        
        if isinstance(metrics, dict):
            for key, value in metrics.items():
                if isinstance(value, (int, float)):
                    formatted_value = _format_financial_value(key, value)
                    key_metrics.append({
                        "label": key.replace("_", " ").title(),
                        "value": formatted_value
                    })
        
        sections.append({
            "title": "Key Financial Metrics",
            "key_metrics": key_metrics[:8],  # Limit to 8 metrics for clean layout
            "page": len(sections) + 1
        })
    
    # Market Analysis with enhanced content structure
    if "market_analysis" in analysis_data:
        content = analysis_data["market_analysis"]
        if isinstance(content, str) and len(content) > 500:
            # Split long content into subsections
            content = _add_subsection_headers(content)
        
        sections.append({
            "title": "Market Analysis & Industry Overview",
            "content": content,
            "page": len(sections) + 1
        })
    
    # Risk Assessment with warning boxes
    if "risk_assessment" in analysis_data:
        content = analysis_data["risk_assessment"]
        if isinstance(content, str):
            # Highlight risk factors
            content = content.replace("Risk:", '<div class="warning-box"><strong>Risk Factor:</strong>')
            content = content.replace("High risk", '<span style="color: #d32f2f; font-weight: bold;">High Risk</span>')
            content = content.replace("Low risk", '<span style="color: #388e3c; font-weight: bold;">Low Risk</span>')
        
        sections.append({
            "title": "Risk Assessment & Mitigation",
            "content": content,
            "page": len(sections) + 1
        })
    
    # Valuation Analysis with enhanced formatting
    if "valuation" in analysis_data:
        content = analysis_data["valuation"]
        if isinstance(content, str):
            # Highlight price targets and valuations
            content = content.replace("Price Target:", '<div class="success-box"><strong>Price Target:</strong>')
            content = content.replace("Fair Value:", '<div class="highlight-box"><strong>Fair Value:</strong>')
        
        sections.append({
            "title": "Valuation Analysis & Price Target",
            "content": content,
            "page": len(sections) + 1
        })
    
    # Add competitive analysis if available
    if "competitive_analysis" in analysis_data:
        sections.append({
            "title": "Competitive Landscape",
            "content": analysis_data["competitive_analysis"],
            "page": len(sections) + 1
        })
    
    return sections

def _format_financial_value(key: str, value: float) -> str:
    """Format financial values with appropriate units and styling"""
    key_lower = key.lower()
    
    if "revenue" in key_lower or "sales" in key_lower:
        if value >= 1e9:
            return f"${value/1e9:.2f}B"
        elif value >= 1e6:
            return f"${value/1e6:.2f}M"
        else:
            return f"${value:,.0f}"
    elif "price" in key_lower or "target" in key_lower:
        return f"${value:.2f}"
    elif "ratio" in key_lower or "multiple" in key_lower:
        return f"{value:.2f}x"
    elif "percent" in key_lower or "%" in key_lower:
        return f"{value:.1f}%"
    elif "margin" in key_lower:
        return f"{value:.1f}%"
    else:
        return f"{value:,.2f}"

def _add_subsection_headers(content: str) -> str:
    """Add subsection headers to long content for better readability"""
    # Simple heuristic to add structure
    sentences = content.split('. ')
    if len(sentences) > 5:
        # Add subsection after every 3-4 sentences
        structured_content = []
        for i, sentence in enumerate(sentences):
            structured_content.append(sentence)
            if i > 0 and (i + 1) % 4 == 0 and i < len(sentences) - 2:
                structured_content.append('</p><h3 class="subsection-title">Analysis Continued</h3><p>')
        return '. '.join(structured_content)
    return content

@app.post("/api/v1/generate-report")
async def generate_report(request: ReportRequest, background_tasks: BackgroundTasks):
    """Generate institutional PDF report"""
    job_id = str(uuid.uuid4())
    
    # Initialize status
    generation_status[job_id] = GenerationStatus(
        job_id=job_id,
        status="pending",
        progress=0,
        message="Report generation queued",
        created_at=datetime.now()
    )
    
    # Start background generation
    background_tasks.add_task(generate_report_background, job_id, request)
    
    return {"job_id": job_id, "status": "queued", "message": "Report generation started"}

@app.get("/api/v1/status/{job_id}")
async def get_generation_status(job_id: str):
    """Get report generation status"""
    if job_id not in generation_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return generation_status[job_id]

@app.get("/api/v1/download/{job_id}")
async def download_report(job_id: str):
    """Download generated report"""
    if job_id not in generation_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    status = generation_status[job_id]
    if status.status != "completed":
        raise HTTPException(status_code=400, detail="Report not ready")
    
    if not status.file_path or not os.path.exists(status.file_path):
        raise HTTPException(status_code=404, detail="Report file not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(
        status.file_path,
        media_type="application/pdf",
        filename=f"report_{job_id}.pdf"
    )

async def generate_report_background(job_id: str, request: ReportRequest):
    """Background task for report generation"""
    try:
        # Update status
        generation_status[job_id].status = "processing"
        generation_status[job_id].progress = 10
        generation_status[job_id].message = "Initializing report generation"
        
        # Create output directory
        output_dir = "generated_reports"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"report_{job_id}.pdf")
        
        # Progress updates
        generation_status[job_id].progress = 25
        generation_status[job_id].message = "Building report structure"
        
        # Generate report
        if request.report_type == "institutional":
            builder = InstitutionalReportBuilder(
                symbol=request.symbol,
                analysis_data=request.analysis_data,
                output_path=output_path
            )
            
            generation_status[job_id].progress = 50
            generation_status[job_id].message = "Generating charts and tables"
            
            # Simulate some processing time
            await asyncio.sleep(2)
            
            generation_status[job_id].progress = 75
            generation_status[job_id].message = "Finalizing PDF document"
            
            # Build the report
            final_path = builder.build_complete_report()
            
            generation_status[job_id].progress = 100
            generation_status[job_id].status = "completed"
            generation_status[job_id].message = "Report generated successfully"
            generation_status[job_id].file_path = final_path
            generation_status[job_id].completed_at = datetime.now()
            
        else:
            raise ValueError(f"Unsupported report type: {request.report_type}")
            
    except Exception as e:
        generation_status[job_id].status = "failed"
        generation_status[job_id].message = f"Generation failed: {str(e)}"
        generation_status[job_id].completed_at = datetime.now()

@app.post("/api/v1/quick-generate")
async def quick_generate_report(request: ReportRequest):
    """Synchronous report generation for smaller reports"""
    try:
        output_dir = "generated_reports"
        os.makedirs(output_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(output_dir, f"{request.symbol}_report_{timestamp}.pdf")
        
        if request.report_type == "institutional":
            builder = InstitutionalReportBuilder(
                symbol=request.symbol,
                analysis_data=request.analysis_data,
                output_path=output_path
            )
            final_path = builder.build_complete_report()
        else:
            # Simple report fallback
            pdf = MarketMindPDFGenerator(output_path)
            pdf.add_cover_page(
                title=f"Analysis Report - {request.symbol}",
                subtitle="Financial Analysis Summary",
                company_name="MarketMind Pro"
            )
            final_path = pdf.generate()
        
        return {
            "status": "completed",
            "file_path": final_path,
            "download_url": f"/api/v1/download-file?path={final_path}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")

@app.get("/api/v1/download-file")
async def download_file(path: str):
    """Direct file download"""
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    
    from fastapi.responses import FileResponse
    return FileResponse(path, media_type="application/pdf")

@app.get("/health")
async def health_check():
    """Enhanced health check endpoint with system status"""
    health_status = {
        "status": "healthy",
        "service": "MarketMind Pro Enhanced PDF Generator",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "capabilities": {
            "pdf_service_available": PDF_SERVICE_AVAILABLE,
            "hybrid_rendering": True,
            "chart_support": True,
            "professional_styling": True
        }
    }
    
    if PDF_SERVICE_AVAILABLE:
        try:
            # Test PDF service availability
            health_status["pdf_engines"] = {
                "puppeteer": pdf_generator.pdf_service.puppeteer_available,
                "weasyprint": pdf_generator.pdf_service.weasyprint_available
            }
        except Exception as e:
            health_status["pdf_engines"] = {"error": str(e)}
    
    return health_status

@app.get("/api/v1/system/status")
async def system_status():
    """Detailed system status for monitoring"""
    return {
        "service": "MarketMind Pro Enhanced PDF Generator",
        "version": "2.0.0",
        "status": "operational",
        "active_jobs": len([j for j in generation_status.values() if j.status == "processing"]),
        "completed_jobs": len([j for j in generation_status.values() if j.status == "completed"]),
        "failed_jobs": len([j for j in generation_status.values() if j.status == "failed"]),
        "total_jobs": len(generation_status),
        "pdf_service_available": PDF_SERVICE_AVAILABLE,
        "timestamp": datetime.now().isoformat()
    }

@app.on_event("shutdown")
async def shutdown_event():
    """Enhanced cleanup on shutdown"""
    logger.info("Shutting down Enhanced PDF Generator...")
    
    if PDF_SERVICE_AVAILABLE:
        try:
            await pdf_generator.close()
            logger.info("PDF generator closed successfully")
        except Exception as e:
            logger.error(f"Error closing PDF generator: {e}")
    
    logger.info("Enhanced PDF Generator shutdown complete")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)