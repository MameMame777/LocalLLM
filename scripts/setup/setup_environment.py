#!/usr/bin/env python3
"""
LocalLLM Project - Environment Setup Script
Sets up a complete development environment with all dependencies.
"""

import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("=" * 70)
    print("🚀 LocalLLM - Complete Environment Setup")
    print("=" * 70)
    print("🏗️  Setting up development environment...")
    print()

def run_command(command, description="", check=True):
    """Run a shell command with error handling"""
    print(f"🔧 {description}")
    try:
        if platform.system() == "Windows":
            result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        else:
            result = subprocess.run(command.split(), check=check, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ {description} - Success")
            return True
        else:
            print(f"❌ {description} - Failed")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Error: Python 3.8+ required. Current: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def setup_virtual_environment():
    """Setup virtual environment"""
    venv_path = Path("venv")
    
    # Remove existing venv if it exists
    if venv_path.exists():
        print("🗑️  Removing existing virtual environment...")
        if platform.system() == "Windows":
            run_command("rmdir /s /q venv", "Removing old venv", check=False)
        else:
            shutil.rmtree(venv_path)
    
    # Create new virtual environment
    if not run_command(f"{sys.executable} -m venv venv", "Creating virtual environment"):
        return False
    
    return True

def install_dependencies():
    """Install all dependencies"""
    if platform.system() == "Windows":
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Upgrade pip first
    if not run_command(f"{python_cmd} -m pip install --upgrade pip", "Upgrading pip"):
        return False
    
    # Install from requirements.txt if it exists
    if Path("requirements.txt").exists():
        if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing from requirements.txt"):
            return False
    
    # Install additional packages that might be missing
    additional_packages = [
        "html2text",
        "pdfminer.six",
        "langdetect",
        "transformers",
    ]
    
    for package in additional_packages:
        run_command(f"{pip_cmd} install {package}", f"Installing {package}", check=False)
    
    return True

def verify_installation():
    """Verify that key packages are installed"""
    if platform.system() == "Windows":
        python_cmd = "venv\\Scripts\\python"
    else:
        python_cmd = "venv/bin/python"
    
    test_script = '''
import sys
packages = [
    "loguru", "tqdm", "schedule", "click", "requests", 
    "bs4", "lxml", "html2text", "PyPDF2", "pdfminer",
    "docx", "transformers", "langdetect", "psutil"
]

success = 0
for pkg in packages:
    try:
        __import__(pkg)
        print(f"✅ {pkg}")
        success += 1
    except ImportError:
        print(f"❌ {pkg}")

print(f"\\n📊 {success}/{len(packages)} packages verified")
'''
    
    print("🔍 Verifying installation...")
    result = subprocess.run([python_cmd, "-c", test_script], capture_output=True, text=True)
    print(result.stdout)
    
    return "✅" in result.stdout

def create_activation_scripts():
    """Create convenient activation scripts"""
    if platform.system() == "Windows":
        # Windows batch script
        batch_content = '''@echo off
echo 🚀 Activating LocalLLM environment...
call venv\\Scripts\\activate.bat
echo ✅ Environment activated!
echo.
echo 📋 Available commands:
echo   python src/gui/batch_gui.py    - Start GUI
echo   python src/main.py --help      - CLI help
echo   python install_dependencies.py - Install missing packages
echo.
'''
        with open("activate.bat", "w") as f:
            f.write(batch_content)
        print("✅ Created activate.bat")
    
    # PowerShell script
    ps1_content = '''Write-Host "🚀 Activating LocalLLM environment..." -ForegroundColor Green
& .\\venv\\Scripts\\Activate.ps1
Write-Host "✅ Environment activated!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Available commands:" -ForegroundColor Yellow
Write-Host "  python src/gui/batch_gui.py    - Start GUI" -ForegroundColor Cyan
Write-Host "  python src/main.py --help      - CLI help" -ForegroundColor Cyan
Write-Host "  python install_dependencies.py - Install missing packages" -ForegroundColor Cyan
Write-Host ""
'''
    with open("activate.ps1", "w") as f:
        f.write(ps1_content)
    print("✅ Created activate.ps1")

def main():
    """Main setup function"""
    print_banner()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Setup virtual environment
    if not setup_virtual_environment():
        print("❌ Failed to setup virtual environment")
        return False
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies")
        return False
    
    # Verify installation
    verify_installation()
    
    # Create activation scripts
    create_activation_scripts()
    
    # Print success message
    print("\n" + "=" * 70)
    print("🎉 Environment Setup Complete!")
    print("=" * 70)
    print("📋 Next steps:")
    
    if platform.system() == "Windows":
        print("   1. Run: activate.bat  (or activate.ps1)")
    else:
        print("   1. Run: source venv/bin/activate")
    
    print("   2. Start GUI: python src/gui/batch_gui.py")
    print("   3. Or CLI: python src/main.py --help")
    print()
    print("💡 If you encounter missing packages, run:")
    print("   python install_dependencies.py")
    print()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
