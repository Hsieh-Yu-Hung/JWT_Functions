"""
JWT Utilities for Main Project

Provides JWT token creation and business logic functions.
Core JWT verification functions are provided by jwt_auth_middleware package.
"""

import jwt
import uuid
import requests
import hashlib
from datetime import datetime, timedelta, timezone
from typing import Dict, Any, Optional
from .jwt_config import JWTConfig
from .blacklist_manager import BlacklistManager

# 全域配置實例 - 延遲初始化
_jwt_config = None
_blacklist_manager = None

def _get_jwt_config() -> JWTConfig:
    """獲取 JWT 配置實例"""
    global _jwt_config
    if _jwt_config is None:
        raise RuntimeError(
            "JWT 配置未初始化。請先使用 set_jwt_config() 設定配置，"
            "或使用 create_jwt_config() 創建配置實例。"
            "範例：\n"
            "from utils.jwt_utils import create_jwt_config, set_jwt_config\n"
            "config = create_jwt_config(secret_key='your_secret_key', config_file='config.yaml')\n"
            "set_jwt_config(config)"
        )
    return _jwt_config

def _get_blacklist_manager() -> Optional[BlacklistManager]:
    """獲取黑名單管理器實例（延遲初始化）"""
    global _blacklist_manager
    if _blacklist_manager is None:
        config = _get_jwt_config()
        if config.enable_blacklist and config.mongodb_api_url:
            _blacklist_manager = BlacklistManager(
                jwt_config=config
            )
    return _blacklist_manager

def set_jwt_config(config: JWTConfig):
    """設置 JWT 配置（主要用於測試）"""
    global _jwt_config, _blacklist_manager
    _jwt_config = config
    _blacklist_manager = None  # 重置黑名單管理器

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """
    建立 JWT access token
    
    Args:
        data: 要編碼到 token 中的資料
        expires_delta: 自定義過期時間
        
    Returns:
        JWT token 字串
    """
    to_encode = data.copy()
    jwt_config = _get_jwt_config()
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=jwt_config.access_token_expires)
    
    to_encode.update({
        "exp": expire,
        "type": "access",  # 標記為 Access Token
        "iat": datetime.now(timezone.utc),  # 發行時間
        "jti": str(uuid.uuid4())  # JWT ID，確保每個 token 唯一
    })
    encoded_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)
    
    return encoded_jwt

def create_refresh_token(data: Dict[str, Any]) -> str:
    """
    建立 JWT refresh token
    
    Args:
        data: 要編碼到 token 中的資料
        
    Returns:
        JWT refresh token 字串
    """
    to_encode = data.copy()
    jwt_config = _get_jwt_config()
    expire = datetime.now(timezone.utc) + timedelta(minutes=jwt_config.refresh_token_expires)
    
    to_encode.update({
        "exp": expire,
        "type": "refresh",  # 標記為 Refresh Token
        "iat": datetime.now(timezone.utc),  # 發行時間
        "jti": str(uuid.uuid4())  # JWT ID，確保每個 token 唯一
    })
    encoded_jwt = jwt.encode(to_encode, jwt_config.secret_key, algorithm=jwt_config.algorithm)
    
    return encoded_jwt

def create_token_pair(data: Dict[str, Any]) -> Dict[str, str]:
    """
    建立 Access Token 和 Refresh Token 對
    
    Args:
        data: 要編碼到 token 中的資料
        
    Returns:
        包含 access_token 和 refresh_token 的字典
    """
    access_token = create_access_token(data)
    refresh_token = create_refresh_token(data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token
    }

def refresh_access_token(refresh_token: str) -> Optional[str]:
    """
    使用 Refresh Token 取得新的 Access Token
    
    Args:
        refresh_token: JWT refresh token 字串
        
    Returns:
        新的 JWT access token，如果無法重新整理則返回 None
    """
    try:
        # 使用套件提供的驗證功能
        from jwt_auth_middleware import verify_refresh_token
        payload = verify_refresh_token(refresh_token)
        
        # 建立新的 access token（不包含 type 和 jti）
        token_data = {k: v for k, v in payload.items() 
                     if k not in ['exp', 'iat', 'type', 'jti']}
        
        return create_access_token(token_data)
        
    except Exception as e:
        print(f"無法重新整理 token: {str(e)}")
        return None

def revoke_token(token: str, reason: str = "revoked") -> bool:
    """
    撤銷 JWT token（加入黑名單）
    
    Args:
        token: 要撤銷的 JWT token
        reason: 撤銷原因
        
    Returns:
        是否成功撤銷
    """
    try:
        blacklist_manager = _get_blacklist_manager()
        if blacklist_manager:
            return blacklist_manager.add_to_blacklist(token, reason)
        else:
            print("警告：黑名單功能未啟用，無法撤銷 token")
            return False
    except Exception as e:
        print(f"撤銷 token 時發生錯誤: {str(e)}")
        return False

def revoke_token_pair(access_token: str, refresh_token: str, reason: str = "user_logout") -> bool:
    """
    撤銷 token 對（access token 和 refresh token）
    
    Args:
        access_token: Access token
        refresh_token: Refresh token
        reason: 撤銷原因
        
    Returns:
        是否成功撤銷兩個 token
    """
    try:
        blacklist_manager = _get_blacklist_manager()
        if blacklist_manager:
            # 撤銷 access token
            access_revoked = blacklist_manager.add_to_blacklist(access_token, f"{reason}_access")
            # 撤銷 refresh token
            refresh_revoked = blacklist_manager.add_to_blacklist(refresh_token, f"{reason}_refresh")
            
            return access_revoked and refresh_revoked
        else:
            print("警告：黑名單功能未啟用，無法撤銷 token")
            return False
    except Exception as e:
        print(f"撤銷 token 對時發生錯誤: {str(e)}")
        return False

def get_token_expiration(token: str) -> Optional[datetime]:
    """
    取得 token 的過期時間
    
    Args:
        token: JWT token 字串
        
    Returns:
        過期時間，如果無法解析則返回 None
    """
    try:
        # 使用套件提供的驗證功能
        from jwt_auth_middleware import verify_token
        payload = verify_token(token)
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp)
    except Exception:
        pass
    return None

def is_token_expired(token: str) -> bool:
    """
    檢查 token 是否已過期
    
    Args:
        token: JWT token 字串
        
    Returns:
        是否已過期
    """
    try:
        # 使用套件提供的驗證功能
        from jwt_auth_middleware import verify_token
        payload = verify_token(token)
        exp_timestamp = payload.get("exp")
        if exp_timestamp:
            return datetime.fromtimestamp(exp_timestamp) < datetime.now(timezone.utc)
    except Exception:
        pass
    return True

def is_token_blacklisted(token: str) -> bool:
    """
    檢查 token 是否在黑名單中
    
    Args:
        token: JWT token 字串
        
    Returns:
        是否在黑名單中
    """
    try:
        blacklist_manager = _get_blacklist_manager()
        if blacklist_manager:
            return blacklist_manager.is_blacklisted(token)
    except Exception as e:
        print(f"檢查黑名單時發生錯誤: {str(e)}")
    return False

def remove_from_blacklist(token: str) -> bool:
    """
    從黑名單中移除 token
    
    Args:
        token: JWT token 字串
        
    Returns:
        是否成功移除
    """
    try:
        blacklist_manager = _get_blacklist_manager()
        if blacklist_manager:
            return blacklist_manager.remove_from_blacklist(token)
    except Exception as e:
        print(f"從黑名單移除時發生錯誤: {str(e)}")
    return False

def cleanup_expired_blacklist_tokens() -> int:
    """
    清理已過期的黑名單 tokens
    
    Returns:
        清理的 token 數量
    """
    try:
        blacklist_manager = _get_blacklist_manager()
        if blacklist_manager:
            return blacklist_manager.cleanup_expired_tokens()
    except Exception as e:
        print(f"清理過期 tokens 時發生錯誤: {str(e)}")
    return 0

def get_blacklist_statistics() -> Dict[str, Any]:
    """
    取得黑名單統計資訊
    
    Returns:
        黑名單統計資訊
    """
    try:
        blacklist_manager = _get_blacklist_manager()
        if blacklist_manager:
            return blacklist_manager.get_blacklist_stats()
    except Exception as e:
        print(f"取得黑名單統計時發生錯誤: {str(e)}")
    return {"total": 0, "expired": 0, "active": 0}

def initialize_blacklist_system(collection_name: str = None) -> bool:
    """
    初始化黑名單系統
    
    Args:
        collection_name: 集合名稱（可選）
        
    Returns:
        是否成功初始化
    """
    try:
        blacklist_manager = _get_blacklist_manager()
        if blacklist_manager:
            return True
        else:
            print("警告：黑名單功能未啟用")
            return False
    except Exception as e:
        print(f"初始化黑名單系統時發生錯誤: {str(e)}")
        return False 