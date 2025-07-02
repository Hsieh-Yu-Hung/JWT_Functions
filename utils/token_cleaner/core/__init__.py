"""
Core module for JWT Authentication
Contains configuration, JWT utilities, and user model
"""

# 不在此處進行相對路徑引用，避免循環引用問題
__all__ = [
    'SECRET_KEY',
    'ALGORITHM', 
    'ACCESS_TOKEN_EXPIRE_MINUTES',
    'MONGO_URI',
    'DB_NAME',
    'create_access_token',
    'verify_token',
    'revoke_token',
    'get_user_by_email',
    'verify_password'
] 