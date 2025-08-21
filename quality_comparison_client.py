#!/usr/bin/env python3
"""
Quality Comparison Client
API vs GUI処理品質の実証比較クライアント
"""

import requests
import time
import json
from typing import Dict, Any

class QualityComparisonClient:
    """品質比較クライアント"""
    
    def __init__(self):
        self.original_api = "http://localhost:8000"
        self.enhanced_api = "http://localhost:8001"
    
    def compare_processing_quality(self, text: str) -> Dict[str, Any]:
        """処理品質を比較"""
        print("🔬 処理品質比較テスト開始")
        print("=" * 50)
        
        results = {
            "original_api": None,
            "enhanced_basic": None,
            "enhanced_enhanced": None,
            "enhanced_academic": None
        }
        
        # 1. オリジナルAPI（基本処理）
        print("\n🌐 オリジナルAPI（ポート8000）をテスト:")
        try:
            original_payload = {
                "content": text,
                "language": "ja",
                "max_length": 150,
                "use_llm": False,
                "auto_detect_language": True,
                "output_format": "markdown"
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.original_api}/api/v1/process",
                json=original_payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                processing_time = time.time() - start_time
                
                results["original_api"] = {
                    "status": result.get("status", "unknown"),
                    "summary": result.get("summary", ""),
                    "processing_time": processing_time,
                    "summary_length": len(result.get("summary", "")),
                    "api_processing_time": result.get("metadata", {}).get("processing_time", 0)
                }
                
                print(f"  ✅ 成功: {result.get('status')}")
                print(f"  ⏱️ 処理時間: {processing_time:.2f}秒")
                print(f"  📝 要約長: {len(result.get('summary', ''))} 文字")
                print(f"  📄 要約: {result.get('summary', '')[:100]}...")
                
            else:
                print(f"  ❌ エラー: HTTP {response.status_code}")
                results["original_api"] = {"error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            print(f"  ❌ 接続エラー: {e}")
            results["original_api"] = {"error": str(e)}
        
        # 2. Enhanced API - Basic Mode
        print("\n🚀 Enhanced API - Basic Mode（ポート8001）をテスト:")
        results["enhanced_basic"] = self._test_enhanced_mode(text, "basic")
        
        # 3. Enhanced API - Enhanced Mode
        print("\n⭐ Enhanced API - Enhanced Mode（ポート8001）をテスト:")
        results["enhanced_enhanced"] = self._test_enhanced_mode(text, "enhanced")
        
        # 4. Enhanced API - Academic Mode
        print("\n🎓 Enhanced API - Academic Mode（ポート8001）をテスト:")
        results["enhanced_academic"] = self._test_enhanced_mode(text, "academic")
        
        return results
    
    def _test_enhanced_mode(self, text: str, mode: str) -> Dict[str, Any]:
        """Enhanced APIの特定モードをテスト"""
        try:
            payload = {
                "content": text,
                "language": "ja",
                "max_length": 150,
                "processing_mode": mode,
                "use_llm": True,
                "enable_translation": True,
                "detect_technical_terms": True,
                "quality_assessment": True,
                "output_format": "academic",
                "include_metadata": True,
                "auto_detect_language": True
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.enhanced_api}/api/v2/process",
                json=payload,
                timeout=60
            )
            
            total_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                
                print(f"  ✅ 成功: {result.get('status')}")
                print(f"  ⏱️ 処理時間: {total_time:.2f}秒")
                print(f"  📝 要約長: {len(result.get('summary', ''))} 文字")
                print(f"  📊 品質スコア: {result.get('quality_score', 'N/A')}")
                print(f"  🏷️ 技術用語: {len(result.get('technical_terms', []))}個")
                print(f"  📄 要約: {result.get('summary', '')[:100]}...")
                
                return {
                    "status": result.get("status"),
                    "summary": result.get("summary", ""),
                    "processing_time": total_time,
                    "quality_score": result.get("quality_score"),
                    "technical_terms": result.get("technical_terms", []),
                    "translation_quality": result.get("translation_quality"),
                    "metadata": result.get("metadata", {}),
                    "summary_length": len(result.get("summary", ""))
                }
                
            else:
                error_msg = f"HTTP {response.status_code}"
                print(f"  ❌ エラー: {error_msg}")
                return {"error": error_msg}
                
        except Exception as e:
            print(f"  ❌ 接続エラー: {e}")
            return {"error": str(e)}
    
    def generate_quality_report(self, results: Dict[str, Any], original_text: str) -> str:
        """品質比較レポートを生成"""
        report = """
# 📊 LocalLLM API 品質比較レポート

## 📝 テストデータ
- **原文長**: {original_length} 文字
- **テスト日時**: {timestamp}

## 🔬 処理結果比較

""".format(
            original_length=len(original_text),
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 各結果を比較
        modes = [
            ("🌐 オリジナルAPI", "original_api"),
            ("🚀 Enhanced Basic", "enhanced_basic"),
            ("⭐ Enhanced Enhanced", "enhanced_enhanced"),
            ("🎓 Enhanced Academic", "enhanced_academic")
        ]
        
        for mode_name, mode_key in modes:
            result = results.get(mode_key)
            if result and "error" not in result:
                report += f"""
### {mode_name}

- **ステータス**: {result.get('status', 'N/A')}
- **処理時間**: {result.get('processing_time', 0):.2f}秒
- **要約長**: {result.get('summary_length', 0)} 文字
- **品質スコア**: {result.get('quality_score', 'N/A')}
- **技術用語数**: {len(result.get('technical_terms', []))}個
- **翻訳品質**: {result.get('translation_quality', 'N/A')}

**要約内容**:
```
{summary}
```

"""
                summary = result.get('summary', '')[:300]
                summary += "..." if len(result.get('summary', '')) > 300 else ""
                report = report.format(summary=summary)
                
            elif result and "error" in result:
                report += f"""
### {mode_name}

❌ **エラー**: {result['error']}

"""
            else:
                report += f"""
### {mode_name}

⚠️ **テスト未実行**

"""
        
        # 総合評価
        report += """
## 📈 総合評価

| 項目 | オリジナルAPI | Enhanced Basic | Enhanced Enhanced | Enhanced Academic |
|------|---------------|----------------|-------------------|-------------------|
"""
        
        # 評価表を生成
        metrics = ["処理時間", "要約品質", "技術対応", "総合評価"]
        for metric in metrics:
            row = f"| {metric} |"
            for mode_name, mode_key in modes:
                result = results.get(mode_key)
                if result and "error" not in result:
                    if metric == "処理時間":
                        score = "⭐⭐⭐⭐⭐" if result.get('processing_time', 999) < 5 else "⭐⭐⭐"
                    elif metric == "要約品質":
                        quality = result.get('quality_score', 0)
                        if quality > 0.8:
                            score = "⭐⭐⭐⭐⭐"
                        elif quality > 0.6:
                            score = "⭐⭐⭐⭐"
                        else:
                            score = "⭐⭐⭐"
                    elif metric == "技術対応":
                        terms = len(result.get('technical_terms', []))
                        score = "⭐⭐⭐⭐⭐" if terms > 3 else ("⭐⭐⭐" if terms > 0 else "⭐")
                    else:  # 総合評価
                        score = "⭐⭐⭐⭐⭐" if mode_key.startswith("enhanced") else "⭐⭐⭐"
                else:
                    score = "❌"
                row += f" {score} |"
            report += row + "\n"
        
        return report

def main():
    """メイン実行関数"""
    print("🚀 LocalLLM API 品質比較テスト")
    print("=" * 60)
    
    # テストテキスト
    test_text = """
    Artificial Intelligence (AI) and Machine Learning (ML) technologies have revolutionized 
    modern computing systems. Large Language Models (LLMs) like GPT and BERT have shown 
    remarkable capabilities in natural language processing tasks including text summarization, 
    translation, and content generation. These neural networks utilize transformer architectures 
    with attention mechanisms to understand contextual relationships in text data. The integration 
    of AI APIs in business applications has enabled automated document processing, intelligent 
    search systems, and real-time language translation services. Recent advances in model 
    optimization techniques have made it possible to deploy these sophisticated algorithms 
    on edge computing devices with limited computational resources.
    """
    
    # 品質比較実行
    client = QualityComparisonClient()
    
    print("⚠️ 注意: 以下のAPIサーバーが起動している必要があります:")
    print("  - オリジナルAPI: http://localhost:8000")
    print("  - Enhanced API: http://localhost:8001")
    print()
    
    results = client.compare_processing_quality(test_text)
    
    # レポート生成
    report = client.generate_quality_report(results, test_text)
    
    # レポート保存
    report_file = Path("output") / "quality_comparison_report.md"
    report_file.parent.mkdir(exist_ok=True)
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📊 品質比較レポートを保存しました: {report_file}")
    print("\n" + "=" * 60)
    print("🎯 結論:")
    
    # 簡単な結論を表示
    successful_results = {k: v for k, v in results.items() if v and "error" not in v}
    
    if len(successful_results) > 1:
        print("  ✅ 複数のAPIモードで比較が完了しました")
        
        # 品質スコア比較
        quality_scores = {k: v.get('quality_score', 0) for k, v in successful_results.items() if v.get('quality_score')}
        if quality_scores:
            best_quality = max(quality_scores.items(), key=lambda x: x[1])
            print(f"  🏆 最高品質: {best_quality[0]} (スコア: {best_quality[1]:.2f})")
        
        # 処理時間比較
        processing_times = {k: v.get('processing_time', 999) for k, v in successful_results.items()}
        if processing_times:
            fastest = min(processing_times.items(), key=lambda x: x[1])
            print(f"  ⚡ 最高速度: {fastest[0]} ({fastest[1]:.2f}秒)")
            
    else:
        print("  ⚠️ 十分な比較データが得られませんでした")
        print("  💡 APIサーバーが正常に起動しているか確認してください")

if __name__ == "__main__":
    from pathlib import Path
    main()
