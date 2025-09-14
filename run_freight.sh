#!/bin/bash

# WEDI 運費查詢自動下載工具執行腳本 (macOS/Linux)
echo "🚛 WEDI 運費查詢自動下載工具"
echo "==============================="

# 載入共用檢查函數
source "$(dirname "$0")/scripts/common_checks.sh"

# 執行環境檢查
check_environment

# 執行運費查詢程式，並傳遞所有命令列參數
echo "🚀 啟動運費查詢功能"
echo

# 使用 uv 執行 Python 程式
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/freight_scraper.py "$@"

# 檢查執行結果
check_execution_result