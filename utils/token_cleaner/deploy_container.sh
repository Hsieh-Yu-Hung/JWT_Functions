#!/bin/bash
#
# JWT Token Cleaner 容器化部署腳本
#
# 快速部署清理 Function 到阿里雲 Function Compute
# 使用 Docker 容器化部署
#

set -e  # 遇到錯誤立即退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置檔案路徑
CONFIG_FILE="fc-config.json"

# 載入配置
load_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        log_error "配置檔案 $CONFIG_FILE 不存在"
        exit 1
    fi
    
    # 直接從配置檔案中提取值（簡化方法）
    # Function 配置
    FUNCTION_NAME=$(grep '"name"' "$CONFIG_FILE" | head -1 | sed 's/.*"name"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    FUNCTION_DESCRIPTION=$(grep '"description"' "$CONFIG_FILE" | sed 's/.*"description"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    RUNTIME=$(grep '"runtime"' "$CONFIG_FILE" | sed 's/.*"runtime"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    HANDLER=$(grep '"handler"' "$CONFIG_FILE" | sed 's/.*"handler"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    TIMEOUT=$(grep '"timeout"' "$CONFIG_FILE" | sed 's/.*"timeout"[[:space:]]*:[[:space:]]*\([^,}]*\).*/\1/' | tr -d ' ')
    MEMORY_SIZE=$(grep '"memorySize"' "$CONFIG_FILE" | sed 's/.*"memorySize"[[:space:]]*:[[:space:]]*\([^,}]*\).*/\1/' | tr -d ' ')
    CPU=$(grep '"cpu"' "$CONFIG_FILE" | sed 's/.*"cpu"[[:space:]]*:[[:space:]]*\([^,}]*\).*/\1/' | tr -d ' ')
    DISK_SIZE=$(grep '"diskSize"' "$CONFIG_FILE" | sed 's/.*"diskSize"[[:space:]]*:[[:space:]]*\([^,}]*\).*/\1/' | tr -d ' ')
    INSTANCE_CONCURRENCY=$(grep '"instanceConcurrency"' "$CONFIG_FILE" | sed 's/.*"instanceConcurrency"[[:space:]]*:[[:space:]]*\([^,}]*\).*/\1/' | tr -d ' ')
    INTERNET_ACCESS=$(grep '"internetAccess"' "$CONFIG_FILE" | sed 's/.*"internetAccess"[[:space:]]*:[[:space:]]*\([^,}]*\).*/\1/' | tr -d ' ')
    ENABLE_LONG_LIVING=$(grep '"enableLongLiving"' "$CONFIG_FILE" | sed 's/.*"enableLongLiving"[[:space:]]*:[[:space:]]*\([^,}]*\).*/\1/' | tr -d ' ')
    
    # ACR 配置
    ACR_DOMAIN=$(grep '"domain"' "$CONFIG_FILE" | sed 's/.*"domain"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    ACR_NAMESPACE=$(grep '"namespace"' "$CONFIG_FILE" | sed 's/.*"namespace"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    IMAGE_NAME=$(grep '"imageName"' "$CONFIG_FILE" | sed 's/.*"imageName"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    IMAGE_VERSION=$(grep '"imageVersion"' "$CONFIG_FILE" | sed 's/.*"imageVersion"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    

    
    # 其他配置
    REGION=$(grep '"region"' "$CONFIG_FILE" | sed 's/.*"region"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/')
    CONTAINER_PORT=$(grep '"port"' "$CONFIG_FILE" | sed 's/.*"port"[[:space:]]*:[[:space:]]*\([^,}]*\).*/\1/' | tr -d ' ')
    
    # 驗證必要配置
    if [ -z "$FUNCTION_NAME" ] || [ -z "$ACR_DOMAIN" ] || [ -z "$REGION" ]; then
        log_error "配置檔案格式錯誤或缺少必要配置"
        log_error "FUNCTION_NAME: $FUNCTION_NAME"
        log_error "ACR_DOMAIN: $ACR_DOMAIN"
        log_error "REGION: $REGION"
        exit 1
    fi
    
    log_success "配置載入完成"
}

# 日誌函數
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 檢查依賴
check_dependencies() {
    log_info "檢查依賴..."
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安裝"
        exit 1
    fi
    
    # 檢查阿里雲 CLI
    if ! command -v aliyun &> /dev/null; then
        log_error "阿里雲 CLI 未安裝"
        log_info "請先安裝阿里雲 CLI: https://help.aliyun.com/document_detail/121541.html"
        exit 1
    fi
    

    
    # 檢查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安裝"
        exit 1
    fi
    
    # 檢查環境變數
    if [ -z "$ACR_USERNAME" ]; then
        log_error "缺少 ACR_USERNAME 環境變數"
        exit 1
    fi
    
    if [ -z "$ACR_PASSWORD" ]; then
        log_error "缺少 ACR_PASSWORD 環境變數"
        exit 1
    fi
    
    log_success "依賴檢查通過"
}

# 準備建構上下文
prepare_build_context() {
    log_info "準備建構上下文..."
    
    # 複製必要檔案
    PROJECT_ROOT="$(dirname "$(dirname "$(pwd)")")"
    
    # 複製 requirements.txt
    if [ -f "$PROJECT_ROOT/requirements.txt" ]; then
        cp "$PROJECT_ROOT/requirements.txt" .
        log_info "複製 requirements.txt"
    fi
    
    log_success "建構上下文準備完成"
}

# 登入 ACR
login_acr() {
    log_info "登入 ACR..."
    
    # 清理認證資訊
    USERNAME=$(echo "$ACR_USERNAME" | tr -d '"' | tr -d "'")
    PASSWORD=$(echo "$ACR_PASSWORD" | tr -d '"' | tr -d "'")
    
    echo "$PASSWORD" | docker login --username "$USERNAME" --password-stdin "$ACR_DOMAIN"
    
    if [ $? -eq 0 ]; then
        log_success "ACR 登入成功"
    else
        log_error "ACR 登入失敗"
        exit 1
    fi
}

# 建構 Docker 映像檔
build_image() {
    log_info "建構 Docker 映像檔..."
    
    docker build -t "$IMAGE_NAME:$IMAGE_VERSION" .
    
    if [ $? -eq 0 ]; then
        log_success "Docker 映像檔建構成功"
    else
        log_error "Docker 映像檔建構失敗"
        exit 1
    fi
}

# 標籤映像檔
tag_image() {
    log_info "標籤映像檔..."
    
    LOCAL_TAG="$IMAGE_NAME:$IMAGE_VERSION"
    ACR_TAG="$ACR_DOMAIN/$ACR_NAMESPACE/$IMAGE_NAME:$IMAGE_VERSION"
    
    docker tag "$LOCAL_TAG" "$ACR_TAG"
    
    if [ $? -eq 0 ]; then
        log_success "映像檔標籤完成"
    else
        log_error "映像檔標籤失敗"
        exit 1
    fi
}

# 推送映像檔
push_image() {
    log_info "推送映像檔到 ACR..."
    
    ACR_TAG="$ACR_DOMAIN/$ACR_NAMESPACE/$IMAGE_NAME:$IMAGE_VERSION"
    
    docker push "$ACR_TAG"
    
    if [ $? -eq 0 ]; then
        log_success "映像檔推送成功"
    else
        log_error "映像檔推送失敗"
        exit 1
    fi
}

# 創建 Function 配置
create_function_config() {
    local vpc_image="${ACR_DOMAIN}/${ACR_NAMESPACE}/${IMAGE_NAME}:${IMAGE_VERSION}"
    
    # 創建臨時配置檔案
    cat > /tmp/function-config.json << EOF
{
  "functionName": "$FUNCTION_NAME",
  "description": "$FUNCTION_DESCRIPTION",
  "runtime": "$RUNTIME",
  "handler": "$HANDLER",
  "timeout": $TIMEOUT,
  "memorySize": $MEMORY_SIZE,
  "cpu": $CPU,
  "diskSize": $DISK_SIZE,
  "instanceConcurrency": $INSTANCE_CONCURRENCY,
  "internetAccess": $INTERNET_ACCESS,
  "enableLongLiving": $ENABLE_LONG_LIVING,
  "customContainerConfig": {
    "image": "$vpc_image",
    "port": $CONTAINER_PORT
  }
}
EOF
    
    echo "/tmp/function-config.json"
}

# 創建 Function 更新配置
create_function_update_config() {
    local vpc_image="${ACR_DOMAIN}/${ACR_NAMESPACE}/${IMAGE_NAME}:${IMAGE_VERSION}"
    
    # 創建臨時配置檔案
    cat > /tmp/function-update.json << EOF
{
  "customContainerConfig": {
    "image": "$vpc_image",
    "port": $CONTAINER_PORT
  }
}
EOF
    
    echo "/tmp/function-update.json"
}

# 檢查 Function 是否存在
check_function_exists() {
    log_info "檢查 Function 是否存在: $FUNCTION_NAME"
    
    if aliyun fc GetFunction --region "$REGION" --functionName "$FUNCTION_NAME" &> /dev/null; then
        return 0  # Function 存在
    else
        return 1  # Function 不存在
    fi
}

# 創建 Function Compute
create_function() {
    log_info "開始創建 Function Compute 服務..."
    
    # 創建配置
    local config_file=$(create_function_config)
    
    log_info "創建 Function: $FUNCTION_NAME"
    log_info "使用映像檔: ${ACR_DOMAIN}/${ACR_NAMESPACE}/${IMAGE_NAME}:${IMAGE_VERSION}"
    
    # 創建 Function
    aliyun fc CreateFunction \
        --region "$REGION" \
        --body "$(cat $config_file)"
    
    # 清理臨時檔案
    rm -f "$config_file"
    
    log_success "Function Compute 服務創建完成"
}

# 更新 Function Compute
update_function() {
    log_info "開始更新 Function Compute 服務..."
    
    # 創建更新配置
    local config_file=$(create_function_update_config)
    
    log_info "更新 Function: $FUNCTION_NAME"
    log_info "使用映像檔: ${ACR_DOMAIN}/${ACR_NAMESPACE}/${IMAGE_NAME}:${IMAGE_VERSION}"
    
    # 更新 Function
    aliyun fc UpdateFunction \
        --region "$REGION" \
        --functionName "$FUNCTION_NAME" \
        --body "$(cat $config_file)"
    
    # 清理臨時檔案
    rm -f "$config_file"
    
    log_success "Function Compute 服務更新完成"
}




# 主函數
main() {
    # 解析參數
    SKIP_BUILD="false"
    SKIP_DEPLOY="false"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            --skip-build)
                SKIP_BUILD="true"
                shift
                ;;
            --skip-deploy)
                SKIP_DEPLOY="true"
                shift
                ;;
            --help|-h)
                echo "用法: $0 [選項]"
                echo "選項:"
                echo "  --skip-build         跳過 Docker 建構步驟"
                echo "  --skip-deploy        跳過 Function Compute 部署步驟"
                echo "  --help, -h           顯示幫助資訊"
                echo ""
                echo "說明:"
                echo "  腳本會自動從 fc-config.json 載入配置"
                echo "  如果 Function 不存在會自動創建，存在則會更新"
                echo "  請在控制台手動設置 Trigger"
                exit 0
                ;;
            *)
                log_error "未知參數: $1"
                echo "使用 --help 查看幫助資訊"
                exit 1
                ;;
        esac
    done
    
    echo "🚀 開始 JWT Token Cleaner 部署"
    echo "=================================================="
    
    # 檢查依賴
    check_dependencies
    
    # 載入配置
    load_config
    
    # 準備建構上下文
    prepare_build_context
    
    if [ "$SKIP_BUILD" = "false" ]; then
        # 登入 ACR
        login_acr
        
        # 建構映像檔
        build_image
        
        # 標籤映像檔
        tag_image
        
        # 推送映像檔
        push_image
    else
        log_info "跳過 Docker 建構步驟"
    fi
    
    if [ "$SKIP_DEPLOY" = "false" ]; then
        # 部署到 Function Compute
        if check_function_exists; then
            log_info "Function 已存在，進行更新"
            update_function
        else
            log_info "Function 不存在，進行創建"
            create_function
        fi
        
        log_success "部署完成！"
        log_info "Function 名稱: $FUNCTION_NAME"
        log_info "區域: $REGION"
        log_info "請在控制台手動設置 Trigger"
    else
        log_info "跳過 Function Compute 部署步驟"
    fi
}

# 執行主函數
main "$@" 