#!/bin/bash
# SeleniumPelican 共用檢查函數 - Shell 版本

test_environment() {
    echo "🔍 檢查執行環境..."

    # 檢查 uv
    if command -v uv &> /dev/null; then
        UV_VERSION=$(uv --version 2>/dev/null)
        echo "✅ uv: $UV_VERSION"
    else
        echo "❌ uv 未安裝或無法執行"
        echo "請先安裝 uv: https://docs.astral.sh/uv/"
        exit 1
    fi

    # 檢查虛擬環境
    if [ -d ".venv" ]; then
        echo "✅ 虛擬環境: .venv 存在"
    else
        echo "⚠️ 虛擬環境: .venv 不存在，將自動建立"
        echo "🚀 執行: uv sync"
        uv sync
        if [ $? -ne 0 ]; then
            echo "❌ 無法建立虛擬環境"
            exit 1
        fi
    fi

    # 檢查配置檔案
    if [ -f "accounts.json" ]; then
        echo "✅ 配置檔案: accounts.json 存在"

        # 使用配置驗證系統
        echo "🔍 執行配置驗證..."
        export PYTHONPATH="$(pwd)"
        if uv run python -c "from src.core.config_validator import validate_config_files; validate_config_files(show_report=False)" 2>/dev/null; then
            echo "✅ 配置檔案驗證通過"
        else
            echo "⚠️ 配置檔案有問題，建議執行詳細檢查:"
            echo "   uv run python -m src.core.config_validator"
        fi
    else
        echo "❌ 配置檔案: accounts.json 不存在"
        if [ -f "accounts.json.example" ]; then
            echo "💡 請複製 accounts.json.example 並填入實際帳號資訊:"
            echo "   cp accounts.json.example accounts.json"
        fi
        exit 1
    fi

    # 檢查 .env 檔案
    if [ -f ".env" ]; then
        echo "✅ 環境設定: .env 存在"
    else
        echo "⚠️ 環境設定: .env 不存在"
        if [ -f ".env.example" ]; then
            echo "💡 建議複製範例檔案:"
            echo "   cp .env.example .env"
        fi
    fi

    # 設定必要的環境變數
    export PYTHONUNBUFFERED=1

    echo "✅ 環境檢查完成"
    echo ""
}

test_execution_result() {
    local exit_code=$1

    echo ""
    if [ $exit_code -eq 0 ]; then
        echo "🎉 執行完成！"
    else
        echo "❌ 執行失敗 (退出碼: $exit_code)"
        echo ""
        echo "💡 疑難排解建議："
        echo "1. 檢查網路連線是否正常"
        echo "2. 確認帳號密碼是否正確"
        echo "3. 檢查 Chrome 瀏覽器是否正常啟動"
        echo "4. 查看 logs/ 目錄下的詳細日誌"
        echo ""
        echo "🔧 執行配置檢查："
        echo "   uv run python -m src.core.config_validator"
    fi
}