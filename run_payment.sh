#!/bin/bash

# 啟動腳本 - 使用 uv 管理 Python 環境 (WEDI 宅配通版本)
echo "📦 WEDI 宅配通自動下載工具"
echo "======================================"

# 載入共用檢查函數
source "$(dirname "$0")/scripts/common_checks.sh"

# 執行環境檢查
check_environment

# 直接執行代收貨款查詢功能
echo "💰 啟動代收貨款查詢功能"
echo ""

# 直接執行新的代收貨款查詢程式，讓它處理所有互動
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/payment_scraper.py "$@"

# 檢查執行結果
check_execution_result