@echo off
set "SCRIPT=%~dp0setup.ps1"

rem 檢查 PowerShell 腳本是否存在
if not exist "%SCRIPT%" (
  echo 錯誤：找不到 %SCRIPT%
  pause
  exit /b 1
)

rem 優先用 Windows Terminal
where wt >nul 2>&1
if %errorlevel%==0 (
  wt -w 0 -p "PowerShell" "pwsh" -NoExit -ExecutionPolicy Bypass -File "%SCRIPT%"
  goto :end
)

rem 如果沒裝 Windows Terminal，直接用 pwsh
where pwsh >nul 2>&1
if %errorlevel%==0 (
  start "" pwsh -NoExit -ExecutionPolicy Bypass -File "%SCRIPT%"
  goto :end
)

rem 備援舊版 PowerShell
where powershell >nul 2>&1
if %errorlevel%==0 (
  start "" powershell -NoExit -ExecutionPolicy Bypass -File "%SCRIPT%"
  goto :end
)

rem 如果都沒有 PowerShell，顯示錯誤訊息
echo 錯誤：系統中找不到 PowerShell
echo 請安裝 PowerShell 7 或確保 Windows PowerShell 可用
pause
exit /b 1

:end