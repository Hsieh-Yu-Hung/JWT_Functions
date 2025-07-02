from datetime import datetime, UTC
from database.base_model import BaseModel
from core.config import MONGODB_BLACKLIST_COLLECTION
import logging

logger = logging.getLogger(__name__)

class BlacklistModel(BaseModel):
    def __init__(self):
        super().__init__(MONGODB_BLACKLIST_COLLECTION)
    
    def _create_indexes(self):
        """建立索引以提升查詢效能"""
        try:
            # 確保 collection 已初始化
            if self.collection is None:
                from database.database import db_manager
                self.collection = db_manager.get_collection(self.collection_name)
                self._initialized = True
            
            # 為 token 建立唯一索引
            self.create_index("token", unique=True)
            # 為 expires_at 建立 TTL 索引（自動清理過期 token）
            self.create_index("expires_at", expire_after_seconds=0)
            # 為 user_id 建立索引
            self.create_index("user_id")
            # 為 revoked_at 建立索引
            self.create_index("revoked_at")
            
        except Exception as e:
            logger.error(f"❌ Blacklist 索引建立失敗: {e}")
    
    def add_to_blacklist(self, token: str, user_id: str, expires_at: datetime, reason: str = "logout"):
        """將 token 加入黑名單"""
        try:
            blacklist_entry = {
                "token": token,
                "user_id": user_id,
                "revoked_at": datetime.now(UTC),
                "expires_at": expires_at,
                "reason": reason,
                "created_at": datetime.now(UTC)
            }
            
            result_id = self.insert_one(blacklist_entry)
            if result_id:
                self._log_success(f"Token 已加入黑名單: {user_id}")
                return result_id
            else:
                raise Exception("插入失敗")
            
        except Exception as e:
            self._log_error("加入黑名單失敗", e)
            raise
    
    def is_blacklisted(self, token: str) -> bool:
        """檢查 token 是否在黑名單中"""
        try:
            return self.exists({"token": token})
        except Exception as e:
            self._log_error("檢查黑名單失敗", e)
            return False
    
    def get_blacklist_stats(self):
        """取得黑名單統計資訊"""
        try:
            total_tokens = self.count_documents()
            active_tokens = self.count_documents({
                "expires_at": {"$gt": datetime.now(UTC)}
            })
            
            return {
                "total_tokens": total_tokens,
                "active_tokens": active_tokens,
                "expired_tokens": total_tokens - active_tokens
            }
        except Exception as e:
            self._log_error("取得黑名單統計失敗", e)
            return {"total_tokens": 0, "active_tokens": 0, "expired_tokens": 0}
    
    def cleanup_expired_tokens(self):
        """清理已過期的 token（MongoDB TTL 索引會自動處理）"""
        try:
            # 手動清理（作為備用方案）
            cleaned_count = self.delete_many({
                "expires_at": {"$lt": datetime.now(UTC)}
            })
            
            if cleaned_count > 0:
                self._log_success(f"清理了 {cleaned_count} 個過期 token")
            
            return cleaned_count
        except Exception as e:
            self._log_error("清理過期 token 失敗", e)
            return 0
    
    def get_user_blacklisted_tokens(self, user_id: str):
        """取得使用者的所有黑名單 token"""
        try:
            tokens = self.find_many(
                filter_dict={"user_id": user_id},
                projection={"token": 1, "revoked_at": 1, "reason": 1, "_id": 0}
            )
            return tokens
        except Exception as e:
            self._log_error("取得使用者黑名單失敗", e)
            return [] 