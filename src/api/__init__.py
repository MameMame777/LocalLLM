"""LocalLLM API Module - REST API endpoints for external integration.

This module provides various API endpoints for document processing and summarization:

- document_api: Main FastAPI server with basic processing
- enhanced_document_api: High-quality processing with academic features  
- server_controller: Programmatic server management
- quick_api: Simple function-based API interface

Usage:
    Start basic API server:
        from localllm.api.document_api import app
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=8000)
        
    Start enhanced API server:
        from localllm.api.enhanced_document_api import app
        import uvicorn  
        uvicorn.run(app, host="0.0.0.0", port=8001)
        
    Programmatic server control:
        from localllm.api.server_controller import LocalLLMAPIServerController
        controller = LocalLLMAPIServerController()
        controller.start_server()
        
    Simple API usage:
        from localllm.api.quick_api import quick_summarize
        result = quick_summarize("Your text here")
"""

__version__ = "1.0.0"

# Import main API components
try:
    from .server_controller import LocalLLMAPIServerController, LocalLLMAPIClient
    from .quick_api import quick_summarize, quick_summarize_file
    
    __all__ = [
        "LocalLLMAPIServerController",
        "LocalLLMAPIClient", 
        "quick_summarize",
        "quick_summarize_file",
        "__version__"
    ]
except ImportError:
    # Handle import errors gracefully during installation
    __all__ = ["__version__"]
