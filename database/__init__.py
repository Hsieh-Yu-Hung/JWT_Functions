"""
Database module for JWT Authentication
Contains API manager and models for database operations
"""

# 匯出 API 管理器
from .api_manager import api_manager, APIManager

# 匯出模型
from .user_model import UserModel
from .role_model import RoleModel
from .user_role_mapping_model import UserRoleMappingModel
from .blacklist_model import BlacklistModel

# 保留原有的資料庫管理器（作為備用）
from .database import db_manager, MongoDBManager

__all__ = [
    # API 管理器
    'api_manager',
    'APIManager',
    
    # 模型
    'UserModel',
    'RoleModel', 
    'UserRoleMappingModel',
    'BlacklistModel',
    
    # 備用資料庫管理器
    'db_manager',
    'MongoDBManager'
] 