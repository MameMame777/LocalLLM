"""Configuration management for the Local LLM Summarizer."""

from pathlib import Path
from typing import Dict, Any
import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # LLM Configuration
    default_model_path: str = Field(default="models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf")
    max_tokens: int = Field(default=512, ge=1, le=8192)
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    context_length: int = Field(default=2048, ge=512, le=4096)
    n_threads: int = Field(default=4, ge=1, le=16)
    n_gpu_layers: int = Field(default=0, ge=0, le=50)
    
    # Processing Configuration
    max_input_length: int = Field(default=100000, ge=1000)
    chunk_size: int = Field(default=4000, ge=500, le=8000)
    chunk_overlap: int = Field(default=200, ge=0, le=500)
    
    # Memory Configuration
    max_memory_usage: int = Field(default=8, ge=2, le=64)  # GB
    gpu_layers: int = Field(default=0, ge=0, le=50)
    
    # Output Configuration
    default_output_format: str = Field(default="markdown")
    output_directory: str = Field(default="output")
    
    # Logging Configuration
    log_level: str = Field(default="INFO")
    log_file: str = Field(default="logs/summarizer.log")
    summary_log_file: str = Field(default="logs/summary_results.log")
    enable_summary_only_log: bool = Field(default=True)
    enable_detailed_log: bool = Field(default=True)
    
    # Email Configuration
    email_sender: str = Field(default="")
    email_password: str = Field(default="")
    notification_email: str = Field(default="")
    smtp_server: str = Field(default="smtp.gmail.com")
    smtp_port: int = Field(default=587)
    
    class Config:
        env_file = ".env"
        case_sensitive = False


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def ensure_directories() -> None:
    """Ensure required directories exist."""
    root = get_project_root()
    directories = [
        root / "output",
        root / "logs",
        root / "models",
        root / "data" / "temp"
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
