#!/usr/bin/env python3
"""
簡化的 JWT Token 清理測試腳本
"""

import os
import sys
from datetime import datetime

# 檢查環境變數
if not os.environ.get('JWT_SECRET_KEY'):
    print("❌ 錯誤：缺少 JWT_SECRET_KEY 環境變數")
    print("📝 請設定 JWT_SECRET_KEY 環境變數後再執行")
    sys.exit(1)

print("🧹 JWT Token 清理器測試")
print("=" * 50)
print(f"📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 檢查資料庫環境變數
db_vars = ['DB_ACCOUNT', 'DB_PASSWORD', 'DB_URI', 'DB_NAME']
missing_vars = [var for var in db_vars if not os.environ.get(var)]

if missing_vars:
    print(f"⚠️ 缺少資料庫環境變數: {', '.join(missing_vars)}")
    print("📝 將跳過資料庫操作")
    
    # 模擬清理結果
    result = {
        "success": True,
        "cleaned_count": 0,
        "remaining_tokens": 0,
        "estimated_memory_usage": 0,
        "memory_saved_bytes": 0,
        "memory_saved_mb": 0,
        "timestamp": datetime.now().isoformat(),
        "execution_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        "message": "測試模式：資料庫不可用，跳過實際清理"
    }
else:
    print("✅ 所有環境變數已設定")
    
    try:
        # 嘗試執行實際的清理
        from cleanup_function import cleanup_tokens
        result = cleanup_tokens()
    except Exception as e:
        print(f"❌ 執行清理時發生錯誤: {e}")
        result = {
            "success": False,
            "error": str(e),
            "cleaned_count": 0,
            "timestamp": datetime.now().isoformat()
        }

print("\n📊 測試結果:")
import json
print(json.dumps(result, ensure_ascii=False, indent=2))

if result.get("success"):
    print("\n✅ 測試完成")
else:
    print(f"\n❌ 測試失敗: {result.get('error', '未知錯誤')}")
    sys.exit(1) 