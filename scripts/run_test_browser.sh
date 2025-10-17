#!/bin/bash
# 瀏覽器測試包裝腳本 - 自動處理環境路徑

# 顏色輸出
BLUE='\033[0;34m'
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

echo -e "${BLUE}ℹ️  正在準備測試環境...${NC}"

# 取得專案根目錄
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT" || exit 1

# 檢測 UV 命令
UV_CMD=""

# 優先檢查常見路徑
if [ -x "/root/.local/bin/uv" ]; then
    UV_CMD="/root/.local/bin/uv"
elif [ -x "$HOME/.local/bin/uv" ]; then
    UV_CMD="$HOME/.local/bin/uv"
elif [ -x "$HOME/.cargo/bin/uv" ]; then
    UV_CMD="$HOME/.cargo/bin/uv"
elif command -v uv &> /dev/null; then
    UV_CMD="uv"
fi

if [ -z "$UV_CMD" ]; then
    echo -e "${RED}❌ 找不到 UV 包管理器${NC}"
    echo "請先執行安裝腳本: ./Linux_安裝.sh"
    echo ""
    echo "或手動安裝 UV:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  source \$HOME/.local/bin/env"
    exit 1
fi

echo -e "${GREEN}✅ 找到 UV: $UV_CMD${NC}"

# 執行測試
echo -e "${BLUE}ℹ️  執行瀏覽器測試...${NC}"
echo ""
"$UV_CMD" run python src/utils/browser_tester.py
