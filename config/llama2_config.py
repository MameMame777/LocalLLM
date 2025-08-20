# Llama 2 7B Model Configuration
import os
from pathlib import Path

# プロジェクトルート取得
PROJECT_ROOT = Path(__file__).parent.parent
LLAMA2_MODEL_PATH = PROJECT_ROOT / "models" / "llama-2-7b-chat.Q4_K_M.gguf"

# モデル設定
MODEL_NAME = "Llama-2-7B-Chat"
MODEL_TYPE = "Llama2-7B"
MULTILINGUAL_SUPPORT = True
RECOMMENDED_RAM = "8-12GB"

# 生成パラメータ設定
LLAMA2_GENERATION_CONFIG = {
    "n_ctx": 4096,           # コンテキスト長
    "n_threads": 8,          # スレッド数
    "temperature": 0.7,      # 創造性（0.0-1.0）
    "top_p": 0.9,           # Top-p サンプリング
    "top_k": 40,            # Top-k サンプリング
    "repeat_penalty": 1.1,   # 繰り返しペナルティ
    "max_tokens": 512,       # 最大生成トークン数
    "verbose": False,        # 詳細ログ
}
