#!/usr/bin/env python3
"""
Complete Dependency Analysis and Installation Script
Analyzes all Python files to extract ALL dependencies and installs them.
"""

import os
import re
import sys
import subprocess
import platform
from pathlib import Path
from typing import Set, Dict, List

def analyze_all_imports() -> Set[str]:
    """Analyze all Python files and extract ALL import statements"""
    all_imports = set()
    
    # Standard library modules to exclude
    stdlib_modules = {
        'sys', 'os', 'time', 'threading', 'json', 'csv', 'argparse', 'subprocess',
        'datetime', 'pathlib', 'typing', 'dataclasses', 'enum', 'logging', 're',
        'mimetypes', 'traceback', 'queue', 'concurrent', 'multiprocessing', 'urllib',
        'webbrowser', 'collections', 'itertools', 'functools', 'copy', 'hashlib',
        'tkinter', 'abc', 'warnings', 'tempfile', 'shutil', 'random', 'math',
        'socket', 'ssl', 'http', 'email', 'xml', 'html', 'string', 'base64',
        'pickle', 'gzip', 'zipfile', 'tarfile', 'io', 'codecs', 'locale',
        'platform', 'getpass', 'glob', 'fnmatch', 'stat', 'filecmp'
    }
    
    # Scan all Python files
    python_files = []
    for root, dirs, files in os.walk('.'):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in {'__pycache__', '.git', '.pytest_cache', 'node_modules', 'venv', '.venv'}]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    print(f"🔍 Analyzing {len(python_files)} Python files...")
    
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Extract import statements with multiple patterns
            patterns = [
                r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)',
                r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import',
                r'__import__\([\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]',
                r'importlib\.import_module\([\'"]([a-zA-Z_][a-zA-Z0-9_]*)[\'"]'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.MULTILINE)
                for match in matches:
                    # Get the top-level package name
                    top_level = match.split('.')[0]
                    if (top_level not in stdlib_modules and 
                        not top_level.startswith(('src', 'config', 'test', 'tests')) and
                        len(top_level) > 1):  # Skip single-letter imports
                        all_imports.add(top_level)
                        
        except Exception as e:
            print(f"⚠️  Error reading {file_path}: {e}")
    
    return all_imports

def get_package_mapping() -> Dict[str, str]:
    """Map import names to actual package names"""
    return {
        'bs4': 'beautifulsoup4',
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'yaml': 'PyYAML',
        'sklearn': 'scikit-learn',
        'cv': 'opencv-python',
        'dns': 'dnspython',
        'serial': 'pyserial',
        'usb': 'pyusb',
        'win32api': 'pywin32',
        'win32con': 'pywin32',
        'win32gui': 'pywin32',
        'pywintypes': 'pywin32',
        'docx': 'python-docx',
        'openpyxl': 'openpyxl',
        'xlsxwriter': 'XlsxWriter',
        'xlrd': 'xlrd',
        'xlwt': 'xlwt',
        'pydantic_settings': 'pydantic-settings',
        'fastapi': 'fastapi',
        'uvicorn': 'uvicorn',
        'starlette': 'starlette',
        'jinja2': 'Jinja2',
        'markupsafe': 'MarkupSafe',
        'werkzeug': 'Werkzeug',
        'flask': 'Flask',
        'django': 'Django',
        'tornado': 'tornado',
        'aiohttp': 'aiohttp',
        'httpx': 'httpx',
        'websocket': 'websocket-client',
        'websockets': 'websockets',
        'paramiko': 'paramiko',
        'fabric': 'fabric',
        'invoke': 'invoke',
        'click': 'click',
        'typer': 'typer',
        'rich': 'rich',
        'colorama': 'colorama',
        'termcolor': 'termcolor',
        'progressbar': 'progressbar2',
        'tqdm': 'tqdm',
        'alive_progress': 'alive-progress',
        'schedule': 'schedule',
        'croniter': 'croniter',
        'celery': 'celery',
        'redis': 'redis',
        'pymongo': 'pymongo',
        'sqlite3': None,  # Built-in
        'psycopg2': 'psycopg2-binary',
        'MySQLdb': 'mysqlclient',
        'pymysql': 'PyMySQL',
        'sqlalchemy': 'SQLAlchemy',
        'alembic': 'alembic',
        'pandas': 'pandas',
        'numpy': 'numpy',
        'scipy': 'scipy',
        'matplotlib': 'matplotlib',
        'seaborn': 'seaborn',
        'plotly': 'plotly',
        'bokeh': 'bokeh',
        'streamlit': 'streamlit',
        'dash': 'dash',
        'jupyter': 'jupyter',
        'ipython': 'ipython',
        'notebook': 'notebook',
        'jupyterlab': 'jupyterlab',
        'tensorflow': 'tensorflow',
        'torch': 'torch',
        'transformers': 'transformers',
        'datasets': 'datasets',
        'tokenizers': 'tokenizers',
        'accelerate': 'accelerate',
        'diffusers': 'diffusers',
        'llama_cpp': 'llama-cpp-python',
        'openai': 'openai',
        'anthropic': 'anthropic',
        'langchain': 'langchain',
        'chainlit': 'chainlit',
        'gradio': 'gradio',
        'huggingface_hub': 'huggingface-hub',
        'sentence_transformers': 'sentence-transformers',
        'spacy': 'spacy',
        'nltk': 'nltk',
        'textblob': 'textblob',
        'gensim': 'gensim',
        'fuzzywuzzy': 'fuzzywuzzy',
        'Levenshtein': 'python-Levenshtein',
        'langdetect': 'langdetect',
        'polyglot': 'polyglot',
        'googletrans': 'googletrans==4.0.0rc1',
        'translate': 'translate',
        'requests': 'requests',
        'httplib2': 'httplib2',
        'urllib3': 'urllib3',
        'certifi': 'certifi',
        'chardet': 'chardet',
        'idna': 'idna',
        'beautifulsoup4': 'beautifulsoup4',
        'lxml': 'lxml',
        'html5lib': 'html5lib',
        'selectolax': 'selectolax',
        'pyquery': 'pyquery',
        'scrapy': 'scrapy',
        'selenium': 'selenium',
        'playwright': 'playwright',
        'html2text': 'html2text',
        'markdown': 'Markdown',
        'mistune': 'mistune',
        'pypandoc': 'pypandoc',
        'weasyprint': 'weasyprint',
        'reportlab': 'reportlab',
        'fpdf': 'fpdf2',
        'pdfplumber': 'pdfplumber',
        'pymupdf': 'PyMuPDF',
        'fitz': 'PyMuPDF',
        'pdfminer': 'pdfminer.six',
        'PyPDF2': 'pypdf2',
        'PyPDF4': 'PyPDF4',
        'pypdf': 'pypdf',
        'camelot': 'camelot-py',
        'tabula': 'tabula-py',
        'pdfkit': 'pdfkit',
        'wkhtmltopdf': 'pdfkit',
        'python_docx': 'python-docx',
        'python_pptx': 'python-pptx',
        'xlwings': 'xlwings',
        'pyexcel': 'pyexcel',
        'ezodf': 'ezodf',
        'odfpy': 'odfpy',
        'python_magic': 'python-magic',
        'filemagic': 'filemagic',
        'mimetypes': None,  # Built-in
        'zipfile': None,   # Built-in
        'tarfile': None,   # Built-in
        'gzip': None,      # Built-in
        'bz2': None,       # Built-in
        'lzma': None,      # Built-in
        'zstandard': 'zstandard',
        'py7zr': 'py7zr',
        'rarfile': 'rarfile',
        'patool': 'patool',
        'loguru': 'loguru',
        'structlog': 'structlog',
        'colorlog': 'colorlog',
        'python_json_logger': 'python-json-logger',
        'sentry_sdk': 'sentry-sdk',
        'rollbar': 'rollbar',
        'bugsnag': 'bugsnag',
        'psutil': 'psutil',
        'memory_profiler': 'memory-profiler',
        'line_profiler': 'line-profiler',
        'py_spy': 'py-spy',
        'pympler': 'Pympler',
        'objgraph': 'objgraph',
        'guppy': 'guppy3',
        'tracemalloc': None,  # Built-in (Python 3.4+)
        'cProfile': None,     # Built-in
        'profile': None,      # Built-in
        'pstats': None,       # Built-in
        'timeit': None,       # Built-in
        'pytest': 'pytest',
        'unittest': None,     # Built-in
        'nose': 'nose',
        'nose2': 'nose2',
        'testfixtures': 'testfixtures',
        'mock': 'mock',
        'responses': 'responses',
        'httpretty': 'httpretty',
        'vcr': 'vcrpy',
        'betamax': 'betamax',
        'freezegun': 'freezegun',
        'factory_boy': 'factory-boy',
        'faker': 'Faker',
        'hypothesis': 'hypothesis',
        'sure': 'sure',
        'expects': 'expects',
        'assertpy': 'assertpy',
        'hamcrest': 'PyHamcrest',
        'pydantic': 'pydantic',
        'marshmallow': 'marshmallow',
        'cerberus': 'Cerberus',
        'voluptuous': 'voluptuous',
        'schema': 'schema',
        'jsonschema': 'jsonschema',
        'attrs': 'attrs',
        'cattrs': 'cattrs',
        'dataclasses_json': 'dataclasses-json',
        'typing_extensions': 'typing-extensions',
        'mypy': 'mypy',
        'pyright': 'pyright',
        'pyre': 'pyre-check',
        'pyflakes': 'pyflakes',
        'pylint': 'pylint',
        'flake8': 'flake8',
        'bandit': 'bandit',
        'safety': 'safety',
        'black': 'black',
        'isort': 'isort',
        'autopep8': 'autopep8',
        'yapf': 'yapf',
        'pycodestyle': 'pycodestyle',
        'pydocstyle': 'pydocstyle',
        'pre_commit': 'pre-commit',
        'tox': 'tox',
        'nox': 'nox',
        'invoke': 'invoke',
        'fabric': 'fabric',
        'doit': 'doit',
        'paver': 'Paver',
        'scons': 'SCons',
        'waf': 'waflib',
        'setuptools': 'setuptools',
        'distutils': None,    # Built-in (deprecated)
        'pip': 'pip',
        'pipenv': 'pipenv',
        'poetry': 'poetry',
        'conda': 'conda',
        'virtualenv': 'virtualenv',
        'virtualenvwrapper': 'virtualenvwrapper',
        'pyenv': 'pyenv',
        'pipx': 'pipx',
        'wheel': 'wheel',
        'twine': 'twine',
        'build': 'build',
        'flit': 'flit',
        'hatch': 'hatch',
        'pdm': 'pdm',
        'micropipenv': 'micropipenv',
    }

def install_packages(packages: List[str]) -> Dict[str, bool]:
    """Install packages and return success status"""
    pip_cmd = "pip" if platform.system() == "Windows" else "pip3"
    results = {}
    
    print(f"\n🚀 Installing {len(packages)} packages...")
    print("=" * 60)
    
    for i, package in enumerate(packages, 1):
        print(f"[{i}/{len(packages)}] Installing {package}...")
        try:
            result = subprocess.run(
                [pip_cmd, "install", package],
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout per package
            )
            print(f"✅ {package}")
            results[package] = True
        except subprocess.CalledProcessError as e:
            print(f"❌ {package} - Error: {e.stderr}")
            results[package] = False
        except subprocess.TimeoutExpired:
            print(f"⏰ {package} - Timeout")
            results[package] = False
        except Exception as e:
            print(f"💥 {package} - Exception: {e}")
            results[package] = False
    
    return results

def main():
    """Main function"""
    print("=" * 70)
    print("🔍 Complete Dependency Analysis & Installation")
    print("=" * 70)
    
    # Analyze all imports
    all_imports = analyze_all_imports()
    print(f"\n📦 Found {len(all_imports)} unique third-party imports:")
    for imp in sorted(all_imports):
        print(f"  • {imp}")
    
    # Map to actual package names
    package_mapping = get_package_mapping()
    packages_to_install = []
    
    for import_name in sorted(all_imports):
        if import_name in package_mapping:
            actual_package = package_mapping[import_name]
            if actual_package is not None:  # Skip built-in modules
                packages_to_install.append(actual_package)
        else:
            # Use import name as package name if not in mapping
            packages_to_install.append(import_name)
    
    # Remove duplicates and sort
    packages_to_install = sorted(list(set(packages_to_install)))
    
    print(f"\n📋 Packages to install ({len(packages_to_install)}):")
    for pkg in packages_to_install:
        print(f"  • {pkg}")
    
    # Install packages
    if packages_to_install:
        results = install_packages(packages_to_install)
        
        # Summary
        successful = [pkg for pkg, success in results.items() if success]
        failed = [pkg for pkg, success in results.items() if not success]
        
        print("\n" + "=" * 70)
        print("📊 Installation Summary")
        print("=" * 70)
        print(f"✅ Successful: {len(successful)}/{len(packages_to_install)}")
        print(f"❌ Failed: {len(failed)}")
        
        if failed:
            print("\n❌ Failed packages:")
            for pkg in failed:
                print(f"  • {pkg}")
            
            print("\n💡 Manual installation commands:")
            pip_cmd = "pip" if platform.system() == "Windows" else "pip3"
            for pkg in failed:
                print(f"  {pip_cmd} install {pkg}")
        
        if successful:
            print(f"\n🎉 Successfully installed {len(successful)} packages!")
    else:
        print("\n✅ No packages to install!")
    
    print("\n🚀 Ready to run LocalLLM!")
    print("  python src/gui/batch_gui.py")

if __name__ == "__main__":
    main()
