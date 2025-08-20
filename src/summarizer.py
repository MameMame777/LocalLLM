"""LLM-based summarization module with enhanced mock fallback."""

from typing import List, Optional, Dict, Any
from pathlib import Path
import re
from loguru import logger

try:
    from llama_cpp import Llama
    LLAMA_CPP_AVAILABLE = True
    logger.info("✅ llama-cpp-python is available")
except ImportError:
    LLAMA_CPP_AVAILABLE = False
    logger.warning("⚠️ llama-cpp-python not available, using enhanced mock")
    Llama = None

from config.settings import Settings
from .enhanced_mock_llm import EnhancedMockLLM


class LLMSummarizer:
    """Local LLM-based text summarizer."""
    
    def __init__(self, model_path: str, settings: Settings):
        self.model_path = Path(model_path)
        self.settings = settings
        self.model: Optional[Llama] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the LLM model."""
        if not Llama:
            raise ImportError("llama-cpp-python is required. Install with: pip install llama-cpp-python")
        
        if not self.model_path.exists():
            logger.warning(f"Model file not found: {self.model_path}")
            logger.info("To download a model, you can use:")
            logger.info("1. Visit https://huggingface.co/models?library=gguf")
            logger.info("2. Download a GGUF model file to the 'models/' directory")
            logger.info("3. Update the model path in .env file")
            logger.info("Example models:")
            logger.info("  - microsoft/DialoGPT-medium (lightweight)")
            logger.info("  - TheBloke/Llama-2-7B-Chat-GGML")
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        logger.info(f"Loading model: {self.model_path}")
        logger.info(f"Model size: {self.model_path.stat().st_size / 1024 / 1024:.1f} MB")
        
        try:
            self.model = Llama(
                model_path=str(self.model_path),
                n_ctx=self.settings.max_tokens * 2,  # Context window
                n_gpu_layers=self.settings.gpu_layers,
                verbose=False,
                n_threads=4,  # CPU threads
                use_mmap=True,  # Memory mapping for efficiency
                use_mlock=False  # Don't lock memory
            )
            logger.success("Model loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.info("Troubleshooting tips:")
            logger.info("1. Check if the model file is corrupted")
            logger.info("2. Ensure sufficient memory is available")
            logger.info("3. Try reducing GPU layers if using GPU")
            raise
    
    def summarize(self, text: str) -> str:
        """
        Generate a summary of the input text.
        
        Args:
            text: Input text to summarize
            
        Returns:
            Generated summary
        """
        if not self.model:
            raise RuntimeError("Model not loaded")
        
        if not text.strip():
            return "No content to summarize."
        
        logger.info(f"Summarizing text ({len(text)} characters)")
        
        # Split text into chunks if too long
        chunks = self._split_text(text)
        
        if len(chunks) == 1:
            return self._generate_summary(chunks[0])
        else:
            # For multiple chunks, summarize each and then create final summary
            logger.info(f"Text split into {len(chunks)} chunks")
            chunk_summaries = []
            
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                summary = self._generate_summary(chunk)
                chunk_summaries.append(summary)
            
            # Combine chunk summaries
            combined_text = "\n\n".join(chunk_summaries)
            logger.info("Creating final summary from chunk summaries")
            return self._generate_summary(combined_text, is_final=True)
    
    def _split_text(self, text: str) -> List[str]:
        """Split text into manageable chunks."""
        max_chunk_size = self.settings.chunk_size
        overlap = self.settings.chunk_overlap
        
        if len(text) <= max_chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + max_chunk_size
            
            if end >= len(text):
                chunks.append(text[start:])
                break
            
            # Try to break at sentence boundaries
            chunk = text[start:end]
            last_period = chunk.rfind('.')
            last_newline = chunk.rfind('\n')
            
            break_point = max(last_period, last_newline)
            
            if break_point > start + max_chunk_size // 2:  # Only if reasonable break point
                end = start + break_point + 1
            
            chunks.append(text[start:end])
            start = end - overlap
        
        return chunks
    
    def _generate_summary(self, text: str, is_final: bool = False) -> str:
        """Generate summary using the LLM."""
        # Prepare prompt
        if is_final:
            prompt = self._create_final_summary_prompt(text)
        else:
            prompt = self._create_summary_prompt(text)
        
        try:
            response = self.model(
                prompt,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature,
                top_p=self.settings.top_p,
                stop=["Human:", "User:", "\n\n\n"],
                echo=False
            )
            
            summary = response['choices'][0]['text'].strip()
            return self._clean_summary(summary)
        
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def _create_summary_prompt(self, text: str) -> str:
        """Create prompt for summarization."""
        return f"""以下のテキストを簡潔で分かりやすい日本語で要約してください。重要なポイントと主な内容を含めてください。

テキスト:
{text}

要約:"""
    
    def _create_final_summary_prompt(self, text: str) -> str:
        """Create prompt for final summary from multiple chunks."""
        return f"""以下は複数の部分要約です。これらを統合して、全体の内容を包括的かつ簡潔にまとめた最終要約を作成してください。

部分要約:
{text}

最終要約:"""
    
    def _clean_summary(self, summary: str) -> str:
        """Clean and format the generated summary."""
        if not summary:
            return "要約を生成できませんでした。"
        
        # Remove any remaining prompt artifacts
        summary = re.sub(r'^(要約|まとめ|概要)[:：]\s*', '', summary, flags=re.IGNORECASE)
        summary = re.sub(r'^(Summary|要約):\s*', '', summary, flags=re.IGNORECASE)
        
        # Clean up formatting
        summary = re.sub(r'\n\s*\n\s*\n', '\n\n', summary)
        summary = summary.strip()
        
        # Ensure minimum length
        if len(summary) < 20:
            return "生成された要約が短すぎます。入力テキストを確認してください。"
        
        return summary
