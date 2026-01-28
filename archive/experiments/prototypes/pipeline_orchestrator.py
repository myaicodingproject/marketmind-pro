import asyncio
import json
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import websockets
import logging

class PipelineStage(Enum):
    GENERATION = "generation"
    VALIDATION = "validation"
    ASSETS = "assets"
    CONSOLIDATION = "consolidation"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

@dataclass
class PipelineProgress:
    stage: PipelineStage
    progress: float
    status: TaskStatus
    message: str
    timestamp: datetime
    errors: List[str] = None

class PipelineOrchestrator:
    def __init__(self, websocket_clients: set = None):
        self.clients = websocket_clients or set()
        self.progress = {}
        self.results = {}
        self.start_time = None
        
    async def execute_pipeline(self, symbol: str, analysis_type: str) -> Dict[str, Any]:
        """Execute the complete 4-stage pipeline"""
        self.start_time = time.time()
        pipeline_id = f"{symbol}_{int(self.start_time)}"
        
        try:
            # Stage 1: Parallel Generation (8 subagents)
            await self._update_progress(pipeline_id, PipelineStage.GENERATION, 0, TaskStatus.RUNNING, "Starting parallel generation")
            generation_results = await self._stage_1_generation(symbol, analysis_type, pipeline_id)
            
            # Stage 2: Quality Validation
            await self._update_progress(pipeline_id, PipelineStage.VALIDATION, 0, TaskStatus.RUNNING, "Validating analysis quality")
            validated_results = await self._stage_2_validation(generation_results, pipeline_id)
            
            # Stage 3: Asset Generation
            await self._update_progress(pipeline_id, PipelineStage.ASSETS, 0, TaskStatus.RUNNING, "Generating charts and tables")
            assets = await self._stage_3_assets(validated_results, pipeline_id)
            
            # Stage 4: Final Consolidation
            await self._update_progress(pipeline_id, PipelineStage.CONSOLIDATION, 0, TaskStatus.RUNNING, "Consolidating final report")
            final_result = await self._stage_4_consolidation(validated_results, assets, pipeline_id)
            
            elapsed = time.time() - self.start_time
            await self._update_progress(pipeline_id, PipelineStage.CONSOLIDATION, 100, TaskStatus.COMPLETED, f"Pipeline completed in {elapsed:.1f}s")
            
            return final_result
            
        except Exception as e:
            await self._update_progress(pipeline_id, None, 0, TaskStatus.FAILED, f"Pipeline failed: {str(e)}")
            raise

    async def _stage_1_generation(self, symbol: str, analysis_type: str, pipeline_id: str) -> Dict[str, Any]:
        """Stage 1: Parallel generation with 8 subagents"""
        subagents = [
            "financial_analysis", "technical_analysis", "market_sentiment", "risk_assessment",
            "competitive_analysis", "growth_prospects", "valuation_metrics", "executive_summary"
        ]
        
        tasks = []
        for i, agent in enumerate(subagents):
            task = self._run_subagent(agent, symbol, analysis_type, pipeline_id, i)
            tasks.append(task)
        
        results = {}
        completed = 0
        
        for task in asyncio.as_completed(tasks):
            try:
                agent_name, result = await task
                results[agent_name] = result
                completed += 1
                progress = (completed / len(subagents)) * 100
                await self._update_progress(pipeline_id, PipelineStage.GENERATION, progress, TaskStatus.RUNNING, f"Completed {agent_name}")
            except Exception as e:
                logging.error(f"Subagent failed: {e}")
                # Continue with other agents
        
        return results

    async def _run_subagent(self, agent_name: str, symbol: str, analysis_type: str, pipeline_id: str, index: int) -> tuple:
        """Run individual subagent with retry logic"""
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            try:
                # Simulate subagent execution (replace with actual subagent calls)
                await asyncio.sleep(0.5 + (index * 0.1))  # Staggered execution
                
                # Mock result - replace with actual subagent integration
                result = {
                    "analysis": f"{agent_name} analysis for {symbol}",
                    "confidence": 0.85,
                    "key_points": [f"Point 1 from {agent_name}", f"Point 2 from {agent_name}"],
                    "timestamp": datetime.now().isoformat()
                }
                
                return agent_name, result
                
            except Exception as e:
                if attempt < max_retries:
                    await asyncio.sleep(1)  # Brief retry delay
                    continue
                raise e

    async def _stage_2_validation(self, generation_results: Dict[str, Any], pipeline_id: str) -> Dict[str, Any]:
        """Stage 2: Quality validation and consistency checks"""
        validated = {}
        total_agents = len(generation_results)
        
        for i, (agent, result) in enumerate(generation_results.items()):
            # Quality checks
            if self._validate_result(result):
                validated[agent] = result
            else:
                # Attempt to fix or flag for manual review
                validated[agent] = self._fix_result(result)
            
            progress = ((i + 1) / total_agents) * 100
            await self._update_progress(pipeline_id, PipelineStage.VALIDATION, progress, TaskStatus.RUNNING, f"Validated {agent}")
        
        return validated

    def _validate_result(self, result: Dict[str, Any]) -> bool:
        """Validate individual analysis result"""
        required_fields = ["analysis", "confidence", "key_points"]
        return all(field in result for field in required_fields) and result.get("confidence", 0) > 0.7

    def _fix_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to fix validation issues"""
        if "confidence" not in result:
            result["confidence"] = 0.75
        if "key_points" not in result:
            result["key_points"] = ["Analysis pending review"]
        return result

    async def _stage_3_assets(self, validated_results: Dict[str, Any], pipeline_id: str) -> Dict[str, Any]:
        """Stage 3: Generate charts, tables, and visual assets"""
        assets = {}
        asset_types = ["price_chart", "financial_table", "risk_matrix", "summary_dashboard"]
        
        for i, asset_type in enumerate(asset_types):
            try:
                # Generate asset (mock implementation)
                asset_data = await self._generate_asset(asset_type, validated_results)
                assets[asset_type] = asset_data
                
                progress = ((i + 1) / len(asset_types)) * 100
                await self._update_progress(pipeline_id, PipelineStage.ASSETS, progress, TaskStatus.RUNNING, f"Generated {asset_type}")
                
            except Exception as e:
                logging.error(f"Asset generation failed for {asset_type}: {e}")
                assets[asset_type] = {"error": str(e)}
        
        return assets

    async def _generate_asset(self, asset_type: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate individual asset"""
        await asyncio.sleep(0.3)  # Simulate asset generation time
        
        return {
            "type": asset_type,
            "data": f"Generated {asset_type} data",
            "format": "png" if "chart" in asset_type else "json",
            "timestamp": datetime.now().isoformat()
        }

    async def _stage_4_consolidation(self, validated_results: Dict[str, Any], assets: Dict[str, Any], pipeline_id: str) -> Dict[str, Any]:
        """Stage 4: Final consolidation into PDF and database"""
        
        # Generate PDF report
        await self._update_progress(pipeline_id, PipelineStage.CONSOLIDATION, 25, TaskStatus.RUNNING, "Generating PDF report")
        pdf_path = await self._generate_pdf(validated_results, assets)
        
        # Save to database
        await self._update_progress(pipeline_id, PipelineStage.CONSOLIDATION, 75, TaskStatus.RUNNING, "Saving to database")
        db_record = await self._save_to_database(validated_results, assets, pdf_path)
        
        return {
            "pipeline_id": pipeline_id,
            "pdf_path": pdf_path,
            "database_id": db_record,
            "analysis_results": validated_results,
            "assets": assets,
            "execution_time": time.time() - self.start_time,
            "timestamp": datetime.now().isoformat()
        }

    async def _generate_pdf(self, results: Dict[str, Any], assets: Dict[str, Any]) -> str:
        """Generate consolidated PDF report"""
        await asyncio.sleep(0.5)  # Simulate PDF generation
        pdf_path = f"reports/report_{int(time.time())}.pdf"
        # Mock PDF generation - replace with actual PDF library
        return pdf_path

    async def _save_to_database(self, results: Dict[str, Any], assets: Dict[str, Any], pdf_path: str) -> str:
        """Save consolidated results to database"""
        await asyncio.sleep(0.2)  # Simulate database save
        # Mock database save - replace with actual database integration
        return f"db_record_{int(time.time())}"

    async def _update_progress(self, pipeline_id: str, stage: PipelineStage, progress: float, status: TaskStatus, message: str):
        """Update progress and broadcast to WebSocket clients"""
        progress_update = PipelineProgress(
            stage=stage,
            progress=progress,
            status=status,
            message=message,
            timestamp=datetime.now()
        )
        
        self.progress[pipeline_id] = progress_update
        
        # Broadcast to WebSocket clients
        if self.clients:
            update_message = {
                "pipeline_id": pipeline_id,
                "stage": stage.value if stage else None,
                "progress": progress,
                "status": status.value,
                "message": message,
                "timestamp": progress_update.timestamp.isoformat()
            }
            
            disconnected = set()
            for client in self.clients:
                try:
                    await client.send(json.dumps(update_message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected.add(client)
            
            # Remove disconnected clients
            self.clients -= disconnected

    def get_progress(self, pipeline_id: str) -> Optional[PipelineProgress]:
        """Get current progress for a pipeline"""
        return self.progress.get(pipeline_id)