"""
JWT Token 清理 Flask 應用

適用於阿里雲 Function Compute 的 HTTP 服務
提供 JWT Token 清理的 REST API 端點
使用 jwt_auth_middleware 套件進行清理操作
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
    
    # 檢查環境變數
    if not os.environ.get('JWT_SECRET_KEY'):
        error_msg = "缺少 JWT_SECRET_KEY 環境變數"
        logger.error(f"❌ {error_msg}")
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'timestamp': datetime.now().isoformat()
        }), 400
    
    try:
        result = cleanup_tokens()
        if result["success"]:
            response_body = {
                "status": "success",
                "message": f"成功清理 {result['cleaned_count']} 個過期 token",
                "data": result,
                "method": result.get("method", "unknown")
            }
            status_code = 200
            logger.info(f"✅ 清理成功: {result['cleaned_count']} 個 token")
        else:
            response_body = {
                "status": "error",
                "message": "清理過程發生錯誤",
                "error": result.get("error", "未知錯誤"),
                "data": result
            }
            status_code = 500
            logger.error(f"❌ 清理失敗: {result.get('error', '未知錯誤')}")
        
        logger.info(f"📊 清理結果: {result}")
        return jsonify(response_body), status_code
        
    except Exception as e:
        error_msg = f"函數執行失敗: {str(e)}"
        logger.error(f"❌ {error_msg}")
        return jsonify({
            'status': 'error',
            'message': error_msg,
            'timestamp': datetime.now().isoformat()
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """健康檢查端點"""
    print("🔍 健康檢查端點")
    try:
        # 檢查套件可用性
        package_status = "unknown"
        try:
            from jwt_utils import cleanup_expired_blacklist_tokens
            package_status = "available"
        except ImportError:
            package_status = "unavailable"
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "service": "JWT Token Cleaner",
            "package_status": package_status,
            "environment": {
                "jwt_secret_key_set": bool(os.environ.get('JWT_SECRET_KEY')),
                "config_file_set": bool(os.environ.get('CONFIG_FILE'))
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500

@app.route('/info', methods=['GET'])
def info():
    """服務資訊端點"""
    return jsonify({
        "service": "JWT Token Cleaner",
        "version": "2.0.0",
        "description": "使用 jwt_auth_middleware 套件的 JWT Token 清理服務",
        "features": [
            "自動清理過期的 JWT tokens",
            "支援 jwt_auth_middleware 套件",
            "備用 pymongo 方案",
            "詳細的統計資訊",
            "健康檢查端點"
        ],
        "endpoints": {
            "POST /": "執行 token 清理",
            "GET /health": "健康檢查",
            "GET /info": "服務資訊"
        },
        "environment_variables": {
            "required": ["JWT_SECRET_KEY"],
            "optional": ["MONGODB_API_URL", "BLACKLIST_COLLECTION"]
        },
        "timestamp": datetime.now().isoformat()
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 啟動 JWT Token Cleaner 服務，端口: {port}")
    app.run(host='0.0.0.0', port=port, debug=False) 