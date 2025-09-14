@echo off
chcp 65001 > nul
echo 📦 WEDI 宅配通自動下載工具
echo ======================================

REM 執行共用檢查
call "%~dp0scripts\common_checks.cmd" check_environment

REM 直接執行代收貨款查詢功能
echo 💰 啟動代收貨款查詢功能
echo.

REM 直接執行新的代收貨款查詢程式，讓它處理所有互動
set PYTHONPATH=%cd% && uv run python -u src/scrapers/payment_scraper.py %* 2>&1 | findstr /v "DevTools listening"

REM 檢查執行結果
call "%~dp0scripts\common_checks.cmd" check_execution_result

pause