#!/usr/bin/env pwsh
# -*- coding: utf-8 -*-

###############################################################################
# 型別檢查暫存檔案清理腳本 (PowerShell)
#
# 用途：清理所有 mypy 和型別檢查相關的暫存檔案、快取和報告
# 使用：.\scripts\cleanup_type_artifacts.ps1
#       或 pwsh scripts/cleanup_type_artifacts.ps1
#
# 清理項目：
# - .mypy_cache/ 目錄
# - .dmypy.json 檔案
# - dmypy.json 檔案
# - mypy-html/ 報告目錄
# - mypy-report/ 報告目錄
# - __pycache__/ 目錄（可選）
# - *.pyc 檔案（可選）
###############################################################################

# 設定錯誤處理
$ErrorActionPreference = "Stop"

# 計數器
$script:RemovedCount = 0
$script:SkippedCount = 0

# 取得專案根目錄（腳本所在目錄的上一層）
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir

# 顏色函數
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "型別檢查暫存檔案清理工具" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-Host ""
Write-ColorOutput "專案目錄：$ProjectRoot" "Cyan"
Write-Host ""

Set-Location $ProjectRoot

# 函數：清理目錄
function Remove-Directories {
    param(
        [string]$Pattern,
        [string]$Description
    )

    Write-ColorOutput "檢查 ${Description}..." "Yellow"

    $dirs = Get-ChildItem -Path . -Recurse -Directory -Filter $Pattern -ErrorAction SilentlyContinue

    if ($dirs) {
        foreach ($dir in $dirs) {
            Write-ColorOutput "  ✗ 刪除: $($dir.FullName)" "Red"
            Remove-Item -Path $dir.FullName -Recurse -Force
            $script:RemovedCount++
        }
    }
    else {
        Write-ColorOutput "  ✓ 未發現 ${Description}" "Green"
        $script:SkippedCount++
    }
}

# 函數：清理檔案
function Remove-Files {
    param(
        [string]$Pattern,
        [string]$Description
    )

    Write-ColorOutput "檢查 ${Description}..." "Yellow"

    $files = Get-ChildItem -Path . -Recurse -File -Filter $Pattern -ErrorAction SilentlyContinue

    if ($files) {
        foreach ($file in $files) {
            Write-ColorOutput "  ✗ 刪除: $($file.FullName)" "Red"
            Remove-Item -Path $file.FullName -Force
            $script:RemovedCount++
        }
    }
    else {
        Write-ColorOutput "  ✓ 未發現 ${Description}" "Green"
        $script:SkippedCount++
    }
}

Write-ColorOutput "開始清理型別檢查相關檔案..." "Cyan"
Write-Host ""

# 1. 清理 .mypy_cache 目錄
Remove-Directories -Pattern ".mypy_cache" -Description "Mypy 快取目錄 (.mypy_cache)"

# 2. 清理 .dmypy.json
Remove-Files -Pattern ".dmypy.json" -Description "dmypy 設定檔 (.dmypy.json)"

# 3. 清理 dmypy.json
Remove-Files -Pattern "dmypy.json" -Description "dmypy 設定檔 (dmypy.json)"

# 4. 清理 mypy-html 報告目錄
Remove-Directories -Pattern "mypy-html" -Description "Mypy HTML 報告目錄 (mypy-html)"

# 5. 清理 mypy-report 報告目錄
Remove-Directories -Pattern "mypy-report" -Description "Mypy 文字報告目錄 (mypy-report)"

# 可選：清理 Python 快取檔案
Write-Host ""
Write-ColorOutput "是否要清理 Python 快取檔案？ (y/N)" "Yellow"
$response = Read-Host

if ($response -ieq "y" -or $response -ieq "yes") {
    Write-Host ""
    Write-ColorOutput "清理 Python 快取檔案..." "Cyan"

    # 清理 __pycache__ 目錄
    Remove-Directories -Pattern "__pycache__" -Description "Python 快取目錄 (__pycache__)"

    # 清理 .pyc 檔案
    Remove-Files -Pattern "*.pyc" -Description "Python 編譯檔案 (*.pyc)"

    # 清理 .pyo 檔案
    Remove-Files -Pattern "*.pyo" -Description "Python 優化檔案 (*.pyo)"
}
else {
    Write-ColorOutput "跳過 Python 快取檔案清理" "Green"
}

# 總結
Write-Host ""
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "清理完成總結" "Cyan"
Write-ColorOutput "========================================" "Cyan"
Write-ColorOutput "✓ 已刪除項目：$RemovedCount" "Green"
Write-ColorOutput "○ 未發現項目：$SkippedCount" "Yellow"
Write-Host ""

if ($RemovedCount -eq 0) {
    Write-ColorOutput "✓ 專案已經很乾淨，無需清理！" "Green"
}
else {
    Write-ColorOutput "✓ 清理完成！專案目錄已整理乾淨。" "Green"
}

Write-Host ""
Write-ColorOutput "提示：您可以執行以下命令重新產生型別檢查報告：" "Cyan"
Write-ColorOutput "  uv run mypy src/" "Yellow"
Write-ColorOutput "  uv run mypy --html-report mypy-html src/" "Yellow"
Write-Host ""

exit 0
