#!/usr/bin/env python3
"""Setup script for LocalLLM package installation."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r', encoding='utf-8') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="localllm",
    version="1.0.0",
    author="MameMame777",
    author_email="",
    description="A local LLM-based document summarization system with Japanese translation capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MameMame777/LocalLLM",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Researchers",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "api": [
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
        ],
        "all": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
            "fastapi>=0.104.0",
            "uvicorn[standard]>=0.24.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "localllm=localllm.main:main",
            "localllm-api=localllm.api.document_api:main",
            "localllm-enhanced-api=localllm.api.enhanced_document_api:main",
        ],
    },
    include_package_data=True,
    package_data={
        "localllm": [
            "config/*.yaml",
            "config/*.json",
            "config/*.py",
        ],
    },
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/MameMame777/LocalLLM/issues",
        "Source": "https://github.com/MameMame777/LocalLLM",
        "Documentation": "https://github.com/MameMame777/LocalLLM/blob/master/README.md",
    },
)
