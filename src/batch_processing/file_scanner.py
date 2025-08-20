#!/usr/bin/env python3
"""
Batch Processing System for LocalLLM
Step 1: File Scanner - Automatic file detection in folders
"""

import os
import sys
from pathlib import Path
from typing import List, Set, Dict, Tuple
from dataclasses import dataclass
import mimetypes

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@dataclass
class FileInfo:
    """File information container."""
    path: Path
    size: int
    file_type: str
    mime_type: str
    
    @property
    def size_mb(self) -> float:
        """File size in MB."""
        return self.size / (1024 * 1024)
    
    @property
    def format_type(self) -> str:
        """Alias for file_type for backward compatibility."""
        return self.file_type


class FileScanner:
    """
    Advanced file scanner for batch processing.
    Automatically detects supported files in directories.
    """
    
    # Supported file extensions
    SUPPORTED_EXTENSIONS = {
        '.pdf': 'PDF Document',
        '.txt': 'Text File',
        '.html': 'HTML Document',
        '.htm': 'HTML Document',
        '.md': 'Markdown Document',
        '.docx': 'Word Document',
        '.json': 'JSON Document',
        '.rtf': 'Rich Text Format'
    }
    
    # File size limits (in MB)
    MAX_FILE_SIZE_MB = 100
    MIN_FILE_SIZE_KB = 1
    
    def __init__(self, recursive: bool = True, include_hidden: bool = False):
        """
        Initialize file scanner.
        
        Args:
            recursive: Include subdirectories
            include_hidden: Include hidden files/directories
        """
        self.recursive = recursive
        self.include_hidden = include_hidden
        self.scanned_files: List[FileInfo] = []
        self.errors: List[Tuple[Path, str]] = []
    
    def scan_directory(self, directory: Path) -> Dict[str, List[FileInfo]]:
        """
        Scan directory for supported files.
        
        Args:
            directory: Directory path to scan
            
        Returns:
            Dictionary categorized by file type
        """
        print(f"🔍 Scanning directory: {directory}")
        
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        
        if not directory.is_dir():
            raise ValueError(f"Path is not a directory: {directory}")
        
        self.scanned_files.clear()
        self.errors.clear()
        
        # Scan files
        try:
            if self.recursive:
                pattern = "**/*"
            else:
                pattern = "*"
            
            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    self._process_file(file_path)
                    
        except Exception as e:
            self.errors.append((directory, f"Scan error: {str(e)}"))
        
        # Categorize results
        categorized = self._categorize_files()
        
        # Print summary
        self._print_scan_summary(directory, categorized)
        
        return categorized
    
    def _process_file(self, file_path: Path) -> None:
        """Process individual file."""
        try:
            # Skip hidden files if not included
            if not self.include_hidden and file_path.name.startswith('.'):
                return
            
            # Check if supported extension
            extension = file_path.suffix.lower()
            if extension not in self.SUPPORTED_EXTENSIONS:
                return
            
            # Get file stats
            stat = file_path.stat()
            file_size = stat.st_size
            
            # Size validation
            # JSONファイルは小さくても有効なデータを含む可能性があるため、最小サイズ制限を緩和
            min_size_bytes = 50 if extension == '.json' else self.MIN_FILE_SIZE_KB * 1024
            if file_size < min_size_bytes:
                self.errors.append((file_path, f"File too small: {file_size} bytes"))
                return
            
            if file_size > self.MAX_FILE_SIZE_MB * 1024 * 1024:
                self.errors.append((file_path, f"File too large: {file_size / 1024 / 1024:.1f} MB"))
                return
            
            # Get MIME type
            mime_type, _ = mimetypes.guess_type(str(file_path))
            if not mime_type:
                mime_type = "application/octet-stream"
            
            # Create file info
            file_info = FileInfo(
                path=file_path,
                size=file_size,
                file_type=self.SUPPORTED_EXTENSIONS[extension],
                mime_type=mime_type
            )
            
            self.scanned_files.append(file_info)
            
        except Exception as e:
            self.errors.append((file_path, f"Processing error: {str(e)}"))
    
    def _categorize_files(self) -> Dict[str, List[FileInfo]]:
        """Categorize files by type."""
        categorized = {}
        
        for file_info in self.scanned_files:
            file_type = file_info.file_type
            if file_type not in categorized:
                categorized[file_type] = []
            categorized[file_type].append(file_info)
        
        return categorized
    
    def _print_scan_summary(self, directory: Path, categorized: Dict[str, List[FileInfo]]) -> None:
        """Print scan summary."""
        print("\n📊 Scan Results Summary")
        print("=" * 50)
        
        total_files = len(self.scanned_files)
        total_size = sum(f.size for f in self.scanned_files)
        
        print(f"📁 Directory: {directory}")
        print(f"📄 Total Files: {total_files}")
        print(f"💾 Total Size: {total_size / 1024 / 1024:.2f} MB")
        
        if categorized:
            print("\n📋 Files by Type:")
            for file_type, files in categorized.items():
                count = len(files)
                size = sum(f.size for f in files)
                print(f"  • {file_type}: {count} files ({size / 1024 / 1024:.2f} MB)")
        
        if self.errors:
            print(f"\n⚠️ Errors: {len(self.errors)}")
            for path, error in self.errors[:5]:  # Show first 5 errors
                print(f"  • {path.name}: {error}")
            if len(self.errors) > 5:
                print(f"  ... and {len(self.errors) - 5} more errors")
        
        print("=" * 50)
    
    def get_processing_queue(self) -> List[FileInfo]:
        """Get files ready for processing."""
        return sorted(self.scanned_files, key=lambda f: f.size)  # Small files first
    
    def get_summary_stats(self) -> Dict[str, any]:
        """Get summary statistics."""
        if not self.scanned_files:
            return {"total_files": 0, "total_size_mb": 0, "file_types": {}}
        
        total_size = sum(f.size for f in self.scanned_files)
        file_types = {}
        
        for file_info in self.scanned_files:
            ftype = file_info.file_type
            if ftype not in file_types:
                file_types[ftype] = {"count": 0, "size_mb": 0}
            file_types[ftype]["count"] += 1
            file_types[ftype]["size_mb"] += file_info.size_mb
        
        return {
            "total_files": len(self.scanned_files),
            "total_size_mb": total_size / 1024 / 1024,
            "file_types": file_types,
            "error_count": len(self.errors)
        }


def test_file_scanner():
    """Test the file scanner functionality."""
    print("🧪 Testing File Scanner")
    print("=" * 60)
    
    # Test with data directory
    scanner = FileScanner(recursive=True, include_hidden=False)
    test_dir = Path("data")
    
    if not test_dir.exists():
        print(f"❌ Test directory not found: {test_dir}")
        print("Creating test directory with sample files...")
        test_dir.mkdir(exist_ok=True)
        
        # Create sample test file
        (test_dir / "sample.txt").write_text("This is a sample text file for testing.")
        print("✅ Created sample test file")
    
    try:
        # Scan directory
        categorized = scanner.scan_directory(test_dir)
        
        # Show detailed results
        print("\n📋 Detailed File List:")
        for file_type, files in categorized.items():
            print(f"\n{file_type} Files:")
            for file_info in files:
                print(f"  📄 {file_info.path.name}")
                print(f"     Size: {file_info.size_mb:.2f} MB")
                print(f"     Type: {file_info.mime_type}")
        
        # Get processing queue
        queue = scanner.get_processing_queue()
        print(f"\n🎯 Processing Queue: {len(queue)} files")
        
        # Get statistics
        stats = scanner.get_summary_stats()
        print(f"\n📊 Statistics: {stats}")
        
        print("\n✅ File Scanner Test Complete!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")


if __name__ == "__main__":
    test_file_scanner()
