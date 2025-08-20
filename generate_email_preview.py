"""
Generate HTML preview of enhanced email content
"""

from src.utils.email_sender import EnhancedEmailSender
from pathlib import Path
import os
from dotenv import load_dotenv

def generate_email_preview():
    # Load environment variables
    load_dotenv()
    
    # Read the enhanced summary file
    summary_file = Path('output/batch_gui/processed/2508.10856v1_summary_ja.md')
    if summary_file.exists():
        with open(summary_file, 'r', encoding='utf-8') as f:
            enhanced_content = f.read()
        
        print(f"✅ Loaded content: {len(enhanced_content)} characters")
        
        # Create enhanced email sender
        sender = EnhancedEmailSender()
        
        # Parse the content
        parsed = sender._parse_summary_content(enhanced_content)
        
        # Test metrics
        test_metrics = {
            'processing_time': '479.00 seconds',
            'original_length': '43,353 characters',
            'summary_length': '4,420 characters',
            'compression_ratio': '10.2%'
        }
        
        # Generate HTML content
        html_content = sender._create_html_content(
            Path('test_data_technical/2508.10856v1.pdf'),
            parsed,
            test_metrics
        )
        
        # Save HTML preview
        preview_file = Path('output/email_preview.html')
        preview_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(preview_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"📧 HTML email preview saved to: {preview_file}")
        print("🔍 Parsed sections:")
        print(f"   📝 English Summary: {len(parsed['english_summary'])} chars")
        print(f"   🌸 Japanese Summary: {len(parsed['japanese_summary'])} chars") 
        print(f"   🌐 Translation: {len(parsed['translation'])} chars")
        
        return str(preview_file)
    else:
        print(f"❌ Summary file not found: {summary_file}")
        return None

if __name__ == "__main__":
    preview_path = generate_email_preview()
    if preview_path:
        print(f"\n✨ You can open the preview file to see how the email will look:")
        print(f"   {preview_path}")
