#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色系統測試腳本
測試角色創建、指派和使用者角色映射功能
"""

import sys
import os
from datetime import datetime

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.role_model import RoleModel
from database.user_role_mapping_model import UserRoleMappingModel
from database.user_model import UserModel

def test_role_system():
    """測試角色系統"""
    print("🚀 測試角色系統")
    print(f"⏰ 測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 創建角色模型實例
        role_model = RoleModel()
        user_role_mapping = UserRoleMappingModel()
        user_model = UserModel()
        
        # 1. 測試取得所有角色
        print(f"\n📋 測試取得所有角色...")
        all_roles = role_model.get_all_roles()
        print(f"   找到 {len(all_roles)} 個角色")
        for role in all_roles:
            print(f"   - {role.get('role_name', '未知')}: {role.get('role_description', '無描述')}")
        
        # 2. 測試取得特定角色
        print(f"\n📋 測試取得 'user' 角色...")
        user_role = role_model.get_role_by_name("user")
        if user_role:
            print(f"   ✅ 找到 user 角色: {user_role.get('role_name')}")
            print(f"   權限: {user_role.get('role_permissions', [])}")
        else:
            print(f"   ❌ 未找到 user 角色")
        
        # 3. 測試取得 'admin' 角色
        print(f"\n📋 測試取得 'admin' 角色...")
        admin_role = role_model.get_role_by_name("admin")
        if admin_role:
            print(f"   ✅ 找到 admin 角色: {admin_role.get('role_name')}")
            print(f"   權限: {admin_role.get('role_permissions', [])}")
        else:
            print(f"   ❌ 未找到 admin 角色")
        
        # 4. 測試角色權限
        print(f"\n📋 測試角色權限...")
        user_permissions = role_model.get_role_permissions("user", include_inherited=True)
        print(f"   user 角色權限: {user_permissions}")
        
        admin_permissions = role_model.get_role_permissions("admin", include_inherited=True)
        print(f"   admin 角色權限: {admin_permissions}")
        
        # 5. 測試使用者角色指派
        print(f"\n📋 測試使用者角色指派...")
        # 創建測試使用者
        test_email = f"role_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}@example.com"
        test_password = "testpassword123"
        test_username = f"roletest_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        user_id = user_model.register_user(test_email, test_password, test_username)
        if user_id:
            print(f"   ✅ 創建測試使用者成功: {user_id}")
            
            # 指派角色
            try:
                result = user_role_mapping.assign_role_to_user(user_id, test_email, "user")
                if result:
                    print(f"   ✅ 指派 user 角色成功")
                else:
                    print(f"   ❌ 指派 user 角色失敗")
            except Exception as e:
                print(f"   ❌ 指派角色異常: {e}")
            
            # 檢查使用者角色
            user_role_data = user_role_mapping.get_user_role(user_id)
            if user_role_data:
                print(f"   ✅ 使用者角色: {user_role_data.get('role_name', '未知')}")
            else:
                print(f"   ❌ 未找到使用者角色")
            
            # 檢查使用者權限
            user_permissions = user_role_mapping.get_user_permissions(user_id)
            print(f"   ✅ 使用者權限: {user_permissions}")
            
        else:
            print(f"   ❌ 創建測試使用者失敗")
        
        print(f"\n✅ 角色系統測試完成！")
        
    except Exception as e:
        print(f"❌ 測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_role_system() 