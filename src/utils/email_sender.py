"""
Enhanced email notification system for LocalLLM processing results
"""

import smtplib
import ssl
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate
from pathlib import Path
from typing import Optional, List, Dict, Any
import os
from datetime import datetime
from loguru import logger


class EnhancedEmailSender:
    """Enhanced email sender for LocalLLM processing results with Japanese/English support"""
    
    def __init__(self, smtp_server: str = "smtp.gmail.com", smtp_port: int = 587):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.sender_email = os.getenv("EMAIL_SENDER", "")
        self.sender_password = os.getenv("EMAIL_PASSWORD", "")
        
    def configure_email(self, sender_email: str, sender_password: str):
        """Configure email credentials"""
        self.sender_email = sender_email
        self.sender_password = sender_password
        logger.info(f"📧 Email configured for: {sender_email}")
        
    def send_summary_result(
        self,
        recipient_email: str,
        file_path: Path,
        summary_content: str,
        processing_metrics: Optional[Dict[str, Any]] = None,
        attach_original: bool = False
    ) -> bool:
        """
        Send processing summary via email with enhanced Japanese/English support
        
        Args:
            recipient_email: Recipient email address
            file_path: Path to processed file
            summary_content: Summary content to include in email
            processing_metrics: Processing statistics
            attach_original: Whether to attach the original file
            
        Returns:
            Success status
        """
        try:
            # Parse summary content for Japanese and English parts
            parsed_content = self._parse_summary_content(summary_content)
            
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = f"🤖 LocalLLM処理完了: {file_path.name}"
            message["From"] = self.sender_email
            message["To"] = recipient_email
            
            # Create email content with parsed summary
            html_content = self._create_html_content(
                file_path, parsed_content, processing_metrics
            )
            text_content = self._create_text_content(
                file_path, parsed_content, processing_metrics
            )
            
            # Add parts
            part1 = MIMEText(text_content, "plain", "utf-8")
            part2 = MIMEText(html_content, "html", "utf-8")
            message.attach(part1)
            message.attach(part2)
            
            # Attach summary file if exists
            summary_file = Path(f"output/batch_gui/processed/{file_path.stem}_summary_ja.md")
            if summary_file.exists():
                self._attach_file(message, summary_file)
            
            # Also attach from other common output directories
            for output_dir in ["output", "output/batch_technical_test", "output/real_llm_batch_test"]:
                potential_file = Path(f"{output_dir}/{file_path.stem}_summary_ja.md")
                if potential_file.exists():
                    self._attach_file(message, potential_file)
                    break
                
            # Attach original file if requested and size is reasonable
            if attach_original and file_path.exists() and file_path.stat().st_size < 10 * 1024 * 1024:  # 10MB limit
                self._attach_file(message, file_path)
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.sendmail(self.sender_email, recipient_email, message.as_string())
                
            logger.success(f"📧 Enhanced email sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to send enhanced email: {e}")
            return False
    
    def _parse_summary_content(self, summary_content: str) -> Dict[str, str]:
        """
        Parse summary content to extract Japanese and English parts
        
        Args:
            summary_content: Raw summary content
            
        Returns:
            Dictionary with parsed content sections
        """
        parsed = {
            'english_summary': '',
            'japanese_summary': '',
            'translation': '',
            'full_content': summary_content
        }
        
        try:
            # Split by common section markers
            sections = summary_content.split('==================================================')
            
            for i, section in enumerate(sections):
                section = section.strip()
                if not section:
                    continue
                
                # Check previous section for headers to identify content
                prev_section = ""
                if i > 0:
                    prev_section = sections[i-1].strip()
                
                # Look for English summary content (follows English summary header)
                if prev_section and '📝 ENGLISH SUMMARY' in prev_section:
                    parsed['english_summary'] = section.strip()
                
                # Look for Japanese summary content (follows Japanese summary header)
                elif prev_section and '📝 日本語要約' in prev_section:
                    parsed['japanese_summary'] = section.strip()
                
                # Look for translation content (follows translation header)
                elif prev_section and '🌐 日本語翻訳' in prev_section:
                    parsed['translation'] = section.strip()
            
            # If no structured content found, use the entire content as Japanese summary
            if not parsed['english_summary'] and not parsed['japanese_summary']:
                parsed['japanese_summary'] = summary_content[:1000]  # Limit length
                
        except Exception as e:
            logger.warning(f"⚠️ Failed to parse summary content: {e}")
            parsed['japanese_summary'] = summary_content[:1000]  # Fallback
            
        return parsed
    
    def _create_html_content(self, file_path: Path, parsed_summary: Dict[str, str], metrics: Optional[Dict[str, Any]] = None) -> str:
        """Create HTML email content with parsed summary sections"""
        
        metrics_html = ""
        if metrics:
            metrics_html = f"""
            <div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3 style="color: #495057; margin-top: 0;">📊 処理統計</h3>
                <ul style="color: #6c757d;">
                    <li>処理時間: {metrics.get('processing_time', 'N/A')}</li>
                    <li>元ファイルサイズ: {metrics.get('original_length', 'N/A')} 文字</li>
                    <li>要約長: {metrics.get('summary_length', 'N/A')} 文字</li>
                    <li>圧縮率: {metrics.get('compression_ratio', 'N/A')}</li>
                </ul>
            </div>
            """
        
        # Create summary sections based on available content
        english_section = ""
        if parsed_summary.get('english_summary'):
            english_section = f"""
            <div style="background-color: #e8f4f8; padding: 20px; border-left: 4px solid #17a2b8; margin: 20px 0; border-radius: 5px;">
                <h3 style="color: #0c5460; margin-top: 0;">📝 English Summary</h3>
                <div style="white-space: pre-wrap; word-wrap: break-word; background-color: #ffffff; padding: 15px; border-radius: 5px; border: 1px solid #bee5eb; max-height: 400px; overflow-y: auto;">{parsed_summary['english_summary'][:1500]}{'...' if len(parsed_summary['english_summary']) > 1500 else ''}</div>
            </div>
            """
        
        japanese_section = ""
        if parsed_summary.get('japanese_summary'):
            japanese_section = f"""
            <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #007bff; margin: 20px 0; border-radius: 5px;">
                <h3 style="color: #495057; margin-top: 0;">📝 日本語要約 (Japanese Summary)</h3>
                <div style="white-space: pre-wrap; word-wrap: break-word; background-color: #ffffff; padding: 15px; border-radius: 5px; border: 1px solid #dee2e6; max-height: 400px; overflow-y: auto;">{parsed_summary['japanese_summary'][:1500]}{'...' if len(parsed_summary['japanese_summary']) > 1500 else ''}</div>
            </div>
            """
        
        translation_section = ""
        if parsed_summary.get('translation'):
            translation_section = f"""
            <div style="background-color: #fff3cd; padding: 20px; border-left: 4px solid #ffc107; margin: 20px 0; border-radius: 5px;">
                <h3 style="color: #856404; margin-top: 0;">🌐 完全翻訳 (Full Translation)</h3>
                <div style="white-space: pre-wrap; word-wrap: break-word; background-color: #ffffff; padding: 15px; border-radius: 5px; border: 1px solid #ffeaa7; max-height: 300px; overflow-y: auto;">{parsed_summary['translation'][:2000]}{'...' if len(parsed_summary['translation']) > 2000 else ''}</div>
            </div>
            """
        
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 20px; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
        .content {{ padding: 20px; background-color: #ffffff; }}
        .footer {{ text-align: center; color: #6c757d; margin-top: 30px; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 LocalLLM 処理完了通知</h1>
        <p>ファイル: <strong>{file_path.name}</strong></p>
        <p>処理日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}</p>
    </div>
    
    <div class="content">
        <h2 style="color: #495057;">📄 処理結果</h2>
        <p>ファイル <strong>{file_path.name}</strong> の要約処理が完了しました。</p>
        
        {metrics_html}
        
        {english_section}
        {japanese_section}
        {translation_section}
        
        <p style="color: #6c757d;">
            <strong>注意:</strong> 完全な処理結果は添付ファイルをご確認ください。
        </p>
    </div>
    
    <div class="footer">
        <p>🤖 LocalLLM - ローカルLLM文書処理システム</p>
        <p>このメールは自動送信されています。</p>
    </div>
</body>
</html>"""
        return html
    
    def _create_text_content(self, file_path: Path, parsed_summary: Dict[str, str], metrics: Optional[Dict[str, Any]] = None) -> str:
        """Create plain text email content with parsed summary sections"""
        
        metrics_text = ""
        if metrics:
            metrics_text = f"""
📊 処理統計:
- 処理時間: {metrics.get('processing_time', 'N/A')}
- 元ファイルサイズ: {metrics.get('original_length', 'N/A')} 文字
- 要約長: {metrics.get('summary_length', 'N/A')} 文字
- 圧縮率: {metrics.get('compression_ratio', 'N/A')}
"""
        
        # Build content sections
        content_sections = []
        
        if parsed_summary.get('english_summary'):
            english_text = f"""
📝 English Summary:
{parsed_summary['english_summary'][:800]}{'...' if len(parsed_summary['english_summary']) > 800 else ''}
"""
            content_sections.append(english_text)
        
        if parsed_summary.get('japanese_summary'):
            japanese_text = f"""
📝 日本語要約 (Japanese Summary):
{parsed_summary['japanese_summary'][:800]}{'...' if len(parsed_summary['japanese_summary']) > 800 else ''}
"""
            content_sections.append(japanese_text)
        
        if parsed_summary.get('translation'):
            translation_text = f"""
🌐 完全翻訳 (Full Translation):
{parsed_summary['translation'][:600]}{'...' if len(parsed_summary['translation']) > 600 else ''}
"""
            content_sections.append(translation_text)
        
        content_body = '\n'.join(content_sections) if content_sections else f"📝 処理結果:\n{parsed_summary['full_content'][:1000]}{'...' if len(parsed_summary['full_content']) > 1000 else ''}"
        
        text = f"""🤖 LocalLLM 処理完了通知

ファイル: {file_path.name}
処理日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}

📄 処理結果:
ファイル {file_path.name} の要約処理が完了しました。
{metrics_text}
{content_body}

注意: 完全な要約結果は添付ファイルをご確認ください。

🤖 LocalLLM - ローカルLLM文書処理システム
このメールは自動送信されています。
"""
        return text
    
    def _attach_file(self, message: MIMEMultipart, file_path: Path):
        """Attach file to email"""
        try:
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {file_path.name}'
            )
            message.attach(part)
            logger.info(f"📎 File attached: {file_path.name}")
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to attach file {file_path.name}: {e}")
    
    def test_connection(self) -> bool:
        """Test email configuration"""
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                logger.success("✅ Enhanced email configuration test successful")
                return True
        except Exception as e:
            logger.error(f"❌ Enhanced email configuration test failed: {e}")
            return False
    
    def send_batch_summary_with_attachments(self, recipient_email, file_path, summary_content, processing_metrics=None, processed_files=None):
        """
        Send batch processing summary email with individual file attachments
        """
        try:
            # Subject using actual file names instead of directory names
            if processed_files and len(processed_files) == 1:
                subject = f"Enhanced Summary: {processed_files[0]['original_name']}"
            elif processed_files and len(processed_files) > 1:
                subject = f"Enhanced Batch Summary: {len(processed_files)} files processed"
            else:
                subject = f"Enhanced Batch Summary: {file_path.name}"
            
            # Parse content with enhanced analysis
            parsed_content = self._parse_summary_content(summary_content)
            
            # Create HTML email body
            html_body = self._create_batch_html_email(
                file_path, 
                parsed_content, 
                processing_metrics, 
                processed_files
            )
            
            # Create plain text version
            text_body = self._create_batch_text_email(
                file_path, 
                parsed_content, 
                processing_metrics, 
                processed_files
            )
            
            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Date'] = formatdate(localtime=True)
            
            # Add text and HTML parts
            text_part = MIMEText(text_body, 'plain', 'utf-8')
            html_part = MIMEText(html_body, 'html', 'utf-8')
            
            message.attach(text_part)
            message.attach(html_part)
            
            # Attach individual summary files if available
            if processed_files:
                # Create combined summary file instead of individual attachments
                combined_summary = self._create_combined_summary_file(processed_files)
                if combined_summary:
                    try:
                        # Create combined attachment
                        attachment = MIMEText(combined_summary, 'plain', 'utf-8')
                        attachment.add_header(
                            'Content-Disposition',
                            f'attachment; filename="combined_batch_summary_{int(time.time())}.md"'
                        )
                        message.attach(attachment)
                        logger.info(f"📎 Combined summary file attached ({len(combined_summary)} characters)")
                        
                    except Exception as e:
                        logger.warning(f"Could not attach combined summary: {e}")
                
                # Optional: Also attach individual files (up to 3 for email size limits)
                for file_info in processed_files[:3]:
                    try:
                        summary_file = file_info['summary_file']
                        if summary_file.exists():
                            with open(summary_file, 'r', encoding='utf-8') as f:
                                attachment_content = f.read()
                            
                            # Create text attachment
                            attachment = MIMEText(attachment_content, 'plain', 'utf-8')
                            attachment.add_header(
                                'Content-Disposition',
                                f'attachment; filename="{file_info["original_name"]}_summary_ja.md"'
                            )
                            message.attach(attachment)
                            
                    except Exception as e:
                        logger.warning(f"Could not attach {file_info['summary_file']}: {e}")
                        continue
            
            # Send email
            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.success(f"✅ Batch email with attachments sent to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error sending batch email with attachments: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _create_batch_html_email(self, file_path, parsed_content, processing_metrics=None, processed_files=None):
        """Create HTML email body for batch processing results"""
        
        # File information section
        if processed_files and len(processed_files) == 1:
            file_info = f"<h2>📄 Processed File: {processed_files[0]['original_name']}</h2>"
        elif processed_files and len(processed_files) > 1:
            file_list = "<ul>" + "".join([f"<li>{f['original_name']}</li>" for f in processed_files[:10]]) + "</ul>"
            if len(processed_files) > 10:
                file_list += f"<p><em>... and {len(processed_files) - 10} more files</em></p>"
            file_info = f"<h2>📁 Batch Processing: {len(processed_files)} files</h2>{file_list}"
        else:
            file_info = f"<h2>📁 Processed Directory: {file_path.name}</h2>"
        
        # Processing metrics section
        metrics_html = ""
        if processing_metrics:
            metrics_html = f"""
            <div style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; margin: 15px 0;">
                <h3>📊 Processing Metrics</h3>
                <ul>
                    <li><strong>Total Files:</strong> {processing_metrics.get('total_files', 'N/A')}</li>
                    <li><strong>Successfully Processed:</strong> {processing_metrics.get('successful_files', 'N/A')}</li>
                    <li><strong>Success Rate:</strong> {processing_metrics.get('success_rate', 'N/A')}%</li>
                    <li><strong>Processing Time:</strong> {processing_metrics.get('processing_time', 'N/A')}</li>
                    <li><strong>Output Directory:</strong> {processing_metrics.get('output_directory', 'N/A')}</li>
                </ul>
            </div>
            """
        
        # Content sections
        english_summary = parsed_content.get('english_summary', '')
        japanese_summary = parsed_content.get('japanese_summary', '')
        translation = parsed_content.get('translation', '')
        
        # Build HTML
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Enhanced Batch Processing Results</title>
        </head>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif; line-height: 1.6; color: #333; max-width: 800px; margin: 0 auto; padding: 20px;">
            
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
                <h1 style="margin: 0; font-size: 24px;">🎓 Enhanced Academic Processing Results</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">Generated by LocalLLM Enhanced Batch System</p>
            </div>
            
            {file_info}
            
            {metrics_html}
            
            {f'''
            <div style="background-color: #f8f9fa; padding: 20px; border-left: 4px solid #007bff; margin: 20px 0;">
                <h3 style="color: #007bff; margin-top: 0;">📝 English Summary</h3>
                <div style="white-space: pre-wrap; font-family: Georgia, serif;">{english_summary}</div>
            </div>
            ''' if english_summary else ''}
            
            {f'''
            <div style="background-color: #fff5f5; padding: 20px; border-left: 4px solid #e53e3e; margin: 20px 0;">
                <h3 style="color: #e53e3e; margin-top: 0;">🌸 Japanese Summary</h3>
                <div style="white-space: pre-wrap; font-family: 'Hiragino Sans', 'Yu Gothic', Meiryo, sans-serif;">{japanese_summary}</div>
            </div>
            ''' if japanese_summary else ''}
            
            {f'''
            <div style="background-color: #f0fff4; padding: 20px; border-left: 4px solid #38a169; margin: 20px 0;">
                <h3 style="color: #38a169; margin-top: 0;">🌐 Translation</h3>
                <div style="white-space: pre-wrap; font-family: 'Hiragino Sans', 'Yu Gothic', Meiryo, sans-serif;">{translation}</div>
            </div>
            ''' if translation else ''}
            
            <div style="background-color: #f7fafc; padding: 15px; border-radius: 8px; margin-top: 30px; text-align: center; border: 1px solid #e2e8f0;">
                <p style="margin: 0; color: #718096; font-size: 14px;">
                    <strong>LocalLLM Enhanced Academic Processor</strong><br>
                    Batch processing completed with technical novelty analysis and comprehensive summaries
                    {f'<br>📎 {len(processed_files)} summary files attached' if processed_files else ''}
                </p>
            </div>
            
        </body>
        </html>
        """
        
        return html_content
    
    def _create_batch_text_email(self, file_path, parsed_content, processing_metrics=None, processed_files=None):
        """Create plain text email body for batch processing results"""
        
        # File information
        if processed_files and len(processed_files) == 1:
            file_info = f"📄 Processed File: {processed_files[0]['original_name']}"
        elif processed_files and len(processed_files) > 1:
            file_list = "\n".join([f"  • {f['original_name']}" for f in processed_files[:10]])
            if len(processed_files) > 10:
                file_list += f"\n  ... and {len(processed_files) - 10} more files"
            file_info = f"📁 Batch Processing: {len(processed_files)} files\n{file_list}"
        else:
            file_info = f"📁 Processed Directory: {file_path.name}"
        
        # Processing metrics
        metrics_text = ""
        if processing_metrics:
            metrics_text = f"""
📊 Processing Metrics:
• Total Files: {processing_metrics.get('total_files', 'N/A')}
• Successfully Processed: {processing_metrics.get('successful_files', 'N/A')}
• Success Rate: {processing_metrics.get('success_rate', 'N/A')}%
• Processing Time: {processing_metrics.get('processing_time', 'N/A')}
• Output Directory: {processing_metrics.get('output_directory', 'N/A')}
"""
        
        # Content sections
        english_summary = parsed_content.get('english_summary', '')
        japanese_summary = parsed_content.get('japanese_summary', '')
        translation = parsed_content.get('translation', '')
        
        text_content = f"""🎓 Enhanced Academic Processing Results
Generated by LocalLLM Enhanced Batch System

{file_info}
{metrics_text}
{'=' * 50}

{f'''📝 English Summary:
{english_summary}

{'=' * 50}
''' if english_summary else ''}

{f'''🌸 Japanese Summary:
{japanese_summary}

{'=' * 50}
''' if japanese_summary else ''}

{f'''🌐 Translation:
{translation}

{'=' * 50}
''' if translation else ''}

LocalLLM Enhanced Academic Processor
Batch processing completed with technical novelty analysis and comprehensive summaries
{f'📎 {len(processed_files)} summary files attached' if processed_files else ''}
        """
        
        return text_content
    
    def _create_combined_summary_file(self, processed_files):
        """Create a combined summary file from all individual summaries"""
        try:
            from datetime import datetime
            
            combined_content = f"""# Combined Batch Processing Summary
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Total Files: {len(processed_files)}

{'=' * 80}

"""
            
            for i, file_info in enumerate(processed_files, 1):
                try:
                    # Read individual summary file
                    with open(file_info['summary_file'], 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # Add file section to combined content
                    file_section = f"""
## File {i}: {file_info['original_name']}
**Source File:** {file_info['summary_file'].name}
**Processing Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{file_content}

{'=' * 80}

"""
                    combined_content += file_section
                    
                except Exception as e:
                    error_section = f"""
## File {i}: {file_info['original_name']} (ERROR)
**Error:** Could not read summary file: {e}

{'=' * 80}

"""
                    combined_content += error_section
                    continue
            
            # Add footer
            footer = f"""
## Summary Statistics
- Total processed files: {len(processed_files)}
- Combined content length: {len(combined_content)} characters
- Generated by: LocalLLM Enhanced Academic Processor
- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This file contains all individual processing results combined into a single document for easy reference.
"""
            combined_content += footer
            
            return combined_content
            
        except Exception as e:
            logger.warning(f"Error creating combined summary file: {e}")
            return None


# Backwards compatibility - alias the original EmailSender to the enhanced version
EmailSender = EnhancedEmailSender


def send_processing_notification(
    recipient_email: str,
    file_path: Path,
    summary_content: str,
    processing_metrics: Optional[Dict[str, Any]] = None,
    sender_email: Optional[str] = None,
    sender_password: Optional[str] = None
) -> bool:
    """
    Convenience function to send enhanced processing notification
    
    Args:
        recipient_email: Recipient email address
        file_path: Path to processed file
        summary_content: Summary content
        processing_metrics: Processing statistics
        sender_email: Sender email (optional, uses env var if not provided)
        sender_password: Sender password (optional, uses env var if not provided)
        
    Returns:
        Success status
    """
    email_sender = EnhancedEmailSender()
    
    if sender_email and sender_password:
        email_sender.configure_email(sender_email, sender_password)
    
    return email_sender.send_summary_result(
        recipient_email, file_path, summary_content, processing_metrics
    )


if __name__ == "__main__":
    # Test enhanced email functionality
    print("🧪 Testing enhanced email functionality...")
    
    sender = EnhancedEmailSender()
    
    # Test configuration (requires environment variables)
    if sender.sender_email and sender.sender_password:
        success = sender.test_connection()
        print(f"Enhanced email test: {'✅ Success' if success else '❌ Failed'}")
    else:
        print("⚠️ Email credentials not configured. Set EMAIL_SENDER and EMAIL_PASSWORD environment variables.")
