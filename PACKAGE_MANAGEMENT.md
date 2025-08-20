# LocalLLM - Automatic Package Management

## 🚀 Quick Start

### Option 1: Quick Start (Fastest)
```bash
python quick_start.py
```
このスクリプトが自動的に必要なパッケージをインストールしてGUIを起動します。

### Option 2: Manual Installation
```bash
python install_dependencies.py
```

### Option 3: Complete Environment Setup
```bash
python setup_environment.py
```
完全な仮想環境をセットアップします。

## 📦 Required Packages

### Core Dependencies
- `loguru` - Advanced logging
- `tqdm` - Progress bars  
- `schedule` - Task scheduling
- `click` - CLI interface

### Document Processing
- `html2text` - HTML to text conversion
- `pdfminer.six` - PDF text extraction
- `pypdf2` - PDF processing
- `python-docx` - Word documents
- `beautifulsoup4` - HTML parsing
- `lxml` - XML/HTML parser

### Web and HTTP
- `requests` - HTTP requests

### AI and Language
- `transformers` - Hugging Face transformers
- `llama-cpp-python` - LLaMA model support
- `langdetect` - Language detection

### System Monitoring
- `psutil` - System monitoring
- `memory-profiler` - Memory profiling

## 🛠️ Manual Installation Commands

### Windows (仮想環境あり)
```cmd
venv\Scripts\activate
pip install -r requirements.txt
```

### Windows (グローバル)
```cmd
pip install loguru tqdm schedule html2text pdfminer.six langdetect transformers beautifulsoup4 lxml requests pypdf2 python-docx llama-cpp-python psutil memory-profiler
```

### Linux/Mac
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 🐛 Troubleshooting

### Common Errors

#### `No module named 'pdfminer'`
```bash
pip install pdfminer.six
```

#### `No module named 'html2text'`
```bash
pip install html2text
```

#### `No module named 'tqdm'`
```bash
pip install tqdm
```

#### `No module named 'langdetect'`
```bash
pip install langdetect
```

### Environment Issues

1. **仮想環境が壊れている場合:**
   ```bash
   python setup_environment.py
   ```

2. **pipが古い場合:**
   ```bash
   python -m pip install --upgrade pip
   ```

3. **権限エラーの場合:**
   ```bash
   pip install --user [package_name]
   ```

## 📋 Verification

### パッケージ確認
```python
python -c "
import loguru, tqdm, schedule, html2text, pdfminer, langdetect
print('✅ All essential packages are installed!')
"
```

### GUI起動テスト
```bash
python src/gui/batch_gui.py
```

## 💡 Development Tips

- 新しいパッケージを追加したら `requirements.txt` を更新
- `extract_packages.py` でコードベースの依存関係を自動検出
- `install_dependencies.py` で一括インストール
- 定期的に `pip freeze > requirements-lock.txt` で固定バージョン作成

## 🔧 Scripts Overview

| Script | Purpose |
|--------|---------|
| `quick_start.py` | 最速セットアップ＆GUI起動 |
| `install_dependencies.py` | 依存関係の一括インストール |
| `setup_environment.py` | 完全な開発環境セットアップ |
| `extract_packages.py` | 依存関係の自動検出 |
