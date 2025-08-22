#!/usr/bin/env python3
"""Setup script for development environment."""

import subprocess
import sys
from pathlib import Path


def run_command(command: str, check: bool = True):
    """Run a shell command."""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, check=check)
    return result.returncode == 0


def main():
    """Setup development environment."""
    print("Setting up Local LLM Summarizer development environment...")
    
    # Check Python version
    if sys.version_info < (3, 10):
        print("Error: Python 3.10 or higher is required")
        sys.exit(1)
    
    # Create virtual environment if not exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("Creating virtual environment...")
        run_command(f"{sys.executable} -m venv venv")
    
    # Determine activation script based on OS
    if sys.platform == "win32":
        activate_script = "venv\\Scripts\\activate"
        pip_path = "venv\\Scripts\\pip"
    else:
        activate_script = "source venv/bin/activate"
        pip_path = "venv/bin/pip"
    
    # Install dependencies
    print("Installing dependencies...")
    run_command(f"{pip_path} install --upgrade pip")
    run_command(f"{pip_path} install -r requirements.txt")
    run_command(f"{pip_path} install -r requirements-dev.txt")
    
    # Create necessary directories
    directories = ["models", "output", "logs", "data/temp"]
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {directory}")
    
    # Setup pre-commit hooks (if available)
    if run_command(f"{pip_path} show pre-commit", check=False):
        run_command(f"{pip_path} run pre-commit install", check=False)
    
    print("\n" + "="*50)
    print("Setup completed successfully!")
    print("="*50)
    print("\nNext steps:")
    print(f"1. Activate virtual environment: {activate_script}")
    print("2. Download a LLM model to the 'models/' directory")
    print("3. Configure settings in '.env' file")
    print("4. Run tests: pytest")
    print("5. Try the application: python src/main.py --help")
    print("\nFor model download instructions, see README.md")


if __name__ == "__main__":
    main()
