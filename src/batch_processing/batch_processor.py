#!/usr/bin/env python3
"""
Batch Processing System for LocalLLM
Step 6: Integrated Batch Processor - Complete batch processing system
"""

import sys
import time
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable
from datetime import datetime
import argparse
from dataclasses import dataclass

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from batch_processing.file_scanner import FileScanner, FileInfo
from batch_processing.progress_tracker import ProgressTracker
from batch_processing.error_handler import ErrorHandler
from batch_processing.task_manager import TaskManager
from batch_processing.report_generator import ReportGenerator


@dataclass
class ProcessingResult:
    """
    Result of processing a single file
    """
    file_path: Path
    status: str  # "success", "error", "skipped"
    summary: str
    processing_time: float
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class BatchProcessor:
    """
    Complete batch processing system for LocalLLM.
    Integrates all components for efficient document processing.
    """
    
    def __init__(
        self,
        max_workers: Optional[int] = None,
        use_multiprocessing: bool = True,
        max_consecutive_errors: int = 5,
        continue_on_error: bool = True,
        output_directory: Path = Path("output/batch")
    ):
        """
        Initialize batch processor.
        
        Args:
            max_workers: Maximum number of worker processes/threads
            use_multiprocessing: Use multiprocessing vs threading
            max_consecutive_errors: Max consecutive errors before stopping
            continue_on_error: Whether to continue processing after errors
            output_directory: Directory for output files and reports
        """
        # Initialize components
        self.file_scanner = FileScanner(recursive=True, include_hidden=False)
        self.task_manager = TaskManager(max_workers, use_multiprocessing)
        self.error_handler = ErrorHandler(max_consecutive_errors, continue_on_error)
        self.report_generator = ReportGenerator(output_directory / "reports")
        
        # Processing state
        self.progress_tracker: Optional[ProgressTracker] = None
        self.session_id = ""
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        
        # Configuration
        self.output_directory = output_directory
        self.output_directory.mkdir(parents=True, exist_ok=True)
        
        print("🚀 BatchProcessor initialized")
        print(f"   Output Directory: {output_directory}")
        print(f"   Max Workers: {self.task_manager.max_workers}")
        print(f"   Processing Mode: {'Multiprocessing' if use_multiprocessing else 'Threading'}")
    
    def process_directory(
        self,
        directory: Path,
        processing_function: Callable,
        parameters: Optional[Dict[str, Any]] = None,
        file_extensions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process all supported files in a directory.
        
        Args:
            directory: Directory containing files to process
            processing_function: Function to process each file
            parameters: Parameters to pass to processing function
            file_extensions: Specific file extensions to process
            
        Returns:
            Processing results summary
        """
        self.session_id = f"batch_{int(time.time())}"
        self.start_time = datetime.now()
        
        print(f"\n🎯 Starting Batch Processing Session: {self.session_id}")
        print("=" * 60)
        
        try:
            # Step 1: Scan files
            print("🔍 Step 1: Scanning files...")
            categorized_files = self.file_scanner.scan_directory(directory)
            
            if not self.file_scanner.scanned_files:
                print("⚠️ No supported files found")
                return {"status": "no_files", "message": "No supported files found"}
            
            # Filter by extensions if specified
            files_to_process = self.file_scanner.scanned_files
            if file_extensions:
                files_to_process = [
                    f for f in files_to_process 
                    if f.path.suffix.lower() in file_extensions
                ]
            
            if not files_to_process:
                print("⚠️ No files match the specified extensions")
                return {"status": "no_matching_files", "message": "No files match specified extensions"}
            
            total_size_mb = sum(f.size_mb for f in files_to_process)
            
            # Step 2: Initialize progress tracking
            print(f"\n📊 Step 2: Initializing processing...")
            self.progress_tracker = ProgressTracker(
                total_files=len(files_to_process),
                total_size_mb=total_size_mb
            )
            
            # Step 3: Add tasks to manager
            print(f"📋 Step 3: Preparing {len(files_to_process)} tasks...")
            task_ids = self.task_manager.add_tasks_batch(
                files_to_process,
                parameters or {}
            )
            
            # Step 4: Start processing
            print("🚀 Step 4: Starting parallel processing...")
            self.progress_tracker.start_processing()
            
            # Process all tasks
            task_results = self.task_manager.process_tasks(
                processing_function=processing_function,
                progress_tracker=self.progress_tracker,
                error_handler=self.error_handler
            )
            
            # Step 5: Save individual result files
            print("\n💾 Step 5: Saving individual result files...")
            saved_individual_files = self._save_individual_results(task_results)
            
            # Step 6: Finish processing
            self.end_time = datetime.now()
            self.progress_tracker.finish_processing()
            
            # Step 7: Generate comprehensive report
            print("\n📋 Step 6: Generating reports...")
            report = self.report_generator.generate_report(
                session_id=self.session_id,
                start_time=self.start_time,
                end_time=self.end_time,
                task_results=task_results,
                error_handler=self.error_handler,
                file_infos=files_to_process
            )
            
            # Save reports in multiple formats
            report_files = self._save_all_reports(report)
            
            # Print final summary
            self.report_generator.print_summary_report(report)
            
            print(f"\n📁 Reports saved:")
            for format_name, file_path in report_files.items():
                print(f"   📄 {format_name}: {file_path}")
            
            return {
                "status": "completed",
                "session_id": self.session_id,
                "total_files": len(files_to_process),
                "successful_files": len([r for r in task_results if r.success]),
                "failed_files": len([r for r in task_results if not r.success]),
                "success_rate": report.success_rate,
                "processing_time": str(self.end_time - self.start_time),
                "report_files": report_files,
                "individual_files": saved_individual_files,
                "task_results": task_results
            }
        
        except Exception as e:
            self.end_time = datetime.now()
            if self.progress_tracker:
                self.progress_tracker.finish_processing()
            
            print(f"[CRITICAL] Batch processing failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "session_id": self.session_id
            }
    
    def _save_individual_results(self, task_results: List[Any]) -> List[str]:
        """Save individual processing results to files.
        
        Args:
            task_results: List of task results from processing
            
        Returns:
            List of saved filenames
        """
        processed_dir = self.output_directory / "processed"
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        saved_files = []
        for result in task_results:
            if result.success and result.result_data:
                try:
                    # Create safe filename from original file
                    original_name = result.file_path.stem
                    file_extension = result.file_path.suffix
                    
                    # Generate descriptive filename for individual file summary
                    # Format: {original_name}_summary_ja.md
                    safe_filename = f"{original_name}_summary_ja.md"
                    output_file = processed_dir / safe_filename
                    
                    # Save result data to file with UTF-8 encoding
                    with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                        f.write(str(result.result_data))
                    
                    saved_files.append(safe_filename)
                    print(f"   Saved: {safe_filename}")
                    
                except Exception as e:
                    print(f"   Failed to save {result.file_path.name}: {e}")
        
        print(f"Saved {len(saved_files)} individual result files to: {processed_dir}")
        return saved_files
    
    def _save_all_reports(self, report) -> Dict[str, Path]:
        """Save reports in all supported formats."""
        report_files = {}
        
        try:
            report_files["JSON"] = self.report_generator.save_report_json(report)
            report_files["CSV"] = self.report_generator.save_report_csv(report)
            report_files["HTML"] = self.report_generator.save_report_html(report)
            report_files["Markdown"] = self.report_generator.save_report_markdown(report)
        except Exception as e:
            print(f"Error saving reports: {e}")
        
        return report_files
    
    def get_processing_summary(self) -> Dict[str, Any]:
        """Get current processing session summary."""
        if not self.progress_tracker:
            return {"status": "not_started"}
        
        stats = self.progress_tracker.get_current_stats()
        task_stats = self.task_manager.get_processing_stats()
        error_stats = self.error_handler.get_error_summary()
        
        return {
            "session_id": self.session_id,
            "progress": stats,
            "performance": task_stats,
            "errors": error_stats
        }


def create_mock_processing_function():
    """Create a mock processing function for testing."""
    def mock_process_file(file_path: Path, **kwargs) -> str:
        """Mock file processing function."""
        # Simulate processing time
        time.sleep(0.1 + (file_path.stat().st_size / 10000) if file_path.exists() else 0.1)
        
        # Simulate occasional failures
        import random
        if random.random() < 0.15:  # 15% failure rate
            raise Exception(f"Mock processing failed for {file_path.name}")
        
        return f"Successfully processed {file_path.name} - Generated summary with {random.randint(50, 200)} words"
    
    return mock_process_file


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(description="LocalLLM Batch Processor")
    parser.add_argument("directory", type=Path, help="Directory to process")
    parser.add_argument("--workers", type=int, help="Number of worker processes")
    parser.add_argument("--extensions", nargs="+", help="File extensions to process")
    parser.add_argument("--output", type=Path, default=Path("output/batch"), help="Output directory")
    parser.add_argument("--threading", action="store_true", help="Use threading instead of multiprocessing")
    
    args = parser.parse_args()
    
    # Initialize batch processor
    processor = BatchProcessor(
        max_workers=args.workers,
        use_multiprocessing=not args.threading,
        output_directory=args.output
    )
    
    # Create mock processing function
    processing_function = create_mock_processing_function()
    
    # Process directory
    results = processor.process_directory(
        directory=args.directory,
        processing_function=processing_function,
        file_extensions=args.extensions
    )
    
    print(f"\n🎉 Batch processing completed with status: {results['status']}")


def test_batch_processor():
    """Test the complete batch processor."""
    print("🧪 Testing Complete Batch Processor")
    print("=" * 60)
    
    # Initialize processor
    processor = BatchProcessor(
        max_workers=2,
        use_multiprocessing=False,  # Use threading for testing
        output_directory=Path("output/test_batch")
    )
    
    # Test with data directory
    test_directory = Path("data")
    if not test_directory.exists():
        print(f"❌ Test directory not found: {test_directory}")
        return
    
    # Create mock processing function
    processing_function = create_mock_processing_function()
    
    # Process directory
    results = processor.process_directory(
        directory=test_directory,
        processing_function=processing_function,
        parameters={"test_mode": True}
    )
    
    print(f"\n🎯 Final Results: {results}")
    print("\n✅ Batch Processor Test Complete!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        main()
    else:
        test_batch_processor()
