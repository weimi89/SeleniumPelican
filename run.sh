#!/bin/bash

# 啟動腳本 - 使用 uv 管理 Python 環境 (WEDI 宅配通版本)
echo "📦 啟動 WEDI 宅配通自動下載工具"
echo "======================================"

# 檢查 uv 是否安裝
if ! command -v uv &> /dev/null; then
    echo "❌ 找不到 uv，請先安裝："
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "   或參考 https://github.com/astral-sh/uv#installation"
    exit 1
fi

# 檢查是否有 .venv 目錄，如果沒有就建立
if [ ! -d ".venv" ]; then
    echo "🔧 建立虛擬環境..."
    uv venv
fi

# 同步依賴套件
echo "📦 同步依賴套件..."
uv sync

# 直接執行下載功能
echo "📥 執行 WEDI 宅配通自動下載代收貨款匯款明細"
# 設定環境變數確保即時輸出
export PYTHONUNBUFFERED=1
echo ""
echo "📅 請輸入開始日期 (格式: YYYYMMDD，例如: 20250101)"
echo "   直接按 Enter 使用預設值 (今天往前7天)"
read -p "開始日期: " start_date

# 如果使用者沒有輸入，使用預設值
if [ -z "$start_date" ]; then
    echo "📅 使用預設日期範圍 (今天往前7天)"
    uv run python -u wedi_selenium_scraper.py "$@"  # 傳遞所有參數
else
    echo "📅 使用指定開始日期: $start_date"
    uv run python -u wedi_selenium_scraper.py --start-date "$start_date" "$@"  # 傳遞所有參數
fi