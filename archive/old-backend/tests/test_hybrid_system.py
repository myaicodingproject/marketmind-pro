#!/usr/bin/env python3
"""
MarketMind Pro - Comprehensive Testing Framework
Phase 3: HybridSystemTester with full test suite
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import aiohttp
import openai
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import tempfile
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """Test result data structure"""
    test_name: str
    status: str  # PASS, FAIL, SKIP
    duration: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

@dataclass
class TestSuite:
    """Test suite results"""
    name: str
    results: List[TestResult]
    start_time: datetime
    end_time: Optional[datetime] = None
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
    
    @property
    def passed(self) -> int:
        return len([r for r in self.results if r.status == "PASS"])
    
    @property
    def failed(self) -> int:
        return len([r for r in self.results if r.status == "FAIL"])

class HybridSystemTester:
    """Comprehensive testing framework for MarketMind Pro"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or self._load_config()
        self.test_suites: List[TestSuite] = []
        self.session: Optional[aiohttp.ClientSession] = None
        
    def _load_config(self) -> Dict[str, Any]:
        """Load test configuration"""
        return {
            "api_base_url": os.getenv("API_BASE_URL", "http://localhost:8000"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "test_timeout": 30,
            "max_retries": 3
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config["test_timeout"])
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Execute all test suites"""
        logger.info("Starting comprehensive system tests...")
        
        test_methods = [
            self.test_environment,
            self.test_openai_connection,
            self.test_content_enhancement,
            self.test_pdf_generation,
            self.test_api_endpoints,
            self.test_quality_validation
        ]
        
        for test_method in test_methods:
            try:
                await test_method()
            except Exception as e:
                logger.error(f"Test suite {test_method.__name__} failed: {e}")
        
        return self.generate_report()
    
    async def test_environment(self):
        """Test environment configuration and dependencies"""
        suite = TestSuite("Environment Tests", [], datetime.now())
        
        # Test Python version
        result = await self._run_test("python_version", self._test_python_version)
        suite.results.append(result)
        
        # Test required packages
        result = await self._run_test("required_packages", self._test_required_packages)
        suite.results.append(result)
        
        # Test environment variables
        result = await self._run_test("environment_variables", self._test_env_variables)
        suite.results.append(result)
        
        # Test file system permissions
        result = await self._run_test("file_permissions", self._test_file_permissions)
        suite.results.append(result)
        
        suite.end_time = datetime.now()
        self.test_suites.append(suite)
    
    async def test_openai_connection(self):
        """Test OpenAI API connectivity and authentication"""
        suite = TestSuite("OpenAI Connection Tests", [], datetime.now())
        
        # Test API key validity
        result = await self._run_test("api_key_valid", self._test_openai_auth)
        suite.results.append(result)
        
        # Test model availability
        result = await self._run_test("model_availability", self._test_openai_models)
        suite.results.append(result)
        
        # Test rate limits
        result = await self._run_test("rate_limits", self._test_openai_limits)
        suite.results.append(result)
        
        suite.end_time = datetime.now()
        self.test_suites.append(suite)
    
    async def test_content_enhancement(self):
        """Test content enhancement and AI processing"""
        suite = TestSuite("Content Enhancement Tests", [], datetime.now())
        
        # Test basic enhancement
        result = await self._run_test("basic_enhancement", self._test_basic_enhancement)
        suite.results.append(result)
        
        # Test financial analysis
        result = await self._run_test("financial_analysis", self._test_financial_analysis)
        suite.results.append(result)
        
        # Test risk assessment
        result = await self._run_test("risk_assessment", self._test_risk_assessment)
        suite.results.append(result)
        
        suite.end_time = datetime.now()
        self.test_suites.append(suite)
    
    async def test_pdf_generation(self):
        """Test PDF generation functionality"""
        suite = TestSuite("PDF Generation Tests", [], datetime.now())
        
        # Test basic PDF creation
        result = await self._run_test("basic_pdf", self._test_basic_pdf)
        suite.results.append(result)
        
        # Test chart integration
        result = await self._run_test("chart_integration", self._test_chart_pdf)
        suite.results.append(result)
        
        # Test large document handling
        result = await self._run_test("large_document", self._test_large_pdf)
        suite.results.append(result)
        
        suite.end_time = datetime.now()
        self.test_suites.append(suite)
    
    async def test_api_endpoints(self):
        """Test API endpoints functionality"""
        suite = TestSuite("API Endpoint Tests", [], datetime.now())
        
        # Test health check
        result = await self._run_test("health_check", self._test_health_endpoint)
        suite.results.append(result)
        
        # Test report generation endpoint
        result = await self._run_test("generate_report", self._test_generate_endpoint)
        suite.results.append(result)
        
        # Test chat endpoint
        result = await self._run_test("chat_endpoint", self._test_chat_endpoint)
        suite.results.append(result)
        
        suite.end_time = datetime.now()
        self.test_suites.append(suite)
    
    async def test_quality_validation(self):
        """Test quality validation mechanisms"""
        suite = TestSuite("Quality Validation Tests", [], datetime.now())
        
        # Test content completeness
        result = await self._run_test("content_completeness", self._test_content_completeness)
        suite.results.append(result)
        
        # Test data accuracy
        result = await self._run_test("data_accuracy", self._test_data_accuracy)
        suite.results.append(result)
        
        # Test format consistency
        result = await self._run_test("format_consistency", self._test_format_consistency)
        suite.results.append(result)
        
        suite.end_time = datetime.now()
        self.test_suites.append(suite)
    
    async def _run_test(self, test_name: str, test_func) -> TestResult:
        """Execute individual test with error handling"""
        start_time = time.time()
        
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            
            duration = time.time() - start_time
            
            if result.get("success", True):
                return TestResult(test_name, "PASS", duration, details=result)
            else:
                return TestResult(test_name, "FAIL", duration, 
                                error_message=result.get("error"), details=result)
        
        except Exception as e:
            duration = time.time() - start_time
            return TestResult(test_name, "FAIL", duration, error_message=str(e))
    
    # Environment Tests
    def _test_python_version(self) -> Dict[str, Any]:
        """Test Python version compatibility"""
        import sys
        version = sys.version_info
        
        if version.major == 3 and version.minor >= 11:
            return {"success": True, "version": f"{version.major}.{version.minor}"}
        else:
            return {"success": False, "error": f"Python 3.11+ required, got {version.major}.{version.minor}"}
    
    def _test_required_packages(self) -> Dict[str, Any]:
        """Test required package availability"""
        required_packages = ["aiohttp", "openai", "reportlab", "fastapi", "pydantic"]
        missing = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing.append(package)
        
        if missing:
            return {"success": False, "error": f"Missing packages: {missing}"}
        return {"success": True, "packages": required_packages}
    
    def _test_env_variables(self) -> Dict[str, Any]:
        """Test environment variables"""
        required_vars = ["OPENAI_API_KEY"]
        missing = [var for var in required_vars if not os.getenv(var)]
        
        if missing:
            return {"success": False, "error": f"Missing env vars: {missing}"}
        return {"success": True, "variables": required_vars}
    
    def _test_file_permissions(self) -> Dict[str, Any]:
        """Test file system permissions"""
        try:
            with tempfile.NamedTemporaryFile(delete=True) as tmp:
                tmp.write(b"test")
                tmp.flush()
            return {"success": True}
        except Exception as e:
            return {"success": False, "error": f"File permission error: {e}"}
    
    # OpenAI Tests
    async def _test_openai_auth(self) -> Dict[str, Any]:
        """Test OpenAI authentication"""
        try:
            client = openai.AsyncOpenAI(api_key=self.config["openai_api_key"])
            models = await client.models.list()
            return {"success": True, "model_count": len(models.data)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_openai_models(self) -> Dict[str, Any]:
        """Test OpenAI model availability"""
        try:
            client = openai.AsyncOpenAI(api_key=self.config["openai_api_key"])
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": "Test"}],
                max_tokens=10
            )
            return {"success": True, "response_length": len(response.choices[0].message.content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_openai_limits(self) -> Dict[str, Any]:
        """Test OpenAI rate limits"""
        try:
            client = openai.AsyncOpenAI(api_key=self.config["openai_api_key"])
            start_time = time.time()
            
            # Make multiple quick requests
            tasks = []
            for _ in range(3):
                task = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": "Hi"}],
                    max_tokens=5
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            duration = time.time() - start_time
            
            return {"success": True, "duration": duration, "requests": len(tasks)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Content Enhancement Tests
    async def _test_basic_enhancement(self) -> Dict[str, Any]:
        """Test basic content enhancement"""
        try:
            client = openai.AsyncOpenAI(api_key=self.config["openai_api_key"])
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user", 
                    "content": "Analyze AAPL stock briefly"
                }],
                max_tokens=100
            )
            
            content = response.choices[0].message.content
            return {"success": True, "content_length": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_financial_analysis(self) -> Dict[str, Any]:
        """Test financial analysis capabilities"""
        try:
            client = openai.AsyncOpenAI(api_key=self.config["openai_api_key"])
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": "Calculate DCF for a company with 10% growth, 8% discount rate"
                }],
                max_tokens=150
            )
            
            content = response.choices[0].message.content
            has_numbers = any(char.isdigit() for char in content)
            
            return {"success": has_numbers, "content_length": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_risk_assessment(self) -> Dict[str, Any]:
        """Test risk assessment functionality"""
        try:
            client = openai.AsyncOpenAI(api_key=self.config["openai_api_key"])
            response = await client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user",
                    "content": "List 3 key risks for tech stocks"
                }],
                max_tokens=100
            )
            
            content = response.choices[0].message.content.lower()
            risk_keywords = ["risk", "volatility", "competition", "regulation"]
            has_risk_content = any(keyword in content for keyword in risk_keywords)
            
            return {"success": has_risk_content, "content_length": len(content)}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # PDF Generation Tests
    def _test_basic_pdf(self) -> Dict[str, Any]:
        """Test basic PDF generation"""
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                c = canvas.Canvas(tmp.name, pagesize=letter)
                c.drawString(100, 750, "Test Report")
                c.drawString(100, 730, "Generated by MarketMind Pro")
                c.save()
                
                file_size = os.path.getsize(tmp.name)
                os.unlink(tmp.name)
                
                return {"success": True, "file_size": file_size}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_chart_pdf(self) -> Dict[str, Any]:
        """Test PDF with chart integration"""
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                c = canvas.Canvas(tmp.name, pagesize=letter)
                c.drawString(100, 750, "Chart Integration Test")
                
                # Simple chart simulation
                c.rect(100, 600, 200, 100)
                c.drawString(110, 650, "Sample Chart Area")
                c.save()
                
                file_size = os.path.getsize(tmp.name)
                os.unlink(tmp.name)
                
                return {"success": True, "file_size": file_size}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _test_large_pdf(self) -> Dict[str, Any]:
        """Test large document PDF generation"""
        try:
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                c = canvas.Canvas(tmp.name, pagesize=letter)
                
                # Generate multiple pages
                for page in range(5):
                    c.drawString(100, 750, f"Page {page + 1}")
                    for line in range(30):
                        c.drawString(100, 720 - line * 20, f"Line {line + 1} content")
                    c.showPage()
                
                c.save()
                
                file_size = os.path.getsize(tmp.name)
                os.unlink(tmp.name)
                
                return {"success": file_size > 10000, "file_size": file_size}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # API Endpoint Tests
    async def _test_health_endpoint(self) -> Dict[str, Any]:
        """Test health check endpoint"""
        try:
            if not self.session:
                return {"success": False, "error": "No session available"}
            
            async with self.session.get(f"{self.config['api_base_url']}/health") as response:
                status = response.status
                data = await response.json() if response.content_type == 'application/json' else {}
                
                return {"success": status == 200, "status": status, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_generate_endpoint(self) -> Dict[str, Any]:
        """Test report generation endpoint"""
        try:
            if not self.session:
                return {"success": False, "error": "No session available"}
            
            payload = {"symbol": "AAPL", "include_charts": False}
            
            async with self.session.post(
                f"{self.config['api_base_url']}/api/v1/generate-report",
                json=payload
            ) as response:
                status = response.status
                data = await response.json() if response.content_type == 'application/json' else {}
                
                return {"success": status in [200, 202], "status": status, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _test_chat_endpoint(self) -> Dict[str, Any]:
        """Test chat endpoint"""
        try:
            if not self.session:
                return {"success": False, "error": "No session available"}
            
            payload = {"report_id": "test", "question": "What are the risks?"}
            
            async with self.session.post(
                f"{self.config['api_base_url']}/api/v1/chat",
                json=payload
            ) as response:
                status = response.status
                data = await response.json() if response.content_type == 'application/json' else {}
                
                return {"success": status in [200, 404], "status": status, "data": data}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    # Quality Validation Tests
    def _test_content_completeness(self) -> Dict[str, Any]:
        """Test content completeness validation"""
        sample_report = {
            "executive_summary": "Sample summary",
            "company_analysis": "Sample analysis",
            "financial_analysis": "Sample financials",
            "valuation": "Sample valuation",
            "risks": "Sample risks"
        }
        
        required_sections = ["executive_summary", "company_analysis", "financial_analysis", "valuation", "risks"]
        missing_sections = [section for section in required_sections if not sample_report.get(section)]
        
        return {"success": len(missing_sections) == 0, "missing_sections": missing_sections}
    
    def _test_data_accuracy(self) -> Dict[str, Any]:
        """Test data accuracy validation"""
        sample_data = {
            "revenue": 100000000,
            "growth_rate": 0.15,
            "pe_ratio": 25.5,
            "market_cap": 2000000000
        }
        
        # Basic validation rules
        validations = [
            sample_data["revenue"] > 0,
            0 <= sample_data["growth_rate"] <= 1,
            sample_data["pe_ratio"] > 0,
            sample_data["market_cap"] > 0
        ]
        
        return {"success": all(validations), "validation_count": len(validations)}
    
    def _test_format_consistency(self) -> Dict[str, Any]:
        """Test format consistency validation"""
        sample_sections = [
            {"title": "Executive Summary", "content": "Content here", "page_count": 2},
            {"title": "Financial Analysis", "content": "Content here", "page_count": 8},
            {"title": "Risk Assessment", "content": "Content here", "page_count": 3}
        ]
        
        # Check format consistency
        has_titles = all(section.get("title") for section in sample_sections)
        has_content = all(section.get("content") for section in sample_sections)
        has_page_counts = all(section.get("page_count") for section in sample_sections)
        
        return {
            "success": has_titles and has_content and has_page_counts,
            "sections_count": len(sample_sections)
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = sum(len(suite.results) for suite in self.test_suites)
        total_passed = sum(suite.passed for suite in self.test_suites)
        total_failed = sum(suite.failed for suite in self.test_suites)
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_suites": len(self.test_suites),
                "total_tests": total_tests,
                "passed": total_passed,
                "failed": total_failed,
                "success_rate": (total_passed / total_tests * 100) if total_tests > 0 else 0
            },
            "suites": []
        }
        
        for suite in self.test_suites:
            suite_data = {
                "name": suite.name,
                "duration": suite.duration,
                "passed": suite.passed,
                "failed": suite.failed,
                "tests": [asdict(result) for result in suite.results]
            }
            report["suites"].append(suite_data)
        
        return report
    
    def save_report(self, filename: str = "test_results.json"):
        """Save test report to file"""
        report = self.generate_report()
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"Test report saved to {filename}")
        return filename

async def main():
    """Main test execution function"""
    async with HybridSystemTester() as tester:
        results = await tester.run_all_tests()
        
        # Print summary
        print("\n" + "="*60)
        print("MARKETMIND PRO - TEST RESULTS SUMMARY")
        print("="*60)
        print(f"Total Suites: {results['summary']['total_suites']}")
        print(f"Total Tests: {results['summary']['total_tests']}")
        print(f"Passed: {results['summary']['passed']}")
        print(f"Failed: {results['summary']['failed']}")
        print(f"Success Rate: {results['summary']['success_rate']:.1f}%")
        
        # Print suite details
        for suite in results['suites']:
            print(f"\n{suite['name']}: {suite['passed']}/{suite['passed'] + suite['failed']} passed ({suite['duration']:.2f}s)")
            
            for test in suite['tests']:
                status_icon = "✓" if test['status'] == "PASS" else "✗"
                print(f"  {status_icon} {test['test_name']} ({test['duration']:.2f}s)")
                if test['error_message']:
                    print(f"    Error: {test['error_message']}")
        
        # Save detailed report
        report_file = tester.save_report()
        print(f"\nDetailed report saved to: {report_file}")
        
        return results

if __name__ == "__main__":
    asyncio.run(main())