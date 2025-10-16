# WEDI 代收貨款匯款明細自動下載工具 - PowerShell 7 版本

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 確保在正確的專案目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

Write-Host "📦 WEDI 代收貨款匯款明細自動下載工具" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
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

    # 詢問日期範圍（如果命令列沒有指定）
    if (-not ($args -contains "--start-date") -and -not ($args -contains "--end-date")) {
        Write-Host "📅 日期範圍設定" -ForegroundColor Yellow
        Write-Host "請輸入查詢日期範圍（格式：YYYYMMDD）："
        Write-Host "• 直接按 Enter 使用預設範圍（過去7天）"
        Write-Host "• 輸入開始日期，結束日期將詢問"
        Write-Host ""

        $startDate = Read-Host "開始日期 (YYYYMMDD)"

        if ($startDate -and $startDate -match '^\d{8}$') {
            $endDate = Read-Host "結束日期 (YYYYMMDD)"
            if ($endDate -and $endDate -match '^\d{8}$') {
                $args += "--start-date"
                $args += $startDate
                $args += "--end-date"
                $args += $endDate
                Write-Host "✅ 將查詢 $startDate 到 $endDate 的資料" -ForegroundColor Green
            } else {
                Write-Host "❌ 結束日期格式錯誤，使用預設範圍" -ForegroundColor Yellow
            }
        } elseif ($startDate) {
            Write-Host "❌ 開始日期格式錯誤，使用預設範圍" -ForegroundColor Yellow
        } else {
            Write-Host "✅ 使用預設範圍：過去7天" -ForegroundColor Green
        }
        Write-Host ""
    }

    # 顯示執行命令
    $commandStr = "uv run python -u src/scrapers/payment_scraper.py"
    if ($args.Count -gt 0) {
        $commandStr += " " + ($args -join " ")
    }
    Write-Host "🚀 執行命令: $commandStr" -ForegroundColor Blue
    Write-Host ""

    # 執行 Python 程式
    Write-Host "🚀 啟動代收貨款匯款明細查詢功能" -ForegroundColor Blue
    Write-Host ""
    & uv run python -u src/scrapers/payment_scraper.py @args

    # 檢查執行結果
    Test-ExecutionResult -ExitCode $LASTEXITCODE

} catch {
    Write-Host "❌ 執行過程中發生錯誤：$($_.Exception.Message)" -ForegroundColor Red
    Test-ExecutionResult -ExitCode 1
}

Write-Host ""
Read-Host "按 Enter 鍵繼續..."
