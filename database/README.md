# Database 模組說明

本模組提供了 MongoDB 資料庫操作的基礎架構，包含一個通用的 `BaseModel` 類別和兩個具體的模型實作。

## 架構概覽

```
database/
├── __init__.py
├── base_model.py      # 通用基礎模型類別
├── blacklist_model.py # JWT Token 黑名單模型
├── role_model.py      # 使用者角色模型
├── database.py        # 資料庫連線管理
└── README.md          # 本文件
```

## BaseModel 基礎類別

`BaseModel` 是一個通用的 MongoDB 模型基礎類別，提供了完整的 CRUD 操作和索引管理功能。

### 主要功能

- **CRUD 操作**: 插入、查詢、更新、刪除文件
- **索引管理**: 自動建立和管理索引
- **錯誤處理**: 統一的錯誤處理和日誌記錄
- **統計資訊**: 取得 collection 統計資訊
- **批量操作**: 支援批量插入、更新、刪除

### 核心方法

#### 基本 CRUD 操作

```python
# 插入文件
insert_one(document: Dict[str, Any]) -> Optional[str]
insert_many(documents: List[Dict[str, Any]]) -> List[str]

# 查詢文件
find_one(filter_dict: Dict[str, Any], projection: Dict[str, Any] = None) -> Optional[Dict[str, Any]]
find_many(filter_dict: Dict[str, Any] = None, projection: Dict[str, Any] = None, 
          sort: List[tuple] = None, limit: int = None) -> List[Dict[str, Any]]

# 更新文件
update_one(filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> bool
update_many(filter_dict: Dict[str, Any], update_dict: Dict[str, Any]) -> int

# 刪除文件
delete_one(filter_dict: Dict[str, Any]) -> bool
delete_many(filter_dict: Dict[str, Any]) -> int
```

#### 輔助方法

```python
# 統計和檢查
count_documents(filter_dict: Dict[str, Any] = None) -> int
exists(filter_dict: Dict[str, Any]) -> bool

# 索引管理
create_index(field: str, unique: bool = False, expire_after_seconds: int = None)

# 統計資訊
get_collection_stats() -> Dict[str, Any]
```

#### 日誌方法

```python
_log_success(message: str)      # 記錄成功訊息
_log_error(message: str, error: Exception = None)  # 記錄錯誤訊息
_log_warning(message: str)      # 記錄警告訊息
```

## 如何建立新的資料模型

### 步驟 1: 建立新的模型類別

```python
from datetime import datetime, UTC
from database.base_model import BaseModel
from core.config import MONGODB_YOUR_COLLECTION  # 在 config.py 中定義

class YourModel(BaseModel):
    def __init__(self):
        super().__init__(MONGODB_YOUR_COLLECTION)
    
    def _create_indexes(self):
        """建立索引 - 必須實作此方法"""
        try:
            # 建立唯一索引
            self.create_index("unique_field", unique=True)
            
            # 建立普通索引
            self.create_index("search_field")
            
            # 建立 TTL 索引（自動過期）
            self.create_index("expires_at", expire_after_seconds=0)
            
        except Exception as e:
            self._log_error("索引建立失敗", e)
```

### 步驟 2: 實作業務邏輯方法

```python
class YourModel(BaseModel):
    # ... __init__ 和 _create_indexes 方法 ...
    
    def create_item(self, data: dict):
        """建立新項目"""
        try:
            item = {
                **data,
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC)
            }
            
            result_id = self.insert_one(item)
            if result_id:
                self._log_success(f"項目建立成功: {result_id}")
                return result_id
            else:
                raise Exception("插入失敗")
                
        except Exception as e:
            self._log_error("建立項目失敗", e)
            raise
    
    def get_item_by_id(self, item_id: str):
        """根據 ID 取得項目"""
        try:
            return self.find_one({"_id": item_id})
        except Exception as e:
            self._log_error("取得項目失敗", e)
            return None
    
    def update_item(self, item_id: str, update_data: dict):
        """更新項目"""
        try:
            update_data["updated_at"] = datetime.now(UTC)
            success = self.update_one({"_id": item_id}, update_data)
            
            if success:
                self._log_success(f"項目更新成功: {item_id}")
                return True
            else:
                self._log_warning(f"項目更新失敗（未找到記錄）: {item_id}")
                return False
                
        except Exception as e:
            self._log_error("更新項目失敗", e)
            return False
    
    def delete_item(self, item_id: str):
        """刪除項目"""
        try:
            success = self.delete_one({"_id": item_id})
            
            if success:
                self._log_success(f"項目刪除成功: {item_id}")
                return True
            else:
                self._log_warning(f"項目刪除失敗（未找到記錄）: {item_id}")
                return False
                
        except Exception as e:
            self._log_error("刪除項目失敗", e)
            return False
    
    def get_items_by_condition(self, condition: dict, limit: int = None):
        """根據條件查詢項目"""
        try:
            return self.find_many(
                filter_dict=condition,
                limit=limit
            )
        except Exception as e:
            self._log_error("查詢項目失敗", e)
            return []
```

### 步驟 3: 在 config.py 中定義 collection 名稱

```python
# core/config.py
MONGODB_YOUR_COLLECTION = "your_collection_name"
```

### 步驟 4: 在 database/__init__.py 中匯出

```python
# database/__init__.py
from .your_model import YourModel

__all__ = ['YourModel']
```

## 實際範例

### 範例 1: 使用者設定模型

```python
from datetime import datetime, UTC
from database.base_model import BaseModel
from core.config import MONGODB_USER_SETTINGS_COLLECTION

class UserSettingsModel(BaseModel):
    def __init__(self):
        super().__init__(MONGODB_USER_SETTINGS_COLLECTION)
    
    def _create_indexes(self):
        """建立索引"""
        try:
            self.create_index("user_id", unique=True)
            self.create_index("theme")
            self.create_index("language")
        except Exception as e:
            self._log_error("UserSettings 索引建立失敗", e)
    
    def get_user_settings(self, user_id: str):
        """取得使用者設定"""
        return self.find_one({"user_id": user_id})
    
    def update_user_settings(self, user_id: str, settings: dict):
        """更新使用者設定"""
        settings["updated_at"] = datetime.now(UTC)
        return self.update_one({"user_id": user_id}, settings)
```

### 範例 2: 系統日誌模型

```python
from datetime import datetime, UTC
from database.base_model import BaseModel
from core.config import MONGODB_SYSTEM_LOGS_COLLECTION

class SystemLogModel(BaseModel):
    def __init__(self):
        super().__init__(MONGODB_SYSTEM_LOGS_COLLECTION)
    
    def _create_indexes(self):
        """建立索引"""
        try:
            self.create_index("timestamp")
            self.create_index("level")
            self.create_index("module")
            # 自動清理 30 天前的日誌
            self.create_index("timestamp", expire_after_seconds=30*24*60*60)
        except Exception as e:
            self._log_error("SystemLog 索引建立失敗", e)
    
    def add_log(self, level: str, message: str, module: str = "system"):
        """新增系統日誌"""
        log_entry = {
            "level": level,
            "message": message,
            "module": module,
            "timestamp": datetime.now(UTC)
        }
        return self.insert_one(log_entry)
    
    def get_logs_by_level(self, level: str, limit: int = 100):
        """根據等級取得日誌"""
        return self.find_many(
            filter_dict={"level": level},
            sort=[("timestamp", -1)],
            limit=limit
        )
```

## 最佳實踐

### 1. 索引設計

- **唯一索引**: 用於確保資料唯一性（如 user_id）
- **查詢索引**: 用於經常查詢的欄位
- **TTL 索引**: 用於自動清理過期資料
- **複合索引**: 用於多欄位查詢

### 2. 錯誤處理

- 使用 `_log_error()` 記錄錯誤
- 使用 `_log_success()` 記錄成功操作
- 使用 `_log_warning()` 記錄警告訊息

### 3. 資料驗證

- 在插入前驗證資料格式
- 使用適當的資料類型
- 設定必要的欄位

### 4. 效能優化

- 合理使用索引
- 避免過大的查詢結果
- 使用投影減少傳輸資料量

## 注意事項

1. **必須實作 `_create_indexes()` 方法**: 這是抽象方法，子類別必須實作
2. **使用 UTC 時間**: 所有時間戳記都使用 UTC 時間
3. **錯誤處理**: 所有資料庫操作都應該有適當的錯誤處理
4. **日誌記錄**: 使用基礎類別提供的日誌方法記錄操作結果
5. **索引管理**: 在 `_create_indexes()` 中定義所有必要的索引

## 擴展功能

如果需要更進階的功能，可以考慮：

1. **資料驗證**: 使用 Pydantic 進行資料驗證
2. **快取機制**: 整合 Redis 快取
3. **分頁查詢**: 實作分頁功能
4. **聚合查詢**: 使用 MongoDB 聚合管道
5. **資料遷移**: 實作資料庫遷移功能 