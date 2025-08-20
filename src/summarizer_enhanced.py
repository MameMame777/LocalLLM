"""LLM-based summarization module for real LLM models."""

import time
from typing import List, Optional
from pathlib import Path
import re
from loguru import logger

try:
    from llama_cpp import Llama
    llama_cpp_available = True
    logger.info("✅ llama-cpp-python is available")
except ImportError:
    llama_cpp_available = False
    logger.error("❌ llama-cpp-python not available - this is required for LLM functionality")
    raise ImportError("llama-cpp-python is required. Install with: pip install llama-cpp-python")

from config.settings import Settings
from src.utils.logger import log_summary_result


class LLMSummarizer:
    """Local LLM-based text summarizer for real LLM models only."""
    
    def __init__(self, model_path: str, settings: Settings):
        self.model_path = Path(model_path)
        self.settings = settings
        self.model: Optional[Llama] = None
        self._load_model()
    
    def _load_model(self) -> None:
        """Load the LLM model with error handling."""
        logger.info(f"🤖 Loading model: {self.model_path}")
        
        # Check if model file exists
        if not self.model_path.exists():
            error_msg = f"❌ Model file not found: {self.model_path}"
            logger.error(error_msg)
            logger.info("💡 Available options:")
            logger.info("  • Use download_llama2.py to download Llama 2 7B")
            logger.info("  • Use download_model_fixed.py to download TinyLlama")
            raise FileNotFoundError(error_msg)
        
        # Check if llama-cpp-python is available
        if not llama_cpp_available:
            error_msg = "❌ llama-cpp-python not available"
            logger.error(error_msg)
            logger.info("💡 Install with: pip install llama-cpp-python")
            raise ImportError(error_msg)
        
        try:
            logger.info("📚 Loading real LLM model...")
            self.model = Llama(
                model_path=str(self.model_path),
                n_ctx=self.settings.context_length,
                n_threads=self.settings.n_threads,
                n_gpu_layers=self.settings.n_gpu_layers,
                verbose=False
            )
            logger.success(f"✅ Real LLM model loaded: {self.model_path.name}")
            
        except Exception as e:
            error_msg = f"❌ Failed to load LLM model: {e}"
            logger.error(error_msg)
            logger.info("� Possible solutions:")
            logger.info("  • Check model file integrity")
            logger.info("  • Ensure sufficient RAM available")
            logger.info("  • Try a smaller model variant")
            raise RuntimeError(error_msg)
    
    def summarize(self, text: str, summary_type: str = "concise") -> str:
        """
        Summarize the given text using LLM or enhanced mock.
        
        Args:
            text: Text to summarize
            summary_type: Type of summary ("concise", "detailed", "bullet_points")
        
        Returns:
            Summarized text
        """
        if not text.strip():
            return "No content to summarize."
        
        if not self.model:
            logger.error("❌ No model loaded")
            raise RuntimeError("No LLM model loaded. Cannot perform summarization.")
        
        logger.info(f"📝 Summarizing text ({len(text)} characters)")
        start_time = time.time()
        
        # For very long texts, chunk them
        if len(text) > self.settings.max_input_length:
            summary = self._summarize_long_text(text, summary_type)
        else:
            # Single chunk summarization
            summary = self._summarize_chunk(text, summary_type)
        
        processing_time = time.time() - start_time
        logger.info(f"✅ Summary generated ({len(summary)} characters)")
        
        # Log detailed summary results
        log_summary_result(
            input_text=text,
            summary=summary,
            summary_type=summary_type,
            language_mode="🇯🇵 Japanese → Japanese",
            processing_time=processing_time,
            model_name=self.model_path.name
        )
        
        return summary
    
    def _summarize_long_text(self, text: str, summary_type: str) -> str:
        """Summarize long text by chunking."""
        logger.info("📚 Text is long, using chunked summarization")
        
        chunks = self._split_text(text, self.settings.max_input_length)
        logger.info(f"📄 Split into {len(chunks)} chunks")
        
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"🔄 Processing chunk {i}/{len(chunks)}")
            summary = self._summarize_chunk(chunk, summary_type)
            chunk_summaries.append(summary)
        
        # Combine chunk summaries
        combined_text = "\n\n".join(chunk_summaries)
        
        # If combined summary is still too long, summarize again
        if len(combined_text) > self.settings.max_input_length:
            logger.info("🔄 Final summarization of combined chunks")
            return self._summarize_chunk(combined_text, summary_type)
        
        return combined_text
    
    def _split_text(self, text: str, max_length: int) -> List[str]:
        """Split text into chunks at sentence boundaries."""
        sentences = re.split(r'[.!?。！？]\s+', text)
        chunks = []
        current_chunk = ""
        
        for sentence in sentences:
            # Add sentence to current chunk if it fits
            test_chunk = current_chunk + sentence + ". "
            if len(test_chunk) <= max_length:
                current_chunk = test_chunk
            else:
                # Start new chunk
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        # Add final chunk
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _summarize_chunk(self, text: str, summary_type: str) -> str:
        """Summarize a single chunk of text."""
        prompt = self._create_prompt(text, summary_type)
        
        try:
            # Generate summary using the real LLM model
            response = self.model.create_completion(
                prompt=prompt,
                max_tokens=self.settings.max_tokens,
                temperature=self.settings.temperature,
                top_p=self.settings.top_p,
                stop=["</s>", "\n\n"]
            )
            
            # Extract text from response (llama-cpp-python format)
            summary = response['choices'][0]['text'].strip()
            
            return self._clean_summary(summary)
            
        except Exception as e:
            logger.error(f"❌ Summarization error: {e}")
            raise RuntimeError(f"Failed to generate summary: {str(e)}")
    
    def _create_prompt(self, text: str, summary_type: str) -> str:
        """Create an appropriate prompt for summarization."""
        if summary_type == "detailed":
            instruction = "以下の文章を詳しく要約してください"
        elif summary_type == "bullet_points":
            instruction = "以下の文章の要点を箇条書きで要約してください"
        else:  # concise
            instruction = "以下の文章を要約してください"
        
        # Simple and direct prompt that works well with TinyLlama
        prompt = f"{instruction}：\n\n{text}\n\n要約："
        return prompt
    
    def summarize_english_to_japanese(self, english_text: str, summary_type: str = "concise") -> str:
        """
        Summarize English text in Japanese.
        
        Args:
            english_text: English text to summarize
            summary_type: Type of summary ("concise", "detailed", "bullet_points")
        
        Returns:
            Japanese summary
        """
        if not english_text.strip():
            return "要約する英語コンテンツがありません。"
        
        if not self.model:
            logger.error("❌ No model loaded")
            raise RuntimeError("No LLM model loaded. Cannot perform English-to-Japanese summarization.")
        
        logger.info(f"📝 英語→日本語要約 ({len(english_text)} 文字)")
        start_time = time.time()
        
        # For very long texts, chunk them
        if len(english_text) > self.settings.max_input_length:
            summary = self._summarize_long_english_text(english_text, summary_type)
        else:
            # Single chunk summarization
            summary = self._summarize_english_chunk(english_text, summary_type)
        
        processing_time = time.time() - start_time
        logger.info(f"✅ 日本語要約生成完了 ({len(summary)} 文字)")
        
        # Log detailed summary results
        log_summary_result(
            input_text=english_text,
            summary=summary,
            summary_type=summary_type,
            language_mode="🇺🇸 English → 🇯🇵 Japanese",
            processing_time=processing_time,
            model_name=self.model_path.name
        )
        
        return summary

    def summarize_english_to_english(self, english_text: str, summary_type: str = "concise") -> str:
        """
        Summarize English text in English.
        
        Args:
            english_text: English text to summarize
            summary_type: Type of summary ("concise", "detailed", "bullet_points")
        
        Returns:
            English summary
        """
        if not english_text.strip():
            return "No English content to summarize."
        
        if not self.model:
            logger.error("❌ No model loaded")
            raise RuntimeError("No LLM model loaded. Cannot perform English summarization.")
        
        logger.info(f"📝 English summarization ({len(english_text)} characters)")
        start_time = time.time()
        
        # For very long texts, chunk them
        if len(english_text) > self.settings.max_input_length:
            summary = self._summarize_long_english_to_english(english_text, summary_type)
        else:
            # Single chunk summarization
            summary = self._summarize_english_to_english_chunk(english_text, summary_type)
        
        processing_time = time.time() - start_time
        logger.info(f"✅ English summary generated ({len(summary)} characters)")
        
        # Log detailed summary results
        log_summary_result(
            input_text=english_text,
            summary=summary,
            summary_type=summary_type,
            language_mode="🇺🇸 English → English",
            processing_time=processing_time,
            model_name=self.model_path.name
        )
        
        return summary
    
    def _summarize_long_english_text(self, text: str, summary_type: str) -> str:
        """Summarize long English text by chunking."""
        logger.info("📚 長い英語テキストをチャンク化して要約")
        
        chunks = self._split_text(text, self.settings.max_input_length)
        logger.info(f"📄 {len(chunks)}個のチャンクに分割")
        
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"🔄 チャンク {i}/{len(chunks)} を処理中")
            summary = self._summarize_english_chunk(chunk, summary_type)
            chunk_summaries.append(summary)
        
        # Combine chunk summaries
        combined_text = "\n\n".join(chunk_summaries)
        
        # If combined summary is still too long, summarize again
        if len(combined_text) > self.settings.max_input_length:
            logger.info("🔄 結合した要約を最終要約")
            return self._summarize_chunk(combined_text, summary_type)  # Use regular Japanese summarization
        
        return combined_text

    def _summarize_long_english_to_english(self, text: str, summary_type: str) -> str:
        """Summarize long English text by chunking (English output)."""
        logger.info("📚 Long English text, using chunked summarization")
        
        chunks = self._split_text(text, self.settings.max_input_length)
        logger.info(f"📄 Split into {len(chunks)} chunks")
        
        chunk_summaries = []
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"🔄 Processing chunk {i}/{len(chunks)}")
            summary = self._summarize_english_to_english_chunk(chunk, summary_type)
            chunk_summaries.append(summary)
        
        # Combine chunk summaries
        combined_text = "\n\n".join(chunk_summaries)
        
        # If combined summary is still too long, summarize again
        if len(combined_text) > self.settings.max_input_length:
            logger.info("🔄 Final summarization of combined chunks")
            return self._summarize_english_to_english_chunk(combined_text, summary_type)
        
        return combined_text

    def _summarize_english_to_english_chunk(self, english_text: str, summary_type: str) -> str:
        """Summarize a single chunk of English text in English."""
        prompt = self._create_english_to_english_prompt(english_text, summary_type)
        
        try:
            # Generate summary using optimized parameters for English summarization
            response = self.model.create_completion(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3,
                top_p=0.9,
                stop=["[INST]", "[/INST]", "\n\nText:", "\n\nSummary:"]
            )
            
            # Extract text from response
            summary = response['choices'][0]['text'].strip()
            
            # Clean up common artifacts
            summary = summary.replace("Summary:", "").strip()
            
            return self._clean_summary(summary)
            
        except Exception as e:
            logger.error(f"❌ English summarization error: {e}")
            raise RuntimeError(f"Failed to generate English summary: {str(e)}")

    def _create_english_to_english_prompt(self, english_text: str, summary_type: str) -> str:
        """Create prompt for English to English summarization with enhanced academic analysis."""
        
        # Determine instruction based on summary type with academic focus
        if summary_type == "academic_detailed":
            task_instruction = "comprehensive academic analysis and detailed summary focusing on technical novelty, contributions, methodology, and key findings"
        elif summary_type == "academic_comprehensive":
            task_instruction = "comprehensive meta-analysis summarizing the overall technical contributions, innovations, and significance"
        elif summary_type == "detailed":
            task_instruction = "detailed summary"
        elif summary_type == "bullet_points":
            task_instruction = "bullet points summary"
        else:  # concise
            task_instruction = "concise summary"
        
        # Enhanced prompt for academic papers
        if "academic" in summary_type:
            prompt = f"""[INST] Please provide a {task_instruction} of the following academic/technical text. 

For academic analysis, please include:
- Technical innovations and novel contributions
- Key methodological approaches
- Significant findings and results
- Practical applications and implications
- Comparison with existing approaches (if mentioned)

Text:
{english_text.strip()}

Please provide only the analysis/summary without meta-commentary. Focus on technical substance and innovations. [/INST]

Analysis: """
        else:
            # Standard summarization prompt
            prompt = f"""[INST] Please provide a {task_instruction} of the following English text. Focus on the main points and key information.

Text:
{english_text.strip()}

Please provide only the summary without any explanations or additional text. [/INST]

Summary: """
        
        return prompt
    
    def _summarize_english_chunk(self, english_text: str, summary_type: str) -> str:
        """Summarize a single chunk of English text in Japanese with optimized prompt."""
        prompt = self._create_english_to_japanese_prompt(english_text, summary_type)
        
        try:
            # Generate summary using optimized parameters for English-to-Japanese translation
            # These parameters were proven successful in test_optimized_translation.py
            response = self.model.create_completion(
                prompt=prompt,
                max_tokens=300,                    # Sufficient for quality translation
                temperature=0.3,                   # Low temperature for consistency
                top_p=0.9,                        # Balanced diversity
                stop=["[INST]", "[/INST]", "English text:", "\n\nEnglish"]  # Optimized stop sequences
            )
            
            # Extract text from response (llama-cpp-python format)
            summary = response['choices'][0]['text'].strip()
            
            # Clean up common artifacts from the optimized prompt format
            summary = summary.replace("Japanese translation:", "").strip()
            
            return self._clean_summary(summary)
            
        except Exception as e:
            logger.error(f"❌ 英語→日本語要約エラー: {e}")
            raise RuntimeError(f"Failed to generate English-to-Japanese summary: {str(e)}")
    
    def _create_english_to_japanese_prompt(self, english_text: str, summary_type: str) -> str:
        """Create optimized prompt for English to Japanese summarization using Llama 2 format."""
        
        # Determine instruction based on summary type
        if summary_type == "detailed":
            task_instruction = "detailed Japanese summary"
        elif summary_type == "bullet_points":
            task_instruction = "Japanese bullet points summary"
        else:  # concise
            task_instruction = "concise Japanese summary"
        
        # Use the proven successful prompt format from test_optimized_translation.py
        # This format achieved 100% success rate with 14.35 second average processing time
        optimized_prompt = f"""[INST] You are a professional English-to-Japanese translator. Please translate the following English text into natural, fluent Japanese. Focus on clarity and accuracy.

English text:
{english_text.strip()}

Please provide only the Japanese translation without any explanations or additional text. [/INST]

Japanese translation: """
        
        return optimized_prompt
    
    def _clean_summary(self, summary: str) -> str:
        """Clean and format the generated summary."""
        # Remove common artifacts
        summary = re.sub(r'^(要約[:：]?\s*)', '', summary, flags=re.IGNORECASE)
        summary = re.sub(r'^(Summary[:：]?\s*)', '', summary, flags=re.IGNORECASE)
        
        # Remove excessive whitespace
        summary = re.sub(r'\s+', ' ', summary)
        summary = summary.strip()
        
        # Ensure proper ending
        if summary and not summary.endswith(('.', '。', '!', '！', '?', '？')):
            summary += '。'
        
        return summary
