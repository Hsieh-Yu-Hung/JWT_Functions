#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API 診斷腳本
用於檢查 API 連接和配置問題
"""

import sys
import os
import requests
import json
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import API_BASE_URL, API_KEY
from database.api_manager import APIManager

def print_section(title):
    """打印分隔線"""
    print(f"\n{'='*60}")
    print(f"🔍 {title}")
    print(f"{'='*60}")

def print_result(success, message, details=None):
    """打印結果"""
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    if details:
        print(f"   詳情: {details}")

def check_environment_variables():
    """檢查環境變數"""
    print_section("檢查環境變數")
    
    # 檢查 API 配置
    print_result(bool(API_BASE_URL), f"API_BASE_URL: {API_BASE_URL}")
    print_result(bool(API_KEY), f"API_KEY: {'已設定' if API_KEY else '未設定'}")
    
    if not API_BASE_URL or not API_KEY:
        print("\n⚠️  請檢查 .env 檔案中的以下變數:")
        print("   - API_MODE (internal 或 public)")
        print("   - PUBLIC_API_BASE_URL 或 INTERNAL_API_BASE_URL")
        print("   - PUBLIC_API_KEY 或 INTERNAL_API_KEY")

def test_api_connection():
    """測試 API 連接"""
    print_section("測試 API 連接")
    
    try:
        # 測試基本連接
        response = requests.get(API_BASE_URL, timeout=10)
        print_result(True, f"基本連接成功: {response.status_code}")
    except requests.exceptions.ConnectionError as e:
        print_result(False, f"無法連接到 API: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print_result(False, f"連接超時: {e}")
        return False
    except Exception as e:
        print_result(False, f"連接錯誤: {e}")
        return False
    
    return True

def test_api_health():
    """測試 API 健康檢查"""
    print_section("測試 API 健康檢查")
    
    try:
        api = APIManager()
        result = api.health_check()
        
        if result.get("success"):
            print_result(True, "API 健康檢查通過")
            print(f"   回應: {result}")
        else:
            print_result(False, "API 健康檢查失敗")
            print(f"   錯誤: {result.get('message', '未知錯誤')}")
            if result.get('details'):
                print(f"   詳情: {result.get('details')}")
    except Exception as e:
        print_result(False, f"健康檢查異常: {e}")

def test_user_creation():
    """測試使用者創建"""
    print_section("測試使用者創建")
    
    try:
        api = APIManager()
        
        # 測試資料
        test_user = {
            "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
            "password_hash": "test_hash",
            "username": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_login": None
        }
        
        print(f"測試使用者資料: {test_user}")
        
        result = api.create_user(test_user)
        
        if result.get("success"):
            print_result(True, "使用者創建成功")
            print(f"   使用者 ID: {result.get('data', {}).get('id', '未知')}")
        else:
            print_result(False, "使用者創建失敗")
            print(f"   錯誤: {result.get('message', '未知錯誤')}")
            if result.get('details'):
                print(f"   詳情: {result.get('details')}")
            if result.get('status_code'):
                print(f"   狀態碼: {result.get('status_code')}")
    except Exception as e:
        print_result(False, f"使用者創建測試異常: {e}")

def test_user_search():
    """測試使用者搜尋"""
    print_section("測試使用者搜尋")
    
    try:
        api = APIManager()
        result = api.get_user_by_username("test@example.com")
        
        if result.get("success"):
            print_result(True, "使用者搜尋成功")
            if result.get("data"):
                print(f"   找到使用者: {result['data'].get('email', '未知')}")
            else:
                print("   未找到使用者（這是正常的）")
        else:
            print_result(False, "使用者搜尋失敗")
            print(f"   錯誤: {result.get('message', '未知錯誤')}")
            if result.get('details'):
                print(f"   詳情: {result.get('details')}")
    except Exception as e:
        print_result(False, f"使用者搜尋測試異常: {e}")

def check_api_endpoints():
    """檢查 API 端點"""
    print_section("檢查 API 端點")
    
    api = APIManager()
    
    endpoints = [
        ("使用者創建", api.endpoints["users"]),
        ("使用者搜尋", api.search_endpoints["users"]),
        ("使用者更新", api.update_endpoints["users"]),
        ("角色創建", api.endpoints["roles"]),
        ("黑名單", api.endpoints["blacklist"])
    ]
    
    for name, endpoint in endpoints:
        full_url = f"{API_BASE_URL}{endpoint}"
        print(f"📋 {name}: {full_url}")

def main():
    """主要診斷流程"""
    print("🚀 開始 API 診斷")
    print(f"⏰ 診斷時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. 檢查環境變數
    check_environment_variables()
    
    # 2. 測試基本連接
    if test_api_connection():
        # 3. 測試健康檢查
        test_api_health()
        
        # 4. 檢查端點
        check_api_endpoints()
        
        # 5. 測試使用者搜尋
        test_user_search()
        
        # 6. 測試使用者創建
        test_user_creation()
    
    print_section("診斷完成")
    print("💡 如果發現問題，請檢查:")
    print("   1. .env 檔案中的 API 配置")
    print("   2. API 服務是否正在運行")
    print("   3. 網路連接是否正常")
    print("   4. API Key 是否有效")

if __name__ == "__main__":
    main() 