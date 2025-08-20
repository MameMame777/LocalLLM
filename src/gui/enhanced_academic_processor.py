#!/usr/bin/env python3
"""
Enhanced Academic Processing with LLM Summarization + Google Translate
Combines LLM summarization with Google Translate for best quality
"""

import time
import requests
import threading
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import json
import sys
import re
from loguru import logger

# Global lock for LLM access to prevent concurrent usage
_llm_lock = threading.Lock()

# Add src to path for compatibility
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

try:
    from summarizer_enhanced import LLMSummarizer
    from config.settings import Settings
    from config.llama2_config import LLAMA2_MODEL_PATH, LLAMA2_GENERATION_CONFIG
    llm_available = True
    logger.info("✅ LLM components available")
except ImportError as e:
    logger.warning(f"⚠️ LLM components not available: {e}")
    llm_available = False

class EnhancedAcademicProcessor:
    """Enhanced Academic Processor: LLM Summarization + Google Translate"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Initialize LLM if available
        self.llm_summarizer = None
        self.llm_available = llm_available
        self._initialize_llm()
    
    def _initialize_llm(self) -> bool:
        """Initialize LLM summarizer if available"""
        if not self.llm_available:
            logger.warning("⚠️ LLM components not available - using fallback summarization")
            return False
        
        try:
            settings = Settings()
            model_path = Path(LLAMA2_MODEL_PATH)
            
            if not model_path.exists():
                logger.warning(f"⚠️ LLM model not found: {model_path}")
                logger.info("💡 Run 'python download_llama2.py' to enable LLM summarization")
                return False
                
            logger.info("🤖 Initializing LLM for summarization...")
            self.llm_summarizer = LLMSummarizer(
                model_path=str(model_path),
                settings=settings
            )
            logger.success("✅ LLM summarizer initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM: {e}")
            logger.info("💡 Falling back to basic summarization")
            return False
    
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
            # First try using googletrans library directly
            from googletrans import Translator
            translator = Translator()
            
            # Split long text into chunks for better translation
            if len(text) > 5000:
                chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
                translated_chunks = []
                
                for chunk in chunks:
                    try:
                        result = translator.translate(chunk, dest=target_lang, src=source_lang)
                        translated_chunks.append(result.text if result.text else chunk)
                    except Exception as e:
                        logger.warning(f"Chunk translation failed: {e}")
                        translated_chunks.append(chunk)
                
                return ' '.join(translated_chunks)
            else:
                # Translate short text directly
                result = translator.translate(text, dest=target_lang, src=source_lang)
                return result.text if result.text else text
                
        except Exception as e:
            logger.warning(f"Googletrans translation failed: {e}")
            
        try:
            # Fallback: Use free Google Translate API with chunking for large texts
            if len(text) > 5000:
                # Split into chunks for large texts
                chunks = [text[i:i+4500] for i in range(0, len(text), 4500)]
                translated_chunks = []
                
                for chunk in chunks:
                    try:
                        url = "https://translate.googleapis.com/translate_a/single"
                        params = {
                            'client': 'gtx',
                            'sl': source_lang,
                            'tl': target_lang,
                            'dt': 't',
                            'q': chunk
                        }
                        
                        response = self.session.get(url, params=params, timeout=15)
                        response.raise_for_status()
                        
                        # Parse Google Translate response
                        result = response.json()
                        translated_text = ''
                        
                        if result and result[0]:
                            for translation in result[0]:
                                if translation[0]:
                                    translated_text += translation[0]
                        
                        translated_chunks.append(translated_text if translated_text else chunk)
                        time.sleep(0.5)  # Rate limiting
                        
                    except Exception as chunk_error:
                        logger.warning(f"Chunk translation failed: {chunk_error}")
                        translated_chunks.append(chunk)
                
                return ' '.join(translated_chunks)
            else:
                url = "https://translate.googleapis.com/translate_a/single"
                params = {
                    'client': 'gtx',
                    'sl': source_lang,
                    'tl': target_lang,
                    'dt': 't',
                    'q': text
                }
                
                response = self.session.get(url, params=params, timeout=10)
                response.raise_for_status()
                
                # Parse Google Translate response
                result = response.json()
                translated_text = ''
                
                if result and result[0]:
                    for translation in result[0]:
                        if translation[0]:
                            translated_text += translation[0]
                
                return translated_text if translated_text else text
            
        except Exception as e:
            logger.warning(f"Free API translation failed: {e}")
            return text  # Return original text if translation fails
    
    def _process_large_academic_content(self, content: str, file_path: Path) -> tuple[str, str]:
        """
        Process large academic content with enhanced analysis for technical novelty and contributions
        
        Args:
            content: Large academic text content
            file_path: Path to the file being processed
            
        Returns:
            Tuple of (enhanced_academic_summary, combined_chunks)
        """
        logger.info(f"📄 Processing large academic content ({len(content)} chars) with enhanced analysis")
        
        # Split content into larger chunks for academic analysis
        chunks = self._split_content_into_chunks(content, chunk_size=8000, overlap=400)  # Increased chunk size
        logger.info(f"📋 Split into {len(chunks)} academic chunks")
        
        chunk_summaries = []
        processed_chunks = []
        technical_insights = []
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"🔄 Processing academic chunk {i}/{len(chunks)} ({len(chunk)} chars)")
            
            try:
                # First extract technical novelty and contributions
                novelty_content = self._extract_technical_novelty(chunk)
                
                # If novelty content is insufficient, try key sections
                if len(novelty_content.strip()) < 150:
                    key_sections = self._extract_key_sections(chunk)
                    chunk_content = key_sections if len(key_sections) > len(novelty_content) else novelty_content
                else:
                    chunk_content = novelty_content
                
                # Fallback to technical content if still insufficient
                if len(chunk_content.strip()) < 150:
                    technical_content = self._extract_technical_content(chunk)
                    chunk_content = technical_content if len(technical_content) > len(chunk_content) else chunk[:3000]
                
                # Limit chunk size for LLM but allow larger content for academic analysis
                if len(chunk_content) > 3000:
                    chunk_content = chunk_content[:3000] + "..."
                
                # Create enhanced academic summary for this chunk
                if self.llm_summarizer:
                    with _llm_lock:  # Prevent concurrent LLM access
                        logger.debug(f"🔒 Acquired LLM lock for academic chunk {i}")
                        chunk_summary = self.llm_summarizer.summarize_english_to_english(
                            chunk_content, 
                            summary_type="academic_detailed"  # Enhanced academic analysis
                        )
                        logger.debug(f"🔓 Released LLM lock for academic chunk {i}")
                else:
                    chunk_summary = self._create_fallback_summary(chunk_content)
                
                if chunk_summary and len(chunk_summary.strip()) > 20:
                    # Enhance chunk summary with academic structure
                    enhanced_summary = f"Section {i} Analysis: {chunk_summary}"
                    chunk_summaries.append(enhanced_summary)
                    processed_chunks.append(chunk_content)
                    
                    # Extract technical insights for meta-analysis
                    if "novel" in chunk_summary.lower() or "propose" in chunk_summary.lower() or "contribution" in chunk_summary.lower():
                        technical_insights.append(f"Innovation {i}: {chunk_summary[:200]}...")
                    
                    logger.success(f"✅ Academic chunk {i} processed successfully")
                else:
                    logger.warning(f"⚠️ Academic chunk {i} produced insufficient summary")
                    
            except Exception as e:
                logger.error(f"❌ Error processing academic chunk {i}: {e}")
                # Continue with next chunk
                continue
        
        if not chunk_summaries:
            logger.warning("⚠️ No academic chunks produced valid summaries, using fallback")
            return self._create_fallback_summary(content[:8000]), content[:8000]
        
        # Create comprehensive academic summary
        combined_summary = self._create_comprehensive_academic_summary(chunk_summaries, technical_insights)
        
        # Combine processed chunks for reference
        combined_chunks = "\n\n".join(processed_chunks[:5])  # Take more chunks for academic content
        
        return combined_summary, combined_chunks

    def _create_comprehensive_academic_summary(self, chunk_summaries: list, technical_insights: list) -> str:
        """Create a comprehensive academic summary with technical analysis"""
        
        # Combine chunk summaries
        base_summary = "\n\n".join(chunk_summaries)
        
        # If the combined summary is very long, create a meta-summary with academic focus
        if len(base_summary) > 2500:
            logger.info("📝 Creating meta-summary for comprehensive academic analysis")
            
            # Create structured academic meta-summary
            academic_structure = f"""
Technical Innovation Summary:
{chr(10).join(technical_insights[:3]) if technical_insights else "Technical innovations identified in analysis."}

Comprehensive Analysis:
{base_summary[:2000]}...

Key Contributions:
Based on the analysis, this work presents novel approaches and methodologies with significant technical contributions to the field.
"""
            
            # Use LLM for final academic meta-summary if available
            if self.llm_summarizer:
                try:
                    with _llm_lock:
                        logger.debug("🔒 Acquired LLM lock for academic meta-summary")
                        meta_summary = self.llm_summarizer.summarize_english_to_english(
                            academic_structure, 
                            summary_type="academic_comprehensive"
                        )
                        logger.debug("🔓 Released LLM lock for academic meta-summary")
                        return meta_summary
                except Exception as e:
                    logger.error(f"❌ Error creating academic meta-summary: {e}")
                    return academic_structure
            else:
                return academic_structure
        
        return base_summary

    def _split_content_into_chunks(self, content: str, chunk_size: int = None, overlap: int = None) -> list[str]:
        """
        Split large content into manageable chunks with overlap
        
        Args:
            content: Text content to split
            chunk_size: Maximum size of each chunk
            overlap: Number of characters to overlap between chunks
            
        Returns:
            List of text chunks
        """
        if len(content) <= chunk_size:
            return [content]
        
        chunks = []
        start = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # If this is not the last chunk, try to break at sentence boundary
            if end < len(content):
                # Look for sentence endings within the last 500 characters
                search_start = max(end - 500, start)
                sentence_end = -1
                
                for i in range(end, search_start, -1):
                    if content[i] in '.!?。！？':
                        sentence_end = i + 1
                        break
                
                if sentence_end > 0:
                    end = sentence_end
            
            chunk = content[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap if end < len(content) else end
            
            # Prevent infinite loop
            if start >= len(content):
                break
        
        return chunks

    def _process_large_content(self, content: str, file_path: Path) -> tuple[str, str]:
        """
        Process large content by splitting into chunks and combining results
        
        Args:
            content: Large text content
            file_path: Path to the file being processed
            
        Returns:
            Tuple of (english_summary, combined_chunks)
        """
        logger.info(f"📄 Processing large content ({len(content)} chars) in chunks")
        
        # Split content into chunks
        chunks = self._split_content_into_chunks(content)
        logger.info(f"📋 Split into {len(chunks)} chunks")
        
        chunk_summaries = []
        processed_chunks = []
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"🔄 Processing chunk {i}/{len(chunks)} ({len(chunk)} chars)")
            
            try:
                # Extract key sections from this chunk
                key_sections = self._extract_key_sections(chunk)
                
                if len(key_sections.strip()) < 100:
                    technical_content = self._extract_technical_content(chunk)
                    chunk_content = technical_content if len(technical_content) > len(key_sections) else chunk[:2000]
                else:
                    chunk_content = key_sections
                
                # Limit chunk size for LLM
                if len(chunk_content) > 2000:
                    chunk_content = chunk_content[:2000] + "..."
                
                # Create summary for this chunk with thread lock
                if self.llm_summarizer:
                    with _llm_lock:  # Prevent concurrent LLM access
                        logger.debug(f"🔒 Acquired LLM lock for chunk {i}")
                        chunk_summary = self.llm_summarizer.summarize_english_to_english(
                            chunk_content, 
                            summary_type="concise"
                        )
                        logger.debug(f"🔓 Released LLM lock for chunk {i}")
                else:
                    chunk_summary = self._create_fallback_summary(chunk_content)
                
                if chunk_summary and len(chunk_summary.strip()) > 10:
                    chunk_summaries.append(f"Part {i}: {chunk_summary}")
                    processed_chunks.append(chunk_content)
                    logger.success(f"✅ Chunk {i} processed successfully")
                else:
                    logger.warning(f"⚠️ Chunk {i} produced empty summary")
                    
            except Exception as e:
                logger.error(f"❌ Error processing chunk {i}: {e}")
                # Continue with next chunk
                continue
        
        if not chunk_summaries:
            logger.warning("⚠️ No chunks produced valid summaries, using fallback")
            return self._create_fallback_summary(content[:5000]), content[:5000]
        
        # Combine chunk summaries into final summary
        combined_summary = "\n\n".join(chunk_summaries)
        
        # If combined summary is still too long, summarize it again
        if len(combined_summary) > 3000 and self.llm_summarizer:
            logger.info("📝 Final summary too long, creating meta-summary")
            try:
                with _llm_lock:  # Prevent concurrent LLM access
                    logger.debug("🔒 Acquired LLM lock for meta-summary")
                    final_summary = self.llm_summarizer.summarize_english_to_english(
                        combined_summary,
                        summary_type="concise"
                    )
                    logger.debug("🔓 Released LLM lock for meta-summary")
                if final_summary and len(final_summary.strip()) > 10:
                    combined_summary = final_summary
            except Exception as e:
                logger.warning(f"Meta-summary failed: {e}")
        
        # Combine processed chunks for translation
        combined_chunks = "\n\n".join(processed_chunks[:3])  # Limit to first 3 chunks for translation
        
        logger.success(f"✅ Large content processing completed: {len(chunk_summaries)} chunks processed")
        return combined_summary, combined_chunks

    def create_llm_summary(self, content: str) -> str:
        """Create summary using LLM with enhanced academic analysis and full PDF processing"""
        
        if self.llm_summarizer:
            try:
                logger.info("🤖 Generating LLM-based summary with academic analysis...")
                
                # For academic papers, use more flexible thresholds for full processing
                if len(content) > 15000:  # Reduced threshold for academic content
                    logger.info(f"📄 Large academic content detected ({len(content)} chars), using comprehensive chunk processing")
                    summary, _ = self._process_large_academic_content(content, Path("academic_content"))
                    return summary
                
                # First try to extract technical novelty and contributions
                novelty_content = self._extract_technical_novelty(content)
                
                # If novelty extraction is insufficient, fall back to key sections
                if len(novelty_content.strip()) < 200:
                    logger.info("🔄 Novelty extraction insufficient, trying key sections...")
                    key_sections = self._extract_key_sections(content)
                    summarization_text = key_sections if len(key_sections) > len(novelty_content) else novelty_content
                else:
                    summarization_text = novelty_content
                
                # If still insufficient, use broader technical content
                if len(summarization_text.strip()) < 200:
                    logger.warning("⚠️ Key sections insufficient, using technical content extraction")
                    summarization_text = self._extract_technical_content(content)
                
                # Allow larger text for JSON URL processing with individual summaries
                if len(summarization_text) > 15000:  # Increased significantly for JSON processing
                    logger.info(f"📏 Text lengthy ({len(summarization_text)} chars), truncating to 15000 chars for comprehensive JSON analysis")
                    summarization_text = summarization_text[:15000] + "..."
                
                logger.info(f"📝 Summarizing academic content: {len(summarization_text)} characters")
                
                # Use LLM for high-quality academic summarization with enhanced prompt
                with _llm_lock:  # Prevent concurrent LLM access
                    logger.debug("🔒 Acquired LLM lock for academic summary")
                    summary = self.llm_summarizer.summarize_english_to_english(
                        summarization_text, 
                        summary_type="academic_detailed"  # Enhanced academic analysis
                    )
                    logger.debug("🔓 Released LLM lock for academic summary")
                
                if summary and len(summary.strip()) > 10:
                    logger.success(f"✅ LLM summary generated ({len(summary)} characters)")
                    return summary
                else:
                    logger.warning("⚠️ LLM returned empty/short summary, using fallback")
                    return self._create_fallback_summary(summarization_text)
                
            except Exception as e:
                logger.error(f"❌ LLM summarization failed: {e}")
                logger.info("🔄 Falling back to basic summarization")
        
        # Fallback: Extract key sections for summarization
        return self._create_fallback_summary(content)
    
    def _create_fallback_summary(self, content: str) -> str:
        """Create basic summary when LLM is not available"""
        
        # Extract key sections
        sections = self._extract_key_sections(content)
        
        # Take first few sentences as summary
        sentences = [s.strip() for s in sections.split('.') if s.strip()]
        summary_sentences = sentences[:4] if len(sentences) >= 4 else sentences
        summary = '. '.join(summary_sentences)
        
        if summary and not summary.endswith('.'):
            summary += '.'
        
        # Add technical context if available
        if len(summary) < 150 and len(sentences) > 4:
            additional = sentences[4:6]
            summary += ' ' + '. '.join(additional) + '.'
        
        return summary if summary else "Unable to generate summary from content."
    
    def _extract_technical_novelty(self, content: str) -> str:
        """Extract technical novelty, contributions, and key features from academic papers"""
        cleaned_content = self._clean_pdf_content(content)
        
        # Enhanced patterns for academic content with novelty focus
        academic_patterns = [
            # Core academic sections
            r'(?:^|\n)\s*(?:abstract|要約|概要)[\s:：]*(.{100,2000}?)(?=\n\s*(?:introduction|introduction|keywords|背景|目的|研究目的)|\n\s*[1-9]\.|$)',
            r'(?:^|\n)\s*(?:introduction|はじめに|序論|背景)[\s:：]*(.{200,3000}?)(?=\n\s*(?:related work|先行研究|手法|methodology|実験)|\n\s*[2-9]\.|$)',
            r'(?:^|\n)\s*(?:methodology|手法|提案手法|アプローチ|method)[\s:：]*(.{200,3000}?)(?=\n\s*(?:experiment|実験|結果|evaluation|評価)|\n\s*[3-9]\.|$)',
            r'(?:^|\n)\s*(?:contribution|貢献|新規性|novelty|innovation|main contributions)[\s:：]*(.{100,2000}?)(?=\n\s*(?:experiment|実験|結果|evaluation)|\n\s*[3-9]\.|$)',
            r'(?:^|\n)\s*(?:conclusion|結論|まとめ|考察|summary)[\s:：]*(.{100,2000}?)(?=\n\s*(?:reference|参考文献|acknowledgment)|\n\s*[789]\.|$)',
            
            # Technical innovation patterns
            r'(?:^|\n)\s*(?:proposed|we propose|our method|新しい|novel|innovative|新規|提案する)(.{50,1500}?)(?=\n\s*[A-Z]|\n\s*\d+\.|\n\s*[図表]|$)',
            r'(?:^|\n)\s*(?:algorithm|アルゴリズム|approach|手法)\s*\d*[\s:：]*(.{100,1500}?)(?=\n\s*[A-Z]|\n\s*\d+\.|\n\s*[図表]|$)',
            r'(?:^|\n)\s*(?:feature|特徴|advantage|利点|benefit|benefits|key feature)[\s:：]*(.{50,1000}?)(?=\n\s*[A-Z]|\n\s*\d+\.|\n\s*[図表]|$)',
            r'(?:^|\n)\s*(?:difference|違い|improvement|改善|enhancement|強化)[\s:：]*(.{50,1000}?)(?=\n\s*[A-Z]|\n\s*\d+\.|\n\s*[図表]|$)',
            
            # Results and performance patterns
            r'(?:^|\n)\s*(?:result|結果|performance|性能|evaluation|評価|experimental)[\s:：]*(.{100,1500}?)(?=\n\s*[A-Z]|\n\s*\d+\.|\n\s*[図表]|$)',
            r'(?:^|\n)\s*(?:comparison|比較|baseline|従来手法|state-of-the-art)[\s:：]*(.{100,1500}?)(?=\n\s*[A-Z]|\n\s*\d+\.|\n\s*[図表]|$)',
            
            # Technical details patterns
            r'(?:^|\n)\s*(?:implementation|実装|architecture|アーキテクチャ|design|設計|framework)[\s:：]*(.{100,1500}?)(?=\n\s*[A-Z]|\n\s*\d+\.|\n\s*[図表]|$)',
            
            # Mathematical/technical formulations
            r'(?:^|\n)\s*(?:model|モデル|formulation|定式化|equation|式|mathematical)[\s:：]*(.{100,1200}?)(?=\n\s*[A-Z]|\n\s*\d+\.|\n\s*[図表]|$)',
        ]
        
        extracted_sections = []
        
        for pattern in academic_patterns:
            matches = re.finditer(pattern, cleaned_content, re.IGNORECASE | re.DOTALL)
            for match in matches:
                section_text = match.group(1).strip()
                if len(section_text) > 50:  # Minimum meaningful length
                    # Clean and validate the section
                    clean_match = re.sub(r'\s+', ' ', section_text).strip()
                    
                    # Skip if too much metadata/junk
                    if (len(clean_match) > 100 and 
                        'endobj' not in clean_match[:50] and
                        'obj' not in clean_match[:50] and
                        'stream' not in clean_match[:50] and
                        len(clean_match.split()) > 10):  # Ensure enough words
                        extracted_sections.append(clean_match[:1200])  # Increased section size

        if extracted_sections:
            # Join sections and allow larger content for comprehensive analysis
            combined = "\n\n".join(extracted_sections)
            result = combined[:3000] if len(combined) > 3000 else combined  # Increased limit for technical detail
            logger.info(f"📋 Extracted {len(extracted_sections)} academic sections with novelty focus ({len(result)} chars)")
            return result
        else:
            # Enhanced fallback: Find technical content, skip metadata
            logger.warning("⚠️ No structured academic sections found, using technical content extraction")
            return self._extract_technical_content(cleaned_content)

    def _extract_key_sections(self, content: str) -> str:
        """Extract key sections from technical content with enhanced pattern matching"""
        
        # Clean content first: remove PDF metadata and artifacts
        cleaned_content = self._clean_pdf_content(content)
        
        # Look for common technical document patterns with more aggressive matching
        patterns = [
            # FEATURES section - multiple variations and more flexible
            r'(?:FEATURES|Features|Key Features)[:\s\n]*(.*?)(?:\n\s*(?:APPLICATIONS|SPECIFICATIONS|DESCRIPTION|PIN CONFIGURATION|ORDERING GUIDE|Figure|Table|\d+\s+[A-Z])|$)',
            
            # APPLICATIONS section - multiple variations  
            r'(?:APPLICATIONS|Applications|Typical Applications)[:\s\n]*(.*?)(?:\n\s*(?:FEATURES|SPECIFICATIONS|DESCRIPTION|PIN CONFIGURATION|ORDERING GUIDE|Figure|Table|\d+\s+[A-Z]|GENERAL)|$)',
            
            # GENERAL DESCRIPTION section (common in datasheets)
            r'(?:GENERAL DESCRIPTION|General Description)[:\s\n]*(.*?)(?:\n\s*(?:FEATURES|APPLICATIONS|SPECIFICATIONS|PIN CONFIGURATION|ORDERING GUIDE|Figure|Table|\d+\s+[A-Z])|$)',
            
            # SPECIFICATIONS/CHARACTERISTICS section
            r'(?:SPECIFICATIONS|Specifications|ELECTRICAL CHARACTERISTICS|Electrical Characteristics)[:\s\n]*(.*?)(?:\n\s*(?:FEATURES|APPLICATIONS|DESCRIPTION|PIN CONFIGURATION|ORDERING GUIDE|Figure|Table|\d+\s+[A-Z])|$)',
            
            # OVERVIEW/DESCRIPTION section
            r'(?:OVERVIEW|Overview|DESCRIPTION|Description)[:\s\n]*(.*?)(?:\n\s*(?:FEATURES|APPLICATIONS|SPECIFICATIONS|PIN CONFIGURATION|ORDERING GUIDE|Figure|Table|\d+\s+[A-Z])|$)',
        ]
        
        extracted_sections = []
        for pattern in patterns:
            matches = re.findall(pattern, cleaned_content, re.IGNORECASE | re.DOTALL)
            if matches:
                for match in matches[:1]:  # Take first match per pattern
                    clean_match = match.strip()
                    # Filter out PDF artifacts and ensure meaningful content
                    if (clean_match and 
                        len(clean_match) > 30 and 
                        not clean_match.startswith('%') and
                        'obj' not in clean_match[:50] and
                        'stream' not in clean_match[:50]):
                        extracted_sections.append(clean_match[:1000])  # Limit section size

        if extracted_sections:
            # Join sections and limit to reasonable length for LLM processing
            combined = "\n\n".join(extracted_sections)
            result = combined[:1800] if len(combined) > 1800 else combined  # Stay under token limit
            logger.info(f"📋 Extracted {len(extracted_sections)} structured sections ({len(result)} chars)")
            return result
        else:
            # Enhanced fallback: Find technical content, skip metadata
            logger.warning("⚠️ No structured sections found, using technical content extraction")
            return self._extract_technical_content(cleaned_content)
    
    def _clean_pdf_content(self, content: str) -> str:
        """Clean PDF content by removing metadata and artifacts with aggressive filtering"""
        if not content:
            return content
        
        # Aggressive PDF metadata and artifact removal
        metadata_patterns = [
            r'%PDF-[\d\.]+.*?\n',
            r'rdf:about=.*?\n',
            r'xmlns:.*?=.*?\n',
            r'<\?xml.*?\?>',
            r'adobe\.com.*?\n',
            r'\d+ \d+ obj\s*<<.*?endobj',  # Complete PDF objects
            r'<<[^>]*?>>',  # PDF dictionary objects
            r'stream\s+.*?endstream',  # PDF streams
            r'xref\s+.*?\n',
            r'trailer\s+.*?\n',
            r'startxref\s+.*?\n',
            r'%%EOF.*?\n',
            r'/Type\s*/.*?\n',
            r'/Filter\s*/.*?\n',
            r'/Length\s*\d+.*?\n',
            r'/E\s+\d+',  # PDF linearization info
            r'/H\s+\[.*?\]',
            r'/L\s+\d+',
            r'/線形化\d+',  # Japanese PDF metadata
            r'/n\s+\d+',
            r'/o\s+\d+',
            r'/T\s+\d+',
            r'％[ùúçâãïó]+',  # PDF binary markers
            r'endobj\s*',
            r'obj\s*',
            r'<</.*?>>',
        ]
        
        cleaned = content
        for pattern in metadata_patterns:
            cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove binary and control characters more aggressively
        cleaned = re.sub(r'[^\x20-\x7E\s\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', ' ', cleaned)
        
        # Remove hex patterns and object references
        cleaned = re.sub(r'\b[0-9a-fA-F]{8,}\b', ' ', cleaned)
        cleaned = re.sub(r'\b\d{5,}\s+00000\s+n\b', ' ', cleaned)
        cleaned = re.sub(r'hÞ[^\s]*', ' ', cleaned)
        
        # Remove excessive whitespace and cleanup
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
        
        # If result is too short or still mostly metadata, try fallback extraction
        if len(cleaned.strip()) < 100 or cleaned.count('obj') > 5 or cleaned.count('endobj') > 3:
            # Try to find actual text content by looking for readable sentences
            lines = content.split('\n')
            readable_lines = []
            for line in lines:
                line = line.strip()
                if (len(line) > 20 and 
                    not line.startswith('%') and
                    'obj' not in line and
                    'endobj' not in line and
                    'stream' not in line and
                    not re.match(r'^[0-9\s<>/]+$', line) and
                    re.search(r'[a-zA-Z]{3,}', line)):  # Contains actual words
                    readable_lines.append(line)
            
            if readable_lines:
                cleaned = '\n'.join(readable_lines[:50])  # Take first 50 readable lines
        
        return cleaned.strip()
    
    def _extract_readable_pdf_content(self, pdf_content: str) -> str:
        """Extract only readable content from PDF, ignoring all metadata and structures"""
        if not pdf_content:
            return pdf_content
            
        # Split into lines and filter for readable content
        lines = pdf_content.split('\n')
        readable_lines = []
        
        for line in lines:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
                
            # Skip PDF structural elements
            if (line.startswith('%') or 
                line.startswith('<<') or 
                line.startswith('>>') or
                line.startswith('/') or
                'obj' in line[:10] or
                'endobj' in line or
                'stream' in line[:10] or
                'endstream' in line or
                'xref' in line[:10] or
                'trailer' in line[:10] or
                line.startswith('startxref') or
                line.startswith('%%')):
                continue
                
            # Skip lines that are mostly numbers/IDs
            if re.match(r'^[\d\s<>/\[\]]+$', line):
                continue
                
            # Skip binary-looking content
            if re.search(r'[^\x20-\x7E\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FAF]', line):
                continue
                
            # Must contain actual words (3+ letter sequences)
            if not re.search(r'[a-zA-Z]{3,}', line):
                continue
                
            # Skip lines that are mostly hex or special chars
            special_char_ratio = len(re.findall(r'[^a-zA-Z0-9\s\.\,\-\(\)]', line)) / max(len(line), 1)
            if special_char_ratio > 0.3:
                continue
                
            readable_lines.append(line)
            
        # Join readable lines and do final cleanup
        readable_text = '\n'.join(readable_lines)
        
        # Additional cleanup
        readable_text = re.sub(r'\s+', ' ', readable_text)
        readable_text = re.sub(r'\n\s*\n', '\n', readable_text)
        
        return readable_text.strip()
    
    def _extract_technical_content(self, content: str) -> str:
        """Extract meaningful technical content, avoiding metadata with enhanced filtering"""
        
        # Split into paragraphs
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        if not paragraphs:
            paragraphs = [p.strip() for p in content.split('\n') if p.strip()]

        if not paragraphs:
            return content[:800] + "..." if len(content) > 800 else content

        # Score paragraphs based on technical content with enhanced filtering
        scored_paragraphs = []
        
        for paragraph in paragraphs:
            # Skip PDF artifacts aggressively
            if (paragraph.startswith('%') or 
                'obj' in paragraph[:50] or 
                'stream' in paragraph[:50] or
                'endobj' in paragraph[:50] or
                'endstream' in paragraph[:50] or
                paragraph.startswith('<') or
                len(paragraph.split()) < 5):  # Skip very short paragraphs
                continue
            
            score = 1  # Base score for all paragraphs
            word_count = len(paragraph.split())
            
            # Give longer paragraphs base points
            if word_count >= 10:
                score += 1
            if word_count >= 20:
                score += 1
            
            # Technical keywords score (enhanced list)
            tech_keywords = [
                'voltage', 'current', 'frequency', 'temperature', 'measurement',
                'specification', 'precision', 'accuracy', 'resolution', 'datasheet',
                'features', 'applications', 'performance', 'characteristics',
                'analog', 'digital', 'output', 'input', 'range', 'power',
                'circuit', 'device', 'system', 'signal', 'channel', 'pin',
                'compliance', 'isolation', 'reference', 'converter', 'amplifier'
            ]
            
            for keyword in tech_keywords:
                if keyword.lower() in paragraph.lower():
                    score += 3  # More weight for technical keywords
            
            # Prefer Feature sections and specifications
            feature_indicators = ['features', 'specifications', 'description', 'overview', 'applications']
            for indicator in feature_indicators:
                if indicator.lower() in paragraph.lower()[:100]:  # Check beginning of paragraph
                    score += 5
            
            # Penalize revision history and administrative content more heavily
            admin_patterns = ['revision history', 'changes to', 'page', 'document feedback', 'analog devices', 'pdf', 'metadata']
            for pattern in admin_patterns:
                if pattern.lower() in paragraph.lower():
                    score -= 15  # Heavy penalty for administrative content
            
            # Prefer paragraphs with numbers (specifications)
            if re.search(r'\d+(\.\d+)?', paragraph):
                score += 2
            
            # Prefer paragraphs with units
            units = ['V', 'A', 'Hz', 'MHz', 'GHz', 'kHz', 'Ω', '°C', 'mA', 'μA', 'ppm', 'mV', 'kV']
            for unit in units:
                if unit in paragraph:
                    score += 2
            
            # Prefer paragraphs that look like feature lists
            if '•' in paragraph or paragraph.strip().startswith('•'):
                score += 2
            
            # Penalize very long paragraphs (likely corrupted) more heavily
            if word_count > 300:
                score -= 10  # Heavy penalty for very long paragraphs
                score -= 3
            
            scored_paragraphs.append((score, paragraph))
        
        # Sort by score and take the best paragraphs
        scored_paragraphs.sort(key=lambda x: x[0], reverse=True)
        
        # Take top paragraphs up to ~1500 characters
        result = ""
        for score, paragraph in scored_paragraphs[:8]:  # Increased from 5 to 8
            # Check if adding this paragraph would exceed our limit
            potential_length = len(result + paragraph) + 1  # +1 for newline
            if potential_length > 1500 and result:  # If we already have some content, stop
                break
            elif not result:  # Always take at least one paragraph
                result = paragraph[:1200]  # Truncate if too long
                break
            else:
                result += paragraph + "\n"
        
        # If no good content found, take the beginning (after cleaning)
        if not result.strip() or len(result.strip()) < 100:
            # Try to find the first substantial paragraph
            for paragraph in paragraphs[:10]:
                if len(paragraph) > 50:
                    result = paragraph[:800]
                    break
            
            if not result:
                result = content[:800] + "..." if len(content) > 800 else content
        
        return result.strip()

    def _send_email_notification_if_configured(self, file_path: str, result: str):
        """Send email notification if email settings are configured"""
        try:
            import os
            from src.utils.email_sender import send_processing_notification
            
            # Check if email is configured
            recipient_email = os.getenv("NOTIFICATION_EMAIL")
            sender_email = os.getenv("EMAIL_SENDER")
            sender_password = os.getenv("EMAIL_PASSWORD")
            
            if recipient_email and sender_email and sender_password:
                logger.info(f"📧 Sending email notification to {recipient_email}")
                
                # Extract metrics from result for email
                processing_metrics = self._extract_metrics_from_result(result)
                
                # Extract summary content (first part of result if it's a tuple)
                summary_content = result[0] if isinstance(result, tuple) else result
                
                # Send email notification with processing results
                send_processing_notification(
                    recipient_email=recipient_email,
                    file_path=Path(file_path),
                    summary_content=summary_content,
                    processing_metrics=processing_metrics,
                    sender_email=sender_email,
                    sender_password=sender_password
                )
                
                logger.success(f"✅ Email notification sent successfully to {recipient_email}")
            else:
                logger.info("📧 Email notification not configured - skipping")
                
        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {e}")

    def _extract_metrics_from_result(self, result) -> dict:
        """Extract processing metrics from result for email notification"""
        try:
            if isinstance(result, tuple) and len(result) >= 2:
                summary_content = result[0]
                translation_content = result[1]
                
                return {
                    "summary_length": len(summary_content),
                    "translation_length": len(translation_content),
                    "summary_words": len(summary_content.split()),
                    "translation_words": len(translation_content.split()),
                    "processing_status": "Success",
                    "technical_analysis": "Enhanced Academic Processing with Technical Novelty Detection"
                }
            else:
                content = str(result)
                return {
                    "output_length": len(content),
                    "output_words": len(content.split()),
                    "processing_status": "Success",
                    "technical_analysis": "Enhanced Academic Processing with Technical Novelty Detection"
                }
        except Exception as e:
            logger.warning(f"⚠️ Could not extract metrics: {e}")
            return {"processing_status": "Success", "note": "Metrics extraction failed"}


def create_enhanced_academic_processing_function():
    """
    Create an enhanced academic processing function with LLM + Google Translate
    
    Returns:
        Processing function for batch processor
    """
    processor = EnhancedAcademicProcessor()
    
    def _extract_readable_pdf_content(content: str) -> str:
        """
        Extract readable content from PDF text by filtering out metadata and artifacts
        """
        if not content:
            return ""
        
        lines = content.split('\n')
        readable_lines = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Skip lines that are mostly PDF metadata or artifacts
            if any(pattern in line.lower() for pattern in [
                'rdf:about', 'xmlns:', 'pdf:', 'xmp:', 'producer', 'creator', 
                'moddate', 'creationdate', 'metadata', 'xmpmeta',
                'rdf:rdf', 'x:xmpmeta', 'adobe:ns:meta'
            ]):
                continue
                
            # Check if line has reasonable word/character ratio (readable text)
            words = line.split()
            if len(words) >= 2 and len(line) > 10:
                # Calculate ratio of alphabetic characters
                alpha_chars = sum(1 for c in line if c.isalpha())
                if alpha_chars / len(line) > 0.5:  # At least 50% alphabetic
                    readable_lines.append(line)
        
        return '\n'.join(readable_lines)

    def _send_email_notification_if_configured(self, file_path: str, result: str):
        """Send email notification if email settings are configured"""
        try:
            import os
            from src.utils.email_sender import send_processing_notification
            
            # Check if email is configured
            recipient_email = os.getenv("NOTIFICATION_EMAIL")
            sender_email = os.getenv("EMAIL_SENDER")
            sender_password = os.getenv("EMAIL_PASSWORD")
            
            if recipient_email and sender_email and sender_password:
                logger.info(f"📧 Sending email notification to {recipient_email}")
                
                # Extract metrics from result for email
                processing_metrics = self._extract_metrics_from_result(result)
                
                # Extract summary content (first part of result if it's a tuple)
                summary_content = result[0] if isinstance(result, tuple) else result
                
                # Send email notification with processing results
                send_processing_notification(
                    recipient_email=recipient_email,
                    file_path=Path(file_path),
                    summary_content=summary_content,
                    processing_metrics=processing_metrics,
                    sender_email=sender_email,
                    sender_password=sender_password
                )
                
                logger.success(f"✅ Email notification sent successfully to {recipient_email}")
            else:
                logger.info("📧 Email notification not configured - skipping")
                
        except Exception as e:
            logger.error(f"❌ Failed to send email notification: {e}")

    def _extract_metrics_from_result(self, result) -> dict:
        """Extract processing metrics from result for email notification"""
        try:
            if isinstance(result, tuple) and len(result) >= 2:
                summary = result[0]
                original = result[1]
                
                return {
                    "input_length": len(original),
                    "output_length": len(summary),
                    "input_words": len(original.split()),
                    "output_words": len(summary.split()),
                    "compression_ratio": f"{(len(summary) / len(original) * 100):.1f}%",
                    "processing_status": "Success",
                    "technical_analysis": "Enhanced Academic Processing with Technical Novelty Detection"
                }
            else:
                content = result if isinstance(result, str) else str(result)
                return {
                    "output_length": len(content),
                    "output_words": len(content.split()),
                    "processing_status": "Success",
                    "technical_analysis": "Enhanced Academic Processing with Technical Novelty Detection"
                }
        except Exception as e:
            logger.warning(f"⚠️ Could not extract metrics: {e}")
            return {"processing_status": "Success", "note": "Metrics extraction failed"}

    def process_with_enhanced_academic(file_path: Path, **kwargs) -> str:
        """
        Process file with enhanced academic processing:
        1. LLM-based summarization (if available)
        2. Google Translate for translation
        3. Comprehensive result formatting
        """
        start_time = time.time()
        
        try:
            # Read file content
            try:
                # For PDF files, use DocumentProcessor for proper extraction
                if file_path.suffix.lower() == '.pdf':
                    from src.document_processor import DocumentProcessor
                    doc_processor = DocumentProcessor()
                    content = doc_processor.process(str(file_path))
                    
                    # Apply specialized PDF content extraction
                    readable_content = _extract_readable_pdf_content(content)
                    if len(readable_content.strip()) > 100:
                        content = readable_content
                        logger.info(f"📄 Extracted readable PDF content: {len(content)} characters")
                        
                        # Large PDFs will be handled by automatic chunking in create_llm_summary
                        if len(content) > 20000:
                            logger.info(f"� Large PDF detected ({len(content)} chars), will use chunk processing")
                else:
                    # For JSON files, use DocumentProcessor for URL extraction and processing
                    if file_path.suffix.lower() == '.json':
                        from src.document_processor import DocumentProcessor
                        doc_processor = DocumentProcessor()
                        content = doc_processor.process_file(str(file_path))
                        logger.info(f"🔗 JSON file processed with URL extraction: {len(content)} characters")
                    else:
                        # For text files, read directly
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
            except UnicodeDecodeError:
                # Try with different encoding
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            
            if not content.strip():
                return _create_error_result(file_path, "ファイル内容が空です")
            
            logger.info(f"📄 Processing: {file_path.name} ({len(content)} characters)")
            
            # Step 1: Create LLM-based summary (English)
            english_summary = processor.create_llm_summary(content)
            logger.info(f"📝 English summary created ({len(english_summary)} characters)")
            
            # Step 2: Translate summary to Japanese
            japanese_summary = processor.translate_text(english_summary, 'ja', 'en')
            logger.info(f"🌐 Translated to Japanese ({len(japanese_summary)} characters)")
            
            # Verify translation actually occurred (if same, try again with googletrans)
            if japanese_summary == english_summary or len(japanese_summary) < 10:
                try:
                    from googletrans import Translator
                    translator = Translator()
                    result = translator.translate(english_summary, dest='ja', src='en')
                    japanese_summary = result.text if result.text else japanese_summary
                    logger.info(f"🔄 Used googletrans fallback for translation")
                except Exception as e:
                    logger.warning(f"Googletrans fallback failed: {e}")
            
            # Step 3: Translate full content (no truncation for comprehensive translation)
            japanese_translation = processor.translate_text(content, 'ja', 'en')
            
            processing_time = time.time() - start_time
            
            # Create comprehensive result
            result = _create_enhanced_result(
                file_path=file_path,
                original_content=content,
                english_summary=english_summary,
                japanese_summary=japanese_summary,
                japanese_translation=japanese_translation,
                processing_time=processing_time,
                llm_used=processor.llm_summarizer is not None
            )
            
            logger.success(f"✅ Enhanced processing completed: {file_path.name} ({processing_time:.2f}s)")
            
            # Optional: Send email notification if configured
            try:
                # Use processor instance to call email notification method
                if hasattr(processor, '_send_email_notification_if_configured'):
                    processor._send_email_notification_if_configured(str(file_path), result)
                else:
                    logger.debug("📧 Email notification method not available on processor")
            except Exception as email_error:
                logger.warning(f"⚠️ Failed to send email notification: {email_error}")
            
            return result
                
        except Exception as e:
            return _create_error_result(file_path, f"処理エラー: {str(e)}")
    
    return process_with_enhanced_academic


def _create_enhanced_result(file_path: Path, original_content: str, 
                          english_summary: str, japanese_summary: str,
                          japanese_translation: str, processing_time: float,
                          llm_used: bool) -> str:
    """Create comprehensive enhanced academic result"""
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    processing_method = "🤖 LLM + Google Translate" if llm_used else "📝 Basic + Google Translate"
    
    result = f"""
==================================================
🎓 ENHANCED ACADEMIC PROCESSING RESULTS
==================================================

📁 File: {file_path.name}
📅 Processed: {timestamp}
🔧 Method: {processing_method}
⏱️ Processing Time: {processing_time:.2f} seconds
📊 Original Length: {len(original_content):,} characters

==================================================
📝 ENGLISH SUMMARY (LLM-Generated)
==================================================

{english_summary}

==================================================
📝 日本語要約 (Japanese Summary)
==================================================

{japanese_summary}

==================================================
🌐 日本語翻訳 (Japanese Translation)
==================================================

{japanese_translation}

==================================================
📊 PROCESSING METRICS
==================================================

• Original Text: {len(original_content):,} characters
• English Summary: {len(english_summary):,} characters  
• Japanese Summary: {len(japanese_summary):,} characters
• Translation: {len(japanese_translation):,} characters
• Compression Ratio: {(len(english_summary) / len(original_content) * 100):.1f}%
• LLM Used: {'Yes' if llm_used else 'No (Fallback)'}

==================================================
"""
    return result


def _create_error_result(file_path: Path, error_message: str) -> str:
    """Create error result for failed processing"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    return f"""
==================================================
❌ ENHANCED ACADEMIC PROCESSING ERROR
==================================================

📁 File: {file_path.name}
📅 Processed: {timestamp}
❌ Error: {error_message}

Please check the file format and content.
==================================================
"""


# For compatibility with existing code
def create_google_translate_processing_function():
    """Alias for backward compatibility"""
    return create_enhanced_academic_processing_function()


if __name__ == "__main__":
    # Test the enhanced academic processor
    processor = EnhancedAcademicProcessor()
    test_text = "This is a technical document about advanced neural networks and machine learning algorithms. The research focuses on improving efficiency and accuracy in deep learning models."
    
    print("Testing Enhanced Academic Processor...")
    print("=" * 50)
    
    # Test summarization
    summary = processor.create_llm_summary(test_text)
    print(f"Summary: {summary}")
    
    # Test translation
    translation = processor.translate_text(summary, 'ja', 'en')
    print(f"Translation: {translation}")
