#!/usr/bin/env python3
"""
LocalLLM API Server Controller
別プロジェクトからAPIサーバーを起動・制御するためのコントローラー
"""

import subprocess
import time
import requests
import signal
import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
import threading
import atexit

class LocalLLMAPIServerController:
    """LocalLLM APIサーバーのコントローラー"""
    
    def __init__(self, project_root: Optional[str] = None):
        """
        Args:
            project_root: LocalLLMプロジェクトのルートディレクトリ
        """
        if project_root is None:
            # デフォルトのプロジェクトパス
            self.project_root = Path("e:/Nautilus/workspace/pythonworks/LocalLLM")
        else:
            self.project_root = Path(project_root)
        
        self.api_script = self.project_root / "src" / "api" / "document_api.py"
        self.base_url = "http://localhost:8000"
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        
        # 終了時にサーバーを停止
        atexit.register(self.stop_server)
    
    def is_server_accessible(self) -> bool:
        """APIサーバーにアクセス可能かチェック"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=3)
            return response.status_code == 200
        except:
            return False
    
    def start_server(self, wait_for_startup: bool = True, timeout: int = 30) -> bool:
        """
        APIサーバーを起動
        
        Args:
            wait_for_startup: 起動完了まで待機するか
            timeout: 起動タイムアウト（秒）
        
        Returns:
            起動成功かどうか
        """
        if self.is_server_accessible():
            print("⚠️ APIサーバーは既に起動しています")
            return True
        
        if not self.api_script.exists():
            print(f"❌ APIスクリプトが見つかりません: {self.api_script}")
            return False
        
        try:
            print(f"🚀 APIサーバーを起動中... ({self.api_script})")
            
            # サーバープロセスを起動
            self.process = subprocess.Popen(
                [sys.executable, str(self.api_script)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0
            )
            
            self.is_running = True
            
            if wait_for_startup:
                return self._wait_for_server_startup(timeout)
            else:
                return True
                
        except Exception as e:
            print(f"❌ サーバー起動エラー: {e}")
            return False
    
    def _wait_for_server_startup(self, timeout: int) -> bool:
        """サーバーの起動完了を待機"""
        print(f"⏳ サーバーの起動を待機中（最大{timeout}秒）...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_server_accessible():
                print("✅ APIサーバーが起動しました")
                return True
            
            # プロセスが終了していないかチェック
            if self.process and self.process.poll() is not None:
                stdout, stderr = self.process.communicate()
                print(f"❌ サーバープロセスが異常終了しました")
                print(f"STDOUT: {stdout.decode() if stdout else 'なし'}")
                print(f"STDERR: {stderr.decode() if stderr else 'なし'}")
                return False
            
            print(".", end="", flush=True)
            time.sleep(1)
        
        print(f"\n❌ サーバー起動がタイムアウトしました（{timeout}秒）")
        return False
    
    def stop_server(self) -> bool:
        """APIサーバーを停止"""
        if not self.is_running or not self.process:
            return True
        
        try:
            print("🛑 APIサーバーを停止中...")
            
            if os.name == 'nt':  # Windows
                self.process.send_signal(signal.CTRL_BREAK_EVENT)
            else:  # Unix/Linux
                self.process.send_signal(signal.SIGTERM)
            
            # プロセス終了を待機
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                print("⚠️ 正常終了がタイムアウト、強制終了します")
                self.process.kill()
                self.process.wait()
            
            self.is_running = False
            self.process = None
            print("✅ APIサーバーを停止しました")
            return True
            
        except Exception as e:
            print(f"❌ サーバー停止エラー: {e}")
            return False
    
    def restart_server(self, timeout: int = 30) -> bool:
        """APIサーバーを再起動"""
        print("🔄 APIサーバーを再起動中...")
        self.stop_server()
        time.sleep(2)  # 少し待機
        return self.start_server(wait_for_startup=True, timeout=timeout)
    
    def get_server_info(self) -> Dict[str, Any]:
        """APIサーバーの情報を取得"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """ヘルスチェック"""
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            if response.status_code == 200:
                return response.json()
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}

# ユーティリティクラス：簡単な使用のため
class LocalLLMAPIClient:
    """シンプルなAPIクライアント（サーバー制御機能付き）"""
    
    def __init__(self, project_root: Optional[str] = None, auto_start: bool = True):
        """
        Args:
            project_root: LocalLLMプロジェクトのルートディレクトリ
            auto_start: 初期化時に自動でサーバーを起動するか
        """
        self.controller = LocalLLMAPIServerController(project_root)
        self.base_url = self.controller.base_url
        
        if auto_start:
            self.ensure_server_running()
    
    def ensure_server_running(self) -> bool:
        """サーバーが起動していることを確認（必要に応じて起動）"""
        if not self.controller.is_server_accessible():
            return self.controller.start_server()
        return True
    
    def summarize_text(self, text: str, language: str = "ja", 
                      max_length: int = 150, use_llm: bool = False) -> Dict[str, Any]:
        """テキストを要約"""
        if not self.ensure_server_running():
            return {"error": "APIサーバーが利用できません"}
        
        payload = {
            "content": text,
            "language": language,
            "max_length": max_length,
            "use_llm": use_llm,
            "auto_detect_language": True,
            "output_format": "markdown"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/process",
                json=payload,
                timeout=60
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def summarize_url(self, url: str, language: str = "ja", 
                     max_length: int = 150, use_llm: bool = False) -> Dict[str, Any]:
        """URLのコンテンツを要約"""
        if not self.ensure_server_running():
            return {"error": "APIサーバーが利用できません"}
        
        payload = {
            "url": url,
            "language": language,
            "max_length": max_length,
            "use_llm": use_llm,
            "auto_detect_language": True,
            "output_format": "markdown"
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/process",
                json=payload,
                timeout=120
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}
    
    def stop_server(self):
        """サーバーを停止"""
        self.controller.stop_server()

def demo_usage():
    """使用例のデモ"""
    print("🚀 LocalLLM API Server Controller Demo")
    print("=" * 50)
    
    # 1. サーバーコントローラーのデモ
    print("\n1. サーバーコントローラーのテスト:")
    controller = LocalLLMAPIServerController()
    
    # サーバー起動
    if controller.start_server():
        print("✅ サーバー起動成功")
        
        # ヘルスチェック
        health = controller.health_check()
        print(f"ヘルスチェック: {health}")
        
        # サーバー情報取得
        info = controller.get_server_info()
        print(f"サーバー情報: {info}")
        
        # サーバー停止
        controller.stop_server()
    else:
        print("❌ サーバー起動失敗")
    
    # 2. 簡易クライアントのデモ
    print("\n2. 簡易クライアントのテスト:")
    client = LocalLLMAPIClient(auto_start=True)
    
    # テキスト要約
    result = client.summarize_text(
        "人工知能技術の発展により、様々な分野で自動化が進んでいます。特に自然言語処理の分野では大きな進歩が見られます。",
        language="ja",
        max_length=100
    )
    
    if "error" not in result:
        print(f"✅ テキスト要約成功: {result.get('summary', 'N/A')}")
    else:
        print(f"❌ テキスト要約失敗: {result['error']}")
    
    # クリーンアップ
    client.stop_server()
    
    print("\n✅ デモ完了")

if __name__ == "__main__":
    demo_usage()
