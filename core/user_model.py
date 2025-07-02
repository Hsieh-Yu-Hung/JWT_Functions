from werkzeug.security import check_password_hash

# 模擬一個使用者資料庫
mock_users = {
    "admin@example.com": {
        "email": "admin@example.com",
        "password_hash": "pbkdf2:sha256:600000$xxxxxx",  # 由 werkzeug 生成
        "role": "admin"
    }
}

def get_user_by_email(email):
    return mock_users.get(email)

def verify_password(plain_password, hashed_password):
    return check_password_hash(hashed_password, plain_password)
