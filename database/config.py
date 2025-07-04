import os
import yaml
from dotenv import load_dotenv
from urllib.parse import quote_plus

# 載入 .env 檔案
load_dotenv()

# 載入 config.yaml 檔案
def load_config():
    """載入 config.yaml 配置檔案"""
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config.yaml')
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        raise ValueError(f"配置檔案 {config_path} 不存在")
    except yaml.YAMLError as e:
        raise ValueError(f"配置檔案格式錯誤: {e}")

# 載入配置
config = load_config()

# JWT 配置
SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is required. Please set it in your .env file")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720

# API 配置 - 從 config.yaml 讀取 API 模式
API_MODE = config.get('api', {}).get('mode')
if not API_MODE:
    raise ValueError("API_MODE is required in config.yaml file (internal or public)")
API_MODE = API_MODE.lower()

if API_MODE not in ["internal", "public"]:
    raise ValueError("API_MODE must be either 'internal' or 'public'. Please check your config.yaml file")

# 公網 API 配置
PUBLIC_API_BASE_URL = os.environ.get("PUBLIC_API_BASE_URL")
if not PUBLIC_API_BASE_URL:
    raise ValueError("PUBLIC_API_BASE_URL environment variable is required. Please set it in your .env file")

PUBLIC_API_KEY = os.environ.get("PUBLIC_API_KEY")
if not PUBLIC_API_KEY:
    raise ValueError("PUBLIC_API_KEY environment variable is required. Please set it in your .env file")

# 內網 API 配置
INTERNAL_API_BASE_URL = os.environ.get("INTERNAL_API_BASE_URL")
if not INTERNAL_API_BASE_URL:
    raise ValueError("INTERNAL_API_BASE_URL environment variable is required. Please set it in your .env file")

INTERNAL_API_KEY = os.environ.get("INTERNAL_API_KEY")
if not INTERNAL_API_KEY:
    raise ValueError("INTERNAL_API_KEY environment variable is required. Please set it in your .env file")

# 根據模式選擇 API 配置
if API_MODE == "public":
    API_BASE_URL = PUBLIC_API_BASE_URL
    API_KEY = PUBLIC_API_KEY
    print(f"🌐 使用公網 API: {API_BASE_URL}")
elif API_MODE == "internal":
    API_BASE_URL = INTERNAL_API_BASE_URL
    API_KEY = INTERNAL_API_KEY
    print(f"🏠 使用內網 API: {API_BASE_URL}")
else:
    raise ValueError("API_MODE must be either 'internal' or 'public'. Please check your config.yaml file")

# MongoDB 配置（保留原有配置以備用）
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
MONGODB_USER_ROLE_COLLECTION = "user_role_mapping"
MONGODB_USERS_COLLECTION = "users"

# 資料庫連接池配置
MONGODB_MAX_POOL_SIZE = int(os.environ.get("MONGODB_MAX_POOL_SIZE", "10"))
MONGODB_MIN_POOL_SIZE = int(os.environ.get("MONGODB_MIN_POOL_SIZE", "1")) 