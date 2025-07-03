from datetime import datetime, UTC
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from database.api_manager import api_manager

logger = logging.getLogger(__name__)

class UserModel:
    """使用 API 的用戶模型"""
    
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
        else:
            logger.error(f"❌ {message}")
            print(f"❌ {message}")
    
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
            existing_user = self.api.get_user_by_username(email)
            if existing_user.get("success") and existing_user.get("data"):
                self._log_warning(f"Email 已存在: {email}")
                return None
            
            # 檢查 username 是否已存在（如果提供）
            if username:
                existing_user = self.api.get_user_by_username(username)
                if existing_user.get("success") and existing_user.get("data"):
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
                "created_at": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat(),
                "last_login": None
            }
            
            # 透過 API 創建使用者
            result = self.api.create_user(user_data)
            
            if result.get("success"):
                user_id = result.get("data", {}).get("id")
                self._log_success(f"使用者註冊成功: {email}")
                return user_id
            else:
                self._log_error(f"使用者註冊失敗: {result.get('message', '未知錯誤')}")
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
            # 透過 API 查詢使用者
            result = self.api.get_user_by_email(email)
            
            if not result.get("success") or not result.get("data"):
                self._log_warning(f"使用者不存在或已停用: {email}")
                return None
            
            # 如果 data 是列表，取第一個元素
            user_data = result["data"]
            if isinstance(user_data, list):
                if not user_data:
                    self._log_warning(f"使用者不存在: {email}")
                    return None
                user = user_data[0]
            else:
                user = user_data
            
            # 驗證密碼
            if not check_password_hash(user["password_hash"], password):
                self._log_warning(f"密碼錯誤: {email}")
                return None
            
            # 更新最後登入時間
            update_data = {
                "last_login": datetime.now(UTC).isoformat(),
                "updated_at": datetime.now(UTC).isoformat()
            }
            
            update_result = self.api.update_user(user["_id"], update_data)
            
            if update_result.get("success"):
                self._log_success(f"使用者登入成功: {email}")
            
            # 返回使用者資料（不包含密碼雜湊）
            user_data = {
                "id": user["_id"],
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
            result = self.api.get_user_by_email(email)
            
            if not result.get("success") or not result.get("data"):
                return None
            
            # 如果 data 是列表，取第一個元素
            user_data = result["data"]
            if isinstance(user_data, list):
                if not user_data:
                    return None
                user = user_data[0]
            else:
                user = user_data
            
            # 返回使用者資料（不包含密碼雜湊）
            user_data = {
                "id": user["_id"],
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
            # 先取得使用者 ID
            user = self.get_user_by_email(email)
            if not user:
                self._log_warning(f"使用者不存在: {email}")
                return False
            
            # 不允許更新敏感欄位
            restricted_fields = ["password_hash", "email", "created_at", "id"]
            filtered_data = {k: v for k, v in update_data.items() if k not in restricted_fields}
            
            if not filtered_data:
                self._log_warning("沒有有效的更新資料")
                return False
            
            filtered_data["updated_at"] = datetime.now(UTC).isoformat()
            
            result = self.api.update_user(user["id"], filtered_data)
            
            if result.get("success"):
                self._log_success(f"使用者資料更新成功: {email}")
                return True
            else:
                self._log_warning(f"使用者資料更新失敗: {result.get('message', '未知錯誤')}")
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
            result = self.api.get_user_by_email(email)
            
            if not result.get("success") or not result.get("data"):
                self._log_warning(f"使用者不存在或已停用: {email}")
                return False
            
            user_data = result["data"]
            if isinstance(user_data, list):
                if not user_data:
                    self._log_warning(f"使用者不存在: {email}")
                    return False
                user = user_data[0]
            else:
                user = user_data
            
            if not check_password_hash(user["password_hash"], old_password):
                self._log_warning(f"舊密碼錯誤: {email}")
                return False
            
            # 生成新密碼雜湊
            new_password_hash = generate_password_hash(new_password)
            
            # 更新密碼
            update_data = {
                "password_hash": new_password_hash,
                "updated_at": datetime.now(UTC).isoformat()
            }
            
            update_result = self.api.update_user(user["_id"], update_data)
            
            if update_result.get("success"):
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
            # 先取得使用者 ID
            user = self.get_user_by_email(email)
            if not user:
                self._log_warning(f"使用者不存在: {email}")
                return False
            
            update_data = {
                "is_active": False,
                "updated_at": datetime.now(UTC).isoformat()
            }
            
            result = self.api.update_user(user["id"], update_data)
            
            if result.get("success"):
                self._log_success(f"使用者已停用: {email}")
                return True
            else:
                self._log_warning(f"停用使用者失敗: {result.get('message', '未知錯誤')}")
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
            result = self.api.get_all_users()
            
            if not result.get("success"):
                self._log_error(f"取得使用者列表失敗: {result.get('message', '未知錯誤')}")
                return []
            
            users = result.get("data", [])
            
            # 過濾活躍使用者並移除密碼雜湊
            active_users = []
            for user in users:
                if user.get("is_active", False):
                    user_data = {
                        "id": user.get("_id", user.get("id")),
                        "email": user["email"],
                        "username": user["username"],
                        "is_active": user["is_active"],
                        "created_at": user["created_at"],
                        "last_login": user.get("last_login")
                    }
                    active_users.append(user_data)
            
            return active_users
            
        except Exception as e:
            self._log_error("取得活躍使用者失敗", e)
            return [] 