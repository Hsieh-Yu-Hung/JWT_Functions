# JWT Authentication 專案說明

## 🆕 最新更新

本專案已整合 [jwt-auth-middleware](https://github.com/your-username/jwt-auth-middleware) 套件，提供更強大和標準化的 JWT 認證功能。

### 主要改進：
- ✅ 使用標準化的 JWT Auth Middleware 套件
- ✅ 自動 Token 黑名單管理
- ✅ 內建 Token 清理機制
- ✅ 更好的錯誤處理和日誌記錄
- ✅ 支援多種 JWT 演算法
- ✅ 管理員專用 JWT 管理端點

## 📁 專案目錄結構

```
JWT_Authentication/
├── .env                          # 環境變數檔案（從 env.example 複製）
├── app.py                        # 主應用程式入口
├── requirements.txt              # 依賴套件（包含 jwt-auth-middleware）
├── env.example                   # 環境變數範例檔案
├── README.md                     # 專案說明（本檔案）
├── core/                         # 核心功能模組
│   ├── __init__.py              # 模組初始化
│   ├── config.py                # 配置管理
│   └── jwt_utils.py             # JWT 工具函數（已整合到套件中）
├── database/                     # 資料庫相關
│   ├── __init__.py              # 模組初始化
│   ├── base_model.py            # 基礎模型類別
│   ├── database.py              # 資料庫連接管理
│   ├── blacklist_model.py       # Token 黑名單模型
│   ├── role_model.py            # 使用者角色模型
│   ├── user_model.py            # 使用者模型
│   └── README.md                # 資料庫模組說明
├── routes/                       # 路由模組
│   ├── __init__.py              # 模組初始化
│   └── auth_routes.py           # 認證路由（已整合新套件）
├── utils/                        # 工具模組
│   ├── __init__.py              # 模組初始化
│   └── token_cleanup_scheduler.py # Token 清理排程器（已整合新套件）
├── package/                      # JWT Auth Middleware 套件開發目錄
│   └── jwt_auth_middleware/     # 套件原始碼
└── generateSecret/               # 密鑰產生工具（保持原有）
    ├── generate_secret.py
    ├── quick_secret.py
    └── README.md
```

## 🎯 模組功能說明

### 🔐 JWT Auth Middleware 套件

- **JWTManager**: 核心 JWT 管理類別，提供 Token 建立、驗證、撤銷功能
- **token_required**: 裝飾器，用於保護需要認證的端點
- **自動黑名單管理**: 內建 Token 黑名單功能，支援自動清理
- **多演算法支援**: 支援 HS256、HS384、HS512 等 JWT 演算法
- **管理端點**: 提供 `/admin/jwt/*` 系列管理端點

### 📦 Core 模組

- **config.py**: 應用程式配置管理（JWT、MongoDB 連接、環境變數）
- **jwt_utils.py**: JWT 工具函數（已整合到 jwt-auth-middleware 套件中）

### 🗄️ Database 模組

- **base_model.py**: MongoDB 基礎模型類別，提供通用 CRUD 操作
- **database.py**: MongoDB 連接池與錯誤處理
- **blacklist_model.py**: Token 黑名單資料操作、TTL 索引、統計
- **role_model.py**: 角色權限管理、啟用/停用、權限驗證
- **user_model.py**: 使用者管理、註冊、登入、密碼驗證

### 🛣️ Routes 模組

- **auth_routes.py**: 認證路由（註冊、登入/登出、個人資料、帳戶切換、管理員功能）
- **新增 JWT 管理端點**: `/admin/jwt/blacklist`、`/admin/jwt/cleanup`

### 🛠️ Utils 模組

- **token_cleanup_scheduler.py**: Token 清理排程器（已整合 jwt-auth-middleware 套件）

### 🔑 GenerateSecret 模組

- **generate_secret.py**: 完整版密鑰產生器
- **quick_secret.py**: 快速密鑰產生器
- **README.md**: 使用說明

## 🗄️ MongoDB 資料結構

### Users Collection

```javascript
{
  "_id": ObjectId("..."),
  "email": "user@example.com",
  "password_hash": "pbkdf2:sha256:600000$...",
  "username": "myusername",
  "role": "user",
  "is_active": true,
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "updated_at": ISODate("2024-01-15T10:30:00Z"),
  "last_login": ISODate("2024-01-15T10:30:00Z")
}
```

### Blacklist Collection

```javascript
{
  "_id": ObjectId("..."),
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user_id": "user123@example.com",
  "revoked_at": ISODate("2024-01-15T10:30:00Z"),
  "expires_at": ISODate("2024-01-15T12:30:00Z"),
  "reason": "logout",
  "created_at": ISODate("2024-01-15T10:30:00Z")
}
```

### Role List Collection

```javascript
{
  "_id": ObjectId("..."),
  "user_id": "user123@example.com",
  "email": "user123@example.com",
  "roles": ["user", "admin"],
  "permissions": ["read", "write", "delete"],
  "is_active": true,
  "created_at": ISODate("2024-01-15T10:30:00Z"),
  "updated_at": ISODate("2024-01-15T10:30:00Z")
}
```

## 🌐 服務訪問地址

### 部署環境

- **內網地址**: https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run
- **公網地址**: https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai.fcapp.run

> **⚠️ 重要說明**:
>
> - 目前公網地址僅供測試使用，測試完成後將關閉
> - **未來所有訪問都將使用內網地址**
> - 請確保您的應用程式配置為使用內網地址進行生產環境部署

### 本地開發環境

- **本地地址**: http://localhost:5000

## 🛠️ 安裝與啟動

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

> **注意**: 本專案使用 `jwt-auth-middleware` 套件，會自動從 GitHub 安裝最新版本。

### 2. 設定環境變數

複製環境變數範例檔案：

```bash
cp env.example .env
```

編輯 `.env` 檔案，填入實際的配置值：

```bash
# JWT 設定
JWT_SECRET_KEY=your-super-secret-jwt-key-change-this-in-production
JWT_ALGORITHM=HS256
JWT_EXPIRE_HOURS=24

# 資料庫設定
MONGODB_URI=mongodb://localhost:27017/jwt_auth_db
MONGODB_DATABASE=jwt_auth_db

# 應用程式設定
FLASK_ENV=development
FLASK_DEBUG=True
PORT=9000

# 安全設定
CORS_ORIGINS=http://localhost:3000,http://localhost:8080
```

### 3. 啟動服務

#### 快速啟動（推薦）

**Linux/macOS:**
```bash
chmod +x quick_start.sh
./quick_start.sh
```

**Windows:**
```cmd
quick_start.bat
```

#### 手動啟動

```bash
# 本地開發
python app.py

# Docker 部署
docker build -t jwt-auth .
docker run -p 9000:9000 jwt-auth
```

### 4. 測試 JWT Auth Middleware 套件

```bash
# 確保服務正在運行
python test_jwt_middleware.py
```

## 🚀 完整使用流程

### 1. 使用者註冊

```bash
curl -X POST https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123",
    "username": "newuser",
    "role": "user"
  }'
```

**回應範例：**

```json
{
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011",
  "email": "newuser@example.com"
}
```

### 2. 使用者登入

```bash
curl -X POST https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "password123"
  }'
```

**回應範例：**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "newuser@example.com",
    "username": "newuser",
    "role": "user"
  }
}
```

### 3. 取得個人資料

```bash
curl -X GET https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**回應範例：**

```json
{
  "message": "Profile retrieved successfully",
  "profile": {
    "id": "507f1f77bcf86cd799439011",
    "email": "newuser@example.com",
    "username": "newuser",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-15T10:30:00Z",
    "last_login": "2024-01-15T10:30:00Z",
    "roles": ["user"],
    "permissions": ["read"]
  }
}
```

### 4. 更新個人資料

```bash
curl -X PUT https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/auth/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "updatedusername"
  }'
```

### 5. 變更密碼

```bash
curl -X POST https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/auth/change-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "old_password": "password123",
    "new_password": "newpassword123"
  }'
```

### 6. 帳戶切換

```bash
curl -X POST https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/auth/switch-account \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "adminpassword"
  }'
```

### 7. 登出

```bash
curl -X POST https://jwt-autunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/logout \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**回應範例：**

```json
{
  "message": "Logout successful",
  "note": "Token has been revoked and can no longer be used"
}
```

## 📡 API 端點總覽

### 使用者端點

- `POST /auth/register` - 使用者註冊
- `POST /auth/login` - 使用者登入
- `POST /auth/logout` - 使用者登出
- `POST /auth/switch-account` - 帳戶切換
- `GET /auth/profile` - 取得個人資料
- `PUT /auth/profile` - 更新個人資料
- `POST /auth/change-password` - 變更密碼

### 管理員端點

- `POST /auth/admin/cleanup-tokens` - 清理過期 token
- `GET /auth/admin/blacklist-stats` - 黑名單統計
- `GET /auth/admin/users` - 取得所有活躍使用者
- `PUT /auth/admin/users/<user_id>/roles` - 更新使用者角色
- `POST /auth/admin/users/<email>/deactivate` - 停用使用者

### 受保護端點

- `GET /protected` - 受保護的資源
- `GET /health` - 健康檢查

## 🔐 安全特性

### 密碼安全

- ✅ **密碼雜湊** - 使用 werkzeug.security 進行安全的密碼雜湊
- ✅ **密碼驗證** - 安全的密碼比對機制
- ✅ **密碼變更** - 支援舊密碼驗證的密碼變更

### Token 安全

- ✅ **JWT 驗證** - 完整的 JWT token 驗證機制
- ✅ **Token 撤銷** - 支援登出時撤銷 token
- ✅ **自動過期** - TTL 索引自動清理過期 token
- ✅ **黑名單機制** - 防止已撤銷 token 被重複使用

### 資料安全

- ✅ **權限控制** - 基於角色的權限管理
- ✅ **資料驗證** - 完整的輸入資料驗證
- ✅ **敏感資料保護** - 密碼雜湊等敏感資料不會在回應中返回

## 🗄️ 資料庫功能

### 自動功能

- ✅ **TTL 索引** - 自動清理過期 token
- ✅ **唯一索引** - 防止重複 email 和 token
- ✅ **連接池** - 優化資料庫連接
- ✅ **錯誤處理** - 完整的錯誤處理機制

### 手動功能

- ✅ **使用者管理** - 完整的註冊、登入、資料管理
- ✅ **角色管理** - 完整的使用者角色和權限管理
- ✅ **統計資訊** - 即時統計黑名單和使用者資訊
- ✅ **批量操作** - 支援批量更新和清理

## 🔧 配置選項

### MongoDB 連接配置

```python
# config.py
MONGODB_MAX_POOL_SIZE = 10  # 最大連接池大小
MONGODB_MIN_POOL_SIZE = 1   # 最小連接池大小
```

### JWT 配置

```python
# config.py
ACCESS_TOKEN_EXPIRE_MINUTES = 720  # Token 過期時間（分鐘）
ALGORITHM = "HS256"                # 簽署演算法
```

## 📊 監控與維護

### 1. 查看系統統計

```bash
curl -X GET https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/auth/admin/blacklist-stats \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### 2. 手動清理過期 token

```bash
curl -X POST https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/auth/admin/cleanup-tokens \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### 3. 查看所有使用者

```bash
curl -X GET https://jwt-autfunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run/auth/admin/users \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

## 🚀 效能優化

### 索引設計

- `email` - 唯一索引，快速查詢使用者
- `username` - 唯一索引，快速查詢使用者名稱
- `token` - 唯一索引，快速查詢 token
- `expires_at` - TTL 索引，自動清理過期資料
- `user_id` - 索引，快速查詢使用者相關資料
- `is_active` - 索引，快速篩選活躍使用者

### 連接池

- 自動管理資料庫連接
- 避免頻繁建立/關閉連接
- 提升查詢效能

## 🔒 安全性

### Token 安全

- ✅ 支援 token 撤銷
- ✅ 自動過期清理
- ✅ 角色權限驗證
- ✅ 安全的密鑰管理

### 資料庫安全

- ✅ 環境變數配置
- ✅ 連接加密
- ✅ 錯誤處理
- ✅ 權限控制

### 密碼安全

- ✅ 安全的密碼雜湊
- ✅ 密碼強度驗證
- ✅ 安全的密碼變更機制

## 📝 注意事項

1. **環境變數** - 確保所有必要的環境變數都已設定
2. **資料庫權限** - 確保 MongoDB 使用者有適當的讀寫權限
3. **網路連接** - 確保應用程式可以連接到 MongoDB
4. **密鑰安全** - 定期更換 SECRET_KEY
5. **備份** - 定期備份重要的使用者資料
6. **密碼政策** - 建議實作更嚴格的密碼政策

## 🐛 故障排除

### 常見問題

1. **MongoDB 連接失敗**

   - 檢查環境變數設定
   - 確認網路連接
   - 檢查使用者權限
2. **註冊失敗**

   - 檢查 email 格式
   - 確認密碼長度（最少 6 字元）
   - 檢查 email 是否已存在
3. **登入失敗**

   - 確認 email 和密碼正確
   - 檢查使用者是否已註冊
   - 確認使用者帳戶是否啟用
4. **Token 驗證失敗**

   - 檢查 token 是否過期
   - 確認使用者角色是否有效
   - 檢查 token 是否在黑名單中
5. **權限不足**

   - 確認使用者角色設定
   - 檢查權限配置
   - 確認管理員權限

## 📞 支援

如有問題，請檢查：

1. 應用程式日誌
2. MongoDB 連接狀態
3. 環境變數設定
4. 網路連接狀態
5. 使用者資料完整性

## 📋 模組依賴關係

```
app.py
├── routes.auth_routes
│   ├── core.jwt_utils
│   ├── database.user_model
│   └── database.role_model
├── middleware.jwt_middleware
│   └── core.jwt_utils
├── utils.token_cleanup_scheduler
│   └── core.jwt_utils
└── database.database
    └── core.config
```

## 🎯 擴展指南

### 新增功能模組

1. 在適當的目錄下建立新的 Python 檔案
2. 建立對應的 `__init__.py` 檔案
3. 更新相關模組的 import 路徑
4. 在主應用程式中引用新模組

### 新增路由

1. 在 `routes/` 目錄下建立新的路由檔案
2. 在 `app.py` 中註冊新的藍圖
3. 確保路由使用正確的 import 路徑

### 新增資料庫模型

1. 繼承 `database.base_model.BaseModel`
2. 實作 `_create_indexes()` 方法
3. 在 `database/__init__.py` 匯出新模型
4. 在其他模組中使用相對路徑引用

## 🔒 安全性考量

- 所有敏感配置都透過環境變數管理
- 資料庫連接使用連接池優化
- JWT token 支援撤銷和過期清理
- 完整的錯誤處理和日誌記錄
- 安全的密碼雜湊和驗證機制

## 📊 監控與維護

- 自動 token 清理機制
- 資料庫連接狀態監控
- 完整的統計資訊端點
- 管理員功能支援
- 使用者活動追蹤

這個模組化的結構讓專案更容易維護、擴展和測試！

---

# 阿里雲 Function Compute 部署指南

## 🚀 概述

本指南說明如何將 JWT 認證系統部署到阿里雲 Function Compute，實現無伺服器架構的認證服務。

## 📋 前置需求

### 1. 阿里雲帳號和認證

```bash
# 設定阿里雲認證
export ALIBABA_CLOUD_ACCESS_KEY_ID=your_access_key_id
export ALIBABA_CLOUD_ACCESS_KEY_SECRET=your_access_key_secret
```

### 2. 安裝必要工具

```bash
# 安裝 Aliyun CLI
npm install -g @alicloud/fun

# 安裝 Python 依賴
pip install -r requirements.txt
```

### 3. 阿里雲資源

- VPC 和 VSwitch
- 安全組
- MongoDB 實例（阿里雲 MongoDB 或自建）

## 🔧 配置調整

### 1. 更新 template.yml

```yaml
VpcConfig:
  VpcId: vpc-xxx        # 您的 VPC ID
  VSwitchIds:
    - vsw-xxx          # 您的 VSwitch ID
  SecurityGroupId: sg-xxx  # 您的安全組 ID
```

### 2. 設定環境變數

在 `template.yml` 中更新環境變數：

```yaml
EnvironmentVariables:
  SECRET_KEY: 'your-secret-key-here'
  DB_ACCOUNT: 'your_mongodb_username'
  DB_PASSWORD: 'your_mongodb_password'
  DB_URI: 'your-mongodb-host:port'
  DB_NAME: 'your_database_name'
```

## 🚀 部署步驟

### 1. 執行部署腳本

```bash
chmod +x deploy_to_fc.sh
./deploy_to_fc.sh
```

### 2. 手動部署（可選）

```bash
# 建立部署包
mkdir -p .fun
cp -r core database routes middleware utils .fun/
cp function_compute_adapter.py requirements.txt .fun/

# 安裝依賴
cd .fun
pip install -r requirements.txt -t .

# 部署
fun deploy --template template.yml
```

## 📡 API 端點

部署成功後，您可以使用以下端點：

### 基礎端點

- `GET /health` - 健康檢查
- `GET /protected` - 受保護資源

### 認證端點

- `POST /auth/register` - 使用者註冊
- `POST /auth/login` - 使用者登入
- `POST /auth/logout` - 使用者登出
- `GET /auth/profile` - 取得個人資料
- `PUT /auth/profile` - 更新個人資料
- `POST /auth/change-password` - 變更密碼
- `POST /auth/switch-account` - 帳戶切換

### 管理員端點

- `POST /auth/admin/cleanup-tokens` - 清理過期 token
- `GET /auth/admin/blacklist-stats` - 黑名單統計
- `GET /auth/admin/users` - 取得所有使用者
- `PUT /auth/admin/users/{user_id}/roles` - 更新使用者角色
- `POST /auth/admin/users/{email}/deactivate` - 停用使用者

## 🔧 配置選項

### Function Compute 配置

```yaml
Runtime: python3.9      # Python 運行時
Timeout: 30             # 超時時間（秒）
MemorySize: 512         # 記憶體大小（MB）
```

### 網路配置

- **VPC 配置**: 確保 Function Compute 可以訪問 MongoDB
- **安全組**: 開放必要的端口
- **CORS**: 支援跨域請求

## 📊 監控和日誌

### 1. 查看日誌

```bash
# 查看函數日誌
fun logs jwt-auth-service/jwt-auth-function

# 查看實時日誌
fun logs jwt-auth-service/jwt-auth-function --tail
```

### 2. 監控指標

- 函數執行次數
- 執行時間
- 錯誤率
- 記憶體使用量

## 🔒 安全性考量

### 1. 網路安全

- 使用 VPC 隔離網路
- 配置安全組規則
- 限制 MongoDB 訪問來源

### 2. 認證安全

- 使用強密碼
- 定期更換 SECRET_KEY
- 啟用 HTTPS

### 3. 資料安全

- 加密敏感資料
- 定期備份
- 監控異常訪問

## 🐛 故障排除

### 1. 部署失敗

```bash
# 檢查認證
fun config list

# 檢查模板語法
fun validate --template template.yml
```

### 2. 連接失敗

- 檢查 VPC 配置
- 確認 MongoDB 連接資訊
- 檢查安全組規則

### 3. 函數錯誤

```bash
# 查看錯誤日誌
fun logs jwt-auth-service/jwt-auth-function --tail

# 本地測試
python function_compute_adapter.py
```

## 💰 成本優化

### 1. 記憶體配置

- 根據實際需求調整記憶體大小
- 監控記憶體使用情況

### 2. 超時設定

- 設定合理的超時時間
- 避免不必要的長時間執行

### 3. 冷啟動優化

- 使用連接池
- 預熱函數
- 使用 Provisioned Concurrency

## 🔄 更新部署

### 1. 更新程式碼

```bash
# 修改程式碼後重新部署
./deploy_to_fc.sh
```

### 2. 更新配置

```bash
# 更新環境變數
fun deploy --template template.yml
```

## 📈 擴展建議

### 1. 自動擴展

- 配置自動擴展規則
- 監控負載情況

### 2. 多區域部署

- 在不同區域部署
- 使用 CDN 加速

### 3. 監控告警

- 設定監控告警
- 配置錯誤通知

## 🎯 最佳實踐

1. **環境變數管理**: 使用阿里雲 KMS 加密敏感資訊
2. **日誌管理**: 配置結構化日誌
3. **錯誤處理**: 實作完整的錯誤處理機制
4. **測試**: 建立完整的測試套件
5. **備份**: 定期備份重要資料

## 📞 支援

如有問題，請檢查：

1. 阿里雲 Function Compute 文檔
2. 專案日誌
3. 網路連接狀態
4. 環境變數設定

---

這個部署方案讓您的 JWT 認證系統可以在無伺服器環境中穩定運行！
