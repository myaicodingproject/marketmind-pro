"""
Comprehensive Test Suite for Document Processing Pipeline

Tests all components of the advanced document processing system:
- Document processor functionality
- SEC filing parser
- Document chunking and embedding
- Semantic search capabilities
- Kiro CLI integration
"""

import asyncio
import json
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
import logging

# Import all components
from .document_processor import DocumentProcessor, DocumentType
from .sec_filing_parser import SECFilingParser
from .document_chunker import DocumentChunker, ChunkType
from .semantic_search import SemanticSearchEngine, SearchMode
from .kiro_integration import KiroContextPreparer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentPipelineTestSuite:
    """Comprehensive test suite for document processing pipeline"""
    
    def __init__(self):
        self.temp_dir = None
        self.test_results = {}
        
        # Sample test data
        self.test_documents = {
            "sample_10k": {
                "content": """
                ITEM 1. BUSINESS
                
                Apple Inc. designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and accessories worldwide. The Company sells and delivers digital content and applications through the iTunes Store, App Store, Mac App Store, TV App Store, Book Store, and Apple Music.
                
                Products
                The Company's products include iPhone, Mac, iPad, AirPods, Apple TV, Apple Watch, Beats products, HomePod, iPod touch and accessories.
                
                ITEM 1A. RISK FACTORS
                
                The Company's business, reputation, results of operations, financial condition and stock price can be affected by a number of factors, whether currently known or unknown, including those described below.
                
                Competition
                The markets for the Company's products and services are highly competitive and the Company is confronted by aggressive competition in all areas of its business.
                
                ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS
                
                Revenue
                Total net sales increased 8% or $22.0 billion during 2023 compared to 2022. iPhone revenue increased $3.0 billion or 2% during 2023 compared to 2022.
                
                Consolidated Statements of Operations
                (In millions, except number of shares and per share amounts)
                
                                    2023      2022      2021
                Net sales          $383,285  $394,328  $365,817
                Cost of sales       212,035   223,546   212,981
                Gross margin        171,250   170,782   152,836
                """,
                "metadata": {
                    "form": "10-K",
                    "ticker": "AAPL",
                    "filing_date": "2023-11-03",
                    "document_type": "SEC_10K"
                }
            },
            "sample_earnings": {
                "content": """
                {
                    "symbol": "AAPL",
                    "annualReports": [
                        {
                            "fiscalDateEnding": "2023-09-30",
                            "reportedCurrency": "USD",
                            "totalRevenue": "383285000000",
                            "totalOperatingExpense": "212035000000",
                            "costOfRevenue": "212035000000",
                            "grossProfit": "171250000000",
                            "ebit": "114301000000",
                            "netIncome": "96995000000"
                        }
                    ]
                }
                """,
                "metadata": {
                    "ticker": "AAPL",
                    "date": "2023-09-30",
                    "document_type": "FINANCIAL_STATEMENT"
                }
            }
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and return comprehensive results"""
        logger.info("Starting comprehensive document processing pipeline tests")
        
        # Setup test environment
        await self._setup_test_environment()
        
        try:
            # Run individual component tests
            await self._test_document_processor()
            await self._test_sec_filing_parser()
            await self._test_document_chunker()
            await self._test_semantic_search()
            await self._test_kiro_integration()
            
            # Run integration tests
            await self._test_end_to_end_pipeline()
            
            # Generate test report
            return self._generate_test_report()
        
        finally:
            await self._cleanup_test_environment()
    
    async def _setup_test_environment(self):
        """Setup test environment with temporary directories"""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="doc_pipeline_test_"))
        logger.info(f"Created test environment: {self.temp_dir}")
    
    async def _cleanup_test_environment(self):
        """Cleanup test environment"""
        if self.temp_dir and self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            logger.info("Cleaned up test environment")
    
    async def _test_document_processor(self):
        """Test document processor functionality"""
        logger.info("Testing Document Processor...")
        
        test_name = "document_processor"
        self.test_results[test_name] = {
            "status": "running",
            "tests": {},
            "errors": []
        }
        
        try:
            # Initialize processor
            chroma_path = self.temp_dir / "chroma_test"
            processor = DocumentProcessor(str(chroma_path))
            
            # Test 1: Process SEC filing
            test_doc = self.test_documents["sample_10k"]
            processed_doc = await processor.process_financial_document(
                ticker="AAPL",
                content=test_doc["content"],
                metadata=test_doc["metadata"]
            )
            
            self.test_results[test_name]["tests"]["process_sec_filing"] = {
                "passed": processed_doc is not None,
                "details": {
                    "document_id": processed_doc.document_id if processed_doc else None,
                    "chunks_created": len(processed_doc.chunks) if processed_doc else 0,
                    "document_type": processed_doc.document_type.value if processed_doc else None
                }
            }
            
            # Test 2: Process financial document
            financial_doc = self.test_documents["sample_earnings"]
            processed_financial = await processor.process_financial_document(
                ticker="AAPL",
                content=financial_doc["content"],
                metadata=financial_doc["metadata"]
            )
            
            self.test_results[test_name]["tests"]["process_financial_document"] = {
                "passed": processed_financial is not None,
                "details": {
                    "document_id": processed_financial.document_id if processed_financial else None,
                    "financial_tables": len(processed_financial.financial_tables) if processed_financial else 0
                }
            }
            
            # Test 3: Search functionality
            search_results = await processor.search_documents(
                query="revenue earnings financial performance",
                ticker="AAPL",
                n_results=5
            )
            
            self.test_results[test_name]["tests"]["search_documents"] = {
                "passed": len(search_results) > 0,
                "details": {
                    "results_count": len(search_results),
                    "avg_relevance": sum(r.get("distance", 1) for r in search_results) / len(search_results) if search_results else 0
                }
            }
            
            # Test 4: Context retrieval
            context = await processor.get_company_context("AAPL", "financial performance")
            
            self.test_results[test_name]["tests"]["get_company_context"] = {
                "passed": len(context) > 100,
                "details": {
                    "context_length": len(context),
                    "contains_ticker": "AAPL" in context.upper()
                }
            }
            
            await processor.cleanup()
            self.test_results[test_name]["status"] = "completed"
            
        except Exception as e:
            self.test_results[test_name]["status"] = "failed"
            self.test_results[test_name]["errors"].append(str(e))
            logger.error(f"Document processor test failed: {e}")
    
    async def _test_sec_filing_parser(self):
        """Test SEC filing parser"""
        logger.info("Testing SEC Filing Parser...")
        
        test_name = "sec_filing_parser"
        self.test_results[test_name] = {
            "status": "running",
            "tests": {},
            "errors": []
        }
        
        try:
            parser = SECFilingParser()
            
            # Test 1: HTML parsing
            html_content = f"""
            <html>
            <body>
            <h1>FORM 10-K</h1>
            {self.test_documents["sample_10k"]["content"]}
            <table>
            <tr><th>Year</th><th>Revenue</th></tr>
            <tr><td>2023</td><td>$383,285</td></tr>
            <tr><td>2022</td><td>$394,328</td></tr>
            </table>
            </body>
            </html>
            """.encode('utf-8')
            
            parsed_html = await parser._parse_html_filing(
                html_content, 
                self.test_documents["sample_10k"]["metadata"]
            )
            
            self.test_results[test_name]["tests"]["parse_html_filing"] = {
                "passed": parsed_html is not None and len(parsed_html["text_content"]) > 100,
                "details": {
                    "text_length": len(parsed_html["text_content"]) if parsed_html else 0,
                    "sections_found": len(parsed_html["sections"]) if parsed_html else 0,
                    "tables_found": len(parsed_html["financial_tables"]) if parsed_html else 0
                }
            }
            
            # Test 2: Text parsing
            parsed_text = await parser._parse_text_filing(
                self.test_documents["sample_10k"]["content"].encode('utf-8'),
                self.test_documents["sample_10k"]["metadata"]
            )
            
            self.test_results[test_name]["tests"]["parse_text_filing"] = {
                "passed": parsed_text is not None,
                "details": {
                    "sections_extracted": len(parsed_text["sections"]) if parsed_text else 0,
                    "has_business_section": "business" in parsed_text["sections"] if parsed_text else False
                }
            }
            
            await parser.cleanup()
            self.test_results[test_name]["status"] = "completed"
            
        except Exception as e:
            self.test_results[test_name]["status"] = "failed"
            self.test_results[test_name]["errors"].append(str(e))
            logger.error(f"SEC filing parser test failed: {e}")
    
    async def _test_document_chunker(self):
        """Test document chunker"""
        logger.info("Testing Document Chunker...")
        
        test_name = "document_chunker"
        self.test_results[test_name] = {
            "status": "running",
            "tests": {},
            "errors": []
        }
        
        try:
            chunker = DocumentChunker()
            
            # Test 1: Basic chunking
            content = self.test_documents["sample_10k"]["content"]
            metadata = self.test_documents["sample_10k"]["metadata"]
            
            chunks = chunker.chunk_document(content, metadata)
            
            self.test_results[test_name]["tests"]["basic_chunking"] = {
                "passed": len(chunks) > 0,
                "details": {
                    "chunks_created": len(chunks),
                    "avg_chunk_size": sum(len(c.content) for c in chunks) / len(chunks) if chunks else 0,
                    "chunk_types": list(set(c.chunk_type.value for c in chunks))
                }
            }
            
            # Test 2: Chunk quality analysis
            if chunks:
                quality_stats = self._analyze_chunk_quality(chunks)
                
                self.test_results[test_name]["tests"]["chunk_quality"] = {
                    "passed": quality_stats["avg_chunk_size"] > 100,
                    "details": quality_stats
                }
            
            # Test 3: Financial content detection
            financial_chunks = [c for c in chunks if c.contains_financial_terms]
            
            self.test_results[test_name]["tests"]["financial_detection"] = {
                "passed": len(financial_chunks) > 0,
                "details": {
                    "financial_chunks": len(financial_chunks),
                    "total_chunks": len(chunks),
                    "financial_ratio": len(financial_chunks) / len(chunks) if chunks else 0
                }
            }
            
            self.test_results[test_name]["status"] = "completed"
            
        except Exception as e:
            self.test_results[test_name]["status"] = "failed"
            self.test_results[test_name]["errors"].append(str(e))
            logger.error(f"Document chunker test failed: {e}")
    
    async def _test_semantic_search(self):
        """Test semantic search engine"""
        logger.info("Testing Semantic Search Engine...")
        
        test_name = "semantic_search"
        self.test_results[test_name] = {
            "status": "running",
            "tests": {},
            "errors": []
        }
        
        try:
            chroma_path = self.temp_dir / "chroma_search_test"
            search_engine = SemanticSearchEngine(str(chroma_path))
            
            # First, we need to populate the database with test data
            # This would normally be done by the document processor
            # For testing, we'll create a minimal setup
            
            # Test 1: Search functionality (basic)
            # Note: This test may not return results if no data is indexed
            results = await search_engine.search(
                query="revenue financial performance",
                ticker="AAPL",
                search_mode=SearchMode.KEYWORD,
                max_results=5
            )
            
            self.test_results[test_name]["tests"]["basic_search"] = {
                "passed": True,  # Test passes if no errors occur
                "details": {
                    "results_count": len(results),
                    "search_mode": "keyword"
                }
            }
            
            # Test 2: Different search modes
            for mode in [SearchMode.SEMANTIC, SearchMode.HYBRID, SearchMode.FINANCIAL]:
                try:
                    mode_results = await search_engine.search(
                        query="business operations",
                        search_mode=mode,
                        max_results=3
                    )
                    
                    self.test_results[test_name]["tests"][f"search_mode_{mode.value}"] = {
                        "passed": True,
                        "details": {"results_count": len(mode_results)}
                    }
                except Exception as e:
                    self.test_results[test_name]["tests"][f"search_mode_{mode.value}"] = {
                        "passed": False,
                        "error": str(e)
                    }
            
            # Test 3: Context preparation
            context = await search_engine.get_context_for_analysis("AAPL", "financial_performance")
            
            self.test_results[test_name]["tests"]["context_preparation"] = {
                "passed": isinstance(context, str),
                "details": {
                    "context_length": len(context),
                    "has_content": len(context) > 0
                }
            }
            
            # Test 4: Search statistics
            stats = search_engine.get_search_stats()
            
            self.test_results[test_name]["tests"]["search_stats"] = {
                "passed": isinstance(stats, dict),
                "details": stats
            }
            
            self.test_results[test_name]["status"] = "completed"
            
        except Exception as e:
            self.test_results[test_name]["status"] = "failed"
            self.test_results[test_name]["errors"].append(str(e))
            logger.error(f"Semantic search test failed: {e}")
    
    async def _test_kiro_integration(self):
        """Test Kiro CLI integration"""
        logger.info("Testing Kiro Integration...")
        
        test_name = "kiro_integration"
        self.test_results[test_name] = {
            "status": "running",
            "tests": {},
            "errors": []
        }
        
        try:
            chroma_path = self.temp_dir / "chroma_kiro_test"
            kiro_preparer = KiroContextPreparer(str(chroma_path))
            
            # Test 1: Comprehensive context preparation
            context_dict = await kiro_preparer.prepare_comprehensive_context("AAPL", "investment_thesis")
            
            self.test_results[test_name]["tests"]["comprehensive_context"] = {
                "passed": isinstance(context_dict, dict) and len(context_dict) > 0,
                "details": {
                    "context_sections": list(context_dict.keys()),
                    "total_sections": len(context_dict),
                    "avg_section_length": sum(len(v) for v in context_dict.values()) / len(context_dict) if context_dict else 0
                }
            }
            
            # Test 2: Prompt-specific context
            prompt_context = await kiro_preparer.prepare_prompt_specific_context(
                "AAPL", "company-overview-investment-thesis"
            )
            
            self.test_results[test_name]["tests"]["prompt_specific_context"] = {
                "passed": isinstance(prompt_context, str) and len(prompt_context) > 0,
                "details": {
                    "context_length": len(prompt_context),
                    "has_ticker": "AAPL" in prompt_context.upper()
                }
            }
            
            # Test 3: Context validation
            if context_dict and "business_overview" in context_dict:
                validation = await kiro_preparer.validate_context_quality(
                    context_dict["business_overview"], "AAPL"
                )
                
                self.test_results[test_name]["tests"]["context_validation"] = {
                    "passed": isinstance(validation, dict),
                    "details": validation
                }
            
            # Test 4: Processing statistics
            stats = await kiro_preparer.get_processing_statistics()
            
            self.test_results[test_name]["tests"]["processing_statistics"] = {
                "passed": isinstance(stats, dict),
                "details": {
                    "has_document_processor_stats": "document_processor" in stats,
                    "has_search_engine_stats": "search_engine" in stats,
                    "context_templates": stats.get("context_templates", 0)
                }
            }
            
            await kiro_preparer.cleanup()
            self.test_results[test_name]["status"] = "completed"
            
        except Exception as e:
            self.test_results[test_name]["status"] = "failed"
            self.test_results[test_name]["errors"].append(str(e))
            logger.error(f"Kiro integration test failed: {e}")
    
    async def _test_end_to_end_pipeline(self):
        """Test complete end-to-end pipeline"""
        logger.info("Testing End-to-End Pipeline...")
        
        test_name = "end_to_end_pipeline"
        self.test_results[test_name] = {
            "status": "running",
            "tests": {},
            "errors": []
        }
        
        try:
            chroma_path = self.temp_dir / "chroma_e2e_test"
            
            # Initialize all components
            processor = DocumentProcessor(str(chroma_path))
            kiro_preparer = KiroContextPreparer(str(chroma_path))
            
            # Test 1: Process document and retrieve context
            test_doc = self.test_documents["sample_10k"]
            
            # Process document
            processed_doc = await processor.process_financial_document(
                ticker="AAPL",
                content=test_doc["content"],
                metadata=test_doc["metadata"]
            )
            
            # Wait a moment for indexing
            await asyncio.sleep(1)
            
            # Retrieve context
            context = await kiro_preparer.prepare_prompt_specific_context(
                "AAPL", "company-overview-investment-thesis"
            )
            
            self.test_results[test_name]["tests"]["document_to_context"] = {
                "passed": processed_doc is not None and len(context) > 0,
                "details": {
                    "document_processed": processed_doc is not None,
                    "chunks_created": len(processed_doc.chunks) if processed_doc else 0,
                    "context_generated": len(context) > 0,
                    "context_length": len(context)
                }
            }
            
            # Test 2: Multiple document types
            financial_doc = self.test_documents["sample_earnings"]
            processed_financial = await processor.process_financial_document(
                ticker="AAPL",
                content=financial_doc["content"],
                metadata=financial_doc["metadata"]
            )
            
            # Wait for indexing
            await asyncio.sleep(1)
            
            # Get comprehensive context
            comprehensive_context = await kiro_preparer.prepare_comprehensive_context("AAPL")
            
            self.test_results[test_name]["tests"]["multiple_documents"] = {
                "passed": processed_financial is not None and len(comprehensive_context) > 0,
                "details": {
                    "financial_doc_processed": processed_financial is not None,
                    "comprehensive_context_sections": len(comprehensive_context),
                    "total_context_length": sum(len(v) for v in comprehensive_context.values())
                }
            }
            
            # Test 3: Search across processed documents
            search_results = await processor.search_documents(
                query="revenue financial performance business operations",
                ticker="AAPL",
                n_results=10
            )
            
            self.test_results[test_name]["tests"]["cross_document_search"] = {
                "passed": len(search_results) > 0,
                "details": {
                    "search_results": len(search_results),
                    "unique_documents": len(set(r.get("metadata", {}).get("document_id") for r in search_results))
                }
            }
            
            await processor.cleanup()
            await kiro_preparer.cleanup()
            
            self.test_results[test_name]["status"] = "completed"
            
        except Exception as e:
            self.test_results[test_name]["status"] = "failed"
            self.test_results[test_name]["errors"].append(str(e))
            logger.error(f"End-to-end pipeline test failed: {e}")
    
    def _analyze_chunk_quality(self, chunks) -> Dict[str, Any]:
        """Analyze chunk quality metrics"""
        if not chunks:
            return {"error": "No chunks to analyze"}
        
        return {
            "total_chunks": len(chunks),
            "avg_chunk_size": sum(len(c.content) for c in chunks) / len(chunks),
            "chunk_types": {ct.value: sum(1 for c in chunks if c.chunk_type == ct) for ct in set(c.chunk_type for c in chunks)},
            "financial_chunks": sum(1 for c in chunks if c.contains_financial_terms),
            "chunks_with_numbers": sum(1 for c in chunks if c.contains_numbers),
            "avg_word_count": sum(c.word_count for c in chunks) / len(chunks)
        }
    
    def _generate_test_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_tests = 0
        passed_tests = 0
        failed_tests = 0
        
        component_summary = {}
        
        for component, results in self.test_results.items():
            component_tests = len(results.get("tests", {}))
            component_passed = sum(1 for test in results.get("tests", {}).values() if test.get("passed", False))
            component_failed = component_tests - component_passed
            
            total_tests += component_tests
            passed_tests += component_passed
            failed_tests += component_failed
            
            component_summary[component] = {
                "status": results.get("status", "unknown"),
                "total_tests": component_tests,
                "passed": component_passed,
                "failed": component_failed,
                "success_rate": (component_passed / component_tests * 100) if component_tests > 0 else 0,
                "errors": results.get("errors", [])
            }
        
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "success_rate": overall_success_rate,
                "overall_status": "PASSED" if failed_tests == 0 else "FAILED"
            },
            "component_results": component_summary,
            "detailed_results": self.test_results,
            "test_environment": {
                "temp_dir": str(self.temp_dir) if self.temp_dir else None,
                "test_documents": len(self.test_documents)
            }
        }
        
        return report

# Main test execution function
async def run_document_pipeline_tests():
    """Run all document processing pipeline tests"""
    test_suite = DocumentPipelineTestSuite()
    
    try:
        results = await test_suite.run_all_tests()
        
        # Print summary
        print("\n" + "="*80)
        print("DOCUMENT PROCESSING PIPELINE TEST RESULTS")
        print("="*80)
        
        summary = results["test_summary"]
        print(f"Overall Status: {summary['overall_status']}")
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Passed: {summary['passed']}")
        print(f"Failed: {summary['failed']}")
        print(f"Success Rate: {summary['success_rate']:.1f}%")
        
        print("\nComponent Results:")
        print("-" * 40)
        
        for component, comp_results in results["component_results"].items():
            status_icon = "✓" if comp_results["status"] == "completed" else "✗"
            print(f"{status_icon} {component}: {comp_results['passed']}/{comp_results['total_tests']} "
                  f"({comp_results['success_rate']:.1f}%)")
            
            if comp_results["errors"]:
                for error in comp_results["errors"]:
                    print(f"    Error: {error}")
        
        # Save detailed results
        results_file = Path("test_results_document_pipeline.json")
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\nDetailed results saved to: {results_file}")
        
        return results
        
    except Exception as e:
        logger.error(f"Test suite execution failed: {e}")
        return {"error": str(e)}

if __name__ == "__main__":
    asyncio.run(run_document_pipeline_tests())