import json
from typing import Dict, Any, Union
from pydantic import ValidationError
from .schemas.kiro_output import KiroOutput

class KiroOutputValidator:
    
    @staticmethod
    def validate(data: Union[str, Dict[str, Any]]) -> KiroOutput:
        """Validate and parse Kiro CLI output"""
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON: {e}")
        
        try:
            return KiroOutput(**data)
        except ValidationError as e:
            raise ValueError(f"Schema validation failed: {e}")
    
    @staticmethod
    def format_output(raw_output: Union[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Format and standardize Kiro CLI output"""
        validated = KiroOutputValidator.validate(raw_output)
        return validated.dict()
    
    @staticmethod
    def convert_legacy_format(legacy_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert legacy Kiro outputs to standard format"""
        converted = {
            "analysis": legacy_data.get("summary", legacy_data.get("analysis", "")),
            "key_insights": legacy_data.get("insights", legacy_data.get("key_points", [])),
            "metrics": [],
            "charts": [],
            "tables": [],
            "recommendations": []
        }
        
        # Convert metrics
        if "data" in legacy_data:
            for key, value in legacy_data["data"].items():
                converted["metrics"].append({
                    "name": key,
                    "value": value,
                    "unit": None
                })
        
        # Convert recommendations
        if "recommendation" in legacy_data:
            rec = legacy_data["recommendation"]
            converted["recommendations"].append({
                "type": rec.get("action", "HOLD").upper(),
                "confidence": rec.get("confidence", 0.5),
                "reasoning": rec.get("reason", ""),
                "price_target": rec.get("target_price")
            })
        
        return KiroOutputValidator.format_output(converted)

class KiroOutputError(Exception):
    """Custom exception for Kiro output processing errors"""
    pass