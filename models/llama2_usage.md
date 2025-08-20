
# Llama 2 7B使用方法

## モデル情報
- ファイル: llama-2-7b-chat.Q4_K_M.gguf
- サイズ: 3.80 GB
- 説明: バランスの取れた品質と速度

## 使用方法

### 環境変数で指定:
```bash
$env:DEFAULT_MODEL_PATH="models/llama-2-7b-chat.Q4_K_M.gguf"
python -m src.main input_file.pdf --format markdown
```

### 設定ファイル更新:
config/settings.pyの default_model_path を更新

## 多言語機能
- 英語→日本語要約
- 日本語→英語翻訳
- 複数言語の文書処理

## パフォーマンス
- RAM使用量: 8-12GB
- 処理時間: TinyLlamaより遅いが高品質
- GPU加速: 利用可能（n_gpu_layers > 0）
