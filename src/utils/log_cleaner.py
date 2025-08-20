#!/usr/bin/env python3
"""
Log File Cleaner Module for LocalLLM
Automatically manages and cleans up old log files to prevent disk space issues
"""

import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import schedule
from loguru import logger


class LogCleaner:
    """
    Manages automatic cleanup of old log files
    """
    
    def __init__(self, 
                 log_directories: List[str] = None,
                 max_age_days: int = 30,
                 max_file_count: int = 100,
                 max_total_size_mb: int = 500,
                 check_interval_hours: int = 24):
        """
        Initialize log cleaner
        
        Args:
            log_directories: List of directories to monitor for log files
            max_age_days: Maximum age of log files in days
            max_file_count: Maximum number of log files to keep
            max_total_size_mb: Maximum total size of log files in MB
            check_interval_hours: How often to run cleanup (in hours)
        """
        self.log_directories = log_directories or [
            "logs",
            "output/batch_gui/logs",
            "output/debug_large_file/logs",
            "output/debug_translation/logs",
            "output/test_batch/logs"
        ]
        
        self.max_age_days = max_age_days
        self.max_file_count = max_file_count
        self.max_total_size_mb = max_total_size_mb
        self.check_interval_hours = check_interval_hours
        
        self.is_running = False
        self.cleanup_thread = None
        
        # Log file patterns to clean
        self.log_patterns = [
            "*.log",
            "*.log.*",
            "*.out",
            "*.err",
            "summarizer*.log",
            "summary_results*.log",
            "batch_*.log",
            "processing_*.log"
        ]
        
        logger.info(f"🧹 LogCleaner initialized:")
        logger.info(f"   📁 Monitoring directories: {len(self.log_directories)}")
        logger.info(f"   ⏰ Max age: {max_age_days} days")
        logger.info(f"   📊 Max files: {max_file_count}")
        logger.info(f"   💾 Max size: {max_total_size_mb} MB")
        logger.info(f"   🔄 Check interval: {check_interval_hours} hours")
    
    def get_log_files(self) -> List[Path]:
        """
        Scan all directories for log files
        
        Returns:
            List of log file paths
        """
        log_files = []
        
        for directory in self.log_directories:
            dir_path = Path(directory)
            if not dir_path.exists():
                continue
                
            for pattern in self.log_patterns:
                log_files.extend(dir_path.glob(pattern))
                # Also check subdirectories
                log_files.extend(dir_path.glob(f"**/{pattern}"))
        
        # Remove duplicates and sort by modification time
        unique_files = list(set(log_files))
        unique_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        return unique_files
    
    def get_file_age_days(self, file_path: Path) -> float:
        """
        Get the age of a file in days
        
        Args:
            file_path: Path to the file
            
        Returns:
            Age in days
        """
        try:
            file_time = file_path.stat().st_mtime
            current_time = time.time()
            age_seconds = current_time - file_time
            return age_seconds / (24 * 60 * 60)  # Convert to days
        except Exception:
            return 0
    
    def get_total_size_mb(self, files: List[Path]) -> float:
        """
        Calculate total size of files in MB
        
        Args:
            files: List of file paths
            
        Returns:
            Total size in MB
        """
        total_size = 0
        for file_path in files:
            try:
                total_size += file_path.stat().st_size
            except Exception:
                continue
        
        return total_size / (1024 * 1024)  # Convert to MB
    
    def cleanup_by_age(self, log_files: List[Path]) -> Dict[str, int]:
        """
        Remove files older than max_age_days
        
        Args:
            log_files: List of log files to check
            
        Returns:
            Cleanup statistics
        """
        deleted_count = 0
        deleted_size = 0
        
        cutoff_date = datetime.now() - timedelta(days=self.max_age_days)
        
        for file_path in log_files:
            age_days = self.get_file_age_days(file_path)
            
            if age_days > self.max_age_days:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += file_size
                    logger.debug(f"🗑️ Deleted old log file: {file_path} (age: {age_days:.1f} days)")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to delete {file_path}: {e}")
        
        return {
            'deleted_count': deleted_count,
            'deleted_size_mb': deleted_size / (1024 * 1024),
            'criteria': 'age'
        }
    
    def cleanup_by_count(self, log_files: List[Path]) -> Dict[str, int]:
        """
        Keep only the most recent max_file_count files
        
        Args:
            log_files: List of log files (should be sorted by modification time)
            
        Returns:
            Cleanup statistics
        """
        deleted_count = 0
        deleted_size = 0
        
        if len(log_files) > self.max_file_count:
            files_to_delete = log_files[self.max_file_count:]
            
            for file_path in files_to_delete:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += file_size
                    logger.debug(f"🗑️ Deleted excess log file: {file_path}")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to delete {file_path}: {e}")
        
        return {
            'deleted_count': deleted_count,
            'deleted_size_mb': deleted_size / (1024 * 1024),
            'criteria': 'count'
        }
    
    def cleanup_by_size(self, log_files: List[Path]) -> Dict[str, int]:
        """
        Remove oldest files until total size is under max_total_size_mb
        
        Args:
            log_files: List of log files (should be sorted by modification time)
            
        Returns:
            Cleanup statistics
        """
        deleted_count = 0
        deleted_size = 0
        
        # Calculate current total size
        current_size_mb = self.get_total_size_mb(log_files)
        
        if current_size_mb > self.max_total_size_mb:
            target_size_mb = self.max_total_size_mb * 0.9  # Leave some buffer
            
            # Start from oldest files (end of sorted list)
            for file_path in reversed(log_files):
                if current_size_mb <= target_size_mb:
                    break
                
                try:
                    file_size = file_path.stat().st_size
                    file_size_mb = file_size / (1024 * 1024)
                    
                    file_path.unlink()
                    deleted_count += 1
                    deleted_size += file_size
                    current_size_mb -= file_size_mb
                    
                    logger.debug(f"🗑️ Deleted large log file: {file_path} ({file_size_mb:.2f} MB)")
                except Exception as e:
                    logger.warning(f"⚠️ Failed to delete {file_path}: {e}")
        
        return {
            'deleted_count': deleted_count,
            'deleted_size_mb': deleted_size / (1024 * 1024),
            'criteria': 'size'
        }
    
    def run_cleanup(self) -> Dict[str, any]:
        """
        Run full cleanup process
        
        Returns:
            Cleanup statistics
        """
        logger.info("🧹 Starting log cleanup process...")
        
        # Get all log files
        log_files = self.get_log_files()
        
        if not log_files:
            logger.info("📁 No log files found to clean")
            return {'status': 'no_files', 'total_files': 0}
        
        initial_count = len(log_files)
        initial_size_mb = self.get_total_size_mb(log_files)
        
        logger.info(f"📊 Found {initial_count} log files ({initial_size_mb:.2f} MB)")
        
        # Run cleanup operations
        cleanup_stats = {
            'initial_count': initial_count,
            'initial_size_mb': initial_size_mb,
            'operations': []
        }
        
        # 1. Cleanup by age
        age_stats = self.cleanup_by_age(log_files)
        if age_stats['deleted_count'] > 0:
            cleanup_stats['operations'].append(age_stats)
            log_files = self.get_log_files()  # Refresh list
        
        # 2. Cleanup by count
        count_stats = self.cleanup_by_count(log_files)
        if count_stats['deleted_count'] > 0:
            cleanup_stats['operations'].append(count_stats)
            log_files = self.get_log_files()  # Refresh list
        
        # 3. Cleanup by size
        size_stats = self.cleanup_by_size(log_files)
        if size_stats['deleted_count'] > 0:
            cleanup_stats['operations'].append(size_stats)
            log_files = self.get_log_files()  # Refresh list
        
        # Final statistics
        final_count = len(log_files)
        final_size_mb = self.get_total_size_mb(log_files)
        
        total_deleted = initial_count - final_count
        total_freed_mb = initial_size_mb - final_size_mb
        
        cleanup_stats.update({
            'final_count': final_count,
            'final_size_mb': final_size_mb,
            'total_deleted': total_deleted,
            'total_freed_mb': total_freed_mb,
            'status': 'completed'
        })
        
        logger.info(f"✅ Log cleanup completed:")
        logger.info(f"   🗑️ Deleted: {total_deleted} files")
        logger.info(f"   💾 Freed: {total_freed_mb:.2f} MB")
        logger.info(f"   📊 Remaining: {final_count} files ({final_size_mb:.2f} MB)")
        
        return cleanup_stats
    
    def start_scheduler(self):
        """
        Start the scheduled cleanup process
        """
        if self.is_running:
            logger.warning("⚠️ Log cleaner scheduler is already running")
            return
        
        self.is_running = True
        
        # Schedule cleanup
        schedule.every(self.check_interval_hours).hours.do(self.run_cleanup)
        
        def run_scheduler():
            logger.info(f"🕐 Starting log cleanup scheduler (every {self.check_interval_hours} hours)")
            while self.is_running:
                schedule.run_pending()
                time.sleep(3600)  # Check every hour
        
        self.cleanup_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.cleanup_thread.start()
        
        logger.info("✅ Log cleanup scheduler started")
    
    def stop_scheduler(self):
        """
        Stop the scheduled cleanup process
        """
        if not self.is_running:
            logger.debug("🔍 Scheduler is already stopped")
            return
        
        logger.info("🛑 Stopping log cleanup scheduler...")
        self.is_running = False
        
        # Clear the schedule
        try:
            schedule.clear()
        except Exception as e:
            logger.warning(f"⚠️ Error clearing schedule: {e}")
        
        # Wait for thread to finish
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            try:
                self.cleanup_thread.join(timeout=2)
                if self.cleanup_thread.is_alive():
                    logger.warning("⚠️ Cleanup thread did not stop within timeout")
            except Exception as e:
                logger.warning(f"⚠️ Error stopping cleanup thread: {e}")
        
        logger.info("🛑 Log cleanup scheduler stopped")
    
    def get_status(self) -> Dict[str, any]:
        """
        Get current status of log files and cleaner
        
        Returns:
            Status information
        """
        log_files = self.get_log_files()
        total_size_mb = self.get_total_size_mb(log_files)
        
        # Group files by directory
        by_directory = {}
        for file_path in log_files:
            dir_name = str(file_path.parent)
            if dir_name not in by_directory:
                by_directory[dir_name] = []
            by_directory[dir_name].append(file_path)
        
        # Find oldest and newest files
        oldest_file = None
        newest_file = None
        if log_files:
            oldest_file = min(log_files, key=lambda x: x.stat().st_mtime)
            newest_file = max(log_files, key=lambda x: x.stat().st_mtime)
        
        return {
            'total_files': len(log_files),
            'total_size_mb': total_size_mb,
            'directories': {k: len(v) for k, v in by_directory.items()},
            'oldest_file': str(oldest_file) if oldest_file else None,
            'newest_file': str(newest_file) if newest_file else None,
            'oldest_age_days': self.get_file_age_days(oldest_file) if oldest_file else 0,
            'is_scheduler_running': self.is_running,
            'settings': {
                'max_age_days': self.max_age_days,
                'max_file_count': self.max_file_count,
                'max_total_size_mb': self.max_total_size_mb,
                'check_interval_hours': self.check_interval_hours
            }
        }


def create_default_log_cleaner() -> LogCleaner:
    """
    Create a log cleaner with default settings
    
    Returns:
        Configured LogCleaner instance
    """
    return LogCleaner(
        max_age_days=30,        # Keep logs for 30 days
        max_file_count=100,     # Keep maximum 100 log files
        max_total_size_mb=500,  # Keep maximum 500MB of logs
        check_interval_hours=24 # Check daily
    )


if __name__ == "__main__":
    # Test the log cleaner
    cleaner = create_default_log_cleaner()
    
    print("📊 Current log status:")
    status = cleaner.get_status()
    print(f"   Files: {status['total_files']}")
    print(f"   Size: {status['total_size_mb']:.2f} MB")
    print(f"   Oldest: {status['oldest_age_days']:.1f} days")
    
    print("\n🧹 Running cleanup...")
    results = cleaner.run_cleanup()
    print(f"   Deleted: {results.get('total_deleted', 0)} files")
    print(f"   Freed: {results.get('total_freed_mb', 0):.2f} MB")
