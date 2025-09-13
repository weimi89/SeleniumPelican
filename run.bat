@echo off
chcp 65001 > nul
echo 📦 啟動 WEDI 宅配通自動下載工具
echo ======================================

REM 檢查 uv 是否安裝
uv --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 找不到 uv，請先安裝：
    echo    Invoke-RestMethod https://astral.sh/uv/install.ps1 ^| Invoke-Expression
    echo    或參考 https://github.com/astral-sh/uv#installation
    pause
    exit /b 1
)

REM 檢查是否有 .venv 目錄，如果沒有就建立
if not exist ".venv" (
    echo 🔧 建立虛擬環境...
    uv venv
)

REM 檢查 requirements.txt 是否存在並安裝依賴
if exist "requirements.txt" (
    echo 📦 安裝依賴套件...
    uv pip install -r requirements.txt
)

REM 設定環境變數確保即時輸出
set PYTHONUNBUFFERED=1

REM 檢查參數並執行
if "%1"=="download" goto download
if "%1"=="" goto download
goto usage

:download
echo 📥 執行 WEDI 宅配通自動下載代收貨款匯款明細
echo ✅ 已設定 PYTHONUNBUFFERED=1 環境變數
REM 過濾掉 DevTools 訊息
uv run python -u wedi_selenium_scraper.py %* 2>&1 | findstr /v "DevTools listening"
goto end

:usage
echo 使用方式：
echo   run.bat                      - 執行自動下載代收貨款匯款明細
echo   run.bat download             - 執行自動下載代收貨款匯款明細
echo   run.bat download --headless  - 背景模式執行
echo   run.bat download --start-date 20241201 --end-date 20241208  - 指定日期範圍
echo.
echo 或直接使用：
echo   set PYTHONUNBUFFERED=1
echo   uv run python -u wedi_selenium_scraper.py [選項]

:end