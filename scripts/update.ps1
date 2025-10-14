# SeleniumPelican 更新工具 - PowerShell 7 版本

$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 確保在正確的專案目錄
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectPath = Split-Path -Parent $scriptPath
Set-Location $projectPath

Write-Host "🔄 SeleniumPelican 更新工具" -ForegroundColor Cyan
Write-Host "==========================" -ForegroundColor Cyan
Write-Host ""

Write-Host "🔍 檢查更新環境..." -ForegroundColor Yellow

# 檢查 Git
$gitAvailable = $false
try {
    $gitVersion = & git --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Git: $gitVersion" -ForegroundColor Green
        $gitAvailable = $true
    }
} catch {
    Write-Host "❌ Git 未安裝，無法執行自動更新" -ForegroundColor Red
}

# 檢查是否為 Git 儲存庫
$isGitRepo = $false
if ($gitAvailable -and (Test-Path ".git")) {
    Write-Host "✅ Git 儲存庫: 偵測到" -ForegroundColor Green
    $isGitRepo = $true
} else {
    Write-Host "❌ Git 儲存庫: 未偵測到" -ForegroundColor Red
}

# 檢查 uv
try {
    $uvVersion = & uv --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ uv: $uvVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ uv 未安裝，請先執行安裝程序" -ForegroundColor Red
        Read-Host "按 Enter 鍵繼續..."
        exit 1
    }
} catch {
    Write-Host "❌ uv 未安裝，請先執行安裝程序" -ForegroundColor Red
    Read-Host "按 Enter 鍵繼續..."
    exit 1
}

Write-Host ""

if (-not $isGitRepo) {
    Write-Host "⚠️ 非 Git 儲存庫，僅執行依賴更新" -ForegroundColor Yellow
    Write-Host ""

    # 步驟 1: 更新依賴
    Write-Host "📋 步驟 1: 更新依賴套件" -ForegroundColor Yellow
    try {
        Write-Host "⬇️ 正在執行: uv sync --upgrade" -ForegroundColor Blue
        & uv sync --upgrade
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ 依賴更新成功" -ForegroundColor Green
        } else {
            throw "依賴更新失敗"
        }
    } catch {
        Write-Host "❌ 依賴更新失敗: $($_.Exception.Message)" -ForegroundColor Red
        Read-Host "按 Enter 鍵繼續..."
        exit 1
    }
} else {
    Write-Host "🚀 開始執行更新程序..." -ForegroundColor Blue
    Write-Host ""

    # 步驟 1: 檢查遠端更新
    Write-Host "📋 步驟 1: 檢查遠端更新" -ForegroundColor Yellow
    try {
        Write-Host "🔍 正在檢查遠端更新..." -ForegroundColor Blue
        & git fetch origin

        $currentBranch = & git branch --show-current
        $localCommit = & git rev-parse HEAD
        $remoteCommit = & git rev-parse "origin/$currentBranch" 2>$null

        if ($localCommit -eq $remoteCommit) {
            Write-Host "ℹ️ 程式碼已是最新版本" -ForegroundColor Blue
            $hasUpdates = $false
        } else {
            Write-Host "🔄 發現遠端更新" -ForegroundColor Green
            $hasUpdates = $true
        }
    } catch {
        Write-Host "❌ 檢查遠端更新失敗: $($_.Exception.Message)" -ForegroundColor Red
        $hasUpdates = $false
    }

    # 步驟 2: 暫存本地變更
    if ($hasUpdates) {
        Write-Host ""
        Write-Host "📋 步驟 2: 處理本地變更" -ForegroundColor Yellow

        $hasLocalChanges = $false
        try {
            $status = & git status --porcelain
            if ($status) {
                Write-Host "💾 發現本地變更，正在暫存..." -ForegroundColor Blue
                $stashMessage = "Auto-stash before update $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
                & git stash push -m $stashMessage
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ 本地變更已暫存" -ForegroundColor Green
                    $hasLocalChanges = $true
                } else {
                    throw "暫存本地變更失敗"
                }
            } else {
                Write-Host "ℹ️ 無本地變更需要暫存" -ForegroundColor Blue
            }
        } catch {
            Write-Host "❌ 處理本地變更失敗: $($_.Exception.Message)" -ForegroundColor Red
        }

        # 步驟 3: 執行更新
        Write-Host ""
        Write-Host "📋 步驟 3: 執行程式碼更新" -ForegroundColor Yellow
        try {
            Write-Host "⬇️ 正在執行: git pull origin $currentBranch" -ForegroundColor Blue
            & git pull origin $currentBranch
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 程式碼更新成功" -ForegroundColor Green
            } else {
                throw "程式碼更新失敗"
            }
        } catch {
            Write-Host "❌ 程式碼更新失敗: $($_.Exception.Message)" -ForegroundColor Red
            if ($hasLocalChanges) {
                Write-Host "🔄 正在還原暫存的變更..." -ForegroundColor Yellow
                & git stash pop
            }
            Read-Host "按 Enter 鍵繼續..."
            exit 1
        }

        # 步驟 4: 還原本地變更
        if ($hasLocalChanges) {
            Write-Host ""
            Write-Host "📋 步驟 4: 還原本地變更" -ForegroundColor Yellow
            try {
                Write-Host "🔄 正在還原暫存的變更..." -ForegroundColor Blue
                & git stash pop
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "✅ 本地變更已還原" -ForegroundColor Green
                } else {
                    Write-Host "⚠️ 還原本地變更時發生衝突，請手動處理" -ForegroundColor Yellow
                    Write-Host "💡 使用 'git status' 查看衝突檔案" -ForegroundColor Cyan
                }
            } catch {
                Write-Host "⚠️ 還原本地變更失敗: $($_.Exception.Message)" -ForegroundColor Yellow
            }
        }
    }

    # 步驟 5: 檢查依賴更新
    Write-Host ""
    Write-Host "📋 步驟 $(if ($hasUpdates) { '5' } else { '2' }): 檢查依賴更新" -ForegroundColor Yellow

    $needsDependencyUpdate = $false
    try {
        if ($hasUpdates) {
            # 檢查 pyproject.toml 是否有變更
            $pyprojectChanged = & git diff HEAD~1 HEAD --name-only | Select-String "pyproject.toml"
            if ($pyprojectChanged) {
                Write-Host "🔄 偵測到 pyproject.toml 變更，需要更新依賴" -ForegroundColor Yellow
                $needsDependencyUpdate = $true
            } else {
                Write-Host "ℹ️ pyproject.toml 無變更，跳過依賴更新" -ForegroundColor Blue
            }
        } else {
            # 無程式碼更新時，詢問是否強制更新依賴
            $choice = Read-Host "是否強制更新依賴套件？ (y/N)"
            if ($choice -eq 'y' -or $choice -eq 'Y') {
                $needsDependencyUpdate = $true
            }
        }

        if ($needsDependencyUpdate) {
            Write-Host "⬇️ 正在執行: uv sync --upgrade" -ForegroundColor Blue
            & uv sync --upgrade
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ 依賴更新成功" -ForegroundColor Green
            } else {
                throw "依賴更新失敗"
            }
        }
    } catch {
        Write-Host "❌ 依賴更新失敗: $($_.Exception.Message)" -ForegroundColor Red
    }
}

# 最後步驟: 執行配置驗證
Write-Host ""
Write-Host "📋 最後步驟: 執行配置驗證" -ForegroundColor Yellow
try {
    $env:PYTHONPATH = $PWD.Path
    $env:PYTHONUNBUFFERED = "1"
    Write-Host "🔍 正在執行配置驗證..." -ForegroundColor Blue
    & uv run python -m src.core.config_validator
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ 配置驗證通過" -ForegroundColor Green
    } else {
        Write-Host "⚠️ 配置驗證發現問題，請檢查上方詳細資訊" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ 配置驗證執行失敗: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
if ($hasUpdates -or $needsDependencyUpdate) {
    Write-Host "🎉 SeleniumPelican 更新完成！" -ForegroundColor Green
} else {
    Write-Host "ℹ️ SeleniumPelican 已是最新狀態！" -ForegroundColor Blue
}

Write-Host ""
Write-Host "📝 建議執行的檢查：" -ForegroundColor Yellow
Write-Host "• Windows_配置驗證.cmd - 驗證配置檔案" -ForegroundColor Cyan
Write-Host "• 測試執行一個腳本確認功能正常" -ForegroundColor Cyan

Write-Host ""
Read-Host "按 Enter 鍵繼續..."