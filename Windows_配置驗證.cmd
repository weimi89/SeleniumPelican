@echo off
chcp 65001 >nul 2>&1

rem 設定視窗標題
title SeleniumPelican 配置檔案驗證工具

rem 切換到腳本目錄
pushd "%~dp0"

echo.
echo 🔍 SeleniumPelican 配置檔案驗證工具
echo ===================================
echo.

rem 檢查 Python 和 uv
where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ uv 未安裝或無法執行
    echo 請先安裝 uv: https://docs.astral.sh/uv/
    pause
    exit /b 1
)

rem 檢查虛擬環境
if not exist ".venv" (
    echo ⚠️ 虛擬環境不存在，將自動建立...
    echo 🚀 執行: uv sync
    uv sync
    if %errorlevel% neq 0 (
        echo ❌ 無法建立虛擬環境
        pause
        exit /b 1
    fi
)

rem 設定環境變數並執行配置驗證
set PYTHONPATH=%CD%
set PYTHONUNBUFFERED=1

echo 🚀 執行配置檔案驗證...
echo.

rem 執行配置驗證，支援命令列參數
uv run python -m src.core.config_validator %*

echo.
if %errorlevel% equ 0 (
    echo 🎉 配置驗證完成！
) else (
    echo ❌ 配置驗證發現問題，請查看上方詳細資訊
)

echo.
pause
popd