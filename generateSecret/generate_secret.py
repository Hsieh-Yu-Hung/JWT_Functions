#!/usr/bin/env python3
"""
JWT SECRET_KEY 產生器
產生安全的隨機密鑰用於 JWT 簽署
"""

import secrets
import string
import base64
import os
from datetime import datetime

def generate_secret_method1(length=64):
    """方法一：使用 secrets 模組產生隨機字串"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_secret_method2(length=64):
    """方法二：使用 secrets.token_urlsafe (URL 安全)"""
    return secrets.token_urlsafe(length)

def generate_secret_method3(length=64):
    """方法三：使用 secrets.token_hex (十六進位)"""
    return secrets.token_hex(length // 2)

def generate_secret_method4(length=64):
    """方法四：使用 base64 編碼的隨機位元組"""
    random_bytes = secrets.token_bytes(length)
    return base64.b64encode(random_bytes).decode('utf-8')

def display_secret(method_name, secret, method_desc):
    """格式化顯示產生的密鑰"""
    print(f"\n{'='*60}")
    print(f"方法：{method_name}")
    print(f"說明：{method_desc}")
    print(f"長度：{len(secret)} 字元")
    print(f"{'='*60}")
    print(f"SECRET_KEY={secret}")
    print(f"{'='*60}")

def main():
    print("🔐 JWT SECRET_KEY 產生器")
    print("=" * 60)
    print(f"產生時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 產生四種不同類型的密鑰
    secrets_list = [
        ("隨機字串", generate_secret_method1(), "包含字母、數字和特殊字元的隨機字串"),
        ("URL 安全", generate_secret_method2(), "URL 安全的 base64 編碼字串"),
        ("十六進位", generate_secret_method3(), "十六進位格式的隨機字串"),
        ("Base64", generate_secret_method4(), "Base64 編碼的隨機位元組")
    ]
    
    for method_name, secret, description in secrets_list:
        display_secret(method_name, secret, description)
    
    print("\n📝 使用說明：")
    print("1. 選擇其中一個 SECRET_KEY")
    print("2. 複製 SECRET_KEY=xxxxx 這一行")
    print("3. 貼到您的 .env 檔案中")
    print("4. 確保 .env 檔案已加入 .gitignore")
    
    print("\n⚠️  安全提醒：")
    print("- 每個環境（開發、測試、生產）使用不同的 SECRET_KEY")
    print("- 定期更換 SECRET_KEY")
    print("- 不要將 .env 檔案提交到版本控制")
    print("- 建議使用至少 64 字元的密鑰")

if __name__ == "__main__":
    main() 