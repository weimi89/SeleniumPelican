@echo off
chcp 65001 > nul
echo 🚛 WEDI 運費查詢自動下載工具
echo ===============================

REM 執行共用檢查
call "%~dp0scripts\common_checks.cmd" check_environment

REM 執行運費查詢程式，並傳遞所有命令列參數
echo 🚀 啟動運費查詢功能
echo.

REM 使用 uv 執行 Python 程式
set PYTHONPATH=%cd% && uv run python -u src/scrapers/freight_scraper.py %* 2>&1 | findstr /v "DevTools listening"

REM 檢查執行結果
call "%~dp0scripts\common_checks.cmd" check_execution_result

REM 如果沒有傳入參數，暫停以便查看結果
if "%~1"=="" pause