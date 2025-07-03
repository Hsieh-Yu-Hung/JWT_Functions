# API 配置說明

## 概述

本專案已更新為使用 MongoDB Operation API 來進行資料庫操作，而不是直接連接 MongoDB。您可以透過環境變數來選擇使用公網或內網的 API 網址。

## 環境變數配置

**⚠️ 重要**: 所有 API 相關的環境變數都是必需的，如果未設定會導致應用程式啟動失敗並顯示相應的錯誤訊息。

### API 模式選擇（必需）

```bash
# 設定為 "public" 使用公網 API，設定為 "internal" 使用內網 API
API_MODE=internal
```

### 公網 API 配置（必需）

```bash
PUBLIC_API_BASE_URL=https://api.example.com
PUBLIC_API_KEY=your_public_api_key_here
```

### 內網 API 配置（必需）

```bash
INTERNAL_API_BASE_URL=http://localhost:8000
INTERNAL_API_KEY=your_internal_api_key_here
```

## 配置範例

### 使用內網 API（開發環境）

```bash
API_MODE=internal
INTERNAL_API_BASE_URL=http://localhost:8000
INTERNAL_API_KEY=dev_api_key_123
```

### 使用公網 API（生產環境）

```bash
API_MODE=public
PUBLIC_API_BASE_URL=https://api.production.com
PUBLIC_API_KEY=prod_api_key_456
```

## API 端點

系統會自動使用以下 API 端點：

- 用戶管理：`/api/users`
- 角色管理：`/api/roles`
- 用戶角色映射：`/api/user-roles`
- 黑名單管理：`/api/blacklist`

## 功能變更

### 新增功能

1. **API 管理器** (`database/api_manager.py`)
   - 統一的 API 請求處理
   - 自動錯誤處理和重試機制
   - 支援 Bearer Token 認證

2. **配置管理** (`core/config.py`)
   - 動態選擇 API 網址
   - 環境變數驅動的配置

### 更新的模型

所有資料庫模型都已更新為使用 API：

- `UserModel` - 用戶管理
- `RoleModel` - 角色管理
- `UserRoleMappingModel` - 用戶角色映射
- `BlacklistModel` - 黑名單管理

### 向後相容性

原有的 MongoDB 連接器仍然保留作為備用方案，您可以透過修改配置來切換回直接資料庫連接。

## 使用方式

### 基本使用

```python
from database import UserModel, RoleModel

# 創建用戶
user_model = UserModel()
user_id = user_model.register_user("user@example.com", "password123")

# 創建角色
role_model = RoleModel()
role_id = role_model.create_role("admin", "管理員角色", ["admin:read", "admin:write"])
```

### 檢查 API 狀態

```python
from database import api_manager

# 檢查 API 連接
try:
    stats = api_manager.get_blacklist_stats()
    print("API 連接正常")
except Exception as e:
    print(f"API 連接失敗: {e}")
```

## 注意事項

1. **API 金鑰**：確保設定正確的 API 金鑰以進行認證
2. **網路連接**：確保能夠連接到指定的 API 網址
3. **錯誤處理**：API 請求失敗時會拋出異常，請適當處理
4. **資料格式**：API 回應格式應符合預期，包含 `success` 和 `data` 欄位

## 故障排除

### 常見問題

1. **環境變數未設定錯誤**
   - 錯誤訊息: `ValueError: [變數名稱] environment variable is required. Please set it in your .env file`
   - 解決方案: 檢查 `.env` 檔案是否包含所有必需的 API 環境變數
   - 確保以下變數都已設定：
     - `API_MODE`
     - `PUBLIC_API_BASE_URL`
     - `PUBLIC_API_KEY`
     - `INTERNAL_API_BASE_URL`
     - `INTERNAL_API_KEY`

2. **API_MODE 值錯誤**
   - 錯誤訊息: `ValueError: API_MODE must be either 'internal' or 'public'. Please check your .env file`
   - 解決方案: 確保 `API_MODE` 設定為 `internal` 或 `public`（不區分大小寫）

3. **API 連接失敗**
   - 檢查 API 網址是否正確
   - 確認網路連接正常
   - 驗證 API 金鑰是否有效

4. **認證失敗**
   - 檢查 API 金鑰是否正確設定
   - 確認 API 金鑰有足夠的權限

5. **資料格式錯誤**
   - 確認 API 回應格式符合預期
   - 檢查 API 端點是否正確實作

### 切換回直接資料庫連接

如果需要切換回直接 MongoDB 連接，請：

1. 移除 API 相關的環境變數
2. 確保 MongoDB 環境變數正確設定
3. 重新實作模型類別以直接連接 MongoDB 