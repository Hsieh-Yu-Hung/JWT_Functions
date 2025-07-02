#!/bin/bash

# 設定參數
IMAGE_NAME="jwt-functions"
IMAGE_VERSION="latest"
ACR_NAMESPACE="accuin-bio"
ACR_DOMAIN="crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com"
ACR_USERNAME=$(grep -oP 'ACR_USERNAME="\K[^"]+' .env)
ACR_PASSWORD=$(grep -oP 'ACR_PASSWORD="\K[^"]+' .env)

# 若沒有讀取到 ACR_USERNAME 或 ACR_PASSWORD，則報錯提醒 .env 檔案是否正確
if [ -z "$ACR_USERNAME" ] || [ -z "$ACR_PASSWORD" ]; then
  echo "Error: ACR_USERNAME 或 ACR_PASSWORD 未設定，請檢查 .env 檔案"
  exit 1
fi

# Function Compute 設定
FUNCTION_NAME="jwt-auth-functions"
REGION="cn-shanghai"

# 登入 ACR
echo $ACR_PASSWORD | docker login --username=$ACR_USERNAME --password-stdin $ACR_DOMAIN

# 建構映像檔
docker build -t ${IMAGE_NAME}:${IMAGE_VERSION} .

# 打標籤
docker tag ${IMAGE_NAME}:${IMAGE_VERSION} ${ACR_DOMAIN}/${ACR_NAMESPACE}/${IMAGE_NAME}:${IMAGE_VERSION}

# 推送到 ACR
docker push ${ACR_DOMAIN}/${ACR_NAMESPACE}/${IMAGE_NAME}:${IMAGE_VERSION}

echo "更新 Function Compute 服務"

# 更新 Function Compute 服務
aliyun fc UpdateFunction \
  --region ${REGION} \
  --functionName ${FUNCTION_NAME} \
  --body '{
    "customContainerConfig": {
        "image": "crpi-hfqxuov7ff0bdkpc.cn-shanghai.personal.cr.aliyuncs.com/accuin-bio/jwt-functions:latest"
    }
  }'

echo "Function Compute 服務更新完成" 
