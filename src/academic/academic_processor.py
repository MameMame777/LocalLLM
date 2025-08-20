#!/usr/bin/env python3
"""
Academic Paper Processing Engine
Specialized processing for academic papers and technical documents
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from loguru import logger
import json

# Add project paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from document_processor import DocumentProcessor
from batch_processing.batch_processor import ProcessingResult
from academic.technical_translator import TechnicalDocumentTranslator, TechnicalTranslationResult
from academic.academic_output_formatter import AcademicOutputFormatter

@dataclass
class AcademicStructure:
    """学術論文の構造化データ"""
    title: Optional[str] = None
    authors: List[str] = None
    abstract: Optional[str] = None
    keywords: List[str] = None
    introduction: Optional[str] = None
    methodology: Optional[str] = None
    results: Optional[str] = None
    discussion: Optional[str] = None
    conclusion: Optional[str] = None
    references: List[str] = None
    figures: List[str] = None
    tables: List[str] = None
    equations: List[str] = None

@dataclass
class TechnicalSummary:
    """技術文書要約結果"""
    document_type: str  # "research_paper", "technical_report", "patent", "manual"
    technical_level: str  # "basic", "intermediate", "advanced", "expert"
    main_contribution: str
    key_findings: List[str]
    technical_details: List[str]
    practical_applications: List[str]
    limitations: List[str]
    future_work: Optional[str]
    methodology_summary: Optional[str]
    mathematical_concepts: List[str]

class AcademicDocumentProcessor:
    """学術・技術文書専用プロセッサー"""
    
    def __init__(self, llm_processor=None):
        self.base_processor = DocumentProcessor()
        self.formatter = AcademicOutputFormatter()
        self.technical_translator = TechnicalDocumentTranslator(llm_processor)
        self.llm_processor = llm_processor
        
        # 学術論文セクション認識パターン
        self.section_patterns = {
            'title': [
                r'^[\s]*(?:Title|タイトル)[\s]*:?[\s]*(.+?)(?:\n|$)',
                r'^[\s]*(.+?)(?:\n.*?Abstract|\n.*?要約)',
                r'^\s*([A-Z][^.\n]{10,100})\s*$'
            ],
            'authors': [
                r'(?:Authors?|著者)[\s]*:?[\s]*(.+?)(?:\n|Abstract)',
                r'(?:By|執筆者)[\s]*:?[\s]*(.+?)(?:\n)',
                r'([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+\s+[A-Z][a-z]+)*)'
            ],
            'abstract': [
                r'(?:Abstract|要約|概要)[\s]*:?[\s]*\n?(.*?)(?:\n\s*(?:Keywords?|キーワード|Introduction|1\.|I\.)|$)',
                r'(?:ABSTRACT|抄録)[\s]*\n?(.*?)(?:\n\s*(?:Keywords?|キーワード|Introduction)|$)'
            ],
            'keywords': [
                r'(?:Keywords?|キーワード|Key\s*words?)[\s]*:?[\s]*(.+?)(?:\n\s*\n|\n\s*(?:Introduction|1\.))',
                r'(?:Index\s*terms?|索引語)[\s]*:?[\s]*(.+?)(?:\n)'
            ],
            'introduction': [
                r'(?:1\.|I\.|Introduction|はじめに|序論)[\s]*(?:Introduction)?[\s]*\n(.*?)(?:\n\s*(?:2\.|II\.|Methodology|Method|手法))',
                r'(?:Introduction|序論|はじめに)[\s]*\n(.*?)(?:\n\s*(?:Methodology|Method|Related Work))'
            ],
            'methodology': [
                r'(?:2\.|II\.|Methodology|Method|手法|方法論)[\s]*(?:Methodology|Method)?[\s]*\n(.*?)(?:\n\s*(?:3\.|III\.|Results?|実験|結果))',
                r'(?:Methodology|Method|手法|方法論|実験方法)[\s]*\n(.*?)(?:\n\s*(?:Results?|実験結果|結果))'
            ],
            'results': [
                r'(?:3\.|III\.|Results?|実験結果|結果)[\s]*(?:Results?)?[\s]*\n(.*?)(?:\n\s*(?:4\.|IV\.|Discussion|考察|議論))',
                r'(?:Results?|実験結果|結果|成果)[\s]*\n(.*?)(?:\n\s*(?:Discussion|考察))'
            ],
            'discussion': [
                r'(?:4\.|IV\.|Discussion|考察|議論)[\s]*(?:Discussion)?[\s]*\n(.*?)(?:\n\s*(?:5\.|V\.|Conclusion|結論))',
                r'(?:Discussion|考察|議論|検討)[\s]*\n(.*?)(?:\n\s*(?:Conclusion|結論))'
            ],
            'conclusion': [
                r'(?:5\.|V\.|Conclusion|結論|まとめ)[\s]*(?:Conclusion|まとめ)?[\s]*\n(.*?)(?:\n\s*(?:References?|参考文献|Acknowledgment))',
                r'(?:Conclusion|結論|まとめ|おわりに)[\s]*\n(.*?)(?:\n\s*(?:References?|参考文献))'
            ],
            'references': [
                r'(?:References?|参考文献|Bibliography|文献)[\s]*\n(.*?)(?:\n\s*(?:Appendix|付録)|$)',
                r'(?:REFERENCES|参考文献)[\s]*\n(.*?)$'
            ]
        }
        
        # 技術用語・概念認識パターン
        self.technical_patterns = {
            'mathematical_concepts': [
                r'(?:theorem|定理|lemma|補題|corollary|系|proof|証明)',
                r'(?:algorithm|アルゴリズム|optimization|最適化|convergence|収束)',
                r'(?:matrix|行列|vector|ベクトル|eigenvalue|固有値|gradient|勾配)',
                r'(?:neural network|ニューラルネットワーク|deep learning|深層学習)',
                r'(?:machine learning|機械学習|artificial intelligence|人工知能)'
            ],
            'research_methods': [
                r'(?:experiment|実験|simulation|シミュレーション|analysis|解析)',
                r'(?:survey|調査|interview|インタビュー|questionnaire|アンケート)',
                r'(?:statistical|統計的|quantitative|定量的|qualitative|定性的)',
                r'(?:cross-validation|交差検証|hypothesis|仮説|significance|有意性)'
            ],
            'technical_metrics': [
                r'(?:accuracy|精度|precision|適合率|recall|再現率|F1-score)',
                r'(?:RMSE|MAE|MSE|R-squared|AUC|ROC)',
                r'(?:throughput|スループット|latency|レイテンシ|bandwidth|帯域幅)',
                r'(?:efficiency|効率|performance|性能|scalability|拡張性)'
            ]
        }

    def extract_academic_structure(self, text: str) -> AcademicStructure:
        """学術論文の構造を抽出"""
        structure = AcademicStructure()
        
        # セクション別抽出
        for section, patterns in self.section_patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
                if match:
                    content = match.group(1).strip()
                    if len(content) > 10:  # 有効なコンテンツのみ
                        if section == 'authors':
                            # 著者名を分離
                            authors = re.split(r'[,;]\s*|\s+and\s+', content)
                            structure.authors = [author.strip() for author in authors if author.strip()]
                        elif section == 'keywords':
                            # キーワードを分離
                            keywords = re.split(r'[,;]\s*', content)
                            structure.keywords = [kw.strip() for kw in keywords if kw.strip()]
                        elif section == 'references':
                            # 参考文献を分離
                            refs = re.split(r'\n\s*\[\d+\]|\n\s*\d+\.', content)
                            structure.references = [ref.strip() for ref in refs if ref.strip()]
                        else:
                            setattr(structure, section, content[:2000])  # 長すぎる場合は切り詰め
                        break
        
        # 図表・数式の抽出
        structure.figures = self._extract_figures(text)
        structure.tables = self._extract_tables(text)
        structure.equations = self._extract_equations(text)
        
        return structure

    def _extract_figures(self, text: str) -> List[str]:
        """図表キャプションを抽出"""
        figure_patterns = [
            r'(?:Figure|Fig\.|図|Figure)\s*(\d+)[\s:]*(.{10,200}?)(?:\n|$)',
            r'(?:Figure|図)\s*(\d+)[\s]*:[\s]*(.+?)(?:\n)',
        ]
        
        figures = []
        for pattern in figure_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    figures.append(f"Figure {match[0]}: {match[1].strip()}")
        
        return figures[:10]  # 最大10個

    def _extract_tables(self, text: str) -> List[str]:
        """表キャプションを抽出"""
        table_patterns = [
            r'(?:Table|表)\s*(\d+)[\s:]*(.{10,200}?)(?:\n|$)',
            r'(?:Table|表)\s*(\d+)[\s]*:[\s]*(.+?)(?:\n)',
        ]
        
        tables = []
        for pattern in table_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match) >= 2:
                    tables.append(f"Table {match[0]}: {match[1].strip()}")
        
        return tables[:10]  # 最大10個

    def _extract_equations(self, text: str) -> List[str]:
        """数式を抽出"""
        equation_patterns = [
            r'\$\$(.+?)\$\$',  # LaTeX display math
            r'\$(.+?)\$',      # LaTeX inline math
            r'\\begin\{equation\}(.+?)\\end\{equation\}',  # LaTeX equation
            r'\\begin\{align\}(.+?)\\end\{align\}',        # LaTeX align
        ]
        
        equations = []
        for pattern in equation_patterns:
            matches = re.findall(pattern, text, re.DOTALL)
            for match in matches:
                clean_eq = match.strip()
                if len(clean_eq) > 3:
                    equations.append(clean_eq)
        
        return equations[:20]  # 最大20個

    def analyze_technical_content(self, text: str, structure: AcademicStructure) -> TechnicalSummary:
        """技術内容の分析"""
        
        # 文書タイプの判定
        doc_type = self._classify_document_type(text, structure)
        
        # 技術レベルの判定
        tech_level = self._assess_technical_level(text)
        
        # 主要貢献の抽出
        main_contribution = self._extract_main_contribution(structure)
        
        # 主要発見の抽出
        key_findings = self._extract_key_findings(structure)
        
        # 技術詳細の抽出
        technical_details = self._extract_technical_details(text)
        
        # 実用的応用の抽出
        practical_applications = self._extract_applications(text)
        
        # 制限事項の抽出
        limitations = self._extract_limitations(text)
        
        # 今後の課題
        future_work = self._extract_future_work(structure)
        
        # 手法要約
        methodology_summary = structure.methodology[:500] if structure.methodology else None
        
        # 数学的概念
        mathematical_concepts = self._extract_mathematical_concepts(text)
        
        return TechnicalSummary(
            document_type=doc_type,
            technical_level=tech_level,
            main_contribution=main_contribution,
            key_findings=key_findings,
            technical_details=technical_details,
            practical_applications=practical_applications,
            limitations=limitations,
            future_work=future_work,
            methodology_summary=methodology_summary,
            mathematical_concepts=mathematical_concepts
        )

    def _classify_document_type(self, text: str, structure: AcademicStructure) -> str:
        """文書タイプの分類"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['patent', '特許', 'invention', 'claim']):
            return "patent"
        elif any(word in text_lower for word in ['manual', 'user guide', 'tutorial', 'マニュアル', '取扱説明書']):
            return "manual"
        elif any(word in text_lower for word in ['technical report', '技術報告', 'white paper']):
            return "technical_report"
        elif structure.abstract or structure.references:
            return "research_paper"
        else:
            return "technical_document"

    def _assess_technical_level(self, text: str) -> str:
        """技術レベルの評価"""
        # 専門用語の密度を計算
        technical_terms = 0
        basic_terms = 0
        
        advanced_patterns = [
            r'(?:algorithm|optimization|convergence|eigenvalue|gradient)',
            r'(?:neural network|deep learning|machine learning)',
            r'(?:statistical significance|hypothesis testing|p-value)',
            r'(?:complexity analysis|computational complexity)',
            r'(?:stochastic|probabilistic|Bayesian|regression)'
        ]
        
        basic_patterns = [
            r'(?:data|information|system|method|result)',
            r'(?:analysis|comparison|evaluation|measurement)',
            r'(?:performance|efficiency|accuracy|speed)'
        ]
        
        for pattern in advanced_patterns:
            technical_terms += len(re.findall(pattern, text, re.IGNORECASE))
        
        for pattern in basic_patterns:
            basic_terms += len(re.findall(pattern, text, re.IGNORECASE))
        
        total_words = len(text.split())
        advanced_ratio = technical_terms / total_words if total_words > 0 else 0
        
        if advanced_ratio > 0.02:
            return "expert"
        elif advanced_ratio > 0.01:
            return "advanced"
        elif advanced_ratio > 0.005:
            return "intermediate"
        else:
            return "basic"

    def _extract_main_contribution(self, structure: AcademicStructure) -> str:
        """主要貢献の抽出"""
        candidates = []
        
        # アブストラクトから
        if structure.abstract:
            # 貢献を示すキーワード周辺を抽出
            contribution_patterns = [
                r'(?:we propose|we present|we introduce|we develop|this paper presents|our contribution|我々は提案|本論文では|提案する)',
                r'(?:novel|new|innovative|original|improved|enhanced|新しい|新規|改良|向上)'
            ]
            
            for pattern in contribution_patterns:
                matches = re.finditer(pattern, structure.abstract, re.IGNORECASE)
                for match in matches:
                    # マッチ周辺の文を抽出
                    start = max(0, match.start() - 50)
                    end = min(len(structure.abstract), match.end() + 150)
                    candidates.append(structure.abstract[start:end].strip())
        
        # 結論から
        if structure.conclusion:
            conclusion_sentences = re.split(r'[.!?。！？]', structure.conclusion)
            candidates.extend([s.strip() for s in conclusion_sentences[:3] if len(s.strip()) > 20])
        
        if candidates:
            # 最も長い候補を選択
            return max(candidates, key=len)[:300]
        
        return "主要貢献の特定ができませんでした。"

    def _extract_key_findings(self, structure: AcademicStructure) -> List[str]:
        """主要発見の抽出"""
        findings = []
        
        # 結果セクションから
        if structure.results:
            result_sentences = re.split(r'[.!?。！？]', structure.results)
            for sentence in result_sentences:
                if len(sentence.strip()) > 30 and any(word in sentence.lower() for word in 
                    ['achieved', 'improved', 'increased', 'decreased', 'demonstrated', 'showed', 'found',
                     '達成', '改善', '向上', '減少', '示した', '発見', '明らかに']):
                    findings.append(sentence.strip())
        
        # アブストラクトから数値的結果
        if structure.abstract:
            number_patterns = [
                r'(\d+(?:\.\d+)?%\s*(?:improvement|increase|decrease|accuracy|precision|改善|向上|精度))',
                r'(\d+(?:\.\d+)?\s*(?:times faster|倍高速|倍の性能))',
                r'(\d+(?:\.\d+)?\s*(?:dB|Hz|MHz|GHz|ms|μs|ns))'
            ]
            
            for pattern in number_patterns:
                matches = re.findall(pattern, structure.abstract, re.IGNORECASE)
                findings.extend(matches)
        
        return findings[:10]

    def _extract_technical_details(self, text: str) -> List[str]:
        """技術詳細の抽出"""
        details = []
        
        # アルゴリズム・手法の詳細
        algorithm_patterns = [
            r'(?:Algorithm|アルゴリズム)\s*\d*[\s:]*(.{50,300}?)(?:\n|Algorithm|\d\.)',
            r'(?:Method|手法|方法)[\s:]*(.{50,300}?)(?:\n\n|\d\.)',
            r'(?:Implementation|実装|実装方法)[\s:]*(.{50,300}?)(?:\n\n|\d\.)'
        ]
        
        for pattern in algorithm_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            details.extend([match.strip() for match in matches if len(match.strip()) > 20])
        
        # パラメータ設定
        parameter_patterns = [
            r'(?:parameters?|パラメータ|設定)[\s:]*(.{30,200}?)(?:\n\n|\d\.)',
            r'(?:hyperparameters?|ハイパーパラメータ)[\s:]*(.{30,200}?)(?:\n\n|\d\.)'
        ]
        
        for pattern in parameter_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            details.extend([match.strip() for match in matches if len(match.strip()) > 15])
        
        return details[:8]

    def _extract_applications(self, text: str) -> List[str]:
        """実用的応用の抽出"""
        applications = []
        
        application_patterns = [
            r'(?:applications?|応用|適用)[\s:]*(.{50,300}?)(?:\n\n|\d\.)',
            r'(?:use case|使用例|用途)[\s:]*(.{50,300}?)(?:\n\n|\d\.)',
            r'(?:practical|実用的|実際の)[\s\w]*(?:application|応用|適用)[\s:]*(.{50,300}?)(?:\n\n|\d\.)'
        ]
        
        for pattern in application_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            applications.extend([match.strip() for match in matches if len(match.strip()) > 20])
        
        return applications[:5]

    def _extract_limitations(self, text: str) -> List[str]:
        """制限事項の抽出"""
        limitations = []
        
        limitation_patterns = [
            r'(?:limitations?|制限|限界)[\s:]*(.{50,300}?)(?:\n\n|\d\.)',
            r'(?:however|但し|しかし)[\s,]*(.{50,300}?)(?:\n\n|\d\.)',
            r'(?:cannot|can not|できない|不可能)(.{30,200}?)(?:\n\n|\d\.)'
        ]
        
        for pattern in limitation_patterns:
            matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
            limitations.extend([match.strip() for match in matches if len(match.strip()) > 20])
        
        return limitations[:5]

    def _extract_future_work(self, structure: AcademicStructure) -> Optional[str]:
        """今後の課題の抽出"""
        if structure.conclusion:
            future_patterns = [
                r'(?:future work|future research|今後の|将来の)[\s\w]*(.{50,300}?)(?:\n\n|$)',
                r'(?:next step|次のステップ|今後)[\s:]*(.{50,300}?)(?:\n\n|$)'
            ]
            
            for pattern in future_patterns:
                match = re.search(pattern, structure.conclusion, re.DOTALL | re.IGNORECASE)
                if match:
                    return match.group(1).strip()[:200]
        
        return None

    def _extract_mathematical_concepts(self, text: str) -> List[str]:
        """数学的概念の抽出"""
        concepts = []
        
        for concept_type, patterns in self.technical_patterns.items():
            if concept_type == 'mathematical_concepts':
                for pattern in patterns:
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    concepts.extend(matches)
        
        return list(set(concepts))[:10]

    def generate_academic_summary(self, file_path: Path, language: str = "ja", max_length: int = 200) -> Dict[str, Any]:
        """学術論文専用要約生成"""
        try:
            # テキスト抽出
            extracted_text = self.base_processor.process_file(file_path)
            if not extracted_text:
                raise ValueError("テキスト抽出に失敗しました")
            
            # 学術構造解析
            structure = self.extract_academic_structure(extracted_text)
            
            # 技術内容分析
            technical_summary = self.analyze_technical_content(extracted_text, structure)
            
            # 日本語要約生成
            summary_parts = []
            
            # 1. 基本情報
            if structure.title:
                summary_parts.append(f"【タイトル】\n{structure.title}")
            
            if structure.authors:
                authors_str = "、".join(structure.authors[:5])
                summary_parts.append(f"【著者】\n{authors_str}")
            
            # 2. 文書分類
            doc_type_ja = {
                "research_paper": "研究論文",
                "technical_report": "技術報告書", 
                "patent": "特許文書",
                "manual": "技術マニュアル",
                "technical_document": "技術文書"
            }
            
            level_ja = {
                "basic": "基礎レベル",
                "intermediate": "中級レベル", 
                "advanced": "上級レベル",
                "expert": "専門家レベル"
            }
            
            summary_parts.append(f"【文書種別】\n{doc_type_ja.get(technical_summary.document_type, technical_summary.document_type)} ({level_ja.get(technical_summary.technical_level, technical_summary.technical_level)})")
            
            # 3. 主要貢献
            summary_parts.append(f"【主要貢献】\n{technical_summary.main_contribution}")
            
            # 4. 手法概要
            if technical_summary.methodology_summary:
                summary_parts.append(f"【手法概要】\n{technical_summary.methodology_summary}")
            
            # 5. 主要発見
            if technical_summary.key_findings:
                findings_str = "\n".join([f"• {finding}" for finding in technical_summary.key_findings[:5]])
                summary_parts.append(f"【主要発見】\n{findings_str}")
            
            # 6. 実用的応用
            if technical_summary.practical_applications:
                apps_str = "\n".join([f"• {app}" for app in technical_summary.practical_applications[:3]])
                summary_parts.append(f"【実用的応用】\n{apps_str}")
            
            # 7. 技術詳細
            if technical_summary.technical_details:
                details_str = "\n".join([f"• {detail}" for detail in technical_summary.technical_details[:3]])
                summary_parts.append(f"【技術詳細】\n{details_str}")
            
            # 8. 制限事項
            if technical_summary.limitations:
                limitations_str = "\n".join([f"• {limitation}" for limitation in technical_summary.limitations[:3]])
                summary_parts.append(f"【制限事項】\n{limitations_str}")
            
            # 9. 今後の課題
            if technical_summary.future_work:
                summary_parts.append(f"【今後の課題】\n{technical_summary.future_work}")
            
            # 10. 数学的概念
            if technical_summary.mathematical_concepts:
                concepts_str = "、".join(technical_summary.mathematical_concepts[:8])
                summary_parts.append(f"【関連概念】\n{concepts_str}")
            
            # 要約統合
            full_summary = "\n\n".join(summary_parts)
            
            # 長さ調整
            if len(full_summary) > max_length * 20:  # 概算文字数制限
                # 重要度順に削減
                essential_parts = summary_parts[:6]  # 基本情報〜実用的応用まで
                full_summary = "\n\n".join(essential_parts)
            
            return {
                "summary": full_summary,
                "structure": structure,
                "technical_analysis": technical_summary,
                "processing_metadata": {
                    "document_type": technical_summary.document_type,
                    "technical_level": technical_summary.technical_level,
                    "sections_found": sum(1 for attr in ['title', 'authors', 'abstract', 'introduction', 'methodology', 'results', 'conclusion'] 
                                        if getattr(structure, attr) is not None),
                    "figures_count": len(structure.figures) if structure.figures else 0,
                    "tables_count": len(structure.tables) if structure.tables else 0,
                    "equations_count": len(structure.equations) if structure.equations else 0,
                    "references_count": len(structure.references) if structure.references else 0
                }
            }
            
        except Exception as e:
            logger.error(f"学術文書処理エラー: {e}")
            return {
                "summary": f"処理中にエラーが発生しました: {str(e)}",
                "structure": None,
                "technical_analysis": None,
                "processing_metadata": {"error": str(e)}
            }

# 使用例
if __name__ == "__main__":
    processor = AcademicDocumentProcessor()
    
    # テストファイル
    test_files = list(Path("data").glob("*.pdf"))[:1] if Path("data").exists() else []
    def process_technical_document_japanese(self, extracted_content: str, file_path: str = None) -> Dict[str, Any]:
        """
        技術文書の英日翻訳特化処理
        
        Args:
            extracted_content: 抽出されたテキストコンテンツ
            file_path: ファイルパス（オプション）
            
        Returns:
            翻訳処理結果辞書
        """
        try:
            logger.info("🔄 技術文書英日翻訳処理開始")
            
            # 技術翻訳エンジンによる処理
            translation_result: TechnicalTranslationResult = self.technical_translator.translate_technical_document(
                extracted_content
            )
            
            # 学術構造の抽出（バックアップ情報として）
            academic_structure = self.extract_academic_structure(extracted_content)
            
            # 技術分析
            technical_summary = self.analyze_technical_content(extracted_content, academic_structure)
            
            # 結果の統合
            result = {
                "japanese_translation": translation_result.japanese_translation,
                "document_type": translation_result.document_type,
                "technical_level": technical_summary.technical_level,
                "translation_quality": translation_result.translation_quality,
                "confidence_score": translation_result.confidence_score,
                "processing_time": translation_result.processing_time,
                "technical_terms_found": translation_result.technical_terms_found,
                "key_findings": technical_summary.key_findings,
                "practical_applications": technical_summary.practical_applications,
                "technical_details": technical_summary.technical_details,
                "main_contribution": technical_summary.main_contribution,
                "methodology_summary": technical_summary.methodology_summary,
                "mathematical_concepts": technical_summary.mathematical_concepts,
                "processing_metadata": {
                    "processor_type": "technical_translation",
                    "document_classification": translation_result.document_type,
                    "technical_level": technical_summary.technical_level,
                    "translation_confidence": translation_result.confidence_score,
                    "processing_time_seconds": translation_result.processing_time,
                    "terms_detected": len(translation_result.technical_terms_found),
                    "file_path": file_path or "unknown"
                }
            }
            
            logger.info(f"✅ 技術翻訳完了: {translation_result.document_type} ({translation_result.translation_quality})")
            return result
            
        except Exception as e:
            logger.error(f"❌ 技術翻訳処理エラー: {e}")
            return {
                "japanese_translation": f"技術翻訳処理中にエラーが発生しました: {str(e)}",
                "document_type": "error",
                "technical_level": "unknown",
                "translation_quality": "error",
                "confidence_score": 0.0,
                "processing_time": 0.0,
                "technical_terms_found": [],
                "key_findings": [],
                "practical_applications": [],
                "technical_details": [],
                "main_contribution": "処理エラー",
                "methodology_summary": None,
                "mathematical_concepts": [],
                "processing_metadata": {
                    "processor_type": "technical_translation",
                    "error": str(e),
                    "file_path": file_path or "unknown"
                }
            }
    
    def create_enhanced_japanese_summary(self, extracted_content: str, file_path: str = None) -> str:
        """
        拡張日本語要約の生成（技術翻訳特化）
        
        Args:
            extracted_content: 抽出されたコンテンツ
            file_path: ファイルパス
            
        Returns:
            拡張された日本語要約文字列
        """
        try:
            # 技術翻訳処理の実行
            translation_result = self.process_technical_document_japanese(extracted_content, file_path)
            
            # フォーマット済み要約の生成
            enhanced_summary = self.formatter.format_technical_japanese_summary(translation_result)
            
            return enhanced_summary
            
        except Exception as e:
            logger.error(f"拡張日本語要約生成エラー: {e}")
            return f"拡張要約生成中にエラーが発生しました: {str(e)}"

if __name__ == "__main__":
    # テスト実行
    import sys
    from pathlib import Path
    
    # プロジェクトルートをパスに追加
    project_root = Path(__file__).parent.parent.parent
    sys.path.insert(0, str(project_root))
    
    processor = AcademicDocumentProcessor()
    
    # テスト用のPDFファイルを検索
    test_files = list(Path(project_root / "data").glob("*.pdf"))
    
    if test_files:
        result = processor.generate_academic_summary(test_files[0])
        print("=" * 80)
        print("🎓 学術論文要約結果")
        print("=" * 80)
        print(result["summary"])
        
        if result["processing_metadata"]:
            print("\n" + "=" * 40)
            print("📊 処理メタデータ")
            print("=" * 40)
            for key, value in result["processing_metadata"].items():
                print(f"{key}: {value}")
        
        # 技術翻訳テスト
        print("\n" + "=" * 80)
        print("🔬 技術翻訳特化処理テスト")
        print("=" * 80)
        
        with open(test_files[0], 'rb') as f:
            # ここでPDF読み込み処理が必要
            content = "Sample technical content for translation testing."
            
        tech_result = processor.process_technical_document_japanese(content, str(test_files[0]))
        print(tech_result["japanese_translation"])
        
    else:
        print("テスト用PDFファイルが見つかりません。")
