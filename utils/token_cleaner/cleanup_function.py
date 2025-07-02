#!/usr/bin/env python3
"""
JWT Token 清理 Function

適用於阿里雲 Function Compute 的獨立清理服務
可以設定為定時觸發，定期清理過期的 JWT Token
"""

import json
import os
import sys
from datetime import datetime, UTC
from typing import Dict, Any

# 嘗試載入環境變數
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv 不可用，將使用系統環境變數")

# 嘗試導入 pymongo
try:
    from pymongo import MongoClient
    from urllib.parse import quote_plus
    PYMONGO_AVAILABLE = True
    print("✅ pymongo 載入成功")
except ImportError as e:
    print(f"⚠️ pymongo 不可用: {e}")
    print("📝 將跳過資料庫操作")
    PYMONGO_AVAILABLE = False

class TokenCleaner:
    """JWT Token 清理器"""
    
    def __init__(self):
        """初始化清理器"""
        self.initialized = False
        self.client = None
        self.db = None
        
    def initialize(self) -> bool:
        """初始化資料庫連接"""
        try:
            # 檢查環境變數
            if not os.environ.get('JWT_SECRET_KEY'):
                print("❌ 缺少 JWT_SECRET_KEY 環境變數")
                return False
            
            # 檢查資料庫環境變數
            db_vars = ['DB_ACCOUNT', 'DB_PASSWORD', 'DB_URI', 'DB_NAME']
            missing_vars = [var for var in db_vars if not os.environ.get(var)]
            
            if missing_vars:
                print(f"⚠️ 缺少資料庫環境變數: {', '.join(missing_vars)}")
                print("📝 將跳過資料庫操作")
                self.initialized = True
                return True
            
            # 嘗試連接資料庫
            if PYMONGO_AVAILABLE:
                try:
                    # 構建 MongoDB 連接字串
                    db_account = os.environ['DB_ACCOUNT']
                    db_password = os.environ['DB_PASSWORD']
                    db_uri = os.environ['DB_URI']
                    db_name = os.environ['DB_NAME']
                    
                    encoded_username = quote_plus(db_account)
                    encoded_password = quote_plus(db_password)
                    mongo_uri = f"mongodb://{encoded_username}:{encoded_password}@{db_uri}"
                    
                    # 連接資料庫
                    self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
                    self.db = self.client[db_name]
                    
                    # 測試連接
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
        """執行 Token 清理"""
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
            
            # 如果有資料庫連接，執行資料庫清理
            if self.db is not None:
                try:
                    # 清理過期的 blacklist 記錄
                    collection = self.db["blacklist"]
                    
                    # 刪除過期的記錄
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
            
            # 計算記憶體節省（預估）
            memory_saved = self._calculate_memory_saved(cleaned_count)
            
            result = {
                "success": True,
                "cleaned_count": cleaned_count,
                "remaining_tokens": 0,  # 需要根據實際實現來獲取
                "estimated_memory_usage": 0,
                "memory_saved_bytes": memory_saved,
                "memory_saved_mb": round(memory_saved / (1024 * 1024), 2),
                "timestamp": datetime.now().isoformat(),
                "execution_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "message": f"清理完成，共清理 {cleaned_count} 個過期 token"
            }
            
            # 記錄清理結果
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
        """計算節省的記憶體（預估）"""
        # 假設每個 token 平均佔用 500 bytes
        avg_token_size = 500
        return cleaned_count * avg_token_size
    
    def _log_cleanup_result(self, result: Dict[str, Any]):
        """記錄清理結果"""
        if result["success"]:
            print(f"✅ 清理完成：")
            print(f"   - 清理了 {result['cleaned_count']} 個過期 token")
            print(f"   - 預估節省記憶體：{result['memory_saved_mb']} MB")
            print(f"   - 執行時間：{result['execution_time']}")
        else:
            print(f"❌ 清理失敗：{result.get('error', '未知錯誤')}")
    
    def __del__(self):
        """清理資源"""
        if self.client:
            try:
                self.client.close()
            except:
                pass

# 全域清理器實例
token_cleaner = TokenCleaner()

def cleanup_tokens() -> Dict[str, Any]:
    """
    清理過期 Token 的主要函數
    
    Returns:
        Dict[str, Any]: 清理結果
    """
    return token_cleaner.cleanup_tokens()

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Function Compute 主要處理函數
    
    Args:
        event: 事件對象，包含觸發資訊
        context: 上下文對象
    
    Returns:
        API Gateway 回應格式
    """
    print("🧹 JWT Token 清理 Function 開始執行")
    print(f"📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 執行清理
        result = cleanup_tokens()
        
        # 準備回應
        if result["success"]:
            response_body = {
                "status": "success",
                "message": f"成功清理 {result['cleaned_count']} 個過期 token",
                "data": result
            }
            status_code = 200
        else:
            response_body = {
                "status": "error",
                "message": "清理過程發生錯誤",
                "error": result.get("error", "未知錯誤"),
                "data": result
            }
            status_code = 500
        
        print(f"📊 清理結果: {result}")
        
        return {
            'statusCode': status_code,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': json.dumps(response_body, ensure_ascii=False, indent=2)
        }
        
    except Exception as e:
        print(f"❌ 函數執行失敗: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json; charset=utf-8',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'error',
                'message': '函數執行失敗',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }, ensure_ascii=False, indent=2)
        }

if __name__ == "__main__":
    """本地測試用"""
    print("🧹 JWT Token 清理器測試")
    print("=" * 50)
    
    # 檢查環境變數
    if not os.environ.get('JWT_SECRET_KEY'):
        print("❌ 錯誤：缺少 JWT_SECRET_KEY 環境變數")
        print("📝 請設定 JWT_SECRET_KEY 環境變數後再執行")
        sys.exit(1)
    
    # 執行清理
    result = cleanup_tokens()
    
    print("\n📊 測試結果:")
    print(json.dumps(result, ensure_ascii=False, indent=2)) 