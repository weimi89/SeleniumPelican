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

REM 同步依賴套件
echo 📦 同步依賴套件...
uv sync

REM 設定環境變數確保即時輸出
set PYTHONUNBUFFERED=1

REM 檢查參數並執行
if "%1"=="download" goto download
if "%1"=="" goto download
goto usage

:download
echo 📥 執行 WEDI 宅配通自動下載代收貨款匯款明細
echo ✅ 已設定 PYTHONUNBUFFERED=1 環境變數
echo.
echo 📅 請輸入開始日期 (格式: YYYYMMDD，例如: 20250101)
echo    直接按 Enter 使用預設值 (今天往前7天)
set /p start_date="開始日期: "

REM 如果使用者沒有輸入，使用預設值
if "%start_date%"=="" (
    echo 📅 使用預設日期範圍 (今天往前7天)
    uv run python -u wedi_selenium_scraper.py %* 2>&1 | findstr /v "DevTools listening"
) else (
    echo 📅 使用指定開始日期: %start_date%
    uv run python -u wedi_selenium_scraper.py --start-date %start_date% %* 2>&1 | findstr /v "DevTools listening"
)

REM 檢查執行結果
if %errorlevel% equ 0 (
    echo.
    echo ✅ 程式執行完成
) else (
    echo.
    echo ❌ 程式執行時發生錯誤 (錯誤代碼: %errorlevel%)
)
goto end

:usage
echo 使用方式：
echo   run.cmd                      - 互動式執行 (會提示輸入開始日期)
echo   run.cmd download             - 互動式執行 (會提示輸入開始日期)
echo   run.cmd download --headless  - 互動式執行 + 背景模式
echo.
echo 💡 互動式功能：
echo   - 執行時會提示輸入開始日期 (格式: YYYYMMDD)
echo   - 直接按 Enter 使用預設值 (今天往前7天)
echo   - 輸入日期後會自動設定 --start-date 參數
echo.
echo 或直接使用：
echo   set PYTHONUNBUFFERED=1
echo   uv run python -u wedi_selenium_scraper.py [選項]

:end
pause