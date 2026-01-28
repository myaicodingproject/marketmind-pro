#!/usr/bin/env python3
"""
Hybrid PDF System Debugging Framework
Comprehensive debugging tools for OpenAI + PDF enhancement system
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime
from typing import Dict, Any, List
from dotenv import load_dotenv

# Load environment
load_dotenv()

class HybridSystemDebugger:
    """Comprehensive debugging for hybrid PDF system"""
    
    def __init__(self):
        self.debug_log = []
        self.setup_logging()
    
    def setup_logging(self):
        """Setup detailed logging"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('hybrid_debug.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('HybridDebugger')
    
    def log_debug(self, component: str, message: str, data: Any = None):
        """Log debug information"""
        timestamp = datetime.now().isoformat()
        debug_entry = {
            'timestamp': timestamp,
            'component': component,
            'message': message,
            'data': data
        }
        self.debug_log.append(debug_entry)
        self.logger.debug(f"[{component}] {message}")
        if data:
            self.logger.debug(f"[{component}] Data: {json.dumps(data, indent=2, default=str)}")
    
    async def debug_openai_connection(self):
        """Debug OpenAI API connection"""
        print("\n🔍 DEBUGGING OPENAI CONNECTION")
        print("=" * 50)
        
        try:
            from openai import AsyncOpenAI
            
            # Check environment variables
            api_key = os.getenv("OPENAI_API_KEY")
            model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
            
            self.log_debug("OpenAI", "Environment check", {
                "api_key_present": bool(api_key),
                "api_key_length": len(api_key) if api_key else 0,
                "model": model
            })
            
            if not api_key:
                print("❌ OPENAI_API_KEY not found in environment")
                return False
            
            # Test connection
            client = AsyncOpenAI(api_key=api_key)
            
            start_time = time.time()
            response = await client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "Debug test"}],
                max_tokens=5
            )
            response_time = time.time() - start_time
            
            self.log_debug("OpenAI", "Connection test", {
                "response_time": response_time,
                "model_used": response.model,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "response": response.choices[0].message.content
            })
            
            print(f"✅ OpenAI connection successful")
            print(f"   Response time: {response_time:.2f}s")
            print(f"   Model: {response.model}")
            print(f"   Tokens used: {response.usage.total_tokens if response.usage else 'N/A'}")
            
            return True
            
        except Exception as e:
            self.log_debug("OpenAI", "Connection failed", {"error": str(e)})
            print(f"❌ OpenAI connection failed: {e}")
            return False
    
    async def debug_content_enhancement(self, test_content: str = None):
        """Debug content enhancement process"""
        print("\n🔍 DEBUGGING CONTENT ENHANCEMENT")
        print("=" * 50)
        
        if not test_content:
            test_content = """
            Searching for symbols matching: "generate_report"
            + 7: + 8: Alphabet Inc. (GOOGL) stands as the dominant force
            > # Executive Summary
            • Revenue: $339.7 billion
            git/objects/04: IO error
            """
        
        try:
            from openai import AsyncOpenAI
            
            client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            self.log_debug("ContentEnhancement", "Input content", {
                "content_length": len(test_content),
                "content_preview": test_content[:200],
                "issues_detected": {
                    "debug_messages": "Searching for symbols" in test_content,
                    "line_numbers": "+ 7:" in test_content,
                    "system_errors": "git/objects" in test_content,
                    "markdown_headers": "> #" in test_content
                }
            })
            
            # Test enhancement
            start_time = time.time()
            response = await client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {
                        "role": "system",
                        "content": """Debug mode: Clean financial report content.
                        Remove: debug messages, line numbers, system errors
                        Fix: markdown headers, formatting
                        Preserve: all financial data
                        Return: cleaned content only"""
                    },
                    {
                        "role": "user",
                        "content": f"Clean this content:\n{test_content}"
                    }
                ],
                max_tokens=300
            )
            enhancement_time = time.time() - start_time
            
            enhanced_content = response.choices[0].message.content
            
            # Analyze enhancement results
            issues_fixed = {
                "debug_messages_removed": "Searching for symbols" not in enhanced_content,
                "line_numbers_removed": "+ 7:" not in enhanced_content,
                "system_errors_removed": "git/objects" not in enhanced_content,
                "markdown_headers_fixed": "> #" not in enhanced_content,
                "content_preserved": "Revenue" in enhanced_content and "billion" in enhanced_content
            }
            
            self.log_debug("ContentEnhancement", "Enhancement results", {
                "enhancement_time": enhancement_time,
                "tokens_used": response.usage.total_tokens if response.usage else None,
                "issues_fixed": issues_fixed,
                "enhanced_content_length": len(enhanced_content),
                "enhanced_content": enhanced_content
            })
            
            print(f"✅ Content enhancement completed")
            print(f"   Enhancement time: {enhancement_time:.2f}s")
            print(f"   Issues fixed: {sum(issues_fixed.values())}/{len(issues_fixed)}")
            
            for issue, fixed in issues_fixed.items():
                status = "✅" if fixed else "❌"
                print(f"   {status} {issue.replace('_', ' ').title()}")
            
            print(f"\n📝 Enhanced content preview:")
            print(f"   {enhanced_content[:200]}...")
            
            return issues_fixed
            
        except Exception as e:
            self.log_debug("ContentEnhancement", "Enhancement failed", {"error": str(e)})
            print(f"❌ Content enhancement failed: {e}")
            return {}
    
    async def debug_pdf_generation(self, ticker: str = "GOOGL"):
        """Debug PDF generation process"""
        print(f"\n🔍 DEBUGGING PDF GENERATION ({ticker})")
        print("=" * 50)
        
        try:
            import requests
            from professional_pdf_generator import generate_professional_pdf
            
            # Step 1: Get report data
            self.log_debug("PDFGeneration", "Fetching report data", {"ticker": ticker})
            
            response = requests.get(f"http://localhost:8000/api/v1/reports/prod_report_{ticker}_1769350746")
            if response.status_code != 200:
                print(f"❌ Could not fetch report data: {response.status_code}")
                return False
            
            report_data = response.json()
            sections_count = len(report_data.get('sections', {}))
            
            self.log_debug("PDFGeneration", "Report data retrieved", {
                "sections_count": sections_count,
                "data_size": len(json.dumps(report_data)),
                "sections": list(report_data.get('sections', {}).keys())
            })
            
            print(f"✅ Report data retrieved: {sections_count} sections")
            
            # Step 2: Test PDF generation
            start_time = time.time()
            output_path = f"/mnt/c/kiro/{ticker}_Debug_Test.pdf"
            
            pdf_path = generate_professional_pdf(ticker, report_data, output_path)
            generation_time = time.time() - start_time
            
            if os.path.exists(pdf_path):
                file_size = os.path.getsize(pdf_path)
                
                # Analyze PDF
                import PyPDF2
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    first_page = pdf_reader.pages[0].extract_text()
                    
                    pdf_analysis = {
                        "total_pages": total_pages,
                        "file_size": file_size,
                        "first_page_length": len(first_page),
                        "has_content": len(first_page) > 100,
                        "debug_artifacts": {
                            "searching_symbols": "Searching for symbols" in first_page,
                            "line_numbers": any(f"+ {i}:" in first_page for i in range(1, 20)),
                            "git_errors": "git/objects" in first_page
                        }
                    }
                
                self.log_debug("PDFGeneration", "PDF generated successfully", {
                    "generation_time": generation_time,
                    "pdf_path": pdf_path,
                    "analysis": pdf_analysis
                })
                
                print(f"✅ PDF generated successfully")
                print(f"   Generation time: {generation_time:.2f}s")
                print(f"   File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
                print(f"   Pages: {total_pages}")
                
                # Check for issues
                issues_found = sum(pdf_analysis["debug_artifacts"].values())
                if issues_found == 0:
                    print(f"   ✅ No debug artifacts found")
                else:
                    print(f"   ⚠️  {issues_found} debug artifacts found:")
                    for artifact, present in pdf_analysis["debug_artifacts"].items():
                        if present:
                            print(f"      ❌ {artifact.replace('_', ' ').title()}")
                
                return True
            else:
                print(f"❌ PDF not generated")
                return False
                
        except Exception as e:
            self.log_debug("PDFGeneration", "PDF generation failed", {"error": str(e)})
            print(f"❌ PDF generation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def debug_system_integration(self):
        """Debug system integration"""
        print(f"\n🔍 DEBUGGING SYSTEM INTEGRATION")
        print("=" * 50)
        
        try:
            import requests
            
            # Test backend health
            health_response = requests.get("http://localhost:8000/health", timeout=5)
            backend_healthy = health_response.status_code == 200
            
            self.log_debug("SystemIntegration", "Backend health check", {
                "status_code": health_response.status_code,
                "healthy": backend_healthy,
                "response": health_response.json() if backend_healthy else None
            })
            
            print(f"Backend health: {'✅' if backend_healthy else '❌'}")
            
            # Test API endpoints
            endpoints_to_test = [
                "/health",
                "/api/v1/reports/prod_report_GOOGL_1769350746"
            ]
            
            endpoint_results = {}
            for endpoint in endpoints_to_test:
                try:
                    response = requests.get(f"http://localhost:8000{endpoint}", timeout=10)
                    endpoint_results[endpoint] = {
                        "status_code": response.status_code,
                        "response_time": response.elapsed.total_seconds(),
                        "success": response.status_code == 200
                    }
                    print(f"   {endpoint}: {'✅' if response.status_code == 200 else '❌'} ({response.status_code})")
                except Exception as e:
                    endpoint_results[endpoint] = {"error": str(e), "success": False}
                    print(f"   {endpoint}: ❌ {e}")
            
            self.log_debug("SystemIntegration", "API endpoints test", endpoint_results)
            
            return all(result.get("success", False) for result in endpoint_results.values())
            
        except Exception as e:
            self.log_debug("SystemIntegration", "Integration test failed", {"error": str(e)})
            print(f"❌ System integration test failed: {e}")
            return False
    
    def save_debug_report(self):
        """Save comprehensive debug report"""
        debug_report = {
            "timestamp": datetime.now().isoformat(),
            "debug_log": self.debug_log,
            "environment": {
                "openai_api_key_present": bool(os.getenv("OPENAI_API_KEY")),
                "openai_model": os.getenv("OPENAI_MODEL"),
                "python_version": sys.version,
                "working_directory": os.getcwd()
            }
        }
        
        with open("hybrid_debug_report.json", "w") as f:
            json.dump(debug_report, f, indent=2, default=str)
        
        print(f"\n📋 Debug report saved: hybrid_debug_report.json")
        print(f"📋 Debug log saved: hybrid_debug.log")
    
    async def run_full_debug(self):
        """Run complete debugging suite"""
        print("🔍 HYBRID SYSTEM COMPREHENSIVE DEBUG")
        print("=" * 60)
        
        results = {}
        
        # Test 1: OpenAI Connection
        results["openai_connection"] = await self.debug_openai_connection()
        
        # Test 2: Content Enhancement
        results["content_enhancement"] = await self.debug_content_enhancement()
        
        # Test 3: PDF Generation
        results["pdf_generation"] = await self.debug_pdf_generation()
        
        # Test 4: System Integration
        results["system_integration"] = await self.debug_system_integration()
        
        # Summary
        print(f"\n🎯 DEBUG SUMMARY")
        print("=" * 30)
        
        for test_name, result in results.items():
            if isinstance(result, bool):
                status = "✅ PASSED" if result else "❌ FAILED"
            elif isinstance(result, dict):
                status = f"✅ {sum(result.values())}/{len(result)} PASSED"
            else:
                status = "⚠️  PARTIAL"
            
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        # Save debug report
        self.save_debug_report()
        
        return results

async def main():
    """Run debugging framework"""
    debugger = HybridSystemDebugger()
    results = await debugger.run_full_debug()
    
    # Overall assessment
    overall_success = all(
        result if isinstance(result, bool) else all(result.values()) if isinstance(result, dict) else False
        for result in results.values()
    )
    
    if overall_success:
        print(f"\n🏆 ALL SYSTEMS OPERATIONAL - READY FOR PRODUCTION")
    else:
        print(f"\n⚠️  ISSUES DETECTED - CHECK DEBUG LOGS")
    
    return overall_success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
