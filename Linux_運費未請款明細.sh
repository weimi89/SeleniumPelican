#!/bin/bash
# WEDI 運費未請款明細下載工具 - Linux 版本

# 切換到腳本目錄
cd "$(dirname "$0")"

echo ""
echo "📋 WEDI 運費未請款明細下載工具"
echo "=============================="
echo ""

# 載入共用檢查函數
if [ -f "scripts/common_checks.sh" ]; then
    source "scripts/common_checks.sh"
else
    echo "❌ 找不到 scripts/common_checks.sh，請確認檔案存在"
    exit 1
fi

# 執行環境檢查
test_environment

# 設定 PYTHONPATH 並執行 Python 程式
export PYTHONPATH="$(pwd)"

# 顯示執行命令
cmd_str="uv run python -u src/scrapers/unpaid_scraper.py"
if [ $# -gt 0 ]; then
    cmd_str="$cmd_str $*"
fi
echo "🚀 執行命令: $cmd_str"
echo ""

# 執行 Python 程式
echo "🚀 啟動運費未請款明細下載功能"
echo ""
uv run python -u src/scrapers/unpaid_scraper.py "$@"
exit_code=$?

# 檢查執行結果
test_execution_result $exit_code

echo ""
read -p "按 Enter 鍵繼續..."
