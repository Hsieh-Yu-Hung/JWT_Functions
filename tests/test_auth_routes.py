#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT 認證路由測試腳本
展示如何使用 auth_routes.py 中的所有路由
"""

import requests
import json
from datetime import datetime

# 設定基礎 URL
BASE_URL = "http://localhost:9000"

def print_response(response, title):
    """美化輸出回應"""
    print(f"\n{'='*50}")
    print(f"📋 {title}")
    print(f"{'='*50}")
    print(f"狀態碼: {response.status_code}")
    print(f"回應內容:")
    try:
        print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    except:
        print(response.text)
    print(f"{'='*50}")

def test_health_check():
    """測試健康檢查"""
    response = requests.get(f"{BASE_URL}/health")
    print_response(response, "健康檢查")

def test_register():
    """測試使用者註冊"""
    data = {
        "email": "test@example.com",
        "password": "123456",
        "username": "測試使用者",
        "role": "user"
    }
    response = requests.post(f"{BASE_URL}/register", json=data)
    print_response(response, "使用者註冊")

def test_login():
    """測試使用者登入"""
    data = {
        "email": "test@example.com",
        "password": "123456"
    }
    response = requests.post(f"{BASE_URL}/login", json=data)
    print_response(response, "使用者登入")
    
    # 儲存 token 供後續使用
    if response.status_code == 200:
        return response.json().get("access_token")
    return None

def test_protected_route(token):
    """測試受保護的路由"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/protected", headers=headers)
    print_response(response, "受保護的路由")

def test_get_profile(token):
    """測試取得使用者資料"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    print_response(response, "取得使用者資料")

def test_update_profile(token):
    """測試更新使用者資料"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "username": "更新後的測試使用者"
    }
    response = requests.put(f"{BASE_URL}/profile", json=data, headers=headers)
    print_response(response, "更新使用者資料")

def test_change_password(token):
    """測試變更密碼"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "email": "test@example.com",
        "old_password": "123456",
        "new_password": "newpassword123"
    }
    response = requests.post(f"{BASE_URL}/change-password", json=data, headers=headers)
    print_response(response, "變更密碼")

def test_admin_stats(token):
    """測試管理員統計"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/admin/stats", headers=headers)
    print_response(response, "管理員統計")

def test_blacklist_stats():
    """測試黑名單統計（不需要 token）"""
    response = requests.get(f"{BASE_URL}/admin/blacklist-stats")
    print_response(response, "黑名單統計")

def test_get_users():
    """測試取得所有使用者（不需要 token）"""
    response = requests.get(f"{BASE_URL}/admin/users")
    print_response(response, "取得所有使用者")

def test_cleanup_tokens():
    """測試清理 token（不需要 token）"""
    response = requests.post(f"{BASE_URL}/admin/cleanup-tokens")
    print_response(response, "清理過期 Token")

def test_switch_account():
    """測試切換帳戶"""
    data = {
        "email": "test@example.com",
        "password": "newpassword123"
    }
    response = requests.post(f"{BASE_URL}/switch-account", json=data)
    print_response(response, "切換帳戶")
    return response.json().get("access_token") if response.status_code == 200 else None

def test_logout(token):
    """測試登出"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/logout", headers=headers)
    print_response(response, "使用者登出")

def main():
    """主要測試流程"""
    print("🚀 開始測試 JWT 認證路由")
    print(f"📍 目標服務: {BASE_URL}")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. 健康檢查
        test_health_check()
        
        # 2. 註冊新使用者
        test_register()
        
        # 3. 登入
        token = test_login()
        
        if token:
            # 4. 測試受保護的路由
            test_protected_route(token)
            
            # 5. 取得使用者資料
            test_get_profile(token)
            
            # 6. 更新使用者資料
            test_update_profile(token)
            
            # 7. 變更密碼
            test_change_password(token)
            
            # 8. 測試管理員功能
            test_admin_stats(token)
            
            # 9. 切換帳戶
            new_token = test_switch_account()
            
            if new_token:
                # 10. 使用新 token 測試
                test_protected_route(new_token)
                test_logout(new_token)
        
        # 11. 測試不需要 token 的管理員功能
        test_blacklist_stats()
        test_get_users()
        test_cleanup_tokens()
        
        print("\n✅ 所有測試完成！")
        
    except requests.exceptions.ConnectionError:
        print(f"\n❌ 無法連接到服務 {BASE_URL}")
        print("請確保服務正在運行：python app.py")
    except Exception as e:
        print(f"\n❌ 測試過程中發生錯誤: {str(e)}")

if __name__ == "__main__":
    main() 