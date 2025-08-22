"""LocalLLM - A local LLM-based document summarization system.

This package provides document summarization capabilities with Japanese translation
support, using local LLM models for privacy-conscious processing.

Main components:
- document_processor: Core document processing functionality
- summarizer: Text summarization engines
- api: REST API endpoints for external integration
- enhanced_mock_llm: Enhanced LLM integration

Usage:
    Basic summarization:
        from localllm.document_processor import DocumentProcessor
        processor = DocumentProcessor()
        result = processor.process_file("document.pdf")

    API integration:
        from localllm.api.enhanced_document_api import EnhancedDocumentAPI
        api = EnhancedDocumentAPI()
        
    High-quality processing:
        from localllm.summarizer_enhanced import EnhancedAcademicProcessor
        processor = EnhancedAcademicProcessor()
        result = processor.process_academic("document.pdf")
"""

__version__ = "1.0.0"
__author__ = "MameMame777"
__email__ = ""
__description__ = "A local LLM-based document summarization system with Japanese translation capabilities"

# Import main classes for easy access
try:
    from .document_processor import DocumentProcessor
    from .summarizer import LLMSummarizer
    from .summarizer_enhanced import EnhancedAcademicProcessor
    
    __all__ = [
        "DocumentProcessor",
        "LLMSummarizer", 
        "EnhancedAcademicProcessor",
        "__version__",
        "__author__",
        "__description__"
    ]
except ImportError:
    # Handle import errors gracefully during installation
    __all__ = ["__version__", "__author__", "__description__"]
