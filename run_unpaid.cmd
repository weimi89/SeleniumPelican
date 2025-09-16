@echo off
chcp 65001 >nul

REM WEDI 運費未請款明細下載工具執行腳本 (Windows)
REM 自動啟動 PowerShell 7 以獲得最佳體驗

echo 🔧 正在啟動 PowerShell 7...

REM 優先順序：Windows Terminal > PowerShell 7 > 舊版 PowerShell
where /q pwsh
if %ERRORLEVEL% == 0 (
    pwsh -NoProfile -Command "& '%~dp0run_unpaid.ps1' %*"
) else (
    powershell -NoProfile -Command "& '%~dp0run_unpaid.ps1' %*"
)

pause