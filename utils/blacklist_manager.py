"""
JWT Blacklist Management for Main Project

使用 MongoDB API 管理被撤銷的 JWT tokens
Moved from JWT_Midware package to main project.
"""

import requests
import hashlib
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from .jwt_config import JWTConfig

class BlacklistManager:
    """JWT 黑名單管理器"""
    
    def __init__(self, 
                 jwt_config: JWTConfig,
                 collection_name: Optional[str] = None):
        """
        初始化黑名單管理器
        
        Args:
            jwt_config: JWT 配置實例（包含 MongoDB API URL 和黑名單配置）
            collection_name: 黑名單集合名稱（可選，預設使用配置中的值）
        """
        if not jwt_config:
            raise ValueError("JWT 配置實例是必要的")
        
        self.jwt_config = jwt_config
        self.mongodb_api_url = jwt_config.mongodb_api_url.rstrip('/')
        self.collection_name = collection_name or jwt_config.blacklist_collection
    
    def _hash_token(self, token: str) -> str:
        """
        對 token 進行雜湊處理以保護隱私
        
        Args:
            token: JWT token
            
        Returns:
            雜湊後的 token
        """
        return hashlib.sha256(token.encode()).hexdigest()
    
    def _get_token_expiration(self, token: str) -> Optional[datetime]:
        """
        取得 token 的過期時間
        
        Args:
            token: JWT token
            
        Returns:
            過期時間
        """
        try:
            import jwt
            payload = jwt.decode(token, self.jwt_config.secret_key, 
                               algorithms=[self.jwt_config.algorithm])
            exp_timestamp = payload.get("exp")
            if exp_timestamp:
                return datetime.fromtimestamp(exp_timestamp)
        except Exception:
            pass
        return None
    
    def add_to_blacklist(self, token: str, reason: str = "revoked") -> bool:
        """
        將 token 加入黑名單
        
        Args:
            token: 要加入黑名單的 JWT token
            reason: 撤銷原因
            
        Returns:
            是否成功加入黑名單
        """
        try:
            # 雜湊 token
            token_hash = self._hash_token(token)
            
            # 取得過期時間
            expiration = self._get_token_expiration(token)
            
            # 準備文件資料
            document = {
                "token_hash": token_hash,
                "reason": reason,
                "revoked_at": datetime.now(timezone.utc).isoformat(),
                "expires_at": expiration.isoformat() if expiration else None
            }
            
            # 呼叫 MongoDB API 插入文件
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
        """
        檢查 token 是否在黑名單中
        
        Args:
            token: 要檢查的 JWT token
            
        Returns:
            是否在黑名單中
        """
        try:
            # 雜湊 token
            token_hash = self._hash_token(token)
            
            # 呼叫 MongoDB API 查詢
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
    
    def remove_from_blacklist(self, token: str) -> bool:
        """
        從黑名單中移除 token
        
        Args:
            token: 要移除的 JWT token
            
        Returns:
            是否成功移除
        """
        try:
            # 雜湊 token
            token_hash = self._hash_token(token)
            
            # 先查詢文件 ID
            response = requests.get(
                f"{self.mongodb_api_url}/search/documents/{self.collection_name}",
                params={"token_hash": token_hash},
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                documents = result.get("data", [])
                if documents:
                    # 取得第一個文件的 ID
                    doc_id = documents[0].get("_id")
                    if doc_id:
                        # 刪除文件
                        delete_response = requests.delete(
                            f"{self.mongodb_api_url}/delete/document/{self.collection_name}/{doc_id}",
                            timeout=10
                        )
                        if delete_response.status_code == 200:
                            return True
            
            print(f"從黑名單移除失敗: token 不存在或刪除失敗")
            return False
                
        except Exception as e:
            print(f"從黑名單移除時發生錯誤: {str(e)}")
            return False
    
    def cleanup_expired_tokens(self) -> int:
        """
        清理已過期的黑名單 tokens
        
        Returns:
            清理的 token 數量
        """
        try:
            # 取得當前時間
            now = datetime.now(timezone.utc)
            
            # 準備查詢條件
            query_data = {
                "query": {
                    "expires_at": {
                        "$lt": now.isoformat()
                    }
                }
            }
            
            # 呼叫 MongoDB API 查詢過期 tokens
            response = requests.post(
                f"{self.mongodb_api_url}/search/documents/{self.collection_name}",
                json=query_data,
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                expired_tokens = result.get("data", [])
                
                # 刪除過期的 tokens
                deleted_count = 0
                for token_doc in expired_tokens:
                    doc_id = token_doc.get("_id")
                    if doc_id:
                        delete_response = requests.delete(
                            f"{self.mongodb_api_url}/delete/document/{self.collection_name}/{doc_id}",
                            timeout=10
                        )
                        if delete_response.status_code == 200:
                            deleted_count += 1
                
                print(f"清理了 {deleted_count} 個過期的黑名單 tokens")
                return deleted_count
            else:
                print(f"查詢過期 tokens 失敗: {response.status_code} - {response.text}")
                return 0
                
        except Exception as e:
            print(f"清理過期 tokens 時發生錯誤: {str(e)}")
            return 0
    
    def get_blacklist_stats(self) -> Dict[str, Any]:
        """
        取得黑名單統計資訊
        
        Returns:
            黑名單統計資訊
        """
        try:
            # 取得當前時間
            now = datetime.now(timezone.utc)
            
            # 查詢所有 tokens
            response = requests.get(
                f"{self.mongodb_api_url}/search/documents/{self.collection_name}",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                all_tokens = result.get("data", [])
                
                # 計算統計資訊
                total_count = len(all_tokens)
                expired_count = 0
                active_count = 0
                
                for token_doc in all_tokens:
                    expires_at = token_doc.get("expires_at")
                    if expires_at:
                        try:
                            expiration = datetime.fromisoformat(expires_at.replace('Z', '+00:00'))
                            if expiration < now:
                                expired_count += 1
                            else:
                                active_count += 1
                        except Exception:
                            # 如果無法解析日期，算作過期
                            expired_count += 1
                    else:
                        # 沒有過期時間的算作過期
                        expired_count += 1
                
                return {
                    "total": total_count,
                    "expired": expired_count,
                    "active": active_count
                }
            else:
                print(f"取得黑名單統計失敗: {response.status_code} - {response.text}")
                return {"total": 0, "expired": 0, "active": 0}
                
        except Exception as e:
            print(f"取得黑名單統計時發生錯誤: {str(e)}")
            return {"total": 0, "expired": 0, "active": 0} 