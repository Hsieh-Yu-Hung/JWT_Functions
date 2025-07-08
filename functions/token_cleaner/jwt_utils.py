"""
JWT Utilities for Token Cleaner Service

獨立於主專案的 JWT 業務邏輯函數，供 token_cleaner 容器使用。
"""

import jwt
import requests
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import os

def _get_jwt_config():
    """獲取 JWT 配置"""
    secret_key = os.environ.get('JWT_SECRET_KEY')
    if not secret_key:
        raise RuntimeError("JWT_SECRET_KEY 環境變數未設定")
    
    # 從環境變數獲取配置
    config_file = os.environ.get('CONFIG_FILE', 'config.yaml')
    mongodb_api_url = os.environ.get('MONGODB_API_URL')
    blacklist_collection = os.environ.get('BLACKLIST_COLLECTION', 'jwt_blacklist')
    
    return {
        'secret_key': secret_key,
        'config_file': config_file,
        'mongodb_api_url': mongodb_api_url,
        'blacklist_collection': blacklist_collection,
        'enable_blacklist': bool(mongodb_api_url)
    }

def _get_blacklist_manager():
    """獲取黑名單管理器實例"""
    config = _get_jwt_config()
    if not config['enable_blacklist']:
        return None
    
    return BlacklistManager(config)

class BlacklistManager:
    """JWT 黑名單管理器 - 獨立版本"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mongodb_api_url = config['mongodb_api_url'].rstrip('/')
        self.collection_name = config['blacklist_collection']
    
    def _hash_token(self, token: str) -> str:
        """對 token 進行雜湊處理"""
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _get_token_expiration(self, token: str) -> Optional[datetime]:
        """取得 token 的過期時間"""
        try:
            payload = jwt.decode(token, self.config['secret_key'], 
                               algorithms=['HS256'])
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
        except Exception:
            pass
        return None
    
    def add_to_blacklist(self, token: str, reason: str = "revoked") -> bool:
        """將 token 加入黑名單"""
        try:
            token_hash = self._hash_token(token)
            expiration = self._get_token_expiration(token)
            
            document = {
                "token_hash": token_hash,
                "reason": reason,
                "revoked_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": expiration.isoformat() if expiration else None
            }
            
            response = requests.post(
                f"{self.mongodb_api_url}/add/document/{self.collection_name}",
                json={"data": document},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("status") == "ok"
            else:
                print(f"加入黑名單失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"加入黑名單時發生錯誤: {str(e)}")
            return False
    
    def is_blacklisted(self, token: str) -> bool:
        """檢查 token 是否在黑名單中"""
        try:
            token_hash = self._hash_token(token)
            
            response = requests.get(
                f"{self.mongodb_api_url}/search/documents/{self.collection_name}",
                params={"token_hash": token_hash},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return len(result.get("data", [])) > 0
            else:
                print(f"查詢黑名單失敗: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"查詢黑名單時發生錯誤: {str(e)}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """清理已過期的黑名單 tokens"""
        try:
            now = datetime.now(timezone.utc)
            
            query_data = {
                "query": {
                    "expires_at": {
                        "$lt": now.isoformat()
                    }
                }
            }
            
            response = requests.delete(
                f"{self.mongodb_api_url}/delete/documents/{self.collection_name}",
                json=query_data,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("deleted_count", 0)
            else:
                print(f"清理過期 tokens 失敗: {response.status_code} - {response.text}")
                return 0
                
        except Exception as e:
            print(f"清理過期 tokens 時發生錯誤: {str(e)}")
            return 0
    
    def get_blacklist_stats(self) -> Dict[str, Any]:
        """取得黑名單統計資訊"""
        try:
            # 取得總數
            total_response = requests.get(
                f"{self.mongodb_api_url}/search/documents/{self.collection_name}/count",
                timeout=10
            )
            
            total_count = 0
            if total_response.status_code == 200:
                result = total_response.json()
                total_count = result.get("count", 0)
            
            # 取得過期數量
            now = datetime.now(timezone.utc)
            expired_response = requests.get(
                f"{self.mongodb_api_url}/search/documents/{self.collection_name}/count",
                params={
                    "expires_at": f"$lt:{now.isoformat()}"
                },
                timeout=10
            )
            
            expired_count = 0
            if expired_response.status_code == 200:
                result = expired_response.json()
                expired_count = result.get("count", 0)
            
            return {
                "total_tokens": total_count,
                "expired_tokens": expired_count,
                "active_tokens": total_count - expired_count
            }
            
        except Exception as e:
            print(f"取得黑名單統計時發生錯誤: {str(e)}")
            return {
                "total_tokens": 0,
                "expired_tokens": 0,
                "active_tokens": 0
            }

def cleanup_expired_blacklist_tokens() -> int:
    """清理已過期的黑名單 tokens"""
    try:
        blacklist_manager = _get_blacklist_manager()
        if blacklist_manager:
            return blacklist_manager.cleanup_expired_tokens()
    except Exception as e:
        print(f"清理過期 tokens 時發生錯誤: {str(e)}")
    return 0

def get_blacklist_statistics() -> Dict[str, Any]:
    """取得黑名單統計資訊"""
    try:
        blacklist_manager = _get_blacklist_manager()
        if blacklist_manager:
            return blacklist_manager.get_blacklist_stats()
    except Exception as e:
        print(f"取得黑名單統計時發生錯誤: {str(e)}")
    return {"total_tokens": 0, "expired_tokens": 0, "active_tokens": 0} 