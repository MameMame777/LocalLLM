"""Document processing module for PDF and HTML files."""

from pathlib import Path
from typing import Union, Optional
import re
from urllib.parse import urlparse
from loguru import logger

# PDF processing
import PyPDF2
from pdfminer.high_level import extract_text as pdfminer_extract_text

# HTML processing
import requests
from bs4 import BeautifulSoup
import html2text

from config.settings import get_settings


class DocumentProcessor:
    """Process various document formats and extract text content."""
    
    def __init__(self):
        self.settings = get_settings()
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = True
        self.html_converter.ignore_images = True
    
    def process(self, input_path: str) -> str:
        """
        Process a document and extract text content.
        
        Args:
            input_path: Path to file or URL
            
        Returns:
            Extracted text content
        """
        # Determine input type
        if self._is_url(input_path):
            return self._process_url(input_path)
        
        path = Path(input_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {input_path}")
        
        # Process based on file extension
        extension = path.suffix.lower()
        
        if extension == '.pdf':
            return self._process_pdf(path)
        elif extension in ['.html', '.htm']:
            return self._process_html_file(path)
        elif extension == '.json':
            return self._process_json_file(path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    def _is_url(self, input_path: str) -> bool:
        """Check if input is a URL."""
        try:
            result = urlparse(input_path)
            return all([result.scheme, result.netloc])
        except Exception:
            return False
    
    def _process_pdf(self, file_path: Path) -> str:
        """Extract text from PDF file."""
        logger.info(f"Processing PDF: {file_path}")
        
        text_content = ""
        
        try:
            # Try PyPDF2 first (faster)
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content += page_text + "\n"
                    logger.debug(f"Processed page {page_num + 1}")
            
            # If PyPDF2 didn't extract much text, try pdfminer
            if len(text_content.strip()) < 100:
                logger.info("PyPDF2 extracted minimal text, trying pdfminer...")
                text_content = pdfminer_extract_text(str(file_path))
        
        except Exception as e:
            logger.warning(f"Error with PyPDF2, trying pdfminer: {e}")
            try:
                text_content = pdfminer_extract_text(str(file_path))
            except Exception as e2:
                raise Exception(f"Failed to extract PDF text: {e2}")
        
        return self._clean_text(text_content)
    
    def _process_html_file(self, file_path: Path) -> str:
        """Extract text from HTML file."""
        logger.info(f"Processing HTML file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                html_content = file.read()
            return self._extract_html_text(html_content)
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(file_path, 'r', encoding=encoding) as file:
                        html_content = file.read()
                    return self._extract_html_text(html_content)
                except UnicodeDecodeError:
                    continue
            raise Exception(f"Could not decode HTML file: {file_path}")
    
    def _process_url(self, url: str) -> str:
        """Extract text from web page."""
        logger.info(f"Processing URL: {url}")
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            return self._extract_html_text(response.text)
        
        except requests.RequestException as e:
            raise Exception(f"Failed to fetch URL {url}: {e}")
    
    def _extract_html_text(self, html_content: str) -> str:
        """Extract clean text from HTML content."""
        try:
            # Parse HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "aside"]):
                script.decompose()
            
            # Get text using html2text for better formatting
            text = self.html_converter.handle(str(soup))
            
            return self._clean_text(text)
        
        except Exception as e:
            logger.warning(f"Error parsing HTML with BeautifulSoup: {e}")
            # Fallback: simple text extraction
            return self._clean_text(html_content)
    
    def _process_json_file(self, file_path: Path) -> str:
        """Extract and process URLs from JSON file with individual summarization."""
        logger.info(f"Processing JSON file: {file_path}")
        
        try:
            # Import individual JSON URL processor
            from src.utils.individual_json_processor import IndividualJSONUrlProcessor
            
            processor = IndividualJSONUrlProcessor()
            
            # Process JSON file with individual URL summarization
            result_data = processor.process_json_file_individually(file_path)
            
            # Return the integrated summary containing individual summaries
            integrated_content = result_data['integrated_summary']
            
            logger.success(f"✅ JSON processing completed: {result_data['successful_summaries']}/{result_data['total_urls']} URLs individually processed and summarized")
            
            return self._clean_text(integrated_content)
            
        except Exception as e:
            logger.error(f"❌ Error processing JSON file: {e}")
            # Fallback: read JSON as plain text
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    json_content = f.read()
                logger.warning("⚠️ Falling back to plain JSON text processing")
                return self._clean_text(json_content)
            except Exception as e2:
                raise Exception(f"Failed to process JSON file: {e2}")
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize extracted text."""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = re.sub(r'\n\s*\n\s*\n', '\n\n', text)
        text = re.sub(r'[ \t]+', ' ', text)
        
        # Remove common artifacts
        text = re.sub(r'\f', '', text)  # Form feeds
        text = re.sub(r'\r', '', text)  # Carriage returns
        
        # Normalize Unicode
        text = text.strip()
        
        # Limit length
        if len(text) > self.settings.max_input_length:
            logger.warning(f"Text truncated to {self.settings.max_input_length} characters")
            text = text[:self.settings.max_input_length]
        
        return text

    def process_file(self, file_path: Union[str, Path]) -> str:
        """
        Process a file and extract text content.
        Alias for process() method to maintain compatibility.
        
        Args:
            file_path: Path to file
            
        Returns:
            Extracted text content
        """
        return self.process(str(file_path))
