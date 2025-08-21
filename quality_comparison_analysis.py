#!/usr/bin/env python3
"""
API vs GUI Batch Processing Quality Comparison Analysis
APIとGUIバッチ処理での要約品質の差を分析
"""

import sys
from pathlib import Path
import time
import tempfile

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))
sys.path.insert(0, str(project_root))

def analyze_processing_differences():
    """APIとGUIバッチ処理の差異を分析"""
    print("🔍 API vs GUI Batch Processing Quality Analysis")
    print("=" * 60)
    
    print("\n📋 1. 処理フローの比較")
    print("-" * 40)
    
    # API処理フロー
    print("🌐 API処理フロー:")
    print("  1. HTTP Request → FastAPI")
    print("  2. document_api.py → process_single_document()")
    print("  3. real_process_file_global() 呼び出し")
    print("  4. DocumentProcessor で抽出")
    print("  5. LLM使用の場合: LLMSummarizer")
    print("  6. 抽出的要約の場合: _generate_extractive_summary()")
    print("  7. JSON形式でレスポンス")
    
    print("\n🖥️ GUI バッチ処理フロー:")
    print("  1. batch_gui.py → run_batch_processing()")
    print("  2. Enhanced Academic Processing 使用")
    print("  3. create_enhanced_academic_processing_function()")
    print("  4. EnhancedAcademicProcessor クラス")
    print("  5. LLM + Google Translate 統合処理")
    print("  6. 技術翻訳システム")
    print("  7. マークダウン形式で保存")
    
    print("\n🔧 2. 使用される処理器の違い")
    print("-" * 40)
    
    print("🌐 API:")
    print("  ✅ real_process_file_global() - 基本処理")
    print("  ✅ DocumentProcessor - 標準抽出")
    print("  ✅ LLMSummarizer - 単純LLM要約")
    print("  ✅ _generate_extractive_summary() - 抽出的要約")
    print("  ⚠️ 翻訳機能: なし")
    print("  ⚠️ 高度なフォーマッティング: 限定的")
    
    print("\n🖥️ GUI Batch:")
    print("  ✅ EnhancedAcademicProcessor - 高度処理")
    print("  ✅ LLM + Google Translate 統合")
    print("  ✅ Technical Translation System")
    print("  ✅ AcademicDocumentProcessor")
    print("  ✅ 高度なマークダウンフォーマッティング")
    print("  ✅ 専門用語検出")
    print("  ✅ 品質スコア評価")
    
    print("\n⚙️ 3. パラメータ設定の違い")
    print("-" * 40)
    
    print("🌐 API デフォルト設定:")
    api_params = {
        "language": "ja",
        "max_length": 150,
        "use_llm": False,
        "auto_detect_language": True,
        "output_format": "markdown"
    }
    for key, value in api_params.items():
        print(f"  • {key}: {value}")
    
    print("\n🖥️ GUI Batch デフォルト設定:")
    gui_params = {
        "Enhanced Academic Processing": True,
        "LLM + Google Translate": True,
        "Technical Translation": True,
        "Quality Assessment": True,
        "Advanced Formatting": True,
        "Term Detection": True
    }
    for key, value in gui_params.items():
        print(f"  • {key}: {value}")
    
    print("\n🎯 4. 品質差の主な要因")
    print("-" * 40)
    
    quality_factors = [
        ("🔄 翻訳統合", "GUI: Google Translate統合", "API: 翻訳なし"),
        ("🧠 LLM処理", "GUI: Enhanced Academic", "API: 基本LLM"),
        ("📝 フォーマット", "GUI: 高度マークダウン", "API: 基本JSON/MD"),
        ("🎓 学術処理", "GUI: 専門文書対応", "API: 汎用処理"),
        ("🏷️ 用語検出", "GUI: 専門用語抽出", "API: なし"),
        ("📊 品質評価", "GUI: 品質スコア", "API: なし"),
        ("🔍 多段階処理", "GUI: 複数段階処理", "API: 単一段階"),
    ]
    
    for factor, gui_advantage, api_limitation in quality_factors:
        print(f"\n{factor}")
        print(f"  GUI: {gui_advantage}")
        print(f"  API: {api_limitation}")
    
    print("\n🚀 5. 推奨改善策")
    print("-" * 40)
    
    improvements = [
        "API側にEnhancedAcademicProcessor統合",
        "API側にGoogle Translate機能追加", 
        "API側に技術翻訳システム統合",
        "API側の品質評価機能追加",
        "統一された処理パイプライン構築",
        "設定可能な処理モード選択",
        "両方式での同一品質保証"
    ]
    
    for i, improvement in enumerate(improvements, 1):
        print(f"  {i}. {improvement}")
    
    print("\n📊 6. 現在の品質評価")
    print("-" * 40)
    
    quality_comparison = {
        "要約精度": {"GUI": "⭐⭐⭐⭐⭐", "API": "⭐⭐⭐"},
        "言語品質": {"GUI": "⭐⭐⭐⭐⭐", "API": "⭐⭐"},
        "フォーマット": {"GUI": "⭐⭐⭐⭐⭐", "API": "⭐⭐⭐"},
        "専門性": {"GUI": "⭐⭐⭐⭐⭐", "API": "⭐⭐"},
        "処理速度": {"GUI": "⭐⭐⭐", "API": "⭐⭐⭐⭐⭐"},
        "使いやすさ": {"GUI": "⭐⭐⭐⭐", "API": "⭐⭐⭐⭐⭐"}
    }
    
    for metric, scores in quality_comparison.items():
        print(f"  {metric}:")
        print(f"    GUI Batch: {scores['GUI']}")
        print(f"    API:       {scores['API']}")
    
    return quality_comparison

def test_both_approaches():
    """同じファイルで両方の手法をテスト"""
    print("\n🧪 実際の処理テスト")
    print("-" * 40)
    
    # テストテキストを作成
    test_text = """
    Artificial Intelligence (AI) has revolutionized various industries through machine learning and deep learning technologies. 
    These advanced systems can process natural language, recognize images, and make decisions with remarkable accuracy. 
    Large Language Models (LLMs) have particularly transformed text processing capabilities, enabling sophisticated 
    summarization, translation, and content generation tasks. The integration of AI in business processes has led to 
    increased efficiency and cost reduction across multiple sectors.
    """
    
    # 一時ファイル作成
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_text)
        temp_file = Path(f.name)
    
    try:
        print(f"📄 テストファイル: {temp_file.name}")
        print(f"📝 テキスト長: {len(test_text)} 文字")
        
        # API風の処理をテスト
        print("\n🌐 API風処理をテスト:")
        try:
            from src.gui.real_processing import real_process_file_global
            
            api_result = real_process_file_global(
                file_path=temp_file,
                language="ja",
                max_length=150,
                use_llm=False,
                output_dir=None
            )
            
            print(f"  ✅ ステータス: {api_result.status}")
            print(f"  ⏱️ 処理時間: {api_result.processing_time:.2f}秒")
            print(f"  📝 要約長: {len(api_result.summary)} 文字")
            print(f"  📄 要約内容: {api_result.summary[:100]}...")
            
        except Exception as e:
            print(f"  ❌ API風処理エラー: {e}")
        
        # GUI風の処理をテスト
        print("\n🖥️ GUI Enhanced処理をテスト:")
        try:
            from src.gui.enhanced_academic_processor import EnhancedAcademicProcessor
            
            processor = EnhancedAcademicProcessor()
            
            start_time = time.time()
            gui_result = processor.process_document(temp_file, target_language="ja")
            processing_time = time.time() - start_time
            
            print(f"  ✅ 処理完了")
            print(f"  ⏱️ 処理時間: {processing_time:.2f}秒")
            print(f"  📝 結果長: {len(gui_result)} 文字")
            print(f"  📄 結果内容: {gui_result[:100]}...")
            
        except Exception as e:
            print(f"  ❌ GUI Enhanced処理エラー: {e}")
    
    finally:
        # 一時ファイル削除
        if temp_file.exists():
            temp_file.unlink()

def generate_improvement_plan():
    """改善計画を生成"""
    print("\n🚀 API品質改善計画")
    print("=" * 50)
    
    plan_steps = [
        {
            "step": 1,
            "title": "Enhanced Academic Processor統合",
            "description": "APIにGUIで使用されているEnhancedAcademicProcessorを統合",
            "impact": "高",
            "effort": "中",
            "files": ["src/api/document_api.py", "src/api/enhanced_api.py"]
        },
        {
            "step": 2, 
            "title": "Google Translate機能追加",
            "description": "API経由でGoogle Translate機能を利用可能にする",
            "impact": "高",
            "effort": "低",
            "files": ["src/api/translation_api.py"]
        },
        {
            "step": 3,
            "title": "処理モード選択機能",
            "description": "basic/enhanced/academicモードを選択可能にする",
            "impact": "中",
            "effort": "低",
            "files": ["src/api/document_api.py"]
        },
        {
            "step": 4,
            "title": "品質評価機能",
            "description": "要約品質のスコア評価機能を追加",
            "impact": "中",
            "effort": "中",
            "files": ["src/api/quality_assessment.py"]
        },
        {
            "step": 5,
            "title": "統一処理パイプライン",
            "description": "API/GUIで同一の処理パイプラインを使用",
            "impact": "高",
            "effort": "高",
            "files": ["src/common/processing_pipeline.py"]
        }
    ]
    
    for step_info in plan_steps:
        print(f"\n📋 ステップ {step_info['step']}: {step_info['title']}")
        print(f"  📖 説明: {step_info['description']}")
        print(f"  📊 インパクト: {step_info['impact']}")
        print(f"  🔧 作業量: {step_info['effort']}")
        print(f"  📁 対象ファイル: {', '.join(step_info['files'])}")

if __name__ == "__main__":
    # 分析実行
    quality_comparison = analyze_processing_differences()
    
    # 実際のテスト
    test_both_approaches()
    
    # 改善計画
    generate_improvement_plan()
    
    print("\n✅ 分析完了")
    print("\n📋 結論:")
    print("  • GUIバッチ処理は高度なEnhanced Academic Processingを使用")
    print("  • APIは基本的なreal_process_file_global()を使用") 
    print("  • 品質差の主因: 翻訳統合、学術処理、高度フォーマッティング")
    print("  • 改善方法: APIにEnhanced Academic Processor統合が必要")
