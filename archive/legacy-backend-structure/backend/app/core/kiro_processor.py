import asyncio
import logging
from typing import List, Dict, Any, Optional
from .utils.kiro_validator import KiroOutputValidator, KiroOutputError

logger = logging.getLogger(__name__)

class KiroOutputProcessor:
    
    def __init__(self):
        self.validator = KiroOutputValidator()
    
    async def process_single_output(self, raw_output: str, section_name: str) -> Dict[str, Any]:
        """Process a single Kiro CLI output with error handling"""
        try:
            formatted = self.validator.format_output(raw_output)
            formatted["section"] = section_name
            logger.info(f"Successfully processed {section_name}")
            return formatted
        except Exception as e:
            logger.error(f"Failed to process {section_name}: {e}")
            return self._create_error_output(section_name, str(e))
    
    async def process_batch_outputs(self, outputs: Dict[str, str]) -> Dict[str, Dict[str, Any]]:
        """Process multiple Kiro CLI outputs concurrently"""
        tasks = [
            self.process_single_output(output, section)
            for section, output in outputs.items()
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed = {}
        for i, (section, result) in enumerate(zip(outputs.keys(), results)):
            if isinstance(result, Exception):
                logger.error(f"Exception in {section}: {result}")
                processed[section] = self._create_error_output(section, str(result))
            else:
                processed[section] = result
        
        return processed
    
    def validate_report_completeness(self, processed_outputs: Dict[str, Dict[str, Any]]) -> bool:
        """Validate that all required sections are present and valid"""
        required_sections = ["executive_summary", "financial_analysis", "valuation"]
        
        for section in required_sections:
            if section not in processed_outputs:
                return False
            if processed_outputs[section].get("error"):
                return False
        
        return True
    
    def merge_report_sections(self, processed_outputs: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Merge all sections into a comprehensive report"""
        merged = {
            "analysis": "",
            "key_insights": [],
            "metrics": [],
            "charts": [],
            "tables": [],
            "recommendations": [],
            "sections": processed_outputs
        }
        
        for section_data in processed_outputs.values():
            if section_data.get("error"):
                continue
                
            merged["analysis"] += f"\n{section_data.get('analysis', '')}"
            merged["key_insights"].extend(section_data.get("key_insights", []))
            merged["metrics"].extend(section_data.get("metrics", []))
            merged["charts"].extend(section_data.get("charts", []))
            merged["tables"].extend(section_data.get("tables", []))
            merged["recommendations"].extend(section_data.get("recommendations", []))
        
        return merged
    
    def _create_error_output(self, section_name: str, error_msg: str) -> Dict[str, Any]:
        """Create standardized error output"""
        return {
            "section": section_name,
            "error": True,
            "error_message": error_msg,
            "analysis": f"Error processing {section_name}: {error_msg}",
            "key_insights": [f"Failed to generate insights for {section_name}"],
            "metrics": [],
            "charts": [],
            "tables": [],
            "recommendations": []
        }