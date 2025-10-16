#!/bin/bash
# SeleniumPelican 安裝工具 - Linux 版本

# 切換到腳本目錄
cd "$(dirname "$0")"

echo ""
echo "📦 SeleniumPelican 安裝工具"
echo "=========================="
echo ""

# 檢查安裝腳本是否存在
if [ ! -f "scripts/install.sh" ]; then
    echo "❌ 找不到 scripts/install.sh，請確認檔案存在"
    exit 1
fi

# 執行安裝腳本
source "scripts/install.sh" "$@"
