#!/bin/bash

# Function Compute 部署腳本
# 使用 Python 部署工具進行管理

set -e  # 遇到錯誤時退出

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函數：顯示幫助資訊
show_help() {
    echo -e "${BLUE}Function Compute 部署腳本${NC}"
    echo ""
    echo "用法: $0 [選項]"
    echo ""
    echo "選項:"
    echo "  -h, --help          顯示此幫助資訊"
    echo "  -c, --config PATH   指定配置檔案路徑 (預設: config/fc-config.json)"
    echo "  --skip-build        跳過 Docker 建構步驟"
    echo "  --validate          僅驗證配置檔案"
    echo "  --status            顯示部署狀態"
    echo "  --dry-run           模擬執行（不實際部署）"
    echo ""
    echo "範例:"
    echo "  $0                    # 完整部署"
    echo "  $0 --skip-build       # 跳過建構，僅更新函數"
    echo "  $0 --validate         # 驗證配置檔案"
    echo "  $0 --status           # 顯示狀態"
}

# 函數：檢查必要工具
check_requirements() {
    echo -e "${BLUE}🔍 檢查必要工具...${NC}"
    
    # 檢查 Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 未安裝${NC}"
        exit 1
    fi
    
    # 檢查 Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker 未安裝${NC}"
        exit 1
    fi
    
    # 檢查 Aliyun CLI
    if ! command -v aliyun &> /dev/null; then
        echo -e "${RED}❌ Aliyun CLI 未安裝${NC}"
        exit 1
    fi
    
    # 檢查部署腳本
    if [ ! -f "scripts/deploy.py" ]; then
        echo -e "${RED}❌ 部署腳本不存在: scripts/deploy.py${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 必要工具檢查完成${NC}"
}

# 函數：檢查環境變數
check_env_vars() {
    echo -e "${BLUE}🔍 檢查環境變數...${NC}"
    
    if [ ! -f ".env" ]; then
        echo -e "${RED}❌ .env 檔案不存在${NC}"
        exit 1
    fi
    
    # 檢查必要的環境變數
    if ! grep -q "ACR_USERNAME" .env; then
        echo -e "${RED}❌ ACR_USERNAME 未在 .env 檔案中設定${NC}"
        exit 1
    fi
    
    if ! grep -q "ACR_PASSWORD" .env; then
        echo -e "${RED}❌ ACR_PASSWORD 未在 .env 檔案中設定${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✅ 環境變數檢查完成${NC}"
}

# 函數：顯示部署資訊
show_deployment_info() {
    echo -e "${BLUE}📋 部署資訊${NC}"
    echo "  腳本路徑: $(pwd)"
    echo "  配置檔案: ${CONFIG_FILE}"
    echo "  跳過建構: ${SKIP_BUILD}"
    echo "  僅驗證: ${VALIDATE_ONLY}"
    echo "  顯示狀態: ${SHOW_STATUS}"
    echo "  模擬執行: ${DRY_RUN}"
    echo ""
}

# 函數：執行部署
run_deployment() {
    echo -e "${BLUE}🚀 開始部署...${NC}"
    
    # 構建 Python 命令
    PYTHON_CMD="python3 scripts/deploy.py"
    
    if [ "$CONFIG_FILE" != "config/fc-config.json" ]; then
        PYTHON_CMD="$PYTHON_CMD --config $CONFIG_FILE"
    fi
    
    if [ "$SKIP_BUILD" = "true" ]; then
        PYTHON_CMD="$PYTHON_CMD --skip-build"
    fi
    
    if [ "$VALIDATE_ONLY" = "true" ]; then
        PYTHON_CMD="$PYTHON_CMD --validate"
    fi
    
    if [ "$SHOW_STATUS" = "true" ]; then
        PYTHON_CMD="$PYTHON_CMD --status"
    fi
    
    # 執行部署
    if [ "$DRY_RUN" = "true" ]; then
        echo -e "${YELLOW}🔍 模擬執行命令: $PYTHON_CMD${NC}"
        echo -e "${YELLOW}⚠️  這是模擬執行，不會實際部署${NC}"
    else
        echo -e "${GREEN}🔄 執行部署命令...${NC}"
        eval $PYTHON_CMD
    fi
}

# 主程式
main() {
    # 預設值
    CONFIG_FILE="config/fc-config.json"
    SKIP_BUILD="false"
    VALIDATE_ONLY="false"
    SHOW_STATUS="false"
    DRY_RUN="false"
    
    # 解析命令列參數
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            -c|--config)
                CONFIG_FILE="$2"
                shift 2
                ;;
            --skip-build)
                SKIP_BUILD="true"
                shift
                ;;
            --validate)
                VALIDATE_ONLY="true"
                shift
                ;;
            --status)
                SHOW_STATUS="true"
                shift
                ;;
            --dry-run)
                DRY_RUN="true"
                shift
                ;;
            *)
                echo -e "${RED}❌ 未知選項: $1${NC}"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 顯示標題
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}  Function Compute 部署工具${NC}"
    echo -e "${BLUE}================================${NC}"
    echo ""
    
    # 檢查必要條件
    check_requirements
    check_env_vars
    
    # 顯示部署資訊
    show_deployment_info
    
    # 執行部署
    run_deployment
    
    echo ""
    echo -e "${GREEN}🎉 部署流程完成！${NC}"
}

# 執行主程式
main "$@" 