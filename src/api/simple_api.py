#!/usr/bin/env python3
"""
LocalLLM 要約API - 簡単な使用例
===============================

外部コードから要約機能を簡単に呼び出すためのサンプル
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def summarize_file_simple(file_path: str, language: str = "ja") -> dict:
    """
    ファイルを要約する最もシンプルな関数
    
    Args:
        file_path: 要約するファイルのパス
        language: 出力言語 ("ja" または "en")
    
    Returns:
        要約結果の辞書
    """
    try:
        from src.gui.enhanced_academic_processor import create_enhanced_academic_processing_function
        
        # 処理関数を作成
        process_func = create_enhanced_academic_processing_function()
        
        # ファイル処理
        result = process_func(Path(file_path), target_language=language)
        
        return {
            "status": "success",
            "file_path": file_path,
            "result": result,
            "message": "要約が完了しました"
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "file_path": file_path,
            "error": str(e),
            "message": f"要約に失敗しました: {e}"
        }

def summarize_text_simple(text: str, language: str = "ja") -> dict:
    """
    テキストを要約する最もシンプルな関数
    
    Args:
        text: 要約するテキスト
        language: 出力言語 ("ja" または "en")
    
    Returns:
        要約結果の辞書
    """
    try:
        from src.summarizer_enhanced import SummarizerEnhanced
        
        # 要約器を初期化
        summarizer = SummarizerEnhanced()
        
        # 要約実行
        if language == "ja":
            summary = summarizer.summarize_english_to_japanese(text)
        else:
            summary = summarizer.summarize_english_to_english(text)
        
        return {
            "status": "success",
            "original_length": len(text),
            "summary_length": len(summary),
            "summary": summary,
            "message": "要約が完了しました"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"要約に失敗しました: {e}"
        }

def batch_summarize_simple(file_paths: list, language: str = "ja") -> list:
    """
    複数ファイルを一括要約する最もシンプルな関数
    
    Args:
        file_paths: 要約するファイルパスのリスト
        language: 出力言語 ("ja" または "en")
    
    Returns:
        要約結果のリスト
    """
    results = []
    
    for file_path in file_paths:
        print(f"🔄 処理中: {file_path}")
        result = summarize_file_simple(file_path, language)
        results.append(result)
        
        if result["status"] == "success":
            print(f"✅ 完了: {file_path}")
        else:
            print(f"❌ 失敗: {file_path} - {result['message']}")
    
    return results

# 使用例
if __name__ == "__main__":
    print("🚀 LocalLLM 要約API テスト")
    print("=" * 40)
    
    # テキスト要約の例
    print("\n📝 テキスト要約テスト:")
    test_text = """
    This is a sample text for testing the summarization API.
    It contains multiple sentences to demonstrate how the API works.
    The text will be summarized into a shorter version while maintaining the key information.
    """
    
    result = summarize_text_simple(test_text, "ja")
    print(f"状態: {result['status']}")
    if result['status'] == 'success':
        print(f"要約: {result['summary']}")
    else:
        print(f"エラー: {result['message']}")
    
    print("\n🔍 利用可能な関数:")
    print("- summarize_file_simple(file_path, language='ja')")
    print("- summarize_text_simple(text, language='ja')")  
    print("- batch_summarize_simple(file_paths, language='ja')")
    
    print("\n✅ テスト完了")
