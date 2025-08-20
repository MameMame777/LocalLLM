# LocalLLM 要約API 使用ガイド

他のコードから LocalLLM の要約機能を簡単に呼び出すためのAPIを提供します。

## 📋 目次

1. [インストール・セットアップ](#インストールセットアップ)
2. [Quick API（最もシンプル）](#quick-api最もシンプル)
3. [Enhanced API（JSON対応・設定機能）](#enhanced-apijson対応設定機能)
4. [Simple API（基本）](#simple-api基本)
5. [Full API（高機能）](#full-api高機能)
6. [使用例集](#使用例集)
7. [トラブルシューティング](#トラブルシューティング)

## 🚀 インストール・セットアップ

```python
# プロジェクトルートにパスを追加
import sys
from pathlib import Path
project_root = Path("e:/Nautilus/workspace/pythonworks/LocalLLM")
sys.path.insert(0, str(project_root))

# 設定ファイル用（YAML使用時）
pip install pyyaml
```

## 📝 Quick API（最もシンプル）

### 基本的な使用方法

```python
# ファイル要約
from src.api.quick_api import summarize_file
result = summarize_file("document.pdf")
print(result)

# テキスト要約
from src.api.quick_api import summarize_text
result = summarize_text("長いテキストをここに...")
print(result)

# JSON要約（新機能）
from src.api.quick_api import summarize_json
json_data = {"title": "文書", "content": "内容...", "urls": [...]}
result = summarize_json(json_data)
print(result)

# 複数ファイル一括要約
from src.api.quick_api import summarize_batch
results = summarize_batch(["file1.pdf", "file2.txt", "file3.json"])
for item in results:
    print(f"{item['file']}: {item['status']}")
```

### 言語指定

```python
# 日本語要約（デフォルト）
result_ja = summarize_file("document.pdf", "ja")

## 🔧 Enhanced API（JSON対応・設定機能）

### 最新のEnhanced API - 高機能設定対応

```python
from src.api.enhanced_api import summarize_json, SummaryConfig

# 1. 引数で詳細設定
config = SummaryConfig(
    language="ja",           # 出力言語
    summary_type="detailed", # 要約タイプ
    max_length=1000,        # 最大文字数
    individual_processing=True,  # 個別URL処理
    output_format="markdown"     # 出力形式
)
result = summarize_json(json_data, config=config)

# 2. 設定ファイルで管理
result = summarize_json(json_data, config_file="config/summary_config.yaml")

# 3. ハイブリッド（推奨）- 設定ファイル+オーバーライド
result = summarize_json(
    json_data, 
    config_file="config/base_config.yaml",
    language="en",          # 設定ファイルをオーバーライド
    summary_type="brief"    # 設定ファイルをオーバーライド
)
```

### 設定ファイル例

**YAML形式（推奨）:**
```yaml
# config/summary_config.yaml
language: "ja"
summary_type: "detailed"
output_format: "markdown"
max_length: 2000
individual_processing: true
include_urls: true
batch_size: 5
enable_translation: true
```

**JSON形式:**
```json
{
  "language": "en",
  "summary_type": "academic",
  "output_format": "text",
  "max_length": 1500,
  "individual_processing": false
}
```

### 詳細な設定オプション

| 項目 | 型 | デフォルト | 説明 |
|------|----|-----------|----- |
| `language` | str | "ja" | 出力言語（"ja", "en"） |
| `summary_type` | str | "brief" | 要約タイプ（"brief", "detailed", "academic", "concise"） |
| `output_format` | str | "markdown" | 出力形式（"markdown", "text", "html"） |
| `max_length` | int? | None | 最大文字数制限 |
| `individual_processing` | bool | True | 個別URL処理 |
| `include_urls` | bool | True | URL情報を含める |
| `batch_size` | int | 3 | バッチサイズ |
| `enable_translation` | bool | True | 翻訳を有効化 |
| `retry_count` | int | 3 | リトライ回数 |
| `timeout` | int | 300 | タイムアウト（秒） |

詳細なガイド: [doc/ENHANCED_API_GUIDE.md](../../doc/ENHANCED_API_GUIDE.md)

# 英語要約
result_en = summarize_file("document.pdf", "en")
```

## 🔧 Simple API（基本）

より詳細な情報が必要な場合：

```python
from src.api.simple_api import summarize_file_simple, summarize_text_simple

# ファイル要約（詳細結果）
result = summarize_file_simple("document.pdf", "ja")
if result["status"] == "success":
    print(f"要約結果: {result['result']}")
else:
    print(f"エラー: {result['message']}")

# テキスト要約（詳細結果）
result = summarize_text_simple("テキスト...", "ja")
if result["status"] == "success":
    print(f"元の長さ: {result['original_length']}")
    print(f"要約の長さ: {result['summary_length']}")
    print(f"要約: {result['summary']}")
```

## 🎯 Full API（高機能）

最も高機能なAPI：

```python
from src.api.summarization_api import SummarizationAPI

# API初期化
api = SummarizationAPI()

# ヘルスチェック
health = api.health_check()
print(f"API状態: {health['status']}")

# ファイル要約（詳細オプション）
result = api.summarize_file(
    file_path="document.pdf",
    target_language="ja",
    summary_type="detailed",  # "brief", "detailed", "academic"
    output_dir="./output"
)

# バッチ処理（並列処理）
results = api.summarize_batch(
    file_paths=["file1.pdf", "file2.txt"],
    target_language="ja",
    max_workers=2
)
```

## 💡 使用例集

### 例1: PDFファイルの要約

```python
from src.api.quick_api import summarize_file

# PDFファイルを日本語で要約
pdf_summary = summarize_file("research_paper.pdf", "ja")
print("PDF要約結果:")
print(pdf_summary)
```

### 例2: Webからのテキスト要約

```python
import requests
from src.api.quick_api import summarize_text

# Webページからテキスト取得（例）
url = "https://example.com/article"
response = requests.get(url)
text = response.text

# テキストを要約
summary = summarize_text(text, "ja")
print("Web記事要約:")
print(summary)
```

### 例3: フォルダ内のファイル一括要約

```python
from pathlib import Path
from src.api.quick_api import summarize_batch

# フォルダ内のPDFファイルを取得
folder_path = Path("./documents")
pdf_files = list(folder_path.glob("*.pdf"))

# 一括要約
results = summarize_batch([str(f) for f in pdf_files], "ja")

# 結果保存
for result in results:
    if result["status"] == "success":
        output_file = f"{Path(result['file']).stem}_summary.txt"
        with open(output_file, "w", encoding="utf-8") as f:
            f.write(result["result"])
        print(f"✅ 要約保存: {output_file}")
```

### 例4: エラーハンドリング付きの処理

```python
from src.api.simple_api import summarize_file_simple

def safe_summarize(file_path):
    """安全な要約処理（エラーハンドリング付き）"""
    try:
        result = summarize_file_simple(file_path, "ja")
        
        if result["status"] == "success":
            print(f"✅ 要約成功: {file_path}")
            return result["result"]
        else:
            print(f"❌ 要約失敗: {file_path}")
            print(f"   エラー内容: {result['message']}")
            return None
            
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return None

# 使用例
summary = safe_summarize("important_document.pdf")
if summary:
    print("要約結果:", summary[:200] + "...")
```

## 📊 サポート形式・オプション

### ファイル形式
- `.pdf` - PDFファイル
- `.txt` - テキストファイル  
- `.md` - Markdownファイル
- `.html` - HTMLファイル
- `.json` - JSONファイル
- `.csv` - CSVファイル
- `.docx` - Word文書

### 言語オプション
- `"ja"` - 日本語要約（デフォルト）
- `"en"` - 英語要約

### 要約タイプ（Full APIのみ）
- `"brief"` - 簡潔な要約
- `"detailed"` - 詳細な要約
- `"academic"` - 学術的な要約
- `"concise"` - 超簡潔な要約

## 🔧 トラブルシューティング

### よくある問題と解決方法

1. **インポートエラー**
   ```python
   # パスが正しく設定されているか確認
   import sys
   print(sys.path)
   ```

2. **ファイルが見つからない**
   ```python
   from pathlib import Path
   file_path = Path("document.pdf")
   print(f"ファイル存在: {file_path.exists()}")
   print(f"絶対パス: {file_path.absolute()}")
   ```

3. **メモリ不足**
   ```python
   # 大きなファイルは分割処理
   from src.api.summarization_api import SummarizationAPI
   api = SummarizationAPI()
   # max_workersを少なくする
   results = api.summarize_batch(files, max_workers=1)
   ```

4. **API状態確認**
   ```python
   from src.api.summarization_api import SummarizationAPI
   api = SummarizationAPI()
   health = api.health_check()
   print(health)
   ```

## 📞 サポート

問題が発生した場合は、以下の情報を含めてお問い合わせください：
- 使用しているAPI（Quick/Simple/Full）
- ファイル形式・サイズ
- エラーメッセージ
- 実行環境（Python バージョンなど）

---

**🎉 これで他のコードから LocalLLM の要約機能を簡単に利用できます！**
