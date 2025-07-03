from datetime import datetime, UTC
import logging
from database.api_manager import api_manager

logger = logging.getLogger(__name__)

class UserRoleMappingModel:
    """使用 API 的用戶角色映射模型"""
    
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
    
    def assign_role_to_user(self, user_id: str, email: str, role_name: str = "user"):
        """為使用者指派角色"""
        try:
            # 檢查角色是否存在
            from database.role_model import RoleModel
            role_model = RoleModel()
            role = role_model.get_role_by_name(role_name)
            if not role:
                raise Exception(f"角色 '{role_name}' 不存在")
            
            # 透過 API 指派角色
            result = self.api.assign_role_to_user(user_id, role["_id"])
            
            if result.get("success"):
                self._log_success(f"使用者角色指派成功: {user_id} -> {role_name}")
                return True
            else:
                raise Exception(f"指派角色失敗: {result.get('message', '未知錯誤')}")
                    
        except Exception as e:
            self._log_error("指派使用者角色失敗", e)
            raise
    
    def get_user_role(self, user_id: str):
        """取得使用者的角色"""
        try:
            result = self.api.get_user_role_mapping(user_id)
            if result.get("success") and result.get("data"):
                roles = result["data"]
                # 返回第一個活躍的角色映射
                for role_mapping in roles:
                    if role_mapping.get("is_active", False):
                        # 根據角色 ID 取得完整的角色資訊
                        role_id = role_mapping.get("role_id")
                        if role_id:
                            from database.role_model import RoleModel
                            role_model = RoleModel()
                            role = role_model.get_role_by_id(role_id)
                            if role:
                                return role
            return None
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
            
            # 先移除現有角色
            current_role = self.get_user_role(user_id)
            if current_role:
                self.api.remove_role_from_user(user_id, current_role["_id"])
            
            # 指派新角色
            result = self.api.assign_role_to_user(user_id, role["_id"])
            
            if result.get("success"):
                self._log_success(f"使用者角色更新成功: {user_id} -> {role_name}")
                return True
            else:
                raise Exception(f"更新角色失敗: {result.get('message', '未知錯誤')}")
                
        except Exception as e:
            self._log_error("更新使用者角色失敗", e)
            raise
    
    def deactivate_user(self, user_id: str):
        """停用使用者角色"""
        try:
            # 取得使用者的角色
            user_role = self.get_user_role(user_id)
            if not user_role:
                self._log_warning(f"使用者沒有角色: {user_id}")
                return False
            
            # 移除角色
            result = self.api.remove_role_from_user(user_id, user_role["_id"])
            
            if result.get("success"):
                self._log_success(f"使用者角色已停用: {user_id}")
                return True
            else:
                raise Exception(f"停用角色失敗: {result.get('message', '未知錯誤')}")
                
        except Exception as e:
            self._log_error("停用使用者角色失敗", e)
            raise
    
    def activate_user(self, user_id: str):
        """啟用使用者角色"""
        try:
            # 為使用者指派預設角色
            result = self.assign_role_to_user(user_id, "", "user")
            
            if result:
                self._log_success(f"使用者角色已啟用: {user_id}")
                return True
            else:
                raise Exception("啟用角色失敗")
                
        except Exception as e:
            self._log_error("啟用使用者角色失敗", e)
            raise
    
    def get_all_active_users(self):
        """取得所有活躍使用者"""
        try:
            # 這個功能需要透過用戶模型來實現
            from database.user_model import UserModel
            user_model = UserModel()
            return user_model.get_all_active_users()
        except Exception as e:
            self._log_error("取得活躍使用者失敗", e)
            return []
    
    def get_users_by_role(self, role_name: str):
        """取得擁有特定角色的所有使用者"""
        try:
            # 先取得角色 ID
            from database.role_model import RoleModel
            role_model = RoleModel()
            role = role_model.get_role_by_name(role_name)
            if not role:
                return []
            
            # 透過 API 取得角色的使用者
            result = self.api.get_role_users(role["_id"])
            if result.get("success"):
                return result.get("data", [])
            else:
                self._log_error(f"取得角色使用者失敗: {result.get('message', '未知錯誤')}")
                return []
        except Exception as e:
            self._log_error("取得角色使用者失敗", e)
            return []
    
    def ensure_user_role_exists(self, user_id: str, email: str, default_role: str = "user"):
        """確保使用者角色存在，如果不存在則建立"""
        try:
            user_role = self.get_user_role(user_id)
            if not user_role:
                # 使用者沒有角色，指派預設角色
                return self.assign_role_to_user(user_id, email, default_role)
            return True
        except Exception as e:
            self._log_error("確保使用者角色存在失敗", e)
            return False
    
    def get_user_role_hierarchy(self, user_id: str):
        """取得使用者的角色階層結構"""
        try:
            user_role = self.get_user_role(user_id)
            if not user_role:
                return None
            
            role_name = user_role.get("role_name")
            if not role_name:
                return None
            
            # 從角色模型取得階層結構
            from database.role_model import RoleModel
            role_model = RoleModel()
            return role_model.get_role_hierarchy(role_name)
            
        except Exception as e:
            self._log_error("取得使用者角色階層失敗", e)
            return None
    
    def remove_role_from_user(self, user_id: str, role_name: str = None):
        """移除使用者的角色"""
        try:
            if role_name:
                # 指定角色名稱
                from database.role_model import RoleModel
                role_model = RoleModel()
                role = role_model.get_role_by_name(role_name)
                if not role:
                    raise Exception(f"角色 '{role_name}' 不存在")
                
                result = self.api.remove_role_from_user(user_id, role["_id"])
            else:
                # 移除所有角色
                user_role = self.get_user_role(user_id)
                if not user_role:
                    self._log_warning(f"使用者沒有角色: {user_id}")
                    return True
                
                result = self.api.remove_role_from_user(user_id, user_role["_id"])
            
            if result.get("success"):
                self._log_success(f"使用者角色移除成功: {user_id}")
                return True
            else:
                raise Exception(f"移除角色失敗: {result.get('message', '未知錯誤')}")
                
        except Exception as e:
            self._log_error("移除使用者角色失敗", e)
            raise 