from datetime import datetime, UTC
from database.base_model import BaseModel
from core.config import MONGODB_ROLE_COLLECTION
import logging

logger = logging.getLogger(__name__)

class RoleModel(BaseModel):
    def __init__(self):
        super().__init__(MONGODB_ROLE_COLLECTION)
    
    def _create_indexes(self):
        """建立索引"""
        try:
            # 確保 collection 已初始化
            if self.collection is None:
                from database.database import db_manager
                self.collection = db_manager.get_collection(self.collection_name)
                self._initialized = True
            
            # 為 user_id 建立唯一索引
            self.create_index("user_id", unique=True)
            # 為 email 建立索引
            self.create_index("email")
            # 為 is_active 建立索引
            self.create_index("is_active")
            
        except Exception as e:
            logger.error(f"❌ Role 索引建立失敗: {e}")
    
    def create_user_role(self, user_id: str, email: str, roles: list = None, permissions: list = None):
        """建立使用者角色"""
        try:
            user_role = {
                "user_id": user_id,
                "email": email,
                "roles": roles or ["user"],
                "permissions": permissions or ["read"],
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            }
            
            result_id = self.insert_one(user_role)
            if result_id:
                self._log_success(f"使用者角色建立成功: {user_id}")
                return result_id
            else:
                raise Exception("插入失敗")
            
        except Exception as e:
            self._log_error("建立使用者角色失敗", e)
            raise
    
    def get_user_roles(self, user_id: str):
        """取得使用者角色"""
        try:
            return self.find_one({"user_id": user_id, "is_active": True})
        except Exception as e:
            self._log_error("取得使用者角色失敗", e)
            return None
    
    def update_user_roles(self, user_id: str, roles: list = None, permissions: list = None):
        """更新使用者角色"""
        try:
            update_data = {"updated_at": datetime.now(UTC)}
            
            if roles is not None:
                update_data["roles"] = roles
            if permissions is not None:
                update_data["permissions"] = permissions
            
            success = self.update_one({"user_id": user_id}, update_data)
            
            if success:
                self._log_success(f"使用者角色更新成功: {user_id}")
                return True
            else:
                self._log_warning(f"使用者角色更新失敗（未找到記錄）: {user_id}")
                return False
                
        except Exception as e:
            self._log_error("更新使用者角色失敗", e)
            return False
    
    def deactivate_user(self, user_id: str):
        """停用使用者"""
        try:
            success = self.update_one(
                {"user_id": user_id},
                {"is_active": False, "updated_at": datetime.now(UTC)}
            )
            
            if success:
                self._log_success(f"使用者已停用: {user_id}")
                return True
            else:
                self._log_warning(f"停用使用者失敗（未找到記錄）: {user_id}")
                return False
                
        except Exception as e:
            self._log_error("停用使用者失敗", e)
            return False
    
    def check_user_permission(self, user_id: str, required_permission: str):
        """檢查使用者權限"""
        try:
            user_role = self.get_user_roles(user_id)
            if not user_role:
                return False
            
            return required_permission in user_role.get("permissions", [])
        except Exception as e:
            self._log_error("檢查使用者權限失敗", e)
            return False
    
    def get_all_active_users(self):
        """取得所有活躍使用者"""
        try:
            return self.find_many({"is_active": True})
        except Exception as e:
            self._log_error("取得活躍使用者失敗", e)
            return []
    
    def ensure_user_role_exists(self, user_id: str, email: str):
        """確保使用者角色存在，如果不存在則建立"""
        try:
            existing_role = self.get_user_roles(user_id)
            if not existing_role:
                self.create_user_role(user_id, email)
                return True
            return False
        except Exception as e:
            self._log_error("確保使用者角色存在失敗", e)
            return False 