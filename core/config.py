import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

# 載入 .env 檔案
load_dotenv()

# JWT 配置
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required. Please set it in your .env file")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720

# MongoDB 配置（使用原有的環境變數名稱）
DB_ACCOUNT = os.environ.get("DB_ACCOUNT")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_URI = os.environ.get("DB_URI")
DB_NAME = os.environ.get("DB_NAME")

# 檢查必要的 MongoDB 環境變數
if not all([DB_ACCOUNT, DB_PASSWORD, DB_URI, DB_NAME]):
    raise ValueError("MongoDB environment variables (DB_ACCOUNT, DB_PASSWORD, DB_URI, DB_NAME) are required")

# 正確編碼使用者名稱和密碼
encoded_username = quote_plus(DB_ACCOUNT)
encoded_password = quote_plus(DB_PASSWORD)
MONGO_URI = f"mongodb://{encoded_username}:{encoded_password}@{DB_URI}"

# MongoDB Collection 名稱
MONGODB_BLACKLIST_COLLECTION = "blacklist"
MONGODB_ROLE_COLLECTION = "role_list"
MONGODB_USERS_COLLECTION = "users"

# 資料庫連接池配置
MONGODB_MAX_POOL_SIZE = int(os.environ.get("MONGODB_MAX_POOL_SIZE", "10"))
MONGODB_MIN_POOL_SIZE = int(os.environ.get("MONGODB_MIN_POOL_SIZE", "1"))