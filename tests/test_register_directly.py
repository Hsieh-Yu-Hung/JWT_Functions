#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接測試註冊功能
繞過 Web 服務直接測試 UserModel
"""

import sys
import os
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.user_model import UserModel

def test_register_directly():
    """直接測試註冊功能"""
    print("🚀 直接測試使用者註冊功能")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 創建 UserModel 實例
        user_model = UserModel()
        
        # 測試資料
        test_email = f"test_register_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        test_password = "testpassword123"
        test_username = f"testuser_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        print(f"\n📋 測試資料:")
        print(f"   Email: {test_email}")
        print(f"   Username: {test_username}")
        print(f"   Password: {test_password}")
        
        # 執行註冊
        print(f"\n🔄 開始註冊...")
        user_id = user_model.register_user(test_email, test_password, test_username)
        
        if user_id:
            print(f"✅ 註冊成功！")
            print(f"   使用者 ID: {user_id}")
            
            # 測試登入
            print(f"\n🔄 測試登入...")
            user_data = user_model.authenticate_user(test_email, test_password)
            
            if user_data:
                print(f"✅ 登入成功！")
                print(f"   使用者資料: {user_data}")
            else:
                print(f"❌ 登入失敗")
                
        else:
            print(f"❌ 註冊失敗")
            
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_register_directly() 