# WEDI 運費(月結)結帳資料查詢工具 - PowerShell 7 版本

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 確保在正確的專案目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

Write-Host "🚛 WEDI 運費(月結)結帳資料查詢工具" -ForegroundColor Cyan
Write-Host "==================================" -ForegroundColor Cyan
Write-Host ""

# 載入共用檢查函數
$commonChecksPath = Join-Path $PSScriptRoot "common_checks.ps1"
if (Test-Path $commonChecksPath) {
    . $commonChecksPath
} else {
    Write-Host "❌ 找不到 common_checks.ps1，請確認檔案存在" -ForegroundColor Red
    exit 1
}

# 執行環境檢查
Test-Environment

try {
    # 設定 PYTHONPATH 並執行 Python 程式
    $env:PYTHONPATH = $PWD.Path

    # 詢問月份範圍（如果命令列沒有指定）
    if (-not ($args -contains "--start-month") -and -not ($args -contains "--end-month")) {
        Write-Host "📅 月份範圍設定" -ForegroundColor Yellow
        Write-Host "請輸入查詢月份範圍（格式：YYYYMM）："
        Write-Host "• 直接按 Enter 使用預設範圍（上個月）"
        Write-Host "• 輸入開始月份，結束月份將詢問"
        Write-Host ""

        $startMonth = Read-Host "開始月份 (YYYYMM)"

        if ($startMonth -and $startMonth -match '^\d{6}$') {
            $endMonth = Read-Host "結束月份 (YYYYMM)"
            if ($endMonth -and $endMonth -match '^\d{6}$') {
                $args += "--start-month"
                $args += $startMonth
                $args += "--end-month"
                $args += $endMonth
                Write-Host "✅ 將查詢 $startMonth 到 $endMonth 的資料" -ForegroundColor Green
            } else {
                Write-Host "❌ 結束月份格式錯誤，使用預設範圍" -ForegroundColor Yellow
            }
        } elseif ($startMonth) {
            Write-Host "❌ 開始月份格式錯誤，使用預設範圍" -ForegroundColor Yellow
        } else {
            Write-Host "✅ 使用預設範圍：上個月" -ForegroundColor Green
        }
        Write-Host ""
    }

    # 顯示執行命令
    $commandStr = "uv run python -u src/scrapers/freight_scraper.py"
    if ($args.Count -gt 0) {
        $commandStr += " " + ($args -join " ")
    }
    Write-Host "🚀 執行命令: $commandStr" -ForegroundColor Blue
    Write-Host ""

    # 執行 Python 程式
    Write-Host "🚀 啟動運費(月結)結帳資料查詢功能" -ForegroundColor Blue
    Write-Host ""
    & uv run python -u src/scrapers/freight_scraper.py @args

    # 檢查執行結果
    Test-ExecutionResult -ExitCode $LASTEXITCODE

} catch {
    Write-Host "❌ 執行過程中發生錯誤：$($_.Exception.Message)" -ForegroundColor Red
    Test-ExecutionResult -ExitCode 1
}

Write-Host ""
Read-Host "按 Enter 鍵繼續..."