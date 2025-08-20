#!/usr/bin/env python3
"""
LocalLLM Enhanced API with Configuration Support
===============================================

JSON入力対応＆設定ファイル対応の要約API

使用例:
```python
# 1. 引数で設定
from src.api.enhanced_api import summarize_json, SummaryConfi            return str(result)
            
        finally:
            # 一時ファイルの削除
            if temp_file_created and json_file_path.exists():
                os.unlink(json_file_path)
        
        # メール送信処理
        if final_config.email_notification:
            _send_email_notification(result, final_config, json_file_path)
        
    except Exception as e:
        return f"❌ JSON処理エラー: {e}" = SummaryConfig(language="ja", summary_type="detailed")
result = summarize_json(json_data, config=config)

# 2. 設定ファイルで設定
result = summarize_json(json_data, config_file="my_settings.yaml")

# 3. 混合（設定ファイル + 引数オーバーライド）
result = summarize_json(json_data, config_file="base.yaml", language="en")
```
"""

import sys
import json
import yaml
import tempfile
import os
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Union, Dict, List, Any, Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

@dataclass
class SummaryConfig:
    """要約設定クラス"""
    # 基本設定
    language: str = "ja"  # "ja", "en"
    summary_type: str = "brief"  # "brief", "detailed", "academic", "concise"
    
    # 出力設定
    output_format: str = "markdown"  # "markdown", "text", "html"
    max_length: Optional[int] = None  # 最大文字数制限
    
    # JSON処理設定
    individual_processing: bool = True  # 個別URL処理
    include_urls: bool = True  # URL情報を含める
    batch_size: int = 3  # バッチサイズ
    
    # 翻訳設定
    enable_translation: bool = True  # 翻訳を有効化
    translation_chunk_size: int = 5000  # 翻訳チャンクサイズ
    
    # 品質設定
    retry_count: int = 3  # リトライ回数
    timeout: int = 300  # タイムアウト（秒）
    
    # 詳細設定
    preserve_formatting: bool = True  # フォーマット保持
    include_metadata: bool = True  # メタデータ含める
    
    # メール送信設定
    email_notification: bool = False  # メール通知を有効化
    email_config_file: Optional[str] = None  # メール設定ファイルパス
    email_recipients: Optional[List[str]] = None  # 受信者リスト
    
    # メール通知設定
    enable_email: bool = False  # メール通知を有効化
    recipient_email: Optional[str] = None  # 受信者メールアドレス
    sender_email: Optional[str] = None  # 送信者メールアドレス
    sender_password: Optional[str] = None  # 送信者パスワード
    
    @classmethod
    def from_file(cls, config_file: Union[str, Path]) -> 'SummaryConfig':
        """設定ファイルから読み込み"""
        config_path = Path(config_file)
        
        if not config_path.exists():
            raise FileNotFoundError(f"設定ファイルが見つかりません: {config_path}")
        
        with open(config_path, 'r', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif config_path.suffix.lower() == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"サポートされていない設定ファイル形式: {config_path.suffix}")
        
        return cls(**data)
    
    def save_to_file(self, config_file: Union[str, Path]):
        """設定ファイルに保存"""
        config_path = Path(config_file)
        
        with open(config_path, 'w', encoding='utf-8') as f:
            if config_path.suffix.lower() in ['.yaml', '.yml']:
                yaml.dump(asdict(self), f, default_flow_style=False, allow_unicode=True)
            elif config_path.suffix.lower() == '.json':
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)
            else:
                raise ValueError(f"サポートされていない設定ファイル形式: {config_path.suffix}")
    
    def update(self, **kwargs: Any) -> None:
        """設定を更新"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            else:
                raise ValueError(f"未知の設定項目: {key}")

def summarize_json(
    json_input: Union[str, Path, Dict[str, Any], List[Any]],
    config: Optional[SummaryConfig] = None,
    config_file: Optional[Union[str, Path]] = None,
    **kwargs: Any
) -> str:
    """
    JSON形式のデータを要約（高機能版）
    
    Args:
        json_input: JSONデータ（辞書、リスト、ファイルパス、JSON文字列）
        config: SummaryConfig オブジェクト
        config_file: 設定ファイルのパス
        **kwargs: 設定のオーバーライド
    
    Returns:
        要約結果文字列
    """
    try:
        # 設定の準備
        if config_file:
            final_config = SummaryConfig.from_file(config_file)
        elif config:
            final_config = config
        else:
            final_config = SummaryConfig()
        
        # 引数による設定オーバーライド
        if kwargs:
            final_config.update(**kwargs)
        
        # メール設定の環境変数からの自動読み込み
        if final_config.enable_email and not final_config.recipient_email:
            import os
            final_config.recipient_email = os.getenv("NOTIFICATION_EMAIL")
            final_config.sender_email = os.getenv("EMAIL_SENDER") 
            final_config.sender_password = os.getenv("EMAIL_PASSWORD")
        
        # JSON入力の処理
        if isinstance(json_input, (str, Path)):
            input_path = Path(json_input)
            if input_path.exists():
                # ファイルパスの場合
                with open(input_path, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                json_file_path = input_path
            else:
                # JSON文字列の場合
                json_data = json.loads(str(json_input))
                json_file_path = None
        else:
            # 辞書またはリストの場合
            json_data = json_input
            json_file_path = None
        
        # 一時ファイルに保存（必要に応じて）
        if json_file_path is None:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
                json.dump(json_data, f, ensure_ascii=False, indent=2)
                json_file_path = Path(f.name)
            temp_file_created = True
        else:
            temp_file_created = False
        
        try:
            # 処理方法の選択
            if final_config.individual_processing and isinstance(json_data, list):
                # 個別URL処理
                from src.utils.individual_json_processor import IndividualJSONUrlProcessor
                processor = IndividualJSONUrlProcessor()
                result = processor.process_json_file_individually(json_file_path)
            else:
                # 通常のファイル処理
                from src.gui.enhanced_academic_processor import create_enhanced_academic_processing_function
                process_func = create_enhanced_academic_processing_function()
                
                result = process_func(
                    json_file_path,
                    target_language=final_config.language,
                    summary_type=final_config.summary_type,
                    output_format=final_config.output_format
                )
            
            # 結果の処理
            if isinstance(result, (str, Path)) and Path(result).exists():
                with open(result, 'r', encoding='utf-8') as f:
                    content = f.read()
                final_result = content
            else:
                final_result = str(result)
            
            # メール送信処理
            if final_config.email_notification and final_config.email_recipients:
                try:
                    _send_email_notification(final_result, final_config, json_file_path)
                except Exception as email_error:
                    print(f"⚠️ メール送信エラー: {email_error}")
            
            return final_result
            
        finally:
            # 一時ファイルの削除
            if temp_file_created and json_file_path and json_file_path.exists():
                try:
                    os.unlink(json_file_path)
                except Exception:
                    pass  # 削除失敗は無視
        
    except Exception as e:
        return f"❌ JSON処理エラー: {e}"

def summarize_file_with_config(
    file_path: Union[str, Path],
    config: Optional[SummaryConfig] = None,
    config_file: Optional[Union[str, Path]] = None,
    **kwargs: Any
) -> str:
    """
    ファイルを設定付きで要約
    
    Args:
        file_path: ファイルパス
        config: SummaryConfig オブジェクト
        config_file: 設定ファイルのパス
        **kwargs: 設定のオーバーライド
    
    Returns:
        要約結果文字列
    """
    file_path = Path(file_path)
    
    # JSONファイルの場合は専用処理
    if file_path.suffix.lower() == '.json':
        return summarize_json(file_path, config, config_file, **kwargs)
    
    try:
        # 設定の準備
        if config_file:
            final_config = SummaryConfig.from_file(config_file)
        elif config:
            final_config = config
        else:
            final_config = SummaryConfig()
        
        # 引数による設定オーバーライド
        if kwargs:
            final_config.update(**kwargs)
        
        # ファイル処理
        from src.gui.enhanced_academic_processor import create_enhanced_academic_processing_function
        process_func = create_enhanced_academic_processing_function()
        
        result = process_func(
            file_path,
            target_language=final_config.language,
            summary_type=final_config.summary_type,
            output_format=final_config.output_format
        )
        
        # 結果の処理
        if isinstance(result, (str, Path)) and Path(result).exists():
            with open(result, 'r', encoding='utf-8') as f:
                content = f.read()
            return content
        
        return str(result)
        
    except Exception as e:
        return f"❌ ファイル処理エラー: {e}"

def create_default_config_file(config_path: Union[str, Path] = "summary_config.yaml"):
    """デフォルト設定ファイルを作成"""
    config = SummaryConfig()
    config.save_to_file(config_path)
    print(f"✅ デフォルト設定ファイルを作成しました: {config_path}")
    return config_path

def list_available_settings():
    """利用可能な設定項目を表示"""
    config = SummaryConfig()
    print("🔧 利用可能な設定項目:")
    print("=" * 40)
    
    for field_name, field_info in config.__dataclass_fields__.items():
        field_type = field_info.type
        default_value = getattr(config, field_name)
        print(f"• {field_name}: {field_type} = {default_value}")
    
    print("\n📝 使用例:")
    print("config = SummaryConfig(language='en', summary_type='detailed')")
    print("result = summarize_json(data, config=config)")

# 使用例とテスト
def demo_enhanced_api():
    """Enhanced API のデモ"""
    print("🚀 Enhanced API Demo")
    print("=" * 50)
    
    # 1. デフォルト設定ファイル作成
    print("\n1. デフォルト設定ファイル作成:")
    config_file = create_default_config_file("demo_config.yaml")
    
    # 2. 設定項目の表示
    print("\n2. 利用可能な設定項目:")
    list_available_settings()
    
    # 3. JSONデータのテスト
    print("\n3. JSON要約テスト:")
    test_json = {
        "title": "Test Document",
        "content": "This is a test document for JSON summarization API.",
        "urls": [
            {"url": "https://example.com", "title": "Example"},
            {"url": "https://test.com", "title": "Test"}
        ]
    }
    
    # 引数で設定
    config = SummaryConfig(language="ja", summary_type="brief")
    result = summarize_json(test_json, config=config)
    print(f"要約結果: {result[:100]}..." if len(result) > 100 else f"要約結果: {result}")
    
    print("\n✅ Demo完了")

def _send_email_notification(result: str, config: SummaryConfig, file_path: Optional[Path]):
    """内部メール送信機能"""
    try:
        from src.utils.email_sender import EmailSender
        
        # メール設定ファイルからの読み込み
        if config.email_config_file:
            with open(config.email_config_file, 'r', encoding='utf-8') as f:
                email_config = yaml.safe_load(f)
        else:
            # デフォルト設定ファイルを試行
            default_config_path = project_root / "config" / "email_config.yaml"
            if default_config_path.exists():
                with open(default_config_path, 'r', encoding='utf-8') as f:
                    email_config = yaml.safe_load(f)
            else:
                print("⚠️ メール設定ファイルが見つかりません。メール送信をスキップします。")
                return
        
        # メール設定の確認
        email_settings = email_config.get('email', {})
        if not email_settings.get('enabled', False):
            print("📧 メール通知が無効化されています。")
            return
        
        sender_info = email_settings.get('sender', {})
        recipients = config.email_recipients or email_settings.get('recipients', [])
        
        if not all([sender_info.get('email'), sender_info.get('password'), recipients]):
            print("⚠️ メール設定が不完全です。送信をスキップします。")
            return
        
        # 処理メトリクス
        processing_metrics = {
            "api_call": True,
            "result_length": len(result),
            "language": config.language,
            "summary_type": config.summary_type,
            "processing_method": "Enhanced API"
        }
        
        # 各受信者にメール送信
        for recipient in recipients:
            if recipient:  # 空でない場合のみ送信
                from src.utils.email_sender import send_processing_notification
                success = send_processing_notification(
                    recipient_email=recipient,
                    file_path=file_path or Path("API_Input"),
                    summary_content=result[:email_settings.get('content', {}).get('max_content_length', 5000)],
                    processing_metrics=processing_metrics,
                    sender_email=sender_info['email'],
                    sender_password=sender_info['password']
                )
                if success:
                    print(f"✅ メール通知を送信しました: {recipient}")
                else:
                    print(f"❌ メール送信に失敗しました: {recipient}")
        
    except Exception as e:
        print(f"❌ メール送信エラー: {e}")

if __name__ == "__main__":
    demo_enhanced_api()
