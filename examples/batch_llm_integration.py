#!/usr/bin/env python3
"""
Integration Example: Batch Processing with LocalLLM Summarizer
Demonstrates how to integrate the batch processing system with the actual summarizer
"""

import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from batch_processing.batch_processor import BatchProcessor
from summarizer_enhanced import EnhancedSummarizer
from document_processor import DocumentProcessor


def create_llm_processing_function(language="ja", max_length=200):
    """
    Create a processing function that uses the actual LocalLLM summarizer.
    
    Args:
        language: Target language for summaries ("ja", "en", etc.)
        max_length: Maximum length of summaries in words
        
    Returns:
        Processing function for batch processor
    """
    # Initialize the summarizer and document processor
    summarizer = EnhancedSummarizer()
    doc_processor = DocumentProcessor()
    
    def process_file_with_llm(file_path: Path, **kwargs) -> str:
        """
        Process a single file using LocalLLM.
        
        Args:
            file_path: Path to the file to process
            **kwargs: Additional parameters
            
        Returns:
            Summary result as string
        """
        try:
            # Extract text content from file
            if file_path.suffix.lower() == '.pdf':
                content = doc_processor.extract_pdf_text(str(file_path))
            elif file_path.suffix.lower() in ['.html', '.htm']:
                content = doc_processor.extract_html_text(str(file_path))
            else:
                # For plain text files
                content = file_path.read_text(encoding='utf-8')
            
            if not content.strip():
                return f"Warning: No content extracted from {file_path.name}"
            
            # Generate summary using LLM
            summary_result = summarizer.generate_summary(
                content=content,
                target_language=language,
                max_length=max_length,
                input_language="auto",  # Auto-detect input language
                style="balanced"
            )
            
            # Extract summary text from result
            if isinstance(summary_result, dict):
                summary_text = summary_result.get('summary', str(summary_result))
            else:
                summary_text = str(summary_result)
            
            # Save individual summary file
            output_dir = Path("output/batch_summaries")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            summary_file = output_dir / f"{file_path.stem}_summary_{timestamp}.md"
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(f"# Summary: {file_path.name}\n\n")
                f.write(f"**Original File:** {file_path}\n")
                f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"**Language:** {language}\n")
                f.write(f"**Content Length:** {len(content)} characters\n\n")
                f.write("## Summary\n\n")
                f.write(summary_text)
            
            return f"Summary generated: {len(summary_text)} characters -> {summary_file.name}"
            
        except Exception as e:
            raise Exception(f"Failed to process {file_path.name}: {str(e)}")
    
    return process_file_with_llm


def run_batch_summarization():
    """Run batch summarization on the data directory."""
    print("🤖 LocalLLM Batch Summarization System")
    print("=" * 60)
    
    # Initialize batch processor
    processor = BatchProcessor(
        max_workers=2,  # Limit workers for LLM processing
        use_multiprocessing=False,  # Use threading for LLM compatibility
        output_directory=Path("output/batch_llm")
    )
    
    # Create LLM processing function
    llm_function = create_llm_processing_function(
        language="ja",  # Japanese summaries
        max_length=150  # Moderate length summaries
    )
    
    # Process data directory
    data_dir = Path("data")
    if not data_dir.exists():
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    print(f"🎯 Processing directory: {data_dir}")
    print("🤖 Using LocalLLM for actual summarization")
    
    # Run batch processing
    results = processor.process_directory(
        directory=data_dir,
        processing_function=llm_function,
        parameters={
            "language": "ja",
            "max_length": 150,
            "mode": "production"
        },
        file_extensions=[".pdf", ".html", ".txt"]  # Process these types
    )
    
    # Print results
    print(f"\n🎉 Batch summarization completed!")
    print(f"📊 Status: {results['status']}")
    if results['status'] == 'completed':
        print(f"✅ Successful files: {results['successful_files']}")
        print(f"❌ Failed files: {results['failed_files']}")
        print(f"📈 Success rate: {results['success_rate']:.1f}%")
        print(f"⏱️ Processing time: {results['processing_time']}")
        
        print(f"\n📁 Generated reports:")
        for format_name, file_path in results['report_files'].items():
            print(f"   📄 {format_name}: {file_path}")
        
        print(f"\n💡 Individual summaries saved in: output/batch_summaries/")


def main():
    """Main function for LLM batch processing."""
    try:
        run_batch_summarization()
    except KeyboardInterrupt:
        print("\n🛑 Processing interrupted by user")
    except Exception as e:
        print(f"💥 Error: {e}")


if __name__ == "__main__":
    main()
