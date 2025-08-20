"""Performance monitoring utilities."""

import time
import psutil
import memory_profiler
from pathlib import Path
from typing import Dict, Any
from loguru import logger


class PerformanceMonitor:
    """Monitor performance metrics during document processing."""
    
    def __init__(self):
        self.start_time = None
        self.end_time = None
        self.peak_memory = 0
        self.initial_memory = 0
        self.process = psutil.Process()
    
    def start(self) -> None:
        """Start performance monitoring."""
        self.start_time = time.time()
        self.initial_memory = self.get_memory_usage()
        self.peak_memory = self.initial_memory
        logger.info(f"🚀 Performance monitoring started - Initial memory: {self.initial_memory:.1f} MB")
    
    def update_peak_memory(self) -> None:
        """Update peak memory usage."""
        current_memory = self.get_memory_usage()
        if current_memory > self.peak_memory:
            self.peak_memory = current_memory
    
    def stop(self) -> Dict[str, Any]:
        """Stop monitoring and return performance metrics."""
        self.end_time = time.time()
        final_memory = self.get_memory_usage()
        
        metrics = {
            "processing_time_seconds": round(self.end_time - self.start_time, 2),
            "initial_memory_mb": round(self.initial_memory, 1),
            "peak_memory_mb": round(self.peak_memory, 1),
            "final_memory_mb": round(final_memory, 1),
            "memory_increase_mb": round(self.peak_memory - self.initial_memory, 1),
            "cpu_percent": round(self.process.cpu_percent(), 1),
            "memory_percent": round(self.process.memory_percent(), 1)
        }
        
        logger.info(f"🏁 Performance monitoring stopped")
        logger.info(f"   ⏱️  Processing time: {metrics['processing_time_seconds']} seconds")
        logger.info(f"   🧠 Memory usage: {metrics['initial_memory_mb']} → {metrics['peak_memory_mb']} → {metrics['final_memory_mb']} MB")
        logger.info(f"   📊 CPU usage: {metrics['cpu_percent']}%")
        
        return metrics
    
    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            # Get RSS (Resident Set Size) memory in MB
            return self.process.memory_info().rss / 1024 / 1024
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return 0.0
    
    def check_memory_limit(self, limit_gb: int = 8) -> bool:
        """Check if memory usage exceeds the limit."""
        current_memory_gb = self.get_memory_usage() / 1024
        if current_memory_gb > limit_gb:
            logger.warning(f"⚠️  Memory usage ({current_memory_gb:.1f} GB) exceeds limit ({limit_gb} GB)")
            return False
        return True


def log_performance_summary(metrics: Dict[str, Any], input_size: int, output_size: int) -> None:
    """Log a comprehensive performance summary."""
    logger.info("📊 PERFORMANCE SUMMARY")
    logger.info("-" * 50)
    
    # Processing efficiency
    chars_per_second = input_size / metrics['processing_time_seconds'] if metrics['processing_time_seconds'] > 0 else 0
    mb_per_second = (input_size / 1024 / 1024) / metrics['processing_time_seconds'] if metrics['processing_time_seconds'] > 0 else 0
    
    logger.info(f"⏱️  Time: {metrics['processing_time_seconds']} seconds")
    logger.info(f"📈 Throughput: {chars_per_second:.0f} chars/sec, {mb_per_second:.2f} MB/sec")
    logger.info(f"🧠 Memory: {metrics['peak_memory_mb']} MB peak ({metrics['memory_increase_mb']:+.1f} MB change)")
    logger.info(f"🖥️  CPU: {metrics['cpu_percent']}% average")
    logger.info(f"💾 Memory %: {metrics['memory_percent']}% of system")
    
    # File size analysis
    compression_ratio = (output_size / input_size * 100) if input_size > 0 else 0
    logger.info(f"📁 Input size: {input_size:,} characters")
    logger.info(f"📄 Output size: {output_size:,} characters")
    logger.info(f"🗜️  Compression: {compression_ratio:.1f}%")
    
    # Performance rating
    if metrics['processing_time_seconds'] < 10:
        rating = "🚀 Excellent"
    elif metrics['processing_time_seconds'] < 30:
        rating = "✅ Good"
    elif metrics['processing_time_seconds'] < 60:
        rating = "⚠️  Acceptable"
    else:
        rating = "🐌 Slow"
    
    logger.info(f"🏆 Performance: {rating}")
    logger.info("-" * 50)
