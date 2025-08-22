"""GUI package initialization.

This package contains GUI components and academic processing modules for LocalLLM.

Main components:
- enhanced_academic_processor: High-quality academic document processing
- batch_gui: Batch processing GUI interface
- google_translate_processor: Translation integration
- launcher: Application launcher
- modern_batch_gui: Modern batch processing interface
- real_processing: Real-time processing components
"""

__version__ = "1.0.0"

# Import main processing function for easy access
try:
    from .enhanced_academic_processor import create_enhanced_academic_processing_function
    
    __all__ = [
        "create_enhanced_academic_processing_function",
        "__version__"
    ]
except ImportError:
    # Handle import errors gracefully during installation
    __all__ = ["__version__"]
