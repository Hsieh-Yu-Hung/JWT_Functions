#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接測試 API 腳本
用於查看 API 的實際回應內容
"""

import sys
import os
import requests
import json
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.config import API_BASE_URL, API_KEY

def test_api_directly():
    """直接測試 API"""
    print("🚀 直接測試 API")
    print(f"📍 API URL: {API_BASE_URL}")
    print(f"🔑 API Key: {'已設定' if API_KEY else '未設定'}")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_KEY}" if API_KEY else ""
    }
    
    # 測試根路徑
    print(f"\n📋 測試根路徑: {API_BASE_URL}")
    try:
        response = requests.get(API_BASE_URL, headers=headers, timeout=10)
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.text[:500]}")
    except Exception as e:
        print(f"錯誤: {e}")
    
    # 測試健康檢查
    health_url = f"{API_BASE_URL}/health_check"
    print(f"\n📋 測試健康檢查: {health_url}")
    try:
        response = requests.get(health_url, headers=headers, timeout=10)
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.text[:500]}")
    except Exception as e:
        print(f"錯誤: {e}")
    
    # 測試使用者創建
    create_url = f"{API_BASE_URL}/add/document/users"
    test_data = {
        "data": {
            "email": f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com",
            "password_hash": "test_hash",
            "username": f"test_user_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "is_active": True,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "last_login": None
        }
    }
    print(f"\n📋 測試使用者創建: {create_url}")
    print(f"發送資料: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    try:
        response = requests.post(create_url, json=test_data, headers=headers, timeout=10)
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.text[:500]}")
    except Exception as e:
        print(f"錯誤: {e}")
    
    # 測試使用者搜尋
    search_url = f"{API_BASE_URL}/search/documents/users"
    print(f"\n📋 測試使用者搜尋: {search_url}")
    try:
        response = requests.get(search_url, headers=headers, timeout=10)
        print(f"狀態碼: {response.status_code}")
        print(f"回應內容: {response.text[:500]}")
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    test_api_directly() 