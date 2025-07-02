#!/usr/bin/env python3
"""
快速 JWT SECRET_KEY 產生器
產生一個安全的隨機密鑰
"""

import secrets
import string

def generate_secret():
    """產生安全的隨機密鑰"""
    # 使用字母、數字和特殊字元
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;:,.<>?"
    secret = ''.join(secrets.choice(alphabet) for _ in range(64))
    return secret

if __name__ == "__main__":
    secret = generate_secret()
    print("🔐 JWT SECRET_KEY")
    print("=" * 50)
    print(f"SECRET_KEY={secret}")
    print("=" * 50)
    print("請複製上面的 SECRET_KEY 到您的 .env 檔案中") 