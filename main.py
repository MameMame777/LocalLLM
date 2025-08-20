#!/usr/bin/env python3
"""
LocalLLM - Main Entry Point
メインエントリーポイント：CLI、GUI、または対話モードを提供
"""

import sys
import argparse
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

def launch_gui():
    """GUI アプリケーションを起動"""
    try:
        from src.gui.batch_gui import main as gui_main
        print("🚀 LocalLLM GUI を起動中...")
        gui_main()
        return True
    except ImportError as e:
        print(f"❌ GUI起動エラー: {e}")
        print("💡 GUI依存関係をインストールしてください: python scripts/setup/install_dependencies.py")
        return False
    except Exception as e:
        print(f"❌ GUI実行エラー: {e}")
        return False

def launch_cli(args):
    """CLI アプリケーションを起動"""
    try:
        from src.main import main as cli_main
        print("📝 LocalLLM CLI を起動中...")
        # CLIの引数を再構築
        cli_args = []
        if hasattr(args, 'input_path') and args.input_path:
            cli_args.append(args.input_path)
        if hasattr(args, 'output') and args.output:
            cli_args.extend(['--output', args.output])
        if hasattr(args, 'format') and args.format:
            cli_args.extend(['--format', args.format])
        if hasattr(args, 'model') and args.model:
            cli_args.extend(['--model', args.model])
        if hasattr(args, 'verbose') and args.verbose:
            cli_args.append('--verbose')
        
        # CLIを呼び出し
        sys.argv = ['main'] + cli_args
        cli_main()
        return True
    except ImportError as e:
        print(f"❌ CLI起動エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ CLI実行エラー: {e}")
        return False

def interactive_mode():
    """対話モードを起動"""
    print("🤖 LocalLLM - 対話モード")
    print("=" * 50)
    
    while True:
        print("\n使用したい機能を選択してください:")
        print("1. 📱 GUI バッチ処理 (推奨)")
        print("2. 📝 CLI 単体処理")
        print("3. 🛠️ 環境セットアップ")
        print("4. ❌ 終了")
        
        choice = input("\n選択 (1-4): ").strip()
        
        if choice == "1":
            if not launch_gui():
                print("GUI起動に失敗しました。")
            break
        elif choice == "2":
            input_path = input("処理するファイルパス: ").strip()
            if input_path:
                args = argparse.Namespace(
                    input_path=input_path,
                    output=None,
                    format='markdown',
                    model=None,
                    verbose=True
                )
                launch_cli(args)
            break
        elif choice == "3":
            try:
                import subprocess
                subprocess.run([sys.executable, "scripts/setup/setup_environment.py"])
            except Exception as e:
                print(f"❌ セットアップエラー: {e}")
        elif choice == "4":
            print("👋 LocalLLMを終了します。")
            break
        else:
            print("❌ 無効な選択です。1-4を入力してください。")

def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="LocalLLM - ローカルLLMを使った文書要約・翻訳システム",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  python main.py                           # 対話モード
  python main.py --gui                     # GUI起動
  python main.py document.pdf              # CLI単体処理
  python main.py document.pdf -o output.md # CLI with 出力指定
        """
    )
    
    # モード選択
    parser.add_argument('--gui', action='store_true', 
                       help='GUI モードで起動')
    parser.add_argument('--interactive', action='store_true', 
                       help='対話モードで起動 (デフォルト)')
    
    # CLI引数
    parser.add_argument('input_path', nargs='?', 
                       help='処理するファイルパス (CLI モード)')
    parser.add_argument('--output', '-o', 
                       help='出力ファイルパス')
    parser.add_argument('--format', '-f', 
                       choices=['txt', 'markdown', 'json'], 
                       default='markdown',
                       help='出力形式 (デフォルト: markdown)')
    parser.add_argument('--model', '-m', 
                       help='LLMモデルファイルパス')
    parser.add_argument('--verbose', '-v', action='store_true', 
                       help='詳細出力')
    
    args = parser.parse_args()
    
    # モード判定と実行
    if args.gui:
        # GUI モード
        launch_gui()
    elif args.input_path:
        # CLI モード
        launch_cli(args)
    else:
        # 対話モード (デフォルト)
        interactive_mode()

if __name__ == "__main__":
    print("🤖 LocalLLM - ローカルLLM文書処理システム")
    print("=" * 50)
    main()
