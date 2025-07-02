#!/usr/bin/env python3
"""
JWT Auth Middleware 套件測試腳本
測試新的 JWT Auth Middleware 套件是否正常運作
"""

import os
import sys
import requests
import json
from datetime import datetime

# 設定測試環境
BASE_URL = "http://localhost:9000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"
TEST_USERNAME = "testuser"

def print_status(message, status="INFO"):
    """印出狀態訊息"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    if status == "SUCCESS":
        print(f"✅ [{timestamp}] {message}")
    elif status == "ERROR":
        print(f"❌ [{timestamp}] {message}")
    elif status == "WARNING":
        print(f"⚠️ [{timestamp}] {message}")
    else:
        print(f"ℹ️ [{timestamp}] {message}")

def test_health_check():
    """測試健康檢查端點"""
    print_status("測試健康檢查端點...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print_status(f"健康檢查成功: {data.get('status')}", "SUCCESS")
            print_status(f"JWT Middleware 狀態: {data.get('jwt_middleware', 'unknown')}", "SUCCESS")
            return True
        else:
            print_status(f"健康檢查失敗: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"健康檢查異常: {str(e)}", "ERROR")
        return False

def test_user_registration():
    """測試使用者註冊"""
    print_status("測試使用者註冊...")
    try:
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "username": TEST_USERNAME,
            "role": "user"
        }
        response = requests.post(f"{BASE_URL}/register", json=data)
        if response.status_code in [201, 400]:  # 400 可能是使用者已存在
            data = response.json()
            if "message" in data and "successfully" in data["message"]:
                print_status("使用者註冊成功", "SUCCESS")
            else:
                print_status(f"使用者註冊回應: {data.get('msg', 'Unknown')}", "WARNING")
            return True
        else:
            print_status(f"使用者註冊失敗: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"使用者註冊異常: {str(e)}", "ERROR")
        return False

def test_user_login():
    """測試使用者登入"""
    print_status("測試使用者登入...")
    try:
        data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        response = requests.post(f"{BASE_URL}/login", json=data)
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print_status("使用者登入成功", "SUCCESS")
                print_status(f"取得 Token: {token[:20]}...", "SUCCESS")
                return token
            else:
                print_status("登入成功但沒有取得 Token", "ERROR")
                return None
        else:
            print_status(f"使用者登入失敗: {response.status_code}", "ERROR")
            return None
    except Exception as e:
        print_status(f"使用者登入異常: {str(e)}", "ERROR")
        return None

def test_protected_endpoint(token):
    """測試受保護的端點"""
    print_status("測試受保護的端點...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/protected", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_status("受保護端點訪問成功", "SUCCESS")
            print_status(f"使用者: {data.get('user_info', {}).get('email')}", "SUCCESS")
            return True
        else:
            print_status(f"受保護端點訪問失敗: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"受保護端點訪問異常: {str(e)}", "ERROR")
        return False

def test_admin_jwt_endpoints(token):
    """測試管理員 JWT 管理端點"""
    print_status("測試管理員 JWT 管理端點...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # 測試黑名單統計
        response = requests.get(f"{BASE_URL}/admin/jwt/blacklist", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_status("黑名單統計端點訪問成功", "SUCCESS")
        elif response.status_code == 403:
            print_status("需要管理員權限（這是正常的）", "WARNING")
        else:
            print_status(f"黑名單統計端點訪問失敗: {response.status_code}", "ERROR")
        
        # 測試清理端點
        response = requests.post(f"{BASE_URL}/admin/jwt/cleanup", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_status("Token 清理端點訪問成功", "SUCCESS")
        elif response.status_code == 403:
            print_status("需要管理員權限（這是正常的）", "WARNING")
        else:
            print_status(f"Token 清理端點訪問失敗: {response.status_code}", "ERROR")
            
        return True
    except Exception as e:
        print_status(f"管理員端點測試異常: {str(e)}", "ERROR")
        return False

def test_user_logout(token):
    """測試使用者登出"""
    print_status("測試使用者登出...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.post(f"{BASE_URL}/logout", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print_status("使用者登出成功", "SUCCESS")
            return True
        else:
            print_status(f"使用者登出失敗: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"使用者登出異常: {str(e)}", "ERROR")
        return False

def test_token_blacklist(token):
    """測試 Token 黑名單功能"""
    print_status("測試 Token 黑名單功能...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/protected", headers=headers)
        if response.status_code == 401:
            print_status("Token 已被加入黑名單（正常）", "SUCCESS")
            return True
        else:
            print_status(f"Token 黑名單測試失敗: {response.status_code}", "ERROR")
            return False
    except Exception as e:
        print_status(f"Token 黑名單測試異常: {str(e)}", "ERROR")
        return False

def main():
    """主測試函數"""
    print("🧪 JWT Auth Middleware 套件測試")
    print("=" * 50)
    
    # 檢查服務是否運行
    if not test_health_check():
        print_status("服務未運行，請先啟動服務", "ERROR")
        return
    
    # 測試使用者註冊
    test_user_registration()
    
    # 測試使用者登入
    token = test_user_login()
    if not token:
        print_status("無法取得 Token，停止測試", "ERROR")
        return
    
    # 測試受保護的端點
    test_protected_endpoint(token)
    
    # 測試管理員 JWT 端點
    test_admin_jwt_endpoints(token)
    
    # 測試使用者登出
    test_user_logout(token)
    
    # 測試 Token 黑名單
    test_token_blacklist(token)
    
    print("\n" + "=" * 50)
    print_status("測試完成！", "SUCCESS")

if __name__ == "__main__":
    main() 