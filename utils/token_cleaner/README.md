# JWT Token Cleaner

JWT Token 清理 Function，專為阿里雲 Function Compute 環境設計的獨立清理服務。

## 🎯 功能特色

- ✅ **獨立部署**: 與主服務分離，不影響主服務性能
- ✅ **定時觸發**: 支援 Cron 表達式設定執行頻率
- ✅ **記憶體優化**: 自動清理過期 Token，節省記憶體使用
- ✅ **詳細統計**: 提供清理結果和記憶體使用統計
- ✅ **錯誤處理**: 完善的錯誤處理和日誌記錄
- ✅ **自動化部署**: 提供 Python 和 Shell 兩種部署腳本
- ✅ **容器化支援**: 支援 Docker 容器化部署，更穩定可靠

## 📁 目錄結構

```
utils/token_cleaner/
├── __init__.py              # 模組初始化
├── cleanup_function.py      # 主要清理邏輯
├── deploy_container.py     # Python 容器化部署腳本
├── deploy_container.sh     # Shell 容器化部署腳本（推薦）
├── Dockerfile              # Docker 建構檔案
├── requirements.txt        # Python 依賴套件
├── fc-config.json         # Function Compute 配置檔案
├── .dockerignore          # Docker 忽略檔案
├── test_container.py      # 容器化部署測試腳本
└── README.md              # 說明文件
```

## 🚀 快速開始

### 1. 環境準備

確保已安裝以下依賴：

```bash
# 安裝阿里雲 CLI
pip install aliyun-cli

# 安裝 Docker（容器化部署需要）
# https://docs.docker.com/get-docker/

# 或使用官方安裝方式
# https://help.aliyun.com/document_detail/121541.html
```

### 2. 環境變數設定

在 `.env` 檔案中設定必要的環境變數：

```bash
# JWT 設定
JWT_SECRET_KEY="your-jwt-secret-key"

# 阿里雲認證
ALIBABA_CLOUD_ACCESS_KEY_ID="your-access-key-id"
ALIBABA_CLOUD_ACCESS_KEY_SECRET="your-access-key-secret"
ALIBABA_CLOUD_REGION="cn-shanghai"

# ACR 認證（容器化部署需要）
ACR_USERNAME="your-acr-username"
ACR_PASSWORD="your-acr-password"

# 資料庫設定（可選）
DB_ACCOUNT="your-db-account"
DB_PASSWORD="your-db-password"
DB_URI="your-db-uri"
DB_NAME="your-db-name"
```

### 3. 部署方式

#### 方式一：容器化部署（推薦）

```bash
# 使用 Shell 腳本（推薦）
./utils/token_cleaner/deploy_container.sh

# 自訂執行頻率
./utils/token_cleaner/deploy_container.sh --cron "0 0 0 * * *"  # 每天午夜執行
./utils/token_cleaner/deploy_container.sh --cron "0 */30 * * * *"  # 每30分鐘執行

# 跳過 Docker 建構（僅更新 Function）
./utils/token_cleaner/deploy_container.sh --skip-build

# 查看幫助
./utils/token_cleaner/deploy_container.sh --help
```

#### 方式二：使用 Python 腳本

```bash
# 容器化部署
python utils/token_cleaner/deploy_container.py

# 僅執行本地測試
python utils/token_cleaner/test_container.py
```

### 4. 驗證部署

部署完成後，您可以在阿里雲控制台查看：

- **Function Compute 控制台**: 查看服務和 Function 狀態
- **日誌服務**: 查看執行日誌和清理結果
- **監控服務**: 查看執行時間和記憶體使用情況

## ⏰ Cron 表達式說明

### 基本格式

```
秒 分 時 日 月 週
```

### 常用範例

| 表達式             | 說明             |
| ------------------ | ---------------- |
| `0 0 * * * *`    | 每小時執行一次   |
| `0 0 0 * * *`    | 每天午夜執行     |
| `0 0 12 * * *`   | 每天中午執行     |
| `0 */30 * * * *` | 每30分鐘執行一次 |
| `0 0 */2 * * *`  | 每2小時執行一次  |
| `0 0 0 * * 1`    | 每週一午夜執行   |

### 自訂頻率建議

- **高頻率系統**: `0 */15 * * * *` (每15分鐘)
- **一般系統**: `0 0 * * * *` (每小時)
- **低頻率系統**: `0 0 0 * * *` (每天)

## 📊 功能詳解

### 清理邏輯

1. **初始化檢查**: 驗證環境變數和 JWT Manager
2. **資料庫連接**: 嘗試連接 MongoDB（可選）
3. **執行清理**: 調用 JWT Manager 的清理方法
4. **統計計算**: 計算清理結果和記憶體節省
5. **日誌記錄**: 記錄詳細的執行結果

### 回應格式

成功回應：

```json
{
  "status": "success",
  "message": "成功清理 15 個過期 token",
  "data": {
    "success": true,
    "cleaned_count": 15,
    "remaining_tokens": 42,
    "estimated_memory_usage": 21000,
    "memory_saved_bytes": 7500,
    "memory_saved_mb": 0.01,
    "timestamp": "2024-01-15T10:30:00Z",
    "execution_time": "2024-01-15 10:30:00"
  }
}
```

錯誤回應：

```json
{
  "status": "error",
  "message": "清理過程發生錯誤",
  "error": "具體錯誤訊息",
  "data": {
    "success": false,
    "error": "具體錯誤訊息",
    "cleaned_count": 0,
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## 🔧 配置選項

### Function 配置

- **記憶體**: 128MB（足夠清理使用）
- **超時時間**: 60秒
- **運行時**: Python 3.9
- **處理器**: `cleanup_function.handler`

### 環境變數

| 變數名稱                            | 必填 | 說明                     |
| ----------------------------------- | ---- | ------------------------ |
| `JWT_SECRET_KEY`                  | ✅   | JWT 密鑰                 |
| `ALIBABA_CLOUD_ACCESS_KEY_ID`     | ✅   | 阿里雲 Access Key ID     |
| `ALIBABA_CLOUD_ACCESS_KEY_SECRET` | ✅   | 阿里雲 Access Key Secret |
| `ALIBABA_CLOUD_REGION`            | ✅   | 阿里雲區域               |
| `DB_ACCOUNT`                      | ❌   | 資料庫帳戶               |
| `DB_PASSWORD`                     | ❌   | 資料庫密碼               |
| `DB_URI`                          | ❌   | 資料庫 URI               |
| `DB_NAME`                         | ❌   | 資料庫名稱               |

## 🛠️ 本地測試

### 容器化部署測試

```bash
cd utils/token_cleaner
python test_container.py
```

### 直接執行清理功能

```bash
cd utils/token_cleaner
python cleanup_function.py
```

### 單元測試

```bash
# 測試清理功能
python -c "
from cleanup_function import cleanup_tokens
result = cleanup_tokens()
print('清理結果:', result)
"
```

## 📈 監控和維護

### 日誌查看

```bash
# 使用阿里雲 CLI 查看日誌
aliyun fc get-function-logs \
  --service-name jwt-token-cleaner \
  --function-name cleanup \
  --limit 10
```

### 手動觸發

```bash
# 手動觸發清理
aliyun fc invoke-function \
  --service-name jwt-token-cleaner \
  --function-name cleanup
```

### 更新部署

```bash
# 重新部署（會自動更新）
./utils/token_cleaner/deploy_container.sh
```

## 🔍 故障排除

### 常見問題

1. **部署失敗**

   - 檢查阿里雲 CLI 是否正確安裝
   - 確認環境變數是否設定正確
   - 檢查網路連接
2. **清理失敗**

   - 檢查 JWT_SECRET_KEY 是否正確
   - 確認資料庫連接是否正常
   - 查看 Function 執行日誌
3. **觸發器不工作**

   - 檢查 Cron 表達式格式
   - 確認觸發器是否正確建立
   - 查看觸發器狀態

### 日誌分析

```bash
# 查看最近的執行日誌
aliyun fc get-function-logs \
  --service-name jwt-token-cleaner \
  --function-name cleanup \
  --limit 20
```

## 🐳 容器化部署詳解

### 容器化部署優勢

1. **環境一致性**: 確保開發、測試、生產環境的一致性
2. **依賴管理**: 所有依賴都打包在容器中，避免環境差異
3. **版本控制**: 映像檔版本化管理，便於回滾和追蹤
4. **安全性**: 容器隔離，提高安全性
5. **可移植性**: 可在不同環境中輕鬆部署

### Docker 映像檔資訊

- **基礎映像檔**: `python:3.9-slim`
- **工作目錄**: `/app`
- **暴露端口**: `9000`
- **健康檢查**: 每30秒檢查一次
- **非 root 使用者**: 提高安全性

### ACR 存放區配置

```bash
# 存放區域名
crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com

# 命名空間
accuin-bio

# 映像檔名稱
jwt-token-cleaner

# 版本標籤
latest
```

### 手動 Docker 操作

```bash
# 登入 ACR
docker login --username=<登錄賬號> crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com

# 建構映像檔
docker build -t jwt-token-cleaner:latest .

# 標籤映像檔
docker tag jwt-token-cleaner:latest crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com/accuin-bio/jwt-token-cleaner:latest

# 推送映像檔
docker push crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com/accuin-bio/jwt-token-cleaner:latest

# 拉取映像檔
docker pull crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com/accuin-bio/jwt-token-cleaner:latest
```

## 📝 更新日誌

### v1.1.0 (2024-01-15)

- ✅ 新增容器化部署支援
- ✅ 新增 Docker 建構檔案和配置
- ✅ 新增 ACR 推送功能
- ✅ 優化部署腳本和文檔

### v1.0.0 (2024-01-15)

- ✅ 初始版本發布
- ✅ 支援基本清理功能
- ✅ 提供自動化部署腳本
- ✅ 支援定時觸發器
- ✅ 完整的錯誤處理和日誌記錄

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request 來改進這個專案。

## 📄 授權

本專案採用 MIT 授權條款。

# JWT Token Cleaner 容器化部署

這個目錄包含了 JWT Token Cleaner 的容器化部署腳本和相關配置。

## 檔案結構

```
utils/token_cleaner/
├── deploy_container.sh    # 主要部署腳本
├── fc-config.json        # Function Compute 配置檔案
├── cleanup_function.py   # 清理函數實作
├── Dockerfile           # Docker 映像檔配置
├── requirements.txt     # Python 依賴
└── README.md           # 本檔案
```

## 配置檔案

`fc-config.json` 包含了所有 Function Compute 的配置：

```json
{
  "function": {
    "name": "jwt-token-cleaner",
    "description": "JWT Token 定期清理服務",
    "runtime": "custom-container",
    "handler": "cleanup_function.handler",
    "timeout": 60,
    "memorySize": 128,
    "cpu": 1,
    "diskSize": 512,
    "instanceConcurrency": 1,
    "internetAccess": true,
    "enableLongLiving": false
  },
  "container": {
    "image": "crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com/accuin-bio/jwt-token-cleaner:latest",
    "port": 9000
  },
  "acr": {
    "domain": "crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com",
    "namespace": "accuin-bio",
    "imageName": "jwt-token-cleaner",
    "imageVersion": "latest"
  },
  "region": "cn-shanghai"
}
```

## 使用方法

### 1. 設定環境變數

```bash
export ACR_USERNAME="your-acr-username"
export ACR_PASSWORD="your-acr-password"
```

### 2. 執行部署腳本

```bash
# 完整部署（建構 + 部署）
./deploy_container.sh

# 跳過 Docker 建構，只部署
./deploy_container.sh --skip-build

# 只建構 Docker 映像檔，不部署
./deploy_container.sh --skip-deploy

# 查看幫助
./deploy_container.sh --help
```

## 腳本功能

### 自動化功能

1. **配置載入**: 自動從 `fc-config.json` 載入所有配置
2. **依賴檢查**: 檢查 Docker、阿里雲 CLI、jq、Python 等依賴
3. **Docker 建構**: 建構、標籤、推送 Docker 映像檔到 ACR
4. **智能部署**: 
   - 如果 Function 不存在，自動創建
   - 如果 Function 已存在，自動更新
   - 請在控制台手動設置 Trigger

### 支援的選項

- `--skip-build`: 跳過 Docker 建構步驟
- `--skip-deploy`: 跳過 Function Compute 部署步驟
- `--help`: 顯示幫助資訊

## 依賴要求

- Docker
- 阿里雲 CLI (`aliyun`)
- Python 3
- ACR 認證資訊 (環境變數)

## 部署流程

1. **檢查依賴**: 驗證所有必要工具已安裝
2. **載入配置**: 從 `fc-config.json` 讀取配置
3. **準備建構上下文**: 複製必要檔案
4. **Docker 建構** (可選):
   - 登入 ACR
   - 建構映像檔
   - 標籤映像檔
   - 推送映像檔
5. **Function Compute 部署** (可選):
   - 檢查 Function 是否存在
   - 創建或更新 Function
   - 提示在控制台手動設置 Trigger

## 注意事項

- 確保 `fc-config.json` 中的配置正確
- 確保有足夠的 ACR 權限
- 確保有足夠的 Function Compute 權限
- 腳本會自動處理 Function 的創建/更新邏輯
- 請在控制台手動設置 Trigger

## 故障排除

### 常見錯誤

1. **ACR 認證失敗**: 檢查 `ACR_USERNAME` 和 `ACR_PASSWORD` 環境變數
2. **權限不足**: 確保有足夠的阿里雲權限
3. **配置檔案錯誤**: 檢查 `fc-config.json` 格式是否正確
