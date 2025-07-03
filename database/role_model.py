from datetime import datetime, UTC
import logging
from database.api_manager import api_manager

logger = logging.getLogger(__name__)

class RoleModel:
    """使用 API 的角色模型"""
    
    def __init__(self):
        self.api = api_manager
        self._initialize_default_roles()
    
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
    
    def _initialize_default_roles(self):
        """初始化預設角色"""
        try:
            # 檢查是否已存在預設角色
            result = self.api.get_all_roles()
            if result.get("success") and result.get("data"):
                logger.info("✅ 預設角色已存在，跳過初始化")
                return
            
            # 建立預設角色
            default_roles = [
                {
                    "role_id": "user_role_001",
                    "role_name": "user",
                    "role_description": "一般使用者，擁有基本權限",
                    "role_permissions": ["user:read", "user:write"],
                    "inherited_roles": [],  # user 角色不繼承其他角色
                    "is_active": True,
                    "priority": 10,
                    "created_at": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat()
                },
                {
                    "role_id": "admin_role_001", 
                    "role_name": "admin",
                    "role_description": "系統管理員，擁有所有權限並繼承 user 權限",
                    "role_permissions": ["admin:read", "admin:write"],
                    "inherited_roles": ["user"],  # admin 繼承 user 角色
                    "is_active": True,
                    "priority": 100,
                    "created_at": datetime.now(UTC).isoformat(),
                    "updated_at": datetime.now(UTC).isoformat()
                }
            ]
            
            for role in default_roles:
                self.api.create_role(role)
            
            logger.info("✅ 預設角色初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 預設角色初始化失敗: {e}")
    
    def create_role(self, role_name: str, role_description: str, role_permissions: list, 
                   inherited_roles: list = None, priority: int = 50):
        """建立新角色"""
        try:
            # 檢查角色名稱是否已存在
            existing_role = self.get_role_by_name(role_name)
            if existing_role:
                raise Exception(f"角色名稱 '{role_name}' 已存在")
            
            # 驗證繼承的角色是否存在
            if inherited_roles:
                for inherited_role in inherited_roles:
                    if not self.get_role_by_name(inherited_role):
                        raise Exception(f"繼承的角色 '{inherited_role}' 不存在或已停用")
            
            role_data = {
                "role_id": f"{role_name}_role_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "role_name": role_name,
                "role_description": role_description,
                "role_permissions": role_permissions or [],
                "inherited_roles": inherited_roles or [],
                "is_active": True,
                "priority": priority,
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat()
            }
            
            result = self.api.create_role(role_data)
            if result.get("success"):
                role_id = result.get("data", {}).get("id")
                self._log_success(f"角色建立成功: {role_name}")
                return role_id
            else:
                raise Exception(f"角色建立失敗: {result.get('message', '未知錯誤')}")
                
        except Exception as e:
            self._log_error("建立角色失敗", e)
            raise
    
    def get_role_by_name(self, role_name: str):
        """根據角色名稱取得角色"""
        try:
            result = self.api.get_role_by_name(role_name)
            if result.get("success") and result.get("data"):
                # 如果 data 是列表，取第一個元素
                role_data = result["data"]
                if isinstance(role_data, list):
                    if not role_data:
                        return None
                    role = role_data[0]
                else:
                    role = role_data
                
                if role.get("is_active", False):
                    return role
            return None
        except Exception as e:
            self._log_error("取得角色失敗", e)
            return None
    
    def get_role_by_id(self, role_id: str):
        """根據角色 ID 取得角色"""
        try:
            result = self.api.get_role_by_id(role_id)
            if result.get("success") and result.get("data"):
                role = result["data"]
                if role.get("is_active", False):
                    return role
            return None
        except Exception as e:
            self._log_error("取得角色失敗", e)
            return None
    
    def get_all_roles(self):
        """取得所有啟用的角色"""
        try:
            result = self.api.get_all_roles()
            if result.get("success"):
                roles = result.get("data", [])
                return [role for role in roles if role.get("is_active", False)]
            return []
        except Exception as e:
            self._log_error("取得所有角色失敗", e)
            return []
    
    def get_role_permissions(self, role_name: str, include_inherited: bool = True):
        """取得角色的所有權限（包含繼承的權限）"""
        try:
            role = self.get_role_by_name(role_name)
            if not role:
                return []
            
            permissions = set(role.get("role_permissions", []))
            
            if include_inherited:
                # 遞迴取得繼承角色的權限
                inherited_permissions = self._get_inherited_permissions(role.get("inherited_roles", []))
                permissions.update(inherited_permissions)
            
            return list(permissions)
            
        except Exception as e:
            self._log_error("取得角色權限失敗", e)
            return []
    
    def _get_inherited_permissions(self, inherited_roles: list):
        """遞迴取得繼承角色的權限"""
        permissions = set()
        
        for inherited_role_name in inherited_roles:
            inherited_role = self.get_role_by_name(inherited_role_name)
            if inherited_role:
                # 加入直接權限
                permissions.update(inherited_role.get("role_permissions", []))
                # 遞迴取得更深層的繼承權限
                deeper_permissions = self._get_inherited_permissions(
                    inherited_role.get("inherited_roles", [])
                )
                permissions.update(deeper_permissions)
        
        return permissions
    
    def update_role(self, role_name: str, role_description: str = None, 
                   role_permissions: list = None, inherited_roles: list = None, 
                   priority: int = None):
        """更新角色"""
        try:
            # 先取得角色 ID
            role = self.get_role_by_name(role_name)
            if not role:
                raise Exception(f"角色 '{role_name}' 不存在")
            
            update_data = {"updated_at": datetime.now(UTC).isoformat()}
            
            if role_description is not None:
                update_data["role_description"] = role_description
            if role_permissions is not None:
                update_data["role_permissions"] = role_permissions
            if inherited_roles is not None:
                # 驗證繼承的角色是否存在
                for inherited_role in inherited_roles:
                    if not self.get_role_by_name(inherited_role):
                        raise Exception(f"繼承的角色 '{inherited_role}' 不存在或已停用")
                update_data["inherited_roles"] = inherited_roles
            if priority is not None:
                update_data["priority"] = priority
            
            result = self.api.update_role(role["_id"], update_data)
            
            if result.get("success"):
                self._log_success(f"角色更新成功: {role_name}")
                return True
            else:
                raise Exception(f"角色更新失敗: {result.get('message', '未知錯誤')}")
                
        except Exception as e:
            self._log_error("更新角色失敗", e)
            raise
    
    def deactivate_role(self, role_name: str):
        """停用角色"""
        try:
            role = self.get_role_by_name(role_name)
            if not role:
                raise Exception(f"角色 '{role_name}' 不存在")
            
            update_data = {
                "is_active": False,
                "updated_at": datetime.now(UTC).isoformat()
            }
            
            result = self.api.update_role(role["_id"], update_data)
            
            if result.get("success"):
                self._log_success(f"角色已停用: {role_name}")
                return True
            else:
                raise Exception(f"停用角色失敗: {result.get('message', '未知錯誤')}")
                
        except Exception as e:
            self._log_error("停用角色失敗", e)
            raise
    
    def activate_role(self, role_name: str):
        """啟用角色"""
        try:
            # 先取得角色（包括已停用的）
            result = self.api.get_role_by_name(role_name)
            if not result.get("success") or not result.get("data"):
                raise Exception(f"角色 '{role_name}' 不存在")
            
            # 如果 data 是列表，取第一個元素
            role_data = result["data"]
            if isinstance(role_data, list):
                if not role_data:
                    raise Exception(f"角色 '{role_name}' 不存在")
                role = role_data[0]
            else:
                role = role_data
            
            update_data = {
                "is_active": True,
                "updated_at": datetime.now(UTC).isoformat()
            }
            
            result = self.api.update_role(role["_id"], update_data)
            
            if result.get("success"):
                self._log_success(f"角色已啟用: {role_name}")
                return True
            else:
                raise Exception(f"啟用角色失敗: {result.get('message', '未知錯誤')}")
                
        except Exception as e:
            self._log_error("啟用角色失敗", e)
            raise
    
    def check_role_permission(self, role_name: str, required_permission: str):
        """檢查角色是否擁有指定權限"""
        try:
            permissions = self.get_role_permissions(role_name, include_inherited=True)
            return required_permission in permissions
        except Exception as e:
            self._log_error("檢查角色權限失敗", e)
            return False
    
    def get_role_hierarchy(self, role_name: str):
        """取得角色階層結構"""
        try:
            role = self.get_role_by_name(role_name)
            if not role:
                return None
            
            hierarchy = {
                "role_name": role_name,
                "role_description": role.get("role_description"),
                "permissions": role.get("role_permissions", []),
                "inherited_roles": [],
                "priority": role.get("priority", 0)
            }
            
            # 遞迴取得繼承角色的階層
            for inherited_role_name in role.get("inherited_roles", []):
                inherited_hierarchy = self.get_role_hierarchy(inherited_role_name)
                if inherited_hierarchy:
                    hierarchy["inherited_roles"].append(inherited_hierarchy)
            
            return hierarchy
            
        except Exception as e:
            self._log_error("取得角色階層失敗", e)
            return None
    
    def delete_role(self, role_name: str):
        """刪除角色（永久刪除）"""
        try:
            role = self.get_role_by_name(role_name)
            if not role:
                raise Exception(f"角色 '{role_name}' 不存在")
            
            result = self.api.delete_role(role["_id"])
            
            if result.get("success"):
                self._log_success(f"角色已刪除: {role_name}")
                return True
            else:
                raise Exception(f"刪除角色失敗: {result.get('message', '未知錯誤')}")
                
        except Exception as e:
            self._log_error("刪除角色失敗", e)
            raise 