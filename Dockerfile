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

# 啟動
CMD ["gunicorn", "-c", "gunicorn.conf.py", "app:app"] 