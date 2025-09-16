#!/bin/bash

# WEDI 運費未請款明細下載工具執行腳本 (Linux/macOS)
# 自動設定環境變數並執行程式

echo "🔧 設定環境變數..."
export PYTHONUNBUFFERED=1
export PYTHONPATH="$(pwd)"

echo "📊 WEDI 運費未請款明細下載工具"
echo "📅 結束時間: $(date +%Y%m%d) (當日)"
echo ""

# 執行程式
uv run python -u src/scrapers/unpaid_scraper.py "$@"

echo ""
echo "✅ 執行完成"