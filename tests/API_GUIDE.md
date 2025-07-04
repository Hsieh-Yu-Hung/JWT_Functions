# JWT Authentication API 完整指南

## 📋 概述

本指南整合了 JWT Authentication 專案的所有 API 相關資訊，包括：

- 認證 API 端點
- MongoDB Operation API 配置
- 系統測試方法
- 故障排除指南

## 🔗 基礎資訊

### 服務地址

- **開發環境**: `http://localhost:9000`
- **生產環境**: 根據部署配置

### API 架構

- **認證 API**: 提供用戶註冊、登入、登出等功能
- **MongoDB Operation API**: 處理所有資料庫操作
- **管理員 API**: 提供系統管理功能

## 🔐 認證 API 端點

### 用戶註冊

```http
POST /register
```

**請求體：**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "username": "用戶名稱",  // 可選
  "role": "user"          // 可選，預設為 "user"
}
```

**回應：**

```json
{
  "message": "User registered successfully",
  "user_id": "user_id_here",
  "email": "user@example.com"
}
```

### 用戶登入

```http
POST /login
```

**請求體：**

```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**回應：**

```json
{
  "access_token": "jwt_token_here",
  "user": {
    "id": "user_id",
    "email": "user@example.com",
    "username": "用戶名稱",
    "role": "user"
  }
}
```

### 用戶登出

```http
POST /logout
```

**請求頭：**

```
Authorization: Bearer <jwt_token>
```

**回應：**

```json
{
  "message": "Logout successful",
  "note": "Token has been revoked and can no longer be used"
}
```

### 切換帳戶

```http
POST /switch-account
```

**請求體：**

```json
{
  "email": "newuser@example.com",
  "password": "password123"
}
```

### 用戶資料管理

#### 取得用戶資料

```http
GET /profile
```

#### 更新用戶資料

```http
PUT /profile
```

#### 變更密碼

```http
POST /change-password
```

### 管理員功能

#### 統計資訊

```http
GET /admin/stats
```

#### JWT 管理

```http
GET /admin/jwt/blacklist
POST /admin/jwt/cleanup
```

## 🗄️ MongoDB Operation API 配置

### 環境變數設定

**⚠️ 重要**: 所有 API 相關的環境變數都是必需的。

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

### API 端點結構

MongoDB Operation API 使用以下端點模式：

- **新增**: `/add/document/{collection}`
- **查詢**: `/search/documents/{collection}` 或 `/search/document/{collection}/{id}`
- **更新**: `/update/document/{collection}/{id}`
- **刪除**: `/delete/document/{collection}/{id}`

### 集合配置

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

#### 健康檢查

```python
health_status = api_manager.health_check()
```

#### 集合管理

```python
collections = api_manager.get_collections()
count = api_manager.count_documents("users", {"is_active": True})
departments = api_manager.get_distinct_values("users", "department")
stats = api_manager.get_collection_stats("users", group_by="department")
```

#### 文件操作

```python
cloned_id = api_manager.clone_document("users", "original_id")
export_data = api_manager.export_document("users", "document_id")
export_data = api_manager.export_collection("users", {"is_active": True})
```

#### 批量操作

```python
response = api_manager.batch_create_documents("users", documents)
response = api_manager.batch_update_documents("users", query, update)
response = api_manager.batch_delete_documents("users", query)
```

## 🧪 系統測試

### 統一測試腳本

使用整合的測試腳本進行全面系統測試：

```bash
# 執行完整系統測試
python tests/test_system.py
```

### 測試內容

1. **環境變數配置測試**

   - 檢查必要環境變數是否設定
   - 驗證 API 模式配置
   - 檢查 API 網址格式
2. **API 配置測試**

   - 測試配置載入
   - API 健康檢查
   - 集合清單獲取
3. **API 端點測試**

   - 端點配置檢查
   - 具體端點訪問測試
4. **模型測試**

   - 模型導入測試
   - 模型實例化測試
5. **檔案結構測試**

   - 必要檔案存在檢查
   - 移除檔案確認
6. **JWT 功能測試**

   - JWT 管理器初始化
   - JWT 裝飾器導入

### 測試結果

測試完成後會生成詳細的測試報告，包含：

- 測試摘要（總數、通過、失敗、成功率）
- 失敗測試的詳細資訊
- JSON 格式的測試結果檔案

## 🔧 故障排除

### 常見問題

#### 1. 環境變數未設定錯誤

**錯誤訊息**: `ValueError: [變數名稱] environment variable is required`
**解決方案**:

- 檢查 `.env` 檔案是否包含所有必需的 API 環境變數
- 確保以下變數都已設定：
  - `API_MODE`
  - `PUBLIC_API_BASE_URL`
  - `PUBLIC_API_KEY`
  - `INTERNAL_API_BASE_URL`
  - `INTERNAL_API_KEY`

#### 2. API_MODE 值錯誤

**錯誤訊息**: `ValueError: API_MODE must be either 'internal' or 'public'`
**解決方案**: 確保 `config.yaml` 中的 `api.mode` 設定為 `internal` 或 `public`

#### 3. API 連接失敗

**解決方案**:

- 檢查 API 網址是否正確
- 確認網路連接正常
- 驗證 API 金鑰是否有效

#### 4. 認證失敗

**解決方案**:

- 檢查 API 金鑰是否正確設定
- 確認 API 金鑰有足夠的權限

#### 5. 資料格式錯誤

**解決方案**:

- 確認 API 回應格式符合預期
- 檢查 API 端點是否正確實作

### 調試步驟

1. **執行系統測試**

   ```bash
   python tests/test_system.py
   ```
2. **檢查配置**

   ```bash
   # 檢查 config.yaml 中的 API 模式設定
   cat config.yaml | grep -A 2 "api:"

   # 檢查環境變數
   echo $PUBLIC_API_BASE_URL
   echo $INTERNAL_API_BASE_URL
   ```
3. **檢查 API 服務狀態**

   ```python
   from database.api_manager import api_manager
   try:
       health = api_manager.health_check()
       print("API 服務正常")
   except Exception as e:
       print(f"API 服務異常: {e}")
   ```
4. **檢查日誌檔案**

   - 查看應用程式日誌
   - 檢查錯誤訊息

## 📚 相關文件

- [專案 README](../README.md) - 專案整體說明
- [資料庫模組說明](../database/README.md) - 資料庫模組詳細說明
- [API 配置說明](../core/API_CONFIG.md) - API 配置詳細說明

## 🆘 支援

如果遇到問題，請：

1. 執行系統測試腳本
2. 檢查環境變數配置
3. 查看錯誤日誌
4. 參考故障排除指南
5. 聯繫開發團隊
