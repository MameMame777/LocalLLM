#!/usr/bin/env python3
"""
GUI修正パッチ: Enhanced Academic Processing用の正しいメッセージ
"""

import re
from pathlib import Path

def fix_gui_messages():
    """GUIのメッセージを修正"""
    
    gui_file = Path("src/gui/batch_gui.py")
    content = gui_file.read_text(encoding='utf-8')
    
    # 修正対象の箇所
    replacements = [
        # 初期化メッセージ
        (r"self\.queue\.put\(\('status', '[^']*Initializing Google Translate processor[^']*'\)\)",
         "self.queue.put(('status', '🎓 Initializing Enhanced Academic processor...'))"),
        
        # エラーメッセージ
        (r"self\.queue\.put\(\('error', f'Google Translate processor not available: \{e\}'\)\)",
         "self.queue.put(('error', f'Enhanced Academic processor not available: {e}'))"),
        
        # ログメッセージ
        (r"self\.queue\.put\(\('log', f'[^']*Using Google Translate for reliable processing[^']*'\)\)",
         "self.queue.put(('log', f'🎓 Using Enhanced Academic Processing (LLM + Google Translate)'))"),
    ]
    
    modified = False
    for pattern, replacement in replacements:
        if re.search(pattern, content):
            content = re.sub(pattern, replacement, content)
            modified = True
            print(f"✅ Fixed: {pattern[:50]}...")
    
    if modified:
        gui_file.write_text(content, encoding='utf-8')
        print("✅ GUI messages updated successfully!")
    else:
        print("ℹ️ No changes needed")

if __name__ == "__main__":
    fix_gui_messages()
