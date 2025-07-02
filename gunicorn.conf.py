# Gunicorn 配置文件
import multiprocessing

# 綁定地址和端口
bind = "0.0.0.0:9000"

# 工作進程數量
workers = multiprocessing.cpu_count() * 2 + 1

# 工作進程類型
worker_class = "sync"

# 超時設置
timeout = 300  # 增加超時時間到 5 分鐘
keepalive = 5

# 日誌設置
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 進程名稱
proc_name = "jwt-auth-service"

# 預加載應用
preload_app = True

# 最大請求數
max_requests = 1000
max_requests_jitter = 100

# 重啟工作進程
graceful_timeout = 30

# 安全設置
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190 