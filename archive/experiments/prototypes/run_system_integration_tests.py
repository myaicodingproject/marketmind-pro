#!/usr/bin/env python3
"""
MarketMind Pro - Main System Integration Test Runner
Executes all system integration tests and generates comprehensive report
"""

import asyncio
import json
import logging
import time
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Import all test modules
from tests.e2e_report_generation_test import E2EReportTester
from tests.concurrent_user_simulation_test import ConcurrentUserTester
from tests.performance_benchmark_test import PerformanceBenchmarkTester
from tests.error_handling_validation_test import ErrorHandlingTester
from tests.mobile_responsiveness_test import MobileResponsivenessTester

class SystemIntegrationTestRunner:
    """Main system integration test runner"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
        # Test configuration
        self.config = {
            "base_url": "http://localhost:8000",
            "frontend_url": "http://localhost:3000",
            "test_timeout": 3600,  # 1 hour timeout
            "parallel_execution": True
        }
    
    async def run_all_tests(self) -> Dict[str, Any]:
        """Execute all system integration tests"""
        
        self.start_time = time.time()
        
        self.logger.info("="*80)
        self.logger.info("MARKETMIND PRO - SYSTEM INTEGRATION TEST SUITE")
        self.logger.info("="*80)
        self.logger.info(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info(f"Base URL: {self.config['base_url']}")
        self.logger.info(f"Frontend URL: {self.config['frontend_url']}")
        
        # Define test suite
        test_suite = [
            {
                "name": "End-to-End Report Generation",
                "tester_class": E2EReportTester,
                "method": "run_comprehensive_tests",
                "critical": True,
                "timeout": 1800  # 30 minutes
            },
            {
                "name": "Concurrent User Simulation",
                "tester_class": ConcurrentUserTester,
                "method": "run_concurrent_tests",
                "critical": True,
                "timeout": 900  # 15 minutes
            },
            {
                "name": "Performance Benchmarking",
                "tester_class": PerformanceBenchmarkTester,
                "method": "run_performance_benchmarks",
                "critical": True,
                "timeout": 600  # 10 minutes
            },
            {
                "name": "Error Handling Validation",
                "tester_class": ErrorHandlingTester,
                "method": "run_error_handling_tests",
                "critical": True,
                "timeout": 300  # 5 minutes
            },
            {
                "name": "Mobile Responsiveness",
                "tester_class": MobileResponsivenessTester,
                "method": "run_mobile_tests",
                "critical": False,
                "timeout": 300  # 5 minutes
            }
        ]
        
        # Execute tests
        if self.config["parallel_execution"]:
            await self._run_tests_parallel(test_suite)
        else:
            await self._run_tests_sequential(test_suite)
        
        self.end_time = time.time()
        
        # Generate comprehensive report
        final_report = await self._generate_final_report()
        
        return final_report
    
    async def _run_tests_sequential(self, test_suite: List[Dict[str, Any]]):
        """Run tests sequentially"""
        
        self.logger.info("Running tests sequentially...")
        
        for test_config in test_suite:
            await self._execute_single_test(test_config)
    
    async def _run_tests_parallel(self, test_suite: List[Dict[str, Any]]):
        """Run tests in parallel where possible"""
        
        self.logger.info("Running tests in parallel...")
        
        # Group tests by dependency
        critical_tests = [t for t in test_suite if t["critical"]]
        non_critical_tests = [t for t in test_suite if not t["critical"]]
        
        # Run critical tests first (some may need to run sequentially)
        for test_config in critical_tests:
            await self._execute_single_test(test_config)
        
        # Run non-critical tests in parallel
        if non_critical_tests:
            tasks = []
            for test_config in non_critical_tests:
                task = asyncio.create_task(self._execute_single_test(test_config))
                tasks.append(task)
            
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_single_test(self, test_config: Dict[str, Any]):
        """Execute a single test suite"""
        
        test_name = test_config["name"]
        self.logger.info(f"\n{'='*60}")
        self.logger.info(f"EXECUTING: {test_name}")
        self.logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Initialize tester
            if test_config["tester_class"] in [ConcurrentUserTester, PerformanceBenchmarkTester, ErrorHandlingTester]:
                tester = test_config["tester_class"](self.config["base_url"])
            elif test_config["tester_class"] == MobileResponsivenessTester:
                tester = test_config["tester_class"](self.config["frontend_url"])
            else:
                tester = test_config["tester_class"]()
            
            # Execute test with timeout
            test_method = getattr(tester, test_config["method"])
            
            try:
                result = await asyncio.wait_for(
                    test_method(),
                    timeout=test_config["timeout"]
                )
                
                execution_time = time.time() - start_time
                
                # Analyze results
                success = self._analyze_test_results(test_name, result)
                
                self.test_results[test_name] = {
                    "status": "PASSED" if success else "FAILED",
                    "execution_time": execution_time,
                    "result_count": len(result) if isinstance(result, list) else 1,
                    "results": result,
                    "critical": test_config["critical"]
                }
                
                status_icon = "✅" if success else "❌"
                self.logger.info(f"{status_icon} {test_name}: {self.test_results[test_name]['status']} ({execution_time:.2f}s)")
                
            except asyncio.TimeoutError:
                execution_time = time.time() - start_time
                self.test_results[test_name] = {
                    "status": "TIMEOUT",
                    "execution_time": execution_time,
                    "result_count": 0,
                    "results": None,
                    "critical": test_config["critical"],
                    "error": f"Test timed out after {test_config['timeout']} seconds"
                }
                
                self.logger.error(f"⏰ {test_name}: TIMEOUT ({execution_time:.2f}s)")
                
        except Exception as e:
            execution_time = time.time() - start_time
            self.test_results[test_name] = {
                "status": "ERROR",
                "execution_time": execution_time,
                "result_count": 0,
                "results": None,
                "critical": test_config["critical"],
                "error": str(e)
            }
            
            self.logger.error(f"❌ {test_name}: ERROR - {str(e)} ({execution_time:.2f}s)")
    
    def _analyze_test_results(self, test_name: str, results: Any) -> bool:
        """Analyze test results to determine success"""
        
        if not results:
            return False
        
        if isinstance(results, list):
            if test_name == "End-to-End Report Generation":
                # E2E tests: all companies should generate reports successfully
                return all(r.success for r in results)
            
            elif test_name == "Concurrent User Simulation":
                # Concurrent tests: error rate should be < 10%
                return all(r.error_rate < 10 for r in results)
            
            elif test_name == "Performance Benchmarking":
                # Performance tests: critical benchmarks should pass
                critical_benchmarks = [b for b in results if b.metric_type in ['response_time', 'memory']]
                if critical_benchmarks:
                    return sum(1 for b in critical_benchmarks if b.passed) >= len(critical_benchmarks) * 0.8
                return True
            
            elif test_name == "Error Handling Validation":
                # Error handling: critical error scenarios should be handled
                critical_tests = [r for r in results if r.error_scenario in [
                    "Invalid input data", "Authentication failure", "Authorization failure"
                ]]
                if critical_tests:
                    return all(r.handled_correctly for r in critical_tests)
                return sum(1 for r in results if r.handled_correctly) >= len(results) * 0.8
            
            elif test_name == "Mobile Responsiveness":
                # Mobile tests: critical features should work
                critical_features = ["Touch Feedback", "Text Readability", "Mobile Report Layout"]
                critical_tests = [r for r in results if r.feature_tested in critical_features]
                if critical_tests:
                    return sum(1 for r in critical_tests if r.passed) >= len(critical_tests) * 0.9
                return sum(1 for r in results if r.passed) >= len(results) * 0.8
        
        return True
    
    async def _generate_final_report(self) -> Dict[str, Any]:
        """Generate comprehensive final report"""
        
        total_execution_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        self.logger.info("\n" + "="*80)
        self.logger.info("FINAL SYSTEM INTEGRATION TEST REPORT")
        self.logger.info("="*80)
        
        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r["status"] == "PASSED")
        failed_tests = sum(1 for r in self.test_results.values() if r["status"] == "FAILED")
        timeout_tests = sum(1 for r in self.test_results.values() if r["status"] == "TIMEOUT")
        error_tests = sum(1 for r in self.test_results.values() if r["status"] == "ERROR")
        
        # Critical test analysis
        critical_tests = {name: result for name, result in self.test_results.items() if result["critical"]}
        critical_passed = sum(1 for r in critical_tests.values() if r["status"] == "PASSED")
        critical_total = len(critical_tests)
        
        self.logger.info(f"Execution Summary:")
        self.logger.info(f"  Total Execution Time: {total_execution_time:.2f} seconds")
        self.logger.info(f"  Total Test Suites: {total_tests}")
        self.logger.info(f"  Passed: {passed_tests}")
        self.logger.info(f"  Failed: {failed_tests}")
        self.logger.info(f"  Timeout: {timeout_tests}")
        self.logger.info(f"  Error: {error_tests}")
        self.logger.info(f"  Overall Success Rate: {(passed_tests / total_tests) * 100:.1f}%")
        
        self.logger.info(f"\nCritical Tests:")
        self.logger.info(f"  Critical Passed: {critical_passed}/{critical_total}")
        self.logger.info(f"  Critical Success Rate: {(critical_passed / critical_total) * 100:.1f}%")
        
        # Detailed results by test suite
        self.logger.info(f"\nDetailed Results:")
        self.logger.info("-" * 80)
        
        for test_name, result in self.test_results.items():
            status_icon = {
                "PASSED": "✅",
                "FAILED": "❌", 
                "TIMEOUT": "⏰",
                "ERROR": "🚨"
            }.get(result["status"], "❓")
            
            critical_marker = " [CRITICAL]" if result["critical"] else ""
            
            self.logger.info(f"{status_icon} {test_name}{critical_marker}: {result['status']} ({result['execution_time']:.2f}s)")
            
            if result["status"] in ["FAILED", "TIMEOUT", "ERROR"] and "error" in result:
                self.logger.info(f"    Error: {result['error']}")
            
            if result["result_count"] > 0:
                self.logger.info(f"    Results: {result['result_count']} test cases")
        
        # System readiness assessment
        system_ready = self._assess_system_readiness(critical_passed, critical_total, passed_tests, total_tests)
        
        self.logger.info(f"\n{'='*80}")
        if system_ready:
            self.logger.info("🎉 SYSTEM READY FOR PHASE 3 DEPLOYMENT!")
            self.logger.info("All critical tests passed and system meets quality standards.")
        else:
            self.logger.info("🚨 SYSTEM NOT READY FOR PHASE 3 DEPLOYMENT!")
            self.logger.info("Critical issues must be resolved before proceeding.")
        self.logger.info("="*80)
        
        # Identify specific issues for Phase 3 resolution
        issues_for_phase3 = self._identify_phase3_issues()
        
        if issues_for_phase3:
            self.logger.info(f"\nISSUES FOR PHASE 3 RESOLUTION:")
            for issue in issues_for_phase3:
                self.logger.info(f"  - {issue}")
        
        # Generate comprehensive report data
        report_data = {
            "test_execution_summary": {
                "timestamp": datetime.now().isoformat(),
                "start_time": datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
                "end_time": datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
                "total_execution_time": total_execution_time,
                "total_test_suites": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "timeout_tests": timeout_tests,
                "error_tests": error_tests,
                "overall_success_rate": (passed_tests / total_tests) * 100,
                "critical_tests_total": critical_total,
                "critical_tests_passed": critical_passed,
                "critical_success_rate": (critical_passed / critical_total) * 100 if critical_total > 0 else 100
            },
            "system_readiness": {
                "ready_for_phase3": system_ready,
                "assessment_criteria": {
                    "critical_tests_must_pass": True,
                    "overall_success_rate_threshold": 80,
                    "no_timeout_or_error_in_critical": True
                }
            },
            "test_results": {
                name: {
                    "status": result["status"],
                    "execution_time": result["execution_time"],
                    "result_count": result["result_count"],
                    "critical": result["critical"],
                    "error": result.get("error")
                }
                for name, result in self.test_results.items()
            },
            "issues_for_phase3": issues_for_phase3,
            "recommendations": self._generate_recommendations()
        }
        
        # Save comprehensive report
        report_filename = f"system_integration_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_filename, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
        
        self.logger.info(f"\nComprehensive test report saved to: {report_filename}")
        
        return report_data
    
    def _assess_system_readiness(self, critical_passed: int, critical_total: int, 
                                passed_tests: int, total_tests: int) -> bool:
        """Assess if system is ready for Phase 3 deployment"""
        
        # All critical tests must pass
        critical_success = critical_passed == critical_total if critical_total > 0 else True
        
        # Overall success rate must be >= 80%
        overall_success = (passed_tests / total_tests) >= 0.8 if total_tests > 0 else True
        
        # No critical tests should have timeout or error status
        critical_no_failures = all(
            result["status"] not in ["TIMEOUT", "ERROR"] 
            for result in self.test_results.values() 
            if result["critical"]
        )
        
        return critical_success and overall_success and critical_no_failures
    
    def _identify_phase3_issues(self) -> List[str]:
        """Identify specific issues that need resolution in Phase 3"""
        
        issues = []
        
        for test_name, result in self.test_results.items():
            if result["status"] in ["FAILED", "TIMEOUT", "ERROR"]:
                if result["critical"]:
                    issues.append(f"CRITICAL: {test_name} - {result['status']}")
                else:
                    issues.append(f"{test_name} - {result['status']}")
                
                if "error" in result:
                    issues.append(f"  └─ {result['error']}")
        
        # Add specific recommendations based on failed tests
        failed_tests = [name for name, result in self.test_results.items() if result["status"] == "FAILED"]
        
        if "End-to-End Report Generation" in failed_tests:
            issues.append("Report generation pipeline needs optimization")
        
        if "Concurrent User Simulation" in failed_tests:
            issues.append("System scalability improvements required")
        
        if "Performance Benchmarking" in failed_tests:
            issues.append("Performance optimization needed")
        
        if "Error Handling Validation" in failed_tests:
            issues.append("Error handling mechanisms need improvement")
        
        return issues
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for system improvement"""
        
        recommendations = []
        
        # Analyze test results and provide specific recommendations
        for test_name, result in self.test_results.items():
            if result["status"] == "PASSED":
                continue
            
            if test_name == "End-to-End Report Generation":
                recommendations.append("Optimize Kiro CLI integration and report generation pipeline")
                recommendations.append("Implement better error handling for data collection failures")
            
            elif test_name == "Concurrent User Simulation":
                recommendations.append("Implement connection pooling and load balancing")
                recommendations.append("Add rate limiting and request queuing mechanisms")
            
            elif test_name == "Performance Benchmarking":
                recommendations.append("Optimize database queries and add caching layers")
                recommendations.append("Implement CDN for static assets and API response caching")
            
            elif test_name == "Error Handling Validation":
                recommendations.append("Improve error message quality and user feedback")
                recommendations.append("Implement comprehensive logging and monitoring")
            
            elif test_name == "Mobile Responsiveness":
                recommendations.append("Enhance mobile UI components and touch interactions")
                recommendations.append("Optimize mobile performance and loading times")
        
        # General recommendations
        if any(r["status"] != "PASSED" for r in self.test_results.values()):
            recommendations.extend([
                "Implement comprehensive monitoring and alerting system",
                "Set up automated testing pipeline for continuous integration",
                "Create detailed deployment and rollback procedures",
                "Establish performance baselines and SLA monitoring"
            ])
        
        return list(set(recommendations))  # Remove duplicates

async def main():
    """Main test execution"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(f'system_integration_tests_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
        ]
    )
    
    # Create test runner
    runner = SystemIntegrationTestRunner()
    
    try:
        # Execute all tests
        final_report = await runner.run_all_tests()
        
        # Determine exit code based on system readiness
        system_ready = final_report["system_readiness"]["ready_for_phase3"]
        
        return 0 if system_ready else 1
        
    except KeyboardInterrupt:
        logging.info("\nTest execution interrupted by user")
        return 1
    except Exception as e:
        logging.error(f"Test execution failed: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)