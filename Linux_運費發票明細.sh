#!/bin/bash
# WEDI 運費(月結)結帳資料查詢工具 - Linux 版本

# 切換到腳本目錄
cd "$(dirname "$0")"

echo ""
echo "🚛 WEDI 運費(月結)結帳資料查詢工具"
echo "=================================="
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

# 詢問月份範圍（如果命令列沒有指定）
if [[ ! " $* " == *" --start-month "* ]] && [[ ! " $* " == *" --end-month "* ]]; then
    echo "📅 月份範圍設定"
    echo "請輸入查詢月份範圍（格式：YYYYMM）："
    echo "• 直接按 Enter 使用預設範圍（上個月）"
    echo "• 輸入開始月份，結束月份將詢問"
    echo ""

    read -p "開始月份 (YYYYMM): " start_month

    if [ -n "$start_month" ]; then
        if [[ $start_month =~ ^[0-9]{6}$ ]]; then
            read -p "結束月份 (YYYYMM): " end_month
            if [ -n "$end_month" ] && [[ $end_month =~ ^[0-9]{6}$ ]]; then
                set -- "$@" --start-month "$start_month" --end-month "$end_month"
                echo "✅ 將查詢 $start_month 到 $end_month 的資料"
            else
                echo "❌ 結束月份格式錯誤，使用預設範圍"
            fi
        else
            echo "❌ 開始月份格式錯誤，使用預設範圍"
        fi
    else
        echo "✅ 使用預設範圍：上個月"
    fi
    echo ""
fi

# 顯示執行命令
cmd_str="$UV_CMD run python -u src/scrapers/freight_scraper.py"
if [ $# -gt 0 ]; then
    cmd_str="$cmd_str $*"
fi
echo "🚀 執行命令: $cmd_str"
echo ""

# 執行 Python 程式
echo "🚀 啟動運費(月結)結帳資料查詢功能"
echo ""
"$UV_CMD" run python -u src/scrapers/freight_scraper.py "$@"
exit_code=$?

# 檢查執行結果
test_execution_result $exit_code

echo ""
read -p "按 Enter 鍵繼續..."
