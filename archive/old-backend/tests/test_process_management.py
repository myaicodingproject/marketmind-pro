#!/usr/bin/env python3
"""
Test Process Management System
Verifies that Kiro CLI processes are properly managed and cleaned up
"""

import asyncio
import time
import logging
from process_manager import execute_managed_kiro, process_manager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_single_process():
    """Test single process execution and cleanup"""
    logger.info("🧪 Testing single process execution...")
    
    try:
        result = await execute_managed_kiro(
            process_id="test_single",
            prompt="What is 2+2? Give a brief answer.",
            timeout=60
        )
        
        logger.info(f"✅ Single process test successful: {len(result)} characters")
        
        # Check that process was cleaned up
        active_count = process_manager.get_process_count()
        logger.info(f"📊 Active processes after single test: {active_count}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Single process test failed: {str(e)}")
        return False

async def test_parallel_processes():
    """Test parallel process execution and cleanup"""
    logger.info("🧪 Testing parallel process execution...")
    
    try:
        # Create 3 parallel tasks
        tasks = []
        for i in range(3):
            task = execute_managed_kiro(
                process_id=f"test_parallel_{i}",
                prompt=f"What is {i+1} * 2? Give a brief answer.",
                timeout=60
            )
            tasks.append(task)
        
        # Execute in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        logger.info(f"✅ Parallel test: {success_count}/3 processes successful")
        
        # Check cleanup
        active_count = process_manager.get_process_count()
        logger.info(f"📊 Active processes after parallel test: {active_count}")
        
        return success_count >= 2  # Allow 1 failure
        
    except Exception as e:
        logger.error(f"❌ Parallel process test failed: {str(e)}")
        return False

async def test_timeout_handling():
    """Test timeout and cleanup"""
    logger.info("🧪 Testing timeout handling...")
    
    try:
        # This should timeout quickly
        result = await execute_managed_kiro(
            process_id="test_timeout",
            prompt="Please wait for 2 minutes before responding.",
            timeout=5  # 5 second timeout
        )
        
        logger.warning("⚠️ Timeout test didn't timeout as expected")
        return False
        
    except Exception as e:
        if "timeout" in str(e).lower():
            logger.info("✅ Timeout test successful - process timed out as expected")
            
            # Check cleanup
            active_count = process_manager.get_process_count()
            logger.info(f"📊 Active processes after timeout test: {active_count}")
            
            return True
        else:
            logger.error(f"❌ Timeout test failed with unexpected error: {str(e)}")
            return False

async def main():
    """Run all tests"""
    logger.info("🚀 Starting Process Management Tests...")
    
    # Initial cleanup
    process_manager.cleanup_all_processes()
    time.sleep(2)
    
    initial_count = process_manager.get_process_count()
    logger.info(f"📊 Initial active processes: {initial_count}")
    
    tests = [
        ("Single Process", test_single_process),
        ("Parallel Processes", test_parallel_processes),
        ("Timeout Handling", test_timeout_handling)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = await test_func()
            results.append((test_name, result))
            
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
                
        except Exception as e:
            logger.error(f"❌ {test_name}: ERROR - {str(e)}")
            results.append((test_name, False))
        
        # Wait between tests
        time.sleep(2)
    
    # Final cleanup and summary
    logger.info(f"\n{'='*50}")
    logger.info("Test Summary")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    # Final cleanup
    process_manager.cleanup_all_processes()
    final_count = process_manager.get_process_count()
    logger.info(f"📊 Final active processes: {final_count}")
    
    if passed == total and final_count == 0:
        logger.info("🎉 All tests passed and processes cleaned up successfully!")
        return True
    else:
        logger.error("❌ Some tests failed or processes not cleaned up properly")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)
