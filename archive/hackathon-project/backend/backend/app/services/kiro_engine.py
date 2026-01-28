"""
Core Kiro CLI Integration Engine
Handles async execution of specialized financial analysis prompts
"""

import asyncio
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from app.core.config import settings

logger = logging.getLogger(__name__)

class KiroExecutionError(Exception):
    """Custom exception for Kiro execution errors"""
    pass

class KiroEngine:
    """
    Core engine for executing Kiro CLI prompts with async support
    Handles prompt execution, context preparation, and result processing
    """
    
    def __init__(self):
        self.kiro_cli_path = getattr(settings, 'KIRO_CLI_PATH', 'kiro-cli')
        self.workspace_path = getattr(settings, 'KIRO_WORKSPACE_PATH', '/tmp/kiro_workspace')
        self.prompts_path = Path('.kiro/prompts')
        
        # Ensure workspace exists
        Path(self.workspace_path).mkdir(parents=True, exist_ok=True)
        
    async def execute_prompt(
        self, 
        prompt_name: str, 
        context_data: Dict[str, Any],
        timeout: int = 300
    ) -> Dict[str, Any]:
        """
        Execute a single Kiro prompt with provided context
        
        Args:
            prompt_name: Name of the prompt file (without .md extension)
            context_data: Dictionary of context variables for the prompt
            timeout: Execution timeout in seconds
            
        Returns:
            Dictionary containing execution results and metadata
        """
        try:
            execution_id = str(uuid.uuid4())
            start_time = datetime.now()
            
            logger.info(f"Executing Kiro prompt: {prompt_name} (ID: {execution_id})")
            
            # Prepare context file
            context_file = await self._prepare_context_file(context_data, execution_id)
            
            # Execute Kiro CLI command
            result = await self._execute_kiro_command(
                prompt_name, 
                context_file, 
                execution_id,
                timeout
            )
            
            # Process and return results
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'execution_id': execution_id,
                'prompt_name': prompt_name,
                'content': result,
                'execution_time': execution_time,
                'timestamp': start_time.isoformat(),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"Error executing prompt {prompt_name}: {str(e)}")
            raise KiroExecutionError(f"Failed to execute prompt {prompt_name}: {str(e)}")
        
        finally:
            # Cleanup temporary files
            try:
                if 'context_file' in locals():
                    Path(context_file).unlink(missing_ok=True)
            except Exception as cleanup_error:
                logger.warning(f"Failed to cleanup context file: {cleanup_error}")
    
    async def execute_multiple_prompts(
        self,
        prompt_configs: List[Dict[str, Any]],
        max_concurrent: int = 3
    ) -> Dict[str, Any]:
        """
        Execute multiple prompts concurrently with controlled concurrency
        
        Args:
            prompt_configs: List of prompt configurations
            max_concurrent: Maximum number of concurrent executions
            
        Returns:
            Dictionary with results for each prompt
        """
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def execute_with_semaphore(config):
            async with semaphore:
                return await self.execute_prompt(
                    config['prompt_name'],
                    config['context_data'],
                    config.get('timeout', 300)
                )
        
        # Execute all prompts concurrently
        tasks = [execute_with_semaphore(config) for config in prompt_configs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        processed_results = {}
        for i, result in enumerate(results):
            prompt_name = prompt_configs[i]['prompt_name']
            if isinstance(result, Exception):
                processed_results[prompt_name] = {
                    'status': 'error',
                    'error': str(result),
                    'prompt_name': prompt_name
                }
            else:
                processed_results[prompt_name] = result
        
        return processed_results
    
    async def _prepare_context_file(self, context_data: Dict[str, Any], execution_id: str) -> str:
        """Prepare context file for Kiro execution"""
        context_file = Path(self.workspace_path) / f"context_{execution_id}.json"
        
        # Ensure all context values are strings
        processed_context = {}
        for key, value in context_data.items():
            if isinstance(value, (dict, list)):
                processed_context[key] = json.dumps(value, indent=2)
            else:
                processed_context[key] = str(value) if value is not None else "Not available"
        
        # Write context to file
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(processed_context, f, indent=2, ensure_ascii=False)
        
        return str(context_file)
    
    async def _execute_kiro_command(
        self, 
        prompt_name: str, 
        context_file: str, 
        execution_id: str,
        timeout: int
    ) -> str:
        """Execute the actual Kiro CLI command"""
        
        # Construct Kiro CLI command
        prompt_file = self.prompts_path / f"{prompt_name}.md"
        
        if not prompt_file.exists():
            raise KiroExecutionError(f"Prompt file not found: {prompt_file}")
        
        # Kiro CLI command with context injection
        cmd = [
            self.kiro_cli_path,
            'chat',
            '--prompt-file', str(prompt_file),
            '--context-file', context_file,
            '--output-format', 'text'
        ]
        
        logger.debug(f"Executing command: {' '.join(cmd)}")
        
        # Execute command asynchronously
        try:
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(Path.cwd())
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(), 
                timeout=timeout
            )
            
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8') if stderr else "Unknown error"
                raise KiroExecutionError(f"Kiro CLI execution failed: {error_msg}")
            
            result = stdout.decode('utf-8').strip()
            
            if not result:
                raise KiroExecutionError("Kiro CLI returned empty result")
            
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Kiro execution timeout for prompt {prompt_name}")
            raise KiroExecutionError(f"Execution timeout after {timeout} seconds")
        
        except Exception as e:
            logger.error(f"Kiro execution error: {str(e)}")
            raise KiroExecutionError(f"Execution failed: {str(e)}")
    
    def get_available_prompts(self) -> List[str]:
        """Get list of available prompt files"""
        if not self.prompts_path.exists():
            return []
        
        return [
            f.stem for f in self.prompts_path.glob("*.md")
            if f.stem.startswith(('company-', 'financial-', 'valuation-', 'risk-'))
        ]
    
    async def validate_setup(self) -> Dict[str, Any]:
        """Validate Kiro CLI setup and availability"""
        try:
            # Test Kiro CLI availability
            process = await asyncio.create_subprocess_exec(
                self.kiro_cli_path, '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                return {
                    'status': 'error',
                    'message': 'Kiro CLI not available or not working',
                    'error': stderr.decode('utf-8') if stderr else 'Unknown error'
                }
            
            version = stdout.decode('utf-8').strip()
            available_prompts = self.get_available_prompts()
            
            return {
                'status': 'success',
                'kiro_version': version,
                'workspace_path': self.workspace_path,
                'prompts_path': str(self.prompts_path),
                'available_prompts': available_prompts,
                'prompt_count': len(available_prompts)
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': 'Failed to validate Kiro setup',
                'error': str(e)
            }

# Global instance
kiro_engine = KiroEngine()