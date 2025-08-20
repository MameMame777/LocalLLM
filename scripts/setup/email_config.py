"""
Email configuration tool for LocalLLM
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.email_sender import EmailSender


def setup_email_configuration():
    """Interactive email configuration setup"""
    print("📧 LocalLLM メール通知設定")
    print("=" * 50)
    
    print("\n📝 メール通知機能を使用すると、処理完了時に要約結果がメールで送信されます。")
    print("   Gmail, Outlookなどの一般的なメールプロバイダーに対応しています。")
    
    # Get sender email configuration
    print("\n🔧 送信者メール設定:")
    sender_email = input("送信者メールアドレス: ")
    
    print("\n🔑 メールパスワード設定:")
    print("   注意: Gmailの場合は「アプリパスワード」を使用してください。")
    print("   設定方法: https://support.google.com/accounts/answer/185833")
    sender_password = input("メールパスワード（アプリパスワード）: ")
    
    print("\n📮 通知先メール設定:")
    recipient_email = input("通知を受け取るメールアドレス: ")
    
    # Test configuration
    print("\n🧪 メール設定をテストしています...")
    email_sender = EmailSender()
    email_sender.configure_email(sender_email, sender_password)
    
    if email_sender.test_connection():
        print("✅ メール設定テスト成功!")
        
        # Save to environment file
        env_content = f"""
# Email Configuration for LocalLLM
EMAIL_SENDER={sender_email}
EMAIL_PASSWORD={sender_password}
NOTIFICATION_EMAIL={recipient_email}
"""
        
        env_file = Path(".env.email")
        with open(env_file, "w", encoding="utf-8") as f:
            f.write(env_content)
            
        print(f"\n💾 設定を {env_file} に保存しました。")
        print("\n📋 次のステップ:")
        print("1. .env.email ファイルの内容を .env ファイルに追加してください")
        print("2. または、以下の環境変数を設定してください:")
        print(f"   EMAIL_SENDER={sender_email}")
        print(f"   EMAIL_PASSWORD={sender_password}")
        print(f"   NOTIFICATION_EMAIL={recipient_email}")
        
        # Send test email
        send_test = input("\n📧 テストメールを送信しますか？ (y/n): ")
        if send_test.lower() == 'y':
            test_content = """
🤖 LocalLLM メール通知テスト

このメールは LocalLLM のメール通知機能のテストです。
設定が正常に完了しました。

今後、文書処理が完了すると、このアドレスに要約結果が送信されます。

LocalLLM チーム
"""
            
            try:
                from src.utils.email_sender import send_processing_notification
                success = send_processing_notification(
                    recipient_email=recipient_email,
                    file_path=Path("test_notification.txt"),
                    summary_content=test_content,
                    processing_metrics={
                        'processing_time': '5.2秒',
                        'original_length': '1,000 文字',
                        'summary_length': '250 文字',
                        'compression_ratio': '25%'
                    },
                    sender_email=sender_email,
                    sender_password=sender_password
                )
                
                if success:
                    print("✅ テストメールを送信しました。受信BOXを確認してください。")
                else:
                    print("❌ テストメールの送信に失敗しました。")
                    
            except Exception as e:
                print(f"❌ テストメール送信エラー: {e}")
        
    else:
        print("❌ メール設定テスト失敗")
        print("   - メールアドレスとパスワードを確認してください")
        print("   - Gmailの場合は「アプリパスワード」を使用してください")
        print("   - 2段階認証が有効になっているか確認してください")


def check_email_configuration():
    """Check current email configuration"""
    print("📧 現在のメール設定状況")
    print("=" * 30)
    
    sender_email = os.getenv("EMAIL_SENDER")
    sender_password = os.getenv("EMAIL_PASSWORD")
    recipient_email = os.getenv("NOTIFICATION_EMAIL")
    
    print(f"送信者メール: {sender_email if sender_email else '❌ 未設定'}")
    print(f"送信者パスワード: {'✅ 設定済み' if sender_password else '❌ 未設定'}")
    print(f"通知先メール: {recipient_email if recipient_email else '❌ 未設定'}")
    
    if all([sender_email, sender_password, recipient_email]):
        print("\n✅ メール通知が有効です")
        
        # Test connection
        print("\n🧪 接続テスト中...")
        email_sender = EmailSender()
        email_sender.configure_email(sender_email, sender_password)
        
        if email_sender.test_connection():
            print("✅ メールサーバー接続成功")
        else:
            print("❌ メールサーバー接続失敗")
    else:
        print("\n⚠️ メール通知が無効です")
        print("   setup_email_configuration() を実行して設定してください")


def disable_email_notifications():
    """Disable email notifications"""
    print("📧 メール通知を無効化します")
    
    # Remove from environment
    os.environ.pop("EMAIL_SENDER", None)
    os.environ.pop("EMAIL_PASSWORD", None)
    os.environ.pop("NOTIFICATION_EMAIL", None)
    
    print("✅ メール通知を無効化しました")
    print("   環境変数から削除されました")


if __name__ == "__main__":
    print("🤖 LocalLLM メール設定ツール")
    print("=" * 40)
    
    while True:
        print("\n📋 メニュー:")
        print("1. 📧 メール通知を設定")
        print("2. 🔍 現在の設定を確認")
        print("3. ❌ メール通知を無効化")
        print("4. 🚪 終了")
        
        choice = input("\n選択 (1-4): ")
        
        if choice == "1":
            setup_email_configuration()
        elif choice == "2":
            check_email_configuration()
        elif choice == "3":
            disable_email_notifications()
        elif choice == "4":
            print("👋 設定ツールを終了します")
            break
        else:
            print("❌ 無効な選択です")
