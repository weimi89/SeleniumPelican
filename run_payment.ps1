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
    
    # 詢問使用者是否要自訂日期範圍（如果沒有命令列參數）
    $finalArgs = @()
    if ($args.Count -eq 0 -or (-not ($args -contains "--start-date") -and -not ($args -contains "--end-date"))) {
        # 計算預設日期範圍
        $today = Get-Date -Format "yyyyMMdd"
        $sevenDaysAgo = (Get-Date).AddDays(-7).ToString("yyyyMMdd")
        
        Write-Host ""
        Write-Host "📅 日期範圍設定" -ForegroundColor Yellow
        Write-Host "預設查詢範圍：$sevenDaysAgo ~ $today (往前7天到今天)"
        Write-Host ""
        
        $customDate = Read-Host "是否要自訂日期範圍？(y/N)"
        
        if ($customDate -eq 'y' -or $customDate -eq 'Y') {
            Write-Host ""
            $startDateStr = Read-Host "請輸入開始日期 (格式: YYYYMMDD，例如: 20241201)"
            $endDateStr = Read-Host "請輸入結束日期 (格式: YYYYMMDD，例如: 20241208，或按 Enter 使用今天)"
            
            if ($startDateStr -and $startDateStr -match '^\d{8}$') {
                $finalArgs += "--start-date"
                $finalArgs += $startDateStr
            }
            
            if ($endDateStr -and $endDateStr -match '^\d{8}$') {
                $finalArgs += "--end-date"
                $finalArgs += $endDateStr
            }
            
            Write-Host ""
            if ($finalArgs.Count -gt 0) {
                Write-Host "✅ 將使用自訂日期範圍" -ForegroundColor Green
            } else {
                Write-Host "⚠️ 未設定有效日期，將使用預設範圍" -ForegroundColor Yellow
            }
        } else {
            Write-Host "✅ 使用預設日期範圍：$sevenDaysAgo ~ $today" -ForegroundColor Green
        }
        
        # 合併原有參數和新參數
        $finalArgs += $args
    } else {
        $finalArgs = $args
    }
    
    # 顯示執行命令
    $commandStr = "uv run python -u src/scrapers/payment_scraper.py"
    if ($finalArgs.Count -gt 0) {
        $commandStr += " " + ($finalArgs -join " ")
    }
    Write-Host ""
    Write-Host "🚀 執行命令: $commandStr" -ForegroundColor Blue
    Write-Host ""
    
    # 執行 Python 程式
    & uv run python -u src/scrapers/payment_scraper.py @finalArgs
    
    # 檢查執行結果
    Test-ExecutionResult -ExitCode $LASTEXITCODE
    
} catch {
    Write-Host "❌ 執行過程中發生錯誤：$($_.Exception.Message)" -ForegroundColor Red
    Test-ExecutionResult -ExitCode 1
}

Write-Host ""
Read-Host "按 Enter 鍵繼續..."