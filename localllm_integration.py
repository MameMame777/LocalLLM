#!/usr/bin/env python3
"""
LocalLLM External Integration Module
外部プロジェクトからLocalLLMを簡単に使用するためのモジュール

使用例:
    from localllm_integration import LocalLLMService
    
    # 自動でサーバーを起動
    service = LocalLLMService()
    
    # テキストを要約
    result = service.summarize("長いテキスト...")
    print(result)
    
    # 終了時にサーバーを停止（自動）
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, Any, List

# LocalLLMプロジェクトのパスを動的に検出または設定
def find_localllm_project() -> Optional[Path]:
    """LocalLLMプロジェクトのパスを自動検出"""
    possible_paths = [
        Path("e:/Nautilus/workspace/pythonworks/LocalLLM"),
        Path("./LocalLLM"),
        Path("../LocalLLM"),
        Path("../../LocalLLM"),
        Path(os.getenv("LOCALLLM_PATH", "")),
    ]
    
    for path in possible_paths:
        if path.exists() and (path / "src" / "api" / "document_api.py").exists():
            return path.absolute()
    
    return None

# LocalLLMプロジェクトのパスを設定
LOCALLLM_PROJECT_ROOT = find_localllm_project()

if LOCALLLM_PROJECT_ROOT is None:
    raise ImportError(
        "LocalLLMプロジェクトが見つかりません。\n"
        "環境変数 LOCALLLM_PATH を設定するか、\n"
        "LocalLLMService(project_root='path/to/LocalLLM') で指定してください。"
    )

# LocalLLMのパスを追加
sys.path.insert(0, str(LOCALLLM_PROJECT_ROOT / "src" / "api"))

try:
    from server_controller import LocalLLMAPIServerController, LocalLLMAPIClient
except ImportError as e:
    raise ImportError(f"LocalLLM APIモジュールをインポートできません: {e}")

class LocalLLMService:
    """
    外部プロジェクト用の統一インターフェース
    
    Example:
        # 基本的な使用
        service = LocalLLMService()
        summary = service.summarize("長いテキスト...")
        
        # 詳細設定
        service = LocalLLMService(auto_start=True, use_llm=True)
        summary = service.summarize("テキスト", max_length=200)
        
        # URL処理
        summary = service.summarize_url("https://example.com/article")
        
        # バッチ処理
        results = service.summarize_batch(["text1", "text2", "text3"])
    """
    
    def __init__(self, 
                 project_root: Optional[str] = None,
                 auto_start: bool = True,
                 default_language: str = "ja",
                 default_max_length: int = 150,
                 use_llm: bool = False):
        """
        Args:
            project_root: LocalLLMプロジェクトのパス（Noneで自動検出）
            auto_start: 初期化時にサーバーを自動起動
            default_language: デフォルトの出力言語
            default_max_length: デフォルトの要約文字数
            use_llm: デフォルトでLLMを使用するか
        """
        if project_root is None:
            project_root = str(LOCALLLM_PROJECT_ROOT)
        
        self.client = LocalLLMAPIClient(project_root=project_root, auto_start=auto_start)
        self.default_language = default_language
        self.default_max_length = default_max_length
        self.default_use_llm = use_llm
        
        print(f"✅ LocalLLM Service initialized (Project: {project_root})")
    
    def summarize(self, 
                  text: str, 
                  language: Optional[str] = None,
                  max_length: Optional[int] = None,
                  use_llm: Optional[bool] = None) -> str:
        """
        テキストを要約
        
        Args:
            text: 要約するテキスト
            language: 出力言語（デフォルト: ja）
            max_length: 最大文字数（デフォルト: 150）
            use_llm: LLM使用フラグ（デフォルト: False）
        
        Returns:
            要約されたテキスト
        """
        result = self.client.summarize_text(
            text=text,
            language=language or self.default_language,
            max_length=max_length or self.default_max_length,
            use_llm=use_llm if use_llm is not None else self.default_use_llm
        )
        
        if "error" in result:
            return f"❌ 要約エラー: {result['error']}"
        
        return result.get("summary", "要約を生成できませんでした")
    
    def summarize_url(self, 
                     url: str,
                     language: Optional[str] = None,
                     max_length: Optional[int] = None,
                     use_llm: Optional[bool] = None) -> str:
        """
        URLのコンテンツを要約
        
        Args:
            url: 要約するURL
            language: 出力言語（デフォルト: ja）
            max_length: 最大文字数（デフォルト: 150）
            use_llm: LLM使用フラグ（デフォルト: False）
        
        Returns:
            要約されたテキスト
        """
        result = self.client.summarize_url(
            url=url,
            language=language or self.default_language,
            max_length=max_length or self.default_max_length,
            use_llm=use_llm if use_llm is not None else self.default_use_llm
        )
        
        if "error" in result:
            return f"❌ URL要約エラー: {result['error']}"
        
        return result.get("summary", "要約を生成できませんでした")
    
    def summarize_batch(self, 
                       texts: List[str],
                       language: Optional[str] = None,
                       max_length: Optional[int] = None,
                       use_llm: Optional[bool] = None) -> List[str]:
        """
        複数のテキストを一括要約
        
        Args:
            texts: 要約するテキストのリスト
            language: 出力言語（デフォルト: ja）
            max_length: 最大文字数（デフォルト: 150）
            use_llm: LLM使用フラグ（デフォルト: False）
        
        Returns:
            要約されたテキストのリスト
        """
        results = []
        
        for i, text in enumerate(texts):
            print(f"処理中: {i+1}/{len(texts)}")
            summary = self.summarize(text, language, max_length, use_llm)
            results.append(summary)
        
        return results
    
    def is_available(self) -> bool:
        """サービスが利用可能かチェック"""
        return self.client.controller.is_server_accessible()
    
    def get_status(self) -> Dict[str, Any]:
        """サービスの状態を取得"""
        return self.client.controller.health_check()
    
    def restart(self) -> bool:
        """サーバーを再起動"""
        return self.client.controller.restart_server()
    
    def stop(self):
        """サーバーを停止"""
        self.client.stop_server()
        print("🛑 LocalLLM Service stopped")
    
    def __enter__(self):
        """with文サポート"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """with文サポート - 自動停止"""
        self.stop()

# 簡易関数インターフェース
def quick_summarize(text: str, language: str = "ja", max_length: int = 150) -> str:
    """
    簡易要約関数（ワンライナー用）
    
    Example:
        from localllm_integration import quick_summarize
        result = quick_summarize("長いテキスト...")
    """
    with LocalLLMService() as service:
        return service.summarize(text, language, max_length)

def quick_summarize_url(url: str, language: str = "ja", max_length: int = 150) -> str:
    """
    簡易URL要約関数（ワンライナー用）
    
    Example:
        from localllm_integration import quick_summarize_url
        result = quick_summarize_url("https://example.com/article")
    """
    with LocalLLMService() as service:
        return service.summarize_url(url, language, max_length)

# 使用例とテスト
def demo_integration():
    """統合デモ"""
    print("🚀 LocalLLM External Integration Demo")
    print("=" * 50)
    
    # 1. 基本的な使用
    print("\n1. 基本的なテキスト要約:")
    service = LocalLLMService()
    
    test_text = """
    人工知能（AI）技術の発展は目覚ましく、特に機械学習と深層学習の分野で大きな進歩が見られます。
    これらの技術は、画像認識、自然言語処理、音声認識などの様々な領域で応用されており、
    私たちの日常生活にも大きな影響を与えています。特に最近では、大規模言語モデル（LLM）の
    登場により、文章の生成、要約、翻訳などのタスクで人間に匹敵する性能を示すようになりました。
    """
    
    summary = service.summarize(test_text, max_length=100)
    print(f"要約結果: {summary}")
    
    # 2. with文を使用した自動停止
    print("\n2. with文を使用した自動管理:")
    with LocalLLMService(use_llm=False) as service:
        summary = service.summarize("簡単なテストテキストです。", max_length=50)
        print(f"要約結果: {summary}")
    # ここで自動的にサーバーが停止される
    
    # 3. 簡易関数の使用
    print("\n3. 簡易関数の使用:")
    summary = quick_summarize("これは簡易関数のテストです。", max_length=30)
    print(f"簡易要約: {summary}")
    
    print("\n✅ 統合デモ完了")

if __name__ == "__main__":
    demo_integration()
