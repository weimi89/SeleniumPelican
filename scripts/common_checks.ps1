# SeleniumPelican 共用檢查函數 - PowerShell 版本

function Test-Environment {
    """檢查執行環境"""

    Write-Host "🔍 檢查執行環境..." -ForegroundColor Yellow

    # 檢查 Python 和 uv
    try {
        $uvVersion = & uv --version 2>$null
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ uv: $uvVersion" -ForegroundColor Green
        } else {
            Write-Host "❌ uv 未安裝或無法執行" -ForegroundColor Red
            Write-Host "請先安裝 uv: https://docs.astral.sh/uv/" -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "❌ uv 未安裝或無法執行" -ForegroundColor Red
        Write-Host "請先安裝 uv: https://docs.astral.sh/uv/" -ForegroundColor Yellow
        exit 1
    }

    # 檢查虛擬環境
    if (Test-Path ".venv") {
        Write-Host "✅ 虛擬環境: .venv 存在" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 虛擬環境: .venv 不存在，將自動建立" -ForegroundColor Yellow
        Write-Host "🚀 執行: uv sync" -ForegroundColor Blue
        & uv sync
        if ($LASTEXITCODE -ne 0) {
            Write-Host "❌ 無法建立虛擬環境" -ForegroundColor Red
            exit 1
        }
    }

    # 檢查配置檔案
    if (Test-Path "accounts.json") {
        Write-Host "✅ 配置檔案: accounts.json 存在" -ForegroundColor Green

        # 使用配置驗證系統
        try {
            Write-Host "🔍 執行配置驗證..." -ForegroundColor Yellow
            $env:PYTHONPATH = $PWD.Path
            & uv run python -c "from src.core.config_validator import validate_config_files; validate_config_files(show_report=False)" 2>$null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 配置檔案驗證通過" -ForegroundColor Green
            } else {
                Write-Host "⚠️ 配置檔案有問題，建議執行詳細檢查:" -ForegroundColor Yellow
                Write-Host "   uv run python -m src.core.config_validator" -ForegroundColor Cyan
            }
        } catch {
            Write-Host "⚠️ 無法執行配置驗證，請檢查程式是否正常" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ 配置檔案: accounts.json 不存在" -ForegroundColor Red
        if (Test-Path "accounts.json.example") {
            Write-Host "💡 請複製 accounts.json.example 並填入實際帳號資訊:" -ForegroundColor Yellow
            Write-Host "   copy accounts.json.example accounts.json" -ForegroundColor Cyan
        }
        exit 1
    }

    # 檢查 .env 檔案
    if (Test-Path ".env") {
        Write-Host "✅ 環境設定: .env 存在" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 環境設定: .env 不存在" -ForegroundColor Yellow
        if (Test-Path ".env.example") {
            Write-Host "💡 建議複製範例檔案:" -ForegroundColor Yellow
            Write-Host "   copy .env.example .env" -ForegroundColor Cyan
        }
    }

    # 設定必要的環境變數
    $env:PYTHONUNBUFFERED = "1"

    Write-Host "✅ 環境檢查完成" -ForegroundColor Green
    Write-Host ""
}

function Test-ExecutionResult {
    param(
        [int]$ExitCode
    )

    Write-Host ""
    if ($ExitCode -eq 0) {
        Write-Host "🎉 執行完成！" -ForegroundColor Green
    } else {
        Write-Host "❌ 執行失敗 (退出碼: $ExitCode)" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 疑難排解建議：" -ForegroundColor Yellow
        Write-Host "1. 檢查網路連線是否正常" -ForegroundColor White
        Write-Host "2. 確認帳號密碼是否正確" -ForegroundColor White
        Write-Host "3. 檢查 Chrome 瀏覽器是否正常啟動" -ForegroundColor White
        Write-Host "4. 查看 logs/ 目錄下的詳細日誌" -ForegroundColor White
        Write-Host ""
        Write-Host "🔧 執行配置檢查：" -ForegroundColor Yellow
        Write-Host "   uv run python -m src.core.config_validator" -ForegroundColor Cyan
    }
}