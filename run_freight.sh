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

# 詢問使用者是否要自訂月份範圍（如果沒有命令列參數）
final_args=("$@")

# 檢查是否沒有月份相關參數
has_month_params=false
for arg in "$@"; do
    if [[ "$arg" == "--start-month" || "$arg" == "--end-month" ]]; then
        has_month_params=true
        break
    fi
done

if [[ $# -eq 0 || "$has_month_params" == false ]]; then
    # 計算預設月份範圍
    last_month=$(date -d "last month" "+%Y%m" 2>/dev/null || date -v-1m "+%Y%m" 2>/dev/null || echo "")
    
    echo ""
    echo "📅 查詢月份設定"
    if [[ -n "$last_month" ]]; then
        echo "預設查詢範圍：${last_month} (上個月)"
    else
        echo "預設查詢範圍：上個月"
    fi
    echo ""
    
    read -p "是否要自訂月份範圍？(y/N): " custom_month
    
    if [[ "$custom_month" == "y" || "$custom_month" == "Y" ]]; then
        echo ""
        read -p "請輸入開始月份 (格式: YYYYMM，例如: 202411): " start_month_str
        read -p "請輸入結束月份 (格式: YYYYMM，例如: 202412，或按 Enter 使用本月): " end_month_str
        
        # 驗證並添加月份參數
        if [[ "$start_month_str" =~ ^[0-9]{6}$ ]]; then
            final_args+=("--start-month" "$start_month_str")
        fi
        
        if [[ "$end_month_str" =~ ^[0-9]{6}$ ]]; then
            final_args+=("--end-month" "$end_month_str")
        fi
        
        echo ""
        if [[ ${#final_args[@]} -gt $# ]]; then
            echo "✅ 將使用自訂月份範圍"
        else
            echo "⚠️ 未設定有效月份，將使用預設範圍"
        fi
    else
        if [[ -n "$last_month" ]]; then
            echo "✅ 使用預設月份範圍：${last_month} (上個月)"
        else
            echo "✅ 使用預設月份範圍：上個月"
        fi
    fi
fi

# 顯示執行命令
command_str="uv run python -u src/scrapers/freight_scraper.py"
if [[ ${#final_args[@]} -gt 0 ]]; then
    command_str="$command_str ${final_args[*]}"
fi
echo ""
echo "🚀 執行命令: $command_str"
echo ""

# 使用 uv 執行 Python 程式
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/freight_scraper.py "${final_args[@]}"

# 檢查執行結果
check_execution_result