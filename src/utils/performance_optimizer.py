#!/usr/bin/env python3
"""
Performance Optimization Module for LocalLLM
Implements caching, memory optimization, and performance monitoring
"""

import os
import sys
import time
import hashlib
import pickle
import psutil
import threading
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, asdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import multiprocessing as mp
from functools import wraps, lru_cache
from memory_profiler import profile
import json
from loguru import logger

# Performance monitoring
@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    cpu_usage: float
    memory_usage: float
    memory_peak: float
    processing_time: float
    cache_hits: int
    cache_misses: int
    files_processed: int
    throughput: float  # files per second
    
class PerformanceMonitor:
    """Real-time performance monitoring"""
    
    def __init__(self):
        self.metrics_history: List[PerformanceMetrics] = []
        self.start_time = time.time()
        self.cache_stats = {"hits": 0, "misses": 0}
        self.files_processed = 0
        
    def record_metrics(self, processing_time: float) -> PerformanceMetrics:
        """Record current performance metrics"""
        process = psutil.Process()
        memory_info = process.memory_info()
        
        metrics = PerformanceMetrics(
            cpu_usage=psutil.cpu_percent(interval=0.1),
            memory_usage=memory_info.rss / 1024 / 1024,  # MB
            memory_peak=memory_info.peak_wss / 1024 / 1024 if hasattr(memory_info, 'peak_wss') else memory_info.rss / 1024 / 1024,
            processing_time=processing_time,
            cache_hits=self.cache_stats["hits"],
            cache_misses=self.cache_stats["misses"],
            files_processed=self.files_processed,
            throughput=self.files_processed / (time.time() - self.start_time) if time.time() > self.start_time else 0
        )
        
        self.metrics_history.append(metrics)
        self.files_processed += 1
        
        return metrics
    
    def get_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics_history:
            return {}
            
        avg_cpu = sum(m.cpu_usage for m in self.metrics_history) / len(self.metrics_history)
        avg_memory = sum(m.memory_usage for m in self.metrics_history) / len(self.metrics_history)
        peak_memory = max(m.memory_peak for m in self.metrics_history)
        avg_processing_time = sum(m.processing_time for m in self.metrics_history) / len(self.metrics_history)
        total_cache_hits = self.cache_stats["hits"]
        total_cache_misses = self.cache_stats["misses"]
        cache_hit_rate = total_cache_hits / (total_cache_hits + total_cache_misses) if (total_cache_hits + total_cache_misses) > 0 else 0
        
        return {
            "average_cpu_usage": round(avg_cpu, 2),
            "average_memory_usage_mb": round(avg_memory, 2),
            "peak_memory_usage_mb": round(peak_memory, 2),
            "average_processing_time": round(avg_processing_time, 2),
            "total_files_processed": self.files_processed,
            "cache_hit_rate": round(cache_hit_rate * 100, 2),
            "total_cache_hits": total_cache_hits,
            "total_cache_misses": total_cache_misses,
            "current_throughput": round(self.metrics_history[-1].throughput, 2) if self.metrics_history else 0
        }

# Caching system
class DocumentCache:
    """High-performance document caching system"""
    
    def __init__(self, cache_dir: Path = Path("cache"), max_size_mb: int = 1024):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(exist_ok=True)
        self.max_size_mb = max_size_mb
        self.cache_index = {}
        self.load_cache_index()
        
    def _get_file_hash(self, file_path: Path) -> str:
        """Generate hash for file content and metadata"""
        stat = file_path.stat()
        content = f"{file_path.name}_{stat.st_size}_{stat.st_mtime}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_path(self, file_hash: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{file_hash}.pkl"
    
    def get(self, file_path: Path, processing_params: Dict[str, Any]) -> Optional[Any]:
        """Get cached result"""
        file_hash = self._get_file_hash(file_path)
        params_hash = hashlib.md5(str(sorted(processing_params.items())).encode()).hexdigest()
        cache_key = f"{file_hash}_{params_hash}"
        
        cache_path = self._get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    result = pickle.load(f)
                
                # Update access time
                self.cache_index[cache_key] = {
                    "last_access": time.time(),
                    "file_size": cache_path.stat().st_size
                }
                self.save_cache_index()
                
                logger.info(f"🎯 Cache HIT for {file_path.name}")
                return result
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to load cache for {file_path.name}: {e}")
                cache_path.unlink(missing_ok=True)
        
        logger.info(f"❌ Cache MISS for {file_path.name}")
        return None
    
    def set(self, file_path: Path, processing_params: Dict[str, Any], result: Any):
        """Store result in cache"""
        file_hash = self._get_file_hash(file_path)
        params_hash = hashlib.md5(str(sorted(processing_params.items())).encode()).hexdigest()
        cache_key = f"{file_hash}_{params_hash}"
        
        cache_path = self._get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(result, f)
            
            # Update index
            self.cache_index[cache_key] = {
                "last_access": time.time(),
                "file_size": cache_path.stat().st_size
            }
            
            # Clean old cache if needed
            self._cleanup_cache()
            self.save_cache_index()
            
            logger.info(f"💾 Cached result for {file_path.name}")
            
        except Exception as e:
            logger.error(f"❌ Failed to cache result for {file_path.name}: {e}")
    
    def _cleanup_cache(self):
        """Remove old cache entries if size limit exceeded"""
        total_size = sum(info["file_size"] for info in self.cache_index.values())
        max_size_bytes = self.max_size_mb * 1024 * 1024
        
        if total_size > max_size_bytes:
            # Sort by last access time (oldest first)
            sorted_entries = sorted(
                self.cache_index.items(),
                key=lambda x: x[1]["last_access"]
            )
            
            removed_size = 0
            for cache_key, info in sorted_entries:
                cache_path = self._get_cache_path(cache_key)
                if cache_path.exists():
                    cache_path.unlink()
                    removed_size += info["file_size"]
                
                del self.cache_index[cache_key]
                
                if total_size - removed_size <= max_size_bytes * 0.8:  # Remove 20% extra
                    break
            
            logger.info(f"🧹 Cleaned cache: removed {removed_size / 1024 / 1024:.1f} MB")
    
    def load_cache_index(self):
        """Load cache index from disk"""
        index_path = self.cache_dir / "cache_index.json"
        if index_path.exists():
            try:
                with open(index_path, 'r') as f:
                    self.cache_index = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cache index: {e}")
                self.cache_index = {}
    
    def save_cache_index(self):
        """Save cache index to disk"""
        index_path = self.cache_dir / "cache_index.json"
        try:
            with open(index_path, 'w') as f:
                json.dump(self.cache_index, f)
        except Exception as e:
            logger.error(f"Failed to save cache index: {e}")
    
    def clear(self):
        """Clear all cache"""
        for file in self.cache_dir.glob("*.pkl"):
            file.unlink()
        self.cache_index = {}
        self.save_cache_index()
        logger.info("🧹 Cache cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        total_files = len(self.cache_index)
        total_size = sum(info["file_size"] for info in self.cache_index.values())
        
        return {
            "total_cached_files": total_files,
            "total_cache_size_mb": round(total_size / 1024 / 1024, 2),
            "cache_utilization": round(total_size / (self.max_size_mb * 1024 * 1024) * 100, 2)
        }

# Performance decorators
def performance_monitor(monitor: PerformanceMonitor):
    """Decorator for performance monitoring"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                processing_time = time.time() - start_time
                monitor.record_metrics(processing_time)
                return result
            except Exception as e:
                processing_time = time.time() - start_time
                monitor.record_metrics(processing_time)
                raise e
                
        return wrapper
    return decorator

def cached_processing(cache: DocumentCache):
    """Decorator for cached processing"""
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(file_path: Path, **kwargs):
            # Check cache first
            cached_result = cache.get(file_path, kwargs)
            if cached_result is not None:
                return cached_result
            
            # Process and cache
            result = func(file_path, **kwargs)
            cache.set(file_path, kwargs, result)
            
            return result
            
        return wrapper
    return decorator

# Optimized processing functions
class OptimizedProcessor:
    """Optimized document processor with caching and monitoring"""
    
    def __init__(self, cache_dir: Path = Path("cache"), max_cache_mb: int = 1024):
        self.cache = DocumentCache(cache_dir, max_cache_mb)
        self.monitor = PerformanceMonitor()
        self.thread_pool = ThreadPoolExecutor(max_workers=mp.cpu_count())
        
    @cached_processing
    @performance_monitor
    def process_document_optimized(self, file_path: Path, **kwargs):
        """Optimized document processing with caching"""
        # Import here to avoid circular imports
        from gui.real_processing import real_process_file_global
        
        return real_process_file_global(file_path, **kwargs)
    
    def process_batch_optimized(self, file_paths: List[Path], **kwargs) -> List[Any]:
        """Optimized batch processing"""
        futures = []
        
        for file_path in file_paths:
            future = self.thread_pool.submit(
                self.process_document_optimized,
                file_path,
                **kwargs
            )
            futures.append(future)
        
        results = []
        for future in futures:
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to process document: {e}")
                results.append(None)
        
        return results
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        return {
            "performance_metrics": self.monitor.get_summary(),
            "cache_statistics": self.cache.get_stats(),
            "system_info": {
                "cpu_count": mp.cpu_count(),
                "available_memory_mb": round(psutil.virtual_memory().available / 1024 / 1024, 2),
                "total_memory_mb": round(psutil.virtual_memory().total / 1024 / 1024, 2)
            }
        }
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
    
    def __del__(self):
        """Cleanup resources"""
        if hasattr(self, 'thread_pool'):
            self.thread_pool.shutdown(wait=True)

# Memory optimization utilities
@lru_cache(maxsize=100)
def cached_language_detection(text_sample: str):
    """Cached language detection"""
    from utils.language_detector import LanguageDetector
    detector = LanguageDetector()
    return detector.detect_with_fallback(text_sample)

def optimize_memory_usage():
    """Optimize memory usage"""
    import gc
    gc.collect()
    
    # Get current memory usage
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    
    logger.info(f"🧠 Memory optimized. Current usage: {memory_mb:.1f} MB")
    return memory_mb

# Parallel processing optimization
class ParallelOptimizer:
    """Optimize parallel processing based on system resources"""
    
    @staticmethod
    def get_optimal_workers() -> int:
        """Calculate optimal number of workers"""
        cpu_count = mp.cpu_count()
        memory_gb = psutil.virtual_memory().total / (1024**3)
        
        # Conservative approach: use 75% of cores, limited by memory
        optimal_workers = min(
            max(1, int(cpu_count * 0.75)),
            max(1, int(memory_gb / 2))  # Assume 2GB per worker
        )
        
        logger.info(f"🚀 Optimal workers: {optimal_workers} (CPU: {cpu_count}, Memory: {memory_gb:.1f}GB)")
        return optimal_workers
    
    @staticmethod
    def choose_execution_method(num_tasks: int, task_complexity: str = "medium") -> str:
        """Choose between threading and multiprocessing"""
        cpu_count = mp.cpu_count()
        
        complexity_factors = {
            "light": 0.5,
            "medium": 1.0,
            "heavy": 2.0
        }
        
        factor = complexity_factors.get(task_complexity, 1.0)
        
        if num_tasks * factor > cpu_count * 2:
            return "multiprocessing"
        else:
            return "threading"

if __name__ == "__main__":
    # Example usage
    optimizer = OptimizedProcessor()
    
    # Test files
    test_files = list(Path("data").glob("*.pdf"))[:3] if Path("data").exists() else []
    
    if test_files:
        print("🚀 Running optimized processing test...")
        
        start_time = time.time()
        results = optimizer.process_batch_optimized(test_files, language="ja", max_length=100)
        end_time = time.time()
        
        print(f"✅ Processed {len(test_files)} files in {end_time - start_time:.2f}s")
        print("📊 Performance Report:")
        print(json.dumps(optimizer.get_performance_report(), indent=2, ensure_ascii=False))
    else:
        print("ℹ️ No test files found in 'data' directory")
