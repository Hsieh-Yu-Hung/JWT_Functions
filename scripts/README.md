# Function Compute 部署腳本說明

## 📁 檔案結構

```
scripts/
├── deploy.py          # Python 部署工具
├── deploy.sh          # Bash 部署腳本
└── README.md          # 本說明文件

config/
├── fc-config.json     # 實際配置檔案
└── fc-config.example.json  # 配置檔案範例
```

## 🚀 快速開始

### 1. 設定配置檔案

複製範例配置檔案並修改：

```bash
cp config/fc-config.example.json config/fc-config.json
```

編輯 `config/fc-config.json`，填入您的實際配置：

```json
{
  "function": {
    "name": "your-function-name",
    "runtime": "custom-container",
    "handler": "index.handler",
    "timeout": 60,
    "memorySize": 4096
  },
  "acr": {
    "domain": "your-acr-domain.your-region.personal.cr.aliyuncs.com",
    "namespace": "your-namespace",
    "imageName": "your-image-name",
    "imageVersion": "latest"
  },
  "region": "cn-shanghai"
}
```

### 2. 設定環境變數

確保 `.env` 檔案包含必要的認證資訊：

```bash
ACR_USERNAME="your-acr-username"
ACR_PASSWORD="your-acr-password"
```

### 3. 執行部署

使用 Bash 腳本（推薦）：

```bash
# 完整部署
./scripts/deploy.sh

# 跳過 Docker 建構
./scripts/deploy.sh --skip-build

# 驗證配置
./scripts/deploy.sh --validate

# 顯示狀態
./scripts/deploy.sh --status
```

或直接使用 Python 腳本：

```bash
# 完整部署
python3 scripts/deploy.py

# 使用自訂配置檔案
python3 scripts/deploy.py --config config/my-config.json

# 跳過建構
python3 scripts/deploy.py --skip-build
```

## 🔧 配置檔案說明

### function 區段

| 欄位 | 說明 | 範例 |
|------|------|------|
| name | 函數名稱 | "jwt-auth-functions" |
| description | 函數描述 | "JWT Authentication Service" |
| runtime | 運行時 | "custom-container" |
| handler | 處理器 | "index.handler" |
| timeout | 超時時間（秒） | 60 |
| memorySize | 記憶體大小（MB） | 4096 |
| cpu | CPU 核心數 | 4 |
| diskSize | 磁碟大小（MB） | 512 |
| instanceConcurrency | 實例並發數 | 10 |
| internetAccess | 是否允許網路訪問 | true |

### container 區段

| 欄位 | 說明 | 範例 |
|------|------|------|
| image | 容器映像檔 | "crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com/accuin-bio/jwt-functions:latest" |
| port | 容器端口 | 9000 |
| command | 啟動命令 | null |
| entrypoint | 進入點 | null |

### vpc 區段

| 欄位 | 說明 | 範例 |
|------|------|------|
| vpcId | VPC ID | "vpc-uf6g60tlmx6zkp0q0yc84" |
| vSwitchIds | VSwitch ID 列表 | ["vsw-uf6ekfgoluqjz5hs6tu1q"] |
| securityGroupId | 安全組 ID | "sg-uf66lomhewh0z13efsbo" |
| role | 角色 ARN | null |

### acr 區段

| 欄位 | 說明 | 範例 |
|------|------|------|
| domain | ACR 域名 | "crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com" |
| namespace | 命名空間 | "accuin-bio" |
| imageName | 映像檔名稱 | "jwt-functions" |
| imageVersion | 映像檔版本 | "latest" |

## 🛠️ 命令列選項

### deploy.sh 選項

```bash
-h, --help          顯示幫助資訊
-c, --config PATH   指定配置檔案路徑
--skip-build        跳過 Docker 建構步驟
--validate          僅驗證配置檔案
--status            顯示部署狀態
--dry-run           模擬執行（不實際部署）
```

### deploy.py 選項

```bash
--config, -c PATH   配置檔案路徑 (預設: config/fc-config.json)
--skip-build        跳過 Docker 建構步驟
--validate          僅驗證配置檔案
--status            顯示部署狀態
```

## 📋 部署流程

### 完整部署流程

1. **驗證配置** - 檢查配置檔案格式和必要欄位
2. **檢查環境** - 驗證必要工具和環境變數
3. **登入 ACR** - 使用認證資訊登入容器倉庫
4. **建構映像檔** - 執行 Docker build
5. **標籤映像檔** - 為映像檔打上 ACR 標籤
6. **推送映像檔** - 將映像檔推送到 ACR
7. **更新函數** - 更新 Function Compute 服務

### 跳過建構流程

如果使用 `--skip-build` 選項，將跳過步驟 3-6，直接更新函數配置。

## 🔍 故障排除

### 常見問題

1. **配置檔案錯誤**
   ```bash
   # 驗證配置檔案
   ./scripts/deploy.sh --validate
   ```

2. **ACR 認證失敗**
   ```bash
   # 檢查環境變數
   cat .env | grep ACR
   ```

3. **Docker 建構失敗**
   ```bash
   # 檢查 Dockerfile
   docker build -t test .
   ```

4. **函數更新失敗**
   ```bash
   # 檢查 Aliyun CLI 認證
   aliyun fc ListFunctions --region cn-shanghai
   ```

### 日誌查看

```bash
# 查看函數日誌
aliyun fc GetFunctionLogs --region cn-shanghai --functionName jwt-auth-functions

# 查看實時日誌
aliyun fc GetFunctionLogs --region cn-shanghai --functionName jwt-auth-functions --tail
```

## 🔒 安全性考量

1. **敏感資訊保護**
   - 不要將 `.env` 檔案提交到版本控制
   - 使用環境變數管理敏感資訊
   - 定期更換 ACR 密碼

2. **配置檔案安全**
   - 不要將實際配置檔案提交到版本控制
   - 使用範例檔案作為模板
   - 定期檢查配置檔案權限

3. **網路安全**
   - 使用 VPC 隔離網路
   - 配置適當的安全組規則
   - 限制容器網路訪問

## 📈 最佳實踐

1. **版本管理**
   - 使用語義化版本號
   - 為每個部署打上標籤
   - 保留部署歷史記錄

2. **配置管理**
   - 使用環境特定的配置檔案
   - 驗證配置檔案格式
   - 定期更新配置範例

3. **部署策略**
   - 先在測試環境部署
   - 使用藍綠部署策略
   - 監控部署狀態

4. **監控告警**
   - 設定部署失敗告警
   - 監控函數執行狀態
   - 配置錯誤通知

## 📞 支援

如有問題，請檢查：

1. 配置檔案格式是否正確
2. 環境變數是否設定
3. 網路連接是否正常
4. 阿里雲認證是否有效
5. 函數日誌中的錯誤資訊 