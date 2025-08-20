#!/usr/bin/env python3
"""
LocalLLM - Quick Start Script
One-click setup and launch for the LocalLLM project
"""

import sys
import subprocess
import platform
from pathlib import Path

def quick_install_missing_packages():
    """Quickly install only the missing essential packages"""
    essential_packages = [
        "pydantic>=2.0.0",     # Core configuration (必須!)
        "pydantic-settings>=2.0.0", # Pydantic settings (必須!)
        "python-dotenv>=1.0.0", # Environment variables (必須!)
        "html2text",           # HTML to text conversion
        "pdfminer.six",        # PDF text extraction
        "langdetect",          # Language detection
        "tqdm",                # Progress bars
        "schedule",            # Task scheduling
        "loguru",              # Advanced logging
        "beautifulsoup4",      # HTML parsing
        "requests",            # HTTP requests
        "pypdf2",              # PDF processing
        "psutil",              # System monitoring
        "memory-profiler",     # Memory profiling
        "transformers",        # AI models (optional but recommended)
    ]
    
    pip_cmd = "pip" if platform.system() == "Windows" else "pip3"
    
    print("🚀 Quick-installing essential packages...")
    success_count = 0
    for package in essential_packages:
        try:
            subprocess.run([pip_cmd, "install", package], 
                         check=True, capture_output=True)
            print(f"✅ {package}")
            success_count += 1
        except subprocess.CalledProcessError:
            print(f"⚠️  {package} (may already be installed)")
    
    print(f"✅ Quick installation complete! ({success_count}/{len(essential_packages)} packages)")

def launch_gui():
    """Launch the GUI application"""
    gui_path = Path("src/gui/batch_gui.py")
    if not gui_path.exists():
        print("❌ GUI file not found. Please run from the project root directory.")
        return False
    
    print("🚀 Launching LocalLLM GUI...")
    try:
        # Try with virtual environment first
        if Path("venv").exists():
            if platform.system() == "Windows":
                python_cmd = "venv\\Scripts\\python"
            else:
                python_cmd = "venv/bin/python"
        else:
            python_cmd = "python"
        
        subprocess.run([python_cmd, str(gui_path)], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch GUI: {e}")
        return False
    except FileNotFoundError:
        print("❌ Python not found. Please check your Python installation.")
        return False

def main():
    """Main function"""
    print("=" * 50)
    print("🚀 LocalLLM - Quick Start")
    print("=" * 50)
    
    # Quick package installation
    quick_install_missing_packages()
    
    print("\n" + "=" * 50)
    
    # Launch GUI
    launch_gui()

if __name__ == "__main__":
    main()
