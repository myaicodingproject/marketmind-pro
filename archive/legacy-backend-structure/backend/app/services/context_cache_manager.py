"""
Context Caching Manager - Session A4.5
High-performance caching system for RAG context optimization
"""

import asyncio
import json
import hashlib
import time
import pickle
import gzip
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from pathlib import Path
import redis
import logging
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

@dataclass
class CacheEntry:
    key: str
    data: Any
    created_at: datetime
    expires_at: datetime
    access_count: int
    last_accessed: datetime
    size_bytes: int
    quality_score: float
    ticker: str
    analysis_type: str

@dataclass
class CacheStats:
    total_entries: int
    total_size_mb: float
    hit_rate: float
    miss_rate: float
    avg_retrieval_time_ms: float
    memory_usage_percent: float
    expired_entries: int

class ContextCacheManager:
    """High-performance caching system for RAG contexts"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/1",
                 max_memory_mb: int = 512,
                 default_ttl_hours: int = 24):
        
        # Redis connection
        self.redis_client = redis.from_url(redis_url, decode_responses=False)
        
        # Cache configuration
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.default_ttl = timedelta(hours=default_ttl_hours)
        
        # Performance tracking
        self.cache_hits = 0
        self.cache_misses = 0
        self.retrieval_times = []
        
        # Thread pool for async operations
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # Cache key prefixes
        self.prefixes = {
            'context': 'rag_context:',
            'metadata': 'cache_meta:',
            'stats': 'cache_stats:',
            'index': 'cache_index:'
        }
        
        logger.info("Context Cache Manager initialized")
    
    def _generate_cache_key(self, ticker: str, analysis_type: str, 
                          context_config: Dict[str, Any]) -> str:
        """Generate unique cache key for context"""
        
        # Create deterministic hash from configuration
        config_str = json.dumps(context_config, sort_keys=True)
        config_hash = hashlib.md5(config_str.encode()).hexdigest()[:8]
        
        return f"{self.prefixes['context']}{ticker}:{analysis_type}:{config_hash}"
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data for storage efficiency"""
        try:
            # Serialize and compress
            serialized = pickle.dumps(data)
            compressed = gzip.compress(serialized)
            return compressed
        except Exception as e:
            logger.error(f"Data compression failed: {e}")
            raise
    
    def _decompress_data(self, compressed_data: bytes) -> Any:
        """Decompress data from storage"""
        try:
            # Decompress and deserialize
            decompressed = gzip.decompress(compressed_data)
            data = pickle.loads(decompressed)
            return data
        except Exception as e:
            logger.error(f"Data decompression failed: {e}")
            raise
    
    async def get_context(self, ticker: str, analysis_type: str,
                         context_config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Retrieve context from cache"""
        
        start_time = time.time()
        cache_key = self._generate_cache_key(ticker, analysis_type, context_config)
        
        try:
            # Get from Redis
            loop = asyncio.get_event_loop()
            compressed_data = await loop.run_in_executor(
                self.executor,
                self.redis_client.get,
                cache_key
            )
            
            if compressed_data is None:
                self.cache_misses += 1
                logger.debug(f"Cache miss for {ticker} {analysis_type}")
                return None
            
            # Decompress data
            context_data = await loop.run_in_executor(
                self.executor,
                self._decompress_data,
                compressed_data
            )
            
            # Update access metadata
            await self._update_access_metadata(cache_key, ticker, analysis_type)
            
            self.cache_hits += 1
            retrieval_time = (time.time() - start_time) * 1000
            self.retrieval_times.append(retrieval_time)
            
            logger.info(f"Cache hit for {ticker} {analysis_type} ({retrieval_time:.2f}ms)")
            
            return context_data
            
        except Exception as e:
            logger.error(f"Cache retrieval failed for {cache_key}: {e}")
            self.cache_misses += 1
            return None
    
    async def store_context(self, ticker: str, analysis_type: str,
                          context_config: Dict[str, Any],
                          context_data: Dict[str, Any],
                          quality_score: float = 1.0,
                          custom_ttl: Optional[timedelta] = None) -> bool:
        """Store context in cache"""
        
        cache_key = self._generate_cache_key(ticker, analysis_type, context_config)
        ttl = custom_ttl or self.default_ttl
        
        try:
            # Compress data
            loop = asyncio.get_event_loop()
            compressed_data = await loop.run_in_executor(
                self.executor,
                self._compress_data,
                context_data
            )
            
            # Calculate size
            size_bytes = len(compressed_data)
            
            # Check memory limits
            if not await self._check_memory_limits(size_bytes):
                await self._evict_entries()
            
            # Store in Redis with TTL
            ttl_seconds = int(ttl.total_seconds())
            await loop.run_in_executor(
                self.executor,
                lambda: self.redis_client.setex(cache_key, ttl_seconds, compressed_data)
            )
            
            # Store metadata
            await self._store_metadata(
                cache_key, ticker, analysis_type, size_bytes, quality_score, ttl
            )
            
            logger.info(f"Cached context for {ticker} {analysis_type} ({size_bytes} bytes)")
            
            return True
            
        except Exception as e:
            logger.error(f"Cache storage failed for {cache_key}: {e}")
            return False
    
    async def _update_access_metadata(self, cache_key: str, ticker: str, 
                                    analysis_type: str):
        """Update access metadata for cache entry"""
        
        metadata_key = f"{self.prefixes['metadata']}{cache_key}"
        
        try:
            # Get existing metadata
            loop = asyncio.get_event_loop()
            metadata_json = await loop.run_in_executor(
                self.executor,
                self.redis_client.get,
                metadata_key
            )
            
            if metadata_json:
                metadata = json.loads(metadata_json.decode())
                metadata['access_count'] += 1
                metadata['last_accessed'] = datetime.now().isoformat()
                
                # Store updated metadata
                await loop.run_in_executor(
                    self.executor,
                    lambda: self.redis_client.set(
                        metadata_key,
                        json.dumps(metadata).encode()
                    )
                )
                
        except Exception as e:
            logger.warning(f"Failed to update access metadata for {cache_key}: {e}")
    
    async def _store_metadata(self, cache_key: str, ticker: str, analysis_type: str,
                            size_bytes: int, quality_score: float, ttl: timedelta):
        """Store cache entry metadata"""
        
        metadata_key = f"{self.prefixes['metadata']}{cache_key}"
        now = datetime.now()
        
        metadata = {
            'key': cache_key,
            'ticker': ticker,
            'analysis_type': analysis_type,
            'created_at': now.isoformat(),
            'expires_at': (now + ttl).isoformat(),
            'access_count': 1,
            'last_accessed': now.isoformat(),
            'size_bytes': size_bytes,
            'quality_score': quality_score
        }
        
        try:
            loop = asyncio.get_event_loop()
            
            # Store metadata with same TTL as data
            ttl_seconds = int(ttl.total_seconds())
            await loop.run_in_executor(
                self.executor,
                lambda: self.redis_client.setex(
                    metadata_key,
                    ttl_seconds,
                    json.dumps(metadata).encode()
                )
            )
            
            # Add to index for management
            index_key = f"{self.prefixes['index']}{ticker}"
            await loop.run_in_executor(
                self.executor,
                lambda: self.redis_client.sadd(index_key, cache_key)
            )
            
        except Exception as e:
            logger.error(f"Failed to store metadata for {cache_key}: {e}")
    
    async def _check_memory_limits(self, new_entry_size: int) -> bool:
        """Check if new entry fits within memory limits"""
        
        try:
            current_memory = await self._get_current_memory_usage()
            
            if current_memory + new_entry_size <= self.max_memory_bytes:
                return True
            
            logger.warning(f"Memory limit exceeded: {current_memory + new_entry_size} > {self.max_memory_bytes}")
            return False
            
        except Exception as e:
            logger.error(f"Memory check failed: {e}")
            return True  # Allow storage if check fails
    
    async def _get_current_memory_usage(self) -> int:
        """Get current cache memory usage"""
        
        try:
            loop = asyncio.get_event_loop()
            
            # Get Redis memory info
            info = await loop.run_in_executor(
                self.executor,
                self.redis_client.info,
                'memory'
            )
            
            return info.get('used_memory', 0)
            
        except Exception as e:
            logger.error(f"Failed to get memory usage: {e}")
            return 0
    
    async def _evict_entries(self, target_free_bytes: Optional[int] = None):
        """Evict cache entries using LRU strategy"""
        
        if target_free_bytes is None:
            target_free_bytes = self.max_memory_bytes // 4  # Free 25% of cache
        
        try:
            # Get all cache entries with metadata
            entries = await self._get_all_entries_metadata()
            
            if not entries:
                return
            
            # Sort by access patterns (LRU + quality score)
            entries.sort(key=lambda x: (
                x.get('access_count', 0) * x.get('quality_score', 0.5),
                x.get('last_accessed', '1970-01-01')
            ))
            
            freed_bytes = 0
            evicted_count = 0
            
            for entry in entries:
                if freed_bytes >= target_free_bytes:
                    break
                
                cache_key = entry['key']
                
                # Remove from Redis
                await self._remove_cache_entry(cache_key)
                
                freed_bytes += entry.get('size_bytes', 0)
                evicted_count += 1
            
            logger.info(f"Evicted {evicted_count} entries, freed {freed_bytes} bytes")
            
        except Exception as e:
            logger.error(f"Cache eviction failed: {e}")
    
    async def _get_all_entries_metadata(self) -> List[Dict[str, Any]]:
        """Get metadata for all cache entries"""
        
        try:
            loop = asyncio.get_event_loop()
            
            # Get all metadata keys
            pattern = f"{self.prefixes['metadata']}*"
            metadata_keys = await loop.run_in_executor(
                self.executor,
                lambda: self.redis_client.keys(pattern)
            )
            
            entries = []
            
            for key in metadata_keys:
                try:
                    metadata_json = await loop.run_in_executor(
                        self.executor,
                        self.redis_client.get,
                        key
                    )
                    
                    if metadata_json:
                        metadata = json.loads(metadata_json.decode())
                        entries.append(metadata)
                        
                except Exception as e:
                    logger.warning(f"Failed to load metadata for {key}: {e}")
            
            return entries
            
        except Exception as e:
            logger.error(f"Failed to get entries metadata: {e}")
            return []
    
    async def _remove_cache_entry(self, cache_key: str):
        """Remove cache entry and its metadata"""
        
        try:
            loop = asyncio.get_event_loop()
            
            # Remove data
            await loop.run_in_executor(
                self.executor,
                self.redis_client.delete,
                cache_key
            )
            
            # Remove metadata
            metadata_key = f"{self.prefixes['metadata']}{cache_key}"
            await loop.run_in_executor(
                self.executor,
                self.redis_client.delete,
                metadata_key
            )
            
        except Exception as e:
            logger.error(f"Failed to remove cache entry {cache_key}: {e}")
    
    async def invalidate_ticker_cache(self, ticker: str):
        """Invalidate all cache entries for a specific ticker"""
        
        try:
            loop = asyncio.get_event_loop()
            
            # Get ticker index
            index_key = f"{self.prefixes['index']}{ticker}"
            cache_keys = await loop.run_in_executor(
                self.executor,
                lambda: self.redis_client.smembers(index_key)
            )
            
            # Remove all entries
            removed_count = 0
            for cache_key in cache_keys:
                await self._remove_cache_entry(cache_key.decode())
                removed_count += 1
            
            # Remove index
            await loop.run_in_executor(
                self.executor,
                self.redis_client.delete,
                index_key
            )
            
            logger.info(f"Invalidated {removed_count} cache entries for {ticker}")
            
        except Exception as e:
            logger.error(f"Failed to invalidate cache for {ticker}: {e}")
    
    async def cleanup_expired_entries(self):
        """Clean up expired cache entries"""
        
        try:
            entries = await self._get_all_entries_metadata()
            current_time = datetime.now()
            
            expired_count = 0
            
            for entry in entries:
                try:
                    expires_at = datetime.fromisoformat(entry['expires_at'])
                    if current_time > expires_at:
                        await self._remove_cache_entry(entry['key'])
                        expired_count += 1
                except Exception as e:
                    logger.warning(f"Failed to check expiry for entry: {e}")
            
            logger.info(f"Cleaned up {expired_count} expired entries")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    async def get_cache_stats(self) -> CacheStats:
        """Get comprehensive cache statistics"""
        
        try:
            entries = await self._get_all_entries_metadata()
            current_time = datetime.now()
            
            total_entries = len(entries)
            total_size_bytes = sum(entry.get('size_bytes', 0) for entry in entries)
            total_size_mb = total_size_bytes / (1024 * 1024)
            
            # Calculate hit rate
            total_requests = self.cache_hits + self.cache_misses
            hit_rate = self.cache_hits / max(total_requests, 1)
            miss_rate = self.cache_misses / max(total_requests, 1)
            
            # Calculate average retrieval time
            avg_retrieval_time = sum(self.retrieval_times) / max(len(self.retrieval_times), 1)
            
            # Count expired entries
            expired_entries = 0
            for entry in entries:
                try:
                    expires_at = datetime.fromisoformat(entry['expires_at'])
                    if current_time > expires_at:
                        expired_entries += 1
                except:
                    pass
            
            # Memory usage percentage
            memory_usage_percent = (total_size_bytes / self.max_memory_bytes) * 100
            
            return CacheStats(
                total_entries=total_entries,
                total_size_mb=total_size_mb,
                hit_rate=hit_rate,
                miss_rate=miss_rate,
                avg_retrieval_time_ms=avg_retrieval_time,
                memory_usage_percent=memory_usage_percent,
                expired_entries=expired_entries
            )
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return CacheStats(0, 0.0, 0.0, 0.0, 0.0, 0.0, 0)
    
    async def optimize_cache(self):
        """Optimize cache performance"""
        
        try:
            # Clean up expired entries
            await self.cleanup_expired_entries()
            
            # Check memory usage and evict if necessary
            current_memory = await self._get_current_memory_usage()
            if current_memory > self.max_memory_bytes * 0.8:  # 80% threshold
                await self._evict_entries()
            
            # Reset performance counters periodically
            if len(self.retrieval_times) > 1000:
                self.retrieval_times = self.retrieval_times[-100:]  # Keep last 100
            
            logger.info("Cache optimization completed")
            
        except Exception as e:
            logger.error(f"Cache optimization failed: {e}")
    
    async def warm_cache(self, tickers: List[str], analysis_types: List[str]):
        """Pre-warm cache with common ticker/analysis combinations"""
        
        logger.info(f"Warming cache for {len(tickers)} tickers, {len(analysis_types)} analysis types")
        
        # This would be called by the main RAG service to pre-populate cache
        # Implementation depends on integration with RAG context preparation
        pass

# Global cache manager instance
context_cache = ContextCacheManager()