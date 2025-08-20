#!/usr/bin/env python3
"""
Batch Processing System for LocalLLM
Step 3: Error Handler - Robust error handling with skip continuation
"""

import sys
import traceback
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


class ErrorSeverity(Enum):
    """Error severity levels."""
    LOW = "low"         # Non-critical, continue processing
    MEDIUM = "medium"   # Significant but recoverable
    HIGH = "high"       # Critical but file-specific
    CRITICAL = "critical"  # System-level failure


@dataclass
class ProcessingError:
    """Container for processing error information."""
    file_path: Path
    error_type: str
    error_message: str
    severity: ErrorSeverity
    timestamp: datetime
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    def __str__(self) -> str:
        return f"[{self.severity.value.upper()}] {self.file_path.name}: {self.error_message}"


class ErrorHandler:
    """
    Comprehensive error handling for batch processing.
    Provides error categorization, logging, and recovery strategies.
    """
    
    def __init__(self, max_consecutive_errors: int = 5, continue_on_error: bool = True):
        """
        Initialize error handler.
        
        Args:
            max_consecutive_errors: Max consecutive errors before stopping
            continue_on_error: Whether to continue processing after errors
        """
        self.max_consecutive_errors = max_consecutive_errors
        self.continue_on_error = continue_on_error
        
        # Error tracking
        self.errors: List[ProcessingError] = []
        self.consecutive_errors = 0
        self.total_errors = 0
        
        # Error categorization
        self.error_categories = {
            "file_access": ["FileNotFoundError", "PermissionError", "IsADirectoryError"],
            "format_error": ["UnicodeDecodeError", "PDFSyntaxError", "ParseError"],
            "memory_error": ["MemoryError", "OutOfMemoryError"],
            "llm_error": ["LLMError", "TimeoutError", "ConnectionError"],
            "system_error": ["OSError", "SystemError", "RuntimeError"]
        }
        
        # Recovery strategies
        self.recovery_strategies = {
            "file_access": self._handle_file_access_error,
            "format_error": self._handle_format_error,
            "memory_error": self._handle_memory_error,
            "llm_error": self._handle_llm_error,
            "system_error": self._handle_system_error
        }
    
    def handle_error(
        self, 
        file_path: Path, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, str]:
        """
        Handle processing error for a specific file.
        
        Args:
            file_path: Path to the file that caused the error
            error: The exception that occurred
            context: Additional context information
            
        Returns:
            Tuple of (should_continue, recovery_action)
        """
        # Create error record
        error_type = type(error).__name__
        error_message = str(error)
        severity = self._determine_severity(error_type, error_message)
        
        processing_error = ProcessingError(
            file_path=file_path,
            error_type=error_type,
            error_message=error_message,
            severity=severity,
            timestamp=datetime.now(),
            stack_trace=traceback.format_exc(),
            context=context or {}
        )
        
        # Log error
        self._log_error(processing_error)
        
        # Store error
        self.errors.append(processing_error)
        self.total_errors += 1
        
        # Update consecutive error count
        self.consecutive_errors += 1
        
        # Determine recovery action
        category = self._categorize_error(error_type)
        recovery_action = "skip"
        
        if category in self.recovery_strategies:
            try:
                recovery_action = self.recovery_strategies[category](processing_error)
            except Exception as recovery_error:
                self._log_error(ProcessingError(
                    file_path=file_path,
                    error_type="RecoveryError",
                    error_message=f"Recovery failed: {recovery_error}",
                    severity=ErrorSeverity.HIGH,
                    timestamp=datetime.now()
                ))
        
        # Determine if processing should continue
        should_continue = self._should_continue_processing(processing_error)
        
        return should_continue, recovery_action
    
    def reset_consecutive_errors(self) -> None:
        """Reset consecutive error counter (call on successful processing)."""
        self.consecutive_errors = 0
    
    def _determine_severity(self, error_type: str, error_message: str) -> ErrorSeverity:
        """Determine error severity based on type and message."""
        # Critical errors that should stop processing
        critical_errors = ["MemoryError", "SystemError", "KeyboardInterrupt"]
        if error_type in critical_errors:
            return ErrorSeverity.CRITICAL
        
        # High severity errors
        high_severity = ["PermissionError", "OSError"]
        if error_type in high_severity:
            return ErrorSeverity.HIGH
        
        # Medium severity errors
        medium_severity = ["TimeoutError", "ConnectionError", "LLMError"]
        if error_type in medium_severity:
            return ErrorSeverity.MEDIUM
        
        # Default to low severity
        return ErrorSeverity.LOW
    
    def _categorize_error(self, error_type: str) -> str:
        """Categorize error type for recovery strategy."""
        for category, error_types in self.error_categories.items():
            if error_type in error_types:
                return category
        return "unknown"
    
    def _should_continue_processing(self, error: ProcessingError) -> bool:
        """Determine if processing should continue after an error."""
        # Critical errors stop processing
        if error.severity == ErrorSeverity.CRITICAL:
            return False
        
        # Check consecutive error limit
        if self.consecutive_errors >= self.max_consecutive_errors:
            return False
        
        # Check global continue setting
        return self.continue_on_error
    
    def _log_error(self, error: ProcessingError) -> None:
        """Log error information."""
        log_level = {
            ErrorSeverity.LOW: logging.WARNING,
            ErrorSeverity.MEDIUM: logging.ERROR,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }[error.severity]
        
        # Create logger for this session if not exists
        logger = logging.getLogger("batch_processing")
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s | %(levelname)s | %(message)s'
            ))
            logger.addHandler(handler)
            logger.setLevel(logging.WARNING)
        
        logger.log(log_level, str(error))
        
        # Also print to console with safe symbols
        severity_symbols = {
            ErrorSeverity.LOW: "[WARNING]",
            ErrorSeverity.MEDIUM: "[ERROR]",
            ErrorSeverity.HIGH: "[ALERT]",
            ErrorSeverity.CRITICAL: "[CRITICAL]"
        }
        
        print(f"{severity_symbols[error.severity]} {error}")
    
    # Recovery strategy implementations
    def _handle_file_access_error(self, error: ProcessingError) -> str:
        """Handle file access errors."""
        if "PermissionError" in error.error_type:
            return "skip_permission"
        elif "FileNotFoundError" in error.error_type:
            return "skip_missing"
        return "skip"
    
    def _handle_format_error(self, error: ProcessingError) -> str:
        """Handle file format errors."""
        # Could implement format conversion or alternative parsers
        return "skip_format"
    
    def _handle_memory_error(self, error: ProcessingError) -> str:
        """Handle memory errors."""
        # Could implement chunk processing or file size reduction
        return "skip_large"
    
    def _handle_llm_error(self, error: ProcessingError) -> str:
        """Handle LLM-related errors."""
        # Could implement retry with different parameters
        return "retry_llm"
    
    def _handle_system_error(self, error: ProcessingError) -> str:
        """Handle system-level errors."""
        return "skip_system"
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get comprehensive error summary."""
        if not self.errors:
            return {"total_errors": 0, "error_rate": 0.0}
        
        # Group errors by type and severity
        by_type = {}
        by_severity = {}
        
        for error in self.errors:
            # By type
            if error.error_type not in by_type:
                by_type[error.error_type] = 0
            by_type[error.error_type] += 1
            
            # By severity
            severity_str = error.severity.value
            if severity_str not in by_severity:
                by_severity[severity_str] = 0
            by_severity[severity_str] += 1
        
        return {
            "total_errors": self.total_errors,
            "consecutive_errors": self.consecutive_errors,
            "errors_by_type": by_type,
            "errors_by_severity": by_severity,
            "most_recent_errors": [str(e) for e in self.errors[-5:]],  # Last 5 errors
        }
    
    def print_error_report(self) -> None:
        """Print detailed error report."""
        if not self.errors:
            print("✅ No errors encountered during processing!")
            return
        
        print("\n" + "="*60)
        print("📋 Error Report")
        print("="*60)
        
        summary = self.get_error_summary()
        print(f"📊 Total Errors: {summary['total_errors']}")
        print(f"🔄 Consecutive: {summary['consecutive_errors']}")
        
        print("\n📈 Errors by Type:")
        for error_type, count in summary['errors_by_type'].items():
            print(f"   • {error_type}: {count}")
        
        print("\n📊 Errors by Severity:")
        for severity, count in summary['errors_by_severity'].items():
            print(f"   • {severity.upper()}: {count}")
        
        if summary['most_recent_errors']:
            print("\n🔍 Recent Errors:")
            for error in summary['most_recent_errors']:
                print(f"   • {error}")
        
        print("="*60)


def test_error_handler():
    """Test the error handler functionality."""
    print("🧪 Testing Error Handler")
    print("=" * 60)
    
    handler = ErrorHandler(max_consecutive_errors=3, continue_on_error=True)
    
    # Test various error scenarios
    test_files = [
        (Path("file1.pdf"), FileNotFoundError("File not found")),
        (Path("file2.txt"), PermissionError("Access denied")),
        (Path("file3.pdf"), UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")),
        (Path("file4.html"), TimeoutError("Request timeout")),
        (Path("file5.txt"), MemoryError("Out of memory")),
    ]
    
    print("🔍 Testing error handling scenarios:")
    
    for file_path, error in test_files:
        print(f"\n📄 Processing: {file_path}")
        should_continue, recovery_action = handler.handle_error(
            file_path, 
            error, 
            {"file_size": "1.5MB", "attempt": 1}
        )
        print(f"   Continue: {should_continue}, Action: {recovery_action}")
        
        # Simulate some successful processing to reset consecutive errors
        if file_path.name != "file5.txt":  # Don't reset on memory error
            handler.reset_consecutive_errors()
    
    # Print error report
    handler.print_error_report()
    
    # Test summary
    summary = handler.get_error_summary()
    print(f"\n📋 Error Summary: {summary}")
    
    print("\n✅ Error Handler Test Complete!")


if __name__ == "__main__":
    test_error_handler()
