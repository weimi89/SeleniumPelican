#!/bin/bash
# SeleniumPelican 更新工具 - Linux 版本

# 切換到腳本目錄
cd "$(dirname "$0")"

echo ""
echo "🔄 SeleniumPelican 更新工具"
echo "=========================="
echo ""

# 檢查更新腳本是否存在
if [ ! -f "scripts/update.sh" ]; then
    echo "❌ 找不到 scripts/update.sh，請確認檔案存在"
    exit 1
fi

# 執行更新腳本
source "scripts/update.sh" "$@"