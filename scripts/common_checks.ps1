# WEDI 工具共用檢查函數 - PowerShell 7 版本
# 此腳本包含所有執行腳本需要的共用檢查邏輯

function Test-Environment {
    # 檢查 uv 是否安裝
    try {
        $null = uv --version
    } catch {
        Write-Host "❌ 系統元件遺失，請重新安裝程式" -ForegroundColor Red
        Read-Host "按 Enter 鍵繼續..."
        exit 1
    }

    # 檢查是否有 .venv 目錄，如果沒有就建立
    if (-not (Test-Path ".venv")) {
        Write-Host "🔧 正在初始化..." -ForegroundColor Yellow
        uv venv | Out-Null
    }

    # 同步依賴套件
    Write-Host "📦 檢查程式元件..." -ForegroundColor Yellow
    uv sync | Out-Null

    # 設定環境變數確保即時輸出
    $env:PYTHONUNBUFFERED = "1"

    # 檢查設定檔案
    if (-not (Test-Path "accounts.json")) {
        Write-Host "❌ 找不到 accounts.json 設定檔案" -ForegroundColor Red
        Write-Host "請參考 accounts.json.example 建立設定檔案" -ForegroundColor Yellow
        Read-Host "按 Enter 鍵繼續..."
        exit 1
    }
}

function Test-ExecutionResult {
    param(
        [int]$ExitCode
    )
    
    Write-Host ""
    if ($ExitCode -eq 0) {
        Write-Host "✅ 執行完成" -ForegroundColor Green
    } else {
        Write-Host "❌ 執行時發生錯誤" -ForegroundColor Red
    }
}