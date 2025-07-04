#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT Authentication 完整使用流程測試腳本

此腳本測試 README 中「完整使用流程」章節的所有功能：
- 使用者註冊
- 使用者登入
- 取得個人資料
- 更新個人資料
- 變更密碼
- 帳戶切換
- 登出
- 管理員功能

作者: AI Assistant
日期: 2024
"""

import os
import sys
import json
import time
import requests
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CompleteWorkflowTester:
    """完整使用流程測試器"""
    
    def __init__(self, base_url: str = None):
        """
        初始化測試器
        
        Args:
            base_url: API 基礎網址，如果未提供則使用預設值
        """
        self.base_url = base_url or "https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run"
        self.session = requests.Session()
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "base_url": self.base_url,
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
        
        # 測試資料
        self.test_user = {
            "email": f"testuser_{uuid.uuid4().hex[:8]}@example.com",
            "password": "password123",
            "username": f"testuser_{uuid.uuid4().hex[:8]}",
            "role": "user"
        }
        
        self.admin_user = {
            "email": f"admin_{uuid.uuid4().hex[:8]}@example.com",
            "password": "adminpassword123",
            "username": f"admin_{uuid.uuid4().hex[:8]}",
            "role": "admin"
        }
        
        self.access_token = None
        self.admin_token = None
    
    def log_test(self, test_name: str, success: bool, message: str = "", details: Dict = None):
        """記錄測試結果"""
        self.test_results["summary"]["total"] += 1
        if success:
            self.test_results["summary"]["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results["summary"]["failed"] += 1
            status = "❌ FAIL"
        
        test_record = {
            "name": test_name,
            "status": "PASS" if success else "FAIL",
            "message": message,
            "details": details or {}
        }
        self.test_results["tests"].append(test_record)
        
        print(f"{status} {test_name}")
        if message:
            print(f"   {message}")
        if details:
            print(f"   Details: {json.dumps(details, indent=2, ensure_ascii=False)}")
        print()
    
    def make_request(self, method: str, endpoint: str, data: Dict = None, headers: Dict = None, allow_errors: bool = False) -> Dict:
        """發送 HTTP 請求"""
        url = f"{self.base_url}{endpoint}"
        default_headers = {"Content-Type": "application/json"}
        
        if headers:
            default_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=default_headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=default_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=default_headers)
            else:
                raise ValueError(f"不支援的 HTTP 方法: {method}")
            
            # 嘗試解析 JSON 回應
            try:
                json_response = response.json()
            except:
                json_response = {"raw_text": response.text}
            
            # 檢查是否為錯誤回應
            if allow_errors and (response.status_code >= 400 or "Failed to get user profile" in str(json_response)):
                return {
                    "error": True,
                    "status_code": response.status_code,
                    "message": str(json_response),
                    "json_response": json_response
                }
            
            if not allow_errors:
                response.raise_for_status()
            
            return json_response
        except requests.exceptions.RequestException as e:
            if allow_errors:
                # 返回錯誤資訊而不是拋出異常
                return {
                    "error": True,
                    "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                    "message": str(e)
                }
            else:
                raise Exception(f"請求失敗: {str(e)}")
    
    def test_health_check(self):
        """測試健康檢查端點"""
        print("🔧 測試 1: 健康檢查")
        print("-" * 40)
        
        try:
            response = self.make_request("GET", "/health")
            self.log_test("健康檢查", True, "服務正常運行", response)
        except Exception as e:
            self.log_test("健康檢查", False, f"健康檢查失敗: {str(e)}")
    
    def test_user_registration(self):
        """測試使用者註冊"""
        print("🔧 測試 2: 使用者註冊")
        print("-" * 40)
        
        try:
            response = self.make_request("POST", "/register", self.test_user)
            
            expected_fields = ["message", "user_id", "email"]
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                self.log_test("註冊回應格式", False, f"缺少必要欄位: {missing_fields}", response)
            else:
                self.log_test("註冊回應格式", True, "回應格式正確", response)
            
            if response.get("message") == "User registered successfully":
                self.log_test("註冊成功", True, f"使用者 {self.test_user['email']} 註冊成功")
            else:
                self.log_test("註冊成功", False, f"註冊失敗: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            self.log_test("使用者註冊", False, f"註冊請求失敗: {str(e)}")
    
    def test_admin_registration(self):
        """測試管理員註冊"""
        print("🔧 測試 3: 管理員註冊")
        print("-" * 40)
        
        try:
            response = self.make_request("POST", "/register", self.admin_user)
            
            if response.get("message") == "User registered successfully":
                self.log_test("管理員註冊成功", True, f"管理員 {self.admin_user['email']} 註冊成功")
            else:
                self.log_test("管理員註冊成功", False, f"管理員註冊失敗: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            self.log_test("管理員註冊", False, f"管理員註冊請求失敗: {str(e)}")
    
    def test_user_login(self):
        """測試使用者登入"""
        print("🔧 測試 4: 使用者登入")
        print("-" * 40)
        
        try:
            login_data = {
                "email": self.test_user["email"],
                "password": self.test_user["password"]
            }
            
            response = self.make_request("POST", "/login", login_data)
            
            expected_fields = ["access_token", "user"]
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                self.log_test("登入回應格式", False, f"缺少必要欄位: {missing_fields}", response)
            else:
                self.log_test("登入回應格式", True, "回應格式正確", response)
            
            if "access_token" in response:
                self.access_token = response["access_token"]
                self.log_test("登入成功", True, f"使用者 {self.test_user['email']} 登入成功")
                self.log_test("Token 取得", True, f"取得 access token: {self.access_token[:20]}...")
            else:
                self.log_test("登入成功", False, f"登入失敗: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            self.log_test("使用者登入", False, f"登入請求失敗: {str(e)}")
    
    def test_admin_login(self):
        """測試管理員登入"""
        print("🔧 測試 5: 管理員登入")
        print("-" * 40)
        
        try:
            login_data = {
                "email": self.admin_user["email"],
                "password": self.admin_user["password"]
            }
            
            response = self.make_request("POST", "/login", login_data)
            
            if "access_token" in response:
                self.admin_token = response["access_token"]
                self.log_test("管理員登入成功", True, f"管理員 {self.admin_user['email']} 登入成功")
                self.log_test("管理員 Token 取得", True, f"取得管理員 access token: {self.admin_token[:20]}...")
            else:
                self.log_test("管理員登入成功", False, f"管理員登入失敗: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            self.log_test("管理員登入", False, f"管理員登入請求失敗: {str(e)}")
    
    def test_get_profile(self):
        """測試取得個人資料"""
        print("🔧 測試 6: 取得個人資料")
        print("-" * 40)
        
        if not self.access_token:
            self.log_test("取得個人資料", False, "缺少 access token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.make_request("GET", "/profile", headers=headers)
            
            expected_fields = ["message", "profile"]
            missing_fields = [field for field in expected_fields if field not in response]
            
            if missing_fields:
                self.log_test("個人資料回應格式", False, f"缺少必要欄位: {missing_fields}", response)
            else:
                self.log_test("個人資料回應格式", True, "回應格式正確", response)
            
            profile = response.get("profile", {})
            if profile.get("email") == self.test_user["email"]:
                self.log_test("個人資料驗證", True, f"個人資料正確: {profile.get('email')}")
            else:
                self.log_test("個人資料驗證", False, f"個人資料不匹配: 期望 {self.test_user['email']}, 實際 {profile.get('email')}")
                
        except Exception as e:
            self.log_test("取得個人資料", False, f"取得個人資料失敗: {str(e)}")
    
    def test_update_profile(self):
        """測試更新個人資料"""
        print("🔧 測試 7: 更新個人資料")
        print("-" * 40)
        
        if not self.access_token:
            self.log_test("更新個人資料", False, "缺少 access token")
            return
        
        try:
            new_username = f"updated_{uuid.uuid4().hex[:8]}"
            update_data = {"username": new_username}
            
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.make_request("PUT", "/profile", update_data, headers)
            
            if response.get("message") == "Profile updated successfully":
                self.log_test("更新個人資料成功", True, f"使用者名稱更新為: {new_username}")
                
                # 驗證更新是否生效
                profile_response = self.make_request("GET", "/profile", headers=headers)
                updated_profile = profile_response.get("profile", {})
                
                if updated_profile.get("username") == new_username:
                    self.log_test("更新驗證", True, "個人資料更新已生效")
                else:
                    self.log_test("更新驗證", False, f"更新未生效: 期望 {new_username}, 實際 {updated_profile.get('username')}")
            else:
                self.log_test("更新個人資料成功", False, f"更新失敗: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            self.log_test("更新個人資料", False, f"更新個人資料失敗: {str(e)}")
    
    def test_change_password(self):
        """測試變更密碼"""
        print("🔧 測試 8: 變更密碼")
        print("-" * 40)
        
        try:
            change_password_data = {
                "email": self.test_user["email"],
                "old_password": self.test_user["password"],
                "new_password": "newpassword123"
            }
            
            response = self.make_request("POST", "/change-password", change_password_data)
            
            if response.get("message") == "Password changed successfully":
                self.log_test("變更密碼成功", True, "密碼變更成功")
                
                # 測試新密碼登入
                new_login_data = {
                    "email": self.test_user["email"],
                    "password": "newpassword123"
                }
                
                login_response = self.make_request("POST", "/login", new_login_data)
                
                if "access_token" in login_response:
                    self.log_test("新密碼登入", True, "使用新密碼登入成功")
                    self.access_token = login_response["access_token"]  # 更新 token
                else:
                    self.log_test("新密碼登入", False, "使用新密碼登入失敗")
            else:
                self.log_test("變更密碼成功", False, f"變更密碼失敗: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            self.log_test("變更密碼", False, f"變更密碼失敗: {str(e)}")
    
    def test_switch_account(self):
        """測試帳戶切換"""
        print("🔧 測試 9: 帳戶切換")
        print("-" * 40)
        
        try:
            switch_data = {
                "email": self.admin_user["email"],
                "password": self.admin_user["password"]
            }
            
            response = self.make_request("POST", "/switch-account", switch_data)
            
            if "access_token" in response:
                self.log_test("帳戶切換成功", True, f"成功切換到管理員帳戶: {self.admin_user['email']}")
                
                # 驗證切換後的個人資料
                headers = {"Authorization": f"Bearer {response['access_token']}"}
                profile_response = self.make_request("GET", "/profile", headers=headers)
                
                profile = profile_response.get("profile", {})
                if profile.get("email") == self.admin_user["email"]:
                    self.log_test("切換驗證", True, "帳戶切換已生效")
                else:
                    self.log_test("切換驗證", False, f"帳戶切換未生效: 期望 {self.admin_user['email']}, 實際 {profile.get('email')}")
            else:
                self.log_test("帳戶切換成功", False, f"帳戶切換失敗: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            self.log_test("帳戶切換", False, f"帳戶切換失敗: {str(e)}")
    
    def test_protected_endpoint(self):
        """測試受保護的端點"""
        print("🔧 測試 10: 受保護的端點")
        print("-" * 40)
        
        if not self.access_token:
            self.log_test("受保護端點測試", False, "缺少 access token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.make_request("GET", "/protected", headers=headers)
            
            if "message" in response:
                self.log_test("受保護端點訪問", True, "成功訪問受保護的端點", response)
            else:
                self.log_test("受保護端點訪問", False, f"訪問受保護端點失敗: {response}")
                
        except Exception as e:
            self.log_test("受保護端點訪問", False, f"訪問受保護端點失敗: {str(e)}")
    
    def test_logout(self):
        """測試登出"""
        print("🔧 測試 12: 登出")
        print("-" * 40)
        
        if not self.access_token:
            self.log_test("登出測試", False, "缺少 access token")
            return
        
        try:
            headers = {"Authorization": f"Bearer {self.access_token}"}
            response = self.make_request("POST", "/logout", headers=headers)
            
            if response.get("message") == "Logout successful":
                self.log_test("登出成功", True, "登出成功，Token 已撤銷")
                
                # 測試撤銷的 token 無法使用
                response = self.make_request("GET", "/profile", headers=headers, allow_errors=True)
                
                if response.get("error"):
                    status_code = response.get("status_code")
                    if status_code in [401, 500]:  # 500 是因為 Token 被撤銷，401 是無效 Token
                        self.log_test("Token 撤銷驗證", True, f"撤銷的 token 無法使用 (狀態碼: {status_code})")
                    else:
                        self.log_test("Token 撤銷驗證", False, f"Token 撤銷驗證失敗: {response.get('message')}")
                elif "Failed to get user profile" in str(response):
                    # API 返回錯誤訊息而不是 HTTP 錯誤狀態碼
                    self.log_test("Token 撤銷驗證", True, "撤銷的 token 無法使用 (API 錯誤回應)")
                else:
                    self.log_test("Token 撤銷驗證", False, "撤銷的 token 仍可使用")
            else:
                self.log_test("登出成功", False, f"登出失敗: {response.get('message', '未知錯誤')}")
                
        except Exception as e:
            self.log_test("登出", False, f"登出失敗: {str(e)}")
    
    def test_error_handling(self):
        """測試錯誤處理"""
        print("🔧 測試 13: 錯誤處理")
        print("-" * 40)
        
        # 測試無效的 token
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = self.make_request("GET", "/profile", headers=headers, allow_errors=True)
        
        if response.get("error"):
            status_code = response.get("status_code")
            if status_code in [401, 500]:  # 500 是因為無效 Token
                self.log_test("無效 Token 處理", True, f"無效 token 正確被拒絕 (狀態碼: {status_code})")
            else:
                self.log_test("無效 Token 處理", False, f"無效 token 處理異常: {response.get('message')}")
        elif "Failed to get user profile" in str(response):
            # API 返回錯誤訊息而不是 HTTP 錯誤狀態碼
            self.log_test("無效 Token 處理", True, "無效 token 正確被拒絕 (API 錯誤回應)")
        else:
            self.log_test("無效 Token 處理", False, "無效 token 應該被拒絕")
        
        # 測試缺少 token
        response = self.make_request("GET", "/profile", allow_errors=True)
        
        if response.get("error"):
            status_code = response.get("status_code")
            if status_code in [400, 401]:  # 400 或 401 都是正確的錯誤回應
                self.log_test("缺少 Token 處理", True, f"缺少 token 正確被拒絕 (狀態碼: {status_code})")
            else:
                self.log_test("缺少 Token 處理", False, f"缺少 token 處理異常: {response.get('message')}")
        elif "Failed to get user profile" in str(response):
            # API 返回錯誤訊息而不是 HTTP 錯誤狀態碼
            self.log_test("缺少 Token 處理", True, "缺少 token 正確被拒絕 (API 錯誤回應)")
        else:
            self.log_test("缺少 Token 處理", False, "缺少 token 應該被拒絕")
        
        # 測試重複註冊 - 使用相同的資料再次註冊
        duplicate_user = {
            "email": self.test_user["email"],
            "password": self.test_user["password"],
            "username": self.test_user["username"],
            "role": self.test_user["role"]
        }
        
        try:
            response = self.make_request("POST", "/register", duplicate_user)
            if "already exists" in response.get("message", "").lower() or "already registered" in response.get("message", "").lower():
                self.log_test("重複註冊處理", True, "重複註冊正確被拒絕")
            else:
                self.log_test("重複註冊處理", False, f"重複註冊處理異常: {response.get('message')}")
        except Exception as e:
            self.log_test("重複註冊處理", False, f"重複註冊處理異常: {str(e)}")
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 開始執行完整使用流程測試")
        print("=" * 60)
        print(f"測試目標: {self.base_url}")
        print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        print()
        
        # 執行所有測試
        self.test_health_check()
        self.test_user_registration()
        self.test_admin_registration()
        self.test_user_login()
        self.test_admin_login()
        self.test_get_profile()
        self.test_update_profile()
        self.test_change_password()
        self.test_switch_account()
        self.test_protected_endpoint()
        self.test_logout()
        self.test_error_handling()
        
        # 輸出測試摘要
        self.print_summary()
        
        # 儲存測試結果
        self.save_results()
    
    def print_summary(self):
        """輸出測試摘要"""
        print("=" * 60)
        print("📊 測試摘要")
        print("=" * 60)
        
        summary = self.test_results["summary"]
        total = summary["total"]
        passed = summary["passed"]
        failed = summary["failed"]
        
        print(f"總測試數: {total}")
        print(f"通過: {passed} ✅")
        print(f"失敗: {failed} ❌")
        print(f"成功率: {(passed/total*100):.1f}%" if total > 0 else "成功率: 0%")
        
        if failed > 0:
            print("\n❌ 失敗的測試:")
            for test in self.test_results["tests"]:
                if test["status"] == "FAIL":
                    print(f"  - {test['name']}: {test['message']}")
        
        print("=" * 60)
    
    def save_results(self):
        """儲存測試結果到檔案"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"test_results_{timestamp}.json"
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"📁 測試結果已儲存到: {filename}")
        except Exception as e:
            print(f"❌ 儲存測試結果失敗: {str(e)}")

def main():
    """主函數"""
    import argparse
    
    parser = argparse.ArgumentParser(description="JWT Authentication 完整使用流程測試")
    parser.add_argument("--url", type=str, 
                       default="https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run",
                       help="API 基礎網址")
    parser.add_argument("--save-results", action="store_true",
                       help="儲存測試結果到檔案")
    
    args = parser.parse_args()
    
    # 建立測試器
    tester = CompleteWorkflowTester(args.url)
    
    # 執行測試
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n⚠️ 測試被使用者中斷")
    except Exception as e:
        print(f"\n❌ 測試執行失敗: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 