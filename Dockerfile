FROM python:3.11-slim

WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

EXPOSE 9000

# 設定環境變數
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV PYTHONUNBUFFERED=1

# 設定執行權限
RUN chmod +x /app/index.py
RUN chmod +x /app/app.py

# 啟動命令 - 使用 gunicorn 啟動 Flask 應用
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "--workers", "1", "--timeout", "300", "--preload", "app:app"] 