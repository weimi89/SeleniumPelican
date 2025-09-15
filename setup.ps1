# WEDI 宅配通自動下載工具 - PowerShell 7 安裝腳本
# 需要 PowerShell 7+ 支援

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 確保在正確的專案目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "🔧 安裝 WEDI 宅配通自動下載工具 - PowerShell 版本" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "🔍 專案路徑: $scriptPath" -ForegroundColor Blue
Write-Host ""

try {
    Write-Host "📦 步驟 1: 安裝 uv..." -ForegroundColor Yellow
    pip install uv
    if ($LASTEXITCODE -ne 0) {
        throw "pip install uv 失敗"
    }

    Write-Host "🔧 步驟 2: 建立虛擬環境..." -ForegroundColor Yellow
    uv venv
    if ($LASTEXITCODE -ne 0) {
        throw "建立虛擬環境失敗"
    }

    Write-Host "📦 步驟 3: 安裝依賴套件..." -ForegroundColor Yellow
    uv sync
    if ($LASTEXITCODE -ne 0) {
        throw "安裝依賴套件失敗"
    }

    Write-Host "🌐 步驟 4: 設定 Chrome 路徑..." -ForegroundColor Yellow
    if (-not (Test-Path ".env")) {
        'CHROME_BINARY_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"' | Out-File -FilePath ".env" -Encoding UTF8
        Write-Host "✅ Chrome 路徑已設定為預設 Windows 位置" -ForegroundColor Green
        Write-Host "💡 如果您的 Chrome 安裝在其他位置，請編輯 .env 檔案" -ForegroundColor Blue
    }

    Write-Host "👤 步驟 5: 建立帳號設定範例..." -ForegroundColor Yellow
    if (-not (Test-Path "accounts.json")) {
        if (Test-Path "accounts.json.example") {
            Copy-Item "accounts.json.example" "accounts.json"
        }
        Write-Host "✅ 請編輯 accounts.json 檔案以新增您的登入憑證" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "🎉 安裝完成！" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 後續步驟：" -ForegroundColor Cyan
    Write-Host "1. 編輯 accounts.json 檔案，新增您的 WEDI 登入憑證"
    Write-Host "2. 執行程式：./run_payment.ps1 或 ./run_freight.ps1"
    Write-Host ""
    Write-Host "💡 如果遇到任何問題，請查看 README.md" -ForegroundColor Blue

} catch {
    Write-Host ""
    Write-Host "❌ 安裝過程中發生錯誤：$($_.Exception.Message)" -ForegroundColor Red
    Write-Host "請檢查錯誤訊息並重試" -ForegroundColor Red
    exit 1
}

Write-Host ""
Read-Host "按 Enter 鍵繼續..."