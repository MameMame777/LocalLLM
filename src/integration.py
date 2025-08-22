"""Simple API interface for external project integration.

This module provides easy-to-use functions for external projects to integrate
LocalLLM functionality without needing to understand the internal architecture.

Usage examples:
    Basic text summarization:
        from localllm.integration import summarize_text
        result = summarize_text("Your text here", language="ja")
        
    File processing:
        from localllm.integration import process_file
        result = process_file("document.pdf", mode="enhanced")
        
    Batch processing:
        from localllm.integration import process_batch
        results = process_batch(["file1.pdf", "file2.txt"], mode="academic")
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import tempfile
import json

def _ensure_imports():
    """Ensure required modules are importable."""
    try:
        from . import document_processor
        from . import summarizer_enhanced
        from .api import server_controller
        return True
    except ImportError as e:
        print(f"Warning: Some LocalLLM components not available: {e}")
        return False

def summarize_text(
    text: str, 
    language: str = "ja",
    mode: str = "enhanced",
    use_llm: bool = True,
    enable_translation: bool = True
) -> Dict[str, Any]:
    """Summarize text with LocalLLM.
    
    Args:
        text: Text content to summarize
        language: Target language for output ("ja", "en")
        mode: Processing mode ("basic", "enhanced", "academic")
        use_llm: Whether to use LLM for summarization
        enable_translation: Whether to enable translation
        
    Returns:
        Dictionary containing summary and metadata
    """
    if not _ensure_imports():
        return {"error": "LocalLLM components not available"}
    
    try:
        # Try API approach first
        from .api.server_controller import LocalLLMAPIServerController, LocalLLMAPIClient
        
        controller = LocalLLMAPIServerController()
        if not controller.is_server_running():
            controller.start_server()
        
        client = LocalLLMAPIClient()
        
        # Use enhanced API if available
        try:
            response = client.process_text_enhanced(
                text=text,
                processing_mode=mode,
                language=language,
                use_llm=use_llm,
                enable_translation=enable_translation
            )
            return response
        except Exception:
            # Fallback to basic API
            response = client.process_text(text)
            return response
            
    except Exception as e:
        # Fallback to direct processing
        try:
            from .document_processor import DocumentProcessor
            processor = DocumentProcessor()
            
            # Create temporary file for processing
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(text)
                temp_path = f.name
            
            try:
                result = processor.process_file(temp_path)
                return {"summary": result, "mode": "fallback", "language": language}
            finally:
                Path(temp_path).unlink(missing_ok=True)
                
        except Exception as fallback_error:
            return {
                "error": f"Processing failed: {str(e)}, Fallback error: {str(fallback_error)}",
                "text": text[:200] + "..." if len(text) > 200 else text
            }

def process_file(
    file_path: Union[str, Path],
    mode: str = "enhanced", 
    language: str = "ja",
    use_llm: bool = True,
    enable_translation: bool = True
) -> Dict[str, Any]:
    """Process a file with LocalLLM.
    
    Args:
        file_path: Path to file to process
        mode: Processing mode ("basic", "enhanced", "academic")
        language: Target language for output
        use_llm: Whether to use LLM for summarization
        enable_translation: Whether to enable translation
        
    Returns:
        Dictionary containing processing results and metadata
    """
    if not _ensure_imports():
        return {"error": "LocalLLM components not available"}
    
    file_path = Path(file_path)
    if not file_path.exists():
        return {"error": f"File not found: {file_path}"}
    
    try:
        # Try API approach first
        from .api.server_controller import LocalLLMAPIServerController, LocalLLMAPIClient
        
        controller = LocalLLMAPIServerController()
        if not controller.is_server_running():
            controller.start_server()
        
        client = LocalLLMAPIClient()
        
        # Use enhanced API if available
        try:
            response = client.process_file_enhanced(
                file_path=str(file_path),
                processing_mode=mode,
                language=language,
                use_llm=use_llm,
                enable_translation=enable_translation
            )
            return response
        except Exception:
            # Fallback to basic API
            response = client.process_file(str(file_path))
            return response
            
    except Exception as e:
        # Fallback to direct processing
        try:
            from .document_processor import DocumentProcessor
            processor = DocumentProcessor()
            result = processor.process_file(str(file_path))
            return {
                "summary": result,
                "file_path": str(file_path),
                "mode": "fallback",
                "language": language
            }
        except Exception as fallback_error:
            return {
                "error": f"Processing failed: {str(e)}, Fallback error: {str(fallback_error)}",
                "file_path": str(file_path)
            }

def process_batch(
    file_paths: List[Union[str, Path]],
    mode: str = "enhanced",
    language: str = "ja",
    use_llm: bool = True,
    enable_translation: bool = True
) -> List[Dict[str, Any]]:
    """Process multiple files with LocalLLM.
    
    Args:
        file_paths: List of file paths to process
        mode: Processing mode ("basic", "enhanced", "academic")
        language: Target language for output
        use_llm: Whether to use LLM for summarization
        enable_translation: Whether to enable translation
        
    Returns:
        List of dictionaries containing processing results
    """
    results = []
    for file_path in file_paths:
        result = process_file(
            file_path=file_path,
            mode=mode,
            language=language,
            use_llm=use_llm,
            enable_translation=enable_translation
        )
        results.append(result)
    return results

def get_available_modes() -> List[str]:
    """Get list of available processing modes.
    
    Returns:
        List of available mode names
    """
    return ["basic", "enhanced", "academic"]

def get_supported_languages() -> List[str]:
    """Get list of supported output languages.
    
    Returns:
        List of supported language codes
    """
    return ["ja", "en"]

def check_installation() -> Dict[str, Any]:
    """Check LocalLLM installation status.
    
    Returns:
        Dictionary with installation status and available features
    """
    status = {
        "localllm_available": False,
        "api_available": False,
        "enhanced_processing": False,
        "translation_support": False,
        "llm_support": False,
        "errors": []
    }
    
    try:
        from . import document_processor
        status["localllm_available"] = True
    except ImportError as e:
        status["errors"].append(f"Document processor not available: {e}")
    
    try:
        from .api import server_controller
        status["api_available"] = True
    except ImportError as e:
        status["errors"].append(f"API controller not available: {e}")
    
    try:
        from . import summarizer_enhanced
        status["enhanced_processing"] = True
    except ImportError as e:
        status["errors"].append(f"Enhanced processing not available: {e}")
    
    # Check for translation support (Google Translate)
    try:
        import googletrans
        status["translation_support"] = True
    except ImportError:
        status["errors"].append("Google Translate not available (pip install googletrans)")
    
    # Check for LLM support
    try:
        import llama_cpp
        status["llm_support"] = True
    except ImportError:
        status["errors"].append("LLM support not available (pip install llama-cpp-python)")
    
    return status

# Convenience aliases
summarize = summarize_text
process = process_file

__all__ = [
    "summarize_text",
    "process_file", 
    "process_batch",
    "get_available_modes",
    "get_supported_languages",
    "check_installation",
    "summarize",  # alias
    "process",    # alias
]
