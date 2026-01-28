"""
WebSocket Manager for Real-time Progress Tracking
Handles WebSocket connections and progress updates for report generation
"""

import asyncio
import json
import logging
from typing import Dict, Set, Any, Optional
from datetime import datetime
import uuid

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        # Active connections by connection ID
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Subscriptions: report_id -> set of connection_ids
        self.subscriptions: Dict[str, Set[str]] = {}
        
        # Connection metadata
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: Optional[str] = None) -> str:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        connection_id = str(uuid.uuid4())
        self.active_connections[connection_id] = websocket
        
        self.connection_metadata[connection_id] = {
            'user_id': user_id,
            'connected_at': datetime.now(),
            'subscriptions': set()
        }
        
        logger.info(f"WebSocket connected: {connection_id} (User: {user_id})")
        
        # Send connection confirmation
        await self._send_to_connection(connection_id, {
            'type': 'connection_established',
            'connection_id': connection_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return connection_id
    
    def disconnect(self, connection_id: str):
        """Remove a WebSocket connection"""
        if connection_id in self.active_connections:
            # Remove from all subscriptions
            for report_id in list(self.subscriptions.keys()):
                self.subscriptions[report_id].discard(connection_id)
                if not self.subscriptions[report_id]:
                    del self.subscriptions[report_id]
            
            # Clean up connection data
            del self.active_connections[connection_id]
            if connection_id in self.connection_metadata:
                del self.connection_metadata[connection_id]
            
            logger.info(f"WebSocket disconnected: {connection_id}")
    
    async def subscribe_to_report(self, connection_id: str, report_id: str):
        """Subscribe a connection to report updates"""
        if connection_id not in self.active_connections:
            return False
        
        if report_id not in self.subscriptions:
            self.subscriptions[report_id] = set()
        
        self.subscriptions[report_id].add(connection_id)
        self.connection_metadata[connection_id]['subscriptions'].add(report_id)
        
        logger.info(f"Connection {connection_id} subscribed to report {report_id}")
        
        # Send subscription confirmation
        await self._send_to_connection(connection_id, {
            'type': 'subscription_confirmed',
            'report_id': report_id,
            'timestamp': datetime.now().isoformat()
        })
        
        return True
    
    async def unsubscribe_from_report(self, connection_id: str, report_id: str):
        """Unsubscribe a connection from report updates"""
        if report_id in self.subscriptions:
            self.subscriptions[report_id].discard(connection_id)
            if not self.subscriptions[report_id]:
                del self.subscriptions[report_id]
        
        if connection_id in self.connection_metadata:
            self.connection_metadata[connection_id]['subscriptions'].discard(report_id)
        
        logger.info(f"Connection {connection_id} unsubscribed from report {report_id}")
    
    async def send_progress_update(self, report_id: str, progress_data: Dict[str, Any]):
        """Send progress update to all subscribers of a report"""
        if report_id not in self.subscriptions:
            return
        
        message = {
            'type': 'progress_update',
            'report_id': report_id,
            'data': progress_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all subscribers
        disconnected_connections = []
        for connection_id in self.subscriptions[report_id].copy():
            success = await self._send_to_connection(connection_id, message)
            if not success:
                disconnected_connections.append(connection_id)
        
        # Clean up disconnected connections
        for connection_id in disconnected_connections:
            self.disconnect(connection_id)
    
    async def send_report_completed(self, report_id: str, report_data: Dict[str, Any]):
        """Send report completion notification"""
        if report_id not in self.subscriptions:
            return
        
        message = {
            'type': 'report_completed',
            'report_id': report_id,
            'data': report_data,
            'timestamp': datetime.now().isoformat()
        }
        
        # Send to all subscribers
        for connection_id in self.subscriptions[report_id].copy():
            await self._send_to_connection(connection_id, message)
    
    async def send_error(self, report_id: str, error_data: Dict[str, Any]):
        """Send error notification to report subscribers"""
        if report_id not in self.subscriptions:
            return
        
        message = {
            'type': 'error',
            'report_id': report_id,
            'data': error_data,
            'timestamp': datetime.now().isoformat()
        }
        
        for connection_id in self.subscriptions[report_id].copy():
            await self._send_to_connection(connection_id, message)
    
    async def _send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send message to a specific connection"""
        if connection_id not in self.active_connections:
            return False
        
        try:
            websocket = self.active_connections[connection_id]
            await websocket.send_text(json.dumps(message))
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to connection {connection_id}: {str(e)}")
            return False
    
    def get_connection_count(self) -> int:
        """Get total number of active connections"""
        return len(self.active_connections)
    
    def get_subscription_count(self, report_id: str) -> int:
        """Get number of subscribers for a specific report"""
        return len(self.subscriptions.get(report_id, set()))
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics"""
        return {
            'active_connections': len(self.active_connections),
            'active_subscriptions': len(self.subscriptions),
            'total_subscribers': sum(len(subs) for subs in self.subscriptions.values()),
            'reports_being_tracked': list(self.subscriptions.keys())
        }

class WebSocketManager:
    """High-level WebSocket manager with additional features"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
    
    async def handle_websocket_connection(self, websocket: WebSocket, user_id: Optional[str] = None):
        """Handle a complete WebSocket connection lifecycle"""
        connection_id = None
        
        try:
            connection_id = await self.connection_manager.connect(websocket, user_id)
            
            # Listen for messages
            while True:
                try:
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    await self._handle_client_message(connection_id, message)
                    
                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    await self._send_error_to_connection(
                        connection_id, 
                        "Invalid JSON message format"
                    )
                except Exception as e:
                    logger.error(f"Error handling WebSocket message: {str(e)}")
                    await self._send_error_to_connection(
                        connection_id,
                        f"Message processing error: {str(e)}"
                    )
        
        except WebSocketDisconnect:
            pass
        except Exception as e:
            logger.error(f"WebSocket connection error: {str(e)}")
        
        finally:
            if connection_id:
                self.connection_manager.disconnect(connection_id)
    
    async def _handle_client_message(self, connection_id: str, message: Dict[str, Any]):
        """Handle incoming client messages"""
        message_type = message.get('type')
        
        if message_type == 'subscribe':
            report_id = message.get('report_id')
            if report_id:
                await self.connection_manager.subscribe_to_report(connection_id, report_id)
            else:
                await self._send_error_to_connection(connection_id, "Missing report_id for subscription")
        
        elif message_type == 'unsubscribe':
            report_id = message.get('report_id')
            if report_id:
                await self.connection_manager.unsubscribe_from_report(connection_id, report_id)
        
        elif message_type == 'ping':
            await self.connection_manager._send_to_connection(connection_id, {
                'type': 'pong',
                'timestamp': datetime.now().isoformat()
            })
        
        else:
            await self._send_error_to_connection(
                connection_id, 
                f"Unknown message type: {message_type}"
            )
    
    async def _send_error_to_connection(self, connection_id: str, error_message: str):
        """Send error message to a specific connection"""
        await self.connection_manager._send_to_connection(connection_id, {
            'type': 'error',
            'message': error_message,
            'timestamp': datetime.now().isoformat()
        })
    
    # Delegate methods to connection manager
    async def send_progress_update(self, report_id: str, progress_data: Dict[str, Any]):
        """Send progress update to report subscribers"""
        await self.connection_manager.send_progress_update(report_id, progress_data)
    
    async def send_report_completed(self, report_id: str, report_data: Dict[str, Any]):
        """Send report completion notification"""
        await self.connection_manager.send_report_completed(report_id, report_data)
    
    async def send_error(self, report_id: str, error_data: Dict[str, Any]):
        """Send error notification"""
        await self.connection_manager.send_error(report_id, error_data)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get WebSocket statistics"""
        return self.connection_manager.get_stats()

# Global instance
websocket_manager = WebSocketManager()