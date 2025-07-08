#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Function Compute 入口點檔案
"""

import sys
import os
import json
from datetime import datetime

# 添加應用程式路徑
sys.path.insert(0, '/app')

try:
    from app import handler, app
    print("✅ 成功導入 app 模組")
except ImportError as e:
    print(f"❌ 導入 app 模組失敗: {e}")
    # 如果導入失敗，提供一個基本的 handler
    def handler(event, context):
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Module import error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

# 導出 handler 函數供 Function Compute 調用
__all__ = ['handler']

# 如果直接執行此檔案，啟動 Flask 應用
if __name__ == '__main__':
    try:
        print("🚀 啟動 JWT 認證服務...")
        print("🔐 JWT Auth Middleware 已啟用")
        app.run(host='0.0.0.0', port=9000, debug=False, threaded=True)
    except Exception as e:
        print(f"❌ 啟動失敗: {e}")
        sys.exit(1) 