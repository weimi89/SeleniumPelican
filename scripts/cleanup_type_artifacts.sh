#!/usr/bin/env bash
# -*- coding: utf-8 -*-

###############################################################################
# 型別檢查暫存檔案清理腳本 (Bash)
#
# 用途：清理所有 mypy 和型別檢查相關的暫存檔案、快取和報告
# 使用：./scripts/cleanup_type_artifacts.sh
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

set -e  # 遇到錯誤立即停止

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 計數器
REMOVED_COUNT=0
SKIPPED_COUNT=0

# 取得專案根目錄（腳本所在目錄的上一層）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}型別檢查暫存檔案清理工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${BLUE}專案目錄：${NC}$PROJECT_ROOT"
echo ""

cd "$PROJECT_ROOT"

# 函數：清理目錄
cleanup_directory() {
    local dir_pattern=$1
    local description=$2

    echo -e "${YELLOW}檢查 ${description}...${NC}"

    # 使用 find 尋找符合模式的目錄
    while IFS= read -r dir; do
        if [ -d "$dir" ]; then
            echo -e "  ${RED}✗${NC} 刪除: $dir"
            rm -rf "$dir"
            ((REMOVED_COUNT++))
        fi
    done < <(find . -type d -name "$dir_pattern" 2>/dev/null)

    # 如果沒有找到任何目錄
    if [ $REMOVED_COUNT -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} 未發現 ${description}"
        ((SKIPPED_COUNT++))
    fi
}

# 函數：清理檔案
cleanup_file() {
    local file_pattern=$1
    local description=$2

    echo -e "${YELLOW}檢查 ${description}...${NC}"

    local found=0
    # 使用 find 尋找符合模式的檔案
    while IFS= read -r file; do
        if [ -f "$file" ]; then
            echo -e "  ${RED}✗${NC} 刪除: $file"
            rm -f "$file"
            ((REMOVED_COUNT++))
            found=1
        fi
    done < <(find . -type f -name "$file_pattern" 2>/dev/null)

    # 如果沒有找到任何檔案
    if [ $found -eq 0 ]; then
        echo -e "  ${GREEN}✓${NC} 未發現 ${description}"
        ((SKIPPED_COUNT++))
    fi
}

echo -e "${BLUE}開始清理型別檢查相關檔案...${NC}"
echo ""

# 1. 清理 .mypy_cache 目錄
cleanup_directory ".mypy_cache" "Mypy 快取目錄 (.mypy_cache)"

# 2. 清理 .dmypy.json
cleanup_file ".dmypy.json" "dmypy 設定檔 (.dmypy.json)"

# 3. 清理 dmypy.json
cleanup_file "dmypy.json" "dmypy 設定檔 (dmypy.json)"

# 4. 清理 mypy-html 報告目錄
cleanup_directory "mypy-html" "Mypy HTML 報告目錄 (mypy-html)"

# 5. 清理 mypy-report 報告目錄
cleanup_directory "mypy-report" "Mypy 文字報告目錄 (mypy-report)"

# 可選：清理 Python 快取檔案
echo ""
echo -e "${YELLOW}是否要清理 Python 快取檔案？ (y/N)${NC}"
read -r response
response=${response,,}  # 轉換為小寫

if [[ "$response" == "y" || "$response" == "yes" ]]; then
    echo ""
    echo -e "${BLUE}清理 Python 快取檔案...${NC}"

    # 清理 __pycache__ 目錄
    cleanup_directory "__pycache__" "Python 快取目錄 (__pycache__)"

    # 清理 .pyc 檔案
    cleanup_file "*.pyc" "Python 編譯檔案 (*.pyc)"

    # 清理 .pyo 檔案
    cleanup_file "*.pyo" "Python 優化檔案 (*.pyo)"
else
    echo -e "${GREEN}跳過 Python 快取檔案清理${NC}"
fi

# 總結
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}清理完成總結${NC}"
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ 已刪除項目：${REMOVED_COUNT}${NC}"
echo -e "${YELLOW}○ 未發現項目：${SKIPPED_COUNT}${NC}"
echo ""

if [ $REMOVED_COUNT -eq 0 ]; then
    echo -e "${GREEN}✓ 專案已經很乾淨，無需清理！${NC}"
else
    echo -e "${GREEN}✓ 清理完成！專案目錄已整理乾淨。${NC}"
fi

echo ""
echo -e "${BLUE}提示：您可以執行以下命令重新產生型別檢查報告：${NC}"
echo -e "${YELLOW}  uv run mypy src/${NC}"
echo -e "${YELLOW}  uv run mypy --html-report mypy-html src/${NC}"
echo ""

exit 0
