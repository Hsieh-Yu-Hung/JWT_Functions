#!/usr/bin/env python3
"""
JWT Token 清理測試腳本

測試 jwt_auth_middleware 套件和備用方案的清理功能
"""

import os
import sys
from datetime import datetime

def check_environment():
    """檢查環境變數和套件可用性"""
    print("🔍 環境檢查")
    print("=" * 30)
    
    # 檢查必要的環境變數
    required_vars = ['JWT_SECRET_KEY']
    missing_required = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_required:
        print(f"❌ 缺少必要環境變數: {', '.join(missing_required)}")
        return False
    
    print("✅ JWT_SECRET_KEY 已設定")
    
    # 檢查可選環境變數
    optional_vars = ['CONFIG_FILE']
    set_optional = [var for var in optional_vars if os.environ.get(var)]
    if set_optional:
        print(f"✅ 可選環境變數已設定: {', '.join(set_optional)}")
    else:
        print("📝 使用預設的可選環境變數")
    
    # 檢查套件可用性
    try:
        from jwt_auth_middleware import cleanup_expired_blacklist_tokens, get_blacklist_statistics
        print("✅ jwt_auth_middleware 套件可用")
        return True
    except ImportError as e:
        print(f"⚠️ jwt_auth_middleware 套件不可用: {e}")
        
        # 檢查備用方案
        try:
            from pymongo import MongoClient
            print("✅ pymongo 備用方案可用")
            
            # 檢查資料庫環境變數
            db_vars = ['DB_ACCOUNT', 'DB_PASSWORD', 'DB_URI', 'DB_NAME']
            missing_db_vars = [var for var in db_vars if not os.environ.get(var)]
            
            if missing_db_vars:
                print(f"⚠️ 缺少資料庫環境變數: {', '.join(missing_db_vars)}")
                print("📝 將使用模擬模式")
                return True
            else:
                print("✅ 資料庫環境變數已設定")
                return True
                
        except ImportError:
            print("❌ pymongo 備用方案也不可用")
            return False

def test_cleanup():
    """測試清理功能"""
    print("\n🧹 清理功能測試")
    print("=" * 30)
    
    try:
        from cleanup_function import cleanup_tokens
        result = cleanup_tokens()
        
        print(f"📊 清理結果:")
        print(f"   - 成功: {result.get('success', False)}")
        print(f"   - 清理數量: {result.get('cleaned_count', 0)}")
        print(f"   - 剩餘 token: {result.get('remaining_tokens', 0)}")
        print(f"   - 總 token 數: {result.get('total_tokens', 0)}")
        print(f"   - 過期 token 數: {result.get('expired_tokens', 0)}")
        print(f"   - 使用方法: {result.get('method', 'unknown')}")
        print(f"   - 節省記憶體: {result.get('memory_saved_mb', 0)} MB")
        
        return result
        
    except Exception as e:
        print(f"❌ 清理測試失敗: {e}")
        return {
            "success": False,
            "error": str(e),
            "cleaned_count": 0,
            "timestamp": datetime.now().isoformat()
        }

def main():
    """主測試函數"""
    print("🧹 JWT Token 清理器測試")
    print("=" * 50)
    print(f"📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 檢查環境
    if not check_environment():
        print("\n❌ 環境檢查失敗，無法繼續測試")
        sys.exit(1)
    
    # 執行清理測試
    result = test_cleanup()
    
    # 輸出詳細結果
    print("\n📊 詳細測試結果:")
    import json
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 總結
    if result.get("success"):
        print("\n✅ 測試完成")
        print(f"🎉 成功清理 {result.get('cleaned_count', 0)} 個過期 token")
    else:
        print(f"\n❌ 測試失敗: {result.get('error', '未知錯誤')}")
        sys.exit(1)

if __name__ == "__main__":
    main() 