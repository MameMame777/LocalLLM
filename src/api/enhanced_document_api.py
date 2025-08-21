#!/usr/bin/env python3
"""
Enhanced API with Academic Processing
高品質な学術処理機能を統合したAPI
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any, Literal
import asyncio
import uuid
import time
from pathlib import Path
import tempfile
import os
import sys

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from document_processor import DocumentProcessor
from gui.real_processing import real_process_file_global, ProcessingResult

# Enhanced Academic Processing imports
try:
    from gui.enhanced_academic_processor import EnhancedAcademicProcessor
    enhanced_processing_available = True
except ImportError:
    enhanced_processing_available = False

app = FastAPI(
    title="LocalLLM Enhanced Academic API",
    description="High-quality document processing with academic-grade summarization",
    version="2.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global processor instances
processor = DocumentProcessor()

# Enhanced processor (if available)
if enhanced_processing_available:
    enhanced_processor = EnhancedAcademicProcessor()
else:
    enhanced_processor = None

class EnhancedDocumentRequest(BaseModel):
    """Enhanced document processing request model"""
    url: Optional[HttpUrl] = None
    urls: Optional[List[HttpUrl]] = None
    content: Optional[str] = None
    
    # Processing parameters
    language: str = "ja"
    max_length: int = 200
    processing_mode: Literal["basic", "enhanced", "academic"] = "enhanced"
    
    # Academic processing options
    use_llm: bool = True
    enable_translation: bool = True
    detect_technical_terms: bool = True
    quality_assessment: bool = True
    
    # Output options
    output_format: Literal["markdown", "json", "text", "academic"] = "academic"
    include_metadata: bool = True
    auto_detect_language: bool = True

class ProcessingResponse(BaseModel):
    """Enhanced processing response model"""
    status: str
    summary: str
    processing_time: float
    quality_score: Optional[float] = None
    technical_terms: Optional[List[str]] = None
    translation_quality: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    """API information with enhanced capabilities"""
    return {
        "service": "LocalLLM Enhanced Academic API",
        "version": "2.0.0",
        "status": "running",
        "enhanced_processing": enhanced_processing_available,
        "capabilities": {
            "basic_processing": True,
            "enhanced_academic": enhanced_processing_available,
            "google_translate": enhanced_processing_available,
            "technical_terms": enhanced_processing_available,
            "quality_assessment": enhanced_processing_available
        },
        "endpoints": {
            "process_single": "/api/v2/process",
            "process_batch": "/api/v2/batch",
            "quality_compare": "/api/v2/compare",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Enhanced health check with capability info"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "enhanced_processing": enhanced_processing_available,
        "llm_available": enhanced_processor.llm_available if enhanced_processor else False
    }

async def process_with_mode(
    content: str,
    file_path: Optional[Path],
    request: EnhancedDocumentRequest
) -> ProcessingResponse:
    """Process content with specified mode"""
    
    start_time = time.time()
    
    if request.processing_mode == "basic":
        # Basic processing using original API logic
        return await _process_basic(content, file_path, request, start_time)
    
    elif request.processing_mode == "enhanced" and enhanced_processing_available:
        # Enhanced processing with academic features
        return await _process_enhanced(content, file_path, request, start_time)
    
    elif request.processing_mode == "academic" and enhanced_processing_available:
        # Full academic processing
        return await _process_academic(content, file_path, request, start_time)
    
    else:
        # Fallback to basic if enhanced not available
        return await _process_basic(content, file_path, request, start_time)

async def _process_basic(
    content: str,
    file_path: Optional[Path],
    request: EnhancedDocumentRequest,
    start_time: float
) -> ProcessingResponse:
    """Basic processing mode"""
    
    # Create temporary file if needed
    if file_path is None:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_file = Path(f.name)
    else:
        temp_file = file_path
    
    try:
        # Use basic real_process_file_global
        result = real_process_file_global(
            file_path=temp_file,
            language=request.language,
            max_length=request.max_length,
            use_llm=request.use_llm,
            auto_detect_language=request.auto_detect_language
        )
        
        processing_time = time.time() - start_time
        
        return ProcessingResponse(
            status=result.status,
            summary=result.summary,
            processing_time=processing_time,
            metadata=result.metadata
        )
        
    finally:
        if file_path is None and temp_file.exists():
            temp_file.unlink()

async def _process_enhanced(
    content: str,
    file_path: Optional[Path],
    request: EnhancedDocumentRequest,
    start_time: float
) -> ProcessingResponse:
    """Enhanced processing mode with translation and LLM"""
    
    if not enhanced_processing_available:
        raise HTTPException(status_code=503, detail="Enhanced processing not available")
    
    try:
        # Use enhanced academic processor
        if request.enable_translation:
            # First translate if needed
            target_lang_map = {"ja": "ja", "en": "en", "zh": "zh"}
            target_lang = target_lang_map.get(request.language, "ja")
            
            if request.auto_detect_language:
                # Auto-detect and translate
                translated_content = enhanced_processor.translate_text(
                    content, 
                    target_lang=target_lang,
                    source_lang='auto'
                )
            else:
                translated_content = enhanced_processor.translate_text(
                    content,
                    target_lang=target_lang
                )
        else:
            translated_content = content
        
        # Generate summary with LLM if available
        if request.use_llm and enhanced_processor.llm_available:
            try:
                summary = enhanced_processor.llm_summarizer.summarize(
                    translated_content,
                    max_length=request.max_length
                )
            except Exception as e:
                # Fallback to basic summarization
                summary = _generate_basic_summary(translated_content, request.max_length)
        else:
            summary = _generate_basic_summary(translated_content, request.max_length)
        
        # Extract technical terms if requested
        technical_terms = []
        if request.detect_technical_terms:
            technical_terms = _extract_technical_terms(content)
        
        # Quality assessment
        quality_score = None
        if request.quality_assessment:
            quality_score = _assess_quality(summary, content)
        
        processing_time = time.time() - start_time
        
        return ProcessingResponse(
            status="success",
            summary=summary,
            processing_time=processing_time,
            quality_score=quality_score,
            technical_terms=technical_terms,
            translation_quality="high" if request.enable_translation else None,
            metadata={
                "processing_mode": "enhanced",
                "llm_used": request.use_llm and enhanced_processor.llm_available,
                "translation_used": request.enable_translation,
                "original_length": len(content),
                "summary_length": len(summary),
                "language": request.language
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Enhanced processing failed: {str(e)}")

async def _process_academic(
    content: str,
    file_path: Optional[Path],
    request: EnhancedDocumentRequest,
    start_time: float
) -> ProcessingResponse:
    """Academic processing mode with full features"""
    
    if not enhanced_processing_available:
        raise HTTPException(status_code=503, detail="Academic processing not available")
    
    try:
        # Create temporary file for academic processor
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(content)
            temp_file = Path(f.name)
        
        try:
            # Use full academic processing pipeline
            # Note: This would need to be implemented based on the GUI academic processing
            academic_result = enhanced_processor.process_academic_document(
                temp_file,
                target_language=request.language,
                use_llm=request.use_llm,
                enable_translation=request.enable_translation,
                max_length=request.max_length
            )
            
            processing_time = time.time() - start_time
            
            return ProcessingResponse(
                status="success",
                summary=academic_result.get("summary", ""),
                processing_time=processing_time,
                quality_score=academic_result.get("quality_score"),
                technical_terms=academic_result.get("technical_terms", []),
                translation_quality=academic_result.get("translation_quality"),
                metadata={
                    "processing_mode": "academic",
                    **academic_result.get("metadata", {})
                }
            )
            
        finally:
            if temp_file.exists():
                temp_file.unlink()
                
    except Exception as e:
        # Fallback to enhanced processing
        return await _process_enhanced(content, file_path, request, start_time)

def _generate_basic_summary(text: str, max_length: int) -> str:
    """Generate basic extractive summary"""
    sentences = text.split('.')
    if len(sentences) <= 2:
        return text[:max_length]
    
    # Simple extractive summary
    summary_sentences = sentences[:min(3, len(sentences))]
    summary = '. '.join(summary_sentences)
    
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."
    
    return summary

def _extract_technical_terms(text: str) -> List[str]:
    """Extract technical terms from text"""
    import re
    
    # Simple technical term detection
    patterns = [
        r'\b[A-Z]{2,}\b',  # Acronyms
        r'\b\w+(?:tion|sion|ment|ness|ity)\b',  # Technical suffixes
        r'\b(?:AI|ML|API|HTTP|JSON|LLM|GPU|CPU)\b'  # Common tech terms
    ]
    
    terms = set()
    for pattern in patterns:
        matches = re.findall(pattern, text)
        terms.update(matches)
    
    return list(terms)[:10]  # Limit to 10 terms

def _assess_quality(summary: str, original: str) -> float:
    """Assess summary quality"""
    if not summary or not original:
        return 0.0
    
    # Simple quality metrics
    summary_length = len(summary.split())
    original_length = len(original.split())
    
    # Compression ratio (should be between 0.1 and 0.3 for good summaries)
    compression_ratio = summary_length / max(original_length, 1)
    
    # Quality score based on compression ratio and content
    if 0.1 <= compression_ratio <= 0.3:
        base_score = 0.8
    elif 0.05 <= compression_ratio <= 0.5:
        base_score = 0.6
    else:
        base_score = 0.4
    
    # Bonus for sentence structure
    sentence_count = summary.count('.') + summary.count('!') + summary.count('?')
    if sentence_count >= 2:
        base_score += 0.1
    
    return min(base_score, 1.0)

@app.post("/api/v2/process")
async def process_document_enhanced(request: EnhancedDocumentRequest):
    """Enhanced document processing with multiple modes"""
    
    try:
        content = ""
        file_path = None
        
        if request.url:
            # Download and process from URL
            import requests
            response = requests.get(str(request.url), timeout=30)
            response.raise_for_status()
            content = response.text
            
        elif request.content:
            content = request.content
            
        else:
            raise HTTPException(status_code=400, detail="Either 'url' or 'content' must be provided")
        
        if not content.strip():
            raise HTTPException(status_code=400, detail="No content to process")
        
        # Process with specified mode
        result = await process_with_mode(content, file_path, request)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/v2/compare")
async def compare_processing_modes(request: EnhancedDocumentRequest):
    """Compare different processing modes for the same content"""
    
    if not request.content and not request.url:
        raise HTTPException(status_code=400, detail="Content or URL required for comparison")
    
    # Get content
    if request.url:
        import requests
        response = requests.get(str(request.url), timeout=30)
        response.raise_for_status()
        content = response.text
    else:
        content = request.content
    
    results = {}
    
    # Test basic mode
    basic_request = request.model_copy()
    basic_request.processing_mode = "basic"
    try:
        results["basic"] = await process_with_mode(content, None, basic_request)
    except Exception as e:
        results["basic"] = {"error": str(e)}
    
    # Test enhanced mode
    if enhanced_processing_available:
        enhanced_request = request.model_copy()
        enhanced_request.processing_mode = "enhanced"
        try:
            results["enhanced"] = await process_with_mode(content, None, enhanced_request)
        except Exception as e:
            results["enhanced"] = {"error": str(e)}
    
    # Test academic mode
    if enhanced_processing_available:
        academic_request = request.model_copy()
        academic_request.processing_mode = "academic"
        try:
            results["academic"] = await process_with_mode(content, None, academic_request)
        except Exception as e:
            results["academic"] = {"error": str(e)}
    
    return {
        "comparison_results": results,
        "enhanced_available": enhanced_processing_available,
        "original_length": len(content)
    }

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "enhanced_document_api:app",
        host="0.0.0.0",
        port=8001,  # Different port from original API
        reload=True,
        log_level="info"
    )
