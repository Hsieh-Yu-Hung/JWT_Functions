#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JWT Authentication 系統測試腳本

此腳本整合了所有系統測試功能，包括：
- API 配置測試
- API 端點測試
- 模型導入和實例化測試
- 檔案結構檢查
- 環境變數驗證
"""

import os
import sys
import json
from datetime import datetime
from typing import Dict, List, Tuple, Any

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

class SystemTester:
    """系統測試器"""
    
    def __init__(self):
        self.test_results = {
            "timestamp": datetime.now().isoformat(),
            "tests": [],
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
    
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
    
    def test_environment_variables(self):
        """測試環境變數配置"""
        print("🔧 測試 1: 環境變數配置")
        print("-" * 40)
        
        required_vars = [
            "API_MODE",
            "PUBLIC_API_BASE_URL", 
            "PUBLIC_API_KEY",
            "INTERNAL_API_BASE_URL",
            "INTERNAL_API_KEY"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            self.log_test("環境變數檢查", False, f"缺少必要的環境變數: {', '.join(missing_vars)}")
        else:
            self.log_test("環境變數檢查", True, "所有必要的環境變數都已設定")
        
        # 檢查 API 模式
        api_mode = os.getenv("API_MODE")
        if api_mode not in ["public", "internal"]:
            self.log_test("API 模式檢查", False, f"API_MODE 必須是 'public' 或 'internal'，當前值: {api_mode}")
        else:
            self.log_test("API 模式檢查", True, f"API 模式設定為: {api_mode}")
        
        # 檢查 API 網址格式
        public_url = os.getenv("PUBLIC_API_BASE_URL")
        internal_url = os.getenv("INTERNAL_API_BASE_URL")
        
        if public_url and not public_url.startswith(("http://", "https://")):
            self.log_test("公網 API 網址格式", False, f"公網 API 網址格式錯誤: {public_url}")
        else:
            self.log_test("公網 API 網址格式", True, f"公網 API 網址: {public_url}")
        
        if internal_url and not internal_url.startswith(("http://", "https://")):
            self.log_test("內網 API 網址格式", False, f"內網 API 網址格式錯誤: {internal_url}")
        else:
            self.log_test("內網 API 網址格式", True, f"內網 API 網址: {internal_url}")
    
    def test_api_configuration(self):
        """測試 API 配置"""
        print("🔧 測試 2: API 配置")
        print("-" * 40)
        
        try:
            from core.config import API_MODE, API_BASE_URL, API_KEY
            
            self.log_test("配置載入", True, f"API 模式: {API_MODE}, 網址: {API_BASE_URL}")
            
            # 測試 API 管理器
            from database.api_manager import api_manager
            
            # 測試健康檢查
            try:
                health_response = api_manager.health_check()
                self.log_test("API 健康檢查", True, "API 服務正常運行", health_response)
            except Exception as e:
                self.log_test("API 健康檢查", False, f"API 健康檢查失敗: {str(e)}")
            
            # 測試獲取集合清單
            try:
                collections_response = api_manager.get_collections()
                self.log_test("獲取集合清單", True, "成功獲取集合清單", collections_response)
            except Exception as e:
                self.log_test("獲取集合清單", False, f"獲取集合清單失敗: {str(e)}")
            
        except ImportError as e:
            self.log_test("API 配置載入", False, f"無法載入 API 配置: {str(e)}")
        except Exception as e:
            self.log_test("API 配置測試", False, f"API 配置測試失敗: {str(e)}")
    
    def test_api_endpoints(self):
        """測試 API 端點配置"""
        print("🔧 測試 3: API 端點配置")
        print("-" * 40)
        
        try:
            from database.api_manager import APIManager, api_manager
            
            # 檢查端點配置
            temp_manager = APIManager()
            endpoint_configs = [
                ("新增端點", temp_manager.endpoints),
                ("查詢端點", temp_manager.search_endpoints),
                ("更新端點", temp_manager.update_endpoints),
                ("刪除端點", temp_manager.delete_endpoints)
            ]
            
            for config_name, endpoints in endpoint_configs:
                if not endpoints:
                    self.log_test(f"{config_name}配置", False, f"{config_name}為空")
                else:
                    self.log_test(f"{config_name}配置", True, f"包含 {len(endpoints)} 個端點", endpoints)
            
            # 測試具體端點
            test_endpoints = [
                ("用戶查詢端點", "/search/documents/users"),
                ("角色查詢端點", "/search/documents/roles"),
                ("用戶角色映射查詢端點", "/search/documents/user_role_mapping"),
                ("黑名單查詢端點", "/search/documents/blacklist")
            ]
            
            for endpoint_name, endpoint_path in test_endpoints:
                try:
                    response = api_manager._make_request("GET", endpoint_path, params={"limit": 1})
                    self.log_test(f"{endpoint_name}訪問", True, f"端點 {endpoint_path} 可正常訪問")
                except Exception as e:
                    self.log_test(f"{endpoint_name}訪問", False, f"端點 {endpoint_path} 訪問失敗: {str(e)}")
            
        except Exception as e:
            self.log_test("API 端點配置", False, f"API 端點配置測試失敗: {str(e)}")
    
    def test_model_imports(self):
        """測試模型導入"""
        print("🔧 測試 4: 模型導入")
        print("-" * 40)
        
        models_to_test = [
            ("API 管理器", "database.api_manager", ["api_manager", "APIManager"]),
            ("用戶模型", "database.user_model", ["UserModel"]),
            ("角色模型", "database.role_model", ["RoleModel"]),
            ("用戶角色映射模型", "database.user_role_mapping_model", ["UserRoleMappingModel"]),
            ("黑名單模型", "database.blacklist_model", ["BlacklistModel"])
        ]
        
        for model_name, module_path, classes in models_to_test:
            try:
                module = __import__(module_path, fromlist=classes)
                for class_name in classes:
                    if hasattr(module, class_name):
                        self.log_test(f"{model_name} - {class_name}導入", True, "")
                    else:
                        self.log_test(f"{model_name} - {class_name}導入", False, f"類別 {class_name} 不存在")
            except Exception as e:
                self.log_test(f"{model_name}導入", False, f"導入失敗: {str(e)}")
        
        # 測試整體模組導入
        try:
            from database import (
                api_manager, APIManager,
                UserModel, RoleModel, 
                UserRoleMappingModel, BlacklistModel
            )
            self.log_test("資料庫模組整體導入", True, "")
        except Exception as e:
            self.log_test("資料庫模組整體導入", False, f"整體導入失敗: {str(e)}")
    
    def test_model_instantiation(self):
        """測試模型實例化"""
        print("🔧 測試 5: 模型實例化")
        print("-" * 40)
        
        models_to_test = [
            ("API 管理器", "database.api_manager", "APIManager"),
            ("用戶模型", "database.user_model", "UserModel"),
            ("角色模型", "database.role_model", "RoleModel"),
            ("用戶角色映射模型", "database.user_role_mapping_model", "UserRoleMappingModel"),
            ("黑名單模型", "database.blacklist_model", "BlacklistModel")
        ]
        
        for model_name, module_path, class_name in models_to_test:
            try:
                module = __import__(module_path, fromlist=[class_name])
                model_class = getattr(module, class_name)
                instance = model_class()
                self.log_test(f"{model_name}實例化", True, "")
            except Exception as e:
                self.log_test(f"{model_name}實例化", False, f"實例化失敗: {str(e)}")
    
    def test_file_structure(self):
        """測試檔案結構"""
        print("🔧 測試 6: 檔案結構")
        print("-" * 40)
        
        # 檢查 base_model.py 是否已被移除
        base_model_path = os.path.join("database", "base_model.py")
        if os.path.exists(base_model_path):
            self.log_test("base_model.py 移除", False, "檔案仍然存在")
        else:
            self.log_test("base_model.py 移除", True, "")
        
        # 檢查必要檔案是否存在
        required_files = [
            "database/api_manager.py",
            "database/user_model.py",
            "database/role_model.py",
            "database/user_role_mapping_model.py",
            "database/blacklist_model.py",
            "database/__init__.py",
            "core/config.py",
            "core/jwt_utils.py"
        ]
        
        for file_path in required_files:
            if os.path.exists(file_path):
                self.log_test(f"{file_path} 存在", True, "")
            else:
                self.log_test(f"{file_path} 存在", False, "檔案不存在")
    
    def test_jwt_functionality(self):
        """測試 JWT 功能"""
        print("🔧 測試 7: JWT 功能")
        print("-" * 40)
        
        try:
            from core.jwt_utils import JWTManager
            jwt_manager = JWTManager()
            self.log_test("JWT 管理器初始化", True, "")
            
            # 測試 JWT 工具函數導入
            from core.jwt_utils import token_required
            self.log_test("JWT 裝飾器導入", True, "")
            
        except Exception as e:
            self.log_test("JWT 功能測試", False, f"JWT 功能測試失敗: {str(e)}")
    
    def run_all_tests(self):
        """執行所有測試"""
        print("🚀 JWT Authentication 系統測試")
        print("=" * 60)
        print(f"測試時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        # 執行所有測試
        self.test_environment_variables()
        self.test_api_configuration()
        self.test_api_endpoints()
        self.test_model_imports()
        self.test_model_instantiation()
        self.test_file_structure()
        self.test_jwt_functionality()
        
        # 輸出測試摘要
        print("📊 測試摘要")
        print("=" * 60)
        summary = self.test_results["summary"]
        print(f"總測試數: {summary['total']}")
        print(f"通過: {summary['passed']} ✅")
        print(f"失敗: {summary['failed']} ❌")
        print(f"成功率: {(summary['passed'] / summary['total'] * 100):.1f}%" if summary['total'] > 0 else "成功率: 0%")
        
        # 輸出失敗的測試
        if summary['failed'] > 0:
            print("\n❌ 失敗的測試:")
            for test_record in self.test_results["tests"]:
                if test_record["status"] == "FAIL":
                    print(f"  - {test_record['name']}: {test_record['message']}")
        
        # 保存測試結果
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = f"system_test_result_{timestamp}.json"
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(self.test_results, f, indent=2, ensure_ascii=False)
            print(f"\n📄 測試結果已保存到: {result_file}")
        except Exception as e:
            print(f"\n⚠️ 無法保存測試結果: {str(e)}")
        
        return summary['failed'] == 0

def main():
    """主函數"""
    tester = SystemTester()
    success = tester.run_all_tests()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 所有測試通過！系統運作正常。")
        sys.exit(0)
    else:
        print("⚠️ 部分測試失敗，請檢查相關問題。")
        sys.exit(1)

if __name__ == "__main__":
    main() 