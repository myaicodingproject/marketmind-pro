"""
WebSocket Real-time Progress Updates
Provides live progress tracking during report generation
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import uuid

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time progress updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.progress_subscriptions: Dict[str, Set[str]] = {}  # report_id -> set of connection_ids
    
    async def connect(self, websocket: WebSocket) -> str:
        """Accept new WebSocket connection"""
        await websocket.accept()
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection_established",
            "connection_id": connection_id,
            "timestamp": datetime.now().isoformat(),
            "message": "Connected to MarketMind Pro real-time updates"
        }, connection_id)
        
        logger.info(f"WebSocket connection established: {connection_id}")
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove WebSocket connection"""
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from all subscriptions
        for report_id in list(self.progress_subscriptions.keys()):
            if connection_id in self.progress_subscriptions[report_id]:
                self.progress_subscriptions[report_id].remove(connection_id)
                if not self.progress_subscriptions[report_id]:
                    del self.progress_subscriptions[report_id]
        
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def send_personal_message(self, message: Dict[str, Any], connection_id: str):
        """Send message to specific connection"""
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending message to {connection_id}: {str(e)}")
                self.disconnect(connection_id)
    
    async def subscribe_to_report(self, connection_id: str, report_id: str):
        """Subscribe connection to report progress updates"""
        if report_id not in self.progress_subscriptions:
            self.progress_subscriptions[report_id] = set()
        
        self.progress_subscriptions[report_id].add(connection_id)
        
        await self.send_personal_message({
            "type": "subscription_confirmed",
            "report_id": report_id,
            "message": f"Subscribed to progress updates for {report_id}"
        }, connection_id)
        
        logger.info(f"Connection {connection_id} subscribed to report {report_id}")
    
    async def broadcast_progress(self, report_id: str, progress_data: Dict[str, Any]):
        """Broadcast progress update to all subscribers"""
        if report_id not in self.progress_subscriptions:
            return
        
        message = {
            "type": "progress_update",
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            **progress_data
        }
        
        # Send to all subscribers
        disconnected_connections = []
        for connection_id in self.progress_subscriptions[report_id]:
            try:
                if connection_id in self.active_connections:
                    websocket = self.active_connections[connection_id]
                    await websocket.send_text(json.dumps(message))
                else:
                    disconnected_connections.append(connection_id)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {str(e)}")
                disconnected_connections.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            self.progress_subscriptions[report_id].discard(connection_id)
    
    async def send_error(self, report_id: str, error_data: Dict[str, Any]):
        """Send error message to report subscribers"""
        if report_id not in self.progress_subscriptions:
            return
        
        message = {
            "type": "error",
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            **error_data
        }
        
        for connection_id in self.progress_subscriptions[report_id]:
            await self.send_personal_message(message, connection_id)
    
    async def send_completion(self, report_id: str, completion_data: Dict[str, Any]):
        """Send completion message to report subscribers"""
        if report_id not in self.progress_subscriptions:
            return
        
        message = {
            "type": "report_completed",
            "report_id": report_id,
            "timestamp": datetime.now().isoformat(),
            **completion_data
        }
        
        for connection_id in self.progress_subscriptions[report_id]:
            await self.send_personal_message(message, connection_id)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get WebSocket connection statistics"""
        return {
            "active_connections": len(self.active_connections),
            "active_subscriptions": len(self.progress_subscriptions),
            "total_subscribers": sum(len(subs) for subs in self.progress_subscriptions.values())
        }

# Global WebSocket manager instance
websocket_manager = WebSocketManager()

class ProgressTracker:
    """Enhanced progress tracker with WebSocket integration"""
    
    def __init__(self, report_id: str):
        self.report_id = report_id
        self.start_time = datetime.now()
        self.current_stage = "initializing"
        self.progress = 0
        self.completed_sections = []
        self.errors = []
    
    async def update_progress(self, stage: str, progress: int, details: Dict[str, Any] = None):
        """Update progress and broadcast to WebSocket subscribers"""
        self.current_stage = stage
        self.progress = progress
        
        progress_data = {
            "stage": stage,
            "progress": progress,
            "elapsed_time": (datetime.now() - self.start_time).total_seconds(),
            "completed_sections": self.completed_sections,
            "details": details or {}
        }
        
        # Broadcast to WebSocket subscribers
        await websocket_manager.broadcast_progress(self.report_id, progress_data)
        
        logger.info(f"Progress update for {self.report_id}: {stage} - {progress}%")
    
    async def section_completed(self, section_id: str, section_data: Dict[str, Any]):
        """Mark section as completed"""
        self.completed_sections.append(section_id)
        
        await self.update_progress(
            f"completed_{section_id}",
            10 + len(self.completed_sections) * 7,  # Rough progress calculation
            {
                "completed_section": section_id,
                "section_quality_score": section_data.get('quality_score', 0),
                "total_completed": len(self.completed_sections),
                "remaining_sections": 8 - len(self.completed_sections)
            }
        )
    
    async def quality_validation_started(self):
        """Mark quality validation as started"""
        await self.update_progress("quality_validation", 70, {
            "validation_stage": "starting",
            "sections_to_validate": len(self.completed_sections)
        })
    
    async def quality_validation_completed(self, quality_result: Dict[str, Any]):
        """Mark quality validation as completed"""
        await self.update_progress("quality_validation_completed", 85, {
            "validation_stage": "completed",
            "overall_quality_score": quality_result.get('overall_score', 0),
            "quality_passed": quality_result.get('overall_passed', False),
            "issues_found": len(quality_result.get('issues', []))
        })
    
    async def report_completed(self, final_report: Dict[str, Any]):
        """Mark report as completed"""
        completion_data = {
            "stage": "completed",
            "progress": 100,
            "total_time": (datetime.now() - self.start_time).total_seconds(),
            "report_statistics": final_report.get('statistics', {}),
            "quality_score": final_report.get('quality_score', 0),
            "download_ready": True
        }
        
        await websocket_manager.send_completion(self.report_id, completion_data)
        logger.info(f"Report completed: {self.report_id}")
    
    async def report_error(self, error_message: str, error_details: Dict[str, Any] = None):
        """Report error during generation"""
        self.errors.append(error_message)
        
        error_data = {
            "stage": "error",
            "error_message": error_message,
            "error_details": error_details or {},
            "elapsed_time": (datetime.now() - self.start_time).total_seconds()
        }
        
        await websocket_manager.send_error(self.report_id, error_data)
        logger.error(f"Report error for {self.report_id}: {error_message}")

# WebSocket endpoint handlers
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint for real-time updates"""
    connection_id = await websocket_manager.connect(websocket)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message.get("type") == "subscribe":
                report_id = message.get("report_id")
                if report_id:
                    await websocket_manager.subscribe_to_report(connection_id, report_id)
            
            elif message.get("type") == "ping":
                await websocket_manager.send_personal_message({
                    "type": "pong",
                    "timestamp": datetime.now().isoformat()
                }, connection_id)
            
            elif message.get("type") == "get_stats":
                stats = websocket_manager.get_connection_stats()
                await websocket_manager.send_personal_message({
                    "type": "stats",
                    "data": stats
                }, connection_id)
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(connection_id)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        websocket_manager.disconnect(connection_id)
