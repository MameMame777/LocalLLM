#!/usr/bin/env python3
"""
LocalLLM Summarization API
==========================

外部コードから要約機能を簡単に利用するためのAPIインターフェース

使用例:
```python
from src.api.summarization_api import SummarizationAPI

# 初期化
summarizer = SummarizationAPI()

# ファイル要約
result = summarizer.summarize_file("document.pdf", target_language="ja")

# テキスト要約
result = summarizer.summarize_text("長い文章...", target_language="en")

# バッチ要約
results = summarizer.summarize_batch(["file1.pdf", "file2.txt"])
```
"""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
import sys
import os

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.gui.enhanced_academic_processor import EnhancedAcademicProcessor
from src.document_processor import DocumentProcessor
from src.summarizer_enhanced import SummarizerEnhanced

logger = logging.getLogger(__name__)

class SummarizationAPI:
    """要約機能の統一APIインターフェース"""
    
    def __init__(self, model_path: Optional[str] = None):
        """
        API初期化
        
        Args:
            model_path: LLMモデルのパス（省略時はデフォルト）
        """
        self.model_path = model_path
        self._processor = None
        self._document_processor = None
        self._summarizer = None
        self._initialized = False
        
        logger.info("🚀 SummarizationAPI initialized")
    
    def _ensure_initialized(self):
        """遅延初期化（初回使用時に初期化）"""
        if self._initialized:
            return
            
        try:
            # Enhanced Academic Processor
            self._processor = EnhancedAcademicProcessor()
            
            # Document Processor  
            self._document_processor = DocumentProcessor()
            
            # Summarizer Enhanced
            self._summarizer = SummarizerEnhanced(model_path=self.model_path)
            
            self._initialized = True
            logger.info("✅ SummarizationAPI components initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize API components: {e}")
            raise
    
    def summarize_file(
        self, 
        file_path: Union[str, Path], 
        target_language: str = "ja",
        summary_type: str = "brief",
        output_dir: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        ファイルを要約
        
        Args:
            file_path: 要約するファイルのパス
            target_language: 出力言語 ("ja", "en") 
            summary_type: 要約タイプ ("brief", "detailed", "academic")
            output_dir: 出力ディレクトリ（省略時は自動）
            
        Returns:
            要約結果の辞書
        """
        self._ensure_initialized()
        
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        logger.info(f"📄 Summarizing file: {file_path}")
        
        try:
            # Enhanced Academic Processor使用
            from src.gui.enhanced_academic_processor import create_enhanced_academic_processing_function
            
            process_func = create_enhanced_academic_processing_function()
            
            # 処理実行
            result_path = process_func(
                file_path, 
                target_language=target_language,
                summary_type=summary_type
            )
            
            # 結果読み込み
            if isinstance(result_path, (str, Path)) and Path(result_path).exists():
                with open(result_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = str(result_path)
            
            result = {
                "status": "success",
                "file_path": str(file_path),
                "target_language": target_language,
                "summary_type": summary_type,
                "content": content,
                "output_path": str(result_path) if isinstance(result_path, Path) else None,
                "processing_status": "Success"
            }
            
            logger.info(f"✅ File summarization completed: {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to summarize file {file_path}: {e}")
            return {
                "status": "error",
                "file_path": str(file_path),
                "error": str(e),
                "processing_status": "Failed"
            }
    
    def summarize_text(
        self, 
        text: str, 
        target_language: str = "ja",
        summary_type: str = "brief"
    ) -> Dict[str, Any]:
        """
        テキストを直接要約
        
        Args:
            text: 要約するテキスト
            target_language: 出力言語 ("ja", "en")
            summary_type: 要約タイプ ("brief", "detailed", "academic")
            
        Returns:
            要約結果の辞書
        """
        self._ensure_initialized()
        
        logger.info(f"📝 Summarizing text ({len(text)} chars)")
        
        try:
            # 直接要約実行
            if target_language == "ja":
                summary = self._summarizer.summarize_english_to_japanese(text, summary_type)
            else:
                summary = self._summarizer.summarize_english_to_english(text, summary_type)
            
            result = {
                "status": "success",
                "input_length": len(text),
                "target_language": target_language,
                "summary_type": summary_type,
                "summary": summary,
                "compression_ratio": len(summary) / len(text) if text else 0,
                "processing_status": "Success"
            }
            
            logger.info(f"✅ Text summarization completed ({len(summary)} chars)")
            return result
            
        except Exception as e:
            logger.error(f"❌ Failed to summarize text: {e}")
            return {
                "status": "error",
                "input_length": len(text),
                "error": str(e),
                "processing_status": "Failed"
            }
    
    def summarize_batch(
        self, 
        file_paths: List[Union[str, Path]], 
        target_language: str = "ja",
        summary_type: str = "brief",
        max_workers: int = 2
    ) -> List[Dict[str, Any]]:
        """
        複数ファイルを一括要約
        
        Args:
            file_paths: 要約するファイルのパスリスト
            target_language: 出力言語
            summary_type: 要約タイプ
            max_workers: 並列処理数
            
        Returns:
            要約結果のリスト
        """
        self._ensure_initialized()
        
        logger.info(f"📁 Batch summarizing {len(file_paths)} files")
        
        results = []
        for file_path in file_paths:
            result = self.summarize_file(
                file_path, 
                target_language=target_language,
                summary_type=summary_type
            )
            results.append(result)
        
        success_count = sum(1 for r in results if r["status"] == "success")
        logger.info(f"✅ Batch summarization completed: {success_count}/{len(file_paths)} successful")
        
        return results
    
    def get_supported_formats(self) -> List[str]:
        """サポートされているファイル形式を取得"""
        return [".pdf", ".txt", ".md", ".html", ".json", ".csv", ".docx"]
    
    def get_supported_languages(self) -> List[str]:
        """サポートされている言語を取得"""
        return ["ja", "en"]
    
    def get_summary_types(self) -> List[str]:
        """サポートされている要約タイプを取得"""
        return ["brief", "detailed", "academic", "concise"]
    
    def health_check(self) -> Dict[str, Any]:
        """APIの動作確認"""
        try:
            self._ensure_initialized()
            
            # 簡単なテスト要約
            test_result = self.summarize_text(
                "This is a simple test text for API health check.", 
                target_language="en"
            )
            
            return {
                "status": "healthy",
                "initialized": self._initialized,
                "test_result": test_result["status"],
                "supported_formats": self.get_supported_formats(),
                "supported_languages": self.get_supported_languages(),
                "summary_types": self.get_summary_types()
            }
            
        except Exception as e:
            return {
                "status": "unhealthy", 
                "error": str(e)
            }


# 簡単な使用例とテスト関数
def demo_usage():
    """API使用例のデモ"""
    print("🚀 SummarizationAPI Demo")
    print("=" * 50)
    
    # API初期化
    api = SummarizationAPI()
    
    # ヘルスチェック
    print("🔍 Health Check:")
    health = api.health_check()
    print(f"Status: {health['status']}")
    
    if health['status'] == 'healthy':
        # テキスト要約
        print("\n📝 Text Summarization:")
        result = api.summarize_text(
            "This is a sample text that will be summarized. It contains multiple sentences to demonstrate the summarization capability of the API.", 
            target_language="ja"
        )
        print(f"Status: {result['status']}")
        if result['status'] == 'success':
            print(f"Summary: {result['summary'][:100]}...")
    
    print("\n✅ Demo completed")

if __name__ == "__main__":
    demo_usage()
