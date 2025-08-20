#!/usr/bin/env python3
"""
Modern Themed GUI for LocalLLM Batch Processing
Enhanced version with modern styling, dark theme support, and advanced features
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import sys
import os
from pathlib import Path
from datetime import datetime
import queue
import webbrowser
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    # Try to import ttkbootstrap for modern themes
    import ttkbootstrap as ttk_bootstrap
    from ttkbootstrap.constants import *
    BOOTSTRAP_AVAILABLE = True
except ImportError:
    BOOTSTRAP_AVAILABLE = False

from batch_processing.batch_processor import BatchProcessor
from batch_processing.file_scanner import FileScanner


class ModernBatchGUI:
    """
    Modern themed GUI for LocalLLM Batch Processing with enhanced UX
    """
    
    def __init__(self):
        # Initialize root window
        if BOOTSTRAP_AVAILABLE:
            # Use modern bootstrap theme
            self.root = ttk_bootstrap.Window(
                title="🚀 LocalLLM Batch Processor Pro",
                themename="superhero",  # Dark modern theme
                size=(1200, 800),
                minsize=(900, 600)
            )
        else:
            # Fallback to standard tkinter
            self.root = tk.Tk()
            self.root.title("🚀 LocalLLM Batch Processor Pro")
            self.root.geometry("1200x800")
            self.root.minsize(900, 600)
            
            # Apply modern styling
            self.style = ttk.Style()
            self.style.theme_use('clam')
        
        # Application state
        self.processor = None
        self.processing_thread = None
        self.is_processing = False
        self.queue = queue.Queue()
        self.current_session = None
        
        # Configuration variables
        self.setup_variables()
        
        # Create the UI
        self.setup_modern_ui()
        
        # Start monitoring
        self.root.after(100, self.check_queue)
        
        # Apply custom styling
        self.apply_custom_styles()
    
    def setup_variables(self):
        """Initialize all tkinter variables"""
        self.input_directory = tk.StringVar()
        self.output_directory = tk.StringVar(value="output/batch_gui_pro")
        self.max_workers = tk.IntVar(value=4)
        self.use_multiprocessing = tk.BooleanVar(value=True)
        self.continue_on_error = tk.BooleanVar(value=True)
        self.target_language = tk.StringVar(value="ja")
        self.max_summary_length = tk.IntVar(value=200)
        
        # File type variables
        self.file_types = {
            'pdf': tk.BooleanVar(value=True),
            'html': tk.BooleanVar(value=True),
            'txt': tk.BooleanVar(value=True),
            'docx': tk.BooleanVar(value=False),
            'md': tk.BooleanVar(value=False)
        }
        
        # Theme variables
        self.dark_mode = tk.BooleanVar(value=True)
        self.auto_scroll = tk.BooleanVar(value=True)
        self.save_settings = tk.BooleanVar(value=True)
    
    def setup_modern_ui(self):
        """Setup the modern user interface"""
        # Main container
        if BOOTSTRAP_AVAILABLE:
            main_frame = ttk_bootstrap.Frame(self.root, padding=15, bootstyle="dark")
        else:
            main_frame = ttk.Frame(self.root, padding=15)
        
        main_frame.pack(fill='both', expand=True)
        
        # Header section
        self.create_header(main_frame)
        
        # Create main content area with sidebar
        self.create_main_content(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
    
    def create_header(self, parent):
        """Create modern header with branding and controls"""
        if BOOTSTRAP_AVAILABLE:
            header_frame = ttk_bootstrap.Frame(parent, bootstyle="primary")
        else:
            header_frame = ttk.Frame(parent)
        header_frame.pack(fill='x', pady=(0, 20))
        
        # Title and logo
        title_frame = ttk.Frame(header_frame)
        title_frame.pack(side='left', fill='x', expand=True)
        
        if BOOTSTRAP_AVAILABLE:
            title_label = ttk_bootstrap.Label(
                title_frame, 
                text="🚀 LocalLLM Batch Processor Pro",
                font=('Segoe UI', 18, 'bold'),
                bootstyle="inverse-primary"
            )
        else:
            title_label = ttk.Label(
                title_frame,
                text="🚀 LocalLLM Batch Processor Pro",
                font=('Segoe UI', 18, 'bold')
            )
        title_label.pack(side='left')
        
        # Version and status
        if BOOTSTRAP_AVAILABLE:
            version_label = ttk_bootstrap.Label(
                title_frame,
                text="v2.0.0 • Advanced Batch Processing",
                font=('Segoe UI', 9),
                bootstyle="secondary"
            )
        else:
            version_label = ttk.Label(
                title_frame,
                text="v2.0.0 • Advanced Batch Processing",
                font=('Segoe UI', 9)
            )
        version_label.pack(side='left', padx=(15, 0))
        
        # Header controls
        controls_frame = ttk.Frame(header_frame)
        controls_frame.pack(side='right')
        
        # Theme toggle
        if BOOTSTRAP_AVAILABLE:
            theme_btn = ttk_bootstrap.Checkbutton(
                controls_frame,
                text="🌙 Dark Mode",
                variable=self.dark_mode,
                command=self.toggle_theme,
                bootstyle="round-toggle"
            )
        else:
            theme_btn = ttk.Checkbutton(
                controls_frame,
                text="🌙 Dark Mode",
                variable=self.dark_mode,
                command=self.toggle_theme
            )
        theme_btn.pack(side='right', padx=(0, 10))
        
        # Settings button
        if BOOTSTRAP_AVAILABLE:
            settings_btn = ttk_bootstrap.Button(
                controls_frame,
                text="⚙️ Settings",
                command=self.open_settings,
                bootstyle="outline-secondary"
            )
        else:
            settings_btn = ttk.Button(
                controls_frame,
                text="⚙️ Settings",
                command=self.open_settings
            )
        settings_btn.pack(side='right', padx=(0, 10))
    
    def create_main_content(self, parent):
        """Create main content area with sidebar and tabs"""
        content_frame = ttk.Frame(parent)
        content_frame.pack(fill='both', expand=True)
        
        # Create paned window for sidebar and main area
        if BOOTSTRAP_AVAILABLE:
            paned = ttk_bootstrap.Panedwindow(content_frame, orient='horizontal', bootstyle="primary")
        else:
            paned = ttk.Panedwindow(content_frame, orient='horizontal')
        paned.pack(fill='both', expand=True)
        
        # Sidebar for quick controls
        self.create_sidebar(paned)
        
        # Main tab area
        self.create_tab_area(paned)
    
    def create_sidebar(self, parent):
        """Create sidebar with quick controls and statistics"""
        if BOOTSTRAP_AVAILABLE:
            sidebar = ttk_bootstrap.Frame(parent, padding=10, bootstyle="secondary")
        else:
            sidebar = ttk.Frame(parent, padding=10)
        sidebar.pack(fill='y', side='left')
        parent.add(sidebar, weight=0)
        
        # Quick Actions section
        if BOOTSTRAP_AVAILABLE:
            actions_frame = ttk_bootstrap.LabelFrame(sidebar, text="🚀 Quick Actions", padding=10, bootstyle="primary")
        else:
            actions_frame = ttk.LabelFrame(sidebar, text="🚀 Quick Actions", padding=10)
        actions_frame.pack(fill='x', pady=(0, 15))
        
        # Directory selection
        if BOOTSTRAP_AVAILABLE:
            self.dir_button = ttk_bootstrap.Button(
                actions_frame,
                text="📁 Select Folder",
                command=self.browse_input_directory,
                bootstyle="success",
                width=15
            )
        else:
            self.dir_button = ttk.Button(
                actions_frame,
                text="📁 Select Folder",
                command=self.browse_input_directory,
                width=15
            )
        self.dir_button.pack(fill='x', pady=(0, 5))
        
        # Scan files
        if BOOTSTRAP_AVAILABLE:
            self.scan_button = ttk_bootstrap.Button(
                actions_frame,
                text="🔍 Scan Files",
                command=self.scan_files,
                bootstyle="info",
                width=15
            )
        else:
            self.scan_button = ttk.Button(
                actions_frame,
                text="🔍 Scan Files",
                command=self.scan_files,
                width=15
            )
        self.scan_button.pack(fill='x', pady=(0, 5))
        
        # Start processing
        if BOOTSTRAP_AVAILABLE:
            self.start_button = ttk_bootstrap.Button(
                actions_frame,
                text="🚀 Start Processing",
                command=self.start_processing,
                bootstyle="success",
                width=15
            )
        else:
            self.start_button = ttk.Button(
                actions_frame,
                text="🚀 Start Processing",
                command=self.start_processing,
                width=15
            )
        self.start_button.pack(fill='x', pady=(0, 5))
        
        # Stop processing
        if BOOTSTRAP_AVAILABLE:
            self.stop_button = ttk_bootstrap.Button(
                actions_frame,
                text="⏹️ Stop",
                command=self.stop_processing,
                bootstyle="danger",
                state='disabled',
                width=15
            )
        else:
            self.stop_button = ttk.Button(
                actions_frame,
                text="⏹️ Stop",
                command=self.stop_processing,
                state='disabled',
                width=15
            )
        self.stop_button.pack(fill='x')
        
        # Live Statistics
        if BOOTSTRAP_AVAILABLE:
            stats_frame = ttk_bootstrap.LabelFrame(sidebar, text="📊 Live Stats", padding=10, bootstyle="info")
        else:
            stats_frame = ttk.LabelFrame(sidebar, text="📊 Live Stats", padding=10)
        stats_frame.pack(fill='x', pady=(0, 15))
        
        # Statistics display
        self.stats_display = {}
        stats_items = [
            ("📁 Files Found", "files_found", "0"),
            ("✅ Completed", "completed", "0"),
            ("❌ Failed", "failed", "0"),
            ("📈 Success Rate", "success_rate", "0%"),
            ("⚡ Speed", "speed", "0 f/min"),
            ("⏱️ Elapsed", "elapsed", "00:00")
        ]
        
        for i, (label, key, default) in enumerate(stats_items):
            if BOOTSTRAP_AVAILABLE:
                ttk_bootstrap.Label(stats_frame, text=label, font=('Segoe UI', 8, 'bold')).pack(anchor='w')
                self.stats_display[key] = ttk_bootstrap.Label(
                    stats_frame, 
                    text=default, 
                    font=('Segoe UI', 9),
                    bootstyle="primary"
                )
            else:
                ttk.Label(stats_frame, text=label, font=('Segoe UI', 8, 'bold')).pack(anchor='w')
                self.stats_display[key] = ttk.Label(stats_frame, text=default, font=('Segoe UI', 9))
            
            self.stats_display[key].pack(anchor='w', pady=(0, 5))
        
        # Progress indicator
        if BOOTSTRAP_AVAILABLE:
            progress_frame = ttk_bootstrap.LabelFrame(sidebar, text="📊 Progress", padding=10, bootstyle="warning")
        else:
            progress_frame = ttk.LabelFrame(sidebar, text="📊 Progress", padding=10)
        progress_frame.pack(fill='x')
        
        if BOOTSTRAP_AVAILABLE:
            self.sidebar_progress = ttk_bootstrap.Progressbar(
                progress_frame,
                mode='determinate',
                bootstyle="striped",
                length=150
            )
        else:
            self.sidebar_progress = ttk.Progressbar(progress_frame, mode='determinate', length=150)
        self.sidebar_progress.pack(fill='x', pady=(0, 5))
        
        if BOOTSTRAP_AVAILABLE:
            self.progress_label = ttk_bootstrap.Label(progress_frame, text="Ready", font=('Segoe UI', 8))
        else:
            self.progress_label = ttk.Label(progress_frame, text="Ready", font=('Segoe UI', 8))
        self.progress_label.pack()
    
    def create_tab_area(self, parent):
        """Create main tabbed interface"""
        if BOOTSTRAP_AVAILABLE:
            tab_frame = ttk_bootstrap.Frame(parent)
        else:
            tab_frame = ttk.Frame(parent)
        tab_frame.pack(fill='both', expand=True)
        parent.add(tab_frame, weight=1)
        
        # Create notebook
        if BOOTSTRAP_AVAILABLE:
            self.notebook = ttk_bootstrap.Notebook(tab_frame, bootstyle="primary")
        else:
            self.notebook = ttk.Notebook(tab_frame)
        self.notebook.pack(fill='both', expand=True, padx=(10, 0))
        
        # Create tabs
        self.create_configuration_tab()
        self.create_monitoring_tab()
        self.create_results_tab()
        self.create_logs_tab()
    
    def create_configuration_tab(self):
        """Create enhanced configuration tab"""
        if BOOTSTRAP_AVAILABLE:
            config_frame = ttk_bootstrap.Frame(self.notebook, padding=15)
        else:
            config_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(config_frame, text="⚙️ Configuration")
        
        # Input section
        self.create_input_section(config_frame)
        
        # File types section
        self.create_file_types_section(config_frame)
        
        # Processing settings
        self.create_processing_settings(config_frame)
        
        # Output settings
        self.create_output_settings(config_frame)
    
    def create_input_section(self, parent):
        """Create input directory selection section"""
        if BOOTSTRAP_AVAILABLE:
            input_frame = ttk_bootstrap.LabelFrame(parent, text="📁 Input Directory", padding=15, bootstyle="primary")
        else:
            input_frame = ttk.LabelFrame(parent, text="📁 Input Directory", padding=15)
        input_frame.pack(fill='x', pady=(0, 15))
        
        # Directory selection
        dir_select_frame = ttk.Frame(input_frame)
        dir_select_frame.pack(fill='x', pady=(0, 10))
        
        if BOOTSTRAP_AVAILABLE:
            self.dir_entry = ttk_bootstrap.Entry(
                dir_select_frame,
                textvariable=self.input_directory,
                font=('Segoe UI', 10),
                bootstyle="primary"
            )
        else:
            self.dir_entry = ttk.Entry(dir_select_frame, textvariable=self.input_directory, font=('Segoe UI', 10))
        self.dir_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        if BOOTSTRAP_AVAILABLE:
            browse_btn = ttk_bootstrap.Button(
                dir_select_frame,
                text="📂 Browse",
                command=self.browse_input_directory,
                bootstyle="outline-primary"
            )
        else:
            browse_btn = ttk.Button(dir_select_frame, text="📂 Browse", command=self.browse_input_directory)
        browse_btn.pack(side='right')
        
        # File preview area
        if BOOTSTRAP_AVAILABLE:
            preview_label = ttk_bootstrap.Label(input_frame, text="📋 File Preview:", font=('Segoe UI', 9, 'bold'))
        else:
            preview_label = ttk.Label(input_frame, text="📋 File Preview:", font=('Segoe UI', 9, 'bold'))
        preview_label.pack(anchor='w', pady=(0, 5))
        
        self.file_preview = scrolledtext.ScrolledText(
            input_frame,
            height=6,
            font=('Consolas', 9),
            state='disabled',
            wrap=tk.WORD
        )
        self.file_preview.pack(fill='x')
    
    def create_file_types_section(self, parent):
        """Create file types selection section"""
        if BOOTSTRAP_AVAILABLE:
            types_frame = ttk_bootstrap.LabelFrame(parent, text="📄 File Types", padding=15, bootstyle="info")
        else:
            types_frame = ttk.LabelFrame(parent, text="📄 File Types", padding=15)
        types_frame.pack(fill='x', pady=(0, 15))
        
        # File type checkboxes in a grid
        checkbox_frame = ttk.Frame(types_frame)
        checkbox_frame.pack(fill='x')
        
        file_type_info = [
            ("pdf", "📄 PDF Documents", "Process PDF files"),
            ("html", "🌐 HTML Pages", "Process HTML/HTM files"),
            ("txt", "📝 Text Files", "Process plain text files"),
            ("docx", "📋 Word Documents", "Process DOCX files"),
            ("md", "📖 Markdown Files", "Process Markdown files")
        ]
        
        for i, (key, text, tooltip) in enumerate(file_type_info):
            row, col = i // 3, i % 3
            
            if BOOTSTRAP_AVAILABLE:
                cb = ttk_bootstrap.Checkbutton(
                    checkbox_frame,
                    text=text,
                    variable=self.file_types[key],
                    bootstyle="round-toggle"
                )
            else:
                cb = ttk.Checkbutton(checkbox_frame, text=text, variable=self.file_types[key])
            
            cb.grid(row=row, column=col, sticky='w', padx=(0, 20), pady=2)
            
            # Add tooltip (simplified)
            self.create_tooltip(cb, tooltip)
    
    def create_processing_settings(self, parent):
        """Create processing settings section"""
        if BOOTSTRAP_AVAILABLE:
            settings_frame = ttk_bootstrap.LabelFrame(parent, text="⚡ Processing Settings", padding=15, bootstyle="success")
        else:
            settings_frame = ttk.LabelFrame(parent, text="⚡ Processing Settings", padding=15)
        settings_frame.pack(fill='x', pady=(0, 15))
        
        # Settings grid
        settings_grid = ttk.Frame(settings_frame)
        settings_grid.pack(fill='x')
        
        # Max Workers
        ttk.Label(settings_grid, text="👥 Max Workers:", font=('Segoe UI', 9, 'bold')).grid(row=0, column=0, sticky='w', pady=5)
        
        worker_frame = ttk.Frame(settings_grid)
        worker_frame.grid(row=0, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        if BOOTSTRAP_AVAILABLE:
            worker_scale = ttk_bootstrap.Scale(
                worker_frame,
                from_=1, to=16,
                variable=self.max_workers,
                orient='horizontal',
                bootstyle="primary"
            )
        else:
            worker_scale = ttk.Scale(worker_frame, from_=1, to=16, variable=self.max_workers, orient='horizontal')
        worker_scale.pack(side='left', fill='x', expand=True)
        
        if BOOTSTRAP_AVAILABLE:
            worker_label = ttk_bootstrap.Label(worker_frame, textvariable=self.max_workers, width=3, bootstyle="primary")
        else:
            worker_label = ttk.Label(worker_frame, textvariable=self.max_workers, width=3)
        worker_label.pack(side='right', padx=(10, 0))
        
        settings_grid.columnconfigure(1, weight=1)
        
        # Processing mode
        ttk.Label(settings_grid, text="🔧 Processing Mode:", font=('Segoe UI', 9, 'bold')).grid(row=1, column=0, sticky='w', pady=5)
        
        mode_frame = ttk.Frame(settings_grid)
        mode_frame.grid(row=1, column=1, sticky='w', padx=(10, 0), pady=5)
        
        if BOOTSTRAP_AVAILABLE:
            ttk_bootstrap.Checkbutton(
                mode_frame,
                text="Multiprocessing",
                variable=self.use_multiprocessing,
                bootstyle="round-toggle"
            ).pack(side='left', padx=(0, 15))
            
            ttk_bootstrap.Checkbutton(
                mode_frame,
                text="Continue on Error",
                variable=self.continue_on_error,
                bootstyle="round-toggle"
            ).pack(side='left')
        else:
            ttk.Checkbutton(mode_frame, text="Multiprocessing", variable=self.use_multiprocessing).pack(side='left', padx=(0, 15))
            ttk.Checkbutton(mode_frame, text="Continue on Error", variable=self.continue_on_error).pack(side='left')
        
        # Language settings
        ttk.Label(settings_grid, text="🌐 Target Language:", font=('Segoe UI', 9, 'bold')).grid(row=2, column=0, sticky='w', pady=5)
        
        if BOOTSTRAP_AVAILABLE:
            lang_combo = ttk_bootstrap.Combobox(
                settings_grid,
                textvariable=self.target_language,
                values=['ja', 'en', 'zh', 'ko', 'es', 'fr', 'de'],
                state='readonly',
                width=15,
                bootstyle="primary"
            )
        else:
            lang_combo = ttk.Combobox(
                settings_grid,
                textvariable=self.target_language,
                values=['ja', 'en', 'zh', 'ko', 'es', 'fr', 'de'],
                state='readonly',
                width=15
            )
        lang_combo.grid(row=2, column=1, sticky='w', padx=(10, 0), pady=5)
        
        # Summary length
        ttk.Label(settings_grid, text="📏 Summary Length:", font=('Segoe UI', 9, 'bold')).grid(row=3, column=0, sticky='w', pady=5)
        
        length_frame = ttk.Frame(settings_grid)
        length_frame.grid(row=3, column=1, sticky='ew', padx=(10, 0), pady=5)
        
        if BOOTSTRAP_AVAILABLE:
            length_scale = ttk_bootstrap.Scale(
                length_frame,
                from_=50, to=500,
                variable=self.max_summary_length,
                orient='horizontal',
                bootstyle="warning"
            )
        else:
            length_scale = ttk.Scale(length_frame, from_=50, to=500, variable=self.max_summary_length, orient='horizontal')
        length_scale.pack(side='left', fill='x', expand=True)
        
        if BOOTSTRAP_AVAILABLE:
            length_label = ttk_bootstrap.Label(length_frame, textvariable=self.max_summary_length, width=4, bootstyle="warning")
        else:
            length_label = ttk.Label(length_frame, textvariable=self.max_summary_length, width=4)
        length_label.pack(side='right', padx=(10, 0))
    
    def create_output_settings(self, parent):
        """Create output settings section"""
        if BOOTSTRAP_AVAILABLE:
            output_frame = ttk_bootstrap.LabelFrame(parent, text="📁 Output Settings", padding=15, bootstyle="warning")
        else:
            output_frame = ttk.LabelFrame(parent, text="📁 Output Settings", padding=15)
        output_frame.pack(fill='x')
        
        # Output directory
        dir_frame = ttk.Frame(output_frame)
        dir_frame.pack(fill='x', pady=(0, 10))
        
        if BOOTSTRAP_AVAILABLE:
            output_entry = ttk_bootstrap.Entry(
                dir_frame,
                textvariable=self.output_directory,
                font=('Segoe UI', 10),
                bootstyle="warning"
            )
        else:
            output_entry = ttk.Entry(dir_frame, textvariable=self.output_directory, font=('Segoe UI', 10))
        output_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        if BOOTSTRAP_AVAILABLE:
            browse_out_btn = ttk_bootstrap.Button(
                dir_frame,
                text="📂 Browse",
                command=self.browse_output_directory,
                bootstyle="outline-warning"
            )
        else:
            browse_out_btn = ttk.Button(dir_frame, text="📂 Browse", command=self.browse_output_directory)
        browse_out_btn.pack(side='right')
        
        # Output options
        options_frame = ttk.Frame(output_frame)
        options_frame.pack(fill='x')
        
        if BOOTSTRAP_AVAILABLE:
            ttk_bootstrap.Checkbutton(
                options_frame,
                text="💾 Auto-save Settings",
                variable=self.save_settings,
                bootstyle="round-toggle"
            ).pack(side='left', padx=(0, 15))
            
            ttk_bootstrap.Checkbutton(
                options_frame,
                text="📜 Auto-scroll Log",
                variable=self.auto_scroll,
                bootstyle="round-toggle"
            ).pack(side='left')
        else:
            ttk.Checkbutton(options_frame, text="💾 Auto-save Settings", variable=self.save_settings).pack(side='left', padx=(0, 15))
            ttk.Checkbutton(options_frame, text="📜 Auto-scroll Log", variable=self.auto_scroll).pack(side='left')
    
    def create_monitoring_tab(self):
        """Create real-time monitoring tab"""
        if BOOTSTRAP_AVAILABLE:
            monitor_frame = ttk_bootstrap.Frame(self.notebook, padding=15)
        else:
            monitor_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(monitor_frame, text="📊 Monitoring")
        
        # Progress section
        self.create_progress_section(monitor_frame)
        
        # Statistics section
        self.create_statistics_section(monitor_frame)
        
        # Current file section
        self.create_current_file_section(monitor_frame)
    
    def create_progress_section(self, parent):
        """Create progress monitoring section"""
        if BOOTSTRAP_AVAILABLE:
            progress_frame = ttk_bootstrap.LabelFrame(parent, text="📈 Progress Overview", padding=15, bootstyle="primary")
        else:
            progress_frame = ttk.LabelFrame(parent, text="📈 Progress Overview", padding=15)
        progress_frame.pack(fill='x', pady=(0, 15))
        
        # Overall progress
        ttk.Label(progress_frame, text="Overall Progress:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        if BOOTSTRAP_AVAILABLE:
            self.main_progress = ttk_bootstrap.Progressbar(
                progress_frame,
                mode='determinate',
                bootstyle="striped-primary",
                length=400
            )
        else:
            self.main_progress = ttk.Progressbar(progress_frame, mode='determinate', length=400)
        self.main_progress.pack(fill='x', pady=(0, 10))
        
        # Current file progress
        ttk.Label(progress_frame, text="Current File:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        
        if BOOTSTRAP_AVAILABLE:
            self.file_progress = ttk_bootstrap.Progressbar(
                progress_frame,
                mode='indeterminate',
                bootstyle="striped-success",
                length=400
            )
        else:
            self.file_progress = ttk.Progressbar(progress_frame, mode='indeterminate', length=400)
        self.file_progress.pack(fill='x')
    
    def create_statistics_section(self, parent):
        """Create detailed statistics section"""
        if BOOTSTRAP_AVAILABLE:
            stats_frame = ttk_bootstrap.LabelFrame(parent, text="📊 Detailed Statistics", padding=15, bootstyle="info")
        else:
            stats_frame = ttk.LabelFrame(parent, text="📊 Detailed Statistics", padding=15)
        stats_frame.pack(fill='x', pady=(0, 15))
        
        # Statistics grid
        stats_grid = ttk.Frame(stats_frame)
        stats_grid.pack(fill='x')
        
        # Create detailed stats display
        self.detailed_stats = {}
        detailed_stats_info = [
            ("📁 Total Files", "total_files", "0"),
            ("✅ Successfully Processed", "success_count", "0"),
            ("❌ Failed Files", "failed_count", "0"),
            ("📈 Success Rate", "success_percentage", "0%"),
            ("⚡ Processing Speed", "processing_speed", "0 files/min"),
            ("📊 Average File Size", "avg_file_size", "0 MB"),
            ("⏱️ Time Elapsed", "time_elapsed", "00:00:00"),
            ("🕐 Estimated Remaining", "time_remaining", "00:00:00"),
            ("💾 Data Processed", "data_processed", "0 MB"),
            ("🔄 Current Worker Count", "active_workers", "0")
        ]
        
        for i, (label, key, default) in enumerate(detailed_stats_info):
            row, col = i // 2, (i % 2) * 2
            
            ttk.Label(stats_grid, text=f"{label}:", font=('Segoe UI', 9, 'bold')).grid(
                row=row, column=col, sticky='w', padx=(0, 10), pady=3
            )
            
            if BOOTSTRAP_AVAILABLE:
                self.detailed_stats[key] = ttk_bootstrap.Label(
                    stats_grid, text=default, font=('Segoe UI', 9), bootstyle="primary"
                )
            else:
                self.detailed_stats[key] = ttk.Label(stats_grid, text=default, font=('Segoe UI', 9))
            
            self.detailed_stats[key].grid(row=row, column=col+1, sticky='w', padx=(0, 40), pady=3)
    
    def create_current_file_section(self, parent):
        """Create current file processing section"""
        if BOOTSTRAP_AVAILABLE:
            current_frame = ttk_bootstrap.LabelFrame(parent, text="📄 Current File Processing", padding=15, bootstyle="success")
        else:
            current_frame = ttk.LabelFrame(parent, text="📄 Current File Processing", padding=15)
        current_frame.pack(fill='both', expand=True)
        
        # Current file info
        if BOOTSTRAP_AVAILABLE:
            self.current_file_label = ttk_bootstrap.Label(
                current_frame,
                text="No file currently being processed",
                font=('Segoe UI', 10, 'bold'),
                bootstyle="success"
            )
        else:
            self.current_file_label = ttk.Label(
                current_frame,
                text="No file currently being processed",
                font=('Segoe UI', 10, 'bold')
            )
        self.current_file_label.pack(anchor='w', pady=(0, 10))
        
        # File details
        details_frame = ttk.Frame(current_frame)
        details_frame.pack(fill='x', pady=(0, 10))
        
        self.file_details = {}
        file_detail_items = [
            ("📁 File Path", "file_path"),
            ("📊 File Size", "file_size"),
            ("🕐 Start Time", "start_time"),
            ("⏱️ Processing Time", "processing_time")
        ]
        
        for i, (label, key) in enumerate(file_detail_items):
            ttk.Label(details_frame, text=f"{label}:", font=('Segoe UI', 9, 'bold')).grid(
                row=i, column=0, sticky='w', pady=2
            )
            
            if BOOTSTRAP_AVAILABLE:
                self.file_details[key] = ttk_bootstrap.Label(
                    details_frame, text="-", font=('Segoe UI', 9), bootstyle="secondary"
                )
            else:
                self.file_details[key] = ttk.Label(details_frame, text="-", font=('Segoe UI', 9))
            
            self.file_details[key].grid(row=i, column=1, sticky='w', padx=(10, 0), pady=2)
        
        # Recent activity
        ttk.Label(current_frame, text="📜 Recent Activity:", font=('Segoe UI', 10, 'bold')).pack(anchor='w', pady=(10, 5))
        
        self.recent_activity = scrolledtext.ScrolledText(
            current_frame,
            height=6,
            font=('Consolas', 8),
            state='disabled',
            wrap=tk.WORD
        )
        self.recent_activity.pack(fill='both', expand=True)
    
    def create_results_tab(self):
        """Create results and reports tab"""
        if BOOTSTRAP_AVAILABLE:
            results_frame = ttk_bootstrap.Frame(self.notebook, padding=15)
        else:
            results_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(results_frame, text="📋 Results")
        
        # Results will be implemented similar to the basic version
        # but with enhanced styling and features
        pass
    
    def create_logs_tab(self):
        """Create logs and debugging tab"""
        if BOOTSTRAP_AVAILABLE:
            logs_frame = ttk_bootstrap.Frame(self.notebook, padding=15)
        else:
            logs_frame = ttk.Frame(self.notebook, padding=15)
        self.notebook.add(logs_frame, text="📜 Logs")
        
        # Enhanced log display with filtering and search
        pass
    
    def create_status_bar(self, parent):
        """Create enhanced status bar"""
        if BOOTSTRAP_AVAILABLE:
            status_frame = ttk_bootstrap.Frame(parent, bootstyle="secondary")
        else:
            status_frame = ttk.Frame(parent)
        status_frame.pack(fill='x', pady=(10, 0))
        
        if BOOTSTRAP_AVAILABLE:
            self.status_label = ttk_bootstrap.Label(
                status_frame,
                text="Ready to process files",
                font=('Segoe UI', 9),
                bootstyle="secondary"
            )
        else:
            self.status_label = ttk.Label(status_frame, text="Ready to process files", font=('Segoe UI', 9))
        self.status_label.pack(side='left', padx=5, pady=5)
        
        # Session info
        if BOOTSTRAP_AVAILABLE:
            self.session_label = ttk_bootstrap.Label(
                status_frame,
                text="No active session",
                font=('Segoe UI', 8),
                bootstyle="secondary"
            )
        else:
            self.session_label = ttk.Label(status_frame, text="No active session", font=('Segoe UI', 8))
        self.session_label.pack(side='right', padx=5, pady=5)
    
    def apply_custom_styles(self):
        """Apply custom styling"""
        if not BOOTSTRAP_AVAILABLE:
            # Apply custom colors and fonts for standard tkinter
            pass
    
    def create_tooltip(self, widget, text):
        """Create a simple tooltip for a widget"""
        def on_enter(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = ttk.Label(tooltip, text=text, background="lightyellow", relief="solid", borderwidth=1)
            label.pack()
            
            widget.tooltip = tooltip
        
        def on_leave(event):
            if hasattr(widget, 'tooltip'):
                widget.tooltip.destroy()
                del widget.tooltip
        
        widget.bind("<Enter>", on_enter)
        widget.bind("<Leave>", on_leave)
    
    # Event handlers and utility methods
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        if BOOTSTRAP_AVAILABLE and hasattr(self.root, 'style'):
            if self.dark_mode.get():
                self.root.style.theme_use('superhero')  # Dark theme
            else:
                self.root.style.theme_use('flatly')  # Light theme
    
    def open_settings(self):
        """Open advanced settings dialog"""
        # This would open a separate settings window
        messagebox.showinfo("Settings", "Advanced settings dialog would open here")
    
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
        # Implementation similar to basic version but with enhanced feedback
        pass
    
    def start_processing(self):
        """Start batch processing"""
        # Implementation with enhanced progress tracking
        pass
    
    def stop_processing(self):
        """Stop batch processing"""
        # Implementation with graceful shutdown
        pass
    
    def check_queue(self):
        """Check for messages from processing thread"""
        # Enhanced queue processing with more message types
        self.root.after(100, self.check_queue)


def main():
    """Main function to run the modern GUI"""
    app = ModernBatchGUI()
    
    # Center window
    app.root.update_idletasks()
    x = (app.root.winfo_screenwidth() // 2) - (app.root.winfo_width() // 2)
    y = (app.root.winfo_screenheight() // 2) - (app.root.winfo_height() // 2)
    app.root.geometry(f"+{x}+{y}")
    
    app.root.mainloop()


if __name__ == "__main__":
    main()
