from datetime import datetime, UTC
from database.base_model import BaseModel
from core.config import MONGODB_USERS_COLLECTION
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logger = logging.getLogger(__name__)

class UserModel(BaseModel):
    def __init__(self):
        super().__init__(MONGODB_USERS_COLLECTION)
    
    def _create_indexes(self):
        """建立索引"""
        try:
            # 確保 collection 已初始化
            if self.collection is None:
                from database.database import db_manager
                self.collection = db_manager.get_collection(self.collection_name)
                self._initialized = True
            
            # 為 email 建立唯一索引
            self.create_index("email", unique=True)
            # 為 username 建立唯一索引（如果需要的話）
            self.create_index("username", unique=True)
            # 為 is_active 建立索引
            self.create_index("is_active")
            # 為 created_at 建立索引
            self.create_index("created_at")
            
        except Exception as e:
            logger.error(f"❌ User 索引建立失敗: {e}")
    
    def register_user(self, email: str, password: str, username: str = None):
        """
        註冊新使用者
        
        Args:
            email: 使用者 email
            password: 明文密碼
            username: 使用者名稱（可選）
            
        Returns:
            註冊成功返回使用者 ID，失敗返回 None
        """
        try:
            # 檢查 email 是否已存在
            if self.exists({"email": email}):
                self._log_warning(f"Email 已存在: {email}")
                return None
            
            # 檢查 username 是否已存在（如果提供）
            if username and self.exists({"username": username}):
                self._log_warning(f"Username 已存在: {username}")
                return None
            
            # 生成密碼雜湊
            password_hash = generate_password_hash(password)
            
            # 建立使用者資料
            user_data = {
                "email": email,
                "password_hash": password_hash,
                "username": username or email.split("@")[0],  # 如果沒有提供 username，使用 email 前綴
                "is_active": True,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "last_login": None
            }
            
            # 插入使用者資料
            user_id = self.insert_one(user_data)
            
            if user_id:
                self._log_success(f"使用者註冊成功: {email}")
                return user_id
            else:
                self._log_error("使用者註冊失敗")
                return None
                
        except Exception as e:
            self._log_error("註冊使用者失敗", e)
            return None
    
    def authenticate_user(self, email: str, password: str):
        """
        驗證使用者登入
        
        Args:
            email: 使用者 email
            password: 明文密碼
            
        Returns:
            驗證成功返回使用者資料，失敗返回 None
        """
        try:
            # 查詢使用者
            user = self.find_one({"email": email, "is_active": True})
            
            if not user:
                self._log_warning(f"使用者不存在或已停用: {email}")
                return None
            
            # 驗證密碼
            if not check_password_hash(user["password_hash"], password):
                self._log_warning(f"密碼錯誤: {email}")
                return None
            
            # 更新最後登入時間
            self.update_one(
                {"email": email},
                {"last_login": datetime.now(UTC), "updated_at": datetime.now(UTC)}
            )
            
            self._log_success(f"使用者登入成功: {email}")
            
            # 返回使用者資料（不包含密碼雜湊）
            user_data = {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
                "last_login": user["last_login"]
            }
            
            return user_data
            
        except Exception as e:
            self._log_error("驗證使用者失敗", e)
            return None
    
    def get_user_by_email(self, email: str):
        """
        根據 email 取得使用者資料
        
        Args:
            email: 使用者 email
            
        Returns:
            使用者資料，不包含密碼雜湊
        """
        try:
            user = self.find_one({"email": email, "is_active": True})
            
            if not user:
                return None
            
            # 返回使用者資料（不包含密碼雜湊）
            user_data = {
                "id": str(user["_id"]),
                "email": user["email"],
                "username": user["username"],
                "is_active": user["is_active"],
                "created_at": user["created_at"],
                "last_login": user["last_login"]
            }
            
            return user_data
            
        except Exception as e:
            self._log_error("取得使用者資料失敗", e)
            return None
    
    def update_user_profile(self, email: str, update_data: dict):
        """
        更新使用者資料
        
        Args:
            email: 使用者 email
            update_data: 要更新的資料
            
        Returns:
            更新是否成功
        """
        try:
            # 不允許更新敏感欄位
            restricted_fields = ["password_hash", "email", "created_at", "_id"]
            filtered_data = {k: v for k, v in update_data.items() if k not in restricted_fields}
            
            if not filtered_data:
                self._log_warning("沒有有效的更新資料")
                return False
            
            filtered_data["updated_at"] = datetime.now(UTC)
            
            success = self.update_one({"email": email}, filtered_data)
            
            if success:
                self._log_success(f"使用者資料更新成功: {email}")
                return True
            else:
                self._log_warning(f"使用者資料更新失敗（未找到記錄）: {email}")
                return False
                
        except Exception as e:
            self._log_error("更新使用者資料失敗", e)
            return False
    
    def change_password(self, email: str, old_password: str, new_password: str):
        """
        變更密碼
        
        Args:
            email: 使用者 email
            old_password: 舊密碼
            new_password: 新密碼
            
        Returns:
            變更是否成功
        """
        try:
            # 先驗證舊密碼
            user = self.find_one({"email": email, "is_active": True})
            
            if not user:
                self._log_warning(f"使用者不存在或已停用: {email}")
                return False
            
            if not check_password_hash(user["password_hash"], old_password):
                self._log_warning(f"舊密碼錯誤: {email}")
                return False
            
            # 生成新密碼雜湊
            new_password_hash = generate_password_hash(new_password)
            
            # 更新密碼
            success = self.update_one(
                {"email": email},
                {"password_hash": new_password_hash, "updated_at": datetime.now(UTC)}
            )
            
            if success:
                self._log_success(f"密碼變更成功: {email}")
                return True
            else:
                self._log_error("密碼變更失敗")
                return False
                
        except Exception as e:
            self._log_error("變更密碼失敗", e)
            return False
    
    def deactivate_user(self, email: str):
        """
        停用使用者
        
        Args:
            email: 使用者 email
            
        Returns:
            停用是否成功
        """
        try:
            success = self.update_one(
                {"email": email},
                {"is_active": False, "updated_at": datetime.now(UTC)}
            )
            
            if success:
                self._log_success(f"使用者已停用: {email}")
                return True
            else:
                self._log_warning(f"停用使用者失敗（未找到記錄）: {email}")
                return False
                
        except Exception as e:
            self._log_error("停用使用者失敗", e)
            return False
    
    def get_all_active_users(self):
        """
        取得所有活躍使用者
        
        Returns:
            活躍使用者列表
        """
        try:
            users = self.find_many({"is_active": True})
            
            # 移除密碼雜湊
            for user in users:
                user["id"] = str(user["_id"])
                del user["_id"]
                del user["password_hash"]
            
            return users
            
        except Exception as e:
            self._log_error("取得活躍使用者失敗", e)
            return [] 