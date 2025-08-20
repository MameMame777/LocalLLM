"""
Academic Output Formatter
包括的な学術文書の出力フォーマット生成
"""

from pathlib import Path
from typing import Dict, Any, List
import json
from datetime import datetime

class AcademicOutputFormatter:
    """学術文書の包括的出力フォーマット生成クラス"""
    
    def __init__(self):
        self.template_sections = {
            'structure': '📊 文書構造分析',
            'technical': '🔬 技術的詳細',
            'findings': '💡 主要な発見',
            'applications': '🎯 応用分野',
            'limitations': '⚠️ 制約・限界',
            'metadata': '📋 文書メタデータ'
        }
    
    def format_technical_japanese_summary(self, translation_data: Dict[str, Any]) -> str:
        """
        技術文書の英日翻訳結果を包括的にフォーマット
        
        Args:
            translation_data: 技術翻訳処理結果辞書
            
        Returns:
            フォーマットされた日本語技術要約
        """
        output_lines = []
        
        # ヘッダー情報
        doc_type_jp = {
            'datasheet': 'データシート',
            'academic_paper': '学術論文',
            'technical_report': '技術レポート',
            'manual': '技術マニュアル',
            'patent': '特許文書',
            'technical_document': '技術文書'
        }.get(translation_data.get('document_type', 'unknown'), '技術文書')
        
        output_lines.append(f"# 📚 {doc_type_jp}翻訳レポート")
        output_lines.append(f"**処理日時:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 品質情報
        quality_jp = {
            'good': '良好',
            'fair': '普通',
            'poor': '要改善'
        }.get(translation_data.get('translation_quality', 'unknown'), '不明')
        
        confidence_score = translation_data.get('quality_score', translation_data.get('confidence_score', 0.0))
        confidence_percent = f"{confidence_score * 100:.1f}%"
        
        processing_time = translation_data.get('processing_time', 0)
        
        output_lines.append(f"**翻訳品質:** {quality_jp} (信頼度: {confidence_percent})")
        output_lines.append(f"**処理時間:** {processing_time:.2f}秒")
        output_lines.append("")
        
        # メイン翻訳内容
        output_lines.append("## 📄 日本語翻訳")
        main_translation = translation_data.get('japanese_translation', '翻訳結果がありません。')
        output_lines.append(main_translation)
        output_lines.append("")
        
        # 主要貢献
        if translation_data.get('main_contribution'):
            output_lines.append("## 💡 主要貢献・特徴")
            output_lines.append(translation_data['main_contribution'])
            output_lines.append("")
        
        # 主要発見
        key_findings = translation_data.get('key_findings', [])
        if key_findings:
            output_lines.append("## 🔍 主要発見・結果")
            for i, finding in enumerate(key_findings[:5], 1):
                output_lines.append(f"{i}. {finding}")
            output_lines.append("")
        
        # 技術詳細
        technical_details = translation_data.get('technical_details', [])
        if technical_details:
            output_lines.append("## ⚙️ 技術詳細")
            for i, detail in enumerate(technical_details[:5], 1):
                output_lines.append(f"**詳細{i}:** {detail}")
            output_lines.append("")
        
        # 実用的応用
        applications = translation_data.get('practical_applications', [])
        if applications:
            output_lines.append("## 🎯 実用的応用・用途")
            for i, app in enumerate(applications[:3], 1):
                output_lines.append(f"- {app}")
            output_lines.append("")
        
        # 数学的概念
        math_concepts = translation_data.get('mathematical_concepts', [])
        if math_concepts:
            output_lines.append("## 🧮 数学的概念・手法")
            for concept in math_concepts[:5]:
                output_lines.append(f"- {concept}")
            output_lines.append("")
        
        # 検出された技術用語
        technical_terms = translation_data.get('technical_terms_found', [])
        if technical_terms:
            output_lines.append("## 🔤 検出技術用語")
            terms_display = ", ".join(technical_terms[:10])
            if len(technical_terms) > 10:
                terms_display += f" など（{len(technical_terms)}語検出）"
            output_lines.append(terms_display)
            output_lines.append("")
        
        # 手法要約
        if translation_data.get('methodology_summary'):
            output_lines.append("## 📋 手法・方法論要約")
            output_lines.append(translation_data['methodology_summary'])
            output_lines.append("")
        
        # 処理メタデータ
        metadata = translation_data.get('processing_metadata', {})
        if metadata:
            output_lines.append("## 📊 処理情報")
            output_lines.append(f"**技術レベル:** {metadata.get('technical_level', '不明')}")
            output_lines.append(f"**文書分類:** {metadata.get('document_classification', '不明')}")
            output_lines.append(f"**検出用語数:** {metadata.get('terms_detected', 0)}語")
            if metadata.get('file_path'):
                output_lines.append(f"**ファイルパス:** {metadata['file_path']}")
            output_lines.append("")
        
        return "\n".join(output_lines)
    
    def format_comprehensive_summary(self, summary_data: Dict[str, Any], 
                                   include_metadata: bool = False) -> str:
        """包括的な学術サマリーをフォーマット"""
        
        output_lines = []
        
        # ヘッダー情報
        output_lines.append("# 📚 学術文書解析レポート")
        output_lines.append(f"**生成日時:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output_lines.append("")
        
        # 基本情報
        if 'basic_info' in summary_data:
            basic = summary_data['basic_info']
            output_lines.append("## 📄 基本情報")
            if 'title' in basic:
                output_lines.append(f"**タイトル:** {basic['title']}")
            if 'document_type' in basic:
                output_lines.append(f"**文書種別:** {basic['document_type']}")
            if 'language' in basic:
                output_lines.append(f"**言語:** {basic['language']}")
            output_lines.append("")
        
        # 要約
        if 'summary' in summary_data:
            output_lines.append("## 📝 要約")
            output_lines.append(summary_data['summary'])
            output_lines.append("")
        
        # 構造分析
        if 'structure_analysis' in summary_data:
            structure = summary_data['structure_analysis']
            output_lines.append(f"## {self.template_sections['structure']}")
            
            if 'sections' in structure:
                output_lines.append("### 📋 セクション構成")
                for i, section in enumerate(structure['sections'], 1):
                    output_lines.append(f"{i}. {section}")
                output_lines.append("")
            
            if 'content_organization' in structure:
                output_lines.append("### 🗂️ 内容構成")
                output_lines.append(structure['content_organization'])
                output_lines.append("")
            
            if 'document_flow' in structure:
                output_lines.append("### 🔄 論理的流れ")
                output_lines.append(structure['document_flow'])
                output_lines.append("")
        
        # 技術的詳細
        if 'technical_details' in summary_data:
            technical = summary_data['technical_details']
            output_lines.append(f"## {self.template_sections['technical']}")
            
            if 'methodologies' in technical:
                output_lines.append("### 🔬 手法・方法論")
                if isinstance(technical['methodologies'], list):
                    for method in technical['methodologies']:
                        output_lines.append(f"- {method}")
                else:
                    output_lines.append(technical['methodologies'])
                output_lines.append("")
            
            if 'technologies' in technical:
                output_lines.append("### 💻 技術・技術仕様")
                if isinstance(technical['technologies'], list):
                    for tech in technical['technologies']:
                        output_lines.append(f"- {tech}")
                else:
                    output_lines.append(technical['technologies'])
                output_lines.append("")
            
            if 'data_analysis' in technical:
                output_lines.append("### 📈 データ分析")
                output_lines.append(technical['data_analysis'])
                output_lines.append("")
        
        # 主要な発見
        if 'key_findings' in summary_data:
            findings = summary_data['key_findings']
            output_lines.append(f"## {self.template_sections['findings']}")
            
            if 'main_results' in findings:
                output_lines.append("### 🎯 主な結果")
                if isinstance(findings['main_results'], list):
                    for i, result in enumerate(findings['main_results'], 1):
                        output_lines.append(f"{i}. {result}")
                else:
                    output_lines.append(findings['main_results'])
                output_lines.append("")
            
            if 'innovations' in findings:
                output_lines.append("### ✨ 革新的要素")
                if isinstance(findings['innovations'], list):
                    for innovation in findings['innovations']:
                        output_lines.append(f"- {innovation}")
                else:
                    output_lines.append(findings['innovations'])
                output_lines.append("")
            
            if 'significance' in findings:
                output_lines.append("### 🌟 意義・重要性")
                output_lines.append(findings['significance'])
                output_lines.append("")
        
        # 応用分野
        if 'applications' in summary_data:
            applications = summary_data['applications']
            output_lines.append(f"## {self.template_sections['applications']}")
            
            if 'practical_uses' in applications:
                output_lines.append("### 🔧 実用的応用")
                if isinstance(applications['practical_uses'], list):
                    for use in applications['practical_uses']:
                        output_lines.append(f"- {use}")
                else:
                    output_lines.append(applications['practical_uses'])
                output_lines.append("")
            
            if 'industries' in applications:
                output_lines.append("### 🏭 対象産業")
                if isinstance(applications['industries'], list):
                    for industry in applications['industries']:
                        output_lines.append(f"- {industry}")
                else:
                    output_lines.append(applications['industries'])
                output_lines.append("")
            
            if 'future_potential' in applications:
                output_lines.append("### 🚀 将来の可能性")
                output_lines.append(applications['future_potential'])
                output_lines.append("")
        
        # 制約・限界
        if 'limitations' in summary_data:
            limitations = summary_data['limitations']
            output_lines.append(f"## {self.template_sections['limitations']}")
            
            if 'technical_limitations' in limitations:
                output_lines.append("### ⚙️ 技術的制約")
                if isinstance(limitations['technical_limitations'], list):
                    for limitation in limitations['technical_limitations']:
                        output_lines.append(f"- {limitation}")
                else:
                    output_lines.append(limitations['technical_limitations'])
                output_lines.append("")
            
            if 'scope_limitations' in limitations:
                output_lines.append("### 📏 適用範囲の制限")
                output_lines.append(limitations['scope_limitations'])
                output_lines.append("")
            
            if 'future_work' in limitations:
                output_lines.append("### 🔮 今後の課題")
                if isinstance(limitations['future_work'], list):
                    for work in limitations['future_work']:
                        output_lines.append(f"- {work}")
                else:
                    output_lines.append(limitations['future_work'])
                output_lines.append("")
        
        # メタデータ（オプション）
        if include_metadata and 'metadata' in summary_data:
            metadata = summary_data['metadata']
            output_lines.append(f"## {self.template_sections['metadata']}")
            
            if 'file_info' in metadata:
                output_lines.append("### 📁 ファイル情報")
                file_info = metadata['file_info']
                for key, value in file_info.items():
                    output_lines.append(f"- **{key}:** {value}")
                output_lines.append("")
            
            if 'processing_info' in metadata:
                output_lines.append("### ⚙️ 処理情報")
                proc_info = metadata['processing_info']
                for key, value in proc_info.items():
                    output_lines.append(f"- **{key}:** {value}")
                output_lines.append("")
        
        # フッター
        output_lines.append("---")
        output_lines.append("*このレポートは学術特化文書処理システムにより自動生成されました。*")
        
        return "\n".join(output_lines)
    
    def create_structured_summary(self, academic_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """学術分析結果から構造化サマリーを作成"""
        
        structured_summary = {
            'basic_info': {
                'title': academic_analysis.get('title', '未特定'),
                'document_type': academic_analysis.get('document_type', 'generic'),
                'language': academic_analysis.get('language', '日本語'),
                'analysis_depth': academic_analysis.get('analysis_depth', 'standard')
            },
            'summary': academic_analysis.get('summary', ''),
            'structure_analysis': self._extract_structure_info(academic_analysis),
            'technical_details': self._extract_technical_info(academic_analysis),
            'key_findings': self._extract_findings_info(academic_analysis),
            'applications': self._extract_applications_info(academic_analysis),
            'limitations': self._extract_limitations_info(academic_analysis),
            'metadata': {
                'file_info': academic_analysis.get('file_info', {}),
                'processing_info': {
                    'processed_at': datetime.now().isoformat(),
                    'processor': 'AcademicDocumentProcessor',
                    'version': '1.0'
                }
            }
        }
        
        return structured_summary
    
    def _extract_structure_info(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """構造情報を抽出"""
        structure = {}
        
        if 'sections' in analysis:
            structure['sections'] = analysis['sections']
        
        if 'content_organization' in analysis:
            structure['content_organization'] = analysis['content_organization']
        elif 'structure' in analysis:
            structure['content_organization'] = analysis['structure']
        
        if 'document_flow' in analysis:
            structure['document_flow'] = analysis['document_flow']
        
        return structure
    
    def _extract_technical_info(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """技術情報を抽出"""
        technical = {}
        
        if 'methodologies' in analysis:
            technical['methodologies'] = analysis['methodologies']
        elif 'methods' in analysis:
            technical['methodologies'] = analysis['methods']
        
        if 'technologies' in analysis:
            technical['technologies'] = analysis['technologies']
        elif 'technical_specs' in analysis:
            technical['technologies'] = analysis['technical_specs']
        
        if 'data_analysis' in analysis:
            technical['data_analysis'] = analysis['data_analysis']
        
        return technical
    
    def _extract_findings_info(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """発見情報を抽出"""
        findings = {}
        
        if 'key_findings' in analysis:
            findings['main_results'] = analysis['key_findings']
        elif 'results' in analysis:
            findings['main_results'] = analysis['results']
        
        if 'innovations' in analysis:
            findings['innovations'] = analysis['innovations']
        elif 'novel_aspects' in analysis:
            findings['innovations'] = analysis['novel_aspects']
        
        if 'significance' in analysis:
            findings['significance'] = analysis['significance']
        elif 'importance' in analysis:
            findings['significance'] = analysis['importance']
        
        return findings
    
    def _extract_applications_info(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """応用情報を抽出"""
        applications = {}
        
        if 'applications' in analysis:
            applications['practical_uses'] = analysis['applications']
        elif 'use_cases' in analysis:
            applications['practical_uses'] = analysis['use_cases']
        
        if 'industries' in analysis:
            applications['industries'] = analysis['industries']
        elif 'target_sectors' in analysis:
            applications['industries'] = analysis['target_sectors']
        
        if 'future_potential' in analysis:
            applications['future_potential'] = analysis['future_potential']
        
        return applications
    
    def _extract_limitations_info(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """制約情報を抽出"""
        limitations = {}
        
        if 'limitations' in analysis:
            limitations['technical_limitations'] = analysis['limitations']
        elif 'constraints' in analysis:
            limitations['technical_limitations'] = analysis['constraints']
        
        if 'scope_limitations' in analysis:
            limitations['scope_limitations'] = analysis['scope_limitations']
        elif 'scope' in analysis:
            limitations['scope_limitations'] = analysis['scope']
        
        if 'future_work' in analysis:
            limitations['future_work'] = analysis['future_work']
        elif 'improvements' in analysis:
            limitations['future_work'] = analysis['improvements']
        
        return limitations
    
    def save_formatted_output(self, formatted_content: str, output_path: Path) -> bool:
        """フォーマット済み内容をファイルに保存"""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(formatted_content)
            
            return True
        except Exception as e:
            print(f"出力保存エラー: {e}")
            return False
