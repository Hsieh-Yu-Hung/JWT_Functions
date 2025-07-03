from datetime import datetime, UTC
import logging
from database.api_manager import api_manager

logger = logging.getLogger(__name__)

class BlacklistModel:
    """使用 API 的黑名單模型"""
    
    def __init__(self):
        self.api = api_manager
    
    def _log_success(self, message: str):
        """記錄成功訊息"""
        logger.info(f"✅ {message}")
        print(f"✅ {message}")
    
    def _log_warning(self, message: str):
        """記錄警告訊息"""
        logger.warning(f"⚠️ {message}")
        print(f"⚠️ {message}")
    
    def _log_error(self, message: str, error: Exception = None):
        """記錄錯誤訊息"""
        if error:
            logger.error(f"❌ {message}: {error}")
            print(f"❌ {message}: {error}")
        else:
            logger.error(f"❌ {message}")
            print(f"❌ {message}")
    
    def add_to_blacklist(self, token: str, user_id: str, expires_at: datetime, reason: str = "logout"):
        """將 token 加入黑名單"""
        try:
            blacklist_entry = {
                "token": token,
                "user_id": user_id,
                "revoked_at": datetime.now(UTC).isoformat(),
                "expires_at": expires_at.isoformat(),
                "reason": reason,
                "created_at": datetime.now(UTC).isoformat()
            }
            
            result = self.api.add_to_blacklist(token, expires_at.isoformat())
            if result.get("success"):
                self._log_success(f"Token 已加入黑名單: {user_id}")
                return result.get("data", {}).get("id")
            else:
                raise Exception(f"加入黑名單失敗: {result.get('message', '未知錯誤')}")
            
        except Exception as e:
            self._log_error("加入黑名單失敗", e)
            raise
    
    def is_blacklisted(self, token: str) -> bool:
        """檢查 token 是否在黑名單中"""
        try:
            result = self.api.is_token_blacklisted(token)
            return result.get("success") and result.get("data", {}).get("is_blacklisted", False)
        except Exception as e:
            self._log_error("檢查黑名單失敗", e)
            return False
    
    def get_blacklist_stats(self):
        """取得黑名單統計資訊"""
        try:
            result = self.api.get_blacklist_stats()
            if result.get("success"):
                return result.get("data", {})
            else:
                self._log_error(f"取得黑名單統計失敗: {result.get('message', '未知錯誤')}")
                return {"total_tokens": 0, "active_tokens": 0, "expired_tokens": 0}
        except Exception as e:
            self._log_error("取得黑名單統計失敗", e)
            return {"total_tokens": 0, "active_tokens": 0, "expired_tokens": 0}
    
    def cleanup_expired_tokens(self):
        """清理已過期的 token"""
        try:
            result = self.api.cleanup_expired_tokens()
            if result.get("success"):
                cleaned_count = result.get("data", {}).get("cleaned_count", 0)
                if cleaned_count > 0:
                    self._log_success(f"清理了 {cleaned_count} 個過期 token")
                return cleaned_count
            else:
                self._log_error(f"清理過期 token 失敗: {result.get('message', '未知錯誤')}")
                return 0
        except Exception as e:
            self._log_error("清理過期 token 失敗", e)
            return 0
    
    def get_user_blacklisted_tokens(self, user_id: str):
        """取得使用者的所有黑名單 token"""
        try:
            # 注意：這個功能可能需要 API 端點支援
            # 如果 API 沒有提供這個端點，可以透過其他方式實現
            result = self.api.get_blacklist_stats()  # 暫時使用統計端點
            if result.get("success"):
                # 這裡需要根據實際的 API 回應格式調整
                return []
            else:
                self._log_error(f"取得使用者黑名單失敗: {result.get('message', '未知錯誤')}")
                return []
        except Exception as e:
            self._log_error("取得使用者黑名單失敗", e)
            return []
    
    def remove_from_blacklist(self, token: str):
        """從黑名單中移除 token"""
        try:
            result = self.api.remove_from_blacklist(token)
            if result.get("success"):
                self._log_success(f"Token 已從黑名單移除")
                return True
            else:
                self._log_error(f"移除黑名單失敗: {result.get('message', '未知錯誤')}")
                return False
        except Exception as e:
            self._log_error("移除黑名單失敗", e)
            return False 