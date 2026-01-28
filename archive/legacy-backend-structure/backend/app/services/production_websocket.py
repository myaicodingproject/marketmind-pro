"""
MarketMind Pro Production WebSocket Manager
Real-time communication for report generation progress
"""

import asyncio
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections: client_id -> WebSocket
        self.active_connections: Dict[str, WebSocket] = {}
        # Connection metadata
        self.connection_info: Dict[str, Dict[str, Any]] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str):
        """Accept a new WebSocket connection"""
        try:
            await websocket.accept()
            self.active_connections[client_id] = websocket
            self.connection_info[client_id] = {
                "connected_at": datetime.now().isoformat(),
                "last_ping": datetime.now().isoformat(),
                "message_count": 0
            }
            
            logger.info(f"WebSocket client {client_id} connected")
            
            # Send welcome message
            await self.send_personal_message({
                "type": "connection",
                "status": "connected",
                "client_id": client_id,
                "timestamp": datetime.now().isoformat()
            }, client_id)
            
        except Exception as e:
            logger.error(f"Error connecting WebSocket client {client_id}: {e}")
            raise
    
    def disconnect(self, client_id: str):
        """Remove a WebSocket connection"""
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.connection_info:
            del self.connection_info[client_id]
        logger.info(f"WebSocket client {client_id} disconnected")
    
    async def send_personal_message(self, message: Dict[str, Any], client_id: str):
        """Send a message to a specific client"""
        if client_id not in self.active_connections:
            logger.warning(f"Attempted to send message to disconnected client {client_id}")
            return False
        
        try:
            websocket = self.active_connections[client_id]
            
            # Add metadata to message
            message.update({
                "timestamp": datetime.now().isoformat(),
                "client_id": client_id
            })
            
            await websocket.send_text(json.dumps(message))
            
            # Update connection info
            if client_id in self.connection_info:
                self.connection_info[client_id]["message_count"] += 1
                self.connection_info[client_id]["last_message"] = datetime.now().isoformat()
            
            return True
            
        except WebSocketDisconnect:
            logger.info(f"Client {client_id} disconnected during message send")
            self.disconnect(client_id)
            return False
        except Exception as e:
            logger.error(f"Error sending message to client {client_id}: {e}")
            self.disconnect(client_id)
            return False
    
    async def broadcast_to_client(self, client_id: str, message: Dict[str, Any]):
        """Broadcast a message to a specific client (alias for send_personal_message)"""
        return await self.send_personal_message(message, client_id)
    
    async def broadcast_to_all(self, message: Dict[str, Any]):
        """Broadcast a message to all connected clients"""
        if not self.active_connections:
            return
        
        message.update({
            "timestamp": datetime.now().isoformat(),
            "broadcast": True
        })
        
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(message))
                if client_id in self.connection_info:
                    self.connection_info[client_id]["message_count"] += 1
            except WebSocketDisconnect:
                disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Error broadcasting to client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def send_progress_update(self, client_id: str, progress: float, status: str, **kwargs):
        """Send a progress update to a specific client"""
        message = {
            "type": "progress",
            "progress": progress,
            "status": status,
            **kwargs
        }
        return await self.send_personal_message(message, client_id)
    
    async def send_error(self, client_id: str, error: str, **kwargs):
        """Send an error message to a specific client"""
        message = {
            "type": "error",
            "error": error,
            **kwargs
        }
        return await self.send_personal_message(message, client_id)
    
    async def send_completion(self, client_id: str, **kwargs):
        """Send a completion message to a specific client"""
        message = {
            "type": "completed",
            "status": "completed",
            **kwargs
        }
        return await self.send_personal_message(message, client_id)
    
    async def ping_all_clients(self):
        """Send ping to all clients to keep connections alive"""
        ping_message = {
            "type": "ping",
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected_clients = []
        
        for client_id, websocket in self.active_connections.items():
            try:
                await websocket.send_text(json.dumps(ping_message))
                if client_id in self.connection_info:
                    self.connection_info[client_id]["last_ping"] = datetime.now().isoformat()
            except WebSocketDisconnect:
                disconnected_clients.append(client_id)
            except Exception as e:
                logger.error(f"Error pinging client {client_id}: {e}")
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """Get statistics about current connections"""
        return {
            "total_connections": len(self.active_connections),
            "active_clients": list(self.active_connections.keys()),
            "connection_info": self.connection_info,
            "timestamp": datetime.now().isoformat()
        }
    
    def is_client_connected(self, client_id: str) -> bool:
        """Check if a client is currently connected"""
        return client_id in self.active_connections

# Global connection manager instance
websocket_manager = ConnectionManager()

class ReportProgressTracker:
    """Tracks and broadcasts report generation progress"""
    
    def __init__(self, manager: ConnectionManager):
        self.manager = manager
        self.active_reports: Dict[str, Dict[str, Any]] = {}
    
    async def start_report_tracking(self, report_id: str, ticker: str):
        """Start tracking a new report"""
        self.active_reports[report_id] = {
            "ticker": ticker,
            "started_at": datetime.now().isoformat(),
            "progress": 0.0,
            "status": "initializing",
            "current_section": None
        }
        
        await self.manager.send_progress_update(
            report_id,
            progress=0.0,
            status=f"Starting report generation for {ticker}",
            report_id=report_id,
            ticker=ticker
        )
    
    async def update_progress(self, report_id: str, progress: float, status: str, **kwargs):
        """Update report progress"""
        if report_id in self.active_reports:
            self.active_reports[report_id].update({
                "progress": progress,
                "status": status,
                "last_update": datetime.now().isoformat(),
                **kwargs
            })
        
        await self.manager.send_progress_update(
            report_id,
            progress=progress,
            status=status,
            report_id=report_id,
            **kwargs
        )
    
    async def complete_report(self, report_id: str, **kwargs):
        """Mark report as completed"""
        if report_id in self.active_reports:
            self.active_reports[report_id].update({
                "progress": 100.0,
                "status": "completed",
                "completed_at": datetime.now().isoformat()
            })
        
        await self.manager.send_completion(
            report_id,
            report_id=report_id,
            progress=100.0,
            **kwargs
        )
        
        # Clean up tracking after a delay
        asyncio.create_task(self._cleanup_report_tracking(report_id, delay=300))  # 5 minutes
    
    async def error_report(self, report_id: str, error: str, **kwargs):
        """Mark report as failed"""
        if report_id in self.active_reports:
            self.active_reports[report_id].update({
                "status": "failed",
                "error": error,
                "failed_at": datetime.now().isoformat()
            })
        
        await self.manager.send_error(
            report_id,
            error=error,
            report_id=report_id,
            **kwargs
        )
        
        # Clean up tracking after a delay
        asyncio.create_task(self._cleanup_report_tracking(report_id, delay=60))  # 1 minute
    
    async def _cleanup_report_tracking(self, report_id: str, delay: int = 300):
        """Clean up report tracking after delay"""
        await asyncio.sleep(delay)
        if report_id in self.active_reports:
            del self.active_reports[report_id]
            logger.info(f"Cleaned up tracking for report {report_id}")
    
    def get_report_status(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of a tracked report"""
        return self.active_reports.get(report_id)
    
    def get_all_active_reports(self) -> Dict[str, Dict[str, Any]]:
        """Get all currently tracked reports"""
        return self.active_reports.copy()

# Global progress tracker
progress_tracker = ReportProgressTracker(websocket_manager)

async def websocket_endpoint(websocket: WebSocket, client_id: str):
    """WebSocket endpoint handler"""
    await websocket_manager.connect(websocket, client_id)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_client_message(client_id, message)
            except json.JSONDecodeError:
                # Handle plain text messages
                await websocket_manager.send_personal_message({
                    "type": "echo",
                    "message": data,
                    "note": "Received plain text message"
                }, client_id)
            
    except WebSocketDisconnect:
        websocket_manager.disconnect(client_id)
        logger.info(f"Client {client_id} disconnected")
    except Exception as e:
        logger.error(f"WebSocket error for client {client_id}: {e}")
        websocket_manager.disconnect(client_id)

async def handle_client_message(client_id: str, message: Dict[str, Any]):
    """Handle incoming messages from WebSocket clients"""
    message_type = message.get("type", "unknown")
    
    if message_type == "ping":
        # Respond to ping
        await websocket_manager.send_personal_message({
            "type": "pong",
            "timestamp": datetime.now().isoformat()
        }, client_id)
    
    elif message_type == "subscribe_report":
        # Subscribe to report updates
        report_id = message.get("report_id")
        if report_id:
            status = progress_tracker.get_report_status(report_id)
            await websocket_manager.send_personal_message({
                "type": "report_status",
                "report_id": report_id,
                "status": status
            }, client_id)
    
    elif message_type == "get_stats":
        # Send connection statistics
        stats = websocket_manager.get_connection_stats()
        await websocket_manager.send_personal_message({
            "type": "stats",
            "data": stats
        }, client_id)
    
    else:
        # Echo unknown messages
        await websocket_manager.send_personal_message({
            "type": "echo",
            "original_message": message,
            "note": f"Unknown message type: {message_type}"
        }, client_id)

# Background task for connection maintenance
async def connection_maintenance():
    """Background task to maintain WebSocket connections"""
    while True:
        try:
            await websocket_manager.ping_all_clients()
            await asyncio.sleep(30)  # Ping every 30 seconds
        except Exception as e:
            logger.error(f"Connection maintenance error: {e}")
            await asyncio.sleep(60)  # Wait longer on error

# Start maintenance task
asyncio.create_task(connection_maintenance())