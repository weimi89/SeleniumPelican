# WEDI 運費未請款明細下載工具執行腳本 (PowerShell)
# 自動設定環境變數並執行程式

# 設定 UTF-8 編碼
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$PSDefaultParameterValues['*:Encoding'] = 'utf8'

Write-Host "🔧 設定環境變數..." -ForegroundColor Cyan
$env:PYTHONUNBUFFERED = "1"
$env:PYTHONPATH = (Get-Location).Path

Write-Host ""
Write-Host "📊 WEDI 運費未請款明細下載工具" -ForegroundColor Green
Write-Host "📅 結束時間: $((Get-Date).ToString('yyyyMMdd')) (當日)" -ForegroundColor Yellow
Write-Host ""

# 執行程式
try {
    uv run python -u src/scrapers/unpaid_scraper.py @args
} catch {
    Write-Host "❌ 執行失敗: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "✅ 執行完成" -ForegroundColor Green

# 只有在直接執行時才暫停
if ($MyInvocation.InvocationName -ne "&") {
    Write-Host "按任意鍵繼續..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}