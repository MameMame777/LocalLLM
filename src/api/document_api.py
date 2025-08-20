#!/usr/bin/env python3
"""
LocalLLM Document Processing API Server
RESTful API for document processing and summarization
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
import asyncio
import uuid
import time
from pathlib import Path
import requests
import tempfile
import os
import sys

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from document_processor import DocumentProcessor
from gui.real_processing import real_process_file_global, ProcessingResult
from utils.language_detector import LanguageDetector

app = FastAPI(
    title="LocalLLM Document API",
    description="High-performance document processing and summarization API",
    version="1.0.0"
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
language_detector = LanguageDetector()

# Task storage (in production, use Redis or database)
task_storage: Dict[str, Dict[str, Any]] = {}

class DocumentRequest(BaseModel):
    """Document processing request model"""
    url: Optional[HttpUrl] = None
    urls: Optional[List[HttpUrl]] = None
    content: Optional[str] = None
    language: str = "ja"
    max_length: int = 150
    use_llm: bool = False
    auto_detect_language: bool = True
    output_format: str = "markdown"  # markdown, json, text

class ProcessingTask(BaseModel):
    """Processing task model"""
    task_id: str
    status: str  # pending, processing, completed, failed
    progress: float
    created_at: float
    completed_at: Optional[float] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class BatchRequest(BaseModel):
    """Batch processing request model"""
    urls: List[HttpUrl]
    language: str = "ja"
    max_length: int = 150
    use_llm: bool = False
    auto_detect_language: bool = True
    parallel_workers: int = 4

@app.get("/")
async def root():
    """API information"""
    return {
        "service": "LocalLLM Document Processing API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "process_single": "/api/v1/process",
            "process_batch": "/api/v1/batch",
            "get_task": "/api/v1/task/{task_id}",
            "health": "/health"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

async def download_file(url: str, temp_dir: str) -> Path:
    """Download file from URL"""
    try:
        response = requests.get(str(url), timeout=30, stream=True)
        response.raise_for_status()
        
        # Determine file extension from content-type or URL
        content_type = response.headers.get('content-type', '')
        if 'pdf' in content_type:
            ext = '.pdf'
        elif 'html' in content_type:
            ext = '.html'
        else:
            ext = Path(url).suffix or '.tmp'
        
        # Create temporary file
        temp_file = Path(temp_dir) / f"download_{uuid.uuid4()}{ext}"
        
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return temp_file
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to download {url}: {str(e)}")

async def process_single_document(
    file_path: Path,
    language: str,
    max_length: int,
    use_llm: bool,
    auto_detect_language: bool,
    output_format: str
) -> Dict[str, Any]:
    """Process a single document"""
    
    output_dir = Path("output/api_processing")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Process the document
    result = real_process_file_global(
        file_path=file_path,
        language=language,
        max_length=max_length,
        output_dir=str(output_dir),
        use_llm=use_llm,
        auto_detect_language=auto_detect_language
    )
    
    # Format result based on requested format
    if output_format == "json":
        return {
            "status": result.status,
            "summary": result.summary,
            "processing_time": result.processing_time,
            "word_count": len(result.summary.split()) if result.summary else 0,
            "metadata": result.metadata or {}
        }
    elif output_format == "text":
        return {
            "status": result.status,
            "content": result.summary,
            "metadata": {
                "processing_time": result.processing_time
            }
        }
    else:  # markdown (default)
        markdown_content = f"""# Document Summary

## Metadata
- **Status**: {result.status}
- **Processing Time**: {result.processing_time:.2f}s
- **Word Count**: {len(result.summary.split()) if result.summary else 0}

## Summary

{result.summary}
"""
        return {
            "status": result.status,
            "content": markdown_content,
            "summary": result.summary,
            "metadata": {
                "processing_time": result.processing_time
            }
        }

@app.post("/api/v1/process")
async def process_document(request: DocumentRequest):
    """Process a single document from URL or content"""
    
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            if request.url:
                # Download and process from URL
                file_path = await download_file(str(request.url), temp_dir)
                
            elif request.content:
                # Process direct content
                file_path = Path(temp_dir) / "content.txt"
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(request.content)
            else:
                raise HTTPException(status_code=400, detail="Either 'url' or 'content' must be provided")
            
            # Process the document
            result = await process_single_document(
                file_path=file_path,
                language=request.language,
                max_length=request.max_length,
                use_llm=request.use_llm,
                auto_detect_language=request.auto_detect_language,
                output_format=request.output_format
            )
            
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.post("/api/v1/batch")
async def process_batch(request: BatchRequest, background_tasks: BackgroundTasks):
    """Start batch processing of multiple documents"""
    
    task_id = str(uuid.uuid4())
    
    # Initialize task
    task_storage[task_id] = {
        "task_id": task_id,
        "status": "pending",
        "progress": 0.0,
        "created_at": time.time(),
        "total_urls": len(request.urls),
        "completed_urls": 0,
        "results": [],
        "errors": []
    }
    
    # Start background processing
    background_tasks.add_task(
        process_batch_background,
        task_id,
        request.urls,
        request.language,
        request.max_length,
        request.use_llm,
        request.auto_detect_language,
        request.parallel_workers
    )
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": f"Batch processing started for {len(request.urls)} documents"
    }

async def process_batch_background(
    task_id: str,
    urls: List[HttpUrl],
    language: str,
    max_length: int,
    use_llm: bool,
    auto_detect_language: bool,
    parallel_workers: int
):
    """Background batch processing"""
    
    try:
        task_storage[task_id]["status"] = "processing"
        
        with tempfile.TemporaryDirectory() as temp_dir:
            results = []
            errors = []
            
            for i, url in enumerate(urls):
                try:
                    # Download file
                    file_path = await download_file(str(url), temp_dir)
                    
                    # Process document
                    result = await process_single_document(
                        file_path=file_path,
                        language=language,
                        max_length=max_length,
                        use_llm=use_llm,
                        auto_detect_language=auto_detect_language,
                        output_format="json"
                    )
                    
                    results.append({
                        "url": str(url),
                        "result": result
                    })
                    
                except Exception as e:
                    errors.append({
                        "url": str(url),
                        "error": str(e)
                    })
                
                # Update progress
                progress = (i + 1) / len(urls) * 100
                task_storage[task_id].update({
                    "progress": progress,
                    "completed_urls": i + 1,
                    "results": results,
                    "errors": errors
                })
            
            # Mark as completed
            task_storage[task_id].update({
                "status": "completed",
                "completed_at": time.time(),
                "progress": 100.0
            })
            
    except Exception as e:
        task_storage[task_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": time.time()
        })

@app.get("/api/v1/task/{task_id}")
async def get_task_status(task_id: str):
    """Get task status and results"""
    
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    task = task_storage[task_id]
    
    return {
        "task_id": task_id,
        "status": task["status"],
        "progress": task["progress"],
        "created_at": task["created_at"],
        "completed_at": task.get("completed_at"),
        "total_urls": task.get("total_urls", 0),
        "completed_urls": task.get("completed_urls", 0),
        "results": task.get("results", []),
        "errors": task.get("errors", []),
        "error": task.get("error")
    }

@app.delete("/api/v1/task/{task_id}")
async def delete_task(task_id: str):
    """Delete task from storage"""
    
    if task_id not in task_storage:
        raise HTTPException(status_code=404, detail="Task not found")
    
    del task_storage[task_id]
    return {"message": "Task deleted successfully"}

@app.get("/api/v1/tasks")
async def list_tasks():
    """List all tasks"""
    
    tasks = []
    for task_id, task_data in task_storage.items():
        tasks.append({
            "task_id": task_id,
            "status": task_data["status"],
            "progress": task_data["progress"],
            "created_at": task_data["created_at"],
            "total_urls": task_data.get("total_urls", 0)
        })
    
    return {"tasks": tasks}

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "document_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
