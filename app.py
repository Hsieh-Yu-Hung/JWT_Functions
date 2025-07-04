from flask import Flask, request, jsonify
from jwt_auth_middleware import JWTConfig, set_jwt_config, token_required, revoke_token
from routes.auth_routes import auth_bp
from database.api_manager import api_manager
import json
from datetime import datetime
from flask_cors import CORS
import logging
import os
from dotenv import load_dotenv

# 配置日誌系統
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),  # 輸出到控制台
    ]
)

app = Flask(__name__)
app.register_blueprint(auth_bp)
CORS(app)

# 初始化 JWT 系統
def initialize_jwt_system():
    """初始化 JWT 系統"""
    # 載入 .env 檔案
    load_dotenv()
    
    # 從環境變數獲取密鑰
    secret_key = os.getenv('JWT_SECRET_KEY')
    if not secret_key:
        raise ValueError("錯誤：未在 .env 檔案中找到 JWT_SECRET_KEY 環境變數，請確保已正確設定")
    
    # 創建 JWT 配置，使用 config.yaml 檔案
    config = JWTConfig(
        secret_key=secret_key,
        config_file="config.yaml"  # 使用配置檔案
    )
    
    # 設定全域配置
    set_jwt_config(config)
    
    print(f"JWT 系統已初始化")
    print(f"演算法: {config.algorithm}")
    print(f"Access Token 過期時間: {config.access_token_expires} 分鐘")
    print(f"Refresh Token 過期時間: {config.refresh_token_expires} 分鐘")
    print(f"啟用黑名單: {config.enable_blacklist}")

# 初始化 JWT 系統
try:
    initialize_jwt_system()
except ValueError as e:
    print(f"❌ JWT 系統初始化失敗: {e}")
    print("💡 請確保 .env 檔案存在且包含 JWT_SECRET_KEY 變數")
    exit(1)
except Exception as e:
    print(f"❌ JWT 系統初始化時發生未知錯誤: {e}")
    exit(1)

@app.route('/protected')
@token_required
def protected(current_user):
    return {
        "message": f"Hello {current_user['sub']}, you have access!",
        "user_info": {
            "email": current_user.get('email'),
            "roles": current_user.get('roles', []),
            "permissions": current_user.get('permissions', [])
        }
    }

@app.route('/health')
def health():
    """健康檢查端點"""
    try:
        # 檢查 API 服務狀態
        api_health = api_manager.health_check()
        
        if api_health.get("success"):
            db_status = "connected"
            print("🗄️ API 服務連接正常")
        else:
            db_status = "disconnected"
            print(f"⚠️ API 服務連接失敗: {api_health.get('message', 'Unknown error')}")
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": "function-compute",
            "version": "1.0.0",
            "database": db_status,
            "jwt_middleware": "enabled",
            "api_status": api_health
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "environment": "function-compute"
        }), 500

@app.route('/admin/stats')
@token_required
def admin_stats(current_user):
    """管理員統計資訊端點"""
    # 檢查是否為管理員
    if 'admin' not in current_user.get('roles', []):
        return {"error": "Admin access required"}, 403
    
    from database.role_model import RoleModel
    
    role_model = RoleModel()
    active_users = role_model.get_all_active_users()
    
    return {
        "system_stats": {
            "active_users_count": len(active_users),
            "total_users": len(active_users)
        },
        "user_info": {
            "current_user": current_user['sub'],
            "roles": current_user.get('roles', [])
        }
    }

# 新增 JWT 相關的管理端點
@app.route('/admin/jwt/blacklist', methods=['GET'])
@token_required
def get_blacklist(current_user):
    """獲取黑名單統計"""
    if 'admin' not in current_user.get('roles', []):
        return {"error": "Admin access required"}, 403
    
    try:
        return jsonify({
            "message": "Blacklist stats not available in current version",
            "note": "JWT tokens are validated by signature and expiration time",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/jwt/blacklist', methods=['POST'])
@token_required
def add_to_blacklist(current_user):
    """手動添加 token 到黑名單"""
    if 'admin' not in current_user.get('roles', []):
        return {"error": "Admin access required"}, 403
    
    try:
        data = request.get_json()
        token = data.get('token')
        if not token:
            return jsonify({"error": "Token is required"}), 400
        
        revoke_token(token)
        return jsonify({"message": "Token revoked successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/admin/jwt/cleanup', methods=['POST'])
@token_required
def cleanup_expired_tokens(current_user):
    """清理過期的 token"""
    if 'admin' not in current_user.get('roles', []):
        return {"error": "Admin access required"}, 403
    
    try:
        return jsonify({
            "message": "Token cleanup not required in current version",
            "note": "Expired tokens automatically become invalid",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def handler(event, context):
    """
    Function Compute 主要處理函數
    
    Args:
        event: 事件對象，包含 HTTP 請求資訊
        context: 上下文對象
    
    Returns:
        API Gateway 回應格式
    """
    try:
        # 解析事件中的 HTTP 請求資訊
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        headers = event.get('headers', {})
        query_string = event.get('queryStringParameters', {})
        body = event.get('body', '')
        
        # 處理請求體
        if body and headers.get('content-type', '').startswith('application/json'):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                body = {}
        
        # 建立 Flask 請求環境
        with app.test_request_context(
            path=path,
            method=http_method,
            headers=headers,
            query_string=query_string,
            json=body if isinstance(body, dict) else None,
            data=body if not isinstance(body, dict) else None
        ):
            # 執行 Flask 應用程式
            response = app.full_dispatch_request()
            
            # 轉換 Flask 回應為 Function Compute 格式
            return {
                'statusCode': response.status_code,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': response.get_data(as_text=True)
            }
    
    except Exception as e:
        # 錯誤處理
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            })
        }

def init_db():
    """初始化 API 服務連接"""
    print("🚀 嘗試初始化 API 服務連接...")
    try:
        # 嘗試連接 API 服務，但不強制要求成功
        api_health = api_manager.health_check()
        if api_health.get("success"):
            print("✅ API 服務連接初始化成功")
        else:
            print(f"⚠️ API 服務連接初始化失敗: {api_health.get('message', 'Unknown error')}")
            print("📝 這在本地測試環境是正常的，部署到 Function Compute 時會自動連接")
    except Exception as e:
        print(f"⚠️ API 服務連接初始化失敗: {e}")
        print("📝 這在本地測試環境是正常的，部署到 Function Compute 時會自動連接")

# 冷啟動時嘗試初始化資料庫（非阻塞）
try:
    init_db()
except Exception as e:
    print(f"⚠️ 初始化失敗.: {e}")
    print("📝 應用程式將繼續運行，資料庫將在需要時連接")

# 為 Function Compute 添加全局變數
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

if __name__ == '__main__':
    try:
        print("🚀 啟動 JWT 認證服務...")
        print("🔐 JWT Auth Middleware 已啟用")
        app.run(host='0.0.0.0', port=9000)
    except KeyboardInterrupt:
        print("\n🛑 正在停止服務...")
    finally:
        print("✅ 服務已停止")
