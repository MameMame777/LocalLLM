# 🎯 GUI Interface Documentation

## 概要
LocalLLM Batch Processorの使いやすいGUIインターフェースです。

## 🚀 利用可能なGUI

### 1. GUI Launcher (推奨)
**ファイル**: `src/gui/launcher.py`

全てのGUIオプションを一箇所から起動できるランチャーアプリケーション。

```bash
python src/gui/launcher.py
```

**機能**:
- 🎯 複数のGUIオプションを選択
- 📋 システム情報表示
- 📖 ドキュメントリンク
- ⚙️ 設定管理

### 2. Standard Batch GUI
**ファイル**: `src/gui/batch_gui.py`

フル機能のバッチ処理GUIインターフェース。

```bash
python src/gui/batch_gui.py
```

**主要機能**:
- 📁 **ディレクトリ選択**: 入力・出力フォルダの指定
- 🔍 **ファイルスキャン**: 対応ファイルの自動検出・プレビュー
- ⚙️ **設定管理**: 並列度、言語、要約長度の調整
- 📊 **リアルタイム監視**: 進行状況・統計・ログ表示
- 📋 **レポート管理**: 処理結果の閲覧・エクスポート

### 3. Modern GUI (実験的)
**ファイル**: `src/gui/modern_batch_gui.py`

ttkbootstrapを使用したモダンテーマのGUI。

**必要条件**:
```bash
pip install ttkbootstrap
```

**追加機能**:
- 🌙 ダークモード対応
- ✨ モダンなスタイリング
- 📊 拡張された統計表示
- 🎨 カスタムテーマ

## 📋 GUIの使用方法

### Step 1: 起動
```bash
# ランチャーから起動 (推奨)
python src/gui/launcher.py

# 直接起動
python src/gui/batch_gui.py
```

### Step 2: 設定
1. **📁 Input Directory**: 処理するファイルが入ったフォルダを選択
2. **📄 File Types**: 処理するファイル形式を選択 (PDF, HTML, TXT等)
3. **⚡ Processing Settings**: 
   - Max Workers: 並列処理数 (推奨: CPU コア数)
   - Multiprocessing: 高速化のため有効化推奨
   - Continue on Error: エラー時も処理継続
4. **🌐 Language Settings**: 
   - Target Language: 要約の言語 (ja, en, zh等)
   - Summary Length: 要約の長さ (50-500語)

### Step 3: 処理実行
1. **🔍 Scan Files**: ファイル検出とプレビュー
2. **🚀 Start Processing**: バッチ処理開始
3. **📊 Monitor Progress**: リアルタイム進行状況監視

### Step 4: 結果確認
1. **📋 Results Tab**: 処理結果サマリー確認
2. **📄 Reports**: 生成されたレポートの閲覧
3. **💾 Export**: 結果のエクスポート

## 🎨 GUI機能詳細

### Configuration Tab (⚙️)
- **Input Directory Selection**: フォルダブラウザーとドラッグ&ドロップ対応
- **File Type Filters**: チェックボックスによる形式選択
- **Processing Parameters**: スライダーによる直感的設定
- **Preview Area**: 選択ファイルのリアルタイムプレビュー

### Processing Tab (⚡)
- **Progress Bars**: 全体・個別ファイル進行状況
- **Live Statistics**: 処理速度・成功率・ETA
- **Real-time Log**: 詳細な処理ログ
- **Control Buttons**: 開始・停止・一時停止

### Results Tab (📋)
- **Summary Display**: 処理結果の概要表示
- **Report Tree**: 生成レポートの階層表示
- **Quick Actions**: レポート閲覧・フォルダオープン
- **Export Options**: 複数形式でのエクスポート

## 🔧 高度な機能

### Real-time Monitoring
- **Live Progress Tracking**: tqdmベースの美しい進行状況バー
- **Performance Metrics**: 処理速度・メモリ使用量・CPU使用率
- **Error Handling**: エラーの分類・詳細表示・回復支援

### Report Generation
- **Multi-format Output**: JSON, CSV, HTML, Markdown
- **Interactive Reports**: クリック可能なHTMLレポート
- **Export Functions**: ワンクリックでレポートフォルダオープン

### Settings Management
- **Profile Save/Load**: 設定プロファイルの保存・読み込み
- **Theme Support**: ライト・ダークモードの切り替え
- **Auto-save**: 設定の自動保存

## 🛠️ トラブルシューティング

### 一般的な問題

**1. GUIが起動しない**
```bash
# Tkinterがインストールされているか確認
python -c "import tkinter; print('Tkinter available')"

# 必要なライブラリのインストール
pip install tqdm
```

**2. ファイルが検出されない**
- 入力ディレクトリの権限を確認
- 対応ファイル形式が選択されているか確認
- ファイルサイズ制限の確認

**3. 処理が遅い**
- Max Workersの値を調整 (CPUコア数推奨)
- Multiprocessingが有効になっているか確認
- 大きなファイルを小さく分割

**4. レポートが生成されない**
- 出力ディレクトリの書き込み権限を確認
- ディスク容量の確認

### パフォーマンス最適化

**推奨設定**:
- **Max Workers**: CPUコア数と同じ値
- **Multiprocessing**: 有効
- **Continue on Error**: 有効
- **File Types**: 必要な形式のみ選択

**メモリ使用量の制御**:
- 大きなファイルが多い場合はMax Workersを減らす
- 同時処理ファイル数を制限

## 📊 システム要件

### 最小要件
- **OS**: Windows 10/11, macOS 10.14+, Linux (Ubuntu 18.04+)
- **Python**: 3.8以上
- **RAM**: 4GB以上
- **ストレージ**: 1GB以上の空き容量

### 推奨要件
- **CPU**: マルチコア (4コア以上)
- **RAM**: 8GB以上
- **ストレージ**: SSD推奨

### 依存関係
```bash
# 必須
pip install tqdm

# 推奨 (Modern GUI用)
pip install ttkbootstrap

# オプション (PDF処理用)
pip install PyPDF2 pdfplumber
```

## 🎯 今後の機能追加予定

- 📱 レスポンシブデザイン対応
- 🔄 処理履歴の管理
- 📈 詳細なパフォーマンス分析
- 🌐 Web UI版の開発
- 🤖 AI設定の最適化提案
- 📅 スケジュール処理機能
