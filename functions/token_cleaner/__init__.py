"""
Token Cleaner 模組

提供獨立的 JWT Token 清理功能，適用於 Function Compute 環境
使用 jwt_auth_middleware 套件提供更強大的清理功能
"""

from .cleanup_function import handler, cleanup_tokens

__all__ = ['handler', 'cleanup_tokens']
__version__ = '2.0.0' 