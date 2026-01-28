"""
MarketMind Pro - Kiro Prompt Service
Handles execution of specialized financial analysis prompts using Kiro CLI
"""

import os
import asyncio
import subprocess
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class KiroPromptService:
    """Service for executing MarketMind Pro Kiro prompts"""
    
    def __init__(self, kiro_cli_path: str = "kiro-cli", prompts_dir: str = ".kiro/prompts"):
        self.kiro_cli_path = kiro_cli_path
        self.prompts_dir = Path(prompts_dir)
        self.prompts = {
            "company_overview": "company-overview-investment-thesis.md",
            "financial_analysis": "financial-analysis-key-metrics.md", 
            "valuation_analysis": "valuation-analysis-price-target.md",
            "risk_assessment": "risk-assessment-summary.md"
        }
    
    async def generate_company_overview(self, data: Dict[str, Any]) -> str:
        """Generate Page 1: Company Overview & Investment Thesis"""
        return await self._execute_prompt("company_overview", data)
    
    async def generate_financial_analysis(self, data: Dict[str, Any]) -> str:
        """Generate Page 2: Financial Analysis & Key Metrics"""
        return await self._execute_prompt("financial_analysis", data)
    
    async def generate_valuation_analysis(self, data: Dict[str, Any]) -> str:
        """Generate Page 3: Valuation Analysis & Price Target"""
        return await self._execute_prompt("valuation_analysis", data)
    
    async def generate_risk_assessment(self, data: Dict[str, Any]) -> str:
        """Generate Pages 4-5: Risk Assessment & Summary"""
        return await self._execute_prompt("risk_assessment", data)
    
    async def generate_full_report(self, ticker: str, company_data: Dict[str, Any]) -> Dict[str, str]:
        """Generate complete 5-page report using all prompts"""
        logger.info(f"Starting full report generation for {ticker}")
        
        try:
            # Execute all prompts concurrently for speed
            tasks = [
                self.generate_company_overview(company_data),
                self.generate_financial_analysis(company_data),
                self.generate_valuation_analysis(company_data),
                self.generate_risk_assessment(company_data)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Check for errors
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Error in prompt {i}: {result}")
                    raise result
            
            report = {
                "page_1_company_overview": results[0],
                "page_2_financial_analysis": results[1], 
                "page_3_valuation_analysis": results[2],
                "pages_4_5_risk_assessment": results[3],
                "ticker": ticker,
                "generated_at": asyncio.get_event_loop().time()
            }
            
            logger.info(f"Successfully generated full report for {ticker}")
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate report for {ticker}: {e}")
            raise
    
    async def _execute_prompt(self, prompt_key: str, data: Dict[str, Any]) -> str:
        """Execute a single Kiro prompt with provided data"""
        prompt_file = self.prompts.get(prompt_key)
        if not prompt_file:
            raise ValueError(f"Unknown prompt key: {prompt_key}")
        
        prompt_path = self.prompts_dir / prompt_file
        if not prompt_path.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
        
        try:
            # Read and format the prompt
            with open(prompt_path, 'r') as f:
                prompt_template = f.read()
            
            formatted_prompt = prompt_template.format(**data)
            
            # Execute with Kiro CLI
            result = await self._run_kiro_cli(formatted_prompt)
            
            logger.info(f"Successfully executed prompt: {prompt_key}")
            return result
            
        except Exception as e:
            logger.error(f"Error executing prompt {prompt_key}: {e}")
            raise
    
    async def _run_kiro_cli(self, prompt: str) -> str:
        """Execute Kiro CLI with the formatted prompt"""
        try:
            # Execute Kiro CLI by passing prompt as input with trust-all-tools for automation
            cmd = [self.kiro_cli_path, "chat", "--no-interactive", "--trust-all-tools"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate(input=prompt.encode())
            
            if process.returncode != 0:
                error_msg = stderr.decode() if stderr else "Unknown error"
                raise RuntimeError(f"Kiro CLI failed: {error_msg}")
            
            return stdout.decode().strip()
            
        except Exception as e:
            logger.error(f"Kiro CLI execution failed: {e}")
            raise

# Singleton instance
kiro_service = KiroPromptService()

# Convenience functions for FastAPI endpoints
async def generate_stock_report(ticker: str, company_data: Dict[str, Any]) -> Dict[str, str]:
    """Generate complete stock analysis report"""
    return await kiro_service.generate_full_report(ticker, company_data)

async def generate_report_section(section: str, data: Dict[str, Any]) -> str:
    """Generate individual report section"""
    section_methods = {
        "company_overview": kiro_service.generate_company_overview,
        "financial_analysis": kiro_service.generate_financial_analysis,
        "valuation_analysis": kiro_service.generate_valuation_analysis,
        "risk_assessment": kiro_service.generate_risk_assessment
    }
    
    method = section_methods.get(section)
    if not method:
        raise ValueError(f"Unknown section: {section}")
    
    return await method(data)