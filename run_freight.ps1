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
    
    # 詢問使用者是否要自訂月份範圍（如果沒有命令列參數）
    $finalArgs = @()
    if ($args.Count -eq 0 -or (-not ($args -contains "--start-month") -and -not ($args -contains "--end-month"))) {
        # 計算預設月份範圍
        $lastMonth = (Get-Date).AddMonths(-1).ToString("yyyyMM")
        
        Write-Host ""
        Write-Host "📅 查詢月份設定" -ForegroundColor Yellow
        Write-Host "預設查詢範圍：$lastMonth (上個月)"
        Write-Host ""
        
        $customMonth = Read-Host "是否要自訂月份範圍？(y/N)"
        
        if ($customMonth -eq 'y' -or $customMonth -eq 'Y') {
            Write-Host ""
            $startMonthStr = Read-Host "請輸入開始月份 (格式: YYYYMM，例如: 202411)"
            $endMonthStr = Read-Host "請輸入結束月份 (格式: YYYYMM，例如: 202412，或按 Enter 使用本月)"
            
            if ($startMonthStr -and $startMonthStr -match '^\d{6}$') {
                $finalArgs += "--start-month"
                $finalArgs += $startMonthStr
            }
            
            if ($endMonthStr -and $endMonthStr -match '^\d{6}$') {
                $finalArgs += "--end-month"
                $finalArgs += $endMonthStr
            }
            
            Write-Host ""
            if ($finalArgs.Count -gt 0) {
                Write-Host "✅ 將使用自訂月份範圍" -ForegroundColor Green
            } else {
                Write-Host "⚠️ 未設定有效月份，將使用預設範圍" -ForegroundColor Yellow
            }
        } else {
            Write-Host "✅ 使用預設月份範圍：$lastMonth (上個月)" -ForegroundColor Green
        }
        
        # 合併原有參數和新參數
        $finalArgs += $args
    } else {
        $finalArgs = $args
    }
    
    # 顯示執行命令
    $commandStr = "uv run python -u src/scrapers/freight_scraper.py"
    if ($finalArgs.Count -gt 0) {
        $commandStr += " " + ($finalArgs -join " ")
    }
    Write-Host ""
    Write-Host "🚀 執行命令: $commandStr" -ForegroundColor Blue
    Write-Host ""
    
    # 執行 Python 程式
    & uv run python -u src/scrapers/freight_scraper.py @finalArgs
    
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