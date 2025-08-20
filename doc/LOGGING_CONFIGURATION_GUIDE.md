# ログシステム設定ガイド

## 概要

LocalLLMシステムでは、**設定可能なログシステム**により、ログ出力を柔軟に制御できます。

## ログ出力の種類

### 1. 詳細ログ（Detailed Log）
- **ファイル**: `logs/summarizer.log`
- **内容**: 完全な分析情報、品質指標、処理統計を含む詳細ログ
- **用途**: 開発、デバッグ、詳細分析

### 2. 要約専用ログ（Summary-Only Log）
- **ファイル**: `logs/summary_results.log`
- **内容**: 要約結果に特化したクリーンなログ
- **用途**: 結果検証、簡単な確認

## 設定方法

### config/settings.py での設定

```python
# Logging Configuration
enable_detailed_log: bool = Field(default=True)      # 詳細ログの有効/無効
enable_summary_only_log: bool = Field(default=True)  # 要約ログの有効/無効
```

### 環境変数での設定

```bash
# 詳細ログを無効化
export ENABLE_DETAILED_LOG=false

# 要約ログを無効化  
export ENABLE_SUMMARY_ONLY_LOG=false

# 両方有効化（デフォルト）
export ENABLE_DETAILED_LOG=true
export ENABLE_SUMMARY_ONLY_LOG=true
```

## 設定パターン

### パターン1: 両方有効（デフォルト）
```python
enable_detailed_log = True
enable_summary_only_log = True
```
- **結果**: 詳細分析ログ + 要約専用ログの両方出力
- **用途**: 完全な記録が必要な場合

### パターン2: 要約ログのみ
```python
enable_detailed_log = False
enable_summary_only_log = True
```
- **結果**: `logs/summary_results.log` のみ出力
- **用途**: 結果確認のみが必要な場合

### パターン3: 詳細ログのみ
```python
enable_detailed_log = True
enable_summary_only_log = False
```
- **結果**: `logs/summarizer.log` のみ出力
- **用途**: 詳細分析が必要だが要約ログは不要な場合

### パターン4: ログ無効化
```python
enable_detailed_log = False
enable_summary_only_log = False
```
- **結果**: 基本的なシステムログのみ
- **用途**: 最小限のログで動作させたい場合

## ログ形式

### 詳細ログの形式
```
🎯 ================================================================================
📝 SUMMARY GENERATION COMPLETE
🎯 ================================================================================
🤖 Model: tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
🌐 Language Mode: 🇯🇵 Japanese → Japanese
📋 Summary Type: concise
⏱️ Processing Time: 3.28 seconds

📊 TEXT METRICS:
   📥 Input:  4 words, 173 characters
   📤 Output: 1 words, 69 characters
   📉 Compression: 39.9% chars, 25.0% words
   ⚡ Speed: 53 chars/sec

📖 INPUT TEXT PREVIEW:
------------------------------------------------------------
人工知能（AI）は、現代のテクノロジーにおいて重要な役割を果たしています。

✨ GENERATED SUMMARY:
------------------------------------------------------------
AIは、現代の技術における重要な役割を果たしています。

🎯 QUALITY INDICATORS:
   📏 Compression Quality: 🟡 Good compression
   ⚡ Processing Speed: 🟢 Fast
   🎭 Summary Length: 🟡 Check length
```

### 要約専用ログの形式
```
================================================================================
📝 SUMMARY RESULT | 2025-08-15 07:29:46
================================================================================
🌐 Language: 🇯🇵 Japanese → Japanese
📋 Type: concise
⏱️ Time: 3.28s
📊 Compression: 39.9% (173 → 69 chars)

📥 INPUT:
人工知能（AI）は、現代のテクノロジーにおいて重要な役割を果たしています。

📤 SUMMARY:
AIは、現代の技術における重要な役割を果たしています。

================================================================================
```

## 使用例

### プログラムでの使用
```python
from config.settings import get_settings
from summarizer_enhanced import LLMSummarizer

# 設定を取得
settings = get_settings()

# サマライザーを初期化
summarizer = LLMSummarizer("models/tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf", settings)

# 要約実行（設定に応じてログ出力）
result = summarizer.summarize("要約したいテキスト")
```

### 環境変数での動的制御
```python
import os

# 実行時に要約ログのみ有効化
os.environ['ENABLE_DETAILED_LOG'] = 'false'
os.environ['ENABLE_SUMMARY_ONLY_LOG'] = 'true'

# 要約実行
result = summarizer.summarize("テキスト")
```

## テスト方法

### 設定テスト
```bash
# 設定可能ログのテスト実行
python -c "
import sys
sys.path.insert(0, '.')
from tests.test_log_configuration import test_logging_configurations
test_logging_configurations()
"
```

### 手動テスト
```bash
# 手動ログテスト実行
python -c "
import sys
sys.path.insert(0, '.')
from tests.test_manual_logging import test_manual_logging
test_manual_logging()
"
```

## ファイル構造

```
logs/
├── summarizer.log        # 詳細ログ（分析情報含む）
└── summary_results.log   # 要約専用ログ（結果のみ）
```

## 推奨設定

### 開発時
```python
enable_detailed_log = True      # 詳細な分析情報が必要
enable_summary_only_log = True  # 結果確認も必要
```

### 本番運用時
```python
enable_detailed_log = False     # 詳細情報は不要
enable_summary_only_log = True  # 結果確認は必要
```

### パフォーマンステスト時
```python
enable_detailed_log = False     # ログI/Oを最小化
enable_summary_only_log = False # 処理速度を最大化
```

---

このログシステムにより、目的に応じて最適なログ出力を選択できます。
