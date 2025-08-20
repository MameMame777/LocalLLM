# 🚀 LocalLLM GUI - 実際のPDF処理ガイド

## 🎯 新機能：実際のPDF処理

LocalLLM GUIが **モック処理** から **実際のPDF要約処理** に対応しました！

---

## 📋 処理モードの選択

### 🔧 設定画面での選択項目

GUIの「📁 Configuration」タブで以下を設定できます：

#### ⚙️ 処理モード設定
- **📄 Real Processing** ✅ (チェック): 実際のPDF処理
- **📄 Real Processing** ❌ (未チェック): モック処理（テスト用）

#### 🤖 LLMモデル設定
- **🤖 Use LLM Model** ✅ (チェック): 高品質AI要約 (要モデル)
- **🤖 Use LLM Model** ❌ (未チェック): 抽出的要約 (高速)

---

## 📊 処理結果の場所と形式

### 📁 **生成される結果**

#### 1. **個別ファイル要約** (実処理時のみ)
```
output/batch_gui/processed/
├── document1_summary_ja.md
├── document2_summary_ja.md
└── document3_summary_ja.md
```

**内容例**:
```markdown
# document.pdf - Processing Result

## File Information
- **Original File**: document.pdf
- **File Size**: 1.23 MB
- **Processing Date**: 2025-08-15 19:30:00
- **Target Language**: ja

## Summary
この文書は〇〇について説明しています...
主要なポイントは以下の通りです：
• ポイント1
• ポイント2
• ポイント3

## Extracted Text
[元のテキスト内容...]
```

#### 2. **バッチ処理レポート** (常に生成)
```
output/batch_gui/reports/
├── batch_report_YYYYMMDD_HHMMSS.md    ← 詳細レポート
├── batch_report_YYYYMMDD_HHMMSS.html  ← ブラウザ表示用
├── batch_report_YYYYMMDD_HHMMSS.json  ← データ分析用
└── batch_results_YYYYMMDD_HHMMSS.csv  ← Excel等で開ける
```

---

## 🔄 処理方式の比較

| 処理モード | 処理内容 | 出力 | 速度 | 品質 |
|------------|----------|------|------|------|
| **モック処理** | テスト用模擬処理 | 統計レポートのみ | ⚡ 超高速 | - |
| **実処理 + 抽出的要約** | PDF解析 + 文章抽出 | 個別要約 + レポート | 🚀 高速 | ⭐⭐⭐ |
| **実処理 + LLM要約** | PDF解析 + AI要約 | 個別要約 + レポート | 🐌 中速 | ⭐⭐⭐⭐⭐ |

---

## 🛠️ 使用手順

### 📝 **STEP 1: 設定**
1. **📁 Configuration** タブを開く
2. **📄 Real Processing** をチェック ✅
3. **🤖 Use LLM Model** を選択（お好みで）
4. **入力フォルダ** と **出力フォルダ** を選択
5. **処理対象ファイル形式** を選択

### ⚡ **STEP 2: 処理実行**
1. **⚡ Processing** タブを開く
2. **🚀 Start Processing** をクリック
3. リアルタイムで進捗を監視

### 📋 **STEP 3: 結果確認**
1. **📋 Results** タブを開く
2. 生成されたレポートを確認
3. **📁 Open Folder** で結果フォルダを開く

---

## 🎯 実際の結果例

### ✅ **成功例（実処理）**
```
📊 Total Files: 25
✅ Successful: 23
❌ Failed: 2  
📈 Success Rate: 92.0%
⏱️ Processing Time: 2:30
```

**生成ファイル**:
- `output/batch_gui/processed/`: 23個の要約ファイル (.md)
- `output/batch_gui/reports/`: 詳細レポート (4形式)

### ⚠️ **参考（モック処理）**
```
📊 Total Files: 278
✅ Successful: 256
❌ Failed: 22
📈 Success Rate: 92.1%
⏱️ Processing Time: 1:51
```

**生成ファイル**:
- `output/batch_gui/reports/`: 統計レポートのみ

---

## 🔧 トラブルシューティング

### ❌ **LLMモデルが見つからない**
```
⚠️ No LLM model found, generating extractive summary
```
**解決**: `models/` フォルダに `.gguf` ファイルを配置

### ❌ **PDFファイルが読めない**
```
❌ Failed to process document.pdf: No text content extracted
```
**解決**: 画像PDFの場合は対応していません

### ❌ **メモリ不足**
```
❌ Processing error: Memory error
```
**解決**: ワーカー数を減らすか、LLMモードを無効化

---

## 🎉 まとめ

**実際のPDF処理が有効になり、以下が可能になりました**：

✅ **本格的なPDF要約処理**  
✅ **個別ファイル要約の生成**  
✅ **日本語要約対応**  
✅ **LLMモデル利用（オプション）**  
✅ **高速抽出的要約**  
✅ **詳細な処理レポート**  

**従来のモック処理との違い**：
- モック: 統計レポートのみ（テスト用）
- 実処理: 実際の要約 + 個別ファイル + レポート

これで LocalLLM GUI は完全な PDF バッチ処理システムとして動作します！ 🚀
