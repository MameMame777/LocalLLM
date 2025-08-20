"""Main entry point for the Local LLM Summarizer."""

import click
from pathlib import Path
from loguru import logger
import sys
from typing import Optional

from config.settings import get_settings, ensure_directories
from src.document_processor import DocumentProcessor
from .summarizer_enhanced import LLMSummarizer
from src.utils.logger import setup_logging


@click.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output file path')
@click.option('--format', '-f', 
              type=click.Choice(['txt', 'markdown', 'json']), 
              default='markdown',
              help='Output format')
@click.option('--model', '-m', type=click.Path(exists=True), 
              help='Path to LLM model file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def main(input_path: str, output: Optional[str], format: str, 
         model: Optional[str], verbose: bool) -> None:
    """
    Summarize PDF or HTML documents using a local LLM.
    
    INPUT_PATH: Path to the document file (PDF, HTML) or URL
    """
    # Setup
    settings = get_settings()
    ensure_directories()
    setup_logging(verbose)
    
    logger.info(f"Starting document summarization: {input_path}")
    
    try:
        # Initialize components
        processor = DocumentProcessor()
        summarizer = LLMSummarizer(
            model_path=model or settings.default_model_path,
            settings=settings
        )
        
        # Process document
        logger.info("Extracting text from document...")
        text_content = processor.process(input_path)
        
        if not text_content.strip():
            logger.error("No text content extracted from document")
            sys.exit(1)
        
        logger.info(f"Extracted {len(text_content)} characters")
        
        # Generate summary
        logger.info("Generating summary...")
        summary = summarizer.summarize(text_content)
        
        # Save output
        if output:
            output_path = Path(output)
        else:
            input_stem = Path(input_path).stem
            output_path = Path(settings.output_directory) / f"{input_stem}_summary.{format}"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == 'json':
            import json
            output_data = {
                "source": str(input_path),
                "summary": summary,
                "metadata": {
                    "input_length": len(text_content),
                    "summary_length": len(summary)
                }
            }
            output_path.write_text(json.dumps(output_data, indent=2, ensure_ascii=False))
        else:
            output_path.write_text(summary, encoding='utf-8')
        
        logger.success(f"Summary saved to: {output_path}")
        
        # Print summary to console if verbose
        if verbose:
            click.echo("\n" + "="*50)
            click.echo("SUMMARY:")
            click.echo("="*50)
            click.echo(summary)
            click.echo("="*50)
    
    except Exception as e:
        logger.error(f"Error during processing: {e}")
        if verbose:
            logger.exception("Detailed error information:")
        sys.exit(1)


if __name__ == "__main__":
    main()
