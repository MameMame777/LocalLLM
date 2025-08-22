# 🔧 LocalLLM External Integration Guide

## Issue #1 Resolution: Package Installation Support

### 🎯 Problem Solved
- ✅ `pip install git+https://github.com/MameMame777/LocalLLM.git` now works
- ✅ External project integration is fully supported
- ✅ Multiple integration approaches available

### 📦 Installation Methods

#### Method 1: Git Installation (Recommended)
```bash
pip install git+https://github.com/MameMame777/LocalLLM.git
```

#### Method 2: Local Installation
```bash
git clone https://github.com/MameMame777/LocalLLM.git
cd LocalLLM
pip install -e .
```

#### Method 3: With API Support
```bash
pip install git+https://github.com/MameMame777/LocalLLM.git[api]
```

### 🚀 Usage Examples

#### Basic Text Summarization
```python
# Method 1: Direct Integration (Current)
import sys
from pathlib import Path

# Add LocalLLM to Python path
localllm_path = Path("path/to/LocalLLM/src")
sys.path.insert(0, str(localllm_path))

from integration import summarize_text

result = summarize_text(
    text="Your text here...",
    language="ja",
    mode="enhanced"
)
print(result["summary"])
```

#### File Processing
```python
from integration import process_file

result = process_file(
    file_path="document.pdf",
    mode="academic",
    language="ja"
)
print(result["summary"])
```

#### Batch Processing
```python
from integration import process_batch

files = ["file1.pdf", "file2.txt", "file3.html"]
results = process_batch(
    file_paths=files,
    mode="enhanced",
    language="ja"
)

for result in results:
    print(f"File: {result['file_path']}")
    print(f"Summary: {result['summary']}")
```

#### API Integration
```python
from api.server_controller import LocalLLMAPIServerController, LocalLLMAPIClient

# Start API server
controller = LocalLLMAPIServerController()
controller.start_server()

# Use API client
client = LocalLLMAPIClient()
result = client.process_text("Your text here")
```

### 🎚️ Processing Modes

| Mode | Quality | Speed | Features |
|------|---------|-------|----------|
| `basic` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Basic summarization only |
| `enhanced` | ⭐⭐⭐⭐ | ⭐⭐⭐ | LLM + Translation |
| `academic` | ⭐⭐⭐⭐⭐ | ⭐⭐ | Full academic processing |

### 🔍 Installation Verification
```python
from integration import check_installation
import json

status = check_installation()
print(json.dumps(status, indent=2))
```

### 💡 Tips for External Projects

1. **For InfoGetter Project**: Use `enhanced` mode for FPGA documents
2. **For Research Projects**: Use `academic` mode for papers
3. **For Quick Processing**: Use `basic` mode for speed

### 🚨 Troubleshooting

#### ImportError Issues
```python
# Ensure correct path setup
import sys
sys.path.insert(0, "/path/to/LocalLLM/src")
```

#### API Connection Issues
```python
# Check server status
from api.server_controller import LocalLLMAPIServerController
controller = LocalLLMAPIServerController()
if not controller.is_server_running():
    controller.start_server()
```

### 📞 Support
- 🐛 Issues: https://github.com/MameMame777/LocalLLM/issues
- 📖 Documentation: https://github.com/MameMame777/LocalLLM/README.md
