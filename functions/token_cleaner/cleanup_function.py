#!/usr/bin/env python3
"""
JWT Token 清理邏輯模組

使用 jwt_auth_middleware 套件提供 TokenCleaner 類別與 cleanup_tokens() 供 Flask app 或 CLI 使用
"""

import os
from datetime import datetime, UTC
from typing import Dict, Any

# 嘗試載入環境變數
try:
    from dotenv import load_dotenv
    load_dotenv(dotenv_path=".env.local")
except ImportError:
    print("❌ 缺少 dotenv 模組")

# 導入 jwt_auth_middleware 套件
try:
    # 嘗試從專案根目錄匯入
    import sys
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from jwt_auth_middleware import (
        JWTConfig,
        set_jwt_config
    )
    # 使用本地的業務邏輯函數
    from jwt_utils import (
        cleanup_expired_blacklist_tokens,
        get_blacklist_statistics
    )
    JWT_MIDDLEWARE_AVAILABLE = True
except ImportError:
    JWT_MIDDLEWARE_AVAILABLE = False
    print("❌ jwt_auth_middleware 套件不可用")

class TokenCleaner:
    """JWT Token 清理器 - 使用 jwt_auth_middleware 套件"""
    def __init__(self):
        self.initialized = False
        self.jwt_config = None
    
    def initialize(self) -> bool:
        try:
            # 檢查必要的環境變數
            if not os.environ.get('JWT_SECRET_KEY'):
                print("❌ 缺少 JWT_SECRET_KEY 環境變數")
                return False
            
            # 檢查套件是否可用
            if not JWT_MIDDLEWARE_AVAILABLE:
                print("❌ jwt_auth_middleware 套件不可用")
                return False
            
            return self._initialize_with_middleware()
                
        except Exception as e:
            print(f"❌ 初始化失敗: {e}")
            return False
    
    def _initialize_with_middleware(self) -> bool:
        """使用 jwt_auth_middleware 套件初始化"""
        try:
            # 從環境變數獲取配置
            secret_key = os.environ.get('JWT_SECRET_KEY')
            config_file = os.environ.get('CONFIG_FILE', 'config.yaml')
            
            # 建立 JWT 配置
            self.jwt_config = JWTConfig(
                secret_key=secret_key,
                config_file=config_file
            )
            
            # 設定全域配置
            set_jwt_config(self.jwt_config)
            
            print("✅ 使用 jwt_auth_middleware 套件初始化成功")
            self.initialized = True
            return True
            
        except Exception as e:
            print(f"❌ jwt_auth_middleware 初始化失敗: {e}")
            return False
    
    def cleanup_tokens(self) -> Dict[str, Any]:
        if not self.initialized:
            if not self.initialize():
                return {
                    "success": False,
                    "error": "初始化失敗",
                    "cleaned_count": 0,
                    "timestamp": datetime.now().isoformat()
                }
        
        try:
            cleaned_count = 0
            remaining_tokens = 0
            total_tokens = 0
            expired_tokens = 0
            
            # 使用套件功能
            if JWT_MIDDLEWARE_AVAILABLE and self.jwt_config:
                try:
                    # 使用套件的清理功能
                    cleaned_count = cleanup_expired_blacklist_tokens()
                    
                    # 取得統計資訊
                    stats = get_blacklist_statistics()
                    remaining_tokens = stats.get('active_tokens', 0)
                    total_tokens = stats.get('total_tokens', 0)
                    expired_tokens = stats.get('expired_tokens', 0)
                    
                    print("cleaned_count", cleaned_count)
                    print("remaining_tokens", remaining_tokens)
                    print("total_tokens", total_tokens)
                    print("expired_tokens", expired_tokens)
                    print(f"✅ 套件清理完成，清理了 {cleaned_count} 個過期記錄")
                    
                except Exception as e:
                    print(f"❌ 套件清理失敗: {e}")
                    cleaned_count = 0
            else:
                print("❌ jwt_auth_middleware 套件不可用")
                return {
                    "success": False,
                    "error": "jwt_auth_middleware 套件不可用",
                    "cleaned_count": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            memory_saved = self._calculate_memory_saved(cleaned_count)
            result = {
                "success": True,
                "cleaned_count": cleaned_count,
                "remaining_tokens": remaining_tokens,
                "total_tokens": total_tokens,
                "expired_tokens": expired_tokens,
                "estimated_memory_usage": 0,
                "memory_saved_bytes": memory_saved,
                "memory_saved_mb": round(memory_saved / (1024 * 1024), 2),
                "timestamp": datetime.now().isoformat(),
                "execution_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "message": f"清理完成，共清理 {cleaned_count} 個過期 token",
                "method": "jwt_auth_middleware"
            }
            self._log_cleanup_result(result)
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e),
                "cleaned_count": 0,
                "timestamp": datetime.now().isoformat()
            }
            print(f"❌ 清理過程發生錯誤: {e}")
            return error_result
    
    def _calculate_memory_saved(self, cleaned_count: int) -> int:
        avg_token_size = 500
        return cleaned_count * avg_token_size
    
    def _log_cleanup_result(self, result: Dict[str, Any]):
        if result["success"]:
            print(f"✅ 清理完成：")
            print(f"   - 清理了 {result['cleaned_count']} 個過期 token")
            print(f"   - 剩餘有效 token: {result['remaining_tokens']}")
            print(f"   - 總 token 數: {result['total_tokens']}")
            print(f"   - 預估節省記憶體：{result['memory_saved_mb']} MB")
            print(f"   - 執行時間：{result['execution_time']}")
            print(f"   - 使用方法：{result.get('method', 'unknown')}")
        else:
            print(f"❌ 清理失敗：{result.get('error', '未知錯誤')}")

# 全域實例
token_cleaner = TokenCleaner()

def cleanup_tokens() -> Dict[str, Any]:
    """清理過期 tokens 的主要函數"""
    return token_cleaner.cleanup_tokens()

if __name__ == "__main__":
    print("🧹 JWT Token 清理器測試")
    print("=" * 50)
    if not os.environ.get('JWT_SECRET_KEY'):
        print("❌ 錯誤：缺少 JWT_SECRET_KEY 環境變數")
        print("📝 請設定 JWT_SECRET_KEY 環境變數後再執行")
        import sys; sys.exit(1)
    result = cleanup_tokens()
    import json
    print("\n📊 測試結果:")
    print(json.dumps(result, ensure_ascii=False, indent=2)) 