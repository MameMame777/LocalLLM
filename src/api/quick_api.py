#!/usr/bin/env python3
"""
LocalLLM Quick Start API
========================

最も簡単に要約機能を使うためのワンライナーAPI

使用例:
```python
# ファイル要約
from src.api.quick_api import summarize_file
result = summarize_file("document.pdf")

# テキスト要約  
from src.api.quick_api import summarize_text
result = summarize_text("長いテキスト...")

# 複数ファイル要約
from src.api.quick_api import summarize_batch
results = summarize_batch(["file1.pdf", "file2.txt"])
```
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def summarize_file(file_path, language="ja"):
    """
    ファイルを要約（最もシンプル）
    
    Args:
        file_path: ファイルパス（文字列）
        language: "ja" または "en" 
    
    Returns:
        要約結果文字列 または エラーメッセージ
    """
    try:
        from src.gui.enhanced_academic_processor import create_enhanced_academic_processing_function
        
        process_func = create_enhanced_academic_processing_function()
        result = process_func(Path(file_path), target_language=language)
        
        if isinstance(result, (str, Path)) and Path(result).exists():
            with open(result, 'r', encoding='utf-8') as f:
                return f.read()
        
        return str(result)
        
    except Exception as e:
        return f"❌ エラー: {e}"

def summarize_text(text, language="ja"):
    """
    テキストを要約（最もシンプル）
    
    Args:
        text: 要約するテキスト
        language: "ja" または "en"
    
    Returns:
        要約結果文字列 または エラーメッセージ
    """
    try:
        # 一時ファイルに保存して処理
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(text)
            temp_path = f.name
        
        try:
            result = summarize_file(temp_path, language)
            return result
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        return f"❌ エラー: {e}"

def summarize_json(json_input, language="ja", summary_config=None):
    """
    JSON形式のデータを要約（新機能）
    
    Args:
        json_input: JSONデータ（辞書、リスト、またはJSONファイルパス）
        language: "ja" または "en"
        summary_config: 要約設定辞書（省略可）
    
    Returns:
        要約結果文字列 または エラーメッセージ
    """
    try:
        import json
        import tempfile
        import os
        
        # 設定のデフォルト値
        config = {
            "summary_type": "brief",
            "max_length": None,
            "individual_processing": True,
            "include_urls": True,
            "output_format": "markdown"
        }
        
        # ユーザー設定をマージ
        if summary_config:
            config.update(summary_config)
        
        # JSON入力の処理
        if isinstance(json_input, str):
            # ファイルパスの場合
            if Path(json_input).exists():
                with open(json_input, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
            else:
                # JSON文字列の場合
                json_data = json.loads(json_input)
        else:
            # 辞書またはリストの場合
            json_data = json_input
        
        # JSONデータを一時ファイルに保存
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
            temp_path = f.name
        
        try:
            # 個別処理または通常処理の選択
            if config["individual_processing"] and isinstance(json_data, list):
                # 個別URL処理（リストの場合）
                from src.utils.individual_json_processor import IndividualJSONUrlProcessor
                processor = IndividualJSONUrlProcessor()
                result = processor.process_json_file_individually(Path(temp_path))
            else:
                # 通常のファイル処理
                result = summarize_file(temp_path, language)
            
            return result
            
        finally:
            if os.path.exists(temp_path):
                os.unlink(temp_path)
        
    except Exception as e:
        return f"❌ JSON処理エラー: {e}"

def summarize_batch(file_paths, language="ja", summary_config=None):
    """
    複数ファイルを一括要約（設定対応）
    
    Args:
        file_paths: ファイルパスのリスト
        language: "ja" または "en"
        summary_config: 要約設定辞書（省略可）
    
    Returns:
        要約結果のリスト
    """
    results = []
    
    for file_path in file_paths:
        print(f"🔄 処理中: {file_path}")
        
        # JSON ファイルの場合は専用処理
        if str(file_path).lower().endswith('.json'):
            result = summarize_json(file_path, language, summary_config)
        else:
            result = summarize_file(file_path, language)
            
        results.append({
            "file": file_path,
            "result": result,
            "status": "success" if not result.startswith("❌") else "error"
        })
    
    return results

def get_help():
    """使用方法を表示"""
    help_text = """
🚀 LocalLLM Quick API 使用方法
========================================

📄 ファイル要約:
   result = summarize_file("document.pdf")
   result = summarize_file("document.txt", "en")

📝 テキスト要約:
   result = summarize_text("長いテキスト...")
   result = summarize_text("English text", "en")

📁 一括要約:
   results = summarize_batch(["file1.pdf", "file2.txt"])

言語オプション:
   - "ja": 日本語要約（デフォルト）
   - "en": 英語要約

サポート形式:
   .pdf, .txt, .md, .html, .json, .csv, .docx
========================================
    """
    return help_text

# テスト関数
def test_api():
    """APIの動作テスト"""
    print("🧪 API動作テスト開始...")
    
    # テキスト要約テスト
    test_text = "This is a simple test text for API verification. It contains multiple sentences to test the summarization functionality."
    
    print("\n📝 テキスト要約テスト:")
    result = summarize_text(test_text, "ja")
    print(f"結果: {result[:100]}..." if len(result) > 100 else f"結果: {result}")
    
    print("\n✅ テスト完了")
    return result

if __name__ == "__main__":
    print(get_help())
    test_api()
