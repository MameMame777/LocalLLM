"""
技術文献専用英日翻訳処理エンジン
Technical Document English-Japanese Translation Engine

このモジュールは技術文献（データシート、技術仕様書、学術論文など）の
英日翻訳に特化した高品質翻訳処理を提供します。
"""

import re
import logging
from typing import Dict, List, Tuple, Any, Union
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class TechnicalTranslationResult:
    """技術翻訳結果データクラス"""
    japanese_translation: str
    document_type: str
    technical_terms_found: List[str]
    translation_quality: str
    processing_time: float
    confidence_score: float

class TechnicalDocumentTranslator:
    """技術文献専用翻訳エンジン"""
    
    def __init__(self, llm_processor: Any = None):
        """
        技術翻訳エンジンの初期化
        
        Args:
            llm_processor: LLMプロセッサインスタンス
        """
        self.llm_processor = llm_processor
        self.technical_terms_dict = self._load_technical_dictionary()
        self.datasheet_patterns = self._load_datasheet_patterns()
        
    def _load_technical_dictionary(self) -> Dict[str, str]:
        """技術用語辞書の読み込み"""
        return {
            # 電子工学基本用語
            'ADC': 'ADC（アナログ-デジタル変換器）',
            'DAC': 'DAC（デジタル-アナログ変換器）',
            'resolution': '分解能',
            'Resolution': '分解能',
            'accuracy': '精度',
            'Accuracy': '精度',
            'precision': '精度',
            'Precision': '精度',
            'linearity': '直線性',
            'Linearity': '直線性',
            'nonlinearity': '非直線性',
            'Nonlinearity': '非直線性',
            'differential': '差動',
            'Differential': '差動',
            'single-ended': 'シングルエンド',
            'Single-ended': 'シングルエンド',
            'unipolar': '単極性',
            'Unipolar': '単極性',
            'bipolar': '双極性',
            'Bipolar': '双極性',
            'multiplexer': 'マルチプレクサ',
            'Multiplexer': 'マルチプレクサ',
            'throughput': 'スループット',
            'Throughput': 'スループット',
            'bandwidth': '帯域幅',
            'Bandwidth': '帯域幅',
            'frequency': '周波数',
            'Frequency': '周波数',
            'response': '応答',
            'Response': '応答',
            'settling': 'セトリング',
            'Settling': 'セトリング',
            'time': '時間',
            'Time': '時間',
            'voltage': '電圧',
            'Voltage': '電圧',
            'current': '電流',
            'Current': '電流',
            'power': '電力',
            'Power': '電力',
            'supply': '電源',
            'Supply': '電源',
            'consumption': '消費',
            'Consumption': '消費',
            'noise': 'ノイズ',
            'Noise': 'ノイズ',
            'distortion': '歪み',
            'Distortion': '歪み',
            'gain': 'ゲイン',
            'Gain': 'ゲイン',
            'offset': 'オフセット',
            'Offset': 'オフセット',
            'drift': 'ドリフト',
            'Drift': 'ドリフト',
            'temperature': '温度',
            'Temperature': '温度',
            'coefficient': '係数',
            'Coefficient': '係数',
            'range': 'レンジ',
            'Range': 'レンジ',
            'input': '入力',
            'Input': '入力',
            'output': '出力',
            'Output': '出力',
            'channel': 'チャンネル',
            'Channel': 'チャンネル',
            'channels': 'チャンネル',
            'Channels': 'チャンネル',
            'signal': '信号',
            'Signal': '信号',
            'analog': 'アナログ',
            'Analog': 'アナログ',
            'digital': 'デジタル',
            'Digital': 'デジタル',
            'package': 'パッケージ',
            'Package': 'パッケージ',
            'pin': 'ピン',
            'Pin': 'ピン',
            'pins': 'ピン',
            'Pins': 'ピン',
            'operating': '動作',
            'Operating': '動作',
            'condition': '条件',
            'Condition': '条件',
            'conditions': '条件',
            'Conditions': '条件',
            'specification': '仕様',
            'Specification': '仕様',
            'specifications': '仕様',
            'Specifications': '仕様',
            'feature': '特長',
            'Feature': '特長',
            'features': '特長',
            'Features': '特長',
            'application': '用途',
            'Application': '用途',
            'applications': '用途',
            'Applications': '用途',
            'performance': '性能',
            'Performance': '性能',
            'function': '機能',
            'Function': '機能',
            'functionality': '機能',
            'Functionality': '機能',
            'typical': '標準',
            'Typical': '標準',
            'minimum': '最小',
            'Minimum': '最小',
            'maximum': '最大',
            'Maximum': '最大',
            'nominal': '公称',
            'Nominal': '公称',
            'data sheet': 'データシート',
            'Data Sheet': 'データシート',
            'datasheet': 'データシート',
            'Datasheet': 'データシート',
            
            # 特殊な技術用語
            'RMS': 'RMS',
            'true RMS': '真のRMS',
            'True RMS': '真のRMS',
            'crest factor': 'クレストファクタ',
            'Crest factor': 'クレストファクタ',
            'SINAD': 'SINAD（信号対雑音歪み比）',
            'SNR': 'SNR（信号対雑音比）',
            'THD': 'THD（全高調波歪み）',
            'LSB': 'LSB（最下位ビット）',
            'MSB': 'MSB（最上位ビット）',
            'INL': 'INL（積分非直線性）',
            'DNL': 'DNL（微分非直線性）',
            'ENOB': 'ENOB（有効ビット数）',
            'SFDR': 'SFDR（スプリアスフリーダイナミックレンジ）',
            
            # 単位
            'V': 'V',
            'mV': 'mV',
            'μV': 'μV',
            'A': 'A',
            'mA': 'mA',
            'μA': 'μA',
            'nA': 'nA',
            'W': 'W',
            'mW': 'mW',
            'μW': 'μW',
            'Hz': 'Hz',
            'kHz': 'kHz',
            'MHz': 'MHz',
            'GHz': 'GHz',
            'dB': 'dB',
            'dBm': 'dBm',
            'dBV': 'dBV',
            '°C': '°C',
            'ppm': 'ppm',
            '%': '%',
            'bit': 'ビット',
            'bits': 'ビット',
            'Bit': 'ビット',
            'Bits': 'ビット',
            'SPS': 'SPS',
            'kSPS': 'kSPS',
            'MSPS': 'MSPS',
            'GSPS': 'GSPS',
            
            # メーカー・ブランド名
            'Analog Devices': 'アナログ・デバイセズ',
            'PulSAR': 'PulSAR',
            'Successive Approximation': '逐次比較',
            'successive approximation': '逐次比較',
            'Sigma-Delta': 'シグマデルタ',
            'sigma-delta': 'シグマデルタ',
            
            # パッケージタイプ
            'SOIC': 'SOIC',
            'DIP': 'DIP',
            'PDIP': 'PDIP',
            'QFN': 'QFN',
            'BGA': 'BGA',
            'TQFP': 'TQFP',
            'MSOP': 'MSOP',
            'LFCSP': 'LFCSP',
            
            # 接続・インターフェース
            'SPI': 'SPI',
            'I2C': 'I2C',
            'UART': 'UART',
            'USB': 'USB',
            'GPIO': 'GPIO',
            'PWM': 'PWM',
            
            # 法的・品質関連
            'Information furnished': '提供される情報',
            'information furnished': '提供される情報',
            'believed to be accurate': '正確であると考えられている',
            'reliable': '信頼性のある',
            'responsibility': '責任',
            'assumed': '想定される',
            'infringements': '侵害',
            'patents': '特許',
            'third parties': '第三者',
            'subject to change': '変更される可能性がある',
            'without notice': '予告なし',
            'All rights reserved': '全権留保',
            'Trademarks': '商標',
            'trademarks': '商標',
            'registered': '登録',
            'property': '財産',
            'respective': 'それぞれの',
            'owners': '所有者',
        }
    
    def _load_datasheet_patterns(self) -> Dict[str, str]:
        """データシート特有のパターン辞書"""
        return {
            # データシート構造
            'GENERAL DESCRIPTION': '概要',
            'General Description': '概要',
            'FEATURES': '特長',
            'Features': '特長',
            'APPLICATIONS': '用途',
            'Applications': '用途',
            'FUNCTIONAL BLOCK DIAGRAM': '機能ブロック図',
            'Functional Block Diagram': '機能ブロック図',
            'PIN CONFIGURATION': 'ピン配置',
            'Pin Configuration': 'ピン配置',
            'SPECIFICATIONS': '仕様',
            'Specifications': '仕様',
            'ELECTRICAL CHARACTERISTICS': '電気的特性',
            'Electrical Characteristics': '電気的特性',
            'OPERATING CONDITIONS': '動作条件',
            'Operating Conditions': '動作条件',
            'ABSOLUTE MAXIMUM RATINGS': '絶対最大定格',
            'Absolute Maximum Ratings': '絶対最大定格',
            'TIMING CHARACTERISTICS': 'タイミング特性',
            'Timing Characteristics': 'タイミング特性',
            'PACKAGE INFORMATION': 'パッケージ情報',
            'Package Information': 'パッケージ情報',
            'ORDERING INFORMATION': '注文情報',
            'Ordering Information': '注文情報',
            
            # 特殊なフレーズ
            'no missing codes': 'ミッシングコードなし',
            'with choice of inputs': '入力選択機能付き',
            'guaranteed': '保証',
            'over temperature': '温度範囲にわたって',
            'full scale': 'フルスケール',
            'end-to-end': 'エンドツーエンド',
            'zero scale': 'ゼロスケール',
            'mid-scale': 'ミッドスケール',
            'half scale': 'ハーフスケール',
            'linearity error': '直線性誤差',
            'gain error': 'ゲイン誤差',
            'offset error': 'オフセット誤差',
        }
    
    def classify_document_type(self, text: str) -> str:
        """文書タイプの判定"""
        text_lower = text.lower()
        
        # データシートの特徴
        if any(pattern in text_lower for pattern in [
            'data sheet', 'datasheet', 'specifications', 'pin configuration',
            'electrical characteristics', 'absolute maximum ratings'
        ]):
            return 'datasheet'
        
        # 学術論文の特徴
        elif any(pattern in text_lower for pattern in [
            'abstract', 'introduction', 'methodology', 'conclusion',
            'references', 'bibliography'
        ]):
            return 'academic_paper'
        
        # 技術レポート
        elif any(pattern in text_lower for pattern in [
            'technical report', 'white paper', 'technical specification',
            'implementation guide'
        ]):
            return 'technical_report'
        
        # マニュアル
        elif any(pattern in text_lower for pattern in [
            'user manual', 'user guide', 'installation guide',
            'operation manual', 'reference manual'
        ]):
            return 'manual'
        
        # 特許文書
        elif any(pattern in text_lower for pattern in [
            'patent', 'invention', 'claim', 'prior art'
        ]):
            return 'patent'
        
        else:
            return 'technical_document'
    
    def create_specialized_prompt(self, english_text: str, doc_type: str) -> str:
        """文書タイプに特化したプロンプト生成"""
        
        # 文書タイプ別の専門指示
        type_instructions = {
            'datasheet': """
技術仕様書・データシート翻訳の専門家として、以下の英語技術文書を正確で自然な日本語に翻訳してください。

翻訳要件：
1. 技術用語は業界標準の日本語訳を使用
2. 数値・単位・仕様値は正確に保持
3. 回路図・ピン配置等の技術情報を適切に表現
4. データシート特有の構造（特長、仕様、用途等）を適切に翻訳
5. エンジニアが理解しやすい専門的な日本語で記述
""",
            'academic_paper': """
学術論文翻訳の専門家として、以下の英語学術文書を正確で自然な日本語に翻訳してください。

翻訳要件：
1. 学術的な専門用語を適切な日本語で表現
2. 論文の論理構造と学術的な文体を保持
3. 研究手法・結果・考察を正確に翻訳
4. 引用・参考文献の形式を適切に処理
5. 学術界で使用される標準的な日本語表現を使用
""",
            'technical_report': """
技術レポート翻訳の専門家として、以下の英語技術文書を正確で自然な日本語に翻訳してください。

翻訳要件：
1. 技術的概念を正確に日本語で表現
2. 専門的でありながら理解しやすい文体
3. 図表・データの説明を適切に翻訳
4. 技術的推奨事項や結論を明確に伝達
5. 業界標準の技術用語を使用
""",
            'manual': """
技術マニュアル翻訳の専門家として、以下の英語マニュアルを正確で自然な日本語に翻訳してください。

翻訳要件：
1. 操作手順を明確で分かりやすい日本語で記述
2. 警告・注意事項を適切に強調
3. 技術用語は一般的な日本語訳を使用
4. ユーザーが実際に使用する際の利便性を重視
5. 手順の論理的な流れを保持
""",
            'patent': """
特許文書翻訳の専門家として、以下の英語特許文書を正確で自然な日本語に翻訳してください。

翻訳要件：
1. 特許特有の法的表現を適切に翻訳
2. 技術的発明内容を正確に記述
3. クレーム（請求項）の法的意味を保持
4. 先行技術との差異を明確に表現
5. 特許庁で使用される標準的な日本語表現を使用
""",
            'technical_document': """
技術文書翻訳の専門家として、以下の英語技術文書を正確で自然な日本語に翻訳してください。

翻訳要件：
1. 技術的内容を正確に日本語で表現
2. 専門用語は業界標準の訳語を使用
3. 文書の目的と読者層を考慮した適切な文体
4. 技術的な詳細情報を漏れなく翻訳
5. 読みやすく理解しやすい日本語で記述
"""
        }
        
        base_instruction = type_instructions.get(doc_type, type_instructions['technical_document'])
        
        # Llama 2用最適化プロンプト形式
        specialized_prompt = f"""[INST] {base_instruction.strip()}

英語原文：
{english_text.strip()}

上記英語文書を要件に従って正確に日本語翻訳してください。翻訳のみを出力し、説明や追加情報は含めないでください。 [/INST]

日本語翻訳："""
        
        return specialized_prompt
    
    def preprocess_text(self, text: str) -> str:
        """翻訳前のテキスト前処理"""
        # 改行の正規化
        text = re.sub(r'\r\n', '\n', text)
        text = re.sub(r'\r', '\n', text)
        
        # 過度な空白の削除
        text = re.sub(r' +', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        
        # 特殊文字の正規化
        text = text.replace('•', '・')
        text = text.replace('–', '-')
        text = text.replace('—', '-')
        text = text.replace('"', '"')
        text = text.replace('"', '"')
        text = text.replace(''', "'")
        text = text.replace(''', "'")
        
        return text.strip()
    
    def postprocess_translation(self, translation: str, doc_type: str) -> str:
        """翻訳後の後処理"""
        # 余分な文字列の除去
        translation = translation.replace("Japanese translation:", "").strip()
        translation = translation.replace("日本語翻訳:", "").strip()
        translation = translation.replace("翻訳:", "").strip()
        
        # 文書タイプ別の接頭辞追加
        if doc_type == 'datasheet' and not translation.startswith('【'):
            translation = f"【データシート翻訳】\n\n{translation}"
        elif doc_type == 'academic_paper' and not translation.startswith('【'):
            translation = f"【学術論文翻訳】\n\n{translation}"
        elif doc_type == 'technical_report' and not translation.startswith('【'):
            translation = f"【技術レポート翻訳】\n\n{translation}"
        
        # 技術用語の後処理（辞書による用語統一）
        for english_term, japanese_term in self.technical_terms_dict.items():
            translation = translation.replace(english_term, japanese_term)
        
        return translation.strip()
    
    def extract_technical_terms(self, text: str) -> List[str]:
        """技術用語の抽出"""
        found_terms = []
        
        for english_term in self.technical_terms_dict.keys():
            if english_term in text:
                found_terms.append(english_term)
        
        return found_terms
    
    def assess_translation_quality(self, original: str, translation: str) -> Tuple[str, float]:
        """翻訳品質の評価"""
        # 基本的な品質指標
        if not translation or len(translation.strip()) < 10:
            return "poor", 0.0
        
        # 長さ比較（極端に短すぎる翻訳をチェック）
        length_ratio = len(translation) / len(original) if len(original) > 0 else 0
        
        if length_ratio < 0.3:  # あまりにも短い
            return "poor", 0.2
        elif length_ratio < 0.5:
            return "fair", 0.5
        elif length_ratio > 2.0:  # あまりにも長い
            return "fair", 0.6
        else:
            return "good", 0.8
    
    def _create_dictionary_translation(self, text: str, technical_terms: List[str], doc_type: str) -> str:
        """辞書ベースの翻訳を生成"""
        lines = text.split('\n')
        translated_lines = []
        
        for line in lines:
            if not line.strip():
                translated_lines.append(line)
                continue
            
            # 技術用語の翻訳
            translated_line = line
            for term in technical_terms:
                if term in self.technical_terms_dict:
                    translated_line = translated_line.replace(term, self.technical_terms_dict[term])
            
            # 基本的な構造翻訳
            if 'FEATURES' in line:
                translated_line = line.replace('FEATURES', '特長')
            elif 'SPECIFICATIONS' in line:
                translated_line = line.replace('SPECIFICATIONS', '仕様')
            elif 'PERFORMANCE' in line:
                translated_line = line.replace('PERFORMANCE', '性能')
            
            translated_lines.append(translated_line)
        
        result = '\n'.join(translated_lines)
        
        if not result.strip():
            return f"【{doc_type}】\n辞書ベース翻訳を実行しましたが、翻訳可能な用語が見つかりませんでした。"
        
        return f"【{doc_type}辞書翻訳】\n{result}"
    
    def translate_technical_document(self, english_text: str) -> TechnicalTranslationResult:
        """技術文書の専門翻訳処理"""
        import time
        
        start_time = time.time()
        
        # 文書タイプの判定
        doc_type = self.classify_document_type(english_text)
        logger.info(f"検出された文書タイプ: {doc_type}")
        
        # テキストの前処理
        processed_text = self.preprocess_text(english_text)
        
        # 技術用語の抽出
        technical_terms = self.extract_technical_terms(processed_text)
        
        # 専門プロンプトの生成
        specialized_prompt = self.create_specialized_prompt(processed_text, doc_type)
        
        # LLMによる翻訳実行
        raw_translation: str = ""
        try:
            if self.llm_processor and hasattr(self.llm_processor, 'translate_technical_text'):
                # 実際のLLMプロセッサを使用
                llm_result = self.llm_processor.translate_technical_text(processed_text, doc_type)
                if llm_result.get('llm_used', False):
                    raw_translation = llm_result.get('japanese_translation', '')
                    logger.info("✅ 実際のLLMによる翻訳を使用")
                else:
                    # LLMが使用できない場合の辞書ベース翻訳
                    raw_translation = self._create_dictionary_translation(processed_text, technical_terms, doc_type)
                    logger.info("⚠️ 辞書ベース翻訳を使用")
            elif self.llm_processor and hasattr(self.llm_processor, 'create_completion'):
                # 旧形式のLLMプロセッサ
                response = self.llm_processor.create_completion(
                    prompt=specialized_prompt,
                    max_tokens=1000,
                    temperature=0.2,
                    top_p=0.9,
                    stop=["[INST]", "[/INST]", "English text:", "\n\nEnglish"]
                )
                
                if 'choices' in response and response['choices']:
                    raw_translation = str(response['choices'][0]['text']).strip()
                else:
                    raw_translation = "翻訳処理中にエラーが発生しました。"
            else:
                # 辞書ベース翻訳（バックアップ）
                raw_translation = self._create_dictionary_translation(processed_text, technical_terms, doc_type)
                logger.info("📖 辞書ベース翻訳を実行")
        
        except Exception as e:
            logger.error(f"翻訳処理エラー: {e}")
            raw_translation = self._create_dictionary_translation(processed_text, technical_terms, doc_type)
            logger.info("❌ エラーにより辞書ベース翻訳を使用")
        
        # 翻訳の後処理
        final_translation = self.postprocess_translation(raw_translation, doc_type)
        
        # 品質評価
        quality, confidence = self.assess_translation_quality(english_text, final_translation)
        
        processing_time = time.time() - start_time
        
        return TechnicalTranslationResult(
            japanese_translation=final_translation,
            document_type=doc_type,
            technical_terms_found=technical_terms,
            translation_quality=quality,
            processing_time=processing_time,
            confidence_score=confidence
        )
