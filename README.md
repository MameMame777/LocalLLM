# 🤖 LocalLLM Document Summarizer

高性能なローカルLLMを使用したドキュメント要約・英日翻訳システム

## ✨ 特徴

- **🔒 完全ローカル実行**: インターネット接続不要、プライバシー完全保護
- **🎯 高品質英日翻訳**: Llama 2 7B最適化プロンプトで100%成功率達成
- **📚 多形式対応**: PDF、HTML、WebページURL、テキストファイル
- **⚡ 高性能**: 平均11秒で自然な日本語翻訳を生成
- **🛡️ 堅牢性**: モックLLM削除により実LLM専用の安定動作
- **🔧 カスタマイズ**: モデル選択、パラメータ調整、プロンプト最適化
- **🖥️ ユーザーフレンドリーGUI**: 直感的な操作画面とリアルタイム監視
- **📊 バッチ処理**: 複数ファイルの並列処理と詳細レポート生成
- **🚀 Enhanced API**: JSON入力対応、設定可能要約、メール通知機能
- **📧 メール通知**: 処理完了時の自動通知システム

## 📊 実証済み性能

| 指標 | 達成値 | 備考 |
|------|--------|------|
| 英日翻訳成功率 | **100%** | 空の結果なし |
| 平均処理時間 | **11.08秒** | 実用的な速度 |
| 翻訳品質 | **高品質** | 自然で流暢な日本語 |
| システム安定性 | **完全安定** | モックフォールバック削除済み |

## 🖥️ 必要環境

### 💻 CPU専用動作（デフォルト）
- **Python**: 3.10以降
- **RAM**: 8GB以上（CPU推論用）
- **CPU**: マルチコア推奨（4コア以上）
- **ストレージ**: 10GB以上（モデルファイル含む）
- **OS**: Windows 10/11, macOS, Linux
- **GPU**: **不要** - 完全にCPUのみで動作

### 最小要件
- **Python**: 3.10以降
- **RAM**: 8GB以上
- **ストレージ**: 10GB以上（モデルファイル含む）
- **OS**: Windows 10/11, macOS, Linux

### 推奨環境（より高性能な動作用）
- **RAM**: 16GB以上（Llama 2 7B最適動作）
- **CPU**: 8コア以上（高速並列処理）
- **ストレージ**: SSD推奨
- **GPU**: オプション（CUDA対応時のみ - 通常は不要）

### 🔧 CPU/GPU設定

**CPU専用（デフォルト設定）**:
```python
# config/settings.py
n_gpu_layers = 0    # CPU専用
n_threads = 4       # CPUスレッド数
```

**GPU使用（オプション）**:
```python  
# GPU使用時の設定例
n_gpu_layers = 32   # GPU層数（モデルによって調整）
n_threads = 2       # GPUと併用時のCPUスレッド数
```

### 💡 CPU専用の利点

- **環境構築が簡単**: GPU ドライバー不要
- **広い互換性**: どのPCでも動作
- **安定性**: GPU依存の問題なし
- **低コスト**: 専用GPU不要

## インストール

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd LocalLLM
```

### 2. 仮想環境の作成

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 依存関係のインストール

```bash
pip install -r requirements.txt
```

### 4. モデルのダウンロード

```bash
# modelsディレクトリを作成
mkdir models

# Llama 2 7B Chat モデル (例)
# https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGML からダウンロード
# または以下のコマンドでダウンロード（要huggingface-hub）
# huggingface-cli download TheBloke/Llama-2-7B-Chat-GGML llama-2-7b-chat.q4_0.bin --local-dir models
```

## 🚀 使用方法

### � メインエントリーポイント

#### 1. 🚀 クイックスタート (最も簡単)
```bash
python quick_start.py
```
- 依存関係の自動チェック・インストール
- GUI自動起動

#### 2. 🤖 メインアプリケーション (推奨)
```bash
python main.py           # 対話モード
python main.py --gui     # GUI直接起動
```

#### 3. 📱 GUI直接起動
```bash
python src/gui/batch_gui.py
```

### �🖥️ GUI バッチ処理インターフェース（推奨）

最も簡単で直感的な方法：

```bash
# GUIランチャーを起動
python src/gui/launcher.py
```

**GUIの特徴**:
- 📁 **ドラッグ&ドロップ対応**: ファイル・フォルダ選択が簡単
- 📊 **リアルタイム監視**: 進行状況・統計・ログをリアルタイム表示
- ⚙️ **直感的設定**: スライダーやチェックボックスで設定調整
- 📋 **自動レポート生成**: 処理結果を4形式で自動出力
- 🔄 **バッチ処理**: 複数ファイルを並列処理

詳細な使用方法は [GUI使用ガイド](doc/GUI_USAGE_GUIDE.md) を参照してください。

### 🚀 Enhanced API (プログラム利用)

JSONデータを入力として高度な要約処理を行う API：

```python
from src.api.enhanced_api import summarize_json, SummaryConfig

# 基本設定
config = SummaryConfig(
    language='japanese',           # 'japanese' or 'english'
    summary_type='detailed',       # 'concise', 'detailed', 'academic'
    max_length=200,               # 最大文字数
    email_notification=True,      # メール通知
    email_recipients=['user@example.com']
)

# JSON要約実行
data = {'text': 'ここに要約したいテキストを入力'}
result = summarize_json(data, config)
print(result)
```

**Enhanced API機能**:
- **JSON入力対応**: 構造化データの直接処理
- **設定可能要約**: 言語、タイプ、長さの詳細制御
- **メール通知**: 処理完了時の自動通知
- **バッチ処理**: 複数データの効率的処理

### 📧 メール通知設定

処理完了時に結果をメール送信する機能：

1. **設定ファイル準備**:
```bash
# サンプルファイルをコピー
cp .env.email.sample .env.email
cp config/email_config.yaml.sample config/email_config.yaml
```

2. **Gmail認証設定**:
   - Gmail で2段階認証を有効化
   - アプリパスワードを生成
   - `.env.email` に認証情報を設定

3. **設定ファイル編集**:
```yaml
# config/email_config.yaml
email:
  enabled: true
  sender:
    email: "your-gmail@gmail.com"
    password: "your-app-password"
  default_recipient: "recipient@example.com"
```

### 💻 コマンドライン使用法

#### 個別ファイル処理

```bash
# PDFファイルの要約
python main.py document.pdf

# HTMLファイルの要約  
python main.py webpage.html

# 出力形式とファイル指定
python main.py document.pdf -o summary.md -f markdown

# 詳細出力
python main.py document.pdf -v
```

#### 従来のCLIインターフェース

```bash
# 従来のCLIも利用可能
python src/main.py document.pdf
```

#### バッチ処理

```bash
# フォルダ内の全ファイルを並列処理
python src/batch_processing/batch_processor.py data/

# 特定の形式のみ処理
python src/batch_processing/batch_processor.py data/ --extensions .pdf .html

# 並列度を指定
python src/batch_processing/batch_processor.py data/ --workers 8

# 実際のLLMを使用したバッチ処理
python examples/batch_llm_integration.py
```

### コマンドラインオプション

- `-o, --output`: 出力ファイルパス
- `-f, --format`: 出力形式 (txt, markdown, json)
- `-m, --model`: LLMモデルファイルパス
- `-v, --verbose`: 詳細出力

## ⚙️ 設定変更方法

LocalLLMの動作設定は3つの方法で変更できます：

### 1. 🔧 環境変数ファイル（.env）- 推奨方法

`.env`ファイルで設定をカスタマイズできます：

```env
# LLM設定
DEFAULT_MODEL_PATH = "models/llama-2-7b-chat.gguf"
MAX_TOKENS = 2048
TEMPERATURE = 0.7
CONTEXT_LENGTH = 2048
N_THREADS = 4           # CPUスレッド数
N_GPU_LAYERS = 0        # GPU層数（0 = CPU専用）

# 処理設定
MAX_INPUT_LENGTH = 100000
CHUNK_SIZE = 4000
CHUNK_OVERLAP = 200

# メモリ設定
MAX_MEMORY_USAGE = 8    # GB
GPU_LAYERS = 0          # GPU層数（N_GPU_LAYERSと同じ）
```

### 2. 🐍 設定ファイル（config/settings.py）

直接Pythonファイルを編集：

```python
# config/settings.py
class Settings(BaseSettings):
    n_gpu_layers: int = Field(default=0)      # 0=CPU専用, >0=GPU使用
    n_threads: int = Field(default=4)         # CPUスレッド数
    max_memory_usage: int = Field(default=8)  # RAM使用量(GB)
    context_length: int = Field(default=2048) # コンテキスト長
```

### 3. 🚀 設定確認・変更ツール

```bash
# 現在の設定を確認
python scripts/setup/verify_cpu_setup.py

# 対話形式設定ツール
python scripts/setup/config_tool.py
```

### 💡 CPU/GPU設定ガイド

**CPU専用（デフォルト・推奨）:**
```env
N_GPU_LAYERS = 0        # すべてCPUで処理
N_THREADS = 4           # CPU並列スレッド数
MAX_MEMORY_USAGE = 8    # RAM使用量制限
```

**GPU併用（高性能GPU必要）:**
```env
N_GPU_LAYERS = 32       # GPUで処理する層数
N_THREADS = 2           # GPU併用時のCPUスレッド数
MAX_MEMORY_USAGE = 12   # RAM+VRAM使用量
```

**自動GPU検証機能:**
- GPU環境が不完全な場合、自動的にCPU専用にフォールバック
- GPU設定でエラーが発生した場合、CPU専用で再試行
- 設定ツールでGPU環境の診断と最適設定を提案

**設定値の目安:**

| GPU層数 | 動作モード | RAM必要量 | VRAM必要量 | 速度 |
|---------|-----------|-----------|------------|------|
| 0 | CPU専用 | 8-16GB | 不要 | 標準 |
| 16 | CPU+GPU | 6-8GB | 4GB以上 | 高速 |
| 32+ | GPU主体 | 4-6GB | 8GB以上 | 最高速 |

## 📁 出力ファイル管理

### 出力ディレクトリ構造

```
output/
├── batch_gui/           # GUI バッチ処理結果
│   ├── processed/       # 処理済みファイル
│   └── reports/         # 処理レポート
├── cli/                 # CLI処理結果
└── temp/               # 一時ファイル
```

### 💡 重要な注意事項

- **🚫 出力ファイルはgit管理対象外**: `output/`、`logs/`、`temp/`ディレクトリの内容はコミットされません
- **🔄 ローカル保存**: 処理結果はローカルに保存され、個人使用可能
- **🧹 定期クリーンアップ**: 不要な出力ファイルは定期的に削除することを推奨
- **📊 重要なレポート**: 必要に応じて重要な処理結果は別途バックアップしてください

### 手動クリーンアップ

```bash
# 出力ファイルをクリーンアップ
Remove-Item -Recurse -Force output/     # Windows
rm -rf output/                          # Linux/Mac

# ログファイルをクリーンアップ  
Remove-Item -Recurse -Force logs/       # Windows
rm -rf logs/                            # Linux/Mac
```

## 開発

### 開発環境のセットアップ

```bash
pip install -r requirements-dev.txt
```

### テストの実行

```bash
pytest
```

### コード品質チェック

```bash
# フォーマッティング
black src/ tests/

# リンティング
flake8 src/ tests/

# 型チェック
mypy src/
```

## プロジェクト構造

```
LocalLLM/
├── src/
│   ├── main.py                 # エントリーポイント
│   ├── document_processor.py   # ドキュメント処理
│   ├── summarizer.py          # LLM要約
│   └── utils/
│       └── logger.py          # ログ設定
├── config/
│   └── settings.py            # 設定管理
├── tests/                     # テストコード
├── doc/                       # ドキュメント
├── data/                      # データファイル
├── models/                    # LLMモデル（要ダウンロード）
├── requirements.txt           # 依存関係
└── README.md                  # このファイル
```

## トラブルシューティング

### よくある問題

1. **メモリ不足エラー**
   - `.env`の`MAX_MEMORY_USAGE`を下げる
   - `CHUNK_SIZE`を小さくする

2. **モデル読み込みエラー**
   - モデルファイルパスを確認
   - モデルファイルの破損チェック

3. **PDF読み込みエラー**
   - パスワード保護されたPDFは非対応
   - 画像のみのPDFはテキスト抽出不可

### パフォーマンス最適化

1. **GPU使用**: `.env`の`GPU_LAYERS`を増やす
2. **メモリ使用量調整**: `MAX_MEMORY_USAGE`を適切に設定
3. **並列処理**: 大量ファイル処理時はバッチ処理推奨

## ライセンス

MIT License

## 貢献

1. フォークする
2. フィーチャーブランチ作成 (`git checkout -b feature/amazing-feature`)
3. コミット (`git commit -m 'Add amazing feature'`)
4. プッシュ (`git push origin feature/amazing-feature`)
5. プルリクエスト作成

## サポート

- バグ報告: GitHub Issues
- 機能要望: GitHub Issues
- 質問: GitHub Discussions
