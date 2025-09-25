#!/bin/bash
# SeleniumPelican 配置檔案驗證工具 - Linux 版本

# 切換到腳本目錄
cd "$(dirname "$0")"

echo ""
echo "🔍 SeleniumPelican 配置檔案驗證工具"
echo "==================================="
echo ""

# 檢查 uv
if ! command -v uv &> /dev/null; then
    echo "❌ uv 未安裝或無法執行"
    echo "請先安裝 uv: https://docs.astral.sh/uv/"
    exit 1
fi

# 檢查虛擬環境
if [ ! -d ".venv" ]; then
    echo "⚠️ 虛擬環境不存在，將自動建立..."
    echo "🚀 執行: uv sync"
    uv sync
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
uv run python -m src.core.config_validator "$@"
exit_code=$?

echo ""
if [ $exit_code -eq 0 ]; then
    echo "🎉 配置驗證完成！"
else
    echo "❌ 配置驗證發現問題，請查看上方詳細資訊"
fi

echo ""
read -p "按 Enter 鍵繼續..."