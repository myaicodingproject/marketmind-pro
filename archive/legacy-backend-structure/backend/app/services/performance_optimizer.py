# C5: Performance Optimization - System-wide Performance

import asyncio
import aioredis
from functools import wraps
import time
import logging
from typing import Dict, Any, Optional
import psutil
import gc

class PerformanceOptimizer:
    def __init__(self):
        self.metrics = {}
        self.cache = {}
        self.connection_pools = {}
        
    async def initialize(self):
        """Initialize performance optimization systems"""
        await self._setup_connection_pools()
        await self._setup_caching()
        self._setup_monitoring()
    
    async def _setup_connection_pools(self):
        """Setup optimized connection pools"""
        # Redis connection pool
        self.connection_pools['redis'] = aioredis.ConnectionPool.from_url(
            "redis://localhost:6379",
            max_connections=50,
            retry_on_timeout=True
        )
        
        # Database connection pool optimization
        from sqlalchemy.pool import QueuePool
        self.connection_pools['db'] = QueuePool(
            creator=self._create_db_connection,
            pool_size=20,
            max_overflow=30,
            pool_recycle=3600,
            pool_pre_ping=True
        )
    
    def _create_db_connection(self):
        """Create optimized database connection"""
        import psycopg2
        return psycopg2.connect(
            host="localhost",
            database="marketmind_pro",
            user="postgres",
            password="password",
            connect_timeout=10
        )
    
    async def _setup_caching(self):
        """Setup multi-level caching"""
        # Memory cache for frequently accessed data
        self.cache['memory'] = {}
        
        # Redis cache for shared data
        self.cache['redis'] = aioredis.Redis(
            connection_pool=self.connection_pools['redis']
        )
    
    def _setup_monitoring(self):
        """Setup performance monitoring"""
        self.metrics = {
            'request_times': [],
            'memory_usage': [],
            'cpu_usage': [],
            'active_connections': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }

# Caching decorators
def cache_result(ttl: int = 300, key_prefix: str = ""):
    """Cache function results with TTL"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{key_prefix}:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            cached = await get_cached_result(cache_key)
            if cached:
                return cached
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await set_cached_result(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator

async def get_cached_result(key: str) -> Optional[Any]:
    """Get result from cache"""
    try:
        # Try memory cache first
        if key in performance_optimizer.cache['memory']:
            return performance_optimizer.cache['memory'][key]
        
        # Try Redis cache
        cached = await performance_optimizer.cache['redis'].get(key)
        if cached:
            import json
            result = json.loads(cached)
            # Store in memory cache for faster access
            performance_optimizer.cache['memory'][key] = result
            performance_optimizer.metrics['cache_hits'] += 1
            return result
        
        performance_optimizer.metrics['cache_misses'] += 1
        return None
    except Exception as e:
        logging.error(f"Cache get error: {e}")
        return None

async def set_cached_result(key: str, value: Any, ttl: int):
    """Set result in cache"""
    try:
        import json
        
        # Store in memory cache
        performance_optimizer.cache['memory'][key] = value
        
        # Store in Redis cache
        await performance_optimizer.cache['redis'].setex(
            key, ttl, json.dumps(value, default=str)
        )
    except Exception as e:
        logging.error(f"Cache set error: {e}")

# Database query optimization
class QueryOptimizer:
    @staticmethod
    def optimize_query(query: str) -> str:
        """Optimize SQL queries"""
        # Add LIMIT if not present for large result sets
        if "SELECT" in query.upper() and "LIMIT" not in query.upper():
            query += " LIMIT 1000"
        
        # Add indexes hints for common patterns
        if "WHERE ticker =" in query:
            query = query.replace("FROM companies", "FROM companies USE INDEX (idx_ticker)")
        
        return query
    
    @staticmethod
    async def execute_optimized_query(query: str, params: tuple = None):
        """Execute query with optimization"""
        optimized_query = QueryOptimizer.optimize_query(query)
        
        # Use connection pool
        async with performance_optimizer.connection_pools['db'].connect() as conn:
            return await conn.execute(optimized_query, params)

# Kiro CLI optimization
class KiroOptimizer:
    def __init__(self):
        self.process_pool = []
        self.max_concurrent = 10
    
    async def optimize_kiro_execution(self, prompts: list) -> list:
        """Optimize Kiro CLI execution with batching and concurrency"""
        
        # Batch prompts for efficiency
        batched_prompts = self._batch_prompts(prompts)
        
        # Execute with controlled concurrency
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def execute_batch(batch):
            async with semaphore:
                return await self._execute_kiro_batch(batch)
        
        tasks = [execute_batch(batch) for batch in batched_prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return [r for r in results if not isinstance(r, Exception)]
    
    def _batch_prompts(self, prompts: list, batch_size: int = 3) -> list:
        """Batch prompts for efficient processing"""
        batches = []
        for i in range(0, len(prompts), batch_size):
            batches.append(prompts[i:i + batch_size])
        return batches
    
    async def _execute_kiro_batch(self, batch: list) -> dict:
        """Execute batch of Kiro prompts"""
        import subprocess
        
        # Combine prompts for single Kiro execution
        combined_prompt = "\n\n".join([p['prompt'] for p in batch])
        
        process = await asyncio.create_subprocess_exec(
            'kiro-cli', 'chat',
            '--prompt', combined_prompt,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {'success': True, 'output': stdout.decode()}
        else:
            return {'success': False, 'error': stderr.decode()}

# Memory management
class MemoryManager:
    @staticmethod
    def cleanup_memory():
        """Cleanup memory and garbage collection"""
        # Clear memory cache if too large
        if len(performance_optimizer.cache['memory']) > 1000:
            # Keep only most recent 500 items
            items = list(performance_optimizer.cache['memory'].items())
            performance_optimizer.cache['memory'] = dict(items[-500:])
        
        # Force garbage collection
        gc.collect()
    
    @staticmethod
    def get_memory_usage() -> dict:
        """Get current memory usage"""
        process = psutil.Process()
        return {
            'memory_percent': process.memory_percent(),
            'memory_info': process.memory_info()._asdict(),
            'system_memory': psutil.virtual_memory()._asdict()
        }

# Request optimization middleware
class RequestOptimizer:
    def __init__(self):
        self.request_queue = asyncio.Queue(maxsize=100)
        self.processing = False
    
    async def optimize_request(self, request_func, *args, **kwargs):
        """Optimize request processing with queuing"""
        if self.request_queue.full():
            raise Exception("Request queue full, please try again later")
        
        await self.request_queue.put((request_func, args, kwargs))
        
        if not self.processing:
            asyncio.create_task(self._process_queue())
        
        return await self._wait_for_result(request_func, args, kwargs)
    
    async def _process_queue(self):
        """Process request queue"""
        self.processing = True
        
        while not self.request_queue.empty():
            try:
                request_func, args, kwargs = await self.request_queue.get()
                await request_func(*args, **kwargs)
                self.request_queue.task_done()
            except Exception as e:
                logging.error(f"Request processing error: {e}")
        
        self.processing = False
    
    async def _wait_for_result(self, request_func, args, kwargs):
        """Wait for request result"""
        # Implementation depends on specific use case
        pass

# Performance monitoring
class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
    
    async def log_performance_metrics(self):
        """Log current performance metrics"""
        metrics = {
            'uptime': time.time() - self.start_time,
            'memory': MemoryManager.get_memory_usage(),
            'cpu_percent': psutil.cpu_percent(),
            'active_connections': performance_optimizer.metrics['active_connections'],
            'cache_hit_rate': self._calculate_cache_hit_rate(),
            'avg_request_time': self._calculate_avg_request_time()
        }
        
        logging.info(f"Performance metrics: {metrics}")
        return metrics
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        hits = performance_optimizer.metrics['cache_hits']
        misses = performance_optimizer.metrics['cache_misses']
        total = hits + misses
        
        return (hits / total * 100) if total > 0 else 0
    
    def _calculate_avg_request_time(self) -> float:
        """Calculate average request time"""
        times = performance_optimizer.metrics['request_times']
        return sum(times) / len(times) if times else 0

# Initialize global optimizer
performance_optimizer = PerformanceOptimizer()
kiro_optimizer = KiroOptimizer()
memory_manager = MemoryManager()
request_optimizer = RequestOptimizer()
performance_monitor = PerformanceMonitor()

# FastAPI middleware for performance
from fastapi import Request, Response
import time

async def performance_middleware(request: Request, call_next):
    """Performance monitoring middleware"""
    start_time = time.time()
    
    # Track active connections
    performance_optimizer.metrics['active_connections'] += 1
    
    try:
        response = await call_next(request)
        
        # Log request time
        request_time = time.time() - start_time
        performance_optimizer.metrics['request_times'].append(request_time)
        
        # Keep only last 1000 request times
        if len(performance_optimizer.metrics['request_times']) > 1000:
            performance_optimizer.metrics['request_times'] = \
                performance_optimizer.metrics['request_times'][-1000:]
        
        # Add performance headers
        response.headers["X-Response-Time"] = str(request_time)
        
        return response
    
    finally:
        performance_optimizer.metrics['active_connections'] -= 1
        
        # Periodic cleanup
        if int(time.time()) % 300 == 0:  # Every 5 minutes
            memory_manager.cleanup_memory()

# Usage examples
@cache_result(ttl=600, key_prefix="stock_data")
async def get_stock_data(ticker: str):
    """Cached stock data retrieval"""
    # Expensive API call
    pass

async def generate_optimized_report(ticker: str):
    """Generate report with all optimizations"""
    # Use optimized Kiro execution
    prompts = [
        {'prompt': f'Analyze {ticker} executive summary'},
        {'prompt': f'Analyze {ticker} financials'},
        {'prompt': f'Analyze {ticker} valuation'}
    ]
    
    results = await kiro_optimizer.optimize_kiro_execution(prompts)
    return results