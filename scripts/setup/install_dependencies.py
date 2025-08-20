#!/usr/bin/env python3
"""
LocalLLM Project - Automatic Package Installation Script
Automatically installs all required dependencies for the LocalLLM project.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print installation banner"""
    print("=" * 60)
    print("🚀 LocalLLM - Automatic Package Installer")
    print("=" * 60)
    print("📦 Installing all required dependencies...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Error: Python 3.8 or higher is required")
        print(f"   Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def get_pip_command():
    """Get the appropriate pip command"""
    if platform.system() == "Windows":
        return "pip"
    else:
        return "pip3"

def install_package(package_name, pip_cmd):
    """Install a single package"""
    try:
        print(f"📦 Installing {package_name}...")
        result = subprocess.run(
            [pip_cmd, "install", package_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {package_name} installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install {package_name}")
        print(f"   Error: {e.stderr}")
        return False

def main():
    """Main installation function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Required packages (実際のコードベースから抽出)
    required_packages = [
        # Core configuration and validation
        "pydantic>=2.0.0",      # Data validation (config/settings.py)
        "python-dotenv>=1.0.0", # Environment variables
        
        # Logging and progress
        "loguru>=0.7.0",        # Advanced logging
        "tqdm>=4.64.0",         # Progress bars
        "schedule>=1.2.0",      # Task scheduling
        "click>=8.0.0",         # CLI interface
        
        # Web and HTTP
        "requests>=2.28.0",     # HTTP requests
        "beautifulsoup4>=4.11.0", # HTML parsing (bs4)
        "lxml>=4.9.0",          # XML/HTML parser
        "html2text>=2020.1.16", # HTML to text conversion
        
        # Document processing
        "pypdf2>=3.0.0",        # PDF processing (PyPDF2)
        "pdfminer.six>=20220524", # PDF text extraction
        "python-docx>=0.8.11", # Word document processing
        
        # AI and language processing
        "transformers>=4.20.0", # Hugging Face transformers
        "llama-cpp-python>=0.1.0", # LLaMA model support
        "langdetect>=1.0.9",    # Language detection
        
        # System monitoring
        "psutil>=5.9.0",        # System monitoring
        "memory-profiler>=0.60.0", # Memory profiling
    ]
    
    pip_cmd = get_pip_command()
    print(f"🔧 Using pip command: {pip_cmd}")
    print()
    
    # Install packages
    failed_packages = []
    success_count = 0
    
    for package in required_packages:
        if install_package(package, pip_cmd):
            success_count += 1
        else:
            failed_packages.append(package)
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 Installation Summary")
    print("=" * 60)
    print(f"✅ Successfully installed: {success_count}/{len(required_packages)} packages")
    
    if failed_packages:
        print(f"❌ Failed packages: {len(failed_packages)}")
        for package in failed_packages:
            print(f"   - {package}")
        print("\n💡 You can try installing failed packages manually:")
        for package in failed_packages:
            print(f"   {pip_cmd} install {package}")
    else:
        print("🎉 All packages installed successfully!")
    
    print("\n📋 Next steps:")
    print("   1. Run the GUI: python src/gui/batch_gui.py")
    print("   2. Or run CLI: python src/main.py --help")
    print()
    
    return len(failed_packages) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
