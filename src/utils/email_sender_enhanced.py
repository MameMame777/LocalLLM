"""
Enhanced email notification system for LocalLLM processing results
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
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
            
            for section in sections:
                section = section.strip()
                if not section:
                    continue
                    
                # Look for English summary
                if 'ENGLISH SUMMARY' in section or 'LLM-Generated' in section:
                    lines = section.split('\n')
                    content_lines: List[str] = []
                    start_content = False
                    for line in lines:
                        if start_content or ('Summary' in line and '==' not in line):
                            start_content = True
                            if line.strip() and '==' not in line and not line.startswith('📝'):
                                content_lines.append(line.strip())
                    if content_lines:
                        parsed['english_summary'] = '\n'.join(content_lines)
                
                # Look for Japanese summary
                elif '日本語要約' in section or 'Japanese Summary' in section:
                    lines = section.split('\n')
                    content_lines: List[str] = []
                    start_content = False
                    for line in lines:
                        if start_content or ('Summary' in line and '==' not in line):
                            start_content = True
                            if line.strip() and '==' not in line and not line.startswith('📝'):
                                content_lines.append(line.strip())
                    if content_lines:
                        parsed['japanese_summary'] = '\n'.join(content_lines)
                
                # Look for translation
                elif '日本語翻訳' in section or 'Japanese Translation' in section:
                    lines = section.split('\n')
                    content_lines: List[str] = []
                    start_content = False
                    for line in lines:
                        if start_content or ('Translation' in line and '==' not in line):
                            start_content = True
                            if line.strip() and '==' not in line and not line.startswith('🌐'):
                                content_lines.append(line.strip())
                    if content_lines:
                        parsed['translation'] = '\n'.join(content_lines)
            
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
