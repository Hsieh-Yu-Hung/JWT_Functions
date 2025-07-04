# JWT Authentication 測試指南

## 📋 概述

本目錄包含 JWT Authentication 專案的所有測試檔案和相關文檔。目前提供完整的端到端測試功能，確保系統的穩定性和可靠性。

## 📁 檔案結構

```
tests/
├── README.md                    # 本整合說明文件
└── test_complete_workflow.py   # 完整使用流程測試（主要測試）
```

## 🧪 測試腳本

### test_complete_workflow.py - 完整使用流程測試（推薦）

**功能**: 測試 JWT Authentication 系統的完整使用流程，包括：
- ✅ 健康檢查 (`/health`)
- ✅ 使用者註冊 (`/register`)
- ✅ 管理員註冊 (`/register`)
- ✅ 使用者登入 (`/login`)
- ✅ 管理員登入 (`/login`)
- ✅ 取得個人資料 (`/profile`)
- ✅ 更新個人資料 (`/profile`)
- ✅ 變更密碼 (`/change-password`)
- ✅ 帳戶切換 (`/switch-account`)
- ✅ 受保護端點測試
- ✅ 管理員功能測試
- ✅ 登出 (`/logout`)
- ✅ 錯誤處理測試

**使用方式**:
```bash
# 使用預設 API 網址執行測試
python tests/test_complete_workflow.py

# 使用自訂 API 網址執行測試
python tests/test_complete_workflow.py --url https://your-api-url.com

# 儲存測試結果到檔案
python tests/test_complete_workflow.py --save-results
```

**測試環境選擇**:
```bash
# 公網環境測試
python tests/test_complete_workflow.py --url https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run

# 內網環境測試
python tests/test_complete_workflow.py --url https://jwt-autunctions-ypvdbtxjmv.cn-shanghai-vpc.fcapp.run

# 本地環境測試
python tests/test_complete_workflow.py --url http://localhost:8000
```

## 🔐 API 端點參考

### 認證 API 端點

#### 用戶註冊
```http
POST /register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123",
  "username": "用戶名稱",
  "role": "user"
}
```

#### 用戶登入
```http
POST /login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

#### 用戶登出
```http
POST /logout
Authorization: Bearer <jwt_token>
```

#### 切換帳戶
```http
POST /switch-account
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "password123"
}
```

#### 用戶資料管理
```http
GET /profile                    # 取得用戶資料
PUT /profile                    # 更新用戶資料
POST /change-password           # 變更密碼
```

#### 管理員功能
```http
GET /admin/users               # 取得所有使用者
GET /admin/blacklist-stats     # 黑名單統計
POST /admin/cleanup-tokens     # 清理過期 token
```

### 環境變數設定

**⚠️ 重要**: 所有 API 相關的環境變數都是必需的。

```bash
# 公網 API 配置（必需）
PUBLIC_API_BASE_URL=https://api.example.com
PUBLIC_API_KEY=your_public_api_key_here

# 內網 API 配置（必需）
INTERNAL_API_BASE_URL=http://localhost:8000
INTERNAL_API_KEY=your_internal_api_key_here
```

## 📊 測試結果

### 測試輸出範例

```
🚀 開始執行完整使用流程測試
============================================================
測試目標: https://jwt-autunctions-ypvdbtxjmv.cn-shanghai.fcapp.run
測試時間: 2024-01-15 14:30:25
============================================================

✅ PASS 健康檢查
   服務正常運行

✅ PASS 註冊成功
   使用者 testuser_abc123@example.com 註冊成功

...

============================================================
📊 測試摘要
============================================================
總測試數: 26
通過: 20 ✅
失敗: 6 ❌
成功率: 76.9%
============================================================
```

### 測試結果檔案

測試完成後，會自動生成 JSON 格式的測試結果檔案：
```bash
# 檔案名稱格式：test_results_YYYYMMDD_HHMMSS.json
test_results_20240115_143025.json
```

## 🐛 故障排除

### 常見問題

1. **連接失敗**
   ```
   ❌ FAIL 健康檢查
      健康檢查失敗: 請求失敗: ConnectionError
   ```
   
   **解決方案：**
   - 檢查 API 網址是否正確
   - 確認網路連接正常
   - 檢查防火牆設定

2. **認證失敗**
   ```
   ❌ FAIL 使用者登入
      登入請求失敗: 請求失敗: 401 Unauthorized
   ```
   
   **解決方案：**
   - 確認測試使用者已正確註冊
   - 檢查密碼是否正確
   - 確認 API 端點路徑正確

3. **模組導入失敗**
   - 確保在專案根目錄執行測試
   - 檢查 Python 路徑設定

4. **環境變數未設定**
   - 檢查 `.env` 檔案是否存在
   - 確認所有必要的環境變數都已設定

### 調試步驟

1. 執行完整工作流程測試腳本
2. 檢查測試結果摘要
3. 查看失敗測試的詳細資訊
4. 根據錯誤訊息進行調試

## 📝 注意事項

1. **測試環境**: 確保測試環境與生產環境配置一致
2. **資料庫**: 測試時使用測試資料庫，避免影響生產資料
3. **網路**: 確保網路連接正常，特別是 API 服務的連接
4. **權限**: 確保測試用戶有足夠的權限執行測試
5. **測試資料**: 每次測試都會生成唯一的測試用戶，避免資料衝突

## 🔗 相關文件

- [專案 README](../README.md) - 專案整體說明
- [資料庫模組說明](../database/README.md) - 資料庫模組說明

---

*最後更新: 2025-01-15* 