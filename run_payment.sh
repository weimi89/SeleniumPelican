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

# 詢問使用者是否要自訂日期範圍（如果沒有命令列參數）
final_args=("$@")

# 檢查是否沒有日期相關參數
has_date_params=false
for arg in "$@"; do
    if [[ "$arg" == "--start-date" || "$arg" == "--end-date" ]]; then
        has_date_params=true
        break
    fi
done

if [[ $# -eq 0 || "$has_date_params" == false ]]; then
    # 計算預設日期範圍
    today=$(date "+%Y%m%d")
    seven_days_ago=$(date -d "7 days ago" "+%Y%m%d" 2>/dev/null || date -v-7d "+%Y%m%d" 2>/dev/null || echo "")
    
    echo ""
    echo "📅 日期範圍設定"
    if [[ -n "$seven_days_ago" ]]; then
        echo "預設查詢範圍：${seven_days_ago} ~ ${today} (往前7天到今天)"
    else
        echo "預設查詢範圍：往前7天到今天"
    fi
    echo ""
    
    read -p "是否要自訂日期範圍？(y/N): " custom_date
    
    if [[ "$custom_date" == "y" || "$custom_date" == "Y" ]]; then
        echo ""
        read -p "請輸入開始日期 (格式: YYYYMMDD，例如: 20241201): " start_date_str
        read -p "請輸入結束日期 (格式: YYYYMMDD，例如: 20241208，或按 Enter 使用今天): " end_date_str
        
        # 驗證並添加日期參數
        if [[ "$start_date_str" =~ ^[0-9]{8}$ ]]; then
            final_args+=("--start-date" "$start_date_str")
        fi
        
        if [[ "$end_date_str" =~ ^[0-9]{8}$ ]]; then
            final_args+=("--end-date" "$end_date_str")
        fi
        
        echo ""
        if [[ ${#final_args[@]} -gt $# ]]; then
            echo "✅ 將使用自訂日期範圍"
        else
            echo "⚠️ 未設定有效日期，將使用預設範圍"
        fi
    else
        if [[ -n "$seven_days_ago" ]]; then
            echo "✅ 使用預設日期範圍：${seven_days_ago} ~ ${today}"
        else
            echo "✅ 使用預設日期範圍：往前7天"
        fi
    fi
fi

# 顯示執行命令
command_str="uv run python -u src/scrapers/payment_scraper.py"
if [[ ${#final_args[@]} -gt 0 ]]; then
    command_str="$command_str ${final_args[*]}"
fi
echo ""
echo "🚀 執行命令: $command_str"
echo ""

# 執行代收貨款查詢程式
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/payment_scraper.py "${final_args[@]}"

# 檢查執行結果
check_execution_result