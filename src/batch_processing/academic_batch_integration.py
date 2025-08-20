#!/usr/bin/env python3
"""
Academic Batch Processing Integration
学術論文・技術文書特化のバッチ処理統合機能
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, Union, List
import re
from dataclasses import dataclass
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from academic.academic_processor import AcademicDocumentProcessor
from academic.academic_output_formatter import AcademicOutputFormatter
from document_processor import DocumentProcessor
from utils.language_detector import LanguageDetector


@dataclass
class AcademicBatchResult:
    """学術バッチ処理結果"""
    file_path: Path
    status: str  # "success", "error", "skipped"
    summary: str
    processing_time: float
    document_type: str  # "academic_paper", "datasheet", "technical_manual", "generic"
    academic_metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class DocumentTypeClassifier:
    """文書タイプ自動分類器"""
    
    def __init__(self):
        # 学術論文パターン
        self.academic_patterns = [
            r'abstract\b.*?(introduction|background)',
            r'(methodology|methods)\b.*?results',
            r'references?\b.*?bibliography',
            r'(doi|arxiv|pubmed)',
            r'journal\s+of|proceedings\s+of|conference\s+on',
            r'(keywords?|key\s+words?)\s*:',
            r'corresponding\s+author',
            r'(manuscript|paper)\s+(received|accepted|published)'
        ]
        
        # データシートパターン
        self.datasheet_patterns = [
            r'(datasheet|data\s+sheet)',
            r'(specifications?|specs?)\b',
            r'(electrical\s+characteristics|operating\s+conditions)',
            r'(pin\s+configuration|pinout)',
            r'(absolute\s+maximum\s+ratings)',
            r'(package\s+information|ordering\s+information)',
            r'(applications?\s+circuit|typical\s+application)',
            r'(input|output)\s+(voltage|current|impedance)',
            r'(supply\s+voltage|power\s+consumption)',
            r'(temperature\s+range|operating\s+temperature)'
        ]
        
        # 技術マニュアルパターン
        self.technical_manual_patterns = [
            r'(user\s+manual|reference\s+manual|programming\s+guide)',
            r'(installation|configuration|setup)\s+(guide|instructions)',
            r'(troubleshooting|maintenance|calibration)',
            r'(safety\s+information|warnings?|cautions?)',
            r'(getting\s+started|quick\s+start)',
            r'(software\s+installation|driver\s+installation)',
            r'(command\s+reference|api\s+reference)',
            r'(version\s+history|revision\s+history)'
        ]
    
    def classify_document(self, text: str, filename: str = "") -> str:
        """
        文書タイプを分類
        
        Args:
            text: 文書内容
            filename: ファイル名（オプション）
            
        Returns:
            文書タイプ ("academic_paper", "datasheet", "technical_manual", "generic")
        """
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # ファイル名からの推定
        if any(keyword in filename_lower for keyword in ['datasheet', 'data_sheet', 'spec', 'specification']):
            return "datasheet"
        
        if any(keyword in filename_lower for keyword in ['manual', 'guide', 'reference', 'handbook']):
            return "technical_manual"
        
        # 内容からの推定
        academic_score = sum(1 for pattern in self.academic_patterns 
                           if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE))
        
        datasheet_score = sum(1 for pattern in self.datasheet_patterns 
                            if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE))
        
        manual_score = sum(1 for pattern in self.technical_manual_patterns 
                          if re.search(pattern, text_lower, re.IGNORECASE | re.MULTILINE))
        
        # スコアリング
        scores = {
            "academic_paper": academic_score,
            "datasheet": datasheet_score,
            "technical_manual": manual_score
        }
        
        max_score = max(scores.values())
        
        # 閾値チェック
        if max_score >= 2:  # 最低2つのパターンマッチが必要
            return max(scores, key=scores.get)
        
        return "generic"


class AcademicBatchProcessor:
    """学術文書特化バッチ処理器"""
    
    def __init__(self):
        self.academic_processor = AcademicDocumentProcessor()
        self.document_processor = DocumentProcessor()
        self.language_detector = LanguageDetector()
        self.classifier = DocumentTypeClassifier()
        
        # 文書タイプ別処理設定
        self.type_specific_settings = {
            "academic_paper": {
                "max_length": 300,
                "focus_sections": ["abstract", "conclusion", "results"],
                "include_metadata": True,
                "detailed_analysis": True
            },
            "datasheet": {
                "max_length": 150,
                "focus_sections": ["specifications", "features", "applications"],
                "include_metadata": True,
                "detailed_analysis": False
            },
            "technical_manual": {
                "max_length": 200,
                "focus_sections": ["overview", "key_features", "usage"],
                "include_metadata": False,
                "detailed_analysis": False
            },
            "generic": {
                "max_length": 200,
                "focus_sections": [],
                "include_metadata": False,
                "detailed_analysis": False
            }
        }
    
    def process_file_specialized(
        self, 
        file_path: Path, 
        language: str = "ja",
        force_type: Optional[str] = None,
        custom_settings: Optional[Dict[str, Any]] = None
    ) -> AcademicBatchResult:
        """
        特化処理でファイルを処理
        
        Args:
            file_path: 処理するファイルパス
            language: 出力言語
            force_type: 強制的に指定する文書タイプ
            custom_settings: カスタム設定
            
        Returns:
            処理結果
        """
        start_time = datetime.now()
        
        try:
            # テキスト抽出
            extracted_text = self.document_processor.process_file(file_path)
            
            if not extracted_text or len(extracted_text.strip()) < 100:
                return AcademicBatchResult(
                    file_path=file_path,
                    status="error",
                    summary="",
                    processing_time=0,
                    document_type="unknown",
                    error="テキスト抽出に失敗またはコンテンツが不十分"
                )
            
            # 文書タイプ分類
            doc_type = force_type or self.classifier.classify_document(
                extracted_text, file_path.name
            )
            
            # 設定取得
            settings = self.type_specific_settings.get(doc_type, self.type_specific_settings["generic"])
            if custom_settings:
                settings.update(custom_settings)
            
            # 文書タイプ別処理
            if doc_type == "academic_paper" and settings.get("detailed_analysis", False):
                # 学術論文として詳細処理
                result = self.academic_processor.generate_academic_summary(
                    file_path,
                    language=language,
                    max_length=settings["max_length"]
                )
                
                summary = result.get("summary", "")
                academic_metadata = {
                    "structure": result.get("structure"),
                    "technical_analysis": result.get("technical_analysis"),
                    "processing_metadata": result.get("processing_metadata")
                }
                
            else:
                # 簡易特化処理
                summary = self._generate_specialized_summary(
                    extracted_text, doc_type, settings, language
                )
                academic_metadata = {
                    "document_type": doc_type,
                    "text_length": len(extracted_text),
                    "processing_approach": "simplified_specialized"
                }
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Create result
            result = AcademicBatchResult(
                file_path=file_path,
                status="success",
                summary=summary,
                processing_time=processing_time,
                document_type=doc_type,
                academic_metadata=academic_metadata
            )
            
            # Save individual file if output directory is specified in custom_settings
            if custom_settings and custom_settings.get("output_dir"):
                self._save_individual_academic_result(result, custom_settings["output_dir"], language)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return AcademicBatchResult(
                file_path=file_path,
                status="error",
                summary="",
                processing_time=processing_time,
                document_type="unknown",
                error=str(e)
            )
    
    def _generate_specialized_summary(
        self, 
        text: str, 
        doc_type: str, 
        settings: Dict[str, Any], 
        language: str
    ) -> str:
        """文書タイプ特化の簡易要約生成"""
        
        # フォーカスセクション機能を無効化し、全テキストを使用
        # 重要セクションの抽出では情報が失われる可能性があるため
        important_text = text[:10000]  # 最初の10000文字を使用（十分な情報を含む）
        
        # 言語検出
        detected_lang, _, _ = self.language_detector.detect_with_fallback(important_text)
        
        # 直接専門化要約を生成（翻訳機能は使わずに要約に集中）
        summary = self._summarize_specialized_content(important_text, doc_type, settings["max_length"])
        
        # 英語テキストで日本語要約が必要な場合のみ、追加翻訳を適用
        if language == "ja" and detected_lang != "ja" and len(summary) < 100:
            # 要約が短すぎる場合のみ翻訳機能を補助的に使用
            translated_summary = self._translate_specialized_content(important_text, doc_type)
            if len(translated_summary) > len(summary):
                summary = translated_summary
        
        return summary
    
    def _save_individual_academic_result(self, result: AcademicBatchResult, output_dir: str, language: str) -> Optional[Path]:
        """
        アカデミック処理結果を個別ファイルとして保存
        
        Args:
            result: アカデミック処理結果
            output_dir: 出力ディレクトリ
            language: 出力言語
            
        Returns:
            保存されたファイルのパス
        """
        try:
            import time
            
            output_path = Path(output_dir) / "processed"
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Generate output filename
            base_name = result.file_path.stem
            output_file = output_path / f"{base_name}_summary_{language}.md"
            
            # Create enhanced markdown content with academic metadata
            content = f"""# {result.file_path.name} - Academic Processing Result

## File Information
- **Original File**: {result.file_path.name}
- **File Size**: {result.file_path.stat().st_size / (1024 * 1024):.2f} MB
- **Processing Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}
- **Target Language**: {language}
- **Document Type**: {result.document_type}
- **Processing Time**: {result.processing_time:.2f}s

## Summary
{result.summary}

## Academic Metadata
"""
            
            # Add academic metadata if available
            if result.academic_metadata:
                for key, value in result.academic_metadata.items():
                    if value is not None:
                        content += f"- **{key}**: {value}\n"
            
            content += "\n---\n*Generated by LocalLLM Academic Batch Processor*\n"
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8', errors='replace') as f:
                f.write(content)
            
            return output_file
            
        except Exception as e:
            print(f"Failed to save academic result for {result.file_path.name}: {e}")
            return None
    
    def _extract_focused_content(self, text: str, focus_sections: List[str], doc_type: str) -> str:
        """重要セクションの抽出"""
        
        if not focus_sections:
            # セクション指定がない場合は先頭部分を使用
            return text[:2000]
        
        important_parts = []
        text_lower = text.lower()
        
        if doc_type == "datasheet":
            # データシートの重要部分抽出
            patterns = {
                "features": r'(features?|key\s+features?|highlights?)\s*:?\s*(.*?)(?=\n\s*[A-Z]|\n\s*\d+\.|\n\s*•|\Z)',
                "specifications": r'(specifications?|electrical\s+characteristics|parameters?)\s*:?\s*(.*?)(?=\n\s*[A-Z]|\n\s*\d+\.|\Z)',
                "applications": r'(applications?|typical\s+applications?|uses?)\s*:?\s*(.*?)(?=\n\s*[A-Z]|\n\s*\d+\.|\Z)'
            }
            
            for section in focus_sections:
                if section in patterns:
                    matches = re.findall(patterns[section], text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    for match in matches:
                        if isinstance(match, tuple):
                            important_parts.append(match[1])
                        else:
                            important_parts.append(match)
        
        elif doc_type == "academic_paper":
            # 学術論文の重要部分抽出
            patterns = {
                "abstract": r'(abstract)\s*:?\s*(.*?)(?=\n\s*(introduction|keywords?|1\.|\Z))',
                "conclusion": r'(conclusion|conclusions?)\s*:?\s*(.*?)(?=\n\s*(references?|bibliography|\Z))',
                "results": r'(results?|findings?)\s*:?\s*(.*?)(?=\n\s*(discussion|conclusion|\Z))'
            }
            
            for section in focus_sections:
                if section in patterns:
                    matches = re.findall(patterns[section], text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
                    for match in matches:
                        if isinstance(match, tuple):
                            important_parts.append(match[1])
                        else:
                            important_parts.append(match)
        
        # 抽出できた場合はそれを、できなかった場合は先頭部分を返す
        if important_parts:
            combined = '\n'.join(important_parts)
            return combined[:3000]  # 適切な長さに制限
        else:
            return text[:2000]
    
    def _translate_specialized_content(self, text: str, doc_type: str) -> str:
        """文書タイプ特化翻訳"""
        # 基本的な辞書ベース翻訳を使用
        translations = {
            # データシート用語
            "specifications": "仕様",
            "features": "特徴",
            "applications": "応用",
            "operating conditions": "動作条件",
            "electrical characteristics": "電気的特性",
            "pin configuration": "ピン配置",
            "package information": "パッケージ情報",
            "absolute maximum ratings": "絶対最大定格",
            
            # 学術論文用語
            "abstract": "要約",
            "introduction": "はじめに",
            "methodology": "手法",
            "results": "結果",
            "discussion": "考察",
            "conclusion": "結論",
            "references": "参考文献",
            "keywords": "キーワード",
            
            # 技術文書共通用語
            "overview": "概要",
            "description": "説明",
            "performance": "性能",
            "efficiency": "効率",
            "accuracy": "精度",
            "reliability": "信頼性"
        }
        
        # 簡易翻訳（実際の実装では、より高度な翻訳システムを使用）
        translated = text
        for en, ja in translations.items():
            translated = re.sub(r'\b' + re.escape(en) + r'\b', ja, translated, flags=re.IGNORECASE)
        
        return translated[:1000]  # 適切な長さに制限
    
    def _summarize_specialized_content(self, text: str, doc_type: str, max_length: int) -> str:
        """文書タイプ特化要約"""
        
        # 文書タイプ別の要約アプローチ
        if doc_type == "datasheet":
            summary_parts = ["【データシート要約】"]
            
            # 改行文字で正しく分割
            lines = [line.strip() for line in re.split(r'[\n\r]+', text) if line.strip() and len(line.strip()) > 3]
            
            # AD637特有の技術仕様を検索
            specs = []
            features = []
            
            for line in lines:
                lower_line = line.lower()
                # 精度、電圧、周波数などの仕様
                if any(keyword in lower_line for keyword in ['精度', 'accuracy', '電圧', 'voltage', '周波数', 'frequency', 'rms', '非直線性', 'クレスト', 'crest']):
                    if line not in specs and len(line) > 10:
                        specs.append(line)
                # 特長・機能
                elif any(keyword in lower_line for keyword in ['特長', 'feature', '機能', 'function', '計算', 'calculation', 'パワー', 'power']):
                    if line not in features and len(line) > 10:
                        features.append(line)
                        
            # 仕様セクション
            if specs:
                summary_parts.append("\n【主要仕様】")
                summary_parts.extend([f"• {spec}" for spec in specs[:5]])
                
            # 特長セクション  
            if features:
                summary_parts.append("\n【主要特長】")
                summary_parts.extend([f"• {feature}" for feature in features[:5]])
                
            # テキストから直接重要な情報を抽出
            if not specs and not features:
                important_lines = []
                for line in lines:
                    if (len(line) > 20 and 
                        any(keyword in line for keyword in ['AD637', 'RMS', '高精度', '広帯域', 'コンバータ', 'dB', 'チップ', 'ピン'])):
                        important_lines.append(line)
                        
                if important_lines:
                    summary_parts.append("\n【技術情報】")
                    summary_parts.extend([f"• {line}" for line in important_lines[:6]])
            
            summary_template = '\n'.join(summary_parts)
            
        elif doc_type == "academic_paper":
            summary_template = "【論文要約】\n"
            # 重要な文を抽出（長い文、数値を含む文を優先）
            sentences = re.split(r'[.!?]+', text)
            important_sentences = sorted(sentences, key=lambda x: len(x) + x.count('%') * 10 + x.count('result') * 5, reverse=True)
            summary_template += ' '.join(important_sentences[:3])
            
        elif doc_type == "technical_manual":
            summary_template = "【技術文書要約】\n"
            # 手順や重要ポイントを抽出
            lines = re.split(r'[\n\r]+', text)
            procedure_lines = [line for line in lines if any(keyword in line.lower() 
                                                           for keyword in ['step', 'procedure', 'important', 'note', 'warning', 'install', 'configure'])]
            summary_template += '\n'.join(procedure_lines[:4])
            
        else:
            summary_template = "【文書要約】\n"
            summary_template += text[:max_length]
        
        # 最大長に制限
        if len(summary_template) > max_length:
            summary_template = summary_template[:max_length] + "..."
        
        return summary_template


def create_academic_batch_processing_function(
    language: str = "ja",
    force_type: Optional[str] = None,
    custom_settings: Optional[Dict[str, Any]] = None,
    use_comprehensive_format: bool = True,
    include_metadata: bool = False
):
    """
    バッチ処理用の学術特化処理関数を作成
    
    Args:
        language: 出力言語
        force_type: 強制的に指定する文書タイプ
        custom_settings: カスタム設定
        use_comprehensive_format: 包括的フォーマットを使用するか
        include_metadata: メタデータを含めるか
        
    Returns:
        バッチ処理で使用可能な処理関数
    """
    processor = AcademicBatchProcessor()
    formatter = AcademicOutputFormatter()
    
    def academic_batch_process_function(file_path: Path, **kwargs) -> AcademicBatchResult:
        """バッチ処理用関数（包括的フォーマット対応）"""
        # 基本処理
        result = processor.process_file_specialized(
            file_path=file_path,
            language=language,
            force_type=force_type,
            custom_settings=custom_settings
        )
        
        # 包括的フォーマットが有効な場合、サマリーを再フォーマット
        if use_comprehensive_format and result.status == "success":
            try:
                # アカデミックメタデータから構造化サマリーを作成
                if result.academic_metadata:
                    structured_summary = formatter.create_structured_summary(result.academic_metadata)
                    comprehensive_summary = formatter.format_comprehensive_summary(
                        structured_summary, 
                        include_metadata=include_metadata
                    )
                    # 元のサマリーを包括的フォーマットで置き換え
                    result.summary = comprehensive_summary
            except Exception as e:
                # フォーマット失敗時は元のサマリーを保持
                print(f"📋 フォーマット処理エラー: {e}")
        
        return result
    
    return academic_batch_process_function


# 使用例とテスト
if __name__ == "__main__":
    # テスト用
    processor = AcademicBatchProcessor()
    
    # テストファイルがある場合
    test_files = list(Path("data").glob("*.pdf"))
    if test_files:
        print("🧪 学術特化バッチ処理テスト")
        result = processor.process_file_specialized(test_files[0])
        print(f"ファイル: {result.file_path.name}")
        print(f"文書タイプ: {result.document_type}")
        print(f"ステータス: {result.status}")
        print(f"要約: {result.summary[:200]}...")
    else:
        print("📁 テストファイルが見つかりません")
