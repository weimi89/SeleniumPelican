@echo off
chcp 65001 >nul 2>&1

rem 設定視窗標題
title WEDI 運費未請款明細下載工具

rem 切換到腳本目錄
pushd "%~dp0"

echo.
echo 📋 WEDI 運費未請款明細下載工具
echo ==============================
echo.

rem 檢查 PowerShell 腳本是否存在
if not exist "scripts\run_unpaid.ps1" (
    echo ❌ 錯誤：找不到 scripts\run_unpaid.ps1 檔案
    echo 📁 當前目錄：%CD%
    pause
    exit /b 1
)

rem 優先用 Windows Terminal + PowerShell 7
where wt >nul 2>&1
if %errorlevel%==0 (
    where pwsh >nul 2>&1
    if %errorlevel%==0 (
        echo 🚀 使用 Windows Terminal + PowerShell 7 啟動...
        wt -w 0 -p "PowerShell" pwsh -NoExit -ExecutionPolicy Bypass -WorkingDirectory "%CD%" -File "%CD%\scripts\run_unpaid.ps1" %*
        goto :end
    )
)

rem 如果沒有 Windows Terminal，直接用 PowerShell 7
where pwsh >nul 2>&1
if %errorlevel%==0 (
    echo 🚀 使用 PowerShell 7 啟動...
    start "WEDI 運費未請款明細" pwsh -NoExit -ExecutionPolicy Bypass -WorkingDirectory "%CD%" -File "%CD%\scripts\run_unpaid.ps1" %*
    goto :end
)

rem 備援使用舊版 PowerShell
echo 🚀 使用傳統 PowerShell 啟動...
start "WEDI 運費未請款明細" powershell -NoExit -ExecutionPolicy Bypass -Command "Set-Location '%CD%'; & '.\scripts\run_unpaid.ps1'" %*

:end
popd
