"""
Batch Processing Module for LocalLLM
Provides efficient batch processing capabilities for multiple documents.
"""

from .file_scanner import FileScanner, FileInfo

__version__ = "1.0.0"
__all__ = ["FileScanner", "FileInfo"]
