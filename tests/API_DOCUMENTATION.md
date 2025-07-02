# JWT 認證 API 文檔

## 📋 概述

這個 JWT 認證系統提供了完整的用戶認證和管理功能，包括註冊、登入、登出、用戶資料管理等。

## 🔗 基礎 URL

```
http://localhost:9000
```

## 📚 API 端點

### 🔐 認證相關

#### 1. 用戶註冊
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

#### 2. 用戶登入
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

#### 3. 用戶登出
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

#### 4. 切換帳戶
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

**回應：**
```json
{
  "message": "Account switched successfully",
  "access_token": "new_jwt_token",
  "user": {
    "id": "new_user_id",
    "email": "newuser@example.com",
    "username": "新用戶名稱",
    "role": "user"
  },
  "note": "Please replace the old token with this new token"
}
```

### 👤 用戶資料管理

#### 5. 取得用戶資料
```http
GET /profile
```

**請求頭：**
```
Authorization: Bearer <jwt_token>
```

**回應：**
```json
{
  "message": "Profile retrieved successfully",
  "profile": {
    "id": "user_id",
    "email": "user@example.com",
    "username": "用戶名稱",
    "role": "user",
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "last_login": "2024-01-01T12:00:00Z",
    "roles": ["user"],
    "permissions": ["read", "write"]
  }
}
```

#### 6. 更新用戶資料
```http
PUT /profile
```

**請求頭：**
```
Authorization: Bearer <jwt_token>
```

**請求體：**
```json
{
  "username": "新的用戶名稱"
}
```

**回應：**
```json
{
  "message": "Profile updated successfully",
  "profile": {
    // 更新後的完整用戶資料
  }
}
```

#### 7. 變更密碼
```http
POST /change-password
```

**請求體：**
```json
{
  "email": "user@example.com",
  "old_password": "old_password",
  "new_password": "new_password"
}
```

**回應：**
```json
{
  "message": "Password changed successfully"
}
```

### 🔧 管理員功能

#### 8. 管理員統計資訊
```http
GET /admin/stats
```

**請求頭：**
```
Authorization: Bearer <admin_jwt_token>
```

**回應：**
```json
{
  "system_stats": {
    "blacklist": {
      "total_tokens": 10,
      "active_tokens": 5,
      "expired_tokens": 5
    },
    "active_users_count": 100,
    "total_users": 100
  },
  "user_info": {
    "current_user": "admin@example.com",
    "roles": ["admin"]
  }
}
```

#### 9. 黑名單統計
```http
GET /admin/blacklist-stats
```

**回應：**
```json
{
  "blacklist_statistics": {
    "total_tokens": 10,
    "active_tokens": 5,
    "expired_tokens": 5
  },
  "note": "These are real-time statistics from MongoDB"
}
```

#### 10. 取得所有用戶
```http
GET /admin/users
```

**回應：**
```json
{
  "users": [
    {
      "id": "user_id",
      "email": "user@example.com",
      "username": "用戶名稱",
      "role": "user",
      "is_active": true
    }
  ],
  "total_users": 100
}
```

#### 11. 更新用戶角色
```http
PUT /admin/users/<user_id>/roles
```

**請求體：**
```json
{
  "roles": ["user", "admin"],
  "permissions": ["read", "write", "admin"]
}
```

**回應：**
```json
{
  "message": "User roles updated successfully"
}
```

#### 12. 停用用戶
```http
POST /admin/users/<email>/deactivate
```

**回應：**
```json
{
  "message": "User deactivated successfully"
}
```

#### 13. 清理過期 Token
```http
POST /admin/cleanup-tokens
```

**回應：**
```json
{
  "message": "Cleanup completed successfully",
  "cleaned_tokens": 5,
  "remaining_tokens": 10,
  "active_tokens": 8,
  "expired_tokens": 2
}
```

### 🏥 系統功能

#### 14. 健康檢查
```http
GET /health
```

**回應：**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00Z",
  "environment": "function-compute",
  "version": "1.0.0",
  "database": "connected"
}
```

#### 15. 受保護的路由
```http
GET /protected
```

**請求頭：**
```
Authorization: Bearer <jwt_token>
```

**回應：**
```json
{
  "message": "Hello user@example.com, you have access!",
  "user_info": {
    "email": "user@example.com",
    "roles": ["user"],
    "permissions": ["read", "write"]
  }
}
```

## 🔑 認證方式

所有需要認證的端點都使用 JWT Bearer Token：

```
Authorization: Bearer <your_jwt_token>
```

## 📝 使用範例

### 使用 curl 測試

```bash
# 1. 註冊用戶
curl -X POST http://localhost:9000/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456","username":"測試用戶"}'

# 2. 登入
curl -X POST http://localhost:9000/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"123456"}'

# 3. 使用 token 存取受保護的路由
curl -X GET http://localhost:9000/protected \
  -H "Authorization: Bearer <your_jwt_token>"

# 4. 取得用戶資料
curl -X GET http://localhost:9000/profile \
  -H "Authorization: Bearer <your_jwt_token>"

# 5. 登出
curl -X POST http://localhost:9000/logout \
  -H "Authorization: Bearer <your_jwt_token>"
```

### 使用 Python requests

```python
import requests

BASE_URL = "http://localhost:9000"

# 註冊
response = requests.post(f"{BASE_URL}/register", json={
    "email": "test@example.com",
    "password": "123456",
    "username": "測試用戶"
})

# 登入
response = requests.post(f"{BASE_URL}/login", json={
    "email": "test@example.com",
    "password": "123456"
})
token = response.json()["access_token"]

# 使用 token
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(f"{BASE_URL}/profile", headers=headers)
```

## ⚠️ 注意事項

1. **密碼長度**：密碼至少需要 6 個字符
2. **Email 格式**：必須是有效的 email 格式
3. **Token 過期**：JWT token 有過期時間，過期後需要重新登入
4. **管理員權限**：某些端點需要管理員權限
5. **資料庫連接**：確保 MongoDB 連接正常

## 🚀 快速開始

1. 啟動服務：
```bash
python app.py
```

2. 運行測試腳本：
```bash
python test_auth_routes.py
```

3. 或使用 curl/Postman 測試各個端點 