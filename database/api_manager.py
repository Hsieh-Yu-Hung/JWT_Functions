import requests
import logging
from typing import Dict, List, Optional, Any
from core.config import API_BASE_URL, API_KEY

logger = logging.getLogger(__name__)

class APIManager:
    """API 管理器，用於與 MongoDB Operation API 通信"""
    
    def __init__(self):
        self.base_url = API_BASE_URL
        self.api_key = API_KEY
        
        # API 端點配置
        self.endpoints = {
            "users": "/add/document/users",
            "roles": "/add/document/roles", 
            "user_role_mapping": "/add/document/user_role_mapping",
            "blacklist": "/add/document/blacklist"
        }
        
        # 查詢端點配置
        self.search_endpoints = {
            "users": "/search/documents/users",
            "roles": "/search/documents/roles",
            "user_role_mapping": "/search/documents/user_role_mapping", 
            "blacklist": "/search/documents/blacklist"
        }
        
        # 更新端點配置
        self.update_endpoints = {
            "users": "/update/document/users",
            "roles": "/update/document/roles",
            "user_role_mapping": "/update/document/user_role_mapping",
            "blacklist": "/update/document/blacklist"
        }
        
        # 刪除端點配置
        self.delete_endpoints = {
            "users": "/delete/document/users",
            "roles": "/delete/document/roles",
            "user_role_mapping": "/delete/document/user_role_mapping",
            "blacklist": "/delete/document/blacklist"
        }
        
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}" if self.api_key else ""
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None, params: Optional[Dict] = None) -> Dict:
        """發送 HTTP 請求到 API"""
        url = f"{self.base_url}{endpoint}"
        
        # 記錄請求資訊
        logger.info(f"發送 {method.upper()} 請求到: {url}")
        if data:
            logger.info(f"請求資料: {data}")
        if params:
            logger.info(f"請求參數: {params}")
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, params=params, timeout=30)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, timeout=30)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, timeout=30)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, params=params, timeout=30)
            else:
                raise ValueError(f"不支援的 HTTP 方法: {method}")
            
            # 記錄回應狀態
            logger.info(f"回應狀態碼: {response.status_code}")
            
            # 檢查 HTTP 狀態碼
            if response.status_code >= 400:
                error_text = response.text
                logger.error(f"HTTP 錯誤 {response.status_code}: {error_text}")
                # 嘗試解析 JSON 錯誤回應
                try:
                    error_json = response.json()
                    return {
                        "success": False,
                        "message": f"HTTP {response.status_code} 錯誤",
                        "details": error_json.get("message", error_text),
                        "status_code": response.status_code
                    }
                except:
                    return {
                        "success": False,
                        "message": f"HTTP {response.status_code} 錯誤",
                        "details": error_text,
                        "status_code": response.status_code
                    }
            
            # 嘗試解析 JSON 回應
            try:
                result = response.json()
                logger.info(f"API 回應: {result}")
                
                # 轉換 API 回應格式為我們期望的格式
                if response.status_code == 200:
                    # 健康檢查端點
                    if endpoint == "/health_check":
                        return {
                            "success": True,
                            "message": "健康檢查通過",
                            "data": result
                        }
                    
                    # 創建文件端點（POST 請求）
                    elif method.upper() == "POST" and "/add/document/" in endpoint:
                        if "inserted_id" in result:
                            return {
                                "success": True,
                                "message": "創建成功",
                                "data": {"id": result["inserted_id"]}
                            }
                        else:
                            return {
                                "success": True,
                                "message": "操作成功",
                                "data": result
                            }
                    
                    # 搜尋端點（GET 請求）
                    elif method.upper() == "GET" and "/search/" in endpoint:
                        if "data" in result:
                            return {
                                "success": True,
                                "message": "搜尋成功",
                                "data": result["data"]
                            }
                        else:
                            return {
                                "success": True,
                                "message": "搜尋成功",
                                "data": result
                            }
                    
                    # 更新端點（PUT 請求）
                    elif method.upper() == "PUT" and "/update/" in endpoint:
                        return {
                            "success": True,
                            "message": "更新成功",
                            "data": result
                        }
                    
                    # 刪除端點（DELETE 請求）
                    elif method.upper() == "DELETE" and "/delete/" in endpoint:
                        return {
                            "success": True,
                            "message": "刪除成功",
                            "data": result
                        }
                    
                    # 其他端點
                    else:
                        return {
                            "success": True,
                            "message": "操作成功",
                            "data": result
                        }
                else:
                    return {
                        "success": False,
                        "message": "操作失敗",
                        "details": result
                    }
                
            except Exception as json_error:
                logger.error(f"JSON 解析失敗: {json_error}")
                logger.error(f"原始回應: {response.text}")
                return {
                    "success": False,
                    "message": "回應格式錯誤",
                    "details": f"無法解析 JSON: {response.text[:200]}",
                    "status_code": response.status_code
                }
            
        except requests.exceptions.Timeout as e:
            logger.error(f"API 請求超時: {e}")
            return {
                "success": False,
                "message": "請求超時",
                "details": str(e)
            }
        except requests.exceptions.ConnectionError as e:
            logger.error(f"API 連接失敗: {e}")
            return {
                "success": False,
                "message": "連接失敗",
                "details": f"無法連接到 {self.base_url}: {str(e)}"
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"API 請求失敗: {e}")
            return {
                "success": False,
                "message": "請求失敗",
                "details": str(e)
            }
        except Exception as e:
            logger.error(f"未知錯誤: {e}")
            return {
                "success": False,
                "message": "未知錯誤",
                "details": str(e)
            }
    
    # User 相關操作
    def create_user(self, user_data: Dict) -> Dict:
        """創建新用戶"""
        return self._make_request("POST", self.endpoints["users"], data={"data": user_data})
    
    def get_user_by_id(self, user_id: str) -> Dict:
        """根據 ID 獲取用戶"""
        return self._make_request("GET", f"/search/document/users/{user_id}")
    
    def get_user_by_username(self, username: str) -> Dict:
        """根據用戶名獲取用戶"""
        return self._make_request("GET", self.search_endpoints["users"], params={"username": username})
    
    def get_user_by_email(self, email: str) -> Dict:
        """根據 email 獲取用戶"""
        return self._make_request("GET", self.search_endpoints["users"], params={"email": email})
    
    def update_user(self, user_id: str, user_data: Dict) -> Dict:
        """更新用戶資訊"""
        return self._make_request("PUT", f"{self.update_endpoints['users']}/{user_id}", data={"update": user_data})
    
    def delete_user(self, user_id: str) -> Dict:
        """刪除用戶"""
        return self._make_request("DELETE", f"{self.delete_endpoints['users']}/{user_id}")
    
    def get_all_users(self, skip: int = 0, limit: int = 100) -> Dict:
        """獲取所有用戶"""
        return self._make_request("GET", self.search_endpoints["users"], params={"skip": skip, "limit": limit})
    
    # Role 相關操作
    def create_role(self, role_data: Dict) -> Dict:
        """創建新角色"""
        return self._make_request("POST", self.endpoints["roles"], data={"data": role_data})
    
    def get_role_by_id(self, role_id: str) -> Dict:
        """根據 ID 獲取角色"""
        return self._make_request("GET", f"/search/document/roles/{role_id}")
    
    def get_role_by_name(self, role_name: str) -> Dict:
        """根據角色名獲取角色"""
        return self._make_request("GET", self.search_endpoints["roles"], params={"role_name": role_name})
    
    def update_role(self, role_id: str, role_data: Dict) -> Dict:
        """更新角色資訊"""
        return self._make_request("PUT", f"{self.update_endpoints['roles']}/{role_id}", data={"update": role_data})
    
    def delete_role(self, role_id: str) -> Dict:
        """刪除角色"""
        return self._make_request("DELETE", f"{self.delete_endpoints['roles']}/{role_id}")
    
    def get_all_roles(self, skip: int = 0, limit: int = 100) -> Dict:
        """獲取所有角色"""
        return self._make_request("GET", self.search_endpoints["roles"], params={"skip": skip, "limit": limit})
    
    # User-Role 映射相關操作
    def assign_role_to_user(self, user_id: str, role_id: str) -> Dict:
        """為用戶分配角色"""
        mapping_data = {
            "user_id": user_id,
            "role_id": role_id,
            "created_at": "2024-01-01T00:00:00Z"  # 使用當前時間
        }
        return self._make_request("POST", self.endpoints["user_role_mapping"], data={"data": mapping_data})
    
    def remove_role_from_user(self, user_id: str, role_id: str) -> Dict:
        """移除用戶的角色"""
        return self._make_request("DELETE", self.delete_endpoints["user_role_mapping"], params={
            "user_id": user_id,
            "role_id": role_id
        })
    
    def get_user_role_mapping(self, user_id: str) -> Dict:
        """獲取用戶的所有角色"""
        return self._make_request("GET", self.search_endpoints["user_role_mapping"], params={"user_id": user_id})
    
    def get_role_users(self, role_id: str) -> Dict:
        """獲取角色的所有用戶"""
        return self._make_request("GET", self.search_endpoints["user_role_mapping"], params={"role_id": role_id})
    
    # Blacklist 相關操作
    def add_to_blacklist(self, token: str, expires_at: str) -> Dict:
        """將 token 加入黑名單"""
        blacklist_data = {
            "token": token,
            "expires_at": expires_at,
            "created_at": "2024-01-01T00:00:00Z"  # 使用當前時間
        }
        return self._make_request("POST", self.endpoints["blacklist"], data={"data": blacklist_data})
    
    def is_token_blacklisted(self, token: str) -> Dict:
        """檢查 token 是否在黑名單中"""
        return self._make_request("GET", self.search_endpoints["blacklist"], params={"token": token})
    
    def remove_from_blacklist(self, token: str) -> Dict:
        """從黑名單中移除 token"""
        return self._make_request("DELETE", self.delete_endpoints["blacklist"], params={"token": token})
    
    def cleanup_expired_tokens(self) -> Dict:
        """清理過期的 token"""
        # 使用批量刪除功能，刪除過期的 token
        current_time = "2024-01-01T00:00:00Z"  # 使用當前時間
        return self._make_request("DELETE", self.delete_endpoints["blacklist"], params={
            "expires_at": {"$lt": current_time}
        })
    
    def get_blacklist_stats(self) -> Dict:
        """獲取黑名單統計資訊"""
        return self._make_request("GET", f"{self.search_endpoints['blacklist']}/count")
    
    # 通用操作方法
    def health_check(self) -> Dict:
        """檢查 API 服務狀態"""
        return self._make_request("GET", "/health_check")
    
    def get_collections(self) -> Dict:
        """獲取所有集合清單"""
        return self._make_request("GET", "/collections")
    
    def count_documents(self, collection: str, query: Optional[Dict] = None) -> Dict:
        """計算指定集合中的文件數量"""
        params = query or {}
        return self._make_request("GET", f"/search/documents/{collection}/count", params=params)
    
    def get_distinct_values(self, collection: str, field: str, query: Optional[Dict] = None) -> Dict:
        """獲取指定欄位的唯一值列表"""
        params = query or {}
        return self._make_request("GET", f"/search/documents/{collection}/distinct/{field}", params=params)
    
    def get_collection_stats(self, collection: str, group_by: Optional[str] = None, query: Optional[Dict] = None) -> Dict:
        """獲取集合統計資訊"""
        params = query or {}
        if group_by:
            params["group_by"] = group_by
        return self._make_request("GET", f"/search/documents/{collection}/stats", params=params)
    
    def clone_document(self, collection: str, document_id: str) -> Dict:
        """複製文件"""
        return self._make_request("POST", f"/add/document/{collection}/{document_id}/clone")
    
    def export_document(self, collection: str, document_id: str) -> Dict:
        """導出單筆文件"""
        return self._make_request("GET", f"/search/document/{collection}/{document_id}/export")
    
    def export_collection(self, collection: str, query: Optional[Dict] = None) -> Dict:
        """導出整個集合"""
        params = query or {}
        return self._make_request("GET", f"/search/documents/{collection}/export", params=params)
    
    def drop_collection(self, collection: str) -> Dict:
        """刪除整個集合（危險操作）"""
        return self._make_request("DELETE", f"/delete/collection/{collection}/drop")
    
    def batch_create_documents(self, collection: str, documents: List[Dict]) -> Dict:
        """批量創建文件"""
        return self._make_request("POST", f"/add/documents/{collection}/batch", data={"data": documents})
    
    def batch_update_documents(self, collection: str, query: Dict, update: Dict) -> Dict:
        """批量更新文件"""
        return self._make_request("PUT", f"/update/documents/{collection}/batch", data={
            "query": query,
            "update": update
        })
    
    def batch_delete_documents(self, collection: str, query: Dict) -> Dict:
        """批量刪除文件"""
        return self._make_request("DELETE", f"/delete/documents/{collection}", params=query)

# 全域 API 管理器實例
api_manager = APIManager() 