from flask import Blueprint, request, jsonify, current_app
from jwt_auth_middleware import verify_token, create_access_token, revoke_token
from database.user_role_mapping_model import UserRoleMappingModel
from database.user_model import UserModel

auth_bp = Blueprint('auth', __name__)
user_role_model = UserRoleMappingModel()
user_model = UserModel()

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    使用者註冊端點
    """
    try:
        data = request.json
        
        # 驗證必要欄位
        if not data or not data.get("email") or not data.get("password"):
            return jsonify({"msg": "Email and password are required"}), 400
        
        email = data.get("email")
        password = data.get("password")
        username = data.get("username")  # 可選
        
        # 基本驗證
        if not email or "@" not in email:
            return jsonify({"msg": "Invalid email format"}), 400
        
        if len(password) < 6:
            return jsonify({"msg": "Password must be at least 6 characters long"}), 400
        
        # 註冊使用者
        user_id = user_model.register_user(email, password, username)
        
        if user_id:
            # 確保使用者角色存在（預設為 user 角色）
            user_role_model.ensure_user_role_exists(email, email, "user")
            
            return jsonify({
                "message": "User registered successfully",
                "user_id": user_id,
                "email": email
            }), 201
        else:
            return jsonify({"msg": "Email already exists or registration failed"}), 400
            
    except Exception as e:
        print(f"❌ 註冊功能發生錯誤: {str(e)}")
        return jsonify({
            "msg": f"Registration failed: {str(e)}",
            "error": "Internal server error"
        }), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    登入端點 - 使用真正的密碼驗證
    """
    data = request.json
    
    # 驗證必要欄位
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"msg": "Email and password are required"}), 400
    
    email = data.get("email")
    password = data.get("password")
    
    # 使用 UserModel 進行密碼驗證
    user = user_model.authenticate_user(email, password)
    
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401
    
    # 確保使用者角色存在
    user_role_model.ensure_user_role_exists(email, email, "user")
    
    # 建立 token 時包含使用者資訊
    token_data = {
        "sub": user["email"], 
        "email": user["email"],
        "user_id": user["id"]
    }
    
    # 使用 create_access_token 函數建立 token
    token = create_access_token(token_data)
    
    return jsonify({
        "access_token": token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"]
        }
    })

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """
    登出端點 - 支援 token 撤銷
    """
    # 從 Authorization header 取得 token
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"message": "No valid token provided"}), 400
    
    token = auth_header.split(" ")[1]
    
    # 使用 revoke_token 函數撤銷 token
    revoke_token(token)
    
    return jsonify({
        "message": "Logout successful",
        "note": "Token has been revoked and can no longer be used"
    }), 200

@auth_bp.route('/switch-account', methods=['POST'])
def switch_account():
    """
    帳戶切換端點
    直接登入新帳戶，返回新的 token
    客戶端應該用新 token 替換舊 token
    """
    data = request.json
    
    # 驗證必要欄位
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"msg": "Email and password are required"}), 400
    
    email = data.get("email")
    password = data.get("password")
    
    # 使用 UserModel 進行密碼驗證
    user = user_model.authenticate_user(email, password)
    
    if not user:
        return jsonify({"msg": "Invalid credentials"}), 401

    # 確保使用者角色存在
    user_role_model.ensure_user_role_exists(email, email, "user")
    
    # 產生新帳戶的 token
    token_data = {
        "sub": user["email"], 
        "email": user["email"],
        "user_id": user["id"]
    }
    
    # 使用 create_access_token 函數建立 token
    new_token = create_access_token(token_data)
    
    return jsonify({
        "message": "Account switched successfully",
        "access_token": new_token,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"]
        },
        "note": "Please replace the old token with this new token"
    }), 200

@auth_bp.route('/profile', methods=['GET'])
def get_profile():
    """
    取得使用者資料 - 需要有效的 JWT token
    """
    try:
        # 從 Authorization header 取得 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"message": "No valid token provided"}), 400
        
        token = auth_header.split(" ")[1]
        
        # 使用 verify_token 函數驗證 token
        payload = verify_token(token)
        
        # 從 token 中取得使用者 email
        email = payload.get("email")
        if not email:
            return jsonify({"message": "Invalid token: email not found"}), 400
        
        # 取得使用者資料
        user = user_model.get_user_by_email(email)
        if not user:
            return jsonify({"message": "User not found"}), 404
        
        # 取得使用者角色資訊
        user_role = user_role_model.get_user_role(email)
        user_permissions = user_role_model.get_user_permissions(email)
        
        # 組合完整的使用者資料
        profile_data = {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "role_name": user_role.get("role_name", "user") if user_role else "user",
            "is_active": user["is_active"],
            "created_at": user["created_at"],
            "last_login": user["last_login"],
            "permissions": user_permissions
        }
        
        return jsonify({
            "message": "Profile retrieved successfully",
            "profile": profile_data
        }), 200
        
    except Exception as e:
        print(f"❌ 取得使用者資料時發生錯誤: {str(e)}")
        return jsonify({
            "message": "Failed to get user profile",
            "error": str(e)
        }), 500

@auth_bp.route('/profile', methods=['PUT'])
def update_profile():
    """
    更新使用者資料 - 需要有效的 JWT token
    """
    try:
        # 從 Authorization header 取得 token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"message": "No valid token provided"}), 400
        
        token = auth_header.split(" ")[1]
        
        # 驗證 JWT token
        payload = verify_token(token)
        
        # 從 token 中取得使用者 email
        email = payload.get("email")
        if not email:
            return jsonify({"message": "Invalid token: email not found"}), 400
        
        # 取得要更新的資料
        data = request.json
        if not data:
            return jsonify({"message": "No update data provided"}), 400
        
        # 只允許更新特定欄位
        allowed_fields = ["username"]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}
        
        if not update_data:
            return jsonify({"message": "No valid fields to update"}), 400
        
        # 更新使用者資料
        success = user_model.update_user_profile(email, update_data)
        
        if success:
            # 重新取得更新後的使用者資料
            user = user_model.get_user_by_email(email)
            user_role = user_role_model.get_user_role(email)
            user_permissions = user_role_model.get_user_permissions(email)
            
            profile_data = {
                "id": user["id"],
                "email": user["email"],
                "username": user["username"],
                "role_name": user_role.get("role_name", "user") if user_role else "user",
                "is_active": user["is_active"],
                "created_at": user["created_at"],
                "last_login": user["last_login"],
                "permissions": user_permissions
            }
            
            return jsonify({
                "message": "Profile updated successfully",
                "profile": profile_data
            }), 200
        else:
            return jsonify({"message": "Failed to update profile"}), 400
            
    except Exception as e:
        return jsonify({"message": f"Failed to update profile: {str(e)}"}), 401

@auth_bp.route('/change-password', methods=['POST'])
def change_password():
    """
    變更密碼端點
    """
    data = request.json
    
    if not data or not data.get("email") or not data.get("old_password") or not data.get("new_password"):
        return jsonify({"msg": "Email, old password, and new password are required"}), 400
    
    email = data.get("email")
    old_password = data.get("old_password")
    new_password = data.get("new_password")
    
    if len(new_password) < 6:
        return jsonify({"msg": "New password must be at least 6 characters long"}), 400
    
    success = user_model.change_password(email, old_password, new_password)
    
    if success:
        return jsonify({"message": "Password changed successfully"}), 200
    else:
        return jsonify({"msg": "Invalid old password or user not found"}), 400

@auth_bp.route('/admin/cleanup-tokens', methods=['POST'])
def cleanup_tokens():
    """
    管理員端點：清理過期的 token
    """
    try:
        # 注意：新版本的 JWT Manager 不支援自動清理功能
        # 過期的 token 會自動失效，無需手動清理
        return jsonify({
            "message": "Token cleanup not required in current version",
            "note": "Expired tokens automatically become invalid"
        }), 200
        
    except Exception as e:
        print(f"❌ 清理 token 時發生錯誤: {str(e)}")
        return jsonify({
            "message": "Failed to cleanup tokens",
            "error": str(e)
        }), 500

@auth_bp.route('/admin/blacklist-stats', methods=['GET'])
def blacklist_stats():
    """
    管理員端點：取得黑名單統計資訊
    """
    try:
        # 注意：新版本的 JWT Manager 不支援黑名單統計功能
        # JWT token 的驗證是基於簽名和過期時間，無需黑名單
        return jsonify({
            "message": "Blacklist stats not available in current version",
            "note": "JWT tokens are validated by signature and expiration time"
        }), 200
        
    except Exception as e:
        print(f"❌ 取得黑名單統計時發生錯誤: {str(e)}")
        return jsonify({
            "message": "Failed to get blacklist stats",
            "error": str(e)
        }), 500

@auth_bp.route('/admin/users', methods=['GET'])
def get_users():
    """
    管理員端點：取得所有活躍使用者
    """
    try:
        users = user_model.get_all_active_users()
        return jsonify({
            "users": users,
            "total_users": len(users)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/admin/users/<user_id>/roles', methods=['PUT'])
def update_user_roles(user_id):
    """
    管理員端點：更新使用者角色
    """
    try:
        data = request.json
        role_name = data.get('role_name')
        
        if not role_name:
            return jsonify({"error": "role_name is required"}), 400
        
        success = user_role_model.update_user_role(user_id, role_name)
        
        if success:
            return jsonify({"message": "User role updated successfully"}), 200
        else:
            return jsonify({"error": "Failed to update user role"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/admin/users/<email>/deactivate', methods=['POST'])
def deactivate_user(email):
    """
    管理員端點：停用使用者
    """
    try:
        success = user_model.deactivate_user(email)
        
        if success:
            return jsonify({"message": "User deactivated successfully"}), 200
        else:
            return jsonify({"error": "Failed to deactivate user"}), 400
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500
