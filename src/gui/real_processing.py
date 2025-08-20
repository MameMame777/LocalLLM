#!/usr/bin/env python3
"""
Real PDF processing functions for LocalLLM GUI
Replaces mock functions with actual document processing and summarization
"""

import sys
import time
import re
import os
from pathlib import Path
from typing import Dict, Any, Optional
import traceback

# Fix encoding issues on Windows
if sys.platform == "win32":
    # Set console output encoding to UTF-8
    os.environ["PYTHONIOENCODING"] = "utf-8"
    
# Import loguru after encoding setup
from loguru import logger

# Safe logging functions to avoid Unicode issues
def safe_log_info(message: str):
    """Safe logging that avoids Unicode encoding issues"""
    try:
        # Remove Unicode characters that cause issues in Windows console
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        logger.info(clean_message)
    except Exception:
        # Fallback to print
        print(f"INFO: {message}")

def safe_log_warning(message: str):
    """Safe warning logging that avoids Unicode encoding issues"""
    try:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        logger.warning(clean_message)
    except Exception:
        print(f"WARNING: {message}")

def safe_log_error(message: str):
    """Safe error logging that avoids Unicode encoding issues"""
    try:
        clean_message = message.encode('ascii', 'ignore').decode('ascii')
        logger.error(clean_message)
    except Exception:
        print(f"ERROR: {message}")

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Import LocalLLM components
from src.document_processor import DocumentProcessor
from src.summarizer_enhanced import LLMSummarizer
from src.batch_processing.batch_processor import ProcessingResult
from src.utils.language_detector import LanguageDetector
from src.summarizer_enhanced import LLMSummarizer
from config.settings import get_settings
from src.batch_processing.batch_processor import ProcessingResult


def real_process_file_global(file_path: Path, **kwargs) -> ProcessingResult:
    """
    Global function for real file processing (pickle-compatible)
    
    Args:
        file_path: Path to the file to process
        **kwargs: Additional parameters including:
            - language: Target language for summary (default: 'ja')
            - max_length: Maximum summary length (default: 200)
            - output_dir: Output directory for individual files
            - use_llm: Whether to use actual LLM (default: True)
            
    Returns:
        ProcessingResult with actual processing outcome
    """
    start_time = time.time()
    
    try:
        # Extract parameters
        language = kwargs.get('language', 'ja')
        max_length = kwargs.get('max_length', 200)
        output_dir = kwargs.get('output_dir', None)
        use_llm = kwargs.get('use_llm', True)
        auto_detect_language = kwargs.get('auto_detect_language', False)
        
        # Initialize language detector
        if auto_detect_language or language == 'auto':
            lang_detector = LanguageDetector()
            safe_log_info(f"Auto-detecting language for: {file_path.name}")
        else:
            lang_detector = None
        
        # Validate file
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Get file info
        file_size = file_path.stat().st_size
        file_size_mb = file_size / (1024 * 1024)
        
        safe_log_info(f"Processing {file_path.name} ({file_size_mb:.2f} MB)")
        
        # Initialize processors
        doc_processor = DocumentProcessor()
        
        # Extract text content
        safe_log_info(f"Extracting text from {file_path}")
        extracted_text = doc_processor.process(str(file_path))
        
        if not extracted_text.strip():
            raise ValueError(f"No text content extracted from {file_path.name}")
        
        word_count = len(extracted_text.split())
        safe_log_info(f"Extracted {word_count} words from {file_path.name}")
        
        # Auto-detect language if enabled
        detected_source_lang = None
        final_target_lang = language
        
        if lang_detector and (auto_detect_language or language == 'auto'):
            try:
                detected_lang, confidence, detailed_info = lang_detector.detect_with_fallback(extracted_text)
                detected_source_lang = detected_lang
                
                safe_log_info(f"Language detected: {detected_lang} (confidence: {confidence:.2f})")
                
                # Determine final target language
                if language == 'auto':
                    final_target_lang = lang_detector.get_recommended_summary_language(detected_lang)
                    safe_log_info(f"Recommended summary language: {final_target_lang}")
                else:
                    final_target_lang = language
                    
            except Exception as e:
                safe_log_warning(f"Language detection failed: {e}, using default: {language}")
                final_target_lang = language if language != 'auto' else 'ja'
        else:
            final_target_lang = language if language != 'auto' else 'ja'
        
        # Generate summary if LLM is requested and available
        summary = ""
        if use_llm:
            try:
                settings = get_settings()
                # Try to find an available model
                model_path = _find_available_model()
                
                if model_path:
                    safe_log_info(f"Using LLM model: {model_path.name}")
                    summarizer = LLMSummarizer(str(model_path), settings)
                    
                    # Generate summary
                    summary = summarizer.summarize(extracted_text)
                    safe_log_info(f"Generated summary for {file_path.name}")
                else:
                    safe_log_warning("No LLM model found, generating extractive summary")
                    summary = _generate_extractive_summary(extracted_text, max_length, final_target_lang)
                    
            except Exception as e:
                safe_log_warning(f"LLM processing failed for {file_path.name}: {str(e)}")
                safe_log_info("Falling back to extractive summary")
                summary = _generate_extractive_summary(extracted_text, max_length, final_target_lang)
        else:
            # Generate simple extractive summary
            summary = _generate_extractive_summary(extracted_text, max_length, final_target_lang)
        
        # Save individual output file if output directory is specified
        output_file = None
        if output_dir:
            output_file = _save_individual_result(
                file_path, extracted_text, summary, output_dir, final_target_lang
            )
        
        # Calculate processing time
        processing_time = time.time() - start_time
        
        # Create detailed result
        result = ProcessingResult(
            file_path=file_path,
            status="success",
            summary=summary,
            processing_time=processing_time,
            metadata={
                'original_size_mb': file_size_mb,
                'word_count': word_count,
                'summary_length': len(summary.split()) if summary else 0,
                'requested_language': language,
                'final_target_language': final_target_lang,
                'detected_source_language': detected_source_lang,
                'language_auto_detected': bool(lang_detector and (auto_detect_language or language == 'auto')),
                'extraction_method': 'llm' if use_llm else 'extractive',
                'output_file': str(output_file) if output_file else None
            }
        )
        
        safe_log_info(f"Successfully processed {file_path.name} in {processing_time:.2f}s")
        return result
        
    except Exception as e:
        processing_time = time.time() - start_time
        error_msg = f"Failed to process {file_path.name}: {str(e)}"
        safe_log_error(f"{error_msg}")
        safe_log_error(f"Error details: {traceback.format_exc()}")
        
        return ProcessingResult(
            file_path=file_path,
            status="error",
            summary="",
            processing_time=processing_time,
            error=error_msg,
            metadata={
                'error_type': type(e).__name__,
                'original_size_mb': file_path.stat().st_size / (1024 * 1024) if file_path.exists() else 0
            }
        )


def _find_available_model() -> Optional[Path]:
    """Find the first available LLM model"""
    model_dir = Path("models")
    
    if not model_dir.exists():
        return None
    
    # Look for GGUF model files
    for model_file in model_dir.glob("*.gguf"):
        if model_file.exists() and model_file.stat().st_size > 1024 * 1024:  # At least 1MB
            return model_file
    
    return None


def _generate_extractive_summary(text: str, max_length: int = 200, target_language: str = 'ja') -> str:
    """
    Generate enhanced technical summary with detailed specifications
    
    Args:
        text: Input text
        max_length: Maximum number of words in summary
        target_language: Target language for summary ('ja', 'en', 'zh', 'ko')
        
    Returns:
        Enhanced technical summary with specifications
    """
    # Enhanced technical extraction patterns
    technical_patterns = {
        'specifications': [
            r'(?:精度|accuracy)[:\s]*([0-9.]+%?[^.\n]*)',
            r'(?:電圧|voltage)[:\s]*([0-9.-]+\s*[VmM]?[Vv][^.\n]*)',
            r'(?:電流|current)[:\s]*([0-9.-]+\s*[μumμmMA]?[Aa][^.\n]*)',
            r'(?:周波数|frequency)[:\s]*([0-9.-]+\s*[kKmMgG]?[Hh][zZ][^.\n]*)',
            r'(?:温度|temperature)[:\s]*([0-9.-]+\s*°?[Cc][^.\n]*)',
            r'(?:レンジ|range)[:\s]*([0-9.-]+[^.\n]*)',
            r'(?:分解能|resolution)[:\s]*([0-9.-]+[^.\n]*)',
            r'(?:ビット|bit)[:\s]*([0-9]+[^.\n]*)',
        ],
        'features': [
            r'(?:特長|特徴|features?)[:\s]*\n?([^。\n]+)',
            r'(?:機能|function)[:\s]*([^。\n]+)',
            r'(?:アプリケーション|applications?)[:\s]*([^。\n]+)',
            r'(?:用途|use)[:\s]*([^。\n]+)',
        ],
        'technical_details': [
            r'(?:入力|input)[:\s]*([^。\n]+)',
            r'(?:出力|output)[:\s]*([^。\n]+)',
            r'(?:動作|operation)[:\s]*([^。\n]+)',
            r'(?:制御|control)[:\s]*([^。\n]+)',
            r'(?:インターフェース|interface)[:\s]*([^。\n]+)',
        ]
    }
    
    # Extract technical information
    extracted_info = {
        'specifications': [],
        'features': [],
        'technical_details': []
    }
    
    for category, patterns in technical_patterns.items():
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                if len(match.strip()) > 5:  # Filter out too short matches
                    extracted_info[category].append(match.strip())
    
    # Build enhanced summary
    summary_parts = []
    
    # Add key specifications
    if extracted_info['specifications']:
        summary_parts.append("【主要仕様】")
        for spec in extracted_info['specifications'][:5]:  # Top 5 specifications
            summary_parts.append(f"• {spec}")
    
    # Add key features
    if extracted_info['features']:
        summary_parts.append("【主要機能】")
        for feature in extracted_info['features'][:3]:  # Top 3 features
            summary_parts.append(f"• {feature}")
    
    # Add technical details
    if extracted_info['technical_details']:
        summary_parts.append("【技術詳細】")
        for detail in extracted_info['technical_details'][:3]:  # Top 3 details
            summary_parts.append(f"• {detail}")
    
    # If no technical info found, fall back to standard extractive summary
    if not any(extracted_info.values()):
        sentences = text.split('.')
        fallback_parts = []
        word_count = 0
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            sentence_words = len(sentence.split())
            if word_count + sentence_words <= max_length:
                fallback_parts.append(sentence)
                word_count += sentence_words
            else:
                break
        
        extractive_summary = '. '.join(fallback_parts)
        if extractive_summary and not extractive_summary.endswith('.'):
            extractive_summary += '.'
    else:
        extractive_summary = '\n'.join(summary_parts)
    
    if not extractive_summary:
        extractive_summary = "No suitable content found for summary."
    
    # Apply translation if target language is different from detected source
    if target_language == 'ja' and not _is_japanese_text(extractive_summary):
        try:
            safe_log_info(f"Attempting translation to Japanese for text of length: {len(extractive_summary)}")
            translated_summary = _translate_to_japanese(extractive_summary)
            if translated_summary and len(translated_summary.strip()) > 10:
                safe_log_info(f"Translation successful. Result length: {len(translated_summary)}")
                return translated_summary
            else:
                safe_log_warning(f"Translation returned insufficient content: '{translated_summary[:50]}...'")
        except Exception as e:
            safe_log_warning(f"Translation failed: {e}, using original text")
    elif target_language == 'ja':
        safe_log_info(f"Text is already Japanese, no translation needed")
    else:
        safe_log_info(f"Target language is {target_language}, no translation needed")
    
    return extractive_summary


def _is_japanese_text(text: str) -> bool:
    """Check if text contains significant Japanese characters"""
    japanese_chars = sum(1 for char in text if '\u3040' <= char <= '\u309F' or 
                        '\u30A0' <= char <= '\u30FF' or 
                        '\u4E00' <= char <= '\u9FAF')
    total_chars = len([c for c in text if c.isalpha()])
    
    if total_chars == 0:
        return False
    
    return japanese_chars / total_chars > 0.1  # 10% threshold


def _translate_to_japanese(text: str) -> str:
    """
    Local translation to Japanese using pattern replacement and technical dictionaries
    
    Args:
        text: English text to translate
        
    Returns:
        Japanese translation (completely offline)
    """
    # Use OFFLINE translation only - no internet required!
    logger.info("🔒 Using offline translation (no internet connection required)")
    
    # Enhanced technical term translation dictionary for semiconductor/IC documents
    translation_patterns = {
        # Document types
        'Data Sheet': 'データシート',
        'data sheet': 'データシート',
        'datasheet': 'データシート',
        'Datasheet': 'データシート',
        
        # Basic electronics
        'Features': '特長',
        'features': '特長',
        'Specifications': '仕様',
        'specifications': '仕様',
        'Application': '用途',
        'application': '用途',
        'Applications': '用途',
        'applications': '用途',
        'Function': '機能',
        'function': '機能',
        'Performance': '性能',
        'performance': '性能',
        
        # AD637 specific (RMS converter)
        'RMS': 'RMS',
        'rms': 'RMS',
        'True RMS': '真のRMS',
        'true rms': '真のRMS',
        'RMS-to-DC': 'RMS-DC変換',
        'converter': 'コンバータ',
        'Converter': 'コンバータ',
        'logarithmic': '対数',
        'Logarithmic': '対数',
        'dB': 'dB',
        'decibel': 'デシベル',
        'Decibel': 'デシベル',
        'crest factor': 'クレストファクタ',
        'Crest factor': 'クレストファクタ',
        'effective value': '実効値',
        'Effective value': '実効値',
        'peak': 'ピーク',
        'Peak': 'ピーク',
        'average': '平均',
        'Average': '平均',
        
        # Voltage and current
        'voltage': '電圧',
        'Voltage': '電圧',
        'current': '電流',
        'Current': '電流',
        'supply': '電源',
        'Supply': '電源',
        'power': '電力',
        'Power': '電力',
        'consumption': '消費',
        'Consumption': '消費',
        
        # Precision and accuracy
        'accuracy': '精度',
        'Accuracy': '精度',
        'precision': '精度',
        'Precision': '精度',
        'resolution': '分解能',
        'Resolution': '分解能',
        'linearity': '直線性',
        'Linearity': '直線性',
        'nonlinearity': '非直線性',
        'Nonlinearity': '非直線性',
        'error': '誤差',
        'Error': '誤差',
        'drift': 'ドリフト',
        'Drift': 'ドリフト',
        'offset': 'オフセット',
        'Offset': 'オフセット',
        
        # Frequency and timing
        'frequency': '周波数',
        'Frequency': '周波数',
        'bandwidth': '帯域幅',
        'Bandwidth': '帯域幅',
        'response': '応答',
        'Response': '応答',
        'settling': 'セトリング',
        'Settling': 'セトリング',
        'time': '時間',
        'Time': '時間',
        
        # Signal types
        'input': '入力',
        'Input': '入力',
        'output': '出力',
        'Output': '出力',
        'signal': '信号',
        'Signal': '信号',
        'analog': 'アナログ',
        'Analog': 'アナログ',
        'digital': 'デジタル',
        'Digital': 'デジタル',
        'differential': '差動',
        'Differential': '差動',
        'single-ended': 'シングルエンド',
        'Single-ended': 'シングルエンド',
        'unipolar': '単極性',
        'Unipolar': '単極性',
        'bipolar': '双極性',
        'Bipolar': '双極性',
        
        # Temperature and environmental
        'temperature': '温度',
        'Temperature': '温度',
        'operating': '動作',
        'Operating': '動作',
        'ambient': '周囲',
        'Ambient': '周囲',
        'range': 'レンジ',
        'Range': 'レンジ',
        'condition': '条件',
        'Condition': '条件',
        'conditions': '条件',
        'Conditions': '条件',
        
        # Package and pins
        'package': 'パッケージ',
        'Package': 'パッケージ',
        'pin': 'ピン',
        'Pin': 'ピン',
        'pins': 'ピン',
        'Pins': 'ピン',
        'lead': 'リード',
        'Lead': 'リード',
        'SOIC': 'SOIC',
        'DIP': 'DIP',
        'PDIP': 'PDIP',
        
        # Common values
        'typical': '標準',
        'Typical': '標準',
        'minimum': '最小',
        'Minimum': '最小',
        'maximum': '最大',
        'Maximum': '最大',
        'nominal': '公称',
        'Nominal': '公称',
        'Information furnished': '提供される情報',
        'information furnished': '提供される情報',
        'believed to be accurate': '正確であると考えられている',
        'reliable': '信頼性のある',
        'responsibility': '責任',
        'assumed': '想定される',
        'infringements': '侵害',
        'patents': '特許',
        'third parties': '第三者',
        'subject to change': '変更される可能性がある',
        'without notice': '予告なし',
        'license': 'ライセンス',
        'granted': '付与される',
        'implication': '含意',
        'otherwise': 'その他',
        'Trademarks': '商標',
        'trademarks': '商標',
        'registered': '登録',
        'property': '財産',
        'respective': 'それぞれの',
        'owners': '所有者',
        'Technology Way': 'テクノロジー・ウェイ',
        'All rights reserved': '全権留保',
        'Rev.': '改訂版',
        'PulSAR': 'PulSAR',
        '16-Bit': '16ビット',
        '4-Channel': '4チャンネル',
        '8-Channel': '8チャンネル',
        '250 kSPS': '250 kSPS',
        'no missing codes': 'ミッシングコードなし',
        'choice of inputs': '入力選択',
        'Pseudo bipolar': '疑似双極性',
        'GND sense': 'GND センス'
    }
    
    # Apply translations
    translated_text = text
    for english, japanese in translation_patterns.items():
        translated_text = translated_text.replace(english, japanese)
    
    # Basic sentence structure improvements
    sentence_patterns = {
        'However, no responsibility is assumed': 'ただし、責任は負いません',
        'for its use': 'その使用について',
        'that may result from its use': 'その使用から生じる可能性のある',
        'No license is granted': 'ライセンスは付与されません',
        'by implication or otherwise': '暗示またはその他の方法により',
        'under any patent': 'いかなる特許の下でも',
        'or patent rights': 'または特許権',
        'and registered trademarks': 'および登録商標',
        'are the property of': 'の財産です',
        'their respective owners': 'それぞれの所有者',
        'with no missing codes': 'ミッシングコードなし',
        'with choice of inputs': '入力選択機能付き'
    }
    
    for english_phrase, japanese_phrase in sentence_patterns.items():
        translated_text = translated_text.replace(english_phrase, japanese_phrase)
    
    # Add contextual prefix for technical documents
    if any(term in text.lower() for term in ['adc', 'data sheet', 'analog devices', 'resolution', 'channel']):
        if not translated_text.startswith('データシート') and not translated_text.startswith('技術文書'):
            translated_text = f"技術文書要約: {translated_text}"
    
    return translated_text
    translation_patterns = {
        # Common technical terms
        'Data Sheet': 'データシート',
        'Features': '特長',
        'Resolution': '分解能',
        'Channel': 'チャンネル',
        'Multiplexer': 'マルチプレクサ',
        'Unipolar': '単極性',
        'Differential': '差動',
        'Throughput': 'スループット',
        'Dynamic range': 'ダイナミックレンジ',
        'ADC': 'ADC（アナログ-デジタル変換器）',
        'ADCs': 'ADC（アナログ-デジタル変換器）',
        'Analog Devices': 'アナログ・デバイセズ',
        'Technical Support': 'テクニカルサポート',
        'Document Feedback': 'ドキュメントフィードバック',
        'Specifications': '仕様',
        'LSB': 'LSB（最下位ビット）',
        'INL': 'INL（積分非直線性）',
        'SINAD': 'SINAD（信号対雑音歪み比）',
        'bit resolution': 'ビット分解能',
        'missing codes': 'ミッシングコード',
        'single-ended': 'シングルエンド',
        'bipolar': '双極性',
        'maximum': '最大',
        'typical': '標準',
        'minimum': '最小'
    }
    
    translated_text = text
    for english, japanese in translation_patterns.items():
        translated_text = translated_text.replace(english, japanese)
    
    # Add basic context if it looks like a technical document
    if any(term in text.lower() for term in ['adc', 'data sheet', 'analog devices', 'resolution']):
        translated_text = f"このドキュメントについて: {translated_text}"
    
    return translated_text


def _save_individual_result(file_path: Path, extracted_text: str, summary: str, 
                          output_dir: str, language: str) -> Path:
    """
    Save individual processing result to file
    
    Args:
        file_path: Original file path
        extracted_text: Extracted text content
        summary: Generated summary
        output_dir: Output directory
        language: Target language
        
    Returns:
        Path to saved output file
    """
    output_path = Path(output_dir) / "processed"
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Generate output filename
    base_name = file_path.stem
    output_file = output_path / f"{base_name}_summary_{language}.md"
    
    # Create markdown content
    content = f"""# {file_path.name} - Processing Result

## File Information
- **Original File**: {file_path.name}
- **File Size**: {file_path.stat().st_size / (1024 * 1024):.2f} MB
- **Processing Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Target Language**: {language}

## Summary
{summary}

## Extracted Text
```
{extracted_text[:2000]}{'...' if len(extracted_text) > 2000 else ''}
```

---
*Generated by LocalLLM Batch Processor*
"""
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return output_file


def create_real_processing_function(**default_params):
    """
    Create a real processing function with default parameters
    
    Args:
        **default_params: Default parameters for processing
        
    Returns:
        Configured processing function
    """
    def process_func(file_path: Path, **kwargs):
        # Merge default params with provided kwargs
        params = {**default_params, **kwargs}
        return real_process_file_global(file_path, **params)
    
    return process_func


# Test function for development
def test_real_processing():
    """Test the real processing function with a sample file"""
    import sys
    from pathlib import Path
    
    # Add src to path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    
    # Test with data directory
    data_dir = Path("data")
    if data_dir.exists():
        # Find first PDF file
        for pdf_file in data_dir.glob("*.pdf"):
            print(f"🧪 Testing real processing with: {pdf_file.name}")
            
            result = real_process_file_global(
                file_path=pdf_file,
                language='ja',
                max_length=150,
                output_dir='output/test_real',
                use_llm=False  # Start with extractive summary
            )
            
            print(f"📊 Result: {result.status}")
            print(f"🕐 Time: {result.processing_time:.2f}s")
            print(f"📝 Summary: {result.summary[:100]}...")
            break
    else:
        print("❌ No data directory found for testing")


if __name__ == "__main__":
    test_real_processing()
