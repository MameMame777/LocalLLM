#!/usr/bin/env python3
"""
Batch Processing System for LocalLLM
Step 4: Task Manager - Parallel processing with worker management
"""

import sys
import time
import multiprocessing as mp
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable, Tuple
from dataclasses import dataclass
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from queue import Queue
import threading

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from batch_processing.file_scanner import FileInfo
from batch_processing.progress_tracker import ProgressTracker
from batch_processing.error_handler import ErrorHandler


@dataclass
class ProcessingTask:
    """Task container for parallel processing."""
    file_info: FileInfo
    task_id: int
    parameters: Dict[str, Any]
    priority: int = 0  # Higher number = higher priority


@dataclass
class TaskResult:
    """Result container for completed tasks."""
    task_id: int
    file_path: Path
    success: bool
    result_data: Any = None
    error_message: str = ""
    processing_time: float = 0.0
    file_size_mb: float = 0.0


class TaskManager:
    """
    Advanced task manager for parallel document processing.
    Supports both multiprocessing and threading with intelligent worker management.
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        use_multiprocessing: bool = True,
        chunk_size: int = 1
    ):
        """
        Initialize task manager.
        
        Args:
            max_workers: Maximum number of worker processes/threads
            use_multiprocessing: Use multiprocessing vs threading
            chunk_size: Number of tasks per worker batch
        """
        # Determine optimal worker count
        if max_workers is None:
            cpu_count = mp.cpu_count()
            # Leave one CPU for main process and one for system
            max_workers = max(1, cpu_count - 2)
        
        self.max_workers = max_workers
        self.use_multiprocessing = use_multiprocessing
        self.chunk_size = chunk_size
        
        # Task management
        self.tasks: List[ProcessingTask] = []
        self.results: List[TaskResult] = []
        self.task_counter = 0
        
        # Worker management
        self.executor = None
        self.active_workers = 0
        
        print(f"🔧 TaskManager initialized:")
        print(f"   Workers: {max_workers} ({'multiprocessing' if use_multiprocessing else 'threading'})")
        print(f"   CPU cores: {mp.cpu_count()}")
    
    def add_task(
        self, 
        file_info: FileInfo, 
        parameters: Optional[Dict[str, Any]] = None,
        priority: int = 0
    ) -> int:
        """
        Add a processing task to the queue.
        
        Args:
            file_info: File information
            parameters: Processing parameters
            priority: Task priority (higher = processed first)
            
        Returns:
            Task ID
        """
        task_id = self.task_counter
        self.task_counter += 1
        
        task = ProcessingTask(
            file_info=file_info,
            task_id=task_id,
            parameters=parameters or {},
            priority=priority
        )
        
        self.tasks.append(task)
        return task_id
    
    def add_tasks_batch(
        self, 
        file_infos: List[FileInfo], 
        parameters: Optional[Dict[str, Any]] = None
    ) -> List[int]:
        """
        Add multiple tasks in batch.
        
        Args:
            file_infos: List of file information objects
            parameters: Common parameters for all tasks
            
        Returns:
            List of task IDs
        """
        task_ids = []
        for file_info in file_infos:
            # Assign priority based on file size (smaller files first)
            priority = int(100 - file_info.size_mb)  # Inverse size priority
            task_id = self.add_task(file_info, parameters, priority)
            task_ids.append(task_id)
        
        return task_ids
    
    def process_tasks(
        self,
        processing_function: Callable,
        progress_tracker: Optional[ProgressTracker] = None,
        error_handler: Optional[ErrorHandler] = None
    ) -> List[TaskResult]:
        """
        Process all tasks in parallel.
        
        Args:
            processing_function: Function to process each file
            progress_tracker: Optional progress tracking
            error_handler: Optional error handling
            
        Returns:
            List of task results
        """
        if not self.tasks:
            print("⚠️ No tasks to process")
            return []
        
        # Sort tasks by priority
        sorted_tasks = sorted(self.tasks, key=lambda t: t.priority, reverse=True)
        
        print(f"🚀 Starting parallel processing of {len(sorted_tasks)} tasks")
        print(f"   Workers: {self.max_workers}")
        print(f"   Mode: {'Multiprocessing' if self.use_multiprocessing else 'Threading'}")
        
        # Initialize results
        self.results.clear()
        
        # Choose executor type
        executor_class = ProcessPoolExecutor if self.use_multiprocessing else ThreadPoolExecutor
        
        try:
            with executor_class(max_workers=self.max_workers) as executor:
                self.executor = executor
                
                # Submit all tasks
                future_to_task = {}
                for task in sorted_tasks:
                    future = executor.submit(
                        self._process_single_task,
                        task,
                        processing_function
                    )
                    future_to_task[future] = task
                
                # Process completed tasks
                for future in as_completed(future_to_task):
                    task = future_to_task[future]
                    
                    try:
                        result = future.result()
                        self.results.append(result)
                        
                        # Update progress tracker
                        if progress_tracker:
                            progress_tracker.complete_file(
                                success=result.success,
                                processing_time=result.processing_time,
                                file_size_mb=result.file_size_mb
                            )
                        
                        # Handle errors
                        if not result.success and error_handler:
                            error = Exception(result.error_message)
                            should_continue, _ = error_handler.handle_error(
                                result.file_path, error
                            )
                            if not should_continue:
                                print("🛑 Stopping due to critical error")
                                break
                        else:
                            # Reset consecutive error count on success
                            if error_handler:
                                error_handler.reset_consecutive_errors()
                        
                    except Exception as e:
                        # Handle executor-level errors
                        error_result = TaskResult(
                            task_id=task.task_id,
                            file_path=task.file_info.path,
                            success=False,
                            error_message=f"Executor error: {str(e)}",
                            processing_time=0.0,
                            file_size_mb=task.file_info.size_mb
                        )
                        self.results.append(error_result)
                        
                        if error_handler:
                            should_continue, _ = error_handler.handle_error(
                                task.file_info.path, e
                            )
                            if not should_continue:
                                break
        
        finally:
            self.executor = None
        
        print(f"✅ Parallel processing completed: {len(self.results)} results")
        return self.results
    
    @staticmethod
    def _process_single_task(task: ProcessingTask, processing_function: Callable) -> TaskResult:
        """
        Process a single task (runs in worker process/thread).
        
        Args:
            task: Task to process
            processing_function: Function to process the file
            
        Returns:
            Task result
        """
        start_time = time.time()
        
        try:
            # Call the processing function
            result_data = processing_function(
                task.file_info.path,
                **task.parameters
            )
            
            processing_time = time.time() - start_time
            
            return TaskResult(
                task_id=task.task_id,
                file_path=task.file_info.path,
                success=True,
                result_data=result_data,
                processing_time=processing_time,
                file_size_mb=task.file_info.size_mb
            )
        
        except Exception as e:
            processing_time = time.time() - start_time
            
            return TaskResult(
                task_id=task.task_id,
                file_path=task.file_info.path,
                success=False,
                error_message=str(e),
                processing_time=processing_time,
                file_size_mb=task.file_info.size_mb
            )
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get comprehensive processing statistics."""
        if not self.results:
            return {"total_tasks": 0, "completed": 0, "failed": 0}
        
        successful = [r for r in self.results if r.success]
        failed = [r for r in self.results if not r.success]
        
        total_time = sum(r.processing_time for r in self.results)
        total_size = sum(r.file_size_mb for r in self.results)
        
        return {
            "total_tasks": len(self.results),
            "completed": len(successful),
            "failed": len(failed),
            "success_rate": len(successful) / len(self.results) * 100,
            "total_processing_time": total_time,
            "total_size_mb": total_size,
            "avg_time_per_file": total_time / len(self.results),
            "processing_speed_mb_per_second": total_size / total_time if total_time > 0 else 0,
            "parallelization_efficiency": self._calculate_efficiency()
        }
    
    def _calculate_efficiency(self) -> float:
        """Calculate parallelization efficiency."""
        if not self.results:
            return 0.0
        
        # Theoretical minimum time if perfectly parallel
        max_processing_time = max(r.processing_time for r in self.results)
        
        # Actual total time (sum of all processing times)
        total_processing_time = sum(r.processing_time for r in self.results)
        
        # Efficiency = theoretical_optimal / actual_performance
        if total_processing_time > 0:
            return (max_processing_time * self.max_workers) / total_processing_time * 100
        return 0.0


# Mock processing function for testing
def mock_processing_function(file_path: Path, **kwargs) -> str:
    """Mock processing function for testing."""
    # Simulate processing time based on file size
    file_size = file_path.stat().st_size if file_path.exists() else 1000
    processing_time = max(0.5, file_size / 1000000)  # 1 second per MB
    
    time.sleep(processing_time)
    
    # Simulate occasional failures
    import random
    if random.random() < 0.1:  # 10% failure rate
        raise Exception(f"Mock processing failed for {file_path.name}")
    
    return f"Processed {file_path.name} successfully"


def test_task_manager():
    """Test the task manager functionality."""
    print("🧪 Testing Task Manager")
    print("=" * 60)
    
    # Create mock file infos
    from batch_processing.file_scanner import FileInfo
    
    mock_files = [
        FileInfo(Path(f"test_file_{i}.pdf"), 1024 * 1024 * (i + 1), "PDF Document", "application/pdf")
        for i in range(5)
    ]
    
    # Initialize components
    task_manager = TaskManager(max_workers=2, use_multiprocessing=False)  # Use threading for testing
    progress_tracker = ProgressTracker(total_files=len(mock_files))
    error_handler = ErrorHandler(max_consecutive_errors=2)
    
    try:
        # Add tasks
        print("\n📋 Adding tasks...")
        task_ids = task_manager.add_tasks_batch(mock_files)
        print(f"✅ Added {len(task_ids)} tasks")
        
        # Start processing
        progress_tracker.start_processing()
        
        # Process tasks
        results = task_manager.process_tasks(
            processing_function=mock_processing_function,
            progress_tracker=progress_tracker,
            error_handler=error_handler
        )
        
        # Finish processing
        progress_tracker.finish_processing()
        
        # Print results
        print(f"\n📊 Processing Results:")
        for result in results:
            status = "✅" if result.success else "❌"
            print(f"   {status} {result.file_path.name}: {result.processing_time:.2f}s")
            if not result.success:
                print(f"      Error: {result.error_message}")
        
        # Print statistics
        stats = task_manager.get_processing_stats()
        print(f"\n📈 Performance Statistics:")
        print(f"   Success Rate: {stats['success_rate']:.1f}%")
        print(f"   Avg Time/File: {stats['avg_time_per_file']:.2f}s")
        print(f"   Parallelization Efficiency: {stats['parallelization_efficiency']:.1f}%")
        
        # Print error report
        error_handler.print_error_report()
        
        print("\n✅ Task Manager Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        progress_tracker.finish_processing()


if __name__ == "__main__":
    test_task_manager()
