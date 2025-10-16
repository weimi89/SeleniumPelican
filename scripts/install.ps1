# SeleniumPelican 安裝工具 - PowerShell 7 版本

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 確保在正確的專案目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

Write-Host "📦 SeleniumPelican 安裝工具" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔍 檢查系統環境..." -ForegroundColor Yellow

# 檢查 Python
try {
    $pythonVersion = & python --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Python: $pythonVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ Python 未安裝或無法執行" -ForegroundColor Red
        Write-Host "請先安裝 Python 3.8+: https://www.python.org/" -ForegroundColor Yellow
        Read-Host "按 Enter 鍵繼續..."
        exit 1
    }
} catch {
    Write-Host "❌ Python 未安裝或無法執行" -ForegroundColor Red
    Write-Host "請先安裝 Python 3.8+: https://www.python.org/" -ForegroundColor Yellow
    Read-Host "按 Enter 鍵繼續..."
    exit 1
}

# 檢查 Git
try {
    $gitVersion = & git --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Git 未安裝，建議安裝以獲得完整功能" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Git 未安裝，建議安裝以獲得完整功能" -ForegroundColor Yellow
}

# 檢查 Chrome 瀏覽器
$chromeInstalled = $false
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

foreach ($chromePath in $chromePaths) {
    if (Test-Path $chromePath) {
        Write-Host "✅ Chrome: 已安裝 ($chromePath)" -ForegroundColor Green
        $chromeInstalled = $true
        break
    }
}

if (-not $chromeInstalled) {
    Write-Host "❌ Google Chrome 未找到" -ForegroundColor Red
    Write-Host "請先安裝 Google Chrome: https://www.google.com/chrome/" -ForegroundColor Yellow
    Read-Host "按 Enter 鍵繼續..."
    exit 1
}

Write-Host ""
Write-Host "🚀 開始安裝 SeleniumPelican..." -ForegroundColor Blue
Write-Host ""

# 步驟 1: 檢查並安裝 uv
Write-Host "📋 步驟 1: 安裝 UV 包管理器" -ForegroundColor Yellow
try {
    $uvVersion = & uv --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ uv 已安裝: $uvVersion" -ForegroundColor Green
    } else {
        throw "uv 未安裝"
    }
} catch {
    Write-Host "⬇️ 正在安裝 UV..." -ForegroundColor Blue
    try {
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        # 重新載入環境變數
        $env:PATH = [System.Environment]::GetEnvironmentVariable("PATH", "Machine") + ";" + [System.Environment]::GetEnvironmentVariable("PATH", "User")
        $uvVersion = & uv --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ UV 安裝成功: $uvVersion" -ForegroundColor Green
        } else {
            throw "UV 安裝失敗"
        }
    } catch {
        Write-Host "❌ UV 安裝失敗，請手動安裝: https://docs.astral.sh/uv/" -ForegroundColor Red
        Read-Host "按 Enter 鍵繼續..."
        exit 1
    }
}

# 步驟 2: 建立虛擬環境並安裝依賴
Write-Host ""
Write-Host "📋 步驟 2: 建立虛擬環境並安裝依賴" -ForegroundColor Yellow
try {
    Write-Host "⬇️ 正在執行: uv sync" -ForegroundColor Blue
    & uv sync
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 虛擬環境建立成功" -ForegroundColor Green
    } else {
        throw "虛擬環境建立失敗"
    }
} catch {
    Write-Host "❌ 虛擬環境建立失敗: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "按 Enter 鍵繼續..."
    exit 1
}

# 步驟 3: 設定配置檔案
Write-Host ""
Write-Host "📋 步驟 3: 設定配置檔案" -ForegroundColor Yellow

# 建立 .env 檔案
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "✅ 已建立 .env 檔案" -ForegroundColor Green
        Write-Host "⚠️ 請編輯 .env 檔案並設定正確的 Chrome 路徑" -ForegroundColor Yellow
    } else {
        Write-Host "❌ 找不到 .env.example 檔案" -ForegroundColor Red
    }
} else {
    Write-Host "ℹ️ .env 檔案已存在" -ForegroundColor Blue
}

# 建立 accounts.json 檔案
if (-not (Test-Path "accounts.json")) {
    if (Test-Path "accounts.json.example") {
        Copy-Item "accounts.json.example" "accounts.json"
        Write-Host "✅ 已建立 accounts.json 檔案" -ForegroundColor Green
        Write-Host "⚠️ 請編輯 accounts.json 檔案並填入實際的帳號資訊" -ForegroundColor Yellow
    } else {
        Write-Host "❌ 找不到 accounts.json.example 檔案" -ForegroundColor Red
    }
} else {
    Write-Host "ℹ️ accounts.json 檔案已存在" -ForegroundColor Blue
}

# 步驟 4: 建立必要目錄
Write-Host ""
Write-Host "📋 步驟 4: 建立必要目錄" -ForegroundColor Yellow

$directories = @("downloads", "logs", "temp", "reports")
foreach ($dir in $directories) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
        Write-Host "✅ 已建立目錄: $dir" -ForegroundColor Green
    } else {
        Write-Host "ℹ️ 目錄已存在: $dir" -ForegroundColor Blue
    }
}

# 步驟 5: 執行配置驗證
Write-Host ""
Write-Host "📋 步驟 5: 執行配置驗證" -ForegroundColor Yellow
try {
    $env:PYTHONPATH = $PWD.Path
    $env:PYTHONUNBUFFERED = "1"
    Write-Host "🔍 正在執行配置驗證..." -ForegroundColor Blue
    & uv run python -m src.core.config_validator --create
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 配置驗證通過" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 配置驗證發現問題，請檢查上方詳細資訊" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 配置驗證執行失敗: $($_.Exception.Message)" -ForegroundColor Red
}

# 步驟 6: 執行測試
Write-Host ""
Write-Host "📋 步驟 6: 執行基本測試" -ForegroundColor Yellow
try {
    Write-Host "🧪 正在執行基本測試..." -ForegroundColor Blue
    & uv run python -c "
from src.core.browser_utils import init_chrome_browser
print('🔍 測試瀏覽器初始化...')
try:
    driver, wait = init_chrome_browser(headless=True)
    print('✅ Chrome WebDriver 啟動成功')
    driver.quit()
    print('✅ 基本功能測試通過')
except Exception as e:
    print(f'❌ 基本功能測試失敗: {e}')
    exit(1)
"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 基本測試通過" -ForegroundColor Green
    } else {
        Write-Host "❌ 基本測試失敗" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ 測試執行失敗: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 SeleniumPelican 安裝完成！" -ForegroundColor Green
Write-Host ""
Write-Host "📝 後續步驟：" -ForegroundColor Yellow
Write-Host "1. 編輯 .env 檔案，設定正確的 Chrome 路徑" -ForegroundColor White
Write-Host "2. 編輯 accounts.json 檔案，填入實際的帳號資訊" -ForegroundColor White
Write-Host "3. 執行配置驗證：Windows_配置驗證.cmd" -ForegroundColor White
Write-Host "4. 開始使用各項功能" -ForegroundColor White
Write-Host ""
Write-Host "🚀 可用的執行腳本：" -ForegroundColor Yellow
Write-Host "• Windows_代收貨款查詢.cmd - 代收貨款匯款明細查詢" -ForegroundColor Cyan
Write-Host "• Windows_運費查詢.cmd - 運費(月結)結帳資料查詢" -ForegroundColor Cyan
Write-Host "• Windows_運費未請款明細.cmd - 運費未請款明細下載" -ForegroundColor Cyan
Write-Host "• Windows_配置驗證.cmd - 配置檔案驗證工具" -ForegroundColor Cyan

Write-Host ""
Read-Host "按 Enter 鍵繼續..."
