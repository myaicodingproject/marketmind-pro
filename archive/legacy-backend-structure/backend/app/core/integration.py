# A4: Core Integration Engine

from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
import asyncio
from typing import Dict, Any
import logging

class IntegrationEngine:
    def __init__(self):
        self.services = {}
        self.health_checks = {}
    
    async def register_service(self, name: str, service: Any):
        self.services[name] = service
        self.health_checks[name] = True
    
    async def orchestrate_report_generation(self, ticker: str, user_id: str) -> str:
        """Orchestrate full report generation pipeline"""
        try:
            # 1. Queue report
            queue_id = await self.services['queue'].enqueue_report(ticker, user_id)
            
            # 2. Prepare RAG context
            context = await self.services['rag'].prepare_context(ticker)
            
            # 3. Execute Kiro processing
            await self.services['kiro'].process_with_context(ticker, context, queue_id)
            
            return queue_id
        except Exception as e:
            logging.error(f"Orchestration failed: {e}")
            raise HTTPException(status_code=500, detail="Generation failed")

# API Gateway
class APIGateway:
    def __init__(self, integration_engine: IntegrationEngine):
        self.engine = integration_engine
    
    async def route_request(self, endpoint: str, data: Dict[str, Any]):
        """Route requests to appropriate services"""
        if endpoint.startswith('/reports'):
            return await self.engine.orchestrate_report_generation(**data)
        elif endpoint.startswith('/search'):
            return await self.engine.services['search'].execute(data)
        else:
            raise HTTPException(status_code=404, detail="Endpoint not found")

# Health monitoring
async def health_check():
    return {"status": "healthy", "services": ["queue", "rag", "kiro", "database"]}