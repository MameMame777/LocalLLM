# 📁 LocalLLM プロジェクト構造

## 🎯 整理完了後のディレクトリ構造

```
LocalLLM/
├── 📁 config/                 # 設定ファイル
│   ├── settings.py           # システム設定
│   ├── model_config.py       # モデル設定
│   └── llama2_config.py      # Llama2専用設定
│
├── 📁 src/                    # メインソースコード
│   ├── main.py               # メイン処理
│   ├── document_processor.py # ドキュメント処理
│   ├── summarizer.py         # 要約エンジン
│   ├── summarizer_enhanced.py # 強化版要約エンジン
│   ├── gui/                  # GUI関連
│   │   ├── batch_gui.py      # バッチ処理GUI (メインアプリ)
│   │   ├── enhanced_academic_processor.py # 学術処理エンジン
│   │   ├── google_translate_processor.py  # Google翻訳処理
│   │   └── launcher.py       # GUIランチャー
│   └── utils/                # ユーティリティ
│
├── 📁 models/                 # LLMモデルファイル
│   ├── llama-2-7b-chat.Q4_K_M.gguf
│   └── tinyllama-1.1b-chat-v1.0.Q4_K_M.gguf
│
├── 📁 data/                   # 入力データ
├── 📁 output/                 # 出力結果
├── 📁 tests/                  # テストスイート
├── 📁 test_data/             # テストデータ
├── 📁 examples/              # 使用例
├── 📁 doc/                   # ドキュメンテーション
├── 📁 logs/                  # ログファイル
│
├── 📁 archive/               # 整理されたアーカイブ
│   ├── old_tests/           # 古いテストファイル (56個)
│   ├── debug_scripts/       # デバッグ・分析スクリプト
│   ├── demo_scripts/        # デモスクリプト
│   └── reports/             # 古いレポートファイル
│
├── 📁 scripts/               # セットアップ・メンテナンススクリプト
│   ├── setup/               # 環境セットアップ関連
│   │   ├── setup_environment.py     # 完全環境構築
│   │   ├── install_dependencies.py  # 依存関係インストール
│   │   ├── complete_dependency_analysis.py # 依存関係分析
│   │   ├── verify_dependencies.py   # 依存関係検証
│   │   └── check_system.py          # システム要件チェック
│   └── maintenance/         # メンテナンス関連
│       ├── fix_gui_messages.py      # GUIメッセージ修正
│       └── extract_packages.py      # パッケージ抽出
│
├── main.py                   # 🚀 メインアプリケーション (統合エントリーポイント)
├── quick_start.py            # ⚡ クイックスタート (簡単起動)
├── setup.py                  # 📦 パッケージセットアップ
├── README.md                 # 📚 プロジェクト説明
├── requirements.txt          # 依存関係
└── pyproject.toml           # プロジェクト設定
```

## 🎯 主要エントリーポイント

### 1. メインアプリケーション (推奨)

```bash
python main.py              # 対話モード
python main.py --gui        # GUI直接起動
python main.py document.pdf # CLI処理
```

- 統合されたエントリーポイント
- GUI・CLI・対話モード対応

### 2. クイックスタート (簡単起動)

```bash
python quick_start.py
```

- 依存関係の自動チェック・インストール
- GUI自動起動

### 3. GUI直接起動

```bash
python src/gui/batch_gui.py
```

- バッチ処理GUI
- 学術文書処理
- PDF/HTML多形式対応

### 3. 環境セットアップ (詳細)

```bash
python scripts/setup/setup_environment.py
```

- 詳細な環境構築

## 🧹 整理作業完了

### 移動されたファイル
- ✅ **56個のテストファイル** → `archive/old_tests/`
- ✅ **デバッグスクリプト** → `archive/debug_scripts/`
- ✅ **デモスクリプト** → `archive/demo_scripts/`
- ✅ **古いレポート** → `archive/reports/`

### 保持された重要ファイル
- ✅ **quick_start.py** - メインエントリーポイント
- ✅ **src/gui/batch_gui.py** - メインGUIアプリ
- ✅ **src/gui/enhanced_academic_processor.py** - 学術処理エンジン
- ✅ **config/settings.py** - システム設定
- ✅ **README.md** - プロジェクト説明

## 📊 品質改善成果

✅ **ディレクトリ複雑度**: 大幅簡素化  
✅ **メンテナンス性**: 向上  
✅ **可読性**: 改善  
✅ **新規開発者**: 理解しやすい構造  
