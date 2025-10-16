#!/bin/bash
# SeleniumPelican 配置檔案驗證工具 - Linux 版本

# 切換到腳本目錄
cd "$(dirname "$0")"

echo ""
echo "🔍 SeleniumPelican 配置檔案驗證工具"
echo "==================================="
echo ""

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
    echo "❌ 找不到 UV 包管理器"
    echo "請先執行安裝腳本: ./Linux_安裝.sh"
    echo ""
    echo "或手動安裝 UV:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  source \$HOME/.local/bin/env"
    exit 1
fi

echo "✅ 找到 UV: $UV_CMD"
echo ""

# 檢查虛擬環境
if [ ! -d ".venv" ]; then
    echo "⚠️ 虛擬環境不存在，將自動建立..."
    echo "🚀 執行: $UV_CMD sync"
    "$UV_CMD" sync
    if [ $? -ne 0 ]; then
        echo "❌ 無法建立虛擬環境"
        exit 1
    fi
fi

# 設定環境變數並執行配置驗證
export PYTHONPATH="$(pwd)"
export PYTHONUNBUFFERED=1

echo "🚀 執行配置檔案驗證..."
echo ""

# 執行配置驗證，支援命令列參數
"$UV_CMD" run python -m src.core.config_validator "$@"
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 配置驗證完成！"
else
    echo "❌ 配置驗證發現問題，請查看上方詳細資訊"
fi

echo ""
read -p "按 Enter 鍵繼續..."
