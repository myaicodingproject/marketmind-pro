"""
MarketMind Pro - Kiro Agent Base Class
Production-ready base class for all Kiro CLI-powered financial analysis agents
"""

import asyncio
import subprocess
import json
import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

@dataclass
class KiroExecutionResult:
    """Result from Kiro CLI execution"""
    success: bool
    content: str
    execution_time: float
    error_message: Optional[str] = None
    retry_count: int = 0

@dataclass
class AgentConfig:
    """Configuration for Kiro agents"""
    max_retries: int = 3
    timeout_seconds: int = 120
    trust_all_tools: bool = True
    no_interactive: bool = True

class KiroAgentBase(ABC):
    """Base class for all Kiro CLI-powered agents"""
    
    def __init__(self, 
                 agent_name: str,
                 kiro_cli_path: str = "kiro-cli",
                 prompts_dir: str = ".kiro/prompts",
                 config: Optional[AgentConfig] = None):
        self.agent_name = agent_name
        self.kiro_cli_path = kiro_cli_path
        self.prompts_dir = Path(prompts_dir)
        self.config = config or AgentConfig()
        
    @abstractmethod
    async def generate_content(self, ticker: str, context_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate content using Kiro CLI - must be implemented by subclasses"""
        pass
    
    async def execute_kiro_prompt(self, 
                                  prompt_file: str, 
                                  context_data: Dict[str, Any],
                                  custom_instructions: Optional[str] = None) -> KiroExecutionResult:
        """Execute a Kiro prompt with retry logic and error handling"""
        
        prompt_path = self.prompts_dir / prompt_file
        if not prompt_path.exists():
            return KiroExecutionResult(
                success=False,
                content="",
                execution_time=0,
                error_message=f"Prompt file not found: {prompt_path}"
            )
        
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                
                # Load and format prompt
                formatted_prompt = await self._load_and_format_prompt(prompt_path, context_data, custom_instructions)
                
                # Execute Kiro CLI
                result = await self._execute_kiro_cli(formatted_prompt)
                
                execution_time = time.time() - start_time
                
                logger.info(f"{self.agent_name}: Successfully executed {prompt_file} in {execution_time:.2f}s")
                
                return KiroExecutionResult(
                    success=True,
                    content=result,
                    execution_time=execution_time,
                    retry_count=attempt
                )
                
            except Exception as e:
                logger.warning(f"{self.agent_name}: Attempt {attempt + 1} failed for {prompt_file}: {e}")
                
                if attempt == self.config.max_retries - 1:
                    return KiroExecutionResult(
                        success=False,
                        content="",
                        execution_time=time.time() - start_time,
                        error_message=str(e),
                        retry_count=attempt + 1
                    )
                
                # Exponential backoff
                await asyncio.sleep(2 ** attempt)
        
        return KiroExecutionResult(
            success=False,
            content="",
            execution_time=0,
            error_message="Max retries exceeded"
        )
    
    async def _load_and_format_prompt(self, 
                                      prompt_path: Path, 
                                      context_data: Dict[str, Any],
                                      custom_instructions: Optional[str] = None) -> str:
        """Load prompt file and format with context data"""
        
        try:
            with open(prompt_path, 'r', encoding='utf-8') as f:
                prompt_template = f.read()
            
            # Add custom instructions if provided
            if custom_instructions:
                prompt_template += f"\n\n## Additional Instructions\n{custom_instructions}"
            
            # Format with context data, handling missing keys gracefully
            formatted_prompt = self._safe_format(prompt_template, context_data)
            
            return formatted_prompt
            
        except Exception as e:
            logger.error(f"Error loading/formatting prompt {prompt_path}: {e}")
            raise
    
    def _safe_format(self, template: str, data: Dict[str, Any]) -> str:
        """Safely format template, replacing missing keys with placeholders"""
        
        # Find all format placeholders
        import re
        placeholders = re.findall(r'\{([^}]+)\}', template)
        
        # Create safe data dict with defaults for missing keys
        safe_data = {}
        for key in placeholders:
            if key in data:
                safe_data[key] = data[key]
            else:
                safe_data[key] = f"[{key}_not_available]"
                logger.warning(f"Missing context data for key: {key}")
        
        return template.format(**safe_data)
    
    async def _execute_kiro_cli(self, prompt: str) -> str:
        """Execute Kiro CLI with the formatted prompt"""
        
        try:
            # Build command
            cmd = [self.kiro_cli_path, "chat"]
            
            if self.config.no_interactive:
                cmd.append("--no-interactive")
            
            if self.config.trust_all_tools:
                cmd.append("--trust-all-tools")
            
            logger.debug(f"{self.agent_name}: Executing Kiro CLI: {' '.join(cmd)}")
            
            # Create subprocess
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Execute with timeout
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(input=prompt.encode('utf-8')),
                    timeout=self.config.timeout_seconds
                )
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                raise RuntimeError(f"Kiro CLI execution timed out after {self.config.timeout_seconds}s")
            
            # Check return code
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                raise RuntimeError(f"Kiro CLI failed (code {process.returncode}): {error_msg}")
            
            result = stdout.decode('utf-8').strip()
            
            if not result:
                raise RuntimeError("Kiro CLI returned empty result")
            
            return result
            
        except Exception as e:
            logger.error(f"{self.agent_name}: Kiro CLI execution failed: {e}")
            raise
    
    async def execute_multiple_prompts(self, 
                                       prompt_configs: List[Dict[str, Any]],
                                       context_data: Dict[str, Any]) -> Dict[str, KiroExecutionResult]:
        """Execute multiple prompts concurrently"""
        
        tasks = []
        prompt_names = []
        
        for config in prompt_configs:
            prompt_file = config['prompt_file']
            custom_instructions = config.get('custom_instructions')
            prompt_name = config.get('name', prompt_file)
            
            task = self.execute_kiro_prompt(prompt_file, context_data, custom_instructions)
            tasks.append(task)
            prompt_names.append(prompt_name)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        execution_results = {}
        for i, result in enumerate(results):
            prompt_name = prompt_names[i]
            
            if isinstance(result, Exception):
                execution_results[prompt_name] = KiroExecutionResult(
                    success=False,
                    content="",
                    execution_time=0,
                    error_message=str(result)
                )
            else:
                execution_results[prompt_name] = result
        
        return execution_results
    
    def validate_result(self, result: KiroExecutionResult, min_length: int = 100) -> bool:
        """Validate Kiro execution result"""
        
        if not result.success:
            return False
        
        if len(result.content) < min_length:
            logger.warning(f"{self.agent_name}: Result too short ({len(result.content)} chars)")
            return False
        
        # Check for common error patterns
        error_patterns = [
            "error occurred",
            "failed to",
            "unable to",
            "not found",
            "invalid"
        ]
        
        content_lower = result.content.lower()
        for pattern in error_patterns:
            if pattern in content_lower:
                logger.warning(f"{self.agent_name}: Detected error pattern: {pattern}")
                return False
        
        return True