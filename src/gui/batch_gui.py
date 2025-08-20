#!/usr/bin/env python3
"""
GUI Interface for LocalLLM Batch Processing
Modern and user-friendly interface using tkinter with ttk styling
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
import time
import random
import subprocess
import traceback
import signal
from pathlib import Path
from datetime import datetime
import queue
import webbrowser
from typing import Dict

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from batch_processing.batch_processor import BatchProcessor
from batch_processing.file_scanner import FileScanner
from utils.log_cleaner import LogCleaner, create_default_log_cleaner

# Signal handling for proper Ctrl+C handling
def signal_handler(signum, frame):
    """Handle keyboard interrupt gracefully"""
    print("\n🛑 KeyboardInterrupt detected - shutting down gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

# 技術翻訳エンジンとの統合
try:
    from academic.technical_translator import TechnicalDocumentTranslator
    from academic.academic_processor import AcademicDocumentProcessor
    from academic.academic_output_formatter import AcademicOutputFormatter
    from academic.llm_processor import LLMProcessor
    TECHNICAL_TRANSLATION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Technical translation modules not available: {e}")
    TECHNICAL_TRANSLATION_AVAILABLE = False


# Global mock processing function for multiprocessing compatibility
def mock_process_file_global(file_path: Path, **kwargs) -> str:
    """
    Global mock processing function that can be pickled for multiprocessing.
    
    Args:
        file_path: Path to the file to process
        **kwargs: Additional parameters
        
    Returns:
        Mock processing result
    """
    import time
    import random
    
    # Simulate processing time based on file size
    try:
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        # Larger files take longer (0.5-3 seconds)
        processing_time = 0.5 + (file_size_mb * 0.1) + (random.random() * 2)
    except:
        processing_time = 0.5 + random.random() * 2
    
    time.sleep(processing_time)
    
    # Simulate occasional failures (10% rate)
    if random.random() < 0.1:
        raise Exception(f"Mock processing failed for {file_path.name}")
    
    # Generate mock result
    word_count = random.randint(50, 200)
    return f"Summary generated for {file_path.name} - {word_count} words, {processing_time:.1f}s processing time"


class BatchProcessingGUI:
    """
    Modern GUI for LocalLLM Batch Processing System
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("LocalLLM Batch Processor")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Set project root first
        self.project_root = Path(__file__).parent.parent.parent
        
        # Set modern style
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Modern looking theme
        
        # Processing state
        self.processor = None
        self.processing_thread = None
        self.is_processing = False
        self.queue = queue.Queue()
        
        # Initialize the log cleaner
        self.log_cleaner = create_default_log_cleaner()
        self.log_cleaner.start_scheduler()  # Start automatic cleanup
        
        # Variables
        self.input_directory = tk.StringVar()
        # Set default to test_data_technical for consistency with command line version
        default_input_dir = self.project_root / "test_data_technical"
        if default_input_dir.exists():
            self.input_directory.set(str(default_input_dir))
        # 絶対パスで統一し、プロジェクトルートのoutputディレクトリを使用
        self.output_directory = tk.StringVar(value=str(self.project_root / "output" / "batch_gui"))
        self.max_workers = tk.IntVar(value=2)  # Reduced for LLM stability
        self.use_multiprocessing = tk.BooleanVar(value=False)  # Default to threading for GUI compatibility
        self.continue_on_error = tk.BooleanVar(value=True)
        self.target_language = tk.StringVar(value="auto")  # Changed to auto
        self.max_summary_length = tk.IntVar(value=2000)  # Increased for comprehensive JSON processing
        self.use_real_processing = tk.BooleanVar(value=True)  # Enable real processing by default
        # Remove unused LLM setting (handled by Enhanced Academic Processing)
        # self.use_llm = tk.BooleanVar(value=False)  # Not needed - LLM is integrated in Academic Processing
        self.auto_detect_language = tk.BooleanVar(value=True)  # New: Auto language detection
        
        # Enhanced Academic Processing is always enabled (simplified UI)
        # Academic processing settings removed - always uses optimal settings
        
        # Output content options (all included by default in academic mode)
        self.include_metadata = tk.BooleanVar(value=False)  # Only metadata is optional
        
        # File extension variables - default to txt for technical files
        self.ext_pdf = tk.BooleanVar(value=False)  # Disable PDF by default to avoid metadata issues
        self.ext_html = tk.BooleanVar(value=False)
        self.ext_txt = tk.BooleanVar(value=True)   # Enable txt for technical test files
        self.ext_docx = tk.BooleanVar(value=False)
        self.ext_json = tk.BooleanVar(value=True)  # Enable JSON for URL processing
        
        self.setup_ui()
        self.setup_styles()
        
        # Start monitoring queue
        self.root.after(100, self.check_queue)
        
        # Setup window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def create_technical_translation_function(self):
        """Create technical translation processing function with real LLM"""
        def process_technical_document(file_path: Path, **kwargs) -> str:
            """Process file using technical translation system with real LLM"""
            try:
                if not TECHNICAL_TRANSLATION_AVAILABLE:
                    return f"""# ⚠️ 技術翻訳システム未利用可能
**ファイル名**: {file_path.name}
**処理日時**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

技術翻訳モジュールが利用できません。インポートエラーが発生しています。
"""
                
                # Extract content based on file type
                start_time = time.time()
                
                if file_path.suffix.lower() == '.pdf':
                    # Simple PDF reading (fallback implementation)
                    try:
                        import PyPDF2
                        with open(file_path, 'rb') as file:
                            pdf_reader = PyPDF2.PdfReader(file)
                            content = ""
                            for page in pdf_reader.pages:
                                content += page.extract_text()
                    except ImportError:
                        # Fallback: treat as text file
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    except Exception as e:
                        content = f"PDF読み込みエラー: {e}"
                        
                elif file_path.suffix.lower() in ['.html', '.htm']:
                    # Simple HTML reading
                    try:
                        from bs4 import BeautifulSoup
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            html_content = f.read()
                        soup = BeautifulSoup(html_content, 'html.parser')
                        content = soup.get_text()
                    except ImportError:
                        # Fallback: read as text
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    except Exception as e:
                        content = f"HTML読み込みエラー: {e}"
                else:
                    # Text file
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                
                if not content.strip():
                    return "⚠️ ファイルからコンテンツを抽出できませんでした"
                
                # Initialize real LLM processor
                self.log_message("🤖 Real LLM processor initializing...")
                llm_processor = LLMProcessor()
                
                # Initialize technical translation system with real LLM
                tech_translator = TechnicalDocumentTranslator(llm_processor=llm_processor)
                
                # Detect document type (now using correct method name)
                doc_type = tech_translator.classify_document_type(content)
                
                # Translate technical document using real LLM
                translation_result = tech_translator.translate_technical_document(content)
                
                # Get LLM translation if available
                if llm_processor.is_loaded:
                    self.log_message("✅ Using real Llama 2 LLM for technical translation")
                    llm_result = llm_processor.translate_technical_text(content[:4000], doc_type)
                    
                    # Debug log
                    print(f"DEBUG: LLM result keys: {llm_result.keys()}")
                    print(f"DEBUG: Japanese translation length: {len(llm_result.get('japanese_translation', ''))}")
                    
                    # Enhanced translation result with LLM - using correct keys
                    enhanced_translation = {
                        'japanese_translation': llm_result.get('japanese_translation', translation_result.japanese_translation),
                        'document_type': doc_type,
                        'technical_terms': translation_result.technical_terms_found,
                        'quality_score': llm_result.get('confidence_score', translation_result.confidence_score),
                        'translation_quality': "excellent" if llm_result.get('llm_used', False) else translation_result.translation_quality,
                        'llm_used': llm_result.get('llm_used', False),
                        'processing_time': llm_result.get('processing_time', 0)
                    }
                else:
                    self.log_message("⚠️ LLM not available, using dictionary-based translation")
                    # Convert TechnicalTranslationResult to dict for formatter
                    enhanced_translation = {
                        'japanese_translation': translation_result.japanese_translation,
                        'document_type': translation_result.document_type,
                        'technical_terms': translation_result.technical_terms_found,
                        'quality_score': translation_result.confidence_score,
                        'translation_quality': translation_result.translation_quality,
                        'llm_used': False,
                        'processing_time': 0
                    }
                
                # Initialize academic processor for enhanced formatting
                academic_processor = AcademicDocumentProcessor(llm_processor=llm_processor)
                
                # Get processing metadata
                processing_time = time.time() - start_time
                word_count = len(content.split())
                
                # Format final result - pass translation data directly to formatter
                final_result = academic_processor.formatter.format_technical_japanese_summary({
                    **enhanced_translation,  # Spread translation data
                    'original_text': content[:500] + "..." if len(content) > 500 else content,
                    'file_name': file_path.name,
                    'file_size': f"{file_path.stat().st_size / 1024 / 1024:.2f} MB",
                    'word_count': word_count,
                    'processing_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'target_language': 'ja'
                })
                
                return final_result
                
            except Exception as e:
                error_msg = f"ERROR 技術翻訳処理エラー: {str(e)}"
                print(f"Technical translation error: {e}")
                return error_msg
        
        return process_technical_document
    
    def on_closing(self):
        """Handle window closing event"""
        try:
            # Stop log cleaner scheduler
            if hasattr(self, 'log_cleaner') and self.log_cleaner:
                self.log_cleaner.stop_scheduler()
            
            # Stop any running processing
            if hasattr(self, 'is_processing') and self.is_processing:
                self.stop_processing()
            
            # Destroy the window
            self.root.destroy()
        except Exception as e:
            print(f"Error during closing: {e}")
            self.root.destroy()
    
    def on_language_mode_change(self):
        """Handle language mode changes"""
        if self.auto_detect_language.get():
            self.lang_detection_label.config(text="Auto-detect enabled", foreground='green')
            if self.target_language.get() != 'auto':
                self.target_language.set('auto')
        else:
            self.lang_detection_label.config(text="Manual language selection", foreground='blue')
            if self.target_language.get() == 'auto':
                self.target_language.set('ja')
                
    # Enhanced Academic Processing is always enabled - no toggle needed
    # def on_academic_mode_change(self): removed - not needed
    
    def setup_styles(self):
        """Setup custom styles for modern appearance"""
        # Configure styles
        self.style.configure('Title.TLabel', font=('Segoe UI', 12, 'bold'))
        self.style.configure('Heading.TLabel', font=('Segoe UI', 10, 'bold'))
        self.style.configure('Status.TLabel', font=('Segoe UI', 9))
        self.style.configure('Success.TLabel', foreground='green', font=('Segoe UI', 9, 'bold'))
        self.style.configure('Error.TLabel', foreground='red', font=('Segoe UI', 9, 'bold'))
        self.style.configure('Warning.TLabel', foreground='orange', font=('Segoe UI', 9, 'bold'))
        
        # Button styles
        self.style.configure('Action.TButton', font=('Segoe UI', 9, 'bold'))
        self.style.configure('Start.TButton', font=('Segoe UI', 10, 'bold'))
    
    def setup_ui(self):
        """Setup the main user interface"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="LocalLLM Batch Processor", style='Title.TLabel')
        title_label.grid(row=0, column=0, pady=(0, 20), sticky=tk.W)
        
        # Toolbar for specialized tools
        self.setup_toolbar(main_frame)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        
        # Setup tabs
        self.setup_config_tab()
        self.setup_processing_tab()
        self.setup_results_tab()
        self.setup_processed_files_tab()
        self.setup_log_management_tab()
        
        # Status bar
        self.setup_status_bar(main_frame)
    
    def setup_toolbar(self, parent):
        """Setup toolbar with specialized processing tools"""
        toolbar_frame = ttk.Frame(parent)
        toolbar_frame.grid(row=0, column=1, sticky=(tk.N, tk.E), pady=(0, 20))
        
        # API Server Button
        api_button = ttk.Button(toolbar_frame, text="API Server", 
                               command=self.toggle_api_server, style='API.TButton')
        api_button.grid(row=0, column=0, padx=5)
        
        # Performance Monitor Button
        perf_button = ttk.Button(toolbar_frame, text="Performance", 
                                command=self.open_performance_monitor, style='Performance.TButton')
        perf_button.grid(row=0, column=1, padx=(5, 0))
        
        # Email Config Button
        email_button = ttk.Button(toolbar_frame, text="📧 Email Config", 
                                 command=self.check_email_config, style='Email.TButton')
        email_button.grid(row=0, column=2, padx=(5, 0))
        
        # Configure custom button styles
        self.style.configure('API.TButton', foreground='#A23B72')
        self.style.configure('Performance.TButton', foreground='#F18F01')
        self.style.configure('Email.TButton', foreground='#1F77B4')
        
    def toggle_api_server(self):
        """Toggle API server"""
        try:
            # Check if API server is running
            import requests
            try:
                response = requests.get("http://localhost:8000/health", timeout=2)
                if response.status_code == 200:
                    messagebox.showinfo("API Server", "🌐 API Server is already running at http://localhost:8000")
                    webbrowser.open("http://localhost:8000/docs")
                    return
            except:
                pass
            
            # Start API server
            import subprocess
            script_path = Path(__file__).parent.parent / "api" / "document_api.py"
            subprocess.Popen([sys.executable, str(script_path)])
            self.log_message("🌐 API Server starting at http://localhost:8000")
            
            # Open docs after a delay
            self.root.after(3000, lambda: webbrowser.open("http://localhost:8000/docs"))
            
        except Exception as e:
            messagebox.showerror("エラー", f"API Server toggle failed: {str(e)}")
            
    def open_performance_monitor(self):
        """Open performance monitoring window"""
        try:
            # Create performance monitoring window
            perf_window = tk.Toplevel(self.root)
            perf_window.title("📊 Performance Monitor")
            perf_window.geometry("600x400")
            
            # Performance info display
            info_text = scrolledtext.ScrolledText(perf_window, wrap=tk.WORD)
            info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            # Get performance info
            try:
                import psutil
                import json
                
                perf_info = {
                    "CPU Usage": f"{psutil.cpu_percent()}%",
                    "Memory Usage": f"{psutil.virtual_memory().percent}%",
                    "Available Memory": f"{psutil.virtual_memory().available / (1024**3):.1f} GB",
                    "Disk Usage": f"{psutil.disk_usage('/').percent}%",
                    "Process Count": psutil.boot_time()
                }
                
                info_text.insert(tk.END, "🔍 System Performance Information\n")
                info_text.insert(tk.END, "=" * 40 + "\n\n")
                
                for key, value in perf_info.items():
                    info_text.insert(tk.END, f"{key}: {value}\n")
                
                info_text.insert(tk.END, f"\n📁 Current Working Directory: {os.getcwd()}\n")
                info_text.insert(tk.END, f"🐍 Python Version: {sys.version}\n")
                
            except ImportError:
                info_text.insert(tk.END, "⚠️ psutil not available for detailed performance monitoring\n")
                info_text.insert(tk.END, f"📁 Current Working Directory: {os.getcwd()}\n")
                info_text.insert(tk.END, f"🐍 Python Version: {sys.version}\n")
            
            self.log_message("📊 Performance Monitor opened")
            
        except Exception as e:
            messagebox.showerror("エラー", f"Performance Monitor failed: {str(e)}")
    
    def check_email_config(self):
        """Check and display email configuration status"""
        try:
            import os
            import yaml
            from dotenv import load_dotenv
            from pathlib import Path
            
            # Create email config window
            email_window = tk.Toplevel(self.root)
            email_window.title("📧 Email Configuration Status")
            email_window.geometry("600x500")
            
            # Email info display
            info_text = scrolledtext.ScrolledText(email_window, wrap=tk.WORD)
            info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            info_text.insert(tk.END, "📧 Email Configuration Check\n")
            info_text.insert(tk.END, "=" * 40 + "\n\n")
            
            # Check .env.email file
            env_email_path = Path(".env.email")
            if env_email_path.exists():
                load_dotenv(env_email_path)
                info_text.insert(tk.END, "✅ .env.email file found\n")
                
                sender_email = os.getenv("EMAIL_SENDER")
                sender_password = os.getenv("EMAIL_PASSWORD")
                recipient_email = os.getenv("NOTIFICATION_EMAIL")
                
                if sender_email:
                    info_text.insert(tk.END, f"   📤 Sender: {sender_email}\n")
                if sender_password:
                    info_text.insert(tk.END, f"   🔑 Password: {'*' * len(sender_password)}\n")
                if recipient_email:
                    info_text.insert(tk.END, f"   📥 Recipient: {recipient_email}\n")
                    
                if sender_email and sender_password and recipient_email:
                    info_text.insert(tk.END, "   ✅ All email credentials configured\n\n")
                else:
                    info_text.insert(tk.END, "   ⚠️ Missing email credentials\n\n")
            else:
                info_text.insert(tk.END, "❌ .env.email file not found\n\n")
            
            # Check config/email_config.yaml
            config_path = Path("config/email_config.yaml")
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        email_config = yaml.safe_load(f)
                    
                    info_text.insert(tk.END, "✅ config/email_config.yaml found\n")
                    
                    email_settings = email_config.get('email', {})
                    if email_settings.get('enabled', False):
                        info_text.insert(tk.END, "   ✅ Email notifications enabled\n")
                        
                        sender_info = email_settings.get('sender', {})
                        if sender_info.get('email'):
                            info_text.insert(tk.END, f"   📤 Configured sender: {sender_info.get('email')}\n")
                        if sender_info.get('password'):
                            info_text.insert(tk.END, f"   🔑 Password configured: {'*' * len(sender_info.get('password', ''))}\n")
                        if email_settings.get('default_recipient'):
                            info_text.insert(tk.END, f"   📥 Default recipient: {email_settings.get('default_recipient')}\n")
                    else:
                        info_text.insert(tk.END, "   ⚠️ Email notifications disabled\n")
                        
                except Exception as e:
                    info_text.insert(tk.END, f"   ❌ Error reading config: {e}\n")
            else:
                info_text.insert(tk.END, "❌ config/email_config.yaml not found\n\n")
            
            # Setup instructions
            info_text.insert(tk.END, "\n📋 Setup Instructions:\n")
            info_text.insert(tk.END, "-" * 25 + "\n")
            info_text.insert(tk.END, "1. Copy .env.email.sample to .env.email\n")
            info_text.insert(tk.END, "2. Copy config/email_config.yaml.sample to config/email_config.yaml\n")
            info_text.insert(tk.END, "3. Configure your Gmail credentials:\n")
            info_text.insert(tk.END, "   - Enable 2-factor authentication\n")
            info_text.insert(tk.END, "   - Generate app password\n")
            info_text.insert(tk.END, "   - Update configuration files\n")
            info_text.insert(tk.END, "4. Set 'enabled: true' in email_config.yaml\n")
            
            # Test email button
            test_frame = ttk.Frame(email_window)
            test_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
            
            ttk.Button(test_frame, text="🧪 Test Email Configuration", 
                      command=self.test_email_configuration).pack(side=tk.LEFT, padx=(0, 5))
            ttk.Button(test_frame, text="📁 Open Config Folder", 
                      command=lambda: os.startfile("config")).pack(side=tk.LEFT)
            
            self.log_message("📧 Email Configuration window opened")
            
        except Exception as e:
            messagebox.showerror("エラー", f"Email config check failed: {str(e)}")
    
    def test_email_configuration(self):
        """Test email configuration by sending a test email"""
        try:
            import os
            import yaml
            from dotenv import load_dotenv
            from pathlib import Path
            
            # Load configuration
            env_email_path = Path(".env.email")
            if env_email_path.exists():
                load_dotenv(env_email_path)
            
            config_path = Path("config/email_config.yaml")
            email_config = {}
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    email_config = yaml.safe_load(f)
            
            # Get credentials
            sender_email = os.getenv("EMAIL_SENDER")
            sender_password = os.getenv("EMAIL_PASSWORD")
            recipient_email = os.getenv("NOTIFICATION_EMAIL")
            
            # Try config file if env vars not found
            if email_config and not (sender_email and sender_password and recipient_email):
                email_settings = email_config.get('email', {})
                if email_settings.get('enabled', False):
                    sender_info = email_settings.get('sender', {})
                    sender_email = sender_info.get('email')
                    sender_password = sender_info.get('password')
                    recipient_email = email_settings.get('default_recipient')
            
            if not (sender_email and sender_password and recipient_email):
                messagebox.showerror("Configuration Error", 
                                   "Email configuration incomplete. Please configure credentials first.")
                return
            
            # Send test email
            from src.utils.email_sender import send_processing_notification
            
            test_metrics = {
                "test_type": "GUI Email Configuration Test",
                "timestamp": str(datetime.now()),
                "status": "success"
            }
            
            success = send_processing_notification(
                recipient_email=recipient_email,
                file_path=Path("Email_Configuration_Test"),
                summary_content="This is a test email from LocalLLM Batch GUI to verify email configuration is working correctly.",
                processing_metrics=test_metrics,
                sender_email=sender_email,
                sender_password=sender_password
            )
            
            if success:
                messagebox.showinfo("Test Success", 
                                  f"✅ Test email sent successfully to {recipient_email}")
                self.log_message(f"✅ Test email sent successfully to {recipient_email}")
            else:
                messagebox.showerror("Test Failed", 
                                   "❌ Failed to send test email. Please check your configuration.")
                self.log_message("❌ Test email failed")
                
        except Exception as e:
            messagebox.showerror("Test Error", f"Email test failed: {str(e)}")
            self.log_message(f"❌ Email test error: {str(e)}")
    
    
    def setup_config_tab(self):
        """Setup configuration tab"""
        config_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(config_frame, text="Configuration")
        
        # Configure grid weights for proper layout
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1)
        config_frame.rowconfigure(0, weight=0)  # Input Directory
        config_frame.rowconfigure(1, weight=0)  # File Types & Processing Settings  
        config_frame.rowconfigure(2, weight=0)  # Enhanced Academic Processing
        config_frame.rowconfigure(3, weight=0)  # Output Directory
        
        # Input Directory Section
        input_section = ttk.LabelFrame(config_frame, text="Input Directory", padding="10")
        input_section.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        config_frame.columnconfigure(0, weight=1)
        
        ttk.Label(input_section, text="Select folder containing files to process:").grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        dir_frame = ttk.Frame(input_section)
        dir_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        dir_frame.columnconfigure(0, weight=1)
        
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.input_directory, width=60)
        self.dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(dir_frame, text="Browse", command=self.browse_input_directory).grid(row=0, column=1)
        
        # File preview
        self.file_preview = tk.Text(input_section, height=4, width=70, state='disabled')
        self.file_preview.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # File Types Section
        types_section = ttk.LabelFrame(config_frame, text="File Types to Process", padding="10")
        types_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10), padx=(0, 5))
        
        ttk.Checkbutton(types_section, text="PDF Files (.pdf)", variable=self.ext_pdf).grid(row=0, column=0, sticky=tk.W)
        ttk.Checkbutton(types_section, text="HTML Files (.html, .htm)", variable=self.ext_html).grid(row=1, column=0, sticky=tk.W)
        ttk.Checkbutton(types_section, text="Text Files (.txt)", variable=self.ext_txt).grid(row=2, column=0, sticky=tk.W)
        ttk.Checkbutton(types_section, text="Word Documents (.docx)", variable=self.ext_docx).grid(row=3, column=0, sticky=tk.W)
        ttk.Checkbutton(types_section, text="JSON Files (.json)", variable=self.ext_json).grid(row=4, column=0, sticky=tk.W)
        
        # Processing Settings Section
        settings_section = ttk.LabelFrame(config_frame, text="Processing Settings", padding="10")
        settings_section.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N), pady=(0, 10), padx=(5, 0))
        
        # Workers
        ttk.Label(settings_section, text="Max Workers:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        worker_frame = ttk.Frame(settings_section)
        worker_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        ttk.Scale(worker_frame, from_=1, to=16, variable=self.max_workers, orient='horizontal').grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Label(worker_frame, textvariable=self.max_workers).grid(row=0, column=1, padx=(5, 0))
        worker_frame.columnconfigure(0, weight=1)
        
        # Processing mode
        ttk.Checkbutton(settings_section, text="⚡ Use Multiprocessing", variable=self.use_multiprocessing).grid(row=1, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        ttk.Checkbutton(settings_section, text="🔧 Continue on Errors", variable=self.continue_on_error).grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        ttk.Checkbutton(settings_section, text="📄 Real Processing", variable=self.use_real_processing).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Note: LLM processing is handled by Enhanced Academic Processing
        llm_info_label = ttk.Label(settings_section, 
                                  text="💡 LLM processing is available via Enhanced Academic Processing below", 
                                  foreground='#666666', font=('Segoe UI', 8))
        llm_info_label.grid(row=4, column=0, columnspan=2, sticky=tk.W, pady=(5, 0))
        
        # Language settings
        language_frame = ttk.LabelFrame(settings_section, text="🌐 Language Settings", padding="5")
        language_frame.grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 5))
        language_frame.columnconfigure(1, weight=1)
        
        # Auto-detect option
        ttk.Checkbutton(language_frame, text="🔍 Auto-detect source language", 
                       variable=self.auto_detect_language, 
                       command=self.on_language_mode_change).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))
        
        # Target language selection
        ttk.Label(language_frame, text="Summary Language:").grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        lang_values = ['auto', 'ja', 'en', 'zh', 'ko']
        lang_combo = ttk.Combobox(language_frame, textvariable=self.target_language, 
                                 values=lang_values, state='readonly', width=12)
        lang_combo.grid(row=1, column=1, sticky=tk.W, pady=(5, 0), padx=(10, 0))
        
        # Language detection info
        self.lang_detection_label = ttk.Label(language_frame, text="💡 Auto-detect enabled", 
                                            foreground='green', font=('Segoe UI', 8))
        self.lang_detection_label.grid(row=2, column=0, columnspan=2, sticky=tk.W, pady=(2, 0))
        
        # Summary length
        ttk.Label(settings_section, text="Max Summary Length:").grid(row=6, column=0, sticky=tk.W, pady=(5, 0))
        length_frame = ttk.Frame(settings_section)
        length_frame.grid(row=6, column=1, sticky=(tk.W, tk.E), pady=(5, 0))
        ttk.Scale(length_frame, from_=200, to=5000, variable=self.max_summary_length, orient='horizontal').grid(row=0, column=0, sticky=(tk.W, tk.E))
        ttk.Label(length_frame, textvariable=self.max_summary_length).grid(row=0, column=1, padx=(5, 0))
        length_frame.columnconfigure(0, weight=1)
        
        # Enhanced Academic Processing Section (Always Active)
        academic_section = ttk.LabelFrame(config_frame, text="Enhanced Academic Processing (Always Active)", padding="10")
        academic_section.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        
        # Information display (no toggle needed)
        academic_info_frame = ttk.Frame(academic_section)
        academic_info_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status info label
        status_label = ttk.Label(academic_info_frame, 
                               text="● Active: Automatic Llama2 LLM summarization + Google Translate translation", 
                               foreground='green', font=('Segoe UI', 9, 'bold'))
        status_label.grid(row=0, column=0, sticky=tk.W)
        
        # Detailed info label
        detail_label = ttk.Label(academic_info_frame, 
                               text="Process: Document → LLM Summary → Translation → Comprehensive Results", 
                               foreground='blue', font=('Segoe UI', 8))
        detail_label.grid(row=1, column=0, sticky=tk.W, pady=(2, 0))
        
        # Output format options
        output_frame = ttk.LabelFrame(academic_section, text="Output Content", padding="5")
        output_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        output_frame.columnconfigure(0, weight=1)
        
        # Information label for what's included
        info_text = "Always uses: Llama2 LLM (summarization) + Google Translate (translation) = Comprehensive results"
        info_label = ttk.Label(output_frame, text=info_text, 
                              font=('Segoe UI', 8), foreground='#666666')
        info_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        # Simple metadata option
        ttk.Checkbutton(output_frame, text="Include document metadata", 
                       variable=self.include_metadata).grid(row=1, column=0, sticky=tk.W)
        

        
        # Output Directory Section
        output_section = ttk.LabelFrame(config_frame, text="Output Directory", padding="10")
        output_section.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 10))
        
        output_dir_frame = ttk.Frame(output_section)
        output_dir_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        output_dir_frame.columnconfigure(0, weight=1)
        output_section.columnconfigure(0, weight=1)
        
        ttk.Entry(output_dir_frame, textvariable=self.output_directory, width=60).grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(output_dir_frame, text="Browse", command=self.browse_output_directory).grid(row=0, column=1)
    
    def setup_processing_tab(self):
        """Setup processing tab with real-time monitoring"""
        process_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(process_frame, text="Processing")
        
        # Control buttons
        control_frame = ttk.Frame(process_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        process_frame.columnconfigure(0, weight=1)
        
        self.start_button = ttk.Button(control_frame, text="🚀 Start Processing", command=self.start_processing, style='Start.TButton')
        self.start_button.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_button = ttk.Button(control_frame, text="⏹️ Stop", command=self.stop_processing, state='disabled')
        self.stop_button.grid(row=0, column=1, padx=(0, 10))
        
        self.scan_button = ttk.Button(control_frame, text="🔍 Scan Files", command=self.scan_files)
        self.scan_button.grid(row=0, column=2)
        
        # Progress Section
        progress_section = ttk.LabelFrame(process_frame, text="Progress", padding="10")
        progress_section.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        # Overall progress
        ttk.Label(progress_section, text="Overall Progress:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.overall_progress = ttk.Progressbar(progress_section, mode='determinate')
        self.overall_progress.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_section.columnconfigure(0, weight=1)
        
        # Current file progress
        ttk.Label(progress_section, text="Current File:").grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.current_progress = ttk.Progressbar(progress_section, mode='indeterminate')
        self.current_progress.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Status labels
        self.status_label = ttk.Label(progress_section, text="Ready to start processing", style='Status.TLabel')
        self.status_label.grid(row=4, column=0, sticky=tk.W, pady=(0, 5))
        
        self.file_status_label = ttk.Label(progress_section, text="", style='Status.TLabel')
        self.file_status_label.grid(row=5, column=0, sticky=tk.W)
        
        # Statistics Section
        stats_section = ttk.LabelFrame(process_frame, text="Real-time Statistics", padding="10")
        stats_section.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        stats_frame = ttk.Frame(stats_section)
        stats_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        stats_section.columnconfigure(0, weight=1)
        
        # Create stats labels in a grid
        self.stats_labels: Dict[str, ttk.Label] = {}
        stats = [
            ("📁 Total Files:", "total_files"),
            ("✅ Completed:", "completed"),
            ("❌ Failed:", "failed"),
            ("📊 Success Rate:", "success_rate"),
            ("⚡ Speed:", "speed"),
            ("⏱️ ETA:", "eta")
        ]
        
        for i, (label, key) in enumerate(stats):
            row, col = i // 2, (i % 2) * 2
            ttk.Label(stats_frame, text=label).grid(row=row, column=col, sticky=tk.W, padx=(0, 5), pady=2)
            self.stats_labels[key] = ttk.Label(stats_frame, text="-", style='Status.TLabel')
            self.stats_labels[key].grid(row=row, column=col+1, sticky=tk.W, padx=(0, 20), pady=2)
        
        # Log Section
        log_section = ttk.LabelFrame(process_frame, text="Processing Log", padding="10")
        log_section.grid(row=3, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        process_frame.rowconfigure(3, weight=1)
        
        # Create scrolled text for log
        self.log_text = scrolledtext.ScrolledText(log_section, height=8, width=80, state='disabled')
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        log_section.columnconfigure(0, weight=1)
        log_section.rowconfigure(0, weight=1)
        
        # Log control buttons
        log_control_frame = ttk.Frame(log_section)
        log_control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(log_control_frame, text="🗑️ Clear Log", command=self.clear_log).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(log_control_frame, text="💾 Save Log", command=self.save_log).grid(row=0, column=1)
    
    def setup_results_tab(self):
        """Setup results and reports tab"""
        results_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(results_frame, text="Results")
        
        # Results summary section
        summary_section = ttk.LabelFrame(results_frame, text="Processing Summary", padding="10")
        summary_section.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        results_frame.columnconfigure(0, weight=1)
        
        self.results_text = tk.Text(summary_section, height=10, width=80, state='disabled', wrap=tk.WORD)
        self.results_text.grid(row=0, column=0, sticky=(tk.W, tk.E))
        summary_section.columnconfigure(0, weight=1)
        
        # Reports section
        reports_section = ttk.LabelFrame(results_frame, text="Generated Reports", padding="10")
        reports_section.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        results_frame.rowconfigure(1, weight=1)
        
        # Reports list
        self.reports_tree = ttk.Treeview(reports_section, columns=('Type', 'Size', 'Modified'), show='tree headings', height=8)
        self.reports_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        reports_section.columnconfigure(0, weight=1)
        reports_section.rowconfigure(0, weight=1)
        
        # Configure treeview columns
        self.reports_tree.heading('#0', text='Report File')
        self.reports_tree.heading('Type', text='Type')
        self.reports_tree.heading('Size', text='Size')
        self.reports_tree.heading('Modified', text='Modified')
        
        self.reports_tree.column('#0', width=300)
        self.reports_tree.column('Type', width=80)
        self.reports_tree.column('Size', width=100)
        self.reports_tree.column('Modified', width=150)
        
        # Scrollbar for treeview
        tree_scrollbar = ttk.Scrollbar(reports_section, orient='vertical', command=self.reports_tree.yview)
        tree_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.reports_tree.configure(yscrollcommand=tree_scrollbar.set)
        
        # Report control buttons
        report_control_frame = ttk.Frame(reports_section)
        report_control_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        ttk.Button(report_control_frame, text="🔄 Refresh", command=self.refresh_reports).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(report_control_frame, text="📁 Open Folder", command=self.open_reports_folder).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(report_control_frame, text="👁️ View Report", command=self.view_selected_report).grid(row=0, column=2)
        
        # Double-click to open report
        self.reports_tree.bind('<Double-1>', lambda e: self.view_selected_report())
    
    def setup_status_bar(self, parent):
        """Setup status bar at bottom"""
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        self.status_bar = ttk.Label(status_frame, text="Ready", relief='sunken', style='Status.TLabel')
        self.status_bar.grid(row=0, column=0, sticky=(tk.W, tk.E))
        status_frame.columnconfigure(0, weight=1)
    
    def browse_input_directory(self):
        """Browse for input directory"""
        directory = filedialog.askdirectory(title="Select Input Directory")
        if directory:
            self.input_directory.set(directory)
            self.scan_files()
    
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_directory.set(directory)
    
    def scan_files(self):
        """Scan files in the selected directory"""
        if not self.input_directory.get():
            messagebox.showwarning("Warning", "Please select an input directory first.")
            return
        
        try:
            scanner = FileScanner()
            input_path = Path(self.input_directory.get())
            
            if not input_path.exists():
                messagebox.showerror("Error", f"Directory does not exist: {input_path}")
                return
            
            # Scan directory
            categorized_files = scanner.scan_directory(input_path)
            
            # Update file preview
            self.file_preview.config(state='normal')
            self.file_preview.delete(1.0, tk.END)
            
            if scanner.scanned_files:
                preview_text = f"Found {len(scanner.scanned_files)} supported files:\n\n"
                for file_info in scanner.scanned_files[:10]:  # Show first 10 files
                    preview_text += f"📄 {file_info.path.name} ({file_info.file_type.upper()}, {file_info.size_mb:.2f} MB)\n"
                
                if len(scanner.scanned_files) > 10:
                    preview_text += f"\n... and {len(scanner.scanned_files) - 10} more files"
            else:
                preview_text = "No supported files found in the selected directory."
            
            self.file_preview.insert(1.0, preview_text)
            self.file_preview.config(state='disabled')
            
            self.log_message(f"✅ Scanned directory: {len(scanner.scanned_files)} files found")
            
        except Exception as e:
            error_msg = f"Failed to scan directory: {str(e)}"
            print(f"Error details: {e}")  # Debug output
            messagebox.showerror("Error", error_msg)
            self.log_message(f"❌ Error scanning directory: {str(e)}")
            
            # Additional debug information
            if hasattr(e, '__traceback__'):
                import traceback
                traceback.print_exc()  # Print full traceback for debugging
    
    def get_selected_extensions(self):
        """Get list of selected file extensions"""
        extensions = []
        if self.ext_pdf.get():
            extensions.extend(['.pdf'])
        if self.ext_html.get():
            extensions.extend(['.html', '.htm'])
        if self.ext_txt.get():
            extensions.extend(['.txt'])
        if self.ext_docx.get():
            extensions.extend(['.docx'])
        if self.ext_json.get():
            extensions.extend(['.json'])
        return extensions
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        # Clean emoji characters for better compatibility
        safe_message = self._sanitize_message(message)
        log_entry = f"[{timestamp}] {safe_message}\n"
        
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')
    
    def _sanitize_message(self, message):
        """Replace problematic characters for better encoding compatibility"""
        emoji_replacements = {
            '🚀': '[START]',
            '✅': '[OK]',
            '❌': '[ERROR]',
            '📄': '[FILE]',
            '🤖': '[LLM]',
            '🎓': '[ACADEMIC]',
            '📁': '[FOLDER]',
            '📊': '[STATS]',
            '⚠️': '[WARNING]',
            '💡': '[INFO]',
            '🎉': '[SUCCESS]',
            '🔍': '[SEARCH]',
            '⏱️': '[TIME]',
            '🚨': '[ALERT]'
        }
        
        safe_message = message
        for emoji, replacement in emoji_replacements.items():
            safe_message = safe_message.replace(emoji, replacement)
        
        return safe_message
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
    
    def save_log(self):
        """Save log to file"""
        try:
            content = self.log_text.get(1.0, tk.END)
            if not content.strip():
                messagebox.showinfo("Info", "No log content to save.")
                return
            
            file_path = filedialog.asksaveasfilename(
                title="Save Log File",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            
            if file_path:
                # Sanitize content for safe saving
                safe_content = self._sanitize_message(content)
                with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(safe_content)
                messagebox.showinfo("Success", f"Log saved to: {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save log: {str(e)}")
    
    def start_processing(self):
        """Start batch processing in background thread"""
        if self.is_processing:
            messagebox.showwarning("Warning", "Processing is already running.")
            return
        
        # Validate inputs
        if not self.input_directory.get():
            messagebox.showerror("Error", "Please select an input directory.")
            return
        
        extensions = self.get_selected_extensions()
        if not extensions:
            messagebox.showerror("Error", "Please select at least one file type to process.")
            return
        
        # Disable start button, enable stop button
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.is_processing = True
        
        # Reset progress bars and status
        self.overall_progress['value'] = 0
        self.current_progress['value'] = 0
        self.current_progress.stop()
        self.status_label.config(text="Initializing...")
        self.file_status_label.config(text="")
        
        # Reset statistics
        for key in self.stats_labels:
            self.stats_labels[key].config(text="-")
        
        # Clear previous results
        self.clear_log()
        self.results_text.config(state='normal')
        self.results_text.delete(1.0, tk.END)
        self.results_text.config(state='disabled')
        
        # Start processing thread
        self.processing_thread = threading.Thread(target=self.run_batch_processing, daemon=True)
        self.processing_thread.start()
        
        self.log_message("🚀 Starting batch processing...")
        self.status_bar.config(text="Processing...")
    
    def run_batch_processing(self):
        """Run batch processing in background thread"""
        try:
            # Send initial status
            self.queue.put(('status', '🚀 Initializing batch processor...'))
            
            # Initialize processor
            self.processor = BatchProcessor(
                max_workers=self.max_workers.get(),
                use_multiprocessing=self.use_multiprocessing.get(),
                output_directory=Path(self.output_directory.get())
            )
            
            # Always use Enhanced Academic Processing (LLM + Google Translate)
            self.queue.put(('status', 'Initializing Enhanced Academic processor...'))
            
            try:
                from src.gui.enhanced_academic_processor import create_enhanced_academic_processing_function
                processing_function = create_enhanced_academic_processing_function()
                self.queue.put(('status', 'Enhanced Academic processor loaded'))
            except ImportError as e:
                self.queue.put(('error', f'Enhanced Academic processor not available: {e}'))
                return
            
            self.queue.put(('log', f'Using Enhanced Academic Processing (LLM + Google Translate)'))
            
            # Send progress update
            self.queue.put(('status', 'Scanning directory for files...'))
            
            # Get file list first to send progress updates
            directory = Path(self.input_directory.get())
            extensions = self.get_selected_extensions()
            
            # Scan files manually to get count
            from batch_processing.file_scanner import FileScanner
            scanner = FileScanner()
            categorized_files = scanner.scan_directory(directory)
            
            files_to_process = scanner.scanned_files
            if extensions:
                files_to_process = [
                    f for f in files_to_process 
                    if f.path.suffix.lower() in extensions
                ]
            
            if not files_to_process:
                self.queue.put(('error', 'No supported files found to process'))
                return
            
            total_files = len(files_to_process)
            processed_files = 0
            
            # Send initial progress
            self.queue.put(('progress', {
                'current': 0,
                'total': total_files
            }))
            
            # Send initial stats
            self.queue.put(('stats', {
                'total_files': total_files,
                'completed': 0,
                'failed': 0,
                'success_rate': 0.0,
                'speed': 0.0,
                'eta': '00:00:00'
            }))
            
            # Custom wrapper to track progress
            start_time = time.time()
            successful_files = 0
            failed_files = 0
            
            def progress_wrapper(original_func):
                def wrapper(*args, **kwargs):
                    nonlocal processed_files, successful_files, failed_files
                    
                    # Get file path from arguments
                    file_path = args[0] if args else kwargs.get('file_path', 'Unknown file')
                    
                    # Send current file status
                    self.queue.put(('status', f'📄 Processing: {Path(file_path).name}'))
                    self.queue.put(('progress', {
                        'current': processed_files,
                        'total': total_files,
                        'current_file': Path(file_path).name
                    }))
                    
                    # Process file
                    result = original_func(*args, **kwargs)
                    
                    # Update counters
                    processed_files += 1
                    # Check for success: either dict with "processing_status": "Success" or non-None result
                    if (isinstance(result, dict) and result.get('processing_status') == 'Success') or \
                       (result is not None and not isinstance(result, dict)):
                        successful_files += 1
                    else:
                        failed_files += 1
                    
                    # Calculate statistics
                    elapsed_time = time.time() - start_time
                    speed = processed_files / (elapsed_time / 60) if elapsed_time > 0 else 0
                    success_rate = (successful_files / processed_files * 100) if processed_files > 0 else 0
                    
                    # Estimate remaining time
                    if processed_files > 0 and speed > 0:
                        remaining_files = total_files - processed_files
                        eta_minutes = remaining_files / speed
                        eta_seconds = int(eta_minutes * 60)
                        eta_str = f"{eta_seconds // 3600:02d}:{(eta_seconds % 3600) // 60:02d}:{eta_seconds % 60:02d}"
                    else:
                        eta_str = "Calculating..."
                    
                    # Send progress update
                    self.queue.put(('progress', {
                        'current': processed_files,
                        'total': total_files,
                        'current_file': Path(file_path).name if processed_files < total_files else "Complete"
                    }))
                    
                    # Send stats update
                    self.queue.put(('stats', {
                        'total_files': total_files,
                        'completed': successful_files,
                        'failed': failed_files,
                        'success_rate': success_rate,
                        'speed': speed,
                        'eta': eta_str
                    }))
                    
                    return result
                    
                return wrapper
            
            # Wrap processing function with progress tracking
            wrapped_function = progress_wrapper(processing_function)
            
            # Process directory with wrapped function
            results = self.processor.process_directory(
                directory=directory,
                processing_function=wrapped_function,
                parameters={
                    'language': self.target_language.get(),
                    'max_length': self.max_summary_length.get(),
                    'output_dir': self.output_directory.get(),
                    'auto_detect_language': self.auto_detect_language.get()
                    # Note: LLM usage is handled automatically by Enhanced Academic Processing
                },
                file_extensions=extensions
            )
            
            # Send completion message
            self.queue.put(('complete', results))
            
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n\nTraceback:\n{traceback.format_exc()}"
            self.queue.put(('error', error_msg))
    
    def stop_processing(self):
        """Stop batch processing forcefully"""
        print("🛑 Stop processing requested")
        
        if self.processing_thread and self.processing_thread.is_alive():
            self.log_message("⏹️ Forcefully stopping processing...")
            
            # Set stop flag
            self.is_processing = False
            
            # If processor exists, try to stop it
            if hasattr(self, 'processor') and self.processor:
                try:
                    # Force stop any running tasks
                    if hasattr(self.processor, 'task_manager') and self.processor.task_manager:
                        if hasattr(self.processor.task_manager, 'executor') and self.processor.task_manager.executor:
                            self.processor.task_manager.executor.shutdown(wait=False)
                except Exception as e:
                    print(f"Error stopping processor: {e}")
            
            # Wait briefly for thread to finish, then force terminate
            self.processing_thread.join(timeout=2.0)
            if self.processing_thread.is_alive():
                print("⚠️ Thread did not stop gracefully")
                self.log_message("⚠️ Processing thread did not stop gracefully")
        
        # Reset UI state
        self.is_processing = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_bar.config(text="Stopped")
        self.file_status_label.config(text="Processing stopped")
        
        # Reset progress bars
        self.overall_progress['value'] = 0
        self.current_progress['value'] = 0
        self.current_progress.stop()
        
        print("✅ Stop processing completed")
    
    def check_queue(self):
        """Check for messages from processing thread"""
        try:
            while True:
                msg_type, data = self.queue.get_nowait()
                
                if msg_type == 'status':
                    self.file_status_label.config(text=data)
                    self.log_message(data)
                
                elif msg_type == 'progress':
                    # Update overall progress bar
                    if 'current' in data and 'total' in data:
                        current = data['current']
                        total = data['total']
                        percentage = (current / total * 100) if total > 0 else 0
                        self.overall_progress['value'] = percentage
                        
                        # Update status label
                        status_text = f"Processing file {current}/{total} ({percentage:.1f}%)"
                        self.status_label.config(text=status_text)
                        
                        # Update current file display
                        if 'current_file' in data:
                            self.file_status_label.config(text=f"📄 Current: {data['current_file']}")
                        
                        # Start current file progress animation if processing
                        if current < total:
                            self.current_progress.start(10)
                        else:
                            self.current_progress.stop()
                            self.current_progress['value'] = 100
                
                elif msg_type == 'stats':
                    # Update statistics display
                    if 'total_files' in data:
                        self.stats_labels['total_files'].config(text=str(data['total_files']))
                    if 'completed' in data:
                        self.stats_labels['completed'].config(text=str(data['completed']))
                    if 'failed' in data:
                        self.stats_labels['failed'].config(text=str(data['failed']))
                    if 'success_rate' in data:
                        self.stats_labels['success_rate'].config(text=f"{data['success_rate']:.1f}%")
                    if 'speed' in data:
                        self.stats_labels['speed'].config(text=f"{data['speed']:.1f} files/min")
                    if 'eta' in data:
                        self.stats_labels['eta'].config(text=str(data['eta']))
                
                elif msg_type == 'complete':
                    self.handle_processing_complete(data)
                
                elif msg_type == 'error':
                    self.handle_processing_error(data)
        
        except queue.Empty:
            pass
        
        # Schedule next check
        if hasattr(self, 'root') and self.root.winfo_exists():
            self.root.after(100, self.check_queue)
    
    def handle_processing_complete(self, results):
        """Handle processing completion"""
        self.is_processing = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_bar.config(text="Processing completed")
        
        # Update progress bars to 100%
        self.overall_progress['value'] = 100
        self.current_progress.stop()
        self.current_progress['value'] = 100
        self.status_label.config(text="Processing completed (100%)")
        self.file_status_label.config(text="✅ All files processed")
        
        # Update results display
        self.results_text.config(state='normal')
        
        if results['status'] == 'completed':
            summary = f"""[OK] Batch Processing Completed Successfully!

[STATS] Summary:
• Total Files: {results['total_files']}
• Successful: {results['successful_files']}
• Failed: {results['failed_files']}
• Success Rate: {results['success_rate']:.1f}%
• Processing Time: {results['processing_time']}

[FILES] Individual Summary Files Created:
Each input file has been processed and individual summary files have been generated.
Location: {self.output_directory.get()}/processed/
Format: {"{filename}_summary_ja.md"}
"""
            
            # Add individual file list if available
            individual_files = results.get('individual_files', [])
            if individual_files:
                summary += f"\nGenerated Files ({len(individual_files)}):\n"
                for filename in individual_files[:10]:  # Show first 10 files
                    summary += f"• {filename}\n"
                if len(individual_files) > 10:
                    summary += f"... and {len(individual_files) - 10} more files\n"
            
            summary += "\n[FOLDER] Reports Generated:\n"
            for format_name, file_path in results.get('report_files', {}).items():
                summary += f"• {format_name}: {file_path}\n"
            
            self.results_text.insert(tk.END, summary)
            self.log_message("[OK] Processing completed successfully!")
            
            # Send email notification if configured
            self._send_batch_completion_email(results)
            
            # Show success message
            messagebox.showinfo("Success", "Batch processing completed successfully!")
        
        else:
            error_summary = f"[ERROR] Processing failed with status: {results['status']}"
            self.results_text.insert(tk.END, error_summary)
            self.log_message(f"[ERROR] Processing failed: {results.get('error', 'Unknown error')}")
        
        self.results_text.config(state='disabled')
        
        # Refresh reports list
        self.refresh_reports()
        
        # Switch to results tab
        self.notebook.select(2)
    
    def handle_processing_error(self, error_msg):
        """Handle processing error"""
        self.is_processing = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.status_bar.config(text="Processing failed")
        
        self.log_message(f"❌ Processing error: {error_msg}")
        messagebox.showerror("Error", f"Processing failed: {error_msg}")
    
    def refresh_reports(self):
        """Refresh the reports list"""
        # Clear existing items
        for item in self.reports_tree.get_children():
            self.reports_tree.delete(item)
        
        try:
            output_path = Path(self.output_directory.get()) / "reports"
            if output_path.exists():
                for file_path in output_path.glob("*"):
                    if file_path.is_file():
                        stats = file_path.stat()
                        size = f"{stats.st_size / 1024:.1f} KB"
                        modified = datetime.fromtimestamp(stats.st_mtime).strftime("%Y-%m-%d %H:%M")
                        file_type = file_path.suffix.upper().lstrip('.')
                        
                        self.reports_tree.insert('', 'end', text=file_path.name, 
                                               values=(file_type, size, modified))
        
        except Exception as e:
            self.log_message(f"❌ Error refreshing reports: {str(e)}")
    
    def open_reports_folder(self):
        """Open the reports folder in file explorer"""
        try:
            output_path = Path(self.output_directory.get()) / "reports"
            if output_path.exists():
                os.startfile(str(output_path))  # Windows
            else:
                messagebox.showinfo("Info", "No reports folder found.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open folder: {str(e)}")
    
    def view_selected_report(self):
        """View the selected report"""
        selection = self.reports_tree.selection()
        if not selection:
            messagebox.showinfo("Info", "Please select a report to view.")
            return
        
        try:
            item = self.reports_tree.item(selection[0])
            filename = item['text']
            file_path = Path(self.output_directory.get()) / "reports" / filename
            
            if file_path.exists():
                if file_path.suffix.lower() == '.html':
                    # Open HTML files in browser
                    webbrowser.open(f"file://{file_path.absolute()}")
                else:
                    # Open other files with default application
                    os.startfile(str(file_path))
            else:
                messagebox.showerror("Error", f"File not found: {file_path}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open report: {str(e)}")


    
    def setup_processed_files_tab(self):
        """Setup processed files viewing tab"""
        processed_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(processed_frame, text="Processed Files")
        
        # Output directory selection
        output_section = ttk.LabelFrame(processed_frame, text="Output Directory", padding="10")
        output_section.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        processed_frame.columnconfigure(0, weight=1)
        
        output_dir_frame = ttk.Frame(output_section)
        output_dir_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        output_dir_frame.columnconfigure(0, weight=1)
        
        # Set default to processed folder with absolute path
        processed_dir = self.project_root / "output" / "batch_gui" / "processed"
        self.output_dir_var = tk.StringVar(value=str(processed_dir))
        self.output_dir_entry = ttk.Entry(output_dir_frame, textvariable=self.output_dir_var, width=60)
        self.output_dir_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_dir_frame, text="📂 Browse", command=self.browse_output_directory).grid(row=0, column=1)
        ttk.Button(output_dir_frame, text="🔄 Refresh", command=self.refresh_processed_files).grid(row=0, column=2, padx=(5, 0))
        ttk.Button(output_dir_frame, text="📁 Processed", command=self.goto_processed_folder).grid(row=0, column=3, padx=(5, 0))
        
        # Processed files list
        files_section = ttk.LabelFrame(processed_frame, text="Processed Files", padding="10")
        files_section.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        processed_frame.rowconfigure(1, weight=1)
        
        # File list with treeview
        tree_frame = ttk.Frame(files_section)
        tree_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_frame.columnconfigure(0, weight=1)
        tree_frame.rowconfigure(0, weight=1)
        files_section.columnconfigure(0, weight=1)
        files_section.rowconfigure(0, weight=1)
        
        self.processed_tree = ttk.Treeview(tree_frame, columns=('size', 'modified', 'type'), height=15)
        self.processed_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Column headers
        self.processed_tree.heading('#0', text='File Name')
        self.processed_tree.heading('size', text='Size')
        self.processed_tree.heading('modified', text='Modified')
        self.processed_tree.heading('type', text='Type')
        
        # Column widths
        self.processed_tree.column('#0', width=300)
        self.processed_tree.column('size', width=80)
        self.processed_tree.column('modified', width=150)
        self.processed_tree.column('type', width=100)
        
        # Scrollbar for tree
        processed_scrollbar = ttk.Scrollbar(tree_frame, orient='vertical', command=self.processed_tree.yview)
        processed_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.processed_tree.configure(yscrollcommand=processed_scrollbar.set)
        
        # Double-click to view file
        self.processed_tree.bind('<Double-1>', self.view_processed_file)
        
        # File content preview
        preview_section = ttk.LabelFrame(processed_frame, text="File Preview", padding="10")
        preview_section.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        processed_frame.rowconfigure(2, weight=1)
        
        self.file_content_text = scrolledtext.ScrolledText(preview_section, height=10, wrap=tk.WORD)
        self.file_content_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        preview_section.columnconfigure(0, weight=1)
        preview_section.rowconfigure(0, weight=1)
        
        # Action buttons
        button_frame = ttk.Frame(processed_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="📖 View Selected", command=self.view_selected_file).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(button_frame, text="📂 Open Folder", command=self.open_output_folder).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(button_frame, text="🗑️ Delete Selected", command=self.delete_selected_file).grid(row=0, column=2, padx=(0, 5))
        
        # Load processed files on startup
        self.refresh_processed_files()
    
    def browse_output_directory(self):
        """Browse for output directory"""
        directory = filedialog.askdirectory(title="Select Output Directory")
        if directory:
            self.output_dir_var.set(directory)
            self.refresh_processed_files()
    
    def goto_processed_folder(self):
        """Go to the processed folder automatically"""
        processed_dir = self.project_root / "output" / "batch_gui" / "processed"
        if processed_dir.exists():
            self.output_dir_var.set(str(processed_dir))
            self.refresh_processed_files()
        else:
            # Create the directory if it doesn't exist
            processed_dir.mkdir(parents=True, exist_ok=True)
            self.output_dir_var.set(str(processed_dir))
            self.refresh_processed_files()
            messagebox.showinfo("Info", f"Created processed folder: {processed_dir}")
    
    def refresh_processed_files(self):
        """Refresh the list of processed files"""
        # Clear existing items
        for item in self.processed_tree.get_children():
            self.processed_tree.delete(item)
        
        output_dir = Path(self.output_dir_var.get())
        if not output_dir.exists():
            return
        
        # Scan for processed files
        supported_extensions = ['.md', '.markdown', '.txt', '.json']
        processed_files = []
        
        for ext in supported_extensions:
            processed_files.extend(output_dir.glob(f'**/*{ext}'))
        
        # Sort by modification time (newest first)
        processed_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # Add to tree
        for file_path in processed_files:
            try:
                stat = file_path.stat()
                size_mb = stat.st_size / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB" if size_mb >= 1 else f"{stat.st_size} B"
                
                modified_time = datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
                file_type = "Summary" if file_path.suffix in ['.md', '.markdown'] else "Data"
                
                self.processed_tree.insert('', 'end', text=file_path.name, 
                                         values=(size_str, modified_time, file_type),
                                         tags=(str(file_path),))
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
    
    def view_processed_file(self, event=None):
        """View selected processed file on double-click"""
        self.view_selected_file()
    
    def view_selected_file(self):
        """View the content of selected file"""
        selection = self.processed_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to view.")
            return
        
        try:
            item = self.processed_tree.item(selection[0])
            print(f"DEBUG: Selected item: {item}")
            
            if not item.get('tags'):
                messagebox.showerror("Error", "No file path found for selected item.")
                return
            
            file_path = Path(item['tags'][0])
            print(f"DEBUG: File path: {file_path}")
            
            if not file_path.exists():
                messagebox.showerror("Error", f"File not found: {file_path}")
                return
            
            # Check if it's a binary file
            if file_path.suffix.lower() in ['.pdf', '.jpg', '.jpeg', '.png', '.gif', '.zip', '.rar', '.7z']:
                messagebox.showinfo("Binary File", f"Cannot display binary file: {file_path.name}\nPlease open it with an appropriate application.")
                return
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Clear and display content
            self.file_content_text.delete(1.0, tk.END)
            self.file_content_text.insert(1.0, content)
            
            # Highlight Japanese text
            self.highlight_japanese_text()
            
            messagebox.showinfo("Success", f"File loaded: {file_path.name}")
            
        except UnicodeDecodeError as e:
            try:
                # Try with different encoding
                with open(file_path, 'r', encoding='cp932') as f:
                    content = f.read()
                self.file_content_text.delete(1.0, tk.END)
                self.file_content_text.insert(1.0, content)
                self.highlight_japanese_text()
                messagebox.showinfo("Success", f"File loaded with CP932 encoding: {file_path.name}")
            except Exception as e2:
                messagebox.showerror("Encoding Error", f"Failed to read file with UTF-8 or CP932 encoding:\n{e2}")
        except Exception as e:
            print(f"DEBUG: Error in view_selected_file: {e}")
            messagebox.showerror("Error", f"Failed to read file: {e}")
    
    def highlight_japanese_text(self):
        """Highlight Japanese text in the preview"""
        content = self.file_content_text.get(1.0, tk.END)
        
        # Configure tags for highlighting
        self.file_content_text.tag_configure("japanese", background="#E8F4FD", foreground="#1976D2")
        
        # Find Japanese characters and highlight
        start_idx = 1.0
        for i, char in enumerate(content):
            if ord(char) >= 0x3040 and ord(char) <= 0x9FAF:  # Japanese character range
                char_idx = f"1.{i}"
                end_idx = f"1.{i+1}"
                self.file_content_text.tag_add("japanese", char_idx, end_idx)
    
    def open_output_folder(self):
        """Open output folder in file explorer"""
        output_dir = Path(self.output_dir_var.get())
        if output_dir.exists():
            if sys.platform == "win32":
                os.startfile(output_dir)
            elif sys.platform == "darwin":
                os.system(f"open '{output_dir}'")
            else:
                os.system(f"xdg-open '{output_dir}'")
        else:
            messagebox.showerror("Error", "Output directory does not exist.")
    
    def delete_selected_file(self):
        """Delete the selected processed file"""
        selection = self.processed_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a file to delete.")
            return
        
        item = self.processed_tree.item(selection[0])
        file_path = Path(item['tags'][0])
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete:\n{file_path.name}?"):
            try:
                file_path.unlink()
                self.refresh_processed_files()
                self.file_content_text.delete(1.0, tk.END)
                messagebox.showinfo("Success", "File deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete file: {e}")
    
    def setup_log_management_tab(self):
        """Setup log management tab"""
        log_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(log_frame, text="Log Management")
        
        # Current log status section
        status_section = ttk.LabelFrame(log_frame, text="Current Log Status", padding="10")
        status_section.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        
        self.log_status_text = scrolledtext.ScrolledText(status_section, height=8, wrap=tk.WORD)
        self.log_status_text.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        status_section.columnconfigure(0, weight=1)
        
        status_button_frame = ttk.Frame(status_section)
        status_button_frame.grid(row=1, column=0, pady=(5, 0))
        
        ttk.Button(status_button_frame, text="🔄 Refresh Status", command=self.refresh_log_status).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(status_button_frame, text="🧹 Run Cleanup Now", command=self.run_log_cleanup).grid(row=0, column=1, padx=(0, 5))
        
        # Log cleaner settings section
        settings_section = ttk.LabelFrame(log_frame, text="Cleanup Settings", padding="10")
        settings_section.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Max age setting
        age_frame = ttk.Frame(settings_section)
        age_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        settings_section.columnconfigure(0, weight=1)
        
        ttk.Label(age_frame, text="Max Age (days):").grid(row=0, column=0, sticky=tk.W)
        self.max_age_var = tk.IntVar(value=30)
        ttk.Spinbox(age_frame, from_=1, to=365, textvariable=self.max_age_var, width=10).grid(row=0, column=1, padx=(5, 0))
        
        # Max file count setting
        count_frame = ttk.Frame(settings_section)
        count_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(count_frame, text="Max File Count:").grid(row=0, column=0, sticky=tk.W)
        self.max_count_var = tk.IntVar(value=100)
        ttk.Spinbox(count_frame, from_=10, to=1000, textvariable=self.max_count_var, width=10).grid(row=0, column=1, padx=(5, 0))
        
        # Max total size setting
        size_frame = ttk.Frame(settings_section)
        size_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(size_frame, text="Max Total Size (MB):").grid(row=0, column=0, sticky=tk.W)
        self.max_size_var = tk.IntVar(value=500)
        ttk.Spinbox(size_frame, from_=50, to=5000, textvariable=self.max_size_var, width=10).grid(row=0, column=1, padx=(5, 0))
        
        # Check interval setting
        interval_frame = ttk.Frame(settings_section)
        interval_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(interval_frame, text="Check Interval (hours):").grid(row=0, column=0, sticky=tk.W)
        self.check_interval_var = tk.IntVar(value=24)
        ttk.Spinbox(interval_frame, from_=1, to=168, textvariable=self.check_interval_var, width=10).grid(row=0, column=1, padx=(5, 0))
        
        # Apply settings button
        ttk.Button(settings_section, text="✅ Apply Settings", command=self.apply_log_settings).grid(row=4, column=0, pady=(10, 0))
        
        # Log directories section
        dirs_section = ttk.LabelFrame(log_frame, text="Monitored Directories", padding="10")
        dirs_section.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.rowconfigure(2, weight=1)
        
        self.log_dirs_listbox = tk.Listbox(dirs_section, height=6)
        self.log_dirs_listbox.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        dirs_section.columnconfigure(0, weight=1)
        dirs_section.rowconfigure(0, weight=1)
        
        dirs_scrollbar = ttk.Scrollbar(dirs_section, orient='vertical', command=self.log_dirs_listbox.yview)
        dirs_scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.log_dirs_listbox.configure(yscrollcommand=dirs_scrollbar.set)
        
        dirs_button_frame = ttk.Frame(dirs_section)
        dirs_button_frame.grid(row=1, column=0, columnspan=2, pady=(5, 0))
        
        ttk.Button(dirs_button_frame, text="➕ Add Directory", command=self.add_log_directory).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(dirs_button_frame, text="➖ Remove Selected", command=self.remove_log_directory).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(dirs_button_frame, text="📂 Open Directory", command=self.open_log_directory).grid(row=0, column=2, padx=(0, 5))
        
        # Load initial status and settings
        self.refresh_log_status()
        self.refresh_log_directories()
    
    def refresh_log_status(self):
        """Refresh log status display"""
        try:
            status = self.log_cleaner.get_status()
            
            status_text = f"""📊 Log File Statistics:
• Total Files: {status['total_files']}
• Total Size: {status['total_size_mb']:.2f} MB
• Oldest File Age: {status['oldest_age_days']:.1f} days

📁 Files by Directory:
"""
            for directory, count in status['directories'].items():
                status_text += f"  • {directory}: {count} files\n"
            
            status_text += f"""
⚙️ Current Settings:
• Max Age: {status['settings']['max_age_days']} days
• Max Files: {status['settings']['max_file_count']}
• Max Size: {status['settings']['max_total_size_mb']} MB
• Check Interval: {status['settings']['check_interval_hours']} hours
• Auto Cleanup: {'✅ Running' if status['is_scheduler_running'] else '❌ Stopped'}

📂 Recent Files:
• Oldest: {status['oldest_file'] or 'None'}
• Newest: {status['newest_file'] or 'None'}
"""
            
            self.log_status_text.delete(1.0, tk.END)
            self.log_status_text.insert(1.0, status_text)
            
        except Exception as e:
            self.log_status_text.delete(1.0, tk.END)
            self.log_status_text.insert(1.0, f"❌ Error getting log status: {e}")
    
    def run_log_cleanup(self):
        """Run log cleanup manually"""
        try:
            self.log_status_text.delete(1.0, tk.END)
            self.log_status_text.insert(1.0, "🧹 Running log cleanup...\n")
            self.log_status_text.update()
            
            results = self.log_cleaner.run_cleanup()
            
            if results['status'] == 'no_files':
                result_text = "📁 No log files found to clean."
            else:
                result_text = f"""✅ Log cleanup completed!

📊 Results:
• Initial files: {results['initial_count']} ({results['initial_size_mb']:.2f} MB)
• Files deleted: {results['total_deleted']}
• Space freed: {results['total_freed_mb']:.2f} MB
• Remaining files: {results['final_count']} ({results['final_size_mb']:.2f} MB)

🧹 Operations performed:
"""
                for operation in results.get('operations', []):
                    result_text += f"  • {operation['criteria'].title()}: {operation['deleted_count']} files ({operation['deleted_size_mb']:.2f} MB)\n"
            
            self.log_status_text.delete(1.0, tk.END)
            self.log_status_text.insert(1.0, result_text)
            
            messagebox.showinfo("Cleanup Complete", f"Deleted {results.get('total_deleted', 0)} files, freed {results.get('total_freed_mb', 0):.2f} MB")
            
        except Exception as e:
            error_text = f"❌ Error during cleanup: {e}"
            self.log_status_text.delete(1.0, tk.END)
            self.log_status_text.insert(1.0, error_text)
            messagebox.showerror("Cleanup Error", str(e))
    
    def apply_log_settings(self):
        """Apply new log cleaner settings"""
        try:
            # Stop current scheduler
            self.log_cleaner.stop_scheduler()
            
            # Update settings
            self.log_cleaner.max_age_days = self.max_age_var.get()
            self.log_cleaner.max_file_count = self.max_count_var.get()
            self.log_cleaner.max_total_size_mb = self.max_size_var.get()
            self.log_cleaner.check_interval_hours = self.check_interval_var.get()
            
            # Restart scheduler
            self.log_cleaner.start_scheduler()
            
            messagebox.showinfo("Settings Applied", "Log cleaner settings have been updated and scheduler restarted.")
            self.refresh_log_status()
            
        except Exception as e:
            messagebox.showerror("Settings Error", f"Failed to apply settings: {e}")
    
    def refresh_log_directories(self):
        """Refresh log directories list"""
        self.log_dirs_listbox.delete(0, tk.END)
        for directory in self.log_cleaner.log_directories:
            self.log_dirs_listbox.insert(tk.END, directory)
    
    def add_log_directory(self):
        """Add a new log directory to monitor"""
        directory = filedialog.askdirectory(title="Select Log Directory to Monitor")
        if directory:
            if directory not in self.log_cleaner.log_directories:
                self.log_cleaner.log_directories.append(directory)
                self.refresh_log_directories()
                self.refresh_log_status()
                messagebox.showinfo("Directory Added", f"Added directory: {directory}")
            else:
                messagebox.showwarning("Duplicate Directory", "This directory is already being monitored.")
    
    def remove_log_directory(self):
        """Remove selected log directory"""
        selection = self.log_dirs_listbox.curselection()
        if selection:
            index = selection[0]
            directory = self.log_cleaner.log_directories[index]
            
            if messagebox.askyesno("Remove Directory", f"Stop monitoring directory:\n{directory}?"):
                del self.log_cleaner.log_directories[index]
                self.refresh_log_directories()
                self.refresh_log_status()
                messagebox.showinfo("Directory Removed", f"Removed: {directory}")
        else:
            messagebox.showwarning("No Selection", "Please select a directory to remove.")
    
    def open_log_directory(self):
        """Open selected log directory in file explorer"""
        selection = self.log_dirs_listbox.curselection()
        if selection:
            index = selection[0]
            directory = Path(self.log_cleaner.log_directories[index])
            
            if directory.exists():
                if sys.platform == "win32":
                    os.startfile(directory)
                elif sys.platform == "darwin":
                    os.system(f"open '{directory}'")
                else:
                    os.system(f"xdg-open '{directory}'")
            else:
                messagebox.showerror("Directory Not Found", f"Directory does not exist: {directory}")
        else:
            messagebox.showwarning("No Selection", "Please select a directory to open.")

    def _send_batch_completion_email(self, results):
        """Send email notification for batch processing completion with individual file results"""
        try:
            import os
            import yaml
            from dotenv import load_dotenv
            from src.utils.email_sender import EnhancedEmailSender
            from pathlib import Path
            
            # Try to load from .env.email first, then fall back to .env
            env_email_path = Path(".env.email")
            if env_email_path.exists():
                load_dotenv(env_email_path)
                self.log_message("📧 Loading email configuration from .env.email")
            else:
                load_dotenv()  # Load from .env
                self.log_message("📧 Loading email configuration from .env")
            
            # Try to load from config/email_config.yaml as well
            config_path = Path("config/email_config.yaml")
            email_config = {}
            if config_path.exists():
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        email_config = yaml.safe_load(f)
                    self.log_message("📧 Email config file found and loaded")
                except Exception as e:
                    self.log_message(f"⚠️ Could not load email config: {e}")
            
            # Check if email is configured from environment variables
            recipient_email = os.getenv("NOTIFICATION_EMAIL")
            sender_email = os.getenv("EMAIL_SENDER") 
            sender_password = os.getenv("EMAIL_PASSWORD")
            
            # If not found in env vars, try from config file
            if email_config and not (recipient_email and sender_email and sender_password):
                email_settings = email_config.get('email', {})
                if email_settings.get('enabled', False):
                    sender_info = email_settings.get('sender', {})
                    sender_email = sender_info.get('email')
                    sender_password = sender_info.get('password')
                    recipient_email = email_settings.get('default_recipient')
                    self.log_message("📧 Using email configuration from config file")
            
            if not (recipient_email and sender_email and sender_password):
                self.log_message("📧 Email notification not configured - skipping")
                self.log_message("   Please configure email in .env.email or config/email_config.yaml")
                return
            
            self.log_message(f"📧 Sending batch completion email to {recipient_email}")
            
            # Get list of processed files for proper file naming
            output_dir = Path(self.output_directory.get()) / "processed"
            processed_files = []
            
            if output_dir.exists():
                summary_files = list(output_dir.glob("*_summary_ja.md"))
                for summary_file in summary_files:
                    original_name = summary_file.stem.replace('_summary_ja', '')
                    processed_files.append({
                        'original_name': original_name,
                        'summary_file': summary_file
                    })
            
            # Use the first processed file name for email subject, or batch info if multiple
            if len(processed_files) == 1:
                main_file_name = processed_files[0]['original_name']
                email_file_path = Path(f"{main_file_name}.pdf")  # Assume PDF for subject
            else:
                main_file_name = f"Batch_{len(processed_files)}_files"
                email_file_path = Path(f"Batch_{len(processed_files)}_files")
            
            # Create enhanced batch processing summary with actual file results
            batch_summary = self._create_enhanced_batch_summary_with_files(results, processed_files)
            
            # Create processing metrics
            processing_metrics = {
                "total_files": results['total_files'],
                "successful_files": results['successful_files'],
                "failed_files": results['failed_files'],
                "success_rate": results['success_rate'],
                "processing_time": str(results['processing_time']),
                "processing_type": "Enhanced Batch Processing",
                "output_directory": str(self.output_directory.get()),
                "processed_files": [f['original_name'] for f in processed_files]
            }
            
            # Use enhanced email sender directly for better control
            email_sender = EnhancedEmailSender()
            email_sender.configure_email(sender_email, sender_password)
            
            # Send email notification with enhanced content and file attachments
            success = email_sender.send_batch_summary_with_attachments(
                recipient_email=recipient_email,
                file_path=email_file_path,
                summary_content=batch_summary,
                processing_metrics=processing_metrics,
                processed_files=processed_files
            )
            
            if success:
                self.log_message(f"✅ Enhanced batch completion email sent successfully to {recipient_email}")
            else:
                self.log_message("❌ Failed to send batch completion email")
                
        except Exception as e:
            self.log_message(f"❌ Error sending batch completion email: {e}")
    
    def _create_enhanced_batch_summary_with_files(self, results, processed_files):
        """Create enhanced batch summary with actual individual file processing results"""
        try:
            # Base batch statistics
            batch_header = f"""==================================================
🎓 ENHANCED BATCH PROCESSING RESULTS
==================================================

📁 Batch Directory: {self.input_directory.get()}
📅 Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 Method: 🤖 LLM + Enhanced Academic Processing
⏱️ Total Processing Time: {results['processing_time']}
📊 Files Processed: {results['successful_files']}/{results['total_files']} (Success Rate: {results['success_rate']:.1f}%)

==================================================
📝 INDIVIDUAL FILE RESULTS
==================================================

"""
            
            # Process each individual file result
            individual_results = []
            
            for file_info in processed_files:
                try:
                    with open(file_info['summary_file'], 'r', encoding='utf-8') as f:
                        file_content = f.read()
                    
                    # Parse content using enhanced email sender
                    from src.utils.email_sender import EnhancedEmailSender
                    sender = EnhancedEmailSender()
                    parsed = sender._parse_summary_content(file_content)
                    
                    english_summary = parsed.get('english_summary', '')
                    japanese_summary = parsed.get('japanese_summary', '')
                    translation = parsed.get('translation', '')
                    
                    file_result = f"""
📄 File: {file_info['original_name']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 English Summary ({len(english_summary)} characters):
{english_summary}

🌸 Japanese Summary ({len(japanese_summary)} characters):
{japanese_summary}

🌐 Translation Preview ({len(translation)} characters):
{translation}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    individual_results.append(file_result)
                    self.log_message(f"✅ Added to email: {file_info['original_name']} (EN:{len(english_summary)}, JA:{len(japanese_summary)})")
                    
                except Exception as e:
                    self.log_message(f"⚠️ Error reading summary file {file_info['summary_file']}: {e}")
                    # Add error info to results
                    error_result = f"""
📄 File: {file_info['original_name']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ Error reading summary file: {e}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
                    individual_results.append(error_result)
                    continue
            
            # Combine results
            if individual_results:
                combined_results = batch_header + "\n".join(individual_results)
                
                combined_results += f"""

==================================================
🌐 BATCH PROCESSING SUMMARY
==================================================

Enhanced Academic Processing機能により、各ファイルに対して以下の分析が実行されました：
• 📖 技術的新規性分析
• 📝 包括的な英語要約生成
• 🌸 日本語要約作成
• 🌐 完全な日本語翻訳

📁 出力ディレクトリ: {self.output_directory.get()}
📎 添付ファイル: 各ファイルの完全な処理結果

==================================================
📊 PROCESSING METRICS
==================================================

• 📁 Original Files: {results['total_files']} files
• ✅ Successfully Processed: {results['successful_files']} files
• 📈 Processing Success Rate: {results['success_rate']:.1f}%
• ⏱️ Total Processing Time: {results['processing_time']}
• 🚀 Average Time per File: {self._calculate_avg_time_per_file(results)}

=================================================="""
                
                return combined_results
            else:
                # Fallback if no individual results found
                return batch_header + f"""
⚠️ バッチ処理が完了しましたが、個別ファイルの詳細結果を読み込めませんでした。

処理統計:
• 総ファイル数: {results['total_files']}
• 成功: {results['successful_files']}
• 失敗: {results['failed_files']}
• 成功率: {results['success_rate']:.1f}%
• 処理時間: {results['processing_time']}

出力ディレクトリ: {self.output_directory.get()}

Enhanced Academic Processing機能により、各ファイルに対して技術的新規性分析を含む包括的な要約が生成されました。
"""
                
        except Exception as e:
            self.log_message(f"⚠️ Error creating enhanced batch summary: {e}")
            # Fallback to simple summary
            return f"""バッチ処理が完了しました

処理統計:
• 総ファイル数: {results['total_files']}
• 成功: {results['successful_files']}
• 失敗: {results['failed_files']}
• 成功率: {results['success_rate']:.1f}%
• 処理時間: {results['processing_time']}

出力ディレクトリ: {self.output_directory.get()}

Enhanced Academic Processing機能により、各ファイルに対して技術的新規性分析を含む包括的な要約が生成されました。
"""
    
    def _calculate_avg_time_per_file(self, results):
        """Calculate average processing time per file"""
        try:
            time_str = str(results['processing_time'])
            # Parse time string like "0:07:54.423797"
            parts = time_str.split(':')
            if len(parts) >= 3:
                hours = int(parts[0])
                minutes = int(parts[1])
                seconds = float(parts[2])
                total_seconds = hours * 3600 + minutes * 60 + seconds
                avg_seconds = total_seconds / max(results['successful_files'], 1)
                return f"{avg_seconds:.1f}s"
            else:
                return "N/A"
        except Exception:
            return "N/A"
    
    def _create_enhanced_batch_summary(self, results):
        """Create enhanced batch summary with actual file processing results"""
        try:
            # Base batch statistics
            batch_header = f"""==================================================
🎓 ENHANCED BATCH PROCESSING RESULTS
==================================================

📁 Batch Directory: {self.input_directory.get()}
📅 Processed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
🔧 Method: 🤖 LLM + Enhanced Academic Processing
⏱️ Total Processing Time: {results['processing_time']}
📊 Files Processed: {results['successful_files']}/{results['total_files']} (Success Rate: {results['success_rate']:.1f}%)

==================================================
📝 BATCH PROCESSING SUMMARY
==================================================

"""
            
            # Collect individual file results
            individual_results = []
            output_dir = Path(self.output_directory.get()) / "processed"
            
            if output_dir.exists():
                # Find all processed summary files
                summary_files = list(output_dir.glob("*_summary_ja.md"))
                
                for summary_file in summary_files:
                    try:
                        with open(summary_file, 'r', encoding='utf-8') as f:
                            file_content = f.read()
                        
                        # Extract file name from summary
                        file_name = summary_file.stem.replace('_summary_ja', '')
                        
                        # Try to extract sections from individual file results
                        sections = file_content.split('==================================================')
                        english_summary = ""
                        japanese_summary = ""
                        
                        for i, section in enumerate(sections):
                            if i > 0 and '📝 ENGLISH SUMMARY' in sections[i-1]:
                                english_summary = section.strip()  # No length limit
                            elif i > 0 and '📝 日本語要約' in sections[i-1]:
                                japanese_summary = section.strip()  # No length limit
                        
                        if english_summary or japanese_summary:
                            file_result = f"""
📄 File: {file_name}
{"📝 English Summary: " + english_summary if english_summary else ""}
{"🌸 Japanese Summary: " + japanese_summary if japanese_summary else ""}
"""
                            individual_results.append(file_result)
                            
                    except Exception as e:
                        self.log_message(f"⚠️ Error reading summary file {summary_file}: {e}")
                        continue
            
            # Combine results
            if individual_results:
                combined_results = batch_header + "\n".join(individual_results)  # Show all files
                # No artificial limit on number of files displayed
                
                combined_results += f"""

==================================================
🌐 PROCESSING DETAILS
==================================================

Enhanced Academic Processing機能により、各ファイルに対して以下の分析が実行されました：
• 技術的新規性分析
• 包括的な英語要約生成
• 日本語要約作成
• 完全な日本語翻訳

出力ディレクトリ: {self.output_directory.get()}

==================================================
📊 PROCESSING METRICS
==================================================

• Original Files: {results['total_files']} files
• Successfully Processed: {results['successful_files']} files
• Processing Success Rate: {results['success_rate']:.1f}%
• Total Processing Time: {results['processing_time']}
• Average Time per File: {float(str(results['processing_time']).split(':')[-1].split('.')[0]) / max(results['successful_files'], 1):.1f}s

=================================================="""
                
                return combined_results
            else:
                # Fallback if no individual results found
                return batch_header + f"""
バッチ処理が完了しましたが、個別ファイルの詳細結果を読み込めませんでした。

処理統計:
• 総ファイル数: {results['total_files']}
• 成功: {results['successful_files']}
• 失敗: {results['failed_files']}
• 成功率: {results['success_rate']:.1f}%
• 処理時間: {results['processing_time']}

出力ディレクトリ: {self.output_directory.get()}

Enhanced Academic Processing機能により、各ファイルに対して技術的新規性分析を含む包括的な要約が生成されました。
"""
                
        except Exception as e:
            self.log_message(f"⚠️ Error creating enhanced batch summary: {e}")
            # Fallback to simple summary
            return f"""バッチ処理が完了しました

処理統計:
• 総ファイル数: {results['total_files']}
• 成功: {results['successful_files']}
• 失敗: {results['failed_files']}
• 成功率: {results['success_rate']:.1f}%
• 処理時間: {results['processing_time']}

出力ディレクトリ: {self.output_directory.get()}

Enhanced Academic Processing機能により、各ファイルに対して技術的新規性分析を含む包括的な要約が生成されました。
"""
            import traceback
            print(f"Email error details: {traceback.format_exc()}")


def main():
    """Main function to run the GUI with proper KeyboardInterrupt handling"""
    try:
        root = tk.Tk()
        
        # Set up KeyboardInterrupt handler for GUI
        def on_ctrl_c():
            print("\n🛑 KeyboardInterrupt detected - closing GUI...")
            try:
                root.quit()
                root.destroy()
            except:
                pass
            sys.exit(0)
        
        # Bind Ctrl+C to the handler
        root.bind('<Control-c>', lambda e: on_ctrl_c())
        
        app = BatchProcessingGUI(root)
        
        # Center window on screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        # Make window visible and start event loop
        root.deiconify()
        root.mainloop()
        
    except KeyboardInterrupt:
        print("\n🛑 KeyboardInterrupt caught in main - shutting down gracefully...")
        try:
            if 'root' in locals():
                root.quit()
                root.destroy()
        except:
            pass
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error in main: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
