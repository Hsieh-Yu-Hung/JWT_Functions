from datetime import datetime, UTC
import logging
from typing import Dict, List, Any, Optional, Union
from pymongo.collection import Collection
from pymongo.cursor import Cursor

logger = logging.getLogger(__name__)

class BaseModel:
    """MongoDB 模型基礎類別，提供通用的資料庫操作方法"""
    
    def __init__(self, collection_name: str):
        """
        初始化基礎模型
        
        Args:
            collection_name: MongoDB collection 名稱
        """
        self.collection_name = collection_name
        self.collection: Collection = None
        self._initialized = False
    
    def _ensure_initialized(self):
        """確保模型已初始化"""
        if not self._initialized:
            from database.database import db_manager
            self.collection = db_manager.get_collection(self.collection_name)
            self._initialized = True
            # 在初始化完成後才建立索引，避免遞迴調用
            self._create_indexes()
    
    def _create_indexes(self):
        """建立索引 - 子類別需要實作此方法"""
        raise NotImplementedError("子類別必須實作 _create_indexes 方法")
    
    def _log_success(self, message: str):
        """記錄成功訊息"""
        logger.info(f"✅ {message}")
        # 移除 print 以避免遞迴問題
    
    def _log_error(self, message: str, error: Exception = None):
        """記錄錯誤訊息"""
        error_msg = f"❌ {message}"
        if error:
            error_msg += f": {error}"
        logger.error(error_msg)
        # 移除 print 以避免遞迴問題
    
    def _log_warning(self, message: str):
        """記錄警告訊息"""
        logger.warning(f"⚠️ {message}")
        # 移除 print 以避免遞迴問題
    
    def insert_one(self, document: Dict[str, Any]) -> Optional[str]:
        """
        插入單一文件
        
        Args:
            document: 要插入的文件
            
        Returns:
            插入的文件 ID，失敗時返回 None
        """
        try:
            self._ensure_initialized()
            result = self.collection.insert_one(document)
            return str(result.inserted_id)
        except Exception as e:
            self._log_error(f"插入文件失敗", e)
            return None
    
    def insert_many(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        插入多個文件
        
        Args:
            documents: 要插入的文件列表
            
        Returns:
            插入的文件 ID 列表
        """
        try:
            self._ensure_initialized()
            result = self.collection.insert_many(documents)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            self._log_error(f"批量插入文件失敗", e)
            return []
    
    def find_one(self, filter_dict: Dict[str, Any], projection: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        查詢單一文件
        
        Args:
            filter_dict: 查詢條件
            projection: 投影欄位
            
        Returns:
            查詢到的文件，未找到時返回 None
        """
        try:
            self._ensure_initialized()
            return self.collection.find_one(filter_dict, projection)
        except Exception as e:
            self._log_error(f"查詢文件失敗", e)
            return None
    
    def find_many(self, filter_dict: Dict[str, Any] = None, projection: Dict[str, Any] = None, 
                  sort: List[tuple] = None, limit: int = None) -> List[Dict[str, Any]]:
        """
        查詢多個文件
        
        Args:
            filter_dict: 查詢條件
            projection: 投影欄位
            sort: 排序條件
            limit: 限制數量
            
        Returns:
            查詢到的文件列表
        """
        try:
            self._ensure_initialized()
            cursor = self.collection.find(filter_dict or {}, projection)
            
            if sort:
                cursor = cursor.sort(sort)
            if limit:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except Exception as e:
            self._log_error(f"查詢多個文件失敗", e)
            return []
    
    def update_one(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool:
        """
        更新單一文件
        
        Args:
            filter_dict: 查詢條件
            update_dict: 更新內容
            
        Returns:
            更新是否成功
        """
        try:
            self._ensure_initialized()
            result = self.collection.update_one(filter_dict, {"$set": update_dict})
            return result.modified_count > 0
        except Exception as e:
            self._log_error(f"更新文件失敗", e)
            return False
    
    def update_many(self, filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> int:
        """
        更新多個文件
        
        Args:
            filter_dict: 查詢條件
            update_dict: 更新內容
            
        Returns:
            更新的文件數量
        """
        try:
            self._ensure_initialized()
            result = self.collection.update_many(filter_dict, {"$set": update_dict})
            return result.modified_count
        except Exception as e:
            self._log_error(f"批量更新文件失敗", e)
            return 0
    
    def delete_one(self, filter_dict: Dict[str, Any]) -> bool:
        """
        刪除單一文件
        
        Args:
            filter_dict: 查詢條件
            
        Returns:
            刪除是否成功
        """
        try:
            self._ensure_initialized()
            result = self.collection.delete_one(filter_dict)
            return result.deleted_count > 0
        except Exception as e:
            self._log_error(f"刪除文件失敗", e)
            return False
    
    def delete_many(self, filter_dict: Dict[str, Any]) -> int:
        """
        刪除多個文件
        
        Args:
            filter_dict: 查詢條件
            
        Returns:
            刪除的文件數量
        """
        try:
            self._ensure_initialized()
            result = self.collection.delete_many(filter_dict)
            return result.deleted_count
        except Exception as e:
            self._log_error(f"批量刪除文件失敗", e)
            return 0
    
    def count_documents(self, filter_dict: Dict[str, Any] = None) -> int:
        """
        計算文件數量
        
        Args:
            filter_dict: 查詢條件
            
        Returns:
            文件數量
        """
        try:
            self._ensure_initialized()
            return self.collection.count_documents(filter_dict or {})
        except Exception as e:
            self._log_error(f"計算文件數量失敗", e)
            return 0
    
    def exists(self, filter_dict: Dict[str, Any]) -> bool:
        """
        檢查文件是否存在
        
        Args:
            filter_dict: 查詢條件
            
        Returns:
            文件是否存在
        """
        try:
            self._ensure_initialized()
            return self.collection.count_documents(filter_dict, limit=1) > 0
        except Exception as e:
            self._log_error(f"檢查文件存在失敗", e)
            return False
    
    def create_index(self, field: str, unique: bool = False, expire_after_seconds: int = None):
        """
        建立索引
        
        Args:
            field: 欄位名稱
            unique: 是否為唯一索引
            expire_after_seconds: TTL 索引的過期時間（秒）
        """
        try:
            # 確保 collection 已初始化
            if self.collection is None:
                from database.database import db_manager
                self.collection = db_manager.get_collection(self.collection_name)
                self._initialized = True
            
            # 檢查索引是否已存在
            existing_indexes = list(self.collection.list_indexes())
            index_name = f"{field}_1"
            
            # 如果索引已存在，跳過建立
            if any(idx["name"] == index_name for idx in existing_indexes):
                logger.info(f"索引已存在，跳過建立: {self.collection_name}.{field}")
                return
            
            index_kwargs = {}
            if unique:
                index_kwargs["unique"] = True
            if expire_after_seconds is not None:
                index_kwargs["expireAfterSeconds"] = expire_after_seconds
                
            self.collection.create_index(field, **index_kwargs)
            logger.info(f"✅ {self.collection_name} 索引建立成功: {field}")
        except Exception as e:
            logger.error(f"❌ {self.collection_name} 索引建立失敗: {field} - {e}")
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        取得 collection 統計資訊
        
        Returns:
            統計資訊字典
        """
        try:
            self._ensure_initialized()
            total_count = self.count_documents()
            return {
                "collection_name": self.collection_name,
                "total_documents": total_count,
                "indexes": list(self.collection.list_indexes())
            }
        except Exception as e:
            self._log_error(f"取得統計資訊失敗", e)
            return {
                "collection_name": self.collection_name,
                "total_documents": 0,
                "indexes": []
            } 