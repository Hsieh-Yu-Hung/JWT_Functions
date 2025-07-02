#!/usr/bin/env python3
"""
JWT Token 清理邏輯模組

提供 TokenCleaner 類別與 cleanup_tokens() 供 Flask app 或 CLI 使用
"""

import os
from datetime import datetime, UTC
from typing import Dict, Any

# 嘗試載入環境變數
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# 嘗試導入 pymongo
try:
    from pymongo import MongoClient
    from urllib.parse import quote_plus
    PYMONGO_AVAILABLE = True
except ImportError:
    PYMONGO_AVAILABLE = False

class TokenCleaner:
    """JWT Token 清理器"""
    def __init__(self):
        self.initialized = False
        self.client = None
        self.db = None
    
    def initialize(self) -> bool:
        try:
            if not os.environ.get('JWT_SECRET_KEY'):
                print("❌ 缺少 JWT_SECRET_KEY 環境變數")
                return False
            db_vars = ['DB_ACCOUNT', 'DB_PASSWORD', 'DB_URI', 'DB_NAME']
            missing_vars = [var for var in db_vars if not os.environ.get(var)]
            if missing_vars:
                print(f"⚠️ 缺少資料庫環境變數: {', '.join(missing_vars)}")
                print("📝 將跳過資料庫操作")
                self.initialized = True
                return True
            if PYMONGO_AVAILABLE:
                try:
                    db_account = os.environ['DB_ACCOUNT']
                    db_password = os.environ['DB_PASSWORD']
                    db_uri = os.environ['DB_URI']
                    db_name = os.environ['DB_NAME']
                    encoded_username = quote_plus(db_account)
                    encoded_password = quote_plus(db_password)
                    mongo_uri = f"mongodb://{encoded_username}:{encoded_password}@{db_uri}"
                    self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
                    self.db = self.client[db_name]
                    self.client.admin.command('ping')
                    print("✅ 資料庫連接成功")
                except Exception as e:
                    print(f"⚠️ 資料庫連接失敗: {e}")
                    print("📝 將繼續執行清理，但可能無法獲取完整統計")
            else:
                print("📝 pymongo 不可用，跳過資料庫操作")
            self.initialized = True
            return True
        except Exception as e:
            print(f"❌ 初始化失敗: {e}")
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
            if self.db is not None:
                try:
                    collection = self.db["blacklist"]
                    result = collection.delete_many({
                        "expires_at": {"$lt": datetime.now(UTC)}
                    })
                    cleaned_count = result.deleted_count
                    print(f"✅ 資料庫清理完成，清理了 {cleaned_count} 個過期記錄")
                except Exception as e:
                    print(f"⚠️ 資料庫清理失敗: {e}")
                    cleaned_count = 0
            else:
                print("📝 資料庫不可用，跳過資料庫清理")
            memory_saved = self._calculate_memory_saved(cleaned_count)
            result = {
                "success": True,
                "cleaned_count": cleaned_count,
                "remaining_tokens": 0,
                "estimated_memory_usage": 0,
                "memory_saved_bytes": memory_saved,
                "memory_saved_mb": round(memory_saved / (1024 * 1024), 2),
                "timestamp": datetime.now().isoformat(),
                "execution_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "message": f"清理完成，共清理 {cleaned_count} 個過期 token"
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
            print(f"   - 預估節省記憶體：{result['memory_saved_mb']} MB")
            print(f"   - 執行時間：{result['execution_time']}")
        else:
            print(f"❌ 清理失敗：{result.get('error', '未知錯誤')}")
    def __del__(self):
        if self.client:
            try:
                self.client.close()
            except:
                pass

token_cleaner = TokenCleaner()
def cleanup_tokens() -> Dict[str, Any]:
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