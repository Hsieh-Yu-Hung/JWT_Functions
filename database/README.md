# Database 模組說明

本模組提供了統一的資料庫操作架構，透過 MongoDB Operation API 進行所有資料庫操作，支援公網和內網 API 的動態切換。

## 🆕 最新更新

本模組已更新為使用 API 架構，所有資料庫操作都透過統一的 API 管理器進行，不再直接連接 MongoDB。

### 主要改進：

- ✅ **API 驅動架構**: 所有操作透過 MongoDB Operation API 進行
- ✅ **統一 API 管理器**: 集中處理所有 API 請求
- ✅ **動態 API 切換**: 支援公網/內網 API 的環境變數切換
- ✅ **API 優先架構**: 完全基於 API 的資料庫操作
- ✅ **更好的錯誤處理**: 統一的 API 錯誤處理機制

## 架構概覽

```
database/
├── __init__.py                    # 模組初始化
├── api_manager.py                 # API 管理器（新增）
├── user_model.py                  # 用戶模型（已更新為使用 API）
├── role_model.py                  # 角色模型（已更新為使用 API）
├── user_role_mapping_model.py     # 用戶角色映射模型（已更新為使用 API）
├── blacklist_model.py             # 黑名單模型（已更新為使用 API）
# 基礎模型類別已移除（改為使用 API 架構）
├── api_manager.py                 # API 管理器
└── README.md                      # 本文件
```

## API 管理器 (APIManager)

`APIManager` 是統一的 API 請求處理器，負責與 MongoDB Operation API 進行通信。

### 主要功能

- **統一請求處理**: 所有 HTTP 請求的統一處理
- **自動錯誤處理**: 統一的錯誤處理和重試機制
- **Bearer Token 認證**: 支援 API 金鑰認證
- **會話管理**: 使用 requests.Session 提升效能
- **超時控制**: 自動請求超時處理

### 核心方法

#### 用戶相關操作

```python
# 用戶管理
create_user(user_data: Dict) -> Dict
get_user_by_id(user_id: str) -> Dict
get_user_by_username(username: str) -> Dict
update_user(user_id: str, user_data: Dict) -> Dict
delete_user(user_id: str) -> Dict
get_all_users(skip: int = 0, limit: int = 100) -> Dict
```

#### 角色相關操作

```python
# 角色管理
create_role(role_data: Dict) -> Dict
get_role_by_id(role_id: str) -> Dict
get_role_by_name(role_name: str) -> Dict
update_role(role_id: str, role_data: Dict) -> Dict
delete_role(role_id: str) -> Dict
get_all_roles(skip: int = 0, limit: int = 100) -> Dict
```

#### 用戶角色映射操作

```python
# 用戶角色映射
assign_role_to_user(user_id: str, role_id: str) -> Dict
remove_role_from_user(user_id: str, role_id: str) -> Dict
get_user_role_mapping(user_id: str) -> Dict
get_role_users(role_id: str) -> Dict
```

#### 黑名單操作

```python
# 黑名單管理
add_to_blacklist(token: str, expires_at: str) -> Dict
is_token_blacklisted(token: str) -> Dict
remove_from_blacklist(token: str) -> Dict
cleanup_expired_tokens() -> Dict
get_blacklist_stats() -> Dict
```

## 模型架構

### 1. UserModel - 用戶管理

使用 API 進行用戶相關操作，包含註冊、登入、資料更新等功能。

```python
from database import UserModel

# 創建用戶模型實例
user_model = UserModel()

# 註冊新用戶
user_id = user_model.register_user("user@example.com", "password123", "username")

# 用戶登入驗證
user_data = user_model.authenticate_user("user@example.com", "password123")

# 更新用戶資料
success = user_model.update_user_profile("user@example.com", {"username": "new_username"})

# 變更密碼
success = user_model.change_password("user@example.com", "old_password", "new_password")
```

### 2. RoleModel - 角色管理

管理系統角色和權限，支援角色繼承和權限驗證。

```python
from database import RoleModel

# 創建角色模型實例
role_model = RoleModel()

# 創建新角色
role_id = role_model.create_role("admin", "管理員角色", ["admin:read", "admin:write"])

# 取得角色權限
permissions = role_model.get_role_permissions("admin", include_inherited=True)

# 檢查權限
has_permission = role_model.check_role_permission("admin", "admin:read")

# 取得角色階層
hierarchy = role_model.get_role_hierarchy("admin")
```

### 3. UserRoleMappingModel - 用戶角色映射

管理用戶與角色的關聯關係。

```python
from database import UserRoleMappingModel

# 創建映射模型實例
mapping_model = UserRoleMappingModel()

# 為用戶指派角色
success = mapping_model.assign_role_to_user("user_id", "user@example.com", "admin")

# 取得用戶角色
user_role = mapping_model.get_user_role("user_id")

# 取得用戶權限
permissions = mapping_model.get_user_permissions("user_id")

# 檢查用戶權限
has_permission = mapping_model.check_user_permission("user_id", "admin:read")
```

### 4. BlacklistModel - 黑名單管理

管理 JWT Token 黑名單，支援自動清理過期 Token。

```python
from database import BlacklistModel

# 創建黑名單模型實例
blacklist_model = BlacklistModel()

# 將 Token 加入黑名單
blacklist_id = blacklist_model.add_to_blacklist("token_string", "user_id", expires_at, "logout")

# 檢查 Token 是否在黑名單中
is_blacklisted = blacklist_model.is_blacklisted("token_string")

# 取得黑名單統計
stats = blacklist_model.get_blacklist_stats()

# 清理過期 Token
cleaned_count = blacklist_model.cleanup_expired_tokens()
```

## 配置管理

### 環境變數設定

**⚠️ 重要**: 所有 API 相關的環境變數都是必需的，如果未設定會導致應用程式啟動失敗。

```bash
# API 模式選擇（現在在 config.yaml 中設定）
# 請修改 config.yaml 中的 api.mode 設定為 "internal" 或 "public"

# 公網 API 配置（必需）
PUBLIC_API_BASE_URL=https://api.example.com
PUBLIC_API_KEY=your_public_api_key_here

# 內網 API 配置（必需）
INTERNAL_API_BASE_URL=http://localhost:8000
INTERNAL_API_KEY=your_internal_api_key_here
```

### API 端點配置

API 端點配置直接管理在 `database/api_manager.py` 中，根據 MongoDB Operation API 的實際端點結構：

```python
# 新增端點
self.endpoints = {
    "users": "/add/document/users",
    "roles": "/add/document/roles", 
    "user_role_mapping": "/add/document/user_role_mapping",
    "blacklist": "/add/document/blacklist"
}

# 查詢端點
self.search_endpoints = {
    "users": "/search/documents/users",
    "roles": "/search/documents/roles",
    "user_role_mapping": "/search/documents/user_role_mapping", 
    "blacklist": "/search/documents/blacklist"
}

# 更新端點
self.update_endpoints = {
    "users": "/update/document/users",
    "roles": "/update/document/roles",
    "user_role_mapping": "/update/document/user_role_mapping",
    "blacklist": "/update/document/blacklist"
}

# 刪除端點
self.delete_endpoints = {
    "users": "/delete/document/users",
    "roles": "/delete/document/roles",
    "user_role_mapping": "/delete/document/user_role_mapping",
    "blacklist": "/delete/document/blacklist"
}
```

### 通用 API 操作

除了基本的 CRUD 操作外，API 管理器還提供以下通用功能：

```python
# 健康檢查
health_check() -> Dict

# 集合管理
get_collections() -> Dict
count_documents(collection: str, query: Optional[Dict] = None) -> Dict
get_distinct_values(collection: str, field: str, query: Optional[Dict] = None) -> Dict
get_collection_stats(collection: str, group_by: Optional[str] = None, query: Optional[Dict] = None) -> Dict

# 文件操作
clone_document(collection: str, document_id: str) -> Dict
export_document(collection: str, document_id: str) -> Dict
export_collection(collection: str, query: Optional[Dict] = None) -> Dict

# 批量操作
batch_create_documents(collection: str, documents: List[Dict]) -> Dict
batch_update_documents(collection: str, query: Dict, update: Dict) -> Dict
batch_delete_documents(collection: str, query: Dict) -> Dict

# 危險操作（謹慎使用）
drop_collection(collection: str) -> Dict
```

## 使用範例

### 基本使用

```python
from database import UserModel, RoleModel, UserRoleMappingModel, BlacklistModel

# 初始化模型
user_model = UserModel()
role_model = RoleModel()
mapping_model = UserRoleMappingModel()
blacklist_model = BlacklistModel()

# 創建用戶
user_id = user_model.register_user("admin@example.com", "admin123", "admin")

# 創建角色
role_id = role_model.create_role("admin", "系統管理員", ["admin:read", "admin:write"])

# 指派角色給用戶
mapping_model.assign_role_to_user(user_id, "admin@example.com", "admin")

# 檢查用戶權限
has_admin_permission = mapping_model.check_user_permission(user_id, "admin:read")
```

### 錯誤處理

```python
from database import UserModel

user_model = UserModel()

try:
    # 嘗試註冊用戶
    user_id = user_model.register_user("user@example.com", "password123")
    if user_id:
        print(f"用戶註冊成功: {user_id}")
    else:
        print("用戶註冊失敗")
except Exception as e:
    print(f"註冊過程發生錯誤: {e}")
```

### API 狀態檢查

```python
from database import api_manager

# 檢查 API 連接狀態
try:
    stats = api_manager.get_blacklist_stats()
    print("API 連接正常")
    print(f"黑名單統計: {stats}")
except Exception as e:
    print(f"API 連接失敗: {e}")
```

## 架構說明

本專案已完全遷移到 API 架構，不再支援直接 MongoDB 連接。所有資料庫操作都透過 MongoDB Operation API 進行，確保了更好的可擴展性和維護性。

## 最佳實踐

### 1. API 錯誤處理

- 所有 API 請求都應該有適當的錯誤處理
- 使用 try-catch 包裝 API 調用
- 記錄詳細的錯誤訊息

### 2. 資料驗證

- 在發送 API 請求前驗證資料格式
- 確保必要欄位存在
- 使用適當的資料類型

### 3. 效能優化

- 合理使用 API 請求
- 避免不必要的重複請求
- 使用適當的請求超時設定

### 4. 安全性

- 保護 API 金鑰
- 使用 HTTPS 進行 API 通信
- 定期更新 API 金鑰

## 故障排除

### 常見問題

1. **API 連接失敗**

   - 檢查 API 網址是否正確
   - 確認 API 服務是否運行
   - 驗證 API 金鑰是否有效
2. **認證失敗**

   - 檢查 API 金鑰是否正確設定
   - 確認 API 金鑰有足夠的權限
3. **資料格式錯誤**

   - 確認 API 回應格式符合預期
   - 檢查 API 端點是否正確實作

### 測試配置

執行以下命令進行系統測試：

```bash
# 執行完整系統測試（推薦）
python tests/test_system.py

# 執行特定測試
python tests/test_auth_routes.py    # 認證路由測試
python tests/test_jwt_middleware.py # JWT 中間件測試
```

## 擴展功能

### 自定義 API 端點

如果需要添加新的 API 端點，請在 `api_manager.py` 中添加相應的方法：

```python
def custom_operation(self, data: Dict) -> Dict:
    """自定義操作"""
    return self._make_request("POST", "/api/custom", data=data)
```

### 添加新的模型

1. 創建新的模型類別
2. 在 `api_manager.py` 中添加相應的 API 方法
3. 在 `database/__init__.py` 中匯出新模型
4. 更新配置檔案

## 注意事項

1. **API 依賴**: 確保 MongoDB Operation API 服務正常運行
2. **網路連接**: 確保能夠連接到指定的 API 網址
3. **錯誤處理**: API 請求失敗時會拋出異常，請適當處理
4. **資料格式**: API 回應格式應符合預期，包含 `success` 和 `data` 欄位
5. **環境變數**: 正確設定所有必要的環境變數

## 相關文件

- [API_CONFIG.md](../API_CONFIG.md) - 詳細的 API 配置說明
- [test_api_config.py](../test_api_config.py) - API 配置測試腳本
- [MongoDB Operation API](https://github.com/ACCUiNBio/MongoDB_Operation.git) - API 服務說明
