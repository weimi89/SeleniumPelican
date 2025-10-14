#!/bin/bash
# WEDI 代收貨款匯款明細自動下載工具 - Linux 版本

# 切換到腳本目錄
cd "$(dirname "$0")"

echo ""
echo "📦 WEDI 代收貨款匯款明細自動下載工具"
echo "=========================================="
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

# 詢問日期範圍（如果命令列沒有指定）
if [[ ! " $* " == *" --start-date "* ]] && [[ ! " $* " == *" --end-date "* ]]; then
    echo "📅 日期範圍設定"
    echo "請輸入查詢日期範圍（格式：YYYYMMDD）："
    echo "• 直接按 Enter 使用預設範圍（過去7天）"
    echo "• 輸入開始日期，結束日期將詢問"
    echo ""

    read -p "開始日期 (YYYYMMDD): " start_date

    if [ -n "$start_date" ]; then
        if [[ $start_date =~ ^[0-9]{8}$ ]]; then
            read -p "結束日期 (YYYYMMDD): " end_date
            if [ -n "$end_date" ] && [[ $end_date =~ ^[0-9]{8}$ ]]; then
                set -- "$@" --start-date "$start_date" --end-date "$end_date"
                echo "✅ 將查詢 $start_date 到 $end_date 的資料"
            else
                echo "❌ 結束日期格式錯誤，使用預設範圍"
            fi
        else
            echo "❌ 開始日期格式錯誤，使用預設範圍"
        fi
    else
        echo "✅ 使用預設範圍：過去7天"
    fi
    echo ""
fi

# 顯示執行命令
cmd_str="uv run python -u src/scrapers/payment_scraper.py"
if [ $# -gt 0 ]; then
    cmd_str="$cmd_str $*"
fi
echo "🚀 執行命令: $cmd_str"
echo ""

# 執行 Python 程式
echo "🚀 啟動代收貨款匯款明細查詢功能"
echo ""
uv run python -u src/scrapers/payment_scraper.py "$@"
exit_code=$?

# 檢查執行結果
test_execution_result $exit_code

echo ""
read -p "按 Enter 鍵繼續..."