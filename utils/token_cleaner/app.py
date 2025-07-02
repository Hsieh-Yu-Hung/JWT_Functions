#!/usr/bin/env python3
"""
JWT Token 清理 Flask 應用

適用於阿里雲 Function Compute 的 HTTP 服務
提供 JWT Token 清理的 REST API 端點
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime
import logging
from cleanup_function import cleanup_tokens
import os

# 設定日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 創建 Flask 應用
app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def cleanup_route():
    logger.info("🧹 JWT Token 清理 Function 開始執行")
    logger.info(f"📅 執行時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        result = cleanup_tokens()
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
        logger.info(f"📊 清理結果: {result}")
        return jsonify(response_body), status_code
    except Exception as e:
        logger.error(f"❌ 函數執行失敗: {e}")
        return jsonify({
            'status': 'error',
            'message': '函數執行失敗',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "JWT Token Cleaner"
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 9000))
    app.run(host='0.0.0.0', port=port, debug=False) 