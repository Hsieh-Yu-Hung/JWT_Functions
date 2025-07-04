from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging
from core.config import (
    MONGO_URI, 
    DB_NAME, 
    MONGODB_MAX_POOL_SIZE, 
    MONGODB_MIN_POOL_SIZE
)

logger = logging.getLogger(__name__)

class MongoDBManager:
    def __init__(self):
        self.client = None
        self.db = None
        self._connected = False
    
    def _connect(self):
        """建立 MongoDB 連接"""
        if self._connected and self.client:
            return
            
        try:
            self.client = MongoClient(
                MONGO_URI,
                maxPoolSize=MONGODB_MAX_POOL_SIZE,
                minPoolSize=MONGODB_MIN_POOL_SIZE,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # 測試連接
            self.client.admin.command('ping')
            self.db = self.client[DB_NAME]
            self._connected = True
            
            logger.info("✅ MongoDB 連接成功")
            print("✅ MongoDB 連接成功")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"❌ MongoDB 連接失敗: {e}")
            print(f"❌ MongoDB 連接失敗: {e}")
            self._connected = False
            # 不拋出異常，讓應用程式可以繼續運行
            return
    
    def is_connected(self):
        """檢查是否已連接"""
        return self._connected and self.client is not None
    
    def connect(self):
        """手動連接資料庫"""
        if not self.is_connected():
            self._connect()
        return self.is_connected()
    
    def get_collection(self, collection_name):
        """取得指定的 collection"""
        if not self.is_connected():
            self.connect()
        if self.db is not None:
            return self.db[collection_name]
        else:
            raise ConnectionError("MongoDB 未連接")
    
    def close(self):
        """關閉資料庫連接"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("🔌 MongoDB 連接已關閉")
            print("🔌 MongoDB 連接已關閉")

# 全域資料庫管理器實例（延遲連接）
db_manager = MongoDBManager() 