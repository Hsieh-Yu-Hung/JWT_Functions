from datetime import datetime, UTC
from database.base_model import BaseModel
from core.config import MONGODB_ROLE_COLLECTION
import logging

logger = logging.getLogger(__name__)

class RoleModel(BaseModel):
    def __init__(self):
        super().__init__(MONGODB_ROLE_COLLECTION)
        self._initialize_default_roles()
    
    def _create_indexes(self):
        """建立索引"""
        try:
            # 確保 collection 已初始化
            if self.collection is None:
                from database.database import db_manager
                self.collection = db_manager.get_collection(self.collection_name)
                self._initialized = True
            
            # 為 role_id 建立唯一索引
            self.create_index("role_id", unique=True)
            # 為 role_name 建立唯一索引
            self.create_index("role_name", unique=True)
            # 為 is_active 建立索引
            self.create_index("is_active")
            # 為 priority 建立索引
            self.create_index("priority")
            
        except Exception as e:
            logger.error(f"❌ Role 索引建立失敗: {e}")
    
    def _initialize_default_roles(self):
        """初始化預設角色"""
        try:
            # 檢查是否已存在預設角色
            existing_roles = self.find_many({})
            if existing_roles:
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
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC)
                },
                {
                    "role_id": "admin_role_001", 
                    "role_name": "admin",
                    "role_description": "系統管理員，擁有所有權限並繼承 user 權限",
                    "role_permissions": ["admin:read", "admin:write"],
                    "inherited_roles": ["user"],  # admin 繼承 user 角色
                    "is_active": True,
                    "priority": 100,
                    "created_at": datetime.now(UTC),
                    "updated_at": datetime.now(UTC)
                }
            ]
            
            for role in default_roles:
                self.insert_one(role)
            
            logger.info("✅ 預設角色初始化完成")
            
        except Exception as e:
            logger.error(f"❌ 預設角色初始化失敗: {e}")
    
    def create_role(self, role_name: str, role_description: str, role_permissions: list, 
                   inherited_roles: list = None, priority: int = 50):
        """建立新角色"""
        try:
            # 檢查角色名稱是否已存在
            existing_role = self.find_one({"role_name": role_name})
            if existing_role:
                raise Exception(f"角色名稱 '{role_name}' 已存在")
            
            # 驗證繼承的角色是否存在
            if inherited_roles:
                for inherited_role in inherited_roles:
                    if not self.find_one({"role_name": inherited_role, "is_active": True}):
                        raise Exception(f"繼承的角色 '{inherited_role}' 不存在或已停用")
            
            role_data = {
                "role_id": f"{role_name}_role_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "role_name": role_name,
                "role_description": role_description,
                "role_permissions": role_permissions or [],
                "inherited_roles": inherited_roles or [],
                "is_active": True,
                "priority": priority,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            }
            
            result_id = self.insert_one(role_data)
            if result_id:
                self._log_success(f"角色建立成功: {role_name}")
                return result_id
            else:
                raise Exception("插入失敗")
                
        except Exception as e:
            self._log_error("建立角色失敗", e)
            raise
    
    def get_role_by_name(self, role_name: str):
        """根據角色名稱取得角色"""
        try:
            return self.find_one({"role_name": role_name, "is_active": True})
        except Exception as e:
            self._log_error("取得角色失敗", e)
            return None
    
    def get_role_by_id(self, role_id: str):
        """根據角色 ID 取得角色"""
        try:
            return self.find_one({"role_id": role_id, "is_active": True})
        except Exception as e:
            self._log_error("取得角色失敗", e)
            return None
    
    def get_all_roles(self):
        """取得所有啟用的角色"""
        try:
            return self.find_many({"is_active": True})
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
            update_data = {"updated_at": datetime.now(UTC)}
            
            if role_description is not None:
                update_data["role_description"] = role_description
            if role_permissions is not None:
                update_data["role_permissions"] = role_permissions
            if inherited_roles is not None:
                # 驗證繼承的角色是否存在
                for inherited_role in inherited_roles:
                    if not self.find_one({"role_name": inherited_role, "is_active": True}):
                        raise Exception(f"繼承的角色 '{inherited_role}' 不存在或已停用")
                update_data["inherited_roles"] = inherited_roles
            if priority is not None:
                update_data["priority"] = priority
            
            success = self.update_one({"role_name": role_name}, update_data)
            
            if success:
                self._log_success(f"角色更新成功: {role_name}")
                return True
            else:
                self._log_warning(f"角色更新失敗（未找到記錄）: {role_name}")
                return False
                
        except Exception as e:
            self._log_error("更新角色失敗", e)
            return False
    
    def deactivate_role(self, role_name: str):
        """停用角色"""
        try:
            success = self.update_one(
                {"role_name": role_name},
                {"is_active": False, "updated_at": datetime.now(UTC)}
            )
            
            if success:
                self._log_success(f"角色已停用: {role_name}")
                return True
            else:
                self._log_warning(f"停用角色失敗（未找到記錄）: {role_name}")
                return False
                
        except Exception as e:
            self._log_error("停用角色失敗", e)
            return False
    
    def activate_role(self, role_name: str):
        """啟用角色"""
        try:
            success = self.update_one(
                {"role_name": role_name},
                {"is_active": True, "updated_at": datetime.now(UTC)}
            )
            
            if success:
                self._log_success(f"角色已啟用: {role_name}")
                return True
            else:
                self._log_warning(f"啟用角色失敗（未找到記錄）: {role_name}")
                return False
                
        except Exception as e:
            self._log_error("啟用角色失敗", e)
            return False
    
    def check_role_permission(self, role_name: str, required_permission: str):
        """檢查角色是否擁有特定權限（包含繼承權限）"""
        try:
            permissions = self.get_role_permissions(role_name, include_inherited=True)
            return required_permission in permissions
        except Exception as e:
            self._log_error("檢查角色權限失敗", e)
            return False
    
    def get_role_hierarchy(self, role_name: str):
        """取得角色的完整繼承層級結構"""
        try:
            role = self.get_role_by_name(role_name)
            if not role:
                return None
            
            hierarchy = {
                "role_name": role_name,
                "role_description": role.get("role_description"),
                "direct_permissions": role.get("role_permissions", []),
                "inherited_roles": [],
                "all_permissions": self.get_role_permissions(role_name, include_inherited=True)
            }
            
            # 遞迴取得繼承角色的詳細資訊
            for inherited_role_name in role.get("inherited_roles", []):
                inherited_hierarchy = self.get_role_hierarchy(inherited_role_name)
                if inherited_hierarchy:
                    hierarchy["inherited_roles"].append(inherited_hierarchy)
            
            return hierarchy
            
        except Exception as e:
            self._log_error("取得角色層級結構失敗", e)
            return None
    
    def delete_role(self, role_name: str):
        """刪除角色（僅在沒有其他角色繼承時允許）"""
        try:
            # 檢查是否有其他角色繼承此角色
            inheriting_roles = self.find_many({"inherited_roles": role_name})
            if inheriting_roles:
                inheriting_names = [r["role_name"] for r in inheriting_roles]
                raise Exception(f"無法刪除角色 '{role_name}'，因為以下角色正在繼承它: {inheriting_names}")
            
            success = self.delete_one({"role_name": role_name})
            
            if success:
                self._log_success(f"角色刪除成功: {role_name}")
                return True
            else:
                self._log_warning(f"刪除角色失敗（未找到記錄）: {role_name}")
                return False
                
        except Exception as e:
            self._log_error("刪除角色失敗", e)
            return False 