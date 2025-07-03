# JWT Functions 專案說明

## 🆕 最新更新

本專案已整合 [jwt-auth-middleware](https://github.com/Hsieh-Yu-Hung/JWT_Midware) 套件，提供更強大和標準化的 JWT 認證功能。

### 主要改進：

- ✅ 使用標準化的 JWT Auth Middleware 套件
- ✅ 自動 Token 黑名單管理
- ✅ 內建 Token 清理機制
- ✅ 更好的錯誤處理和日誌記錄
- ✅ 支援多種 JWT 演算法
- ✅ 管理員專用 JWT 管理端點

## 📁 專案目錄結構

```
JWT_Functions/
├── .env                          # 環境變數檔案（請聯繫專案管理員取得）
├── app.py                        # 主應用程式入口
├── requirements.txt              # 依賴套件（包含 jwt-auth-middleware）
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
├── utils/                        # Utils Functions 模組
│   ├── __init__.py              # 模組初始化
│   └── token_cleaner/           # JWT Token 清理 Function
│       ├── __init__.py          # 模組初始化
│       ├── cleanup_function.py  # 主要清理邏輯
│       ├── deploy_container.sh  # Shell 容器化部署腳本
│       ├── Dockerfile           # Docker 映像檔配置
│       ├── fc-config.json       # Function Compute 配置
│       ├── requirements.txt     # 依賴套件
│       ├── test_cleanup.py      # 測試腳本
│       └── README.md           # 詳細使用說明
├── scripts/                      # 部署腳本
│   ├── deploy.py                # Python 部署腳本
│   ├── deploy.sh                # Shell 部署腳本
│   ├── test_config.py           # 配置測試腳本
│   └── README.md               # 部署腳本說明
├── config/                       # 配置檔案
│   ├── fc-config.example.json   # Function Compute 配置範例
│   └── fc-config.json          # Function Compute 實際配置
├── package/                      # JWT Auth Middleware 套件開發目錄
│   └── jwt_auth_middleware/     # JWT middleware 套件專案
├── tests/                        # 測試檔案
│   ├── test_auth_routes.py      # 認證路由測試
│   ├── test_jwt_middleware.py   # JWT 中間件測試
│   └── API_DOCUMENTATION.md     # API 文件
├── generateSecret/               # 密鑰產生工具
│   ├── generate_secret.py       # 完整版密鑰產生器
│   ├── quick_secret.py          # 快速密鑰產生器
│   └── README.md               # 使用說明
├── Dockerfile                    # 主專案 Docker 配置
├── gunicorn.conf.py             # Gunicorn 配置
└── requirements.txt              # 主專案依賴套件
```

### 🔐 JWT Auth Middleware 套件

- **JWTManager**: 核心 JWT 管理類別，提供 Token 建立、驗證、撤銷功能
- **token_required**: 裝飾器，用於保護需要認證的端點
- **自動黑名單管理**: 內建 Token 黑名單功能
- **多演算法支援**: 支援 HS256演算法
- **管理端點**: 提供 `/admin/jwt/*` 系列管理端點

* JWT 中間件已製作成 python package, 發佈在 Github 上面
* 未來需要 JWT 驗證的專案可以安裝此套件, 使用其中驗證功能, 不用每個專案重複實作
* 連結 : [https://github.com/Hsieh-Yu-Hung/JWT_Midware.git](https://github.com/Hsieh-Yu-Hung/JWT_Midware.git)

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

### 🛠️ Utils Functions 模組

utils/ 底下是 utils Function，目前只有 token_cleaner 這個功能：

- **token_cleaner/**: JWT Token 清理 Function（適用於 Function Compute 環境）
  - **cleanup_function.py**: 主要清理邏輯
  - **deploy_container.sh**: Shell 容器化部署腳本
  - **Dockerfile**: Docker 映像檔配置
  - **fc-config.json**: Function Compute 配置檔案
  - **requirements.txt**: 依賴套件
  - **test_cleanup.py**: 測試腳本
  - **README.md**: 詳細使用說明

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

## 🚀 專案轉移

### 1. 複製專案

```bash
git clone git@github.com:Hsieh-Yu-Hung/JWT_Functions.git
cd JWT_Functions
```

### 2. 取得環境變數檔案

```bash
# 取得主專案的 .env 檔案，放在專案根目錄
# 請聯繫專案管理員取得 .env 檔案
```

### 3. 取得 Utils Functions 環境變數

```bash
# 取得各個 utils Function 的 .env.local 檔案
# 放在各個 utils Function 目錄底下

# 例如：utils/token_cleaner/.env.local
# 請聯繫專案管理員取得對應的 .env.local 檔案
```

### 4. 按照安裝與啟動流程安裝

請參考下方 [🛠️ 安裝與啟動](##🛠️安裝與啟動) 章節進行安裝。

### 5. Utils Functions 安裝與啟動

各個 utils Function 的安裝與啟動請參考各個 utils Function 的 README：

- **token_cleaner**: 請參考 `utils/token_cleaner/README.md`

## 🛠️安裝與啟動

### 1. 安裝依賴

```bash
pip install -r requirements.txt
```

> **注意**: 本專案使用 `jwt-auth-middleware` 套件，會自動從 GitHub 安裝最新版本。

### 2. 設定環境變數

編輯 `.env` 檔案，填入實際的配置值：

```bash
# MongoDB 登入
DB_ACCOUNT="資料庫帳戶"
DB_PASSWORD="資料庫密碼"
DB_URI="資料庫URI"
DB_NAME="資料庫名稱"

# 映像存放倉庫
ACR_USERNAME="ACR帳戶"
ACR_PASSWORD="ACR密碼"

# JWT 設定
JWT_SECRET_KEY="請生成JWT密碼或是繼承自此專案的"
```

### 3. 啟動服務

```bash
# Docker 部署到 Function Compute (自動化腳本)
bash scripts/deploy.sh
```

### 4. 測試 JWT Auth Middleware 套件

```bash
# 確保服務正在運行
python tests/test_jwt_middleware.py
```

## ⚠️ 部署注意事項

### 獨立部署架構

- **主專案和 utils Function 是獨立部署**
- 每個 utils Function 都有自己的部署配置和環境變數
- 主專案和 utils Function 可以分別更新和部署

### Utils Function 更新部署

- **若 utils Function 有更新要記得部署**
- 請參考各個 utils Function 的 README 進行部署
- 部署前請確認環境變數檔案（.env.local）已正確設定

### 部署檢查清單

#### 主專案部署

- [ ] 確認 `.env` 檔案已正確設定
- [ ] 確認 `config/fc-config.json` 配置正確
- [ ] 執行 `bash scripts/deploy.sh` 部署主專案

#### Utils Function 部署

- [ ] 確認 `utils/{function_name}/.env.local` 檔案已正確設定
- [ ] 確認 `utils/{function_name}/fc-config.json` 配置正確
- [ ] 參考對應的 README 進行部署

### 常見部署問題

1. **環境變數未設定**

   - 確認 `.env` 和 `.env.local` 檔案存在且內容正確
   - 檢查環境變數名稱是否與程式碼一致
2. **配置檔案錯誤**

   - 確認 `fc-config.json` 格式正確
   - 檢查 ACR 認證資訊是否正確
3. **部署權限問題**

   - 確認阿里雲 CLI 認證已正確設定
   - 檢查 Function Compute 服務權限

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
curl -X PUT https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run/profile \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "updatedusername"
  }'
```

### 5. 變更密碼

```bash
curl -X POST https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run/change-password \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "old_password": "password123",
    "new_password": "newpassword123"
  }'
```

### 6. 帳戶切換

```bash
curl -X POST https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run/switch-account \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "adminpassword"
  }'
```

### 7. 登出

```bash
curl -X POST https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run/logout \
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

- `POST /register` - 使用者註冊
- `POST /login` - 使用者登入
- `POST /logout` - 使用者登出
- `POST /switch-account` - 帳戶切換
- `GET /profile` - 取得個人資料
- `PUT /profile` - 更新個人資料
- `POST /change-password` - 變更密碼

### 管理員端點

- `POST /admin/cleanup-tokens` - 清理過期 token
- `GET /admin/blacklist-stats` - 黑名單統計
- `GET /admin/users` - 取得所有活躍使用者
- `PUT /admin/users/<user_id>/roles` - 更新使用者角色
- `POST /admin/users/<email>/deactivate` - 停用使用者

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

## 🧹 JWT Token 清理功能

### 背景說明

在阿里雲 Function Compute 的 Web Function 環境中，由於函數是事件驅動的，無法維持長時間運行的背景執行緒來進行定期清理。為了解決這個問題，我們提供了獨立的 **JWT Token 清理 Function**。

### 功能特色

- ✅ **獨立部署**: 與主服務分離，不影響主服務性能
- ✅ **定時觸發**: 支援 Cron 表達式設定執行頻率
- ✅ **記憶體優化**: 自動清理過期 Token，節省記憶體使用
- ✅ **詳細統計**: 提供清理結果和記憶體使用統計
- ✅ **自動化部署**: 提供 Python 和 Shell 兩種部署腳本

### 快速部署

#### 1. 環境準備

```bash
# 安裝阿里雲 CLI
pip install aliyun-cli

# 設定環境變數（在 .env 檔案中）
JWT_SECRET_KEY="your-jwt-secret-key"
ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key-id"
ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-access-key-secret"
ALIBABA_CLOUD_REGION="cn-shanghai"
```

#### 2. 部署清理 Function

```bash
# 使用 Shell 腳本（推薦）
./utils/token_cleaner/deploy_container.sh

# 自訂執行頻率
./utils/token_cleaner/deploy_container.sh --cron "0 0 0 * * *"  # 每天午夜執行
./utils/token_cleaner/deploy_container.sh --cron "0 */30 * * * *"  # 每30分鐘執行
```

```

#### 3. 驗證部署

部署完成後，您可以在阿里雲控制台查看：

- **Function Compute 控制台**: 查看服務和 Function 狀態
- **日誌服務**: 查看執行日誌和清理結果
- **監控服務**: 查看執行時間和記憶體使用情況

### 常用 Cron 表達式

| 表達式             | 說明             |
| ------------------ | ---------------- |
| `0 0 * * * *`    | 每小時執行一次   |
| `0 0 0 * * *`    | 每天午夜執行     |
| `0 0 12 * * *`   | 每天中午執行     |
| `0 */30 * * * *` | 每30分鐘執行一次 |
| `0 0 */2 * * *`  | 每2小時執行一次  |

### 監控和維護

```bash
# 查看執行日誌
aliyun fc get-function-logs \
  --service-name jwt-token-cleaner \
  --function-name cleanup \
  --limit 10

# 手動觸發清理
aliyun fc invoke-function \
  --service-name jwt-token-cleaner \
  --function-name cleanup

# 重新部署
./utils/token_cleaner/deploy_container.sh
```

### 詳細文件

更多詳細資訊請參考：[utils/token_cleaner/README.md](utils/token_cleaner/README.md)

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

- 手動 token 清理端點 (`/admin/jwt/cleanup`)
- 獨立的 token 清理 Function (`utils/token_cleaner/`)
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

## 🔧 配置管理

### 1. 配置檔案結構

本專案使用 JSON 配置檔案管理 Function Compute 部署設定：

```
config/
├── fc-config.json          # 實際配置檔案
└── fc-config.example.json  # 配置檔案範例
```

### 2. 設定配置檔案

複製範例配置檔案並修改：

```bash
cp config/fc-config.example.json config/fc-config.json
```

編輯 `config/fc-config.json`，填入您的實際配置：

```json
{
  "function": {
    "name": "jwt-auth-functions",
    "runtime": "custom-container",
    "handler": "index.handler",
    "timeout": 60,
    "memorySize": 4096
  },
  "acr": {
    "domain": "your-acr-domain.your-region.personal.cr.aliyuncs.com",
    "namespace": "your-namespace",
    "imageName": "jwt-functions",
    "imageVersion": "latest"
  },
  "region": "cn-shanghai"
}
```

### 3. 配置檔案說明

#### function 區段

- `name`: 函數名稱
- `runtime`: 運行時（custom-container）
- `handler`: 處理器
- `timeout`: 超時時間（秒）
- `memorySize`: 記憶體大小（MB）
- `cpu`: CPU 核心數
- `diskSize`: 磁碟大小（MB）

#### container 區段

- `image`: 容器映像檔完整路徑
- `port`: 容器端口
- `command`: 啟動命令（可選）
- `entrypoint`: 進入點（可選）

#### vpc 區段

- `vpcId`: VPC ID
- `vSwitchIds`: VSwitch ID 列表
- `securityGroupId`: 安全組 ID

#### acr 區段

- `domain`: ACR 域名
- `namespace`: 命名空間
- `imageName`: 映像檔名稱
- `imageVersion`: 映像檔版本

## 🚀 部署流程

### 1. 使用新的部署工具（推薦）

```bash
# 完整部署
./scripts/deploy.sh

# 跳過 Docker 建構
./scripts/deploy.sh --skip-build

# 驗證配置檔案
./scripts/deploy.sh --validate

# 顯示部署狀態
./scripts/deploy.sh --status

# 模擬執行
./scripts/deploy.sh --dry-run
```

### 2. 直接使用 Python 腳本

```bash
# 完整部署
python3 scripts/deploy.py

# 使用自訂配置檔案
python3 scripts/deploy.py --config config/my-config.json

# 跳過建構
python3 scripts/deploy.py --skip-build
```

### 3. 部署流程說明

1. **驗證配置** - 檢查配置檔案格式和必要欄位
2. **檢查環境** - 驗證必要工具和環境變數
3. **登入 ACR** - 使用認證資訊登入容器倉庫
4. **建構映像檔** - 執行 Docker build
5. **標籤映像檔** - 為映像檔打上 ACR 標籤
6. **推送映像檔** - 將映像檔推送到 ACR
7. **更新函數** - 更新 Function Compute 服務

## 🔧 配置調整

### 1. 環境變數設定

確保 `.env` 檔案包含必要的認證資訊：

```bash
# ACR 認證
ACR_USERNAME="your-acr-username"
ACR_PASSWORD="your-acr-password"

# MongoDB 連接
DB_ACCOUNT="your_mongodb_username"
DB_PASSWORD="your_mongodb_password"
DB_URI="your-mongodb-host:port"
DB_NAME="your_database_name"

# JWT 設定
JWT_SECRET_KEY="your-secret-key-here"
```

### 2. 驗證配置

在部署前驗證配置檔案：

```bash
./scripts/deploy.sh --validate
```

## 🚀 部署步驟

### 1. 執行部署腳本

```bash
# 設定執行權限
chmod +x scripts/deploy.sh

# 完整部署
./scripts/deploy.sh
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

- `POST /register` - 使用者註冊
- `POST /login` - 使用者登入
- `POST /logout` - 使用者登出
- `GET /profile` - 取得個人資料
- `PUT /profile` - 更新個人資料
- `POST /change-password` - 變更密碼
- `POST /switch-account` - 帳戶切換

### 管理員端點

- `POST /admin/cleanup-tokens` - 清理過期 token
- `GET /admin/blacklist-stats` - 黑名單統計
- `GET /admin/users` - 取得所有使用者
- `PUT /admin/users/{user_id}/roles` - 更新使用者角色
- `POST /admin/users/{email}/deactivate` - 停用使用者

## 🔧 配置選項

### Function Compute 配置

在 `config/fc-config.json` 中調整以下設定：

```json
{
  "function": {
    "timeout": 60,           // 超時時間（秒）
    "memorySize": 4096,      // 記憶體大小（MB）
    "cpu": 4,               // CPU 核心數
    "diskSize": 512,        // 磁碟大小（MB）
    "instanceConcurrency": 10  // 實例並發數
  }
}
```

### 網路配置

- **VPC 配置**: 在 `vpc` 區段設定 VPC ID、VSwitch ID 和安全組
- **容器配置**: 在 `container` 區段設定端口和啟動參數
- **CORS**: 支援跨域請求

### 日誌配置

在 `log` 區段設定日誌相關配置：

```json
{
  "log": {
    "project": "your-log-project",
    "logstore": "default-logs",
    "enableRequestMetrics": true,
    "enableInstanceMetrics": true
  }
}
```

## 📊 監控和日誌

### 1. 查看日誌

```bash
# 查看函數日誌
aliyun fc GetFunctionLogs --region cn-shanghai --functionName jwt-auth-functions

# 查看實時日誌
aliyun fc GetFunctionLogs --region cn-shanghai --functionName jwt-auth-functions --tail

# 使用配置檔案中的函數名稱
aliyun fc GetFunctionLogs --region $(jq -r '.region' config/fc-config.json) --functionName $(jq -r '.function.name' config/fc-config.json)
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
aliyun configure list

# 驗證配置檔案
./scripts/deploy.sh --validate

# 檢查環境變數
cat .env | grep -E "(ACR_USERNAME|ACR_PASSWORD)"

# 檢查配置檔案格式
python3 -m json.tool config/fc-config.json
```

### 2. 連接失敗

- 檢查 VPC 配置
- 確認 MongoDB 連接資訊
- 檢查安全組規則

### 3. 函數錯誤

```bash
# 查看錯誤日誌
aliyun fc GetFunctionLogs --region cn-shanghai --functionName jwt-auth-functions --tail

# 本地測試
python function_compute_adapter.py

# 檢查函數狀態
aliyun fc GetFunction --region cn-shanghai --functionName jwt-auth-functions
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
./scripts/deploy.sh

# 僅更新函數配置（跳過 Docker 建構）
./scripts/deploy.sh --skip-build
```

### 2. 更新配置

```bash
# 編輯配置檔案
vim config/fc-config.json

# 驗證配置
./scripts/deploy.sh --validate

# 重新部署
./scripts/deploy.sh
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

1. **配置管理**: 使用 JSON 配置檔案管理部署設定
2. **環境變數管理**: 使用阿里雲 KMS 加密敏感資訊
3. **日誌管理**: 配置結構化日誌
4. **錯誤處理**: 實作完整的錯誤處理機制
5. **測試**: 建立完整的測試套件
6. **備份**: 定期備份重要資料
7. **版本控制**: 使用語義化版本號管理映像檔
8. **部署驗證**: 部署前驗證配置檔案格式

## 📞 支援

如有問題，請檢查：

1. 阿里雲 Function Compute 文檔
2. 專案日誌
3. 網路連接狀態
4. 環境變數設定
5. 配置檔案格式
6. 部署腳本說明：`cat scripts/README.md`
