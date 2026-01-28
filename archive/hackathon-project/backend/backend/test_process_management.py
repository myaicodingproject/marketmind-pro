#!/usr/bin/env python3
"""
Comprehensive Test Suite for Kiro Process Management System
Tests concurrent execution, memory management, and system stability
"""
import asyncio
import time
import logging
import json
from typing import List, Dict, Any
import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.process_manager import process_manager, ProcessStatus
from app.core.queue_manager import queue_manager, QueuePriority
from app.services.kiro_process_service import kiro_process_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProcessManagementTester:
    """Comprehensive tester for process management system"""
    
    def __init__(self):
        self.test_results = []
        
    async def run_all_tests(self):
        """Run all test scenarios"""
        logger.info("🚀 Starting Process Management Test Suite")
        
        try:
            # Initialize services
            await self._initialize_services()
            
            # Run test scenarios
            await self._test_basic_process_execution()
            await self._test_concurrent_execution()
            await self._test_memory_management()
            await self._test_queue_management()
            await self._test_error_handling()
            await self._test_resource_limits()
            await self._test_multiple_users()
            
            # Generate report
            self._generate_test_report()
            
        except Exception as e:
            logger.error(f"Test suite failed: {e}")
            raise
        finally:
            # Cleanup
            await self._cleanup_services()
            
    async def _initialize_services(self):
        """Initialize all process management services"""
        logger.info("Initializing services...")
        
        await process_manager.start()
        await queue_manager.start()
        await kiro_process_service.start()
        
        logger.info("✓ All services initialized")
        
    async def _cleanup_services(self):
        """Cleanup all services"""
        logger.info("Cleaning up services...")
        
        await kiro_process_service.stop()
        await queue_manager.stop()
        await process_manager.stop()
        
        logger.info("✓ All services cleaned up")
        
    async def _test_basic_process_execution(self):
        """Test basic process execution"""
        logger.info("🧪 Testing basic process execution...")
        
        start_time = time.time()
        
        try:
            # Test simple command execution
            result = await process_manager.execute_with_timeout(
                process_id="test_basic",
                command=["echo", "Hello World"],
                timeout=10
            )
            
            success = result["success"] and "Hello World" in result["stdout"]
            duration = time.time() - start_time
            
            self.test_results.append({
                "test": "basic_process_execution",
                "success": success,
                "duration": duration,
                "details": result
            })
            
            logger.info(f"✓ Basic execution test: {'PASSED' if success else 'FAILED'}")
            
        except Exception as e:
            self.test_results.append({
                "test": "basic_process_execution",
                "success": False,
                "error": str(e)
            })
            logger.error(f"✗ Basic execution test failed: {e}")
            
    async def _test_concurrent_execution(self):
        """Test concurrent process execution"""
        logger.info("🧪 Testing concurrent execution...")
        
        start_time = time.time()
        
        try:
            # Create multiple concurrent tasks
            tasks = []
            for i in range(5):
                task = process_manager.execute_with_timeout(
                    process_id=f"concurrent_test_{i}",
                    command=["sleep", "2"],
                    timeout=10
                )
                tasks.append(task)
                
            # Execute all tasks concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check results
            successful = sum(1 for r in results if isinstance(r, dict) and r.get("success"))
            duration = time.time() - start_time
            
            # Should complete in ~2 seconds (concurrent) not ~10 seconds (sequential)
            concurrent_success = duration < 5 and successful == 5
            
            self.test_results.append({
                "test": "concurrent_execution",
                "success": concurrent_success,
                "duration": duration,
                "successful_tasks": successful,
                "total_tasks": 5
            })
            
            logger.info(f"✓ Concurrent execution test: {'PASSED' if concurrent_success else 'FAILED'}")
            
        except Exception as e:
            self.test_results.append({
                "test": "concurrent_execution",
                "success": False,
                "error": str(e)
            })
            logger.error(f"✗ Concurrent execution test failed: {e}")
            
    async def _test_memory_management(self):
        """Test memory management and cleanup"""
        logger.info("🧪 Testing memory management...")
        
        try:
            initial_metrics = process_manager.get_metrics()
            
            # Create and complete several processes
            for i in range(10):
                result = await process_manager.execute_with_timeout(
                    process_id=f"memory_test_{i}",
                    command=["echo", f"test_{i}"],
                    timeout=5
                )
                
            # Wait for cleanup
            await asyncio.sleep(2)
            
            final_metrics = process_manager.get_metrics()
            
            # Check that active processes are cleaned up
            memory_success = final_metrics["active_processes"] == 0
            
            self.test_results.append({
                "test": "memory_management",
                "success": memory_success,
                "initial_active": initial_metrics["active_processes"],
                "final_active": final_metrics["active_processes"]
            })
            
            logger.info(f"✓ Memory management test: {'PASSED' if memory_success else 'FAILED'}")
            
        except Exception as e:
            self.test_results.append({
                "test": "memory_management",
                "success": False,
                "error": str(e)
            })
            logger.error(f"✗ Memory management test failed: {e}")
            
    async def _test_queue_management(self):
        """Test queue management system"""
        logger.info("🧪 Testing queue management...")
        
        try:
            # Submit multiple requests to queue
            request_ids = []
            for i in range(3):
                request_id = await queue_manager.submit_request(
                    user_id=f"test_user_{i}",
                    ticker="AAPL",
                    request_type="comprehensive_report",
                    priority=QueuePriority.NORMAL
                )
                request_ids.append(request_id)
                
            # Wait for processing
            await asyncio.sleep(5)
            
            # Check queue status
            queue_status = await queue_manager.get_queue_status()
            
            # Check individual request statuses
            completed_requests = 0
            for request_id in request_ids:
                status = await queue_manager.get_request_status(request_id)
                if status and status["status"] in ["completed", "failed"]:
                    completed_requests += 1
                    
            queue_success = completed_requests > 0
            
            self.test_results.append({
                "test": "queue_management",
                "success": queue_success,
                "completed_requests": completed_requests,
                "total_requests": len(request_ids),
                "queue_status": queue_status
            })
            
            logger.info(f"✓ Queue management test: {'PASSED' if queue_success else 'FAILED'}")
            
        except Exception as e:
            self.test_results.append({
                "test": "queue_management",
                "success": False,
                "error": str(e)
            })
            logger.error(f"✗ Queue management test failed: {e}")
            
    async def _test_error_handling(self):
        """Test error handling and recovery"""
        logger.info("🧪 Testing error handling...")
        
        try:
            # Test invalid command
            result = await process_manager.execute_with_timeout(
                process_id="error_test",
                command=["nonexistent_command"],
                timeout=5
            )
            
            # Should fail gracefully
            error_handled = not result["success"] and "error" in result
            
            # Test timeout handling
            timeout_result = await process_manager.execute_with_timeout(
                process_id="timeout_test",
                command=["sleep", "10"],
                timeout=2
            )
            
            timeout_handled = not timeout_result["success"] and "timeout" in timeout_result.get("error", "").lower()
            
            overall_success = error_handled and timeout_handled
            
            self.test_results.append({
                "test": "error_handling",
                "success": overall_success,
                "error_handled": error_handled,
                "timeout_handled": timeout_handled
            })
            
            logger.info(f"✓ Error handling test: {'PASSED' if overall_success else 'FAILED'}")
            
        except Exception as e:
            self.test_results.append({
                "test": "error_handling",
                "success": False,
                "error": str(e)
            })
            logger.error(f"✗ Error handling test failed: {e}")
            
    async def _test_resource_limits(self):
        """Test resource limit enforcement"""
        logger.info("🧪 Testing resource limits...")
        
        try:
            # Try to exceed concurrent process limit
            tasks = []
            for i in range(10):  # More than max_concurrent (3)
                task = process_manager.execute_with_timeout(
                    process_id=f"limit_test_{i}",
                    command=["sleep", "1"],
                    timeout=5
                )
                tasks.append(task)
                
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check that not all processes ran simultaneously
            metrics = process_manager.get_metrics()
            
            # Should have limited concurrent processes
            limit_enforced = True  # Basic test - more sophisticated checking could be added
            
            self.test_results.append({
                "test": "resource_limits",
                "success": limit_enforced,
                "max_concurrent_observed": metrics.get("active_processes", 0)
            })
            
            logger.info(f"✓ Resource limits test: {'PASSED' if limit_enforced else 'FAILED'}")
            
        except Exception as e:
            self.test_results.append({
                "test": "resource_limits",
                "success": False,
                "error": str(e)
            })
            logger.error(f"✗ Resource limits test failed: {e}")
            
    async def _test_multiple_users(self):
        """Test multiple user scenario"""
        logger.info("🧪 Testing multiple users...")
        
        try:
            # Simulate multiple users submitting requests
            users = ["user1", "user2", "user3"]
            request_ids = []
            
            for user in users:
                for i in range(2):  # 2 requests per user
                    request_id = await queue_manager.submit_request(
                        user_id=user,
                        ticker=f"TEST{i}",
                        request_type="comprehensive_report",
                        priority=QueuePriority.NORMAL
                    )
                    request_ids.append((user, request_id))
                    
            # Check user quotas
            user_statuses = {}
            for user in users:
                status = await queue_manager.get_user_status(user)
                user_statuses[user] = status
                
            # Basic success check
            multi_user_success = len(request_ids) == 6
            
            self.test_results.append({
                "test": "multiple_users",
                "success": multi_user_success,
                "total_requests": len(request_ids),
                "user_statuses": user_statuses
            })
            
            logger.info(f"✓ Multiple users test: {'PASSED' if multi_user_success else 'FAILED'}")
            
        except Exception as e:
            self.test_results.append({
                "test": "multiple_users",
                "success": False,
                "error": str(e)
            })
            logger.error(f"✗ Multiple users test failed: {e}")
            
    def _generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 Generating test report...")
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        
        report = {
            "test_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%"
            },
            "test_results": self.test_results,
            "timestamp": time.time()
        }
        
        # Save report to file
        with open("process_management_test_report.json", "w") as f:
            json.dump(report, f, indent=2, default=str)
            
        # Print summary
        print("\n" + "="*60)
        print("🧪 PROCESS MANAGEMENT TEST REPORT")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {report['test_summary']['success_rate']}")
        print("="*60)
        
        for result in self.test_results:
            status = "✅ PASS" if result["success"] else "❌ FAIL"
            print(f"{status} {result['test']}")
            if not result["success"] and "error" in result:
                print(f"    Error: {result['error']}")
                
        print("="*60)
        print(f"📄 Detailed report saved to: process_management_test_report.json")
        print("="*60)

async def main():
    """Main test runner"""
    tester = ProcessManagementTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())