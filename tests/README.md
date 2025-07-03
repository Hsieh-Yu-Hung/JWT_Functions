# Tests 目錄說明

本目錄包含 JWT Authentication 專案的所有測試檔案。

## 📁 檔案結構

```
tests/
├── README.md                    # 本說明文件
├── test_system.py              # 統一系統測試腳本
├── test_auth_routes.py         # 認證路由測試
├── test_jwt_middleware.py      # JWT 中間件測試
└── API_GUIDE.md                # 整合 API 指南
```

## 🧪 測試腳本

### 1. test_system.py - 統一系統測試

**功能**: 整合了所有系統測試功能，包括：
- API 配置測試
- API 端點測試
- 模型導入和實例化測試
- 檔案結構檢查
- 環境變數驗證
- JWT 功能測試

**使用方式**:
```bash
# 執行完整系統測試
python tests/test_system.py
```

**測試內容**:
1. 環境變數配置測試
2. API 配置測試
3. API 端點配置測試
4. 模型導入測試
5. 模型實例化測試
6. 檔案結構測試
7. JWT 功能測試

### 2. test_auth_routes.py - 認證路由測試

**功能**: 測試認證相關的 API 端點

**使用方式**:
```bash
# 執行認證路由測試
python tests/test_auth_routes.py
```

### 3. test_jwt_middleware.py - JWT 中間件測試

**功能**: 測試 JWT 中間件功能

**使用方式**:
```bash
# 執行 JWT 中間件測試
python tests/test_jwt_middleware.py
```

## 📚 文檔

### API_GUIDE.md - 整合 API 指南

**內容**: 整合了所有 API 相關資訊，包括：
- 認證 API 端點
- MongoDB Operation API 配置
- 系統測試方法
- 故障排除指南

## 🚀 快速開始

### 執行所有測試

```bash
# 執行完整系統測試（推薦）
python tests/test_system.py
```

### 執行特定測試

```bash
# 只測試認證路由
python tests/test_auth_routes.py

# 只測試 JWT 中間件
python tests/test_jwt_middleware.py
```

## 📊 測試結果

### 測試報告

所有測試完成後會生成詳細的測試報告，包含：
- 測試摘要（總數、通過、失敗、成功率）
- 失敗測試的詳細資訊
- JSON 格式的測試結果檔案

### 測試結果檔案

測試結果會保存為 JSON 檔案，格式如下：
```json
{
  "timestamp": "2024-01-01T12:00:00",
  "tests": [
    {
      "name": "測試名稱",
      "status": "PASS",
      "message": "測試訊息",
      "details": {}
    }
  ],
  "summary": {
    "total": 10,
    "passed": 9,
    "failed": 1
  }
}
```

## 🔧 故障排除

### 常見問題

1. **模組導入失敗**
   - 確保在專案根目錄執行測試
   - 檢查 Python 路徑設定

2. **環境變數未設定**
   - 檢查 `.env` 檔案是否存在
   - 確認所有必要的環境變數都已設定

3. **API 連接失敗**
   - 檢查 API 服務是否運行
   - 驗證 API 網址和金鑰

### 調試步驟

1. 執行系統測試腳本
2. 檢查測試結果摘要
3. 查看失敗測試的詳細資訊
4. 根據錯誤訊息進行調試

## 📝 注意事項

1. **測試環境**: 確保測試環境與生產環境配置一致
2. **資料庫**: 測試時使用測試資料庫，避免影響生產資料
3. **網路**: 確保網路連接正常，特別是 API 服務的連接
4. **權限**: 確保測試用戶有足夠的權限執行測試

## 🔗 相關文件

- [專案 README](../README.md) - 專案整體說明
- [API 指南](API_GUIDE.md) - 詳細的 API 使用指南
- [資料庫模組說明](../database/README.md) - 資料庫模組說明 