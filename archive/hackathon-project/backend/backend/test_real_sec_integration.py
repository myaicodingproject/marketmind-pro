#!/usr/bin/env python3
"""
Real SEC Filing Integration Test

This script tests the complete document processing pipeline with real SEC filings.
It demonstrates the full workflow from document fetching to Kiro context preparation.
"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Import pipeline components
from app.services.document_processor import DocumentProcessor
from app.services.sec_filing_parser import SECFilingParser
from app.services.semantic_search import SemanticSearchEngine, SearchMode
from app.services.kiro_integration import KiroContextPreparer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealFilingIntegrationTest:
    """Integration test with real SEC filings"""
    
    def __init__(self, chroma_path: str = "./test_chroma_db"):
        self.chroma_path = Path(chroma_path)
        self.results = {}
        
        # Test companies with known recent filings
        self.test_companies = {
            "AAPL": {
                "name": "Apple Inc.",
                "recent_10k": "https://www.sec.gov/Archives/edgar/data/320193/000032019323000077/aapl-20230930.htm",
                "filing_date": "2023-11-03"
            },
            "MSFT": {
                "name": "Microsoft Corporation", 
                "recent_10k": "https://www.sec.gov/Archives/edgar/data/789019/000156459023003038/msft-10k_20230630.htm",
                "filing_date": "2023-07-27"
            }
        }
    
    async def run_integration_test(self) -> Dict[str, Any]:
        """Run complete integration test"""
        logger.info("Starting real SEC filing integration test")
        
        try:
            # Initialize components
            await self._initialize_components()
            
            # Test each company
            for ticker, company_info in self.test_companies.items():
                logger.info(f"Testing {ticker} - {company_info['name']}")
                await self._test_company_pipeline(ticker, company_info)
            
            # Test cross-company search
            await self._test_cross_company_search()
            
            # Test Kiro integration
            await self._test_kiro_context_preparation()
            
            # Generate final report
            return self._generate_integration_report()
        
        except Exception as e:
            logger.error(f"Integration test failed: {e}")
            return {"error": str(e), "results": self.results}
        
        finally:
            await self._cleanup()
    
    async def _initialize_components(self):
        """Initialize all pipeline components"""
        logger.info("Initializing pipeline components...")
        
        self.document_processor = DocumentProcessor(str(self.chroma_path))
        self.sec_parser = SECFilingParser()
        self.search_engine = SemanticSearchEngine(str(self.chroma_path))
        self.kiro_preparer = KiroContextPreparer(str(self.chroma_path))
        
        logger.info("Components initialized successfully")
    
    async def _test_company_pipeline(self, ticker: str, company_info: Dict[str, Any]):
        """Test complete pipeline for a single company"""
        company_results = {
            "ticker": ticker,
            "name": company_info["name"],
            "tests": {},
            "errors": []
        }
        
        try:
            # Test 1: Parse SEC filing
            logger.info(f"Parsing SEC filing for {ticker}")
            
            filing_metadata = {
                "form": "10-K",
                "ticker": ticker,
                "filing_date": company_info["filing_date"],
                "document_type": "SEC_10K"
            }
            
            parsed_filing = await self.sec_parser.parse_sec_filing(
                company_info["recent_10k"],
                filing_metadata
            )
            
            company_results["tests"]["sec_parsing"] = {
                "success": parsed_filing is not None,
                "sections_found": len(parsed_filing.get("sections", {})),
                "tables_found": len(parsed_filing.get("financial_tables", [])),
                "text_length": len(parsed_filing.get("text_content", ""))
            }
            
            # Test 2: Process through document processor
            logger.info(f"Processing document for {ticker}")
            
            processed_doc = await self.document_processor.process_sec_filing(
                ticker=ticker,
                filing_url=company_info["recent_10k"],
                filing_metadata=filing_metadata
            )
            
            company_results["tests"]["document_processing"] = {
                "success": processed_doc is not None,
                "document_id": processed_doc.document_id if processed_doc else None,
                "chunks_created": len(processed_doc.chunks) if processed_doc else 0,
                "financial_tables": len(processed_doc.financial_tables) if processed_doc else 0
            }
            
            # Wait for indexing
            await asyncio.sleep(2)
            
            # Test 3: Search functionality
            logger.info(f"Testing search for {ticker}")
            
            search_results = await self.search_engine.search(
                query="business operations revenue financial performance",
                ticker=ticker,
                search_mode=SearchMode.FINANCIAL,
                max_results=10
            )
            
            company_results["tests"]["search"] = {
                "success": len(search_results) > 0,
                "results_count": len(search_results),
                "avg_relevance": sum(r.score for r in search_results) / len(search_results) if search_results else 0
            }
            
            # Test 4: Context preparation
            logger.info(f"Preparing context for {ticker}")
            
            context = await self.kiro_preparer.prepare_comprehensive_context(
                ticker=ticker,
                analysis_type="investment_thesis"
            )
            
            company_results["tests"]["context_preparation"] = {
                "success": len(context) > 0,
                "context_sections": len(context),
                "total_context_length": sum(len(v) for v in context.values()),
                "sections": list(context.keys())
            }
            
            # Test 5: Prompt-specific context
            prompt_context = await self.kiro_preparer.prepare_prompt_specific_context(
                ticker=ticker,
                prompt_type="company-overview-investment-thesis"
            )
            
            company_results["tests"]["prompt_context"] = {
                "success": len(prompt_context) > 0,
                "context_length": len(prompt_context),
                "contains_ticker": ticker in prompt_context.upper()
            }
            
        except Exception as e:
            logger.error(f"Error testing {ticker}: {e}")
            company_results["errors"].append(str(e))
        
        self.results[ticker] = company_results
    
    async def _test_cross_company_search(self):
        """Test search across multiple companies"""
        logger.info("Testing cross-company search")
        
        cross_search_results = {
            "tests": {},
            "errors": []
        }
        
        try:
            # Test 1: General financial search
            results = await self.search_engine.search(
                query="revenue growth profitability technology",
                search_mode=SearchMode.FINANCIAL,
                max_results=20
            )
            
            # Analyze results by ticker
            ticker_distribution = {}
            for result in results:
                ticker = result.ticker
                ticker_distribution[ticker] = ticker_distribution.get(ticker, 0) + 1
            
            cross_search_results["tests"]["general_search"] = {
                "success": len(results) > 0,
                "total_results": len(results),
                "companies_found": len(ticker_distribution),
                "ticker_distribution": ticker_distribution
            }
            
            # Test 2: Comparative search
            comparative_results = await self.search_engine.search(
                query="competitive position market share industry leadership",
                search_mode=SearchMode.HYBRID,
                max_results=15
            )
            
            cross_search_results["tests"]["comparative_search"] = {
                "success": len(comparative_results) > 0,
                "results_count": len(comparative_results),
                "unique_companies": len(set(r.ticker for r in comparative_results))
            }
            
        except Exception as e:
            logger.error(f"Cross-company search error: {e}")
            cross_search_results["errors"].append(str(e))
        
        self.results["cross_company_search"] = cross_search_results
    
    async def _test_kiro_context_preparation(self):
        """Test Kiro-specific context preparation"""
        logger.info("Testing Kiro context preparation")
        
        kiro_results = {
            "tests": {},
            "errors": []
        }
        
        try:
            # Test different analysis types
            analysis_types = [
                "company_overview",
                "financial_analysis", 
                "risk_assessment",
                "valuation_analysis"
            ]
            
            for analysis_type in analysis_types:
                for ticker in self.test_companies.keys():
                    try:
                        context = await self.kiro_preparer.prepare_comprehensive_context(
                            ticker=ticker,
                            analysis_type=analysis_type
                        )
                        
                        # Validate context quality
                        validation = await self.kiro_preparer.validate_context_quality(
                            context.get("business_overview", ""),
                            ticker
                        )
                        
                        test_key = f"{analysis_type}_{ticker}"
                        kiro_results["tests"][test_key] = {
                            "success": len(context) > 0,
                            "context_sections": len(context),
                            "quality_score": validation.get("quality_score", 0),
                            "recommendations": validation.get("recommendations", [])
                        }
                    
                    except Exception as e:
                        logger.error(f"Kiro context error for {ticker} {analysis_type}: {e}")
                        kiro_results["errors"].append(f"{ticker} {analysis_type}: {str(e)}")
            
            # Test prompt-specific contexts
            prompt_types = [
                "company-overview-investment-thesis",
                "financial-analysis-key-metrics",
                "risk-assessment-summary",
                "valuation-analysis-price-target"
            ]
            
            for prompt_type in prompt_types:
                for ticker in list(self.test_companies.keys())[:1]:  # Test with one ticker
                    try:
                        prompt_context = await self.kiro_preparer.prepare_prompt_specific_context(
                            ticker=ticker,
                            prompt_type=prompt_type
                        )
                        
                        test_key = f"prompt_{prompt_type}_{ticker}"
                        kiro_results["tests"][test_key] = {
                            "success": len(prompt_context) > 0,
                            "context_length": len(prompt_context),
                            "formatted_properly": "##" in prompt_context and "===" in prompt_context
                        }
                    
                    except Exception as e:
                        logger.error(f"Prompt context error for {ticker} {prompt_type}: {e}")
                        kiro_results["errors"].append(f"{ticker} {prompt_type}: {str(e)}")
        
        except Exception as e:
            logger.error(f"Kiro integration test error: {e}")
            kiro_results["errors"].append(str(e))
        
        self.results["kiro_integration"] = kiro_results
    
    def _generate_integration_report(self) -> Dict[str, Any]:
        """Generate comprehensive integration test report"""
        report = {
            "test_summary": {
                "timestamp": datetime.now().isoformat(),
                "companies_tested": len(self.test_companies),
                "total_tests": 0,
                "passed_tests": 0,
                "failed_tests": 0,
                "success_rate": 0.0
            },
            "component_performance": {},
            "detailed_results": self.results,
            "recommendations": []
        }
        
        # Calculate test statistics
        total_tests = 0
        passed_tests = 0
        
        for component, results in self.results.items():
            if "tests" in results:
                component_tests = len(results["tests"])
                component_passed = sum(1 for test in results["tests"].values() 
                                     if test.get("success", False))
                
                total_tests += component_tests
                passed_tests += component_passed
                
                report["component_performance"][component] = {
                    "total_tests": component_tests,
                    "passed": component_passed,
                    "success_rate": (component_passed / component_tests * 100) if component_tests > 0 else 0,
                    "errors": len(results.get("errors", []))
                }
        
        report["test_summary"]["total_tests"] = total_tests
        report["test_summary"]["passed_tests"] = passed_tests
        report["test_summary"]["failed_tests"] = total_tests - passed_tests
        report["test_summary"]["success_rate"] = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        # Generate recommendations
        if report["test_summary"]["success_rate"] < 90:
            report["recommendations"].append("Review failed tests and improve error handling")
        
        if any(comp["errors"] > 0 for comp in report["component_performance"].values()):
            report["recommendations"].append("Address component-specific errors")
        
        # Check context quality
        kiro_tests = self.results.get("kiro_integration", {}).get("tests", {})
        low_quality_contexts = [test for test, result in kiro_tests.items() 
                               if result.get("quality_score", 1) < 0.7]
        
        if low_quality_contexts:
            report["recommendations"].append(f"Improve context quality for: {', '.join(low_quality_contexts)}")
        
        return report
    
    async def _cleanup(self):
        """Cleanup resources"""
        try:
            if hasattr(self, 'document_processor'):
                await self.document_processor.cleanup()
            if hasattr(self, 'sec_parser'):
                await self.sec_parser.cleanup()
            if hasattr(self, 'kiro_preparer'):
                await self.kiro_preparer.cleanup()
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

async def main():
    """Main test execution"""
    print("🚀 Starting Real SEC Filing Integration Test")
    print("=" * 60)
    
    # Initialize test
    test = RealFilingIntegrationTest()
    
    try:
        # Run integration test
        results = await test.run_integration_test()
        
        # Print summary
        if "error" in results:
            print(f"❌ Test failed: {results['error']}")
            return
        
        summary = results["test_summary"]
        print(f"\n📊 Test Results Summary")
        print(f"Companies Tested: {summary['companies_tested']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed_tests']}")
        print(f"Failed: {summary['failed_tests']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        # Component performance
        print(f"\n🔧 Component Performance:")
        for component, perf in results["component_performance"].items():
            status = "✅" if perf["success_rate"] == 100 else "⚠️" if perf["success_rate"] > 80 else "❌"
            print(f"{status} {component}: {perf['passed']}/{perf['total_tests']} ({perf['success_rate']:.1f}%)")
            
            if perf["errors"] > 0:
                print(f"   Errors: {perf['errors']}")
        
        # Recommendations
        if results["recommendations"]:
            print(f"\n💡 Recommendations:")
            for rec in results["recommendations"]:
                print(f"• {rec}")
        
        # Save detailed results
        results_file = Path("integration_test_results.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed results saved to: {results_file}")
        
        # Overall status
        overall_status = "PASSED" if summary["success_rate"] >= 80 else "FAILED"
        print(f"\n🎯 Overall Status: {overall_status}")
        
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())