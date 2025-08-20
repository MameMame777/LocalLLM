#!/usr/bin/env python3
"""
LocalLLM Configuration Tool
設定の確認と変更のためのツール
"""

import os
import sys
import argparse
from pathlib import Path
import psutil

# プロジェクトルートをパスに追加
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from config.settings import get_settings

def show_current_config():
    """現在の設定を表示"""
    print("🔧 LocalLLM 現在の設定")
    print("=" * 50)
    
    try:
        settings = get_settings()
        
        print("📋 LLM設定:")
        print(f"  🤖 モデルパス: {settings.default_model_path}")
        print(f"  🎯 最大トークン: {settings.max_tokens}")
        print(f"  🌡️ Temperature: {settings.temperature}")
        print(f"  📏 コンテキスト長: {settings.context_length}")
        
        print("\n💻 CPU/GPU設定:")
        print(f"  🖥️ GPU層数: {settings.n_gpu_layers} ({'CPU専用' if settings.n_gpu_layers == 0 else 'GPU併用'})")
        print(f"  🧵 CPUスレッド数: {settings.n_threads}")
        print(f"  💾 RAM制限: {settings.max_memory_usage}GB")
        
        print("\n📊 処理設定:")
        print(f"  📄 最大入力長: {settings.max_input_length:,} 文字")
        print(f"  📦 チャンクサイズ: {settings.chunk_size:,} 文字")
        print(f"  🔗 チャンク重複: {settings.chunk_overlap} 文字")
        
        print("\n📁 出力設定:")
        print(f"  📝 デフォルト形式: {settings.default_output_format}")
        print(f"  📂 出力ディレクトリ: {settings.output_directory}")
        
        # 環境変数の確認
        print("\n🌍 環境変数:")
        env_vars = ['N_GPU_LAYERS', 'N_THREADS', 'MAX_MEMORY_USAGE', 'GPU_LAYERS']
        for var in env_vars:
            value = os.getenv(var, '未設定')
            print(f"  {var}: {value}")
            
    except Exception as e:
        print(f"❌ 設定読み込みエラー: {e}")

def show_env_template():
    """環境変数テンプレートを表示"""
    print("\n📝 .env ファイルテンプレート")
    print("=" * 50)
    
    template = """# LLM Configuration
DEFAULT_MODEL_PATH = "models/llama-2-7b-chat.gguf"
MAX_TOKENS = 2048
TEMPERATURE = 0.7
CONTEXT_LENGTH = 2048
N_THREADS = 4
N_GPU_LAYERS = 0

# Processing Configuration  
MAX_INPUT_LENGTH = 100000
CHUNK_SIZE = 4000
CHUNK_OVERLAP = 200

# Memory Configuration
MAX_MEMORY_USAGE = 8
GPU_LAYERS = 0

# Output Configuration
DEFAULT_OUTPUT_FORMAT = "markdown"
OUTPUT_DIRECTORY = "output"
"""
    
    print(template)
    
    # .envファイルの存在確認
    env_file = Path('.env')
    if env_file.exists():
        print("✅ .envファイル: 存在します")
    else:
        print("⚠️ .envファイル: 存在しません")
        create = input("📝 .envファイルを作成しますか？ (y/N): ").lower()
        if create == 'y':
            env_file.write_text(template)
            print("✅ .envファイルを作成しました")

def check_performance_settings():
    """パフォーマンス設定をチェック"""
    print("\n⚡ パフォーマンス診断")
    print("=" * 50)
    
    settings = get_settings()
    
    # CPU設定チェック
    import psutil
    cpu_cores = psutil.cpu_count(logical=False) or 4
    cpu_threads = psutil.cpu_count(logical=True) or 8
    
    print(f"🖥️ システム情報:")
    print(f"  CPUコア数: {cpu_cores}")
    print(f"  論理プロセッサ数: {cpu_threads}")
    print(f"  設定スレッド数: {settings.n_threads}")
    
    n_threads = settings.n_threads or 4
    if n_threads > cpu_threads:
        print("  ⚠️ 設定スレッド数がシステムを超えています")
    elif n_threads <= cpu_cores:
        print("  ✅ 適切なスレッド数設定です")
    
    # メモリチェック
    ram_gb = psutil.virtual_memory().total / (1024**3)
    print(f"\n💾 メモリ情報:")
    print(f"  総RAM: {ram_gb:.1f}GB")
    print(f"  設定制限: {settings.max_memory_usage}GB")
    
    max_memory = settings.max_memory_usage or 8
    if max_memory > ram_gb * 0.8:
        print("  ⚠️ メモリ設定が高すぎる可能性があります")
    else:
        print("  ✅ 適切なメモリ設定です")
        
    # GPU/CUDA チェック
    print(f"\n🖥️ GPU/CUDA情報:")
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        device_count = torch.cuda.device_count() if cuda_available else 0
        print(f"  CUDA利用可能: {'✅ Yes' if cuda_available else '❌ No'}")
        print(f"  GPU数: {device_count}")
        if cuda_available and device_count > 0:
            for i in range(device_count):
                name = torch.cuda.get_device_name(i)
                print(f"    GPU {i}: {name}")
    except ImportError:
        print("  ❌ PyTorch未インストール")
    except Exception as e:
        print(f"  ⚠️ GPU確認エラー: {e}")
        
    # GPU設定の推奨事項
    print(f"\n🎯 推奨設定:")
    n_gpu_layers = settings.n_gpu_layers or 0
    if n_gpu_layers > 0:
        try:
            import torch
            if not torch.cuda.is_available():
                print("  ⚠️ GPU層数が設定されていますが、CUDAが利用できません")
                print("    → N_GPU_LAYERS=0 を推奨")
            else:
                print("  ✅ GPU設定が有効です")
        except ImportError:
            print("  ⚠️ GPU層数が設定されていますが、PyTorchが未インストール")
            print("    → N_GPU_LAYERS=0 を推奨")
    else:
        print("  ✅ CPU専用設定です")

def configure_gpu_settings():
    """GPU設定の対話的変更"""
    print("🖥️ GPU設定の変更")
    print("=" * 50)
    
    try:
        # GPU環境の検証
        try:
            sys.path.insert(0, str(project_root))
            from src.utils.gpu_validator import gpu_validator
            validation = gpu_validator.validate_gpu_environment()
            
            print("🔍 GPU環境の確認:")
            print(f"  CUDA利用可能: {'✅ Yes' if validation['cuda_available'] else '❌ No'}")
            print(f"  GPU数: {validation['gpu_count']}")
            
            if validation['gpu_info']:
                for gpu in validation['gpu_info']:
                    print(f"    GPU {gpu['id']}: {gpu['name']} ({gpu['memory_gb']}GB)")
                    
            print(f"\n🎯 推奨設定:")
            rec = validation['recommended_settings']
            print(f"  GPU層数: {rec['n_gpu_layers']}")
            print(f"  CPUスレッド数: {rec['n_threads']}")
            print(f"  理由: {rec['reason']}")
            
        except ImportError:
            print("⚠️ GPU検証モジュール未利用")
            validation = None
            
        # 現在の設定表示
        settings = get_settings()
        print(f"\n📋 現在の設定:")
        print(f"  GPU層数: {settings.n_gpu_layers}")
        print(f"  CPUスレッド数: {settings.n_threads}")
        
        # 設定変更の選択肢
        print(f"\n🔧 設定オプション:")
        print("1. CPU専用（推奨・安全）")
        print("2. GPU少量使用（4-8層）")
        print("3. GPU中量使用（16-24層）")
        print("4. GPU最大使用（32層）")
        print("5. カスタム設定")
        print("6. 推奨設定を適用")
        print("7. 戻る")
        
        choice = input("\n選択 (1-7): ").strip()
        
        new_settings = {}
        
        if choice == "1":
            new_settings = {"n_gpu_layers": 0, "n_threads": 4}
            print("💻 CPU専用設定を選択")
        elif choice == "2":
            new_settings = {"n_gpu_layers": 8, "n_threads": 4}
            print("🖥️ GPU少量使用設定を選択")
        elif choice == "3":
            new_settings = {"n_gpu_layers": 20, "n_threads": 2}
            print("🖥️ GPU中量使用設定を選択")
        elif choice == "4":
            new_settings = {"n_gpu_layers": 32, "n_threads": 2}
            print("🖥️ GPU最大使用設定を選択")
        elif choice == "5":
            # カスタム設定
            try:
                gpu_layers = int(input("GPU層数 (0-50): "))
                threads = int(input("CPUスレッド数 (1-16): "))
                new_settings = {"n_gpu_layers": gpu_layers, "n_threads": threads}
                print(f"🔧 カスタム設定: GPU{gpu_layers}層, CPU{threads}スレッド")
            except ValueError:
                print("❌ 無効な入力です")
                return
        elif choice == "6":
            if validation and validation['recommended_settings']:
                rec = validation['recommended_settings']
                new_settings = {
                    "n_gpu_layers": rec['n_gpu_layers'],
                    "n_threads": rec['n_threads']
                }
                print(f"🎯 推奨設定を適用: GPU{rec['n_gpu_layers']}層")
            else:
                print("❌ 推奨設定が利用できません")
                return
        elif choice == "7":
            return
        else:
            print("❌ 無効な選択です")
            return
            
        # 設定の保存
        if new_settings:
            update_env_file(new_settings)
            print(f"✅ 設定を更新しました:")
            print(f"   GPU層数: {new_settings['n_gpu_layers']}")
            print(f"   CPUスレッド数: {new_settings['n_threads']}")
            print("💡 変更を反映するには、アプリケーションを再起動してください")
            
    except Exception as e:
        print(f"❌ エラー: {e}")

def update_env_file(new_settings):
    """環境変数ファイルの更新"""
    env_path = project_root / ".env"
    
    # 既存の.envファイルを読み込み
    env_lines = []
    if env_path.exists():
        with open(env_path, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
    
    # 設定を更新
    updated_lines = []
    settings_updated = set()
    
    for line in env_lines:
        line = line.strip()
        if line.startswith("N_GPU_LAYERS") and "n_gpu_layers" in new_settings:
            updated_lines.append(f"N_GPU_LAYERS = {new_settings['n_gpu_layers']}\n")
            settings_updated.add("n_gpu_layers")
        elif line.startswith("N_THREADS") and "n_threads" in new_settings:
            updated_lines.append(f"N_THREADS = {new_settings['n_threads']}\n")
            settings_updated.add("n_threads")
        else:
            updated_lines.append(line + "\n" if line else "\n")
    
    # 新しい設定を追加（存在しない場合）
    for key, value in new_settings.items():
        if key not in settings_updated:
            if key == "n_gpu_layers":
                updated_lines.append(f"N_GPU_LAYERS = {value}\n")
            elif key == "n_threads":
                updated_lines.append(f"N_THREADS = {value}\n")
    
    # ファイルに書き込み
    with open(env_path, 'w', encoding='utf-8') as f:
        f.writelines(updated_lines)

def parse_arguments():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(description="LocalLLM Configuration Tool")
    parser.add_argument("--show-config", action="store_true", help="現在の設定を表示")
    parser.add_argument("--show-template", action="store_true", help=".envテンプレートを表示")
    parser.add_argument("--check-performance", action="store_true", help="パフォーマンス診断を実行")
    parser.add_argument("--gpu-config", action="store_true", help="GPU設定メニューを表示")
    parser.add_argument("--set-cpu-only", action="store_true", help="CPU専用設定に変更")
    parser.add_argument("--set-gpu-layers", type=int, metavar="N", help="GPU層数を設定")
    parser.add_argument("--set-threads", type=int, metavar="N", help="CPUスレッド数を設定")
    return parser.parse_args()

def quick_set_cpu_only():
    """CPU専用設定への素早い変更"""
    print("💻 CPU専用設定への変更")
    print("=" * 50)
    
    new_settings = {"n_gpu_layers": 0, "n_threads": 4}
    update_env_file(new_settings)
    
    print("✅ CPU専用設定に変更しました:")
    print("   GPU層数: 0")
    print("   CPUスレッド数: 4")
    print("💡 変更を反映するには、アプリケーションを再起動してください")

def quick_set_gpu_layers(layers: int, threads = None):
    """GPU層数の素早い設定"""
    print(f"🖥️ GPU設定の変更（{layers}層）")
    print("=" * 50)
    
    # 基本的な検証
    if layers < 0 or layers > 50:
        print("❌ GPU層数は0-50の範囲で指定してください")
        return
        
    if threads is None:
        threads = 2 if layers > 0 else 4
    
    new_settings = {"n_gpu_layers": layers, "n_threads": threads}
    
    # GPU環境確認（警告のみ）
    if layers > 0:
        try:
            import torch
            if not torch.cuda.is_available():
                print("⚠️ 警告: CUDA未対応環境でGPU設定を適用します")
                print("   エラーが発生した場合、CPU専用に自動フォールバックされます")
        except ImportError:
            print("⚠️ 警告: PyTorch未インストールでGPU設定を適用します")
    
    update_env_file(new_settings)
    
    print(f"✅ GPU設定を変更しました:")
    print(f"   GPU層数: {layers}")
    print(f"   CPUスレッド数: {threads}")
    print("💡 変更を反映するには、アプリケーションを再起動してください")

def main():
    """メイン関数"""
    args = parse_arguments()
    
    # コマンドライン引数の処理
    if args.show_config:
        show_current_config()
        return
    elif args.show_template:
        show_env_template()
        return
    elif args.check_performance:
        check_performance_settings()
        return
    elif args.set_cpu_only:
        quick_set_cpu_only()
        return
    elif args.set_gpu_layers is not None:
        quick_set_gpu_layers(args.set_gpu_layers, args.set_threads)
        return
    elif args.gpu_config:
        configure_gpu_settings()
        return
    
    # 対話モード
    print("🛠️ LocalLLM Configuration Tool")
    print("=" * 50)
    
    try:
        while True:
            print("\n📋 メニュー:")
            print("1. 📊 現在の設定を表示")
            print("2. 📝 .envテンプレートを表示/作成")
            print("3. ⚡ パフォーマンス診断")
            print("4. 🖥️ GPU設定を変更")
            print("5. ❌ 終了")
            
            choice = input("\n選択 (1-5): ").strip()
            
            if choice == "1":
                show_current_config()
            elif choice == "2":
                show_env_template()
            elif choice == "3":
                check_performance_settings()
            elif choice == "4":
                configure_gpu_settings()
            elif choice == "5":
                print("👋 設定ツールを終了します")
                break
            else:
                print("❌ 無効な選択です")
                
    except (KeyboardInterrupt, EOFError):
        print("\n👋 設定ツールを終了します")

if __name__ == "__main__":
    main()
