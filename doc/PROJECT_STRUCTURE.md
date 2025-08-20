# 📁 LocalLLM プロジェクト構造ガイド

## 🎯 概要

LocalLLMプロジェクトの整理されたディレクトリ構造と各ファイルの役割を説明します。

---

## 📂 ディレクトリ構造

```
LocalLLM/
├── 📁 config/                 # 設定ファイル
│   ├── llama2_config.py      # Llama 2 専用設定
│   ├── model_config.py       # モデル設定
│   └── settings.py           # メイン設定ファイル
├── 📁 data/                  # テストデータ
│   ├── english_test.html     # 英語テストファイル
│   ├── test_document.html    # HTMLテスト文書
│   ├── test_document.pdf     # PDFテスト文書
│   └── temp/                 # 一時ファイル
├── 📁 doc/                   # ドキュメント
│   ├── designspec.md         # 設計仕様書
│   └── LLM_TECHNICAL_INSIGHTS.md  # LLM技術知見書
├── 📁 logs/                  # ログファイル
│   └── summarizer.log        # アプリケーションログ
├── 📁 models/                # LLMモデルファイル
│   ├── llama-2-7b-chat.Q4_K_M.gguf      # Llama 2 7B メインモデル
│   ├── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf  # TinyLlama 軽量モデル
│   └── llama2_usage.md       # Llama 2 使用方法
├── 📁 output/                # 出力ファイル
│   ├── english_content_japanese_summary.md
│   ├── html_extracted.txt
│   ├── pdf_test.md
│   ├── test_document_extracted.txt
│   ├── test_document_summary.markdown
│   ├── webpage_summary.json
│   └── webpage_summary.markdown
├── 📁 src/                   # メインソースコード
│   ├── __init__.py
│   ├── document_processor.py # 文書処理モジュール
│   ├── main.py              # メインエントリポイント
│   ├── summarizer_enhanced.py # 拡張要約モジュール
│   ├── summarizer.py        # 基本要約モジュール
│   └── utils/               # ユーティリティ
│       ├── __init__.py
│       ├── logger.py        # ログ設定
│       └── performance.py   # パフォーマンス測定
├── 📁 tests/                # テストスクリプト（整理済み）
│   ├── analyze_mock_necessity.py      # モック必要性分析
│   ├── test_comparison.py             # 比較テスト
│   ├── test_direct_translation.py     # 直接翻訳テスト
│   ├── test_document_processor.py     # 文書処理テスト
│   ├── test_english_content.py        # 英語コンテンツテスト
│   ├── test_english_to_japanese.py    # 英日翻訳テスト
│   ├── test_extraction.py             # 抽出テスト
│   ├── test_full_pipeline.py          # 全パイプラインテスト
│   ├── test_integrated_optimization.py # 統合最適化テスト
│   ├── test_llama2_simple.py          # Llama 2 簡易テスト
│   ├── test_llama2_translation.py     # Llama 2 翻訳テスト
│   ├── test_no_mock_system.py         # モック削除後テスト
│   ├── test_optimized_translation.py  # 最適化翻訳テスト
│   ├── test_real_llm.py               # 実LLMテスト
│   ├── test_real_summarization.py     # 実要約テスト
│   └── test_simple_english.py         # 簡易英語テスト
├── 📁 utils/                # ユーティリティスクリプト（整理済み）
│   ├── check_system.py      # システム要件チェック
│   ├── create_test_pdf.py   # テストPDF作成
│   ├── download_llama2.py   # Llama 2 ダウンロード
│   ├── download_model.py    # モデルダウンロード（汎用）
│   ├── download_model_fixed.py # 修正版モデルダウンロード
│   └── multilingual_models_info.py # 多言語モデル情報
├── .env                     # 環境変数設定
├── .github/                 # GitHub設定
├── MULTILINGUAL_SETUP_GUIDE.md # 多言語設定ガイド
├── README.md                # プロジェクト概要
├── pyproject.toml          # Poetry設定
├── requirements-dev.txt     # 開発用依存関係
├── requirements.txt         # 本番用依存関係
└── setup.py                # セットアップスクリプト
```

---

## 🎯 主要ファイルの役割

### 🔧 コア機能

**src/summarizer_enhanced.py**
- **役割**: メインのLLM要約エンジン
- **特徴**: 最適化された英日翻訳プロンプト統合済み
- **最新機能**: モックLLM削除、Llama 2専用最適化

**src/document_processor.py**
- **役割**: PDF、HTML、テキストファイルの処理
- **機能**: ファイル形式自動判定、テキスト抽出

**src/main.py**
- **役割**: アプリケーションのメインエントリポイント
- **使用方法**: `python -m src.main [file_path]`

### ⚙️ 設定管理

**config/settings.py**
- **役割**: システム全体の設定管理
- **設定項目**: モデルパス、生成パラメータ、処理設定

**config/llama2_config.py**
- **役割**: Llama 2専用設定
- **最適化**: 英日翻訳用パラメータ調整済み

### 🛠️ ユーティリティ

**utils/download_llama2.py**
- **役割**: Llama 2 7B モデルの自動ダウンロード
- **特徴**: レジューム機能、システム要件チェック

**utils/check_system.py**
- **役割**: システム要件の確認
- **チェック項目**: RAM、ディスク容量、CPU

### 🧪 テスト

**tests/test_integrated_optimization.py**
- **役割**: 最適化統合後の効果測定
- **結果**: 100%成功率、11.08秒平均処理時間

**tests/test_no_mock_system.py**
- **役割**: モックLLM削除後の動作確認
- **検証**: エラーハンドリング、実LLM専用動作

---

## 🚀 使用方法

### 基本的な使用方法

```bash
# メイン機能の実行
python -m src.main data/test_document.pdf

# システム要件確認
python utils/check_system.py

# Llama 2モデルダウンロード
python utils/download_llama2.py

# テスト実行
python tests/test_integrated_optimization.py
```

### 開発者向け

```bash
# 開発環境セットアップ
pip install -r requirements-dev.txt

# 全テスト実行
python -m pytest tests/

# 特定テスト実行
python tests/test_english_to_japanese.py
```

---

## 📊 整理の効果

### Before（整理前）
```
LocalLLM/
├── analyze_mock_necessity.py    # ← トップレベルに散乱
├── check_system.py             # ← トップレベルに散乱
├── download_llama2.py          # ← トップレベルに散乱
├── test_*.py (15個)            # ← トップレベルに散乱
└── ...
```

### After（整理後）
```
LocalLLM/
├── 📁 tests/          # テストスクリプト集約
├── 📁 utils/          # ユーティリティ集約
├── 📁 doc/            # ドキュメント充実
├── 📁 src/            # コア機能
└── 基本設定ファイルのみ    # クリーンなトップレベル
```

### 改善効果

1. **🎯 可読性向上**: 目的別にファイルが整理され、プロジェクト構造が明確
2. **🔍 保守性向上**: 必要なファイルを素早く発見可能
3. **👥 協力開発**: 新しい開発者がプロジェクトを理解しやすい
4. **📚 ドキュメント充実**: 技術知見が体系的に整理

---

## 🎓 開発ガイドライン

### ファイル配置ルール

1. **tests/**: テスト関連は全てこのディレクトリに
2. **utils/**: 独立したユーティリティスクリプト
3. **src/**: メインアプリケーションコード
4. **doc/**: ドキュメント、技術知見
5. **config/**: 設定ファイル

### 命名規則

- **テストファイル**: `test_*.py`
- **ユーティリティ**: 機能を表す明確な名前
- **設定ファイル**: `*_config.py` または `settings.py`
- **ドキュメント**: 大文字、アンダースコア区切り

---

*このガイドにより、LocalLLMプロジェクトの構造が明確になり、開発・保守・協力作業が効率化されます。*

**最終更新**: 2025年8月15日  
**整理完了**: トップディレクトリクリーンアップ、ドキュメント体系化完了
