"""
Puppeteer PDF Service - Superior institutional-quality PDF generation
Replaces WeasyPrint with Puppeteer for better typography and performance
"""

import asyncio
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import time
from datetime import datetime

class PuppeteerPDFService:
    """High-performance PDF generation using Puppeteer"""
    
    def __init__(self):
        self.node_script_path = Path(__file__).parent / "puppeteer_generator.js"
        self.template_dir = Path(__file__).parent.parent.parent / "templates"
        self.static_dir = Path(__file__).parent.parent.parent / "static"
        
        # Ensure directories exist
        self.template_dir.mkdir(parents=True, exist_ok=True)
        self.static_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance settings
        self.pdf_options = {
            "format": "A4",
            "margin": {
                "top": "1in",
                "right": "0.75in", 
                "bottom": "1.25in",
                "left": "0.75in"
            },
            "printBackground": True,
            "preferCSSPageSize": True,
            "displayHeaderFooter": True,
            "headerTemplate": """
                <div style="font-size: 9px; color: #666; width: 100%; text-align: center; margin-top: 0.25in;">
                    MarketMind Pro - Institutional Research
                </div>
            """,
            "footerTemplate": """
                <div style="font-size: 9px; color: #666; width: 100%; text-align: center; margin-bottom: 0.25in;">
                    Page <span class="pageNumber"></span> of <span class="totalPages"></span>
                </div>
            """
        }
    
    async def generate_pdf(self, report_data: Dict[str, Any], output_path: str) -> str:
        """Generate PDF using Puppeteer with optimized performance"""
        start_time = time.time()
        
        try:
            # Create Node.js script if it doesn't exist
            await self._ensure_node_script()
            
            # Prepare data for Node.js script
            temp_data = {
                "report_data": report_data,
                "output_path": output_path,
                "pdf_options": self.pdf_options,
                "template_path": str(self.template_dir / "stock_report.html"),
                "css_path": str(self.static_dir / "css" / "report-styles.css")
            }
            
            # Write temporary data file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_file:
                json.dump(temp_data, temp_file, indent=2)
                temp_data_path = temp_file.name
            
            try:
                # Execute Puppeteer script
                result = await self._run_puppeteer_script(temp_data_path)
                
                if not os.path.exists(output_path):
                    raise Exception(f"PDF generation failed: {result}")
                
                # Verify PDF quality
                file_size = os.path.getsize(output_path)
                if file_size < 10000:  # Less than 10KB indicates failure
                    raise Exception("Generated PDF is too small, likely corrupted")
                
                generation_time = time.time() - start_time
                print(f"✅ PDF generated in {generation_time:.2f}s, size: {file_size:,} bytes")
                
                return output_path
                
            finally:
                # Cleanup
                if os.path.exists(temp_data_path):
                    os.unlink(temp_data_path)
                    
        except Exception as e:
            raise Exception(f"Puppeteer PDF generation failed: {str(e)}")
    
    async def _ensure_node_script(self):
        """Ensure Puppeteer Node.js script exists"""
        if not self.node_script_path.exists():
            await self._create_node_script()
    
    async def _create_node_script(self):
        """Create optimized Puppeteer Node.js script"""
        script_content = '''
const puppeteer = require('puppeteer');
const fs = require('fs').promises;
const path = require('path');

async function generatePDF() {
    const dataPath = process.argv[2];
    
    try {
        // Read configuration
        const configData = JSON.parse(await fs.readFile(dataPath, 'utf8'));
        const { report_data, output_path, pdf_options, template_path, css_path } = configData;
        
        // Launch browser with optimized settings
        const browser = await puppeteer.launch({
            headless: 'new',
            args: [
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--no-first-run',
                '--no-zygote',
                '--single-process'
            ]
        });
        
        const page = await browser.newPage();
        
        // Set viewport for consistent rendering
        await page.setViewport({ width: 1200, height: 1600 });
        
        // Read and process HTML template
        let htmlContent = await fs.readFile(template_path, 'utf8');
        
        // Simple template replacement (basic Jinja2-like)
        htmlContent = htmlContent
            .replace(/{{ ticker }}/g, report_data.ticker || 'UNKNOWN')
            .replace(/{{ title }}/g, report_data.title || 'Stock Analysis Report')
            .replace(/{{ generated_date }}/g, report_data.generated_date || new Date().toLocaleDateString());
        
        // Process sections
        let sectionsHtml = '';
        if (report_data.sections) {
            for (const [sectionKey, section] of Object.entries(report_data.sections)) {
                sectionsHtml += `
                    <div class="page-break"></div>
                    <div class="report-section">
                        <div class="section-header">
                            <h2 class="section-title">${section.title || sectionKey.replace('_', ' ').toUpperCase()}</h2>
                            <div class="section-divider"></div>
                        </div>
                        <div class="section-content">
                            ${formatContent(section.content || '')}
                        </div>
                    </div>
                `;
            }
        }
        
        htmlContent = htmlContent.replace('<!-- SECTIONS_PLACEHOLDER -->', sectionsHtml);
        
        // Read CSS
        const cssContent = await fs.readFile(css_path, 'utf8');
        
        // Inject CSS into HTML
        htmlContent = htmlContent.replace('</head>', `<style>${cssContent}</style></head>`);
        
        // Set content and generate PDF
        await page.setContent(htmlContent, { waitUntil: 'networkidle0' });
        
        // Generate PDF with options
        await page.pdf({
            path: output_path,
            ...pdf_options
        });
        
        await browser.close();
        
        console.log(`PDF generated successfully: ${output_path}`);
        
    } catch (error) {
        console.error('PDF generation error:', error);
        process.exit(1);
    }
}

function formatContent(content) {
    if (!content) return '';
    
    // Basic markdown-like formatting
    return content
        .replace(/\\*\\*(.*?)\\*\\*/g, '<strong>$1</strong>')
        .replace(/\\*(.*?)\\*/g, '<em>$1</em>')
        .replace(/^• (.+)$/gm, '<li>$1</li>')
        .replace(/(<li>.*<\\/li>)/gs, '<ul>$1</ul>')
        .replace(/\\n\\n/g, '</p><p>')
        .replace(/^(.+)$/gm, '<p>$1</p>')
        .replace(/<p><ul>/g, '<ul>')
        .replace(/<\\/ul><\\/p>/g, '</ul>');
}

generatePDF();
'''
        
        with open(self.node_script_path, 'w') as f:
            f.write(script_content)
    
    async def _run_puppeteer_script(self, data_path: str) -> str:
        """Execute Puppeteer Node.js script"""
        try:
            # Install puppeteer if needed
            await self._ensure_puppeteer_installed()
            
            # Run the script
            process = await asyncio.create_subprocess_exec(
                'node', str(self.node_script_path), data_path,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise Exception(f"Node.js script failed: {error_msg}")
            
            return stdout.decode()
            
        except Exception as e:
            raise Exception(f"Failed to run Puppeteer script: {str(e)}")
    
    async def _ensure_puppeteer_installed(self):
        """Ensure Puppeteer is installed"""
        try:
            # Check if puppeteer is available
            process = await asyncio.create_subprocess_exec(
                'npm', 'list', 'puppeteer',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(Path(__file__).parent.parent.parent)
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                print("Installing Puppeteer...")
                # Install puppeteer
                install_process = await asyncio.create_subprocess_exec(
                    'npm', 'install', 'puppeteer',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    cwd=str(Path(__file__).parent.parent.parent)
                )
                
                await install_process.communicate()
                
                if install_process.returncode != 0:
                    raise Exception("Failed to install Puppeteer")
                
                print("✅ Puppeteer installed successfully")
                
        except Exception as e:
            raise Exception(f"Puppeteer installation check failed: {str(e)}")


# Integration function
async def generate_puppeteer_pdf(ticker: str, report_data: Dict[str, Any], output_path: str = None) -> str:
    """
    Generate institutional-quality PDF using Puppeteer
    
    Args:
        ticker: Stock ticker symbol
        report_data: Report data structure
        output_path: Output file path (optional)
    
    Returns:
        Path to generated PDF file
    """
    if output_path is None:
        timestamp = int(time.time())
        output_path = f"/mnt/c/kiro/MarketMind_Report_{ticker}_Puppeteer_{timestamp}.pdf"
    
    service = PuppeteerPDFService()
    return await service.generate_pdf(report_data, output_path)