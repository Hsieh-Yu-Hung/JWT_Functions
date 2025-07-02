from datetime import datetime, UTC
from database.base_model import BaseModel
from core.config import MONGODB_USER_ROLE_COLLECTION
import logging

logger = logging.getLogger(__name__)

class UserRoleMappingModel(BaseModel):
    def __init__(self):
        super().__init__(MONGODB_USER_ROLE_COLLECTION)
    
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
            logger.error(f"❌ UserRole 索引建立失敗: {e}")
    
    def assign_role_to_user(self, user_id: str, email: str, role_name: str = "user"):
        """為使用者指派角色"""
        try:
            # 檢查角色是否存在
            from database.role_model import RoleModel
            role_model = RoleModel()
            role = role_model.get_role_by_name(role_name)
            if not role:
                raise Exception(f"角色 '{role_name}' 不存在")
            
            # 檢查使用者是否已有角色指派
            existing_user_role = self.find_one({"user_id": user_id})
            if existing_user_role:
                # 更新現有角色
                success = self.update_one(
                    {"user_id": user_id},
                    {
                        "role_name": role_name,
                        "updated_at": datetime.now(UTC)
                    }
                )
                if success:
                    self._log_success(f"使用者角色更新成功: {user_id} -> {role_name}")
                    return True
                else:
                    raise Exception("更新失敗")
            else:
                # 建立新的角色指派
                user_role_data = {
                    "user_id": user_id,
                    "email": email,
                    "role_name": role_name,
                    "is_active": True,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC)
                }
                
                result_id = self.insert_one(user_role_data)
                if result_id:
                    self._log_success(f"使用者角色指派成功: {user_id} -> {role_name}")
                    return True
                else:
                    raise Exception("插入失敗")
                    
        except Exception as e:
            self._log_error("指派使用者角色失敗", e)
            raise
    
    def get_user_role(self, user_id: str):
        """取得使用者的角色"""
        try:
            return self.find_one({"user_id": user_id, "is_active": True})
        except Exception as e:
            self._log_error("取得使用者角色失敗", e)
            return None
    
    def get_user_permissions(self, user_id: str):
        """取得使用者的所有權限（包含繼承權限）"""
        try:
            user_role = self.get_user_role(user_id)
            if not user_role:
                return []
            
            role_name = user_role.get("role_name")
            if not role_name:
                return []
            
            # 從角色模型取得權限
            from database.role_model import RoleModel
            role_model = RoleModel()
            return role_model.get_role_permissions(role_name, include_inherited=True)
            
        except Exception as e:
            self._log_error("取得使用者權限失敗", e)
            return []
    
    def check_user_permission(self, user_id: str, required_permission: str):
        """檢查使用者是否擁有特定權限"""
        try:
            permissions = self.get_user_permissions(user_id)
            return required_permission in permissions
        except Exception as e:
            self._log_error("檢查使用者權限失敗", e)
            return False
    
    def update_user_role(self, user_id: str, role_name: str):
        """更新使用者角色"""
        try:
            # 檢查角色是否存在
            from database.role_model import RoleModel
            role_model = RoleModel()
            role = role_model.get_role_by_name(role_name)
            if not role:
                raise Exception(f"角色 '{role_name}' 不存在")
            
            success = self.update_one(
                {"user_id": user_id},
                {
                    "role_name": role_name,
                    "updated_at": datetime.now(UTC)
                }
            )
            
            if success:
                self._log_success(f"使用者角色更新成功: {user_id} -> {role_name}")
                return True
            else:
                self._log_warning(f"更新使用者角色失敗（未找到記錄）: {user_id}")
                return False
                
        except Exception as e:
            self._log_error("更新使用者角色失敗", e)
            return False
    
    def deactivate_user(self, user_id: str):
        """停用使用者角色"""
        try:
            success = self.update_one(
                {"user_id": user_id},
                {"is_active": False, "updated_at": datetime.now(UTC)}
            )
            
            if success:
                self._log_success(f"使用者角色已停用: {user_id}")
                return True
            else:
                self._log_warning(f"停用使用者角色失敗（未找到記錄）: {user_id}")
                return False
                
        except Exception as e:
            self._log_error("停用使用者角色失敗", e)
            return False
    
    def activate_user(self, user_id: str):
        """啟用使用者角色"""
        try:
            success = self.update_one(
                {"user_id": user_id},
                {"is_active": True, "updated_at": datetime.now(UTC)}
            )
            
            if success:
                self._log_success(f"使用者角色已啟用: {user_id}")
                return True
            else:
                self._log_warning(f"啟用使用者角色失敗（未找到記錄）: {user_id}")
                return False
                
        except Exception as e:
            self._log_error("啟用使用者角色失敗", e)
            return False
    
    def get_all_active_users(self):
        """取得所有活躍使用者"""
        try:
            return self.find_many({"is_active": True})
        except Exception as e:
            self._log_error("取得活躍使用者失敗", e)
            return []
    
    def get_users_by_role(self, role_name: str):
        """取得擁有特定角色的所有使用者"""
        try:
            return self.find_many({"role_name": role_name, "is_active": True})
        except Exception as e:
            self._log_error("取得角色使用者失敗", e)
            return []
    
    def ensure_user_role_exists(self, user_id: str, email: str, default_role: str = "user"):
        """確保使用者角色存在，如果不存在則建立"""
        try:
            existing_user_role = self.get_user_role(user_id)
            if not existing_user_role:
                self.assign_role_to_user(user_id, email, default_role)
                return True
            return False
        except Exception as e:
            self._log_error("確保使用者角色存在失敗", e)
            return False
    
    def get_user_role_hierarchy(self, user_id: str):
        """取得使用者的完整角色層級結構"""
        try:
            user_role = self.get_user_role(user_id)
            if not user_role:
                return None
            
            role_name = user_role.get("role_name")
            if not role_name:
                return None
            
            # 從角色模型取得層級結構
            from database.role_model import RoleModel
            role_model = RoleModel()
            return role_model.get_role_hierarchy(role_name)
            
        except Exception as e:
            self._log_error("取得使用者角色層級結構失敗", e)
            return None 