#!/usr/bin/env python3
"""
Batch Processing System for LocalLLM
Step 2: Progress Tracker - Visual progress tracking with tqdm
"""

import time
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from tqdm import tqdm
import threading


@dataclass
class ProcessingStats:
    """Processing statistics container."""
    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    skipped_files: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    # File-specific stats
    total_size_mb: float = 0.0
    processed_size_mb: float = 0.0
    
    # Performance metrics
    avg_processing_time: float = 0.0
    files_per_minute: float = 0.0
    
    @property
    def success_rate(self) -> float:
        """Success rate percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.completed_files / self.total_files) * 100
    
    @property
    def elapsed_time(self) -> timedelta:
        """Elapsed processing time."""
        if not self.start_time:
            return timedelta(0)
        end = self.end_time or datetime.now()
        return end - self.start_time
    
    @property
    def estimated_remaining(self) -> timedelta:
        """Estimated remaining time."""
        if self.completed_files == 0 or self.files_per_minute == 0:
            return timedelta(0)
        
        remaining_files = self.total_files - self.completed_files
        remaining_minutes = remaining_files / self.files_per_minute
        return timedelta(minutes=remaining_minutes)


class ProgressTracker:
    """
    Advanced progress tracking with visual feedback.
    Provides real-time statistics and ETA calculations.
    """
    
    def __init__(self, total_files: int, total_size_mb: float = 0.0):
        """
        Initialize progress tracker.
        
        Args:
            total_files: Total number of files to process
            total_size_mb: Total size in MB (optional)
        """
        self.stats = ProcessingStats(
            total_files=total_files,
            total_size_mb=total_size_mb
        )
        
        # Progress bars
        self.main_pbar: Optional[tqdm] = None
        self.current_file_pbar: Optional[tqdm] = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Processing times for average calculation
        self.processing_times: List[float] = []
    
    def start_processing(self) -> None:
        """Start the processing session."""
        self.stats.start_time = datetime.now()
        
        # Initialize main progress bar
        self.main_pbar = tqdm(
            total=self.stats.total_files,
            desc="📁 Processing Files",
            unit="files",
            bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
            colour="green"
        )
        
        print(f"🚀 Starting batch processing of {self.stats.total_files} files")
        print(f"📊 Total size: {self.stats.total_size_mb:.2f} MB")
        print("=" * 60)
    
    def start_file(self, filename: str, file_size_mb: float = 0.0) -> None:
        """
        Start processing a file.
        
        Args:
            filename: Name of the file being processed
            file_size_mb: Size of the file in MB
        """
        with self.lock:
            # Close previous file progress bar
            if self.current_file_pbar:
                self.current_file_pbar.close()
            
            # Create new file progress bar
            self.current_file_pbar = tqdm(
                total=100,
                desc=f"📄 {filename[:30]}{'...' if len(filename) > 30 else ''}",
                unit="%",
                bar_format="{l_bar}{bar}| {n_fmt}% [{elapsed}]",
                colour="blue",
                leave=False
            )
    
    def update_file_progress(self, progress: int) -> None:
        """
        Update current file progress.
        
        Args:
            progress: Progress percentage (0-100)
        """
        if self.current_file_pbar:
            self.current_file_pbar.n = progress
            self.current_file_pbar.refresh()
    
    def complete_file(self, success: bool, processing_time: float, file_size_mb: float = 0.0) -> None:
        """
        Mark file as completed.
        
        Args:
            success: Whether processing was successful
            processing_time: Time taken to process (seconds)
            file_size_mb: Size of processed file in MB
        """
        with self.lock:
            # Close file progress bar
            if self.current_file_pbar:
                self.current_file_pbar.n = 100
                self.current_file_pbar.refresh()
                self.current_file_pbar.close()
                self.current_file_pbar = None
            
            # Update stats
            if success:
                self.stats.completed_files += 1
            else:
                self.stats.failed_files += 1
            
            self.stats.processed_size_mb += file_size_mb
            self.processing_times.append(processing_time)
            
            # Calculate performance metrics
            self._update_performance_metrics()
            
            # Update main progress bar
            if self.main_pbar:
                self.main_pbar.update(1)
                self._update_main_description()
    
    def skip_file(self, reason: str) -> None:
        """
        Mark file as skipped.
        
        Args:
            reason: Reason for skipping
        """
        with self.lock:
            self.stats.skipped_files += 1
            
            if self.main_pbar:
                self.main_pbar.update(1)
                self._update_main_description()
    
    def _update_performance_metrics(self) -> None:
        """Update performance metrics."""
        if self.processing_times:
            self.stats.avg_processing_time = sum(self.processing_times) / len(self.processing_times)
        
        # Calculate files per minute
        if self.stats.elapsed_time.total_seconds() > 0:
            completed = self.stats.completed_files + self.stats.failed_files
            minutes = self.stats.elapsed_time.total_seconds() / 60
            self.stats.files_per_minute = completed / minutes if minutes > 0 else 0
    
    def _update_main_description(self) -> None:
        """Update main progress bar description."""
        if not self.main_pbar:
            return
        
        success_rate = self.stats.success_rate
        eta = self.stats.estimated_remaining
        
        desc = f"📁 Files ✅{self.stats.completed_files} ❌{self.stats.failed_files} ⏭️{self.stats.skipped_files}"
        desc += f" | 📊{success_rate:.1f}% | ⏱️ETA: {eta}"
        
        self.main_pbar.set_description(desc)
    
    def finish_processing(self) -> None:
        """Finish the processing session."""
        self.stats.end_time = datetime.now()
        
        # Close progress bars
        if self.current_file_pbar:
            self.current_file_pbar.close()
        if self.main_pbar:
            self.main_pbar.close()
        
        # Print final summary
        self._print_final_summary()
    
    def _print_final_summary(self) -> None:
        """Print final processing summary."""
        print("\n" + "=" * 60)
        print("🎉 Batch Processing Complete!")
        print("=" * 60)
        
        # Basic stats
        print(f"📊 Total Files: {self.stats.total_files}")
        print(f"✅ Successful: {self.stats.completed_files}")
        print(f"❌ Failed: {self.stats.failed_files}")
        print(f"⏭️ Skipped: {self.stats.skipped_files}")
        print(f"📈 Success Rate: {self.stats.success_rate:.1f}%")
        
        # Time stats
        elapsed = self.stats.elapsed_time
        print(f"\n⏱️ Time Statistics:")
        print(f"   Total Time: {elapsed}")
        print(f"   Avg per File: {self.stats.avg_processing_time:.2f}s")
        print(f"   Processing Speed: {self.stats.files_per_minute:.1f} files/min")
        
        # Size stats
        if self.stats.total_size_mb > 0:
            print(f"\n💾 Size Statistics:")
            print(f"   Total Size: {self.stats.total_size_mb:.2f} MB")
            print(f"   Processed: {self.stats.processed_size_mb:.2f} MB")
            print(f"   Processing Rate: {self.stats.processed_size_mb / elapsed.total_seconds() * 60:.2f} MB/min")
        
        print("=" * 60)
    
    def get_current_stats(self) -> Dict[str, Any]:
        """Get current processing statistics."""
        return {
            "total_files": self.stats.total_files,
            "completed": self.stats.completed_files,
            "failed": self.stats.failed_files,
            "skipped": self.stats.skipped_files,
            "success_rate": self.stats.success_rate,
            "elapsed_time": str(self.stats.elapsed_time),
            "eta": str(self.stats.estimated_remaining),
            "avg_processing_time": self.stats.avg_processing_time,
            "files_per_minute": self.stats.files_per_minute
        }


def test_progress_tracker():
    """Test the progress tracker functionality."""
    print("🧪 Testing Progress Tracker")
    print("=" * 60)
    
    # Simulate processing 5 files
    total_files = 5
    tracker = ProgressTracker(total_files=total_files, total_size_mb=10.5)
    
    try:
        tracker.start_processing()
        
        # Simulate file processing
        for i in range(total_files):
            filename = f"test_file_{i+1}.pdf"
            file_size = 2.1
            
            # Start file
            tracker.start_file(filename, file_size)
            
            # Simulate progress updates
            for progress in [0, 25, 50, 75, 100]:
                tracker.update_file_progress(progress)
                time.sleep(0.2)  # Simulate processing time
            
            # Complete file (simulate some failures)
            success = i != 2  # Fail the 3rd file
            processing_time = 1.0 + (i * 0.5)
            
            if success:
                tracker.complete_file(success, processing_time, file_size)
            else:
                tracker.complete_file(False, processing_time, 0)
        
        # Finish processing
        tracker.finish_processing()
        
        # Show final stats
        final_stats = tracker.get_current_stats()
        print(f"\n📋 Final Statistics: {final_stats}")
        
        print("\n✅ Progress Tracker Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        tracker.finish_processing()


if __name__ == "__main__":
    test_progress_tracker()
