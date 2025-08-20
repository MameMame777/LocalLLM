#!/usr/bin/env python3
"""
Extract third-party package dependencies from the codebase
"""
import os
import re
from pathlib import Path

third_party_packages = set()

# Known standard library modules to exclude
stdlib_modules = {
    'sys', 'os', 'time', 'threading', 'json', 'csv', 'argparse', 'subprocess',
    'datetime', 'pathlib', 'typing', 'dataclasses', 'enum', 'logging', 're',
    'mimetypes', 'traceback', 'queue', 'concurrent', 'multiprocessing', 'urllib',
    'webbrowser', 'collections', 'itertools', 'functools', 'copy', 'hashlib',
    'tkinter', 'abc', 'warnings', 'tempfile', 'shutil', 'random', 'math'
}

def extract_packages_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Find import statements
        import_patterns = [
            r'^import\s+([a-zA-Z_][a-zA-Z0-9_]*)',
            r'^from\s+([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s+import'
        ]
        
        for pattern in import_patterns:
            matches = re.findall(pattern, content, re.MULTILINE)
            for match in matches:
                # Get the top-level package name
                package = match.split('.')[0]
                if package not in stdlib_modules and not package.startswith('src') and not package.startswith('config'):
                    third_party_packages.add(package)
                    
    except Exception as e:
        print(f'Error reading {file_path}: {e}')

def main():
    print("🔍 Extracting third-party packages from codebase...")
    
    # Scan all Python files
    for root, dirs, files in os.walk('src'):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                extract_packages_from_file(file_path)

    print('\n📦 Third-party packages found:')
    for package in sorted(third_party_packages):
        print(f'  {package}')

    print(f'\n📊 Total: {len(third_party_packages)} packages')
    
    # Generate requirements list
    package_mapping = {
        'bs4': 'beautifulsoup4',
        'PyPDF2': 'pypdf2',
        'pdfminer': 'pdfminer.six',
        'llama_cpp': 'llama-cpp-python',
        'memory_profiler': 'memory-profiler'
    }
    
    requirements = []
    for package in sorted(third_party_packages):
        actual_package = package_mapping.get(package, package)
        requirements.append(actual_package)
    
    print('\n📋 Requirements.txt format:')
    for req in requirements:
        print(req)

if __name__ == "__main__":
    main()
