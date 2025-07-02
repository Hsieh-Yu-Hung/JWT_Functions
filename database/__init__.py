"""
Database module for JWT Authentication
Contains database connection and models
"""

# 不在此處進行相對路徑引用，避免循環引用問題
__all__ = [
    'db_manager',
    'BlacklistModel',
    'RoleModel'
] 