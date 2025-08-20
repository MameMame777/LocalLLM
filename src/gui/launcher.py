#!/usr/bin/env python3
"""
GUI Launcher for LocalLLM Batch Processing
Provides options to launch different GUI interfaces
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys
import subprocess
from pathlib import Path


class GUILauncher:
    """
    Simple launcher for different GUI interfaces
    """
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🚀 LocalLLM GUI Launcher")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Center window
        self.center_window()
        
        # Setup UI
        self.setup_ui()
    
    def center_window(self):
        """Center the window on screen"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (self.root.winfo_width() // 2)
        y = (self.root.winfo_screenheight() // 2) - (self.root.winfo_height() // 2)
        self.root.geometry(f"+{x}+{y}")
    
    def setup_ui(self):
        """Setup the launcher UI"""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="30")
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame,
            text="🚀 LocalLLM Batch Processor",
            font=('Segoe UI', 20, 'bold')
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = ttk.Label(
            main_frame,
            text="Choose your interface:",
            font=('Segoe UI', 12)
        )
        subtitle_label.pack(pady=(0, 30))
        
        # GUI Options
        self.create_gui_options(main_frame)
        
        # Information section
        self.create_info_section(main_frame)
        
        # Footer
        self.create_footer(main_frame)
    
    def create_gui_options(self, parent):
        """Create GUI option buttons"""
        options_frame = ttk.LabelFrame(parent, text="Available Interfaces", padding="20")
        options_frame.pack(fill='x', pady=(0, 20))
        
        # Standard GUI option
        standard_frame = ttk.Frame(options_frame)
        standard_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(
            standard_frame,
            text="📋 Standard GUI",
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w')
        
        ttk.Label(
            standard_frame,
            text="Full-featured interface with all batch processing capabilities",
            font=('Segoe UI', 9),
            foreground='gray'
        ).pack(anchor='w', pady=(0, 5))
        
        ttk.Button(
            standard_frame,
            text="🚀 Launch Standard GUI",
            command=self.launch_standard_gui,
            width=25
        ).pack(anchor='w')
        
        # Separator
        ttk.Separator(options_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Modern GUI option
        modern_frame = ttk.Frame(options_frame)
        modern_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Label(
            modern_frame,
            text="✨ Modern GUI (Experimental)",
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w')
        
        ttk.Label(
            modern_frame,
            text="Enhanced interface with modern styling (requires ttkbootstrap)",
            font=('Segoe UI', 9),
            foreground='gray'
        ).pack(anchor='w', pady=(0, 5))
        
        ttk.Button(
            modern_frame,
            text="✨ Launch Modern GUI",
            command=self.launch_modern_gui,
            width=25
        ).pack(anchor='w')
        
        # Separator
        ttk.Separator(options_frame, orient='horizontal').pack(fill='x', pady=10)
        
        # Command Line option
        cli_frame = ttk.Frame(options_frame)
        cli_frame.pack(fill='x')
        
        ttk.Label(
            cli_frame,
            text="💻 Command Line Interface",
            font=('Segoe UI', 12, 'bold')
        ).pack(anchor='w')
        
        ttk.Label(
            cli_frame,
            text="Direct command-line batch processing",
            font=('Segoe UI', 9),
            foreground='gray'
        ).pack(anchor='w', pady=(0, 5))
        
        ttk.Button(
            cli_frame,
            text="💻 Open CLI Guide",
            command=self.show_cli_info,
            width=25
        ).pack(anchor='w')
    
    def create_info_section(self, parent):
        """Create information section"""
        info_frame = ttk.LabelFrame(parent, text="System Information", padding="15")
        info_frame.pack(fill='x', pady=(0, 20))
        
        # System info
        import platform
        import os
        
        info_text = f"""
🖥️  System: {platform.system()} {platform.release()}
🐍  Python: {platform.python_version()}
📁  Workspace: {Path.cwd().name}
👤  User: {os.getenv('USERNAME', 'Unknown')}
        """.strip()
        
        ttk.Label(info_frame, text=info_text, font=('Consolas', 9)).pack(anchor='w')
    
    def create_footer(self, parent):
        """Create footer with additional options"""
        footer_frame = ttk.Frame(parent)
        footer_frame.pack(fill='x', side='bottom')
        
        # Buttons
        button_frame = ttk.Frame(footer_frame)
        button_frame.pack(side='right')
        
        ttk.Button(
            button_frame,
            text="📖 Documentation",
            command=self.open_documentation
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="⚙️ Settings",
            command=self.open_settings
        ).pack(side='left', padx=(0, 5))
        
        ttk.Button(
            button_frame,
            text="❌ Exit",
            command=self.root.quit
        ).pack(side='left')
    
    def launch_standard_gui(self):
        """Launch the standard GUI"""
        try:
            gui_path = Path(__file__).parent / "batch_gui.py"
            if gui_path.exists():
                subprocess.Popen([sys.executable, str(gui_path)])
                messagebox.showinfo("Success", "Standard GUI launched successfully!")
            else:
                messagebox.showerror("Error", f"GUI file not found: {gui_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch GUI: {str(e)}")
    
    def launch_modern_gui(self):
        """Launch the modern GUI"""
        try:
            # Check if ttkbootstrap is available
            try:
                import ttkbootstrap
                modern_gui_path = Path(__file__).parent / "modern_batch_gui.py"
                if modern_gui_path.exists():
                    subprocess.Popen([sys.executable, str(modern_gui_path)])
                    messagebox.showinfo("Success", "Modern GUI launched successfully!")
                else:
                    messagebox.showerror("Error", f"Modern GUI file not found: {modern_gui_path}")
            except ImportError:
                # Offer to install ttkbootstrap
                result = messagebox.askyesno(
                    "Missing Dependency",
                    "Modern GUI requires 'ttkbootstrap' package.\n\nWould you like to install it now?"
                )
                if result:
                    self.install_ttkbootstrap()
                else:
                    messagebox.showinfo("Info", "Using standard GUI instead...")
                    self.launch_standard_gui()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch modern GUI: {str(e)}")
    
    def install_ttkbootstrap(self):
        """Install ttkbootstrap package"""
        try:
            import subprocess
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", "ttkbootstrap"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                messagebox.showinfo("Success", "ttkbootstrap installed successfully!\nYou can now use the Modern GUI.")
            else:
                messagebox.showerror("Error", f"Installation failed:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to install ttkbootstrap: {str(e)}")
    
    def show_cli_info(self):
        """Show CLI usage information"""
        cli_info = """
Command Line Usage:

🔹 Basic batch processing:
   python src/batch_processing/batch_processor.py data/

🔹 With specific options:
   python src/batch_processing/batch_processor.py data/ --workers 4 --extensions .pdf .html

🔹 Real LLM integration:
   python examples/batch_llm_integration.py

🔹 Available parameters:
   --workers N        Number of worker processes
   --extensions X Y   File extensions to process
   --output DIR       Output directory
   --threading        Use threading instead of multiprocessing

Example:
   python src/batch_processing/batch_processor.py C:/Documents --workers 8 --extensions .pdf .txt --output C:/Output
        """
        
        # Create info window
        info_window = tk.Toplevel(self.root)
        info_window.title("💻 Command Line Usage")
        info_window.geometry("700x500")
        info_window.resizable(False, False)
        
        # Center the window
        info_window.update_idletasks()
        x = (info_window.winfo_screenwidth() // 2) - (info_window.winfo_width() // 2)
        y = (info_window.winfo_screenheight() // 2) - (info_window.winfo_height() // 2)
        info_window.geometry(f"+{x}+{y}")
        
        # Add content
        frame = ttk.Frame(info_window, padding="20")
        frame.pack(fill='both', expand=True)
        
        # Title
        ttk.Label(frame, text="💻 Command Line Interface", font=('Segoe UI', 14, 'bold')).pack(anchor='w', pady=(0, 15))
        
        # Info text
        text_widget = tk.Text(frame, wrap=tk.WORD, font=('Consolas', 10), height=20)
        text_widget.pack(fill='both', expand=True)
        text_widget.insert('1.0', cli_info)
        text_widget.config(state='disabled')
        
        # Close button
        ttk.Button(frame, text="Close", command=info_window.destroy).pack(pady=(15, 0))
    
    def open_documentation(self):
        """Open documentation"""
        try:
            doc_path = Path(__file__).parent.parent.parent / "doc" / "batch_processing_complete.md"
            if doc_path.exists():
                import webbrowser
                webbrowser.open(f"file://{doc_path.absolute()}")
            else:
                messagebox.showinfo("Info", f"Documentation not found at: {doc_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open documentation: {str(e)}")
    
    def open_settings(self):
        """Open settings dialog"""
        messagebox.showinfo("Settings", "Settings dialog would be implemented here.\n\nFor now, you can modify configuration directly in the GUI applications.")
    
    def run(self):
        """Start the launcher"""
        self.root.mainloop()


def main():
    """Main function"""
    launcher = GUILauncher()
    launcher.run()


if __name__ == "__main__":
    main()
