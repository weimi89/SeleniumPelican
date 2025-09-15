# WEDI 運費查詢自動下載工具 - PowerShell 7 版本

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 確保在正確的專案目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "🚛 WEDI 運費查詢自動下載工具" -ForegroundColor Cyan
Write-Host "===============================" -ForegroundColor Cyan
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

# 執行運費查詢程式，並傳遞所有命令列參數
Write-Host "🚀 啟動運費查詢功能" -ForegroundColor Green
Write-Host ""

try {
    # 設定 PYTHONPATH
    $env:PYTHONPATH = $PWD.Path
    
    # 執行運費查詢程式
    Write-Host "🚀 執行命令: uv run python -u src/scrapers/freight_scraper.py $args" -ForegroundColor Blue
    
    # 直接使用 uv 執行，保持互動性
    & uv run python -u src/scrapers/freight_scraper.py @args
    
    # 檢查執行結果
    Test-ExecutionResult -ExitCode $LASTEXITCODE
    
} catch {
    Write-Host "❌ 執行過程中發生錯誤：$($_.Exception.Message)" -ForegroundColor Red
    Test-ExecutionResult -ExitCode 1
}

# 如果沒有傳入參數，暫停以便查看結果
if ($args.Count -eq 0) {
    Write-Host ""
    Read-Host "按 Enter 鍵繼續..."
}