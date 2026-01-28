# WebSocket Manager for Real-time Queue Progress Updates

import asyncio
import json
import logging
from typing import Dict, Set
from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

logger = logging.getLogger(__name__)

class WebSocketManager:
    """Manages WebSocket connections for real-time progress updates"""
    
    def __init__(self, redis_url: str):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.redis = redis.from_url(redis_url)
        self.pubsub = None
        self._listening = False
    
    async def connect(self, websocket: WebSocket, job_id: str):
        """Connect a WebSocket to a specific job"""
        await websocket.accept()
        
        if job_id not in self.active_connections:
            self.active_connections[job_id] = set()
        
        self.active_connections[job_id].add(websocket)
        
        # Start Redis listener if not already running
        if not self._listening:
            asyncio.create_task(self._listen_for_updates())
        
        logger.info(f"WebSocket connected for job {job_id}")
    
    async def disconnect(self, websocket: WebSocket, job_id: str):
        """Disconnect a WebSocket from a job"""
        if job_id in self.active_connections:
            self.active_connections[job_id].discard(websocket)
            
            # Clean up empty job connections
            if not self.active_connections[job_id]:
                del self.active_connections[job_id]
        
        logger.info(f"WebSocket disconnected from job {job_id}")
    
    async def _listen_for_updates(self):
        """Listen for Redis pub/sub messages and broadcast to WebSockets"""
        self._listening = True
        self.pubsub = self.redis.pubsub()
        
        # Subscribe to all progress channels
        await self.pubsub.psubscribe("progress:*")
        
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "pmessage":
                    channel = message["channel"].decode()
                    job_id = channel.split(":")[-1]
                    data = json.loads(message["data"])
                    
                    await self._broadcast_to_job(job_id, data)
        
        except Exception as e:
            logger.error(f"Error in WebSocket listener: {str(e)}")
        finally:
            self._listening = False
            if self.pubsub:
                await self.pubsub.unsubscribe()
    
    async def _broadcast_to_job(self, job_id: str, data: Dict):
        """Broadcast update to all WebSockets connected to a job"""
        if job_id not in self.active_connections:
            return
        
        disconnected = set()
        
        for websocket in self.active_connections[job_id].copy():
            try:
                await websocket.send_json(data)
            except WebSocketDisconnect:
                disconnected.add(websocket)
            except Exception as e:
                logger.error(f"Error sending WebSocket message: {str(e)}")
                disconnected.add(websocket)
        
        # Clean up disconnected WebSockets
        for websocket in disconnected:
            self.active_connections[job_id].discard(websocket)
    
    async def send_direct_message(self, job_id: str, message: Dict):
        """Send a direct message to all WebSockets for a job"""
        await self._broadcast_to_job(job_id, message)

# Global WebSocket manager instance
websocket_manager = WebSocketManager("redis://localhost:6379/0")