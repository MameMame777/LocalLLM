#!/usr/bin/env python3
"""
Google Translate Integration for Batch Processing
Simple, reliable translation service
"""

import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json
import sys
import re

# Add src to path for compatibility
sys.path.insert(0, str(Path(__file__).parent.parent))

class GoogleTranslateProcessor:
    """Simple Google Translate API processor for technical documents"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def translate_text(self, text: str, target_lang: str = 'ja', source_lang: str = 'en') -> str:
        """
        Translate text using Google Translate
        
        Args:
            text: Text to translate
            target_lang: Target language (default: Japanese)
            source_lang: Source language (default: English)
            
        Returns:
            Translated text
        """
        try:
            # Use free Google Translate service
            url = "https://translate.googleapis.com/translate_a/single"
            params = {
                'client': 'gtx',
                'sl': source_lang,
                'tl': target_lang,
                'dt': 't',
                'q': text[:5000]  # Limit to 5000 characters
            }
            
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result and result[0]:
                    # Extract translated text
                    translated_parts = []
                    for part in result[0]:
                        if part[0]:
                            translated_parts.append(part[0])
                    return ''.join(translated_parts)
            
            # Fallback: return original text if translation fails
            return f"[翻訳エラー] {text[:200]}..."
            
        except Exception as e:
            print(f"Translation error: {e}")
            return f"[翻訳失敗] {text[:200]}..."
    
    def extract_and_translate_document(self, file_path: Path) -> Dict[str, Any]:
        """
        Extract content from document and translate to Japanese
        
        Args:
            file_path: Path to document file
            
        Returns:
            Processing result with translation
        """
        start_time = time.time()
        
        try:
            # Extract content based on file type
            content = self._extract_content(file_path)
            
            if not content.strip():
                return {
                    'success': False,
                    'error': 'コンテンツの抽出ができませんでした',
                    'file_name': file_path.name
                }
            
            # Summarize content (first part if too long)
            if len(content) > 2000:
                # Extract key sections for technical documents
                summary_content = self._extract_key_sections(content)
            else:
                summary_content = content
            
            # Translate to Japanese
            japanese_translation = self.translate_text(summary_content, 'ja', 'en')
            
            # Create detailed summary
            processing_time = time.time() - start_time
            file_size_mb = file_path.stat().st_size / (1024 * 1024)
            
            return {
                'success': True,
                'japanese_translation': japanese_translation,
                'original_content': content[:500] + "..." if len(content) > 500 else content,
                'file_name': file_path.name,
                'file_size_mb': file_size_mb,
                'processing_time': processing_time,
                'translation_method': 'Google Translate',
                'word_count': len(content.split()),
                'character_count': len(content),
                'translation_length': len(japanese_translation)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'file_name': file_path.name,
                'processing_time': time.time() - start_time
            }
    
    def _extract_content(self, file_path: Path) -> str:
        """Extract content from file based on file type"""
        
        if file_path.suffix.lower() == '.pdf':
            return self._extract_pdf_content(file_path)
        elif file_path.suffix.lower() in ['.html', '.htm']:
            return self._extract_html_content(file_path)
        elif file_path.suffix.lower() in ['.txt', '.md']:
            return self._extract_text_content(file_path)
        else:
            # Try as text file
            return self._extract_text_content(file_path)
    
    def _extract_pdf_content(self, file_path: Path) -> str:
        """Extract content from PDF file"""
        try:
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                content = ""
                for page in pdf_reader.pages[:5]:  # First 5 pages only
                    content += page.extract_text()
                return content
        except ImportError:
            # Fallback: read as binary and extract text patterns
            with open(file_path, 'rb') as file:
                binary_content = file.read()
                # Simple text extraction from PDF
                text_content = binary_content.decode('latin-1', errors='ignore')
                # Extract readable text using regex
                readable_text = re.findall(r'[A-Za-z0-9\s\.,;:\-\(\)]+', text_content)
                return ' '.join(readable_text)[:2000]
        except Exception as e:
            return f"PDF読み込みエラー: {e}"
    
    def _extract_html_content(self, file_path: Path) -> str:
        """Extract content from HTML file"""
        try:
            from bs4 import BeautifulSoup
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                html_content = file.read()
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text()
        except ImportError:
            # Fallback: simple HTML tag removal
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                html_content = file.read()
            # Remove HTML tags
            clean_text = re.sub(r'<[^>]+>', ' ', html_content)
            return clean_text
        except Exception as e:
            return f"HTML読み込みエラー: {e}"
    
    def _extract_text_content(self, file_path: Path) -> str:
        """Extract content from text file"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                return file.read()
        except Exception as e:
            return f"テキスト読み込みエラー: {e}"
    
    def _extract_key_sections(self, content: str) -> str:
        """Extract key sections from technical document"""
        # Look for key technical sections
        key_patterns = [
            r'FEATURES?[:\s]*([^\n]{0,500})',
            r'SPECIFICATIONS?[:\s]*([^\n]{0,500})',
            r'DESCRIPTION[:\s]*([^\n]{0,500})',
            r'OVERVIEW[:\s]*([^\n]{0,500})',
            r'APPLICATIONS?[:\s]*([^\n]{0,500})'
        ]
        
        extracted_sections = []
        for pattern in key_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            extracted_sections.extend(matches)
        
        if extracted_sections:
            return ' '.join(extracted_sections)[:1500]
        else:
            # Return first 1500 characters if no key sections found
            return content[:1500]


def create_google_translate_processing_function():
    """Create comprehensive Google Translate processing function for batch processing"""
    
    def process_with_google_translate(file_path: Path, **kwargs) -> str:
        """
        Process file using Google Translate for reliable translation
        
        Args:
            file_path: Path to the file to process
            **kwargs: Additional parameters
            
        Returns:
            Formatted translation result
        """
        try:
            start_time = time.time()
            
            # Extract content based on file type
            content = ""
            if file_path.suffix.lower() == '.pdf':
                try:
                    import PyPDF2
                    with open(file_path, 'rb') as file:
                        pdf_reader = PyPDF2.PdfReader(file)
                        for page in pdf_reader.pages:
                            content += page.extract_text()
                except ImportError:
                    print(f"⚠️ PyPDF2 not available, treating {file_path.name} as text")
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    content = f"PDF読み込みエラー: {e}"
                    
            elif file_path.suffix.lower() in ['.html', '.htm']:
                try:
                    from bs4 import BeautifulSoup
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        html_content = f.read()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    content = soup.get_text()
                except ImportError:
                    print(f"⚠️ BeautifulSoup not available, treating {file_path.name} as text")
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    content = f"HTML読み込みエラー: {e}"
            else:
                # Text file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            
            if not content.strip():
                return _create_error_result(file_path, "ファイルからコンテンツを抽出できませんでした")
            
            # Initialize Google Translate processor
            translator = GoogleTranslateProcessor()
            
            # Limit content for better translation quality
            max_chars = 3000
            if len(content) > max_chars:
                # Take first part for summary
                content_for_translation = content[:max_chars]
                truncated = True
            else:
                content_for_translation = content
                truncated = False
            
            print(f"🌐 Translating {file_path.name} with Google Translate...")
            
            # Translate content
            japanese_translation = translator.translate_text(content_for_translation)
            
            # Create summary from translation
            summary = _create_summary_from_translation(japanese_translation, file_path.name)
            
            processing_time = time.time() - start_time
            
            # Create comprehensive result
            result = _create_google_translate_result(
                file_path=file_path,
                original_content=content,
                japanese_translation=japanese_translation,
                summary=summary,
                processing_time=processing_time,
                truncated=truncated
            )
            
            print(f"✅ Translation completed: {len(japanese_translation)} chars in {processing_time:.2f}s")
            return result
                
        except Exception as e:
            return _create_error_result(file_path, f"処理エラー: {str(e)}")
    
    return process_with_google_translate

def _create_summary_from_translation(translation: str, filename: str) -> str:
    """Create a concise summary from the translated text"""
    
    # Extract key information patterns
    sentences = [s.strip() for s in translation.split('。') if s.strip()]
    
    # Take first few sentences as summary
    summary_sentences = sentences[:3] if len(sentences) >= 3 else sentences
    summary = '。'.join(summary_sentences)
    
    if summary and not summary.endswith('。'):
        summary += '。'
    
    # If summary is too short, add more context
    if len(summary) < 100 and len(sentences) > 3:
        additional = sentences[3:5]
        summary += '。'.join(additional) + '。'
    
    return summary if summary else "要約を生成できませんでした。"

def _create_google_translate_result(file_path: Path, original_content: str, 
                                  japanese_translation: str, summary: str,
                                  processing_time: float, truncated: bool) -> str:
    """Create formatted Google Translate result"""
    
    # Get file stats
    file_size_mb = file_path.stat().st_size / (1024 * 1024)
    word_count = len(original_content.split())
    char_count = len(original_content)
    
    truncation_note = "（長い文書のため一部を翻訳）" if truncated else ""
    
    result = f"""# 📚 技術文書翻訳レポート {truncation_note}
**ファイル名:** {file_path.name}
**処理日時:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**翻訳サービス:** Google Translate
**処理時間:** {processing_time:.2f}秒
**ファイルサイズ:** {file_size_mb:.2f} MB

## 📊 処理情報
- **原文字数:** {char_count:,} 文字
- **原文単語数:** {word_count:,} 語
- **翻訳文字数:** {len(japanese_translation):,} 文字
- **品質:** Google翻訳による高品質翻訳

## 📝 要約

{summary}

## 📄 完全な日本語翻訳

{japanese_translation}

## 📖 原文プレビュー (最初の300文字)

{original_content[:300]}{'...' if len(original_content) > 300 else ''}

---
*Generated by LocalLLM Google Translate Integration*
"""
    
    return result

def _create_error_result(file_path: Path, error_message: str) -> str:
    """Create error result format"""
    
    result = f"""# ❌ 処理エラーレポート
**ファイル名:** {file_path.name}
**処理日時:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**エラー:** {error_message}

## 問題の詳細

ファイル処理中にエラーが発生しました。以下を確認してください：

1. ファイル形式が対応している (.pdf, .html, .txt)
2. ファイルが破損していない
3. インターネット接続が利用可能

---
*Error in LocalLLM Google Translate Processing*
"""
    
    return result
    """Create Google Translate processing function for batch processing"""
    
    translator = GoogleTranslateProcessor()
    
    def process_with_google_translate(file_path: Path, **kwargs) -> str:
        """Process file using Google Translate"""
        try:
            # Process document
            result = translator.extract_and_translate_document(file_path)
            
            if not result['success']:
                return f"""# ❌ 処理エラー
**ファイル名**: {result['file_name']}
**処理日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## エラー内容
{result['error']}
"""
            
            # Format successful result
            formatted_result = f"""# 📚 技術文書翻訳レポート (Google翻訳)
**ファイル名**: {result['file_name']}
**処理日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**ファイルサイズ**: {result['file_size_mb']:.2f} MB
**処理時間**: {result['processing_time']:.2f}秒
**翻訳方法**: {result['translation_method']}

## 📄 日本語翻訳
{result['japanese_translation']}

## 📊 処理統計
- **元文字数**: {result['character_count']:,} 文字
- **単語数**: {result['word_count']:,} 語
- **翻訳文字数**: {result['translation_length']:,} 文字
- **圧縮率**: {(result['translation_length'] / result['character_count'] * 100):.1f}%

## 📖 原文プレビュー (最初の500文字)
```
{result['original_content']}
```

---
*Generated by Google Translate Batch Processor*
"""
            
            return formatted_result
            
        except Exception as e:
            return f"""# ❌ 処理エラー
**ファイル名**: {file_path.name}
**処理日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## エラー内容
{str(e)}
"""
    
    return process_with_google_translate


# Test function
if __name__ == "__main__":
    # Test the Google Translate processor
    processor = GoogleTranslateProcessor()
    
    # Test translation
    test_text = "TMP112 is a high-accuracy, low-power digital temperature sensor."
    translated = processor.translate_text(test_text)
    print(f"Original: {test_text}")
    print(f"Translated: {translated}")
