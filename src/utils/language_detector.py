"""
Language Detection Utility for LocalLLM
言語自動認識ユーティリティ

Features:
- Automatic language detection from text content
- Support for Japanese, English, Chinese, Korean
- PDF-specific preprocessing for better accuracy
- Fallback mechanisms for mixed-language documents
"""

import re
from typing import Dict, Tuple, Optional
from pathlib import Path

class LanguageDetector:
    """
    Automatic language detection for PDF documents
    """
    
    def __init__(self):
        """Initialize language detector with pattern-based rules"""
        self.language_patterns = {
            'ja': {
                'hiragana': r'[\u3040-\u309F]',
                'katakana': r'[\u30A0-\u30FF]',
                'kanji': r'[\u4E00-\u9FAF]',
                'description': 'Japanese (日本語)'
            },
            'en': {
                'ascii': r'[a-zA-Z]',
                'common_words': r'\b(the|and|or|of|in|to|for|with|by)\b',
                'description': 'English'
            },
            'zh': {
                'chinese': r'[\u4E00-\u9FFF]',
                'traditional': r'[\u3400-\u4DBF]',
                'description': 'Chinese (中文)'
            },
            'ko': {
                'hangul': r'[\uAC00-\uD7AF]',
                'jamo': r'[\u1100-\u11FF]',
                'description': 'Korean (한국어)'
            }
        }
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better language detection
        
        Args:
            text: Raw text from PDF
            
        Returns:
            Cleaned text for language detection
        """
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common PDF artifacts
        text = re.sub(r'[^\w\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF\uAC00-\uD7AF]', ' ', text)
        
        # Take sample from middle of text (avoid headers/footers)
        text_len = len(text)
        if text_len > 1000:
            start = text_len // 4
            end = start + 500
            text = text[start:end]
        
        return text.strip()
    
    def detect_language_patterns(self, text: str) -> Dict[str, float]:
        """
        Detect languages using pattern matching
        
        Args:
            text: Input text to analyze
            
        Returns:
            Dictionary with language codes and confidence scores
        """
        if not text or len(text.strip()) < 10:
            return {'en': 0.5}  # Default fallback
        
        processed_text = self.preprocess_text(text)
        scores = {}
        
        total_chars = len(processed_text)
        if total_chars == 0:
            return {'en': 0.5}
        
        for lang_code, patterns in self.language_patterns.items():
            score = 0.0
            
            for pattern_name, pattern in patterns.items():
                if pattern_name == 'description':
                    continue
                    
                matches = len(re.findall(pattern, processed_text, re.IGNORECASE))
                
                # Weight different patterns
                if lang_code == 'ja':
                    if pattern_name in ['hiragana', 'katakana']:
                        score += matches * 2  # Strong indicators
                    elif pattern_name == 'kanji':
                        score += matches * 1.5  # Shared with Chinese
                
                elif lang_code == 'en':
                    if pattern_name == 'common_words':
                        score += matches * 3  # Strong indicator
                    elif pattern_name == 'ascii':
                        score += matches * 0.1  # Weak indicator
                
                elif lang_code == 'zh':
                    if pattern_name == 'chinese':
                        score += matches * 2
                
                elif lang_code == 'ko':
                    if pattern_name == 'hangul':
                        score += matches * 2
            
            # Normalize score
            scores[lang_code] = min(score / total_chars, 1.0)
        
        return scores
    
    def detect_with_fallback(self, text: str) -> Tuple[str, float, Dict[str, float]]:
        """
        Detect language with advanced fallback mechanisms
        
        Args:
            text: Input text to analyze
            
        Returns:
            Tuple of (detected_language, confidence, all_scores)
        """
        # Pattern-based detection
        scores = self.detect_language_patterns(text)
        
        # Try langdetect if available
        try:
            import langdetect
            langdetect_result = langdetect.detect(text[:1000])  # Sample for speed
            
            # Map langdetect results to our language codes
            langdetect_mapping = {
                'ja': 'ja',
                'en': 'en', 
                'zh-cn': 'zh',
                'zh-tw': 'zh',
                'ko': 'ko'
            }
            
            if langdetect_result in langdetect_mapping:
                mapped_lang = langdetect_mapping[langdetect_result]
                scores[mapped_lang] = max(scores.get(mapped_lang, 0), 0.7)
                
        except ImportError:
            print("📝 Note: Install 'langdetect' for improved accuracy: pip install langdetect")
        except:
            pass  # Continue with pattern-based detection
        
        # Find best match
        if scores:
            best_lang = max(scores.items(), key=lambda x: x[1])
            return best_lang[0], best_lang[1], scores
        else:
            return 'en', 0.5, {'en': 0.5}  # Default fallback
    
    def detect_from_file(self, file_path: Path) -> Tuple[str, float, Dict[str, str]]:
        """
        Detect language from file content
        
        Args:
            file_path: Path to the file
            
        Returns:
            Tuple of (detected_language, confidence, detailed_info)
        """
        try:
            # Extract text using document processor
            from document_processor import DocumentProcessor
            
            processor = DocumentProcessor()
            extracted_text = processor.extract_text(file_path)
            
            if not extracted_text or len(extracted_text.strip()) < 50:
                return 'en', 0.3, {
                    'detected_language': 'en',
                    'confidence': '30%',
                    'reason': 'Insufficient text content - defaulting to English',
                    'file_size': f"{file_path.stat().st_size} bytes"
                }
            
            # Detect language
            detected_lang, confidence, all_scores = self.detect_with_fallback(extracted_text)
            
            # Format results
            detailed_info = {
                'detected_language': detected_lang,
                'confidence': f"{confidence*100:.1f}%",
                'language_name': self.language_patterns[detected_lang]['description'],
                'text_sample': extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
                'all_scores': {lang: f"{score*100:.1f}%" for lang, score in all_scores.items()},
                'text_length': len(extracted_text)
            }
            
            return detected_lang, confidence, detailed_info
            
        except Exception as e:
            return 'en', 0.2, {
                'detected_language': 'en',
                'confidence': '20%',
                'reason': f'Error during detection: {str(e)}',
                'error': str(e)
            }
    
    def get_recommended_summary_language(self, detected_source: str, 
                                       user_preference: Optional[str] = None) -> str:
        """
        Recommend summary language based on source and user preference
        
        Args:
            detected_source: Detected source language
            user_preference: User's preferred summary language
            
        Returns:
            Recommended summary language code
        """
        if user_preference and user_preference != 'auto':
            return user_preference
        
        # Default logic: English docs -> Japanese summary, others -> same language
        if detected_source == 'en':
            return 'ja'  # English to Japanese (common use case)
        else:
            return detected_source  # Same language summary


def test_language_detection():
    """Test the language detection functionality"""
    detector = LanguageDetector()
    
    # Test samples
    test_samples = {
        'ja': "これは日本語のテキストサンプルです。技術文書の要約を作成します。",
        'en': "This is an English text sample for testing language detection algorithms.",
        'zh': "这是中文文本样本，用于测试语言检测功能。",
        'ko': "이것은 한국어 텍스트 샘플입니다."
    }
    
    print("🔍 Language Detection Test Results:")
    print("=" * 50)
    
    for expected_lang, sample_text in test_samples.items():
        detected, confidence, scores = detector.detect_with_fallback(sample_text)
        print(f"Expected: {expected_lang} | Detected: {detected} | Confidence: {confidence:.2f}")
        print(f"All scores: {scores}")
        print("-" * 30)


if __name__ == "__main__":
    test_language_detection()
