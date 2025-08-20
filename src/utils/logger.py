"""Logging configuration for the application."""

import sys
from pathlib import Path
from loguru import logger

from config.settings import get_settings


def setup_logging(verbose: bool = False) -> None:
    """
    Setup logging configuration.
    
    Args:
        verbose: Enable verbose (debug) logging
    """
    settings = get_settings()
    
    # Remove default logger
    logger.remove()
    
    # Console logging
    log_level = "DEBUG" if verbose else settings.log_level
    logger.add(
        sys.stderr,
        level=log_level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True
    )
    
    # File logging
    log_file = Path(settings.log_file)
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    logger.add(
        log_file,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",
        retention="30 days",
        compression="gz"
    )
    
    logger.info("Logging initialized")


def log_processing_result(source: str, original_text: str, summary: str, metadata: dict) -> None:
    """
    Log the processing results including original text and summary.
    
    Args:
        source: Source file path or URL
        original_text: Original extracted text
        summary: Generated summary
        metadata: Additional metadata (processing time, etc.)
    """
    logger.info("="*100)
    logger.info(f"📄 DOCUMENT PROCESSING COMPLETE: {source}")
    logger.info("="*100)
    
    # Log metadata in a readable format
    logger.info("📊 PROCESSING STATISTICS:")
    for key, value in metadata.items():
        logger.info(f"   • {key}: {value}")
    
    # Log original text with clear formatting
    logger.info("\n" + "🔤 ORIGINAL TEXT (extracted from document):")
    logger.info("-" * 80)
    if len(original_text) > 2000:
        # For long texts, show beginning and end
        logger.info(f"[First 800 characters]")
        logger.info(original_text[:800])
        logger.info(f"\n... [TRUNCATED - total {len(original_text)} characters] ...\n")
        logger.info(f"[Last 800 characters]")
        logger.info(original_text[-800:])
    else:
        logger.info(original_text)
    
    # Log summary with clear formatting
    logger.info("\n" + "✨ GENERATED SUMMARY:")
    logger.info("-" * 80)
    logger.info(summary)
    
    # Analysis comparison
    original_words = len(original_text.split())
    summary_words = len(summary.split())
    compression_ratio = (summary_words / original_words * 100) if original_words > 0 else 0
    
    logger.info("\n" + "📈 SUMMARY ANALYSIS:")
    logger.info(f"   • Original: {original_words} words, {len(original_text)} characters")
    logger.info(f"   • Summary: {summary_words} words, {len(summary)} characters")
    logger.info(f"   • Compression: {compression_ratio:.1f}% of original length")
    
    logger.info("="*100 + "\n")


def log_summary_result(
    input_text: str, 
    summary: str, 
    summary_type: str,
    language_mode: str,
    processing_time: float,
    model_name: str = "Unknown"
) -> None:
    """
    Log detailed summary results with analysis and metrics.
    
    Args:
        input_text: Original input text
        summary: Generated summary
        summary_type: Type of summary (concise, detailed, bullet_points)
        language_mode: Language processing mode (jp->jp, en->jp, en->en)
        processing_time: Time taken for processing
        model_name: Name of the LLM model used
    """
    from config.settings import get_settings
    settings = get_settings()
    
    # Log detailed info only if enabled
    if settings.enable_detailed_log:
        logger.info("🎯 " + "="*80)
        logger.info(f"📝 SUMMARY GENERATION COMPLETE")
        logger.info("🎯 " + "="*80)
        
        # Basic information
        logger.info(f"🤖 Model: {model_name}")
        logger.info(f"🌐 Language Mode: {language_mode}")
        logger.info(f"📋 Summary Type: {summary_type}")
        logger.info(f"⏱️ Processing Time: {processing_time:.2f} seconds")
        
        # Text analysis
        input_chars = len(input_text)
        input_words = len(input_text.split())
        summary_chars = len(summary)
        summary_words = len(summary.split())
        
        compression_ratio = (summary_chars / input_chars * 100) if input_chars > 0 else 0
        word_compression = (summary_words / input_words * 100) if input_words > 0 else 0
        
        logger.info(f"\n📊 TEXT METRICS:")
        logger.info(f"   📥 Input:  {input_words:,} words, {input_chars:,} characters")
        logger.info(f"   📤 Output: {summary_words:,} words, {summary_chars:,} characters")
        logger.info(f"   📉 Compression: {compression_ratio:.1f}% chars, {word_compression:.1f}% words")
        logger.info(f"   ⚡ Speed: {input_chars/processing_time:.0f} chars/sec")
        
        # Input text preview
        logger.info(f"\n📖 INPUT TEXT PREVIEW:")
        logger.info("-" * 60)
        if input_chars > 200:
            logger.info(f"{input_text[:200]}... [truncated, total {input_chars} chars]")
        else:
            logger.info(input_text)
        
        # Complete summary output
        logger.info(f"\n✨ GENERATED SUMMARY:")
        logger.info("-" * 60)
        logger.info(summary)
        
        # Quality indicators
        logger.info(f"\n🎯 QUALITY INDICATORS:")
        if compression_ratio < 30:
            quality = "🟢 Excellent compression"
        elif compression_ratio < 50:
            quality = "🟡 Good compression"
        elif compression_ratio < 70:
            quality = "🟠 Moderate compression"
        else:
            quality = "🔴 Low compression"
        
        speed_rating = "🟢 Fast" if processing_time < 10 else "🟡 Normal" if processing_time < 30 else "🔴 Slow"
        
        logger.info(f"   📏 Compression Quality: {quality}")
        logger.info(f"   ⚡ Processing Speed: {speed_rating}")
        logger.info(f"   🎭 Summary Length: {'🟢 Appropriate' if 50 <= summary_words <= 300 else '🟡 Check length'}")
        
        logger.info("🎯 " + "="*80 + "\n")
    
    # Always log to summary-only file if enabled
    if settings.enable_summary_only_log:
        log_summary_only(input_text, summary, language_mode, processing_time, summary_type)


def log_summary_only(
    input_text: str,
    summary: str,
    language_mode: str,
    processing_time: float,
    summary_type: str = "concise"
) -> None:
    """
    Log only summary results to a dedicated summary log file.
    
    Args:
        input_text: Original input text
        summary: Generated summary
        language_mode: Language processing mode (jp->jp, en->jp, en->en)
        processing_time: Time taken for processing
        summary_type: Type of summary
    """
    from pathlib import Path
    import datetime
    
    # Create summary-specific log file
    summary_log_file = Path("logs/summary_results.log")
    summary_log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Prepare log entry
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    separator = "=" * 80
    
    # Calculate basic metrics
    input_chars = len(input_text)
    summary_chars = len(summary)
    compression_ratio = (summary_chars / input_chars * 100) if input_chars > 0 else 0
    
    # Create log entry
    log_entry = f"""
{separator}
📝 SUMMARY RESULT | {timestamp}
{separator}
🌐 Language: {language_mode}
📋 Type: {summary_type}
⏱️ Time: {processing_time:.2f}s
📊 Compression: {compression_ratio:.1f}% ({input_chars} → {summary_chars} chars)

📥 INPUT:
{input_text[:200]}{'...' if len(input_text) > 200 else ''}

📤 SUMMARY:
{summary}

{separator}

"""
    
    # Write to summary log file
    try:
        with open(summary_log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        logger.error(f"Failed to write summary log: {e}")
