import jwt
from datetime import datetime, timedelta, UTC
from core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from database.blacklist_model import BlacklistModel
from database.role_model import RoleModel
import logging

logger = logging.getLogger(__name__)

# 初始化模型
blacklist_model = BlacklistModel()
role_model = RoleModel()

def create_access_token(data: dict):
    """建立 JWT token"""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    # 確保使用者角色存在
    user_id = data.get('sub')
    email = data.get('email', user_id)
    if user_id:
        role_model.ensure_user_role_exists(user_id, email)
    
    logger.info(f"✅ Token 建立成功: {data.get('sub', 'unknown')}")
    print(f"✅ Token 建立成功: {data.get('sub', 'unknown')}")
    return token

def verify_token(token: str):
    """驗證 JWT token"""
    try:
        # 檢查 token 是否在黑名單中
        if blacklist_model.is_blacklisted(token):
            raise Exception("Token has been revoked")
        
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # 檢查使用者角色是否仍然有效
        user_roles = role_model.get_user_roles(payload.get('sub'))
        if not user_roles:
            raise Exception("User role not found or inactive")
        
        # 將角色資訊加入 payload
        payload['roles'] = user_roles.get('roles', [])
        payload['permissions'] = user_roles.get('permissions', [])
        
        return payload
        
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
    except Exception as e:
        logger.error(f"❌ Token 驗證失敗: {e}")
        raise

def revoke_token(token: str, user_id: str = None, reason: str = "logout"):
    """撤銷 token"""
    try:
        # 解碼 token 取得過期時間和使用者資訊
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expires_at = datetime.fromtimestamp(payload['exp'], UTC)
        user_id = user_id or payload.get('sub')
        
        # 加入黑名單
        blacklist_model.add_to_blacklist(token, user_id, expires_at, reason)
        
        logger.info(f"✅ Token 已撤銷: {user_id}")
        print(f"✅ Token 已撤銷: {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Token 撤銷失敗: {e}")
        print(f"❌ Token 撤銷失敗: {e}")
        return False

def is_token_revoked(token: str):
    """檢查 token 是否已被撤銷"""
    return blacklist_model.is_blacklisted(token)

def cleanup_expired_tokens():
    """清理已過期的 token"""
    return blacklist_model.cleanup_expired_tokens()

def get_blacklist_stats():
    """取得黑名單統計資訊"""
    return blacklist_model.get_blacklist_stats()
