#!/usr/bin/env python3
"""
LLM Processor for Technical Translation Integration
Real Llama 2 LLM integration for technical document translation
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

try:
    from src.summarizer_enhanced import LLMSummarizer
    from config.settings import Settings
    from config.llama2_config import LLAMA2_MODEL_PATH, LLAMA2_GENERATION_CONFIG
    llm_available = True
except ImportError as e:
    logger.warning(f"LLM components not available: {e}")
    llm_available = False


class LLMProcessor:
    """
    Real LLM processor for technical translation system.
    Integrates Llama 2 for high-quality technical document translation.
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize LLM processor with Llama 2.
        
        Args:
            model_path: Path to the model file. Uses default Llama 2 if None.
        """
        self.model_path = Path(model_path) if model_path else LLAMA2_MODEL_PATH
        self.settings = Settings()
        self.summarizer: Optional[LLMSummarizer] = None
        self.is_loaded = False
        
        # Try to load the model
        self._initialize_llm()
    
    def _initialize_llm(self) -> bool:
        """Initialize the LLM model."""
        if not llm_available:
            logger.warning("⚠️ LLM components not available")
            return False
            
        if not self.model_path.exists():
            logger.warning(f"⚠️ Model file not found: {self.model_path}")
            logger.info("💡 Run 'python download_llama2.py' to download Llama 2 7B")
            return False
        
        try:
            logger.info("🤖 Initializing Llama 2 for technical translation...")
            self.summarizer = LLMSummarizer(
                model_path=str(self.model_path),
                settings=self.settings
            )
            self.is_loaded = True
            logger.success("✅ Llama 2 LLM processor initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            logger.info("💡 Consider using a smaller model or increasing RAM")
            return False
    
    def translate_technical_text(self, english_text: str, doc_type: str = "datasheet") -> Dict[str, Any]:
        """
        Translate technical English text to Japanese using Llama 2.
        
        Args:
            english_text: English technical text to translate
            doc_type: Document type (datasheet, manual, paper, etc.)
            
        Returns:
            Translation result with metadata
        """
        if not self.is_loaded or not self.summarizer:
            return {
                'japanese_translation': "⚠️ LLMが利用できません。モック翻訳を使用してください。",
                'processing_time': 0.0,
                'confidence_score': 0.0,
                'llm_used': False
            }
        
        start_time = time.time()
        
        # Create specialized technical translation prompt
        specialized_prompt = self._create_technical_prompt(english_text, doc_type)
        
        try:
            # Use LLM for high-quality translation
            logger.info(f"🔄 Processing technical translation ({len(english_text)} chars)")
            
            # Generate Japanese translation using LLM
            japanese_translation = self.summarizer.summarize_english_to_japanese(
                english_text=specialized_prompt
            )
            
            processing_time = time.time() - start_time
            
            # Calculate confidence score based on output quality
            confidence_score = self._calculate_confidence(japanese_translation, english_text)
            
            logger.success(f"✅ Technical translation completed in {processing_time:.2f}s")
            
            return {
                'japanese_translation': japanese_translation,
                'processing_time': processing_time,
                'confidence_score': confidence_score,
                'llm_used': True,
                'model_name': self.model_path.name,
                'word_count': len(english_text.split()),
                'translation_length': len(japanese_translation)
            }
            
        except Exception as e:
            logger.error(f"❌ LLM translation failed: {e}")
            return {
                'japanese_translation': f"❌ LLM翻訳エラー: {str(e)}",
                'processing_time': time.time() - start_time,
                'confidence_score': 0.0,
                'llm_used': False,
                'error': str(e)
            }
    
    def _create_technical_prompt(self, text: str, doc_type: str) -> str:
        """Create specialized prompt for technical translation."""
        
        # Document type specific instructions
        doc_instructions = {
            'datasheet': "データシート形式で、技術仕様と特性を正確に翻訳してください。",
            'manual': "技術マニュアル形式で、操作手順と仕様を分かりやすく翻訳してください。", 
            'paper': "学術論文形式で、専門用語と概念を正確に翻訳してください。",
            'patent': "特許文書形式で、技術的詳細と発明内容を正確に翻訳してください。"
        }
        
        instruction = doc_instructions.get(doc_type, "技術文書として正確に翻訳してください。")
        
        prompt = f"""[INST] 以下の英語技術文書を日本語に翻訳してください。

翻訳方針:
• {instruction}
• 技術用語は正確な日本語専門用語を使用
• 数値・単位・記号は変更しない
• 文書構造を保持
• 自然で読みやすい日本語に翻訳

英語技術文書:
{text[:2000]}

日本語翻訳: [/INST]"""
        
        return prompt
    
    def _calculate_confidence(self, translation: str, original: str) -> float:
        """Calculate translation confidence score."""
        if not translation or translation.startswith("❌"):
            return 0.0
        
        # Basic quality metrics
        translation_length = len(translation)
        original_length = len(original)
        
        if translation_length == 0:
            return 0.0
        
        # Length ratio check (good translation should be reasonable length)
        length_ratio = translation_length / original_length
        
        if 0.5 <= length_ratio <= 2.0:
            confidence = 0.8
        elif 0.3 <= length_ratio <= 3.0:
            confidence = 0.6
        else:
            confidence = 0.4
        
        # Check for Japanese content
        japanese_chars = sum(1 for char in translation if '\u3040' <= char <= '\u309F' or '\u30A0' <= char <= '\u30FF' or '\u4E00' <= char <= '\u9FAF')
        if japanese_chars > len(translation) * 0.3:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model."""
        return {
            'model_path': str(self.model_path),
            'model_loaded': self.is_loaded,
            'model_name': self.model_path.name if self.model_path.exists() else 'Not found',
            'llm_available': llm_available,
            'recommended_ram': '8-12GB'
        }
