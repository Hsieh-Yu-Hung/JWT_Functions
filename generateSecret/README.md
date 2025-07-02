# JWT SECRET_KEY 產生器

這個目錄包含用於產生安全 JWT SECRET_KEY 的 Python 腳本。

## 檔案說明

- `generate_secret.py` - 完整版密鑰產生器，提供四種不同的產生方法
- `quick_secret.py` - 快速版密鑰產生器，只產生一個推薦的密鑰

## 使用方法

### 快速產生密鑰
```bash
python generateSecret/quick_secret.py
```

### 完整版密鑰產生器
```bash
python generateSecret/generate_secret.py
```

## 產生方法說明

1. **隨機字串** - 包含字母、數字和特殊字元的隨機字串
2. **URL 安全** - URL 安全的 base64 編碼字串
3. **十六進位** - 十六進位格式的隨機字串
4. **Base64** - Base64 編碼的隨機位元組

## 安全建議

- 每個環境（開發、測試、生產）使用不同的 SECRET_KEY
- 定期更換 SECRET_KEY
- 不要將 .env 檔案提交到版本控制
- 建議使用至少 64 字元的密鑰
- 確保 .env 檔案已加入 .gitignore

## 使用步驟

1. 執行腳本產生密鑰
2. 複製 `SECRET_KEY=xxxxx` 這一行
3. 貼到您的 .env 檔案中
4. 重新啟動應用程式

## 注意事項

- 這些腳本使用 Python 內建的 `secrets` 模組，確保密鑰的隨機性和安全性
- 產生的密鑰都是 64 字元長度，符合安全要求
- 建議在離線環境中執行腳本以確保安全性 