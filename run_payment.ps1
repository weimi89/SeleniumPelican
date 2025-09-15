# WEDI 代收貨款查詢自動下載工具 - PowerShell 7 版本

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 確保在正確的專案目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "📦 WEDI 宅配通自動下載工具" -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# 載入共用檢查函數
$commonChecksPath = Join-Path $PSScriptRoot "scripts\common_checks.ps1"
if (Test-Path $commonChecksPath) {
    . $commonChecksPath
} else {
    Write-Host "❌ 找不到 common_checks.ps1，請確認檔案存在" -ForegroundColor Red
    exit 1
}

# 執行共用檢查
Test-Environment

# 直接執行代收貨款查詢功能
Write-Host "💰 啟動代收貨款查詢功能" -ForegroundColor Green
Write-Host ""

try {
    # 設定 PYTHONPATH 並執行 Python 程式
    $env:PYTHONPATH = $PWD.Path
    
    # 執行新的代收貨款查詢程式，讓它處理所有互動
    # 過濾掉 DevTools listening 訊息
    $process = Start-Process -FilePath "uv" -ArgumentList @("run", "python", "-u", "src/scrapers/payment_scraper.py") + $args -NoNewWindow -Wait -PassThru -RedirectStandardError
    
    # 檢查執行結果
    Test-ExecutionResult -ExitCode $process.ExitCode
    
} catch {
    Write-Host "❌ 執行過程中發生錯誤：$($_.Exception.Message)" -ForegroundColor Red
    Test-ExecutionResult -ExitCode 1
}

Write-Host ""
Read-Host "按 Enter 鍵繼續..."