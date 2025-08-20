# LocalLLM Enhanced API 使用ガイド

## 概要

Enhanced APIは、JSON入力対応と詳細な設定管理を提供する高機能要約APIです。

## 特徴

- ✅ JSON形式データの直接入力対応
- ⚙️ 設定ファイル（YAML/JSON）サポート  
- 🔧 引数による設定オーバーライド
- 🌐 多言語対応（日本語・英語）
- 📝 複数の要約タイプ
- 🎯 個別URL処理

## インストール

```bash
# 必要なパッケージ
pip install pyyaml
```

## 基本的な使用方法

### 1. 引数で設定を指定

```python
from src.api.enhanced_api import summarize_json, SummaryConfig

# JSONデータ
data = {
    "title": "FPGA設計文書",
    "content": "FPGAは高速並列処理が可能なプログラマブルデバイスです。",
    "urls": [
        {"url": "https://example.com/fpga1", "title": "FPGA基礎"},
        {"url": "https://example.com/fpga2", "title": "FPGA応用"}
    ]
}

# 設定を作成
config = SummaryConfig(
    language="ja",           # 日本語
    summary_type="detailed", # 詳細要約
    max_length=1000         # 最大1000文字
)

# 要約実行
result = summarize_json(data, config=config)
print(result)
```

### 2. 設定ファイルを使用

```python
# 設定ファイルから読み込み
result = summarize_json(data, config_file="config/summary_config.yaml")
```

### 3. 混合方式（推奨）

```python
# 設定ファイル + 引数オーバーライド
result = summarize_json(
    data, 
    config_file="config/summary_config.yaml",
    language="en",          # 設定ファイルをオーバーライド
    summary_type="brief"    # 設定ファイルをオーバーライド
)
```

## 設定オプション

### 基本設定

| 項目 | 型 | デフォルト | 説明 |
|------|----|-----------|----- |
| `language` | str | "ja" | 出力言語（"ja", "en"） |
| `summary_type` | str | "brief" | 要約タイプ |
| `output_format` | str | "markdown" | 出力形式 |
| `max_length` | int? | None | 最大文字数制限 |

### 要約タイプ

- `"brief"` - 簡潔な要約
- `"detailed"` - 詳細な要約  
- `"academic"` - 学術的な要約
- `"concise"` - 要点のみ

### JSON処理設定

| 項目 | 型 | デフォルト | 説明 |
|------|----|-----------|----- |
| `individual_processing` | bool | True | 個別URL処理 |
| `include_urls` | bool | True | URL情報を含める |
| `batch_size` | int | 3 | バッチサイズ |

### 翻訳設定

| 項目 | 型 | デフォルト | 説明 |
|------|----|-----------|----- |
| `enable_translation` | bool | True | 翻訳を有効化 |
| `translation_chunk_size` | int | 5000 | 翻訳チャンクサイズ |

## 設定ファイル例

### YAML形式（推奨）

```yaml
# config/my_summary_config.yaml
language: "ja"
summary_type: "detailed"
output_format: "markdown"
max_length: 2000

individual_processing: true
include_urls: true
batch_size: 5

enable_translation: true
translation_chunk_size: 4000

retry_count: 3
timeout: 600
```

### JSON形式

```json
{
  "language": "en",
  "summary_type": "academic",
  "output_format": "text",
  "max_length": 1500,
  "individual_processing": false,
  "include_urls": false,
  "batch_size": 3
}
```

## 実用的な使用例

### 例1: 研究論文の要約

```python
from src.api.enhanced_api import summarize_json, SummaryConfig

# 研究論文データ
paper_data = {
    "title": "Deep Learning for FPGA Acceleration",
    "abstract": "This paper presents...",
    "urls": [
        {"url": "https://arxiv.org/abs/2024.001", "title": "Paper Link"},
        {"url": "https://github.com/author/code", "title": "Source Code"}
    ]
}

# 学術要約設定
config = SummaryConfig(
    language="ja",
    summary_type="academic",
    output_format="markdown",
    individual_processing=True,
    include_metadata=True
)

result = summarize_json(paper_data, config=config)
```

### 例2: 複数言語対応

```python
# 英語で要約
en_result = summarize_json(data, language="en", summary_type="brief")

# 日本語で要約  
ja_result = summarize_json(data, language="ja", summary_type="detailed")
```

### 例3: バッチ処理

```python
# 大量URLの効率的処理
config = SummaryConfig(
    individual_processing=True,
    batch_size=10,        # 大きなバッチサイズ
    timeout=1800,         # 30分タイムアウト
    retry_count=5         # リトライ増加
)

result = summarize_json(large_url_list, config=config)
```

## エラーハンドリング

```python
try:
    result = summarize_json(data, config=config)
    print("成功:", result)
except FileNotFoundError as e:
    print("設定ファイルが見つかりません:", e)
except ValueError as e:
    print("設定エラー:", e)
except Exception as e:
    print("処理エラー:", e)
```

## パフォーマンス最適化

### 高速処理設定

```python
# 高速処理優先
fast_config = SummaryConfig(
    summary_type="brief",
    individual_processing=False,  # 個別処理無効
    enable_translation=False,     # 翻訳無効
    batch_size=1,
    timeout=60
)
```

### 高品質処理設定

```python
# 品質優先
quality_config = SummaryConfig(
    summary_type="academic",
    individual_processing=True,   # 個別処理有効
    enable_translation=True,      # 翻訳有効
    batch_size=3,
    retry_count=5,
    timeout=600
)
```

## トラブルシューティング

### よくある問題

1. **URLアクセスエラー**
   ```python
   # リトライ設定を増やす
   config.retry_count = 5
   config.timeout = 300
   ```

2. **メモリ不足**
   ```python
   # バッチサイズを減らす
   config.batch_size = 1
   ```

3. **処理時間が長い**
   ```python
   # 簡潔な要約に変更
   config.summary_type = "brief"
   config.individual_processing = False
   ```

## 設定管理のベストプラクティス

### 1. プロジェクト別設定

```bash
config/
├── research_config.yaml      # 研究用
├── business_config.yaml      # ビジネス用  
├── quick_config.yaml         # 高速処理用
└── quality_config.yaml       # 高品質用
```

### 2. 環境別設定

```python
import os

# 環境に応じた設定ファイル選択
env = os.getenv("ENVIRONMENT", "development")
config_file = f"config/{env}_config.yaml"
result = summarize_json(data, config_file=config_file)
```

### 3. 動的設定調整

```python
# 基本設定を読み込み
base_config = SummaryConfig.from_file("config/base.yaml")

# データサイズに応じて調整
if len(str(data)) > 10000:
    base_config.batch_size = 1
    base_config.timeout = 600

result = summarize_json(data, config=base_config)
```

## まとめ

Enhanced APIを使用することで、以下の利点があります：

- 🎯 **柔軟な設定管理**: 引数・設定ファイル・混合方式
- 🚀 **高性能処理**: バッチ処理・並列処理対応
- 🌐 **多言語対応**: 日本語・英語の要約生成
- 📋 **豊富な要約タイプ**: 用途に応じた要約スタイル
- 🔧 **カスタマイズ性**: 詳細な設定オプション

これにより、様々なユースケースに対応した高品質な要約処理が可能になります。
