#!/usr/bin/env python3
"""
LocalLLM メール設定ツール - 簡易版
Enhanced APIでメール送信機能を使用するための設定ファイルを作成します。
"""

import yaml
from pathlib import Path

def setup_email_config():
    """簡易メール設定セットアップ"""
    print("📧 LocalLLM メール設定ツール")
    print("=" * 50)
    
    print("\n⚠️ 注意: このツールは簡易設定用です。")
    print("実際の本番環境では、セキュリティに十分注意してください。")
    
    # 有効化確認
    enable = input("\nメール通知を有効化しますか？ (y/N): ").lower().strip()
    
    config = {
        'email': {
            'enabled': enable == 'y',
            'sender': {
                'email': '',
                'password': '',
                'name': 'LocalLLM システム'
            },
            'recipients': [],
            'smtp': {
                'server': 'smtp.gmail.com',
                'port': 587,
                'use_tls': True
            },
            'content': {
                'subject_prefix': '[LocalLLM]',
                'include_summary': True,
                'include_stats': True,
                'max_content_length': 5000
            },
            'attachments': {
                'enabled': True,
                'max_size_mb': 10,
                'formats': ['md', 'txt', 'pdf']
            }
        }
    }
    
    if enable == 'y':
        print("\n📝 送信者メール設定:")
        sender_email = input("送信者メールアドレス: ").strip()
        
        print("\n🔑 メールパスワード（Gmailの場合はアプリパスワード）:")
        print("   Googleアプリパスワード設定: https://support.google.com/accounts/answer/185833")
        sender_password = input("パスワード: ").strip()
        
        print("\n👥 受信者メールアドレス:")
        recipient = input("受信者メールアドレス: ").strip()
        
        # 設定を更新
        config['email']['sender']['email'] = sender_email
        config['email']['sender']['password'] = sender_password
        config['email']['recipients'] = [recipient] if recipient else []
        
        # SMTP設定の確認
        if '@gmail.com' in sender_email:
            config['email']['smtp']['server'] = 'smtp.gmail.com'
        elif '@outlook.com' in sender_email or '@hotmail.com' in sender_email:
            config['email']['smtp']['server'] = 'smtp-mail.outlook.com'
        else:
            custom_smtp = input(f"\nSMTPサーバー (デフォルト: {config['email']['smtp']['server']}): ").strip()
            if custom_smtp:
                config['email']['smtp']['server'] = custom_smtp
    
    # 設定ファイル保存
    config_dir = Path("config")
    config_dir.mkdir(exist_ok=True)
    
    config_file = config_dir / "email_config.yaml"
    
    with open(config_file, 'w', encoding='utf-8') as f:
        yaml.dump(config, f, default_flow_style=False, allow_unicode=True)
    
    print(f"\n✅ 設定ファイルを保存しました: {config_file}")
    
    if enable == 'y':
        print("\n📋 設定内容:")
        print(f"   送信者: {config['email']['sender']['email']}")
        print(f"   受信者: {', '.join(config['email']['recipients'])}")
        print(f"   SMTPサーバー: {config['email']['smtp']['server']}")
        
        print("\n🚀 Enhanced APIでのメール送信使用例:")
        print("```python")
        print("from src.api.enhanced_api import summarize_json, SummaryConfig")
        print("")
        print("config = SummaryConfig(")
        print("    language='ja',")
        print("    summary_type='brief',")
        print("    email_notification=True")
        print(")")
        print("")
        print("result = summarize_json(data, config=config)")
        print("```")
    else:
        print("\n📧 メール通知は無効化されています。")
        print("   必要に応じて設定ファイルを手動編集するか、このツールを再実行してください。")
    
    return config_file

def test_email_config():
    """メール設定をテスト"""
    config_file = Path("config/email_config.yaml")
    
    if not config_file.exists():
        print("❌ 設定ファイルが見つかりません。先に setup_email_config() を実行してください。")
        return
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    email_config = config.get('email', {})
    
    print("📧 現在のメール設定:")
    print(f"   有効化: {email_config.get('enabled', False)}")
    print(f"   送信者: {email_config.get('sender', {}).get('email', 'NOT SET')}")
    print(f"   受信者: {email_config.get('recipients', [])}")
    print(f"   SMTPサーバー: {email_config.get('smtp', {}).get('server', 'NOT SET')}")
    
    if email_config.get('enabled') and email_config.get('sender', {}).get('email'):
        print("\n✅ 設定は有効です。Enhanced APIでメール送信が可能です。")
    else:
        print("\n⚠️ 設定が不完全またはメール機能が無効化されています。")

if __name__ == "__main__":
    print("LocalLLM メール設定ツール")
    print("1. メール設定を作成")
    print("2. 現在の設定を確認")
    
    choice = input("\n選択 (1/2): ").strip()
    
    if choice == "1":
        setup_email_config()
    elif choice == "2":
        test_email_config()
    else:
        print("無効な選択です。")
