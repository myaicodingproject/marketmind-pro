"""
WebSocket Progress Manager for Real-time Report Generation Updates
Provides live updates on section completion, quality validation, and overall status
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from enum import Enum

logger = logging.getLogger(__name__)

class ProgressStage(Enum):
    INITIALIZING = "initializing"
    DATA_COLLECTION = "data_collection"
    SECTION_GENERATION = "section_generation"
    QUALITY_VALIDATION = "quality_validation"
    PDF_GENERATION = "pdf_generation"
    COMPLETED = "completed"
    FAILED = "failed"

class WebSocketProgressManager:
    """Manages WebSocket connections for real-time report generation progress"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.report_progress: Dict[str, Dict] = {}
        self._connection_metadata: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, report_id: str, user_id: Optional[str] = None):
        """Connect a WebSocket to track specific report progress"""
        try:
            await websocket.accept()
            
            if report_id not in self.active_connections:
                self.active_connections[report_id] = set()
            
            self.active_connections[report_id].add(websocket)
            self._connection_metadata[websocket] = {
                "report_id": report_id,
                "user_id": user_id,
                "connected_at": datetime.utcnow(),
                "last_ping": datetime.utcnow()
            }
            
            # Send current progress if available
            if report_id in self.report_progress:
                await self._send_to_websocket(websocket, {
                    "type": "progress_update",
                    "data": self.report_progress[report_id]
                })
            
            logger.info(f"WebSocket connected for report {report_id} (user: {user_id})")
            
            # Send connection confirmation
            await self._send_to_websocket(websocket, {
                "type": "connection_established",
                "data": {
                    "report_id": report_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "message": "Real-time progress updates active"
                }
            })
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket: {str(e)}")
            raise
    
    async def disconnect(self, websocket: WebSocket):
        """Disconnect a WebSocket and clean up"""
        try:
            metadata = self._connection_metadata.get(websocket)
            if metadata:
                report_id = metadata["report_id"]
                
                if report_id in self.active_connections:
                    self.active_connections[report_id].discard(websocket)
                    
                    # Clean up empty report connections
                    if not self.active_connections[report_id]:
                        del self.active_connections[report_id]
                
                del self._connection_metadata[websocket]
                logger.info(f"WebSocket disconnected from report {report_id}")
        
        except Exception as e:
            logger.error(f"Error disconnecting WebSocket: {str(e)}")
    
    async def update_progress(self, report_id: str, stage: ProgressStage, progress: int, 
                            message: str, section_data: Optional[Dict] = None, 
                            error_details: Optional[Dict] = None):
        """Update progress for a report and broadcast to connected clients"""
        
        progress_data = {
            "report_id": report_id,
            "stage": stage.value,
            "progress": progress,
            "message": message,
            "timestamp": datetime.utcnow().isoformat(),
            "section_data": section_data or {},
            "error_details": error_details
        }
        
        # Store progress
        self.report_progress[report_id] = progress_data
        
        # Broadcast to all connected clients for this report
        await self._broadcast_to_report(report_id, {
            "type": "progress_update",
            "data": progress_data
        })
        
        logger.info(f"Progress updated for {report_id}: {stage.value} - {progress}%")
    
    async def update_section_progress(self, report_id: str, section_name: str, 
                                    section_progress: int, section_status: str,
                                    validation_results: Optional[Dict] = None):
        """Update progress for a specific report section"""
        
        section_data = {
            "section_name": section_name,
            "progress": section_progress,
            "status": section_status,
            "validation": validation_results or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update stored progress
        if report_id in self.report_progress:
            if "sections" not in self.report_progress[report_id]:
                self.report_progress[report_id]["sections"] = {}
            self.report_progress[report_id]["sections"][section_name] = section_data
        
        # Broadcast section update
        await self._broadcast_to_report(report_id, {
            "type": "section_update",
            "data": {
                "report_id": report_id,
                "section": section_data
            }
        })
        
        logger.info(f"Section progress updated for {report_id}: {section_name} - {section_progress}%")
    
    async def update_quality_validation(self, report_id: str, validation_stage: str,
                                      validation_progress: int, validation_results: Dict):
        """Update quality validation progress"""
        
        validation_data = {
            "stage": validation_stage,
            "progress": validation_progress,
            "results": validation_results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Update stored progress
        if report_id in self.report_progress:
            if "quality_validation" not in self.report_progress[report_id]:
                self.report_progress[report_id]["quality_validation"] = {}
            self.report_progress[report_id]["quality_validation"][validation_stage] = validation_data
        
        # Broadcast validation update
        await self._broadcast_to_report(report_id, {
            "type": "quality_validation_update",
            "data": {
                "report_id": report_id,
                "validation": validation_data
            }
        })
        
        logger.info(f"Quality validation updated for {report_id}: {validation_stage} - {validation_progress}%")
    
    async def report_completed(self, report_id: str, success: bool, 
                             report_url: Optional[str] = None, 
                             error_message: Optional[str] = None):
        """Mark report as completed and notify clients"""
        
        completion_data = {
            "report_id": report_id,
            "success": success,
            "report_url": report_url,
            "error_message": error_message,
            "completed_at": datetime.utcnow().isoformat()
        }
        
        # Update stored progress
        if report_id in self.report_progress:
            self.report_progress[report_id].update({
                "stage": ProgressStage.COMPLETED.value if success else ProgressStage.FAILED.value,
                "progress": 100 if success else 0,
                "completed": True,
                "completion_data": completion_data
            })
        
        # Broadcast completion
        await self._broadcast_to_report(report_id, {
            "type": "report_completed",
            "data": completion_data
        })
        
        logger.info(f"Report {report_id} marked as {'completed' if success else 'failed'}")
    
    async def send_error(self, report_id: str, error_type: str, error_message: str, 
                        error_details: Optional[Dict] = None):
        """Send error notification to clients"""
        
        error_data = {
            "report_id": report_id,
            "error_type": error_type,
            "error_message": error_message,
            "error_details": error_details or {},
            "timestamp": datetime.utcnow().isoformat()
        }
        
        await self._broadcast_to_report(report_id, {
            "type": "error",
            "data": error_data
        })
        
        logger.error(f"Error sent for report {report_id}: {error_type} - {error_message}")
    
    async def _broadcast_to_report(self, report_id: str, message: Dict):
        """Broadcast message to all WebSockets connected to a report"""
        if report_id not in self.active_connections:
            return
        
        disconnected = set()
        
        for websocket in self.active_connections[report_id].copy():
            try:
                await self._send_to_websocket(websocket, message)
            except WebSocketDisconnect:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error broadcasting to WebSocket: {str(e)}")
                disconnected.add(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected:
            await self.disconnect(websocket)
    
    async def _send_to_websocket(self, websocket: WebSocket, message: Dict):
        """Send message to a specific WebSocket with error handling"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Failed to send WebSocket message: {str(e)}")
            raise
    
    async def handle_websocket_message(self, websocket: WebSocket, message: Dict):
        """Handle incoming WebSocket messages from clients"""
        try:
            message_type = message.get("type")
            
            if message_type == "ping":
                # Update last ping time
                if websocket in self._connection_metadata:
                    self._connection_metadata[websocket]["last_ping"] = datetime.utcnow()
                
                await self._send_to_websocket(websocket, {
                    "type": "pong",
                    "data": {"timestamp": datetime.utcnow().isoformat()}
                })
            
            elif message_type == "get_progress":
                report_id = message.get("report_id")
                if report_id and report_id in self.report_progress:
                    await self._send_to_websocket(websocket, {
                        "type": "progress_update",
                        "data": self.report_progress[report_id]
                    })
            
        except Exception as e:
            logger.error(f"Error handling WebSocket message: {str(e)}")
    
    def get_report_progress(self, report_id: str) -> Optional[Dict]:
        """Get current progress for a report"""
        return self.report_progress.get(report_id)
    
    def get_active_connections_count(self, report_id: str) -> int:
        """Get number of active connections for a report"""
        return len(self.active_connections.get(report_id, set()))
    
    def cleanup_completed_reports(self, max_age_hours: int = 24):
        """Clean up progress data for old completed reports"""
        cutoff_time = datetime.utcnow().timestamp() - (max_age_hours * 3600)
        
        to_remove = []
        for report_id, progress in self.report_progress.items():
            if progress.get("completed") and "completion_data" in progress:
                completed_at = datetime.fromisoformat(
                    progress["completion_data"]["completed_at"].replace("Z", "+00:00")
                )
                if completed_at.timestamp() < cutoff_time:
                    to_remove.append(report_id)
        
        for report_id in to_remove:
            del self.report_progress[report_id]
            logger.info(f"Cleaned up old progress data for report {report_id}")

# Global instance
progress_manager = WebSocketProgressManager()