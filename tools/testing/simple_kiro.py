#!/usr/bin/env python3
"""
Simple Kiro CLI executor without process management
Fallback for when process management causes issues
"""

import asyncio
import subprocess
import logging
import re
from content_pipeline import clean_ai_content

logger = logging.getLogger(__name__)

async def execute_simple_kiro(prompt: str, timeout: int = 600) -> str:
    """Execute Kiro CLI without process management"""
    
    cmd = ["kiro-cli", "chat"]
    logger.info(f"🚀 Executing simple Kiro CLI")
    
    try:
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd="/mnt/c/kiro"
        )
        
        # Execute with timeout
        stdout, stderr = await asyncio.wait_for(
            process.communicate(input=prompt.encode()),
            timeout=timeout
        )
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise Exception(f"Kiro CLI failed: {error_msg}")
        
        # Process output
        raw_output = stdout.decode()
        
        # Clean up ANSI codes
        clean_output = re.sub(r'\x1b\[[0-9;]*m', '', raw_output)
        
        # Check content length
        if len(clean_output.strip()) < 100:
            raise Exception(f"Insufficient content generated: {len(clean_output)} characters")
        
        # Clean AI-generated content
        cleaned_content = clean_ai_content(clean_output.strip())
        
        logger.info(f"✅ Simple Kiro CLI completed: {len(cleaned_content)} characters")
        return cleaned_content
        
    except asyncio.TimeoutError:
        logger.error(f"⏰ Simple Kiro CLI timeout after {timeout}s")
        if process.returncode is None:
            process.kill()
            await process.wait()
        raise Exception(f"Kiro CLI timeout after {timeout} seconds")
        
    except Exception as e:
        logger.error(f"❌ Simple Kiro CLI failed: {str(e)}")
        raise

if __name__ == "__main__":
    # Test the simple executor
    async def test():
        result = await execute_simple_kiro("What is 2+2? Give a brief answer.", timeout=60)
        print(f"Result: {result}")
    
    asyncio.run(test())
