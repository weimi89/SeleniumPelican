#!/bin/bash
# -*- coding: utf-8 -*-

###############################################################################
# Ubuntu 環境驗證腳本
# 功能: 驗證 SeleniumPelican 所需的所有配置是否正確
###############################################################################

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 計數器
TOTAL_CHECKS=0
PASSED_CHECKS=0

# 輔助函式
print_check() {
    TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
    echo -ne "${BLUE}[$TOTAL_CHECKS] $1...${NC} "
}

print_pass() {
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
    echo -e "${GREEN}✅ $1${NC}"
}

print_fail() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# 取得專案根目錄
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo ""
echo "═══════════════════════════════════════"
echo "  Ubuntu 環境驗證"
echo "═══════════════════════════════════════"
echo ""

# 1. 檢查 Python 版本
print_check "檢查 Python 版本"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        print_pass "Python $PYTHON_VERSION"
    else
        print_fail "Python 版本過舊: $PYTHON_VERSION (需要 >= 3.8)"
    fi
else
    print_fail "未找到 Python 3"
    print_info "安裝: sudo apt install python3"
fi

# 2. 檢查 Chromium
print_check "檢查 Chromium 瀏覽器"
if command -v chromium-browser &> /dev/null; then
    CHROMIUM_VERSION=$(chromium-browser --version 2>/dev/null || echo "unknown")
    CHROMIUM_PATH=$(which chromium-browser)

    if [ -x "$CHROMIUM_PATH" ]; then
        print_pass "$CHROMIUM_VERSION ($CHROMIUM_PATH)"
    else
        print_fail "Chromium 不可執行"
        print_info "權限: ls -la $CHROMIUM_PATH"
    fi
else
    print_fail "未找到 Chromium"
    print_info "安裝: sudo apt install chromium-browser"
fi

# 3. 檢查 ChromeDriver
print_check "檢查 ChromeDriver"
if command -v chromedriver &> /dev/null; then
    CHROMEDRIVER_VERSION=$(chromedriver --version 2>/dev/null | cut -d' ' -f2 || echo "unknown")
    CHROMEDRIVER_PATH=$(which chromedriver)

    if [ -x "$CHROMEDRIVER_PATH" ]; then
        print_pass "版本 $CHROMEDRIVER_VERSION ($CHROMEDRIVER_PATH)"
    else
        print_fail "ChromeDriver 不可執行"
        print_info "權限: ls -la $CHROMEDRIVER_PATH"
    fi
else
    print_fail "未找到 ChromeDriver"
    print_info "安裝: sudo apt install chromium-chromedriver"
fi

# 4. 檢查版本相容性
print_check "檢查 Chromium 和 ChromeDriver 版本相容性"
if command -v chromium-browser &> /dev/null && command -v chromedriver &> /dev/null; then
    CHROMIUM_MAJOR=$(chromium-browser --version 2>/dev/null | grep -oP '\d+' | head -1)
    CHROMEDRIVER_MAJOR=$(chromedriver --version 2>/dev/null | grep -oP '\d+' | head -1)

    if [ -n "$CHROMIUM_MAJOR" ] && [ -n "$CHROMEDRIVER_MAJOR" ]; then
        if [ "$CHROMIUM_MAJOR" -eq "$CHROMEDRIVER_MAJOR" ]; then
            print_pass "版本匹配 ($CHROMIUM_MAJOR.x)"
        else
            print_warning "版本可能不匹配 (Chromium: $CHROMIUM_MAJOR.x, ChromeDriver: $CHROMEDRIVER_MAJOR.x)"
            print_info "修復: sudo apt install --reinstall chromium-browser chromium-chromedriver"
        fi
    else
        print_warning "無法取得版本號碼"
    fi
else
    print_fail "缺少 Chromium 或 ChromeDriver"
fi

# 5. 檢查 .env 檔案
print_check "檢查 .env 檔案配置"
ENV_FILE="$PROJECT_ROOT/.env"

if [ -f "$ENV_FILE" ]; then
    # 檢查 CHROME_BINARY_PATH
    CHROME_BINARY_PATH=$(grep "^CHROME_BINARY_PATH=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'")
    if [ -n "$CHROME_BINARY_PATH" ]; then
        if [ -f "$CHROME_BINARY_PATH" ] && [ -x "$CHROME_BINARY_PATH" ]; then
            print_pass ".env 存在且配置正確"
        else
            print_fail "CHROME_BINARY_PATH 路徑無效: $CHROME_BINARY_PATH"
            SUGGESTED_PATH=$(which chromium-browser 2>/dev/null || echo "/usr/bin/chromium-browser")
            print_info "建議設定為: $SUGGESTED_PATH"
        fi
    else
        print_warning ".env 檔案缺少 CHROME_BINARY_PATH"
        print_info "執行: ./scripts/ubuntu_quick_setup.sh 重新配置"
    fi
else
    print_fail ".env 檔案不存在"
    print_info "執行: ./scripts/ubuntu_quick_setup.sh 建立配置"
fi

# 6. 檢查 accounts.json
print_check "檢查 accounts.json 檔案"
ACCOUNTS_FILE="$PROJECT_ROOT/accounts.json"

if [ -f "$ACCOUNTS_FILE" ]; then
    print_pass "accounts.json 存在"
else
    print_fail "accounts.json 不存在"
    print_info "複製範例: cp accounts.json.example accounts.json"
fi

# 6.1 檢查 .env 中的 HEADLESS 設定
print_check "檢查 HEADLESS 模式設定"
if [ -f "$ENV_FILE" ]; then
    HEADLESS_VALUE=$(grep "^HEADLESS=" "$ENV_FILE" | cut -d'=' -f2 | tr -d '"' | tr -d "'" | tr '[:upper:]' '[:lower:]')
    if [ "$HEADLESS_VALUE" = "true" ]; then
        print_pass "HEADLESS 模式已啟用（適合無頭環境）"
    elif [ "$HEADLESS_VALUE" = "false" ]; then
        print_warning "HEADLESS 模式未啟用"
        print_info "Ubuntu 無頭環境建議在 .env 設定: HEADLESS=true"
    else
        print_warning ".env 檔案缺少 HEADLESS 設定"
        print_info "Ubuntu 無頭環境建議在 .env 新增: HEADLESS=true"
    fi
else
    print_warning "無法檢查 HEADLESS 設定（.env 不存在）"
fi

# 7. 檢查目錄權限
print_check "檢查目錄結構與權限"
REQUIRED_DIRS=("downloads" "logs")
ALL_DIRS_OK=true

for dir in "${REQUIRED_DIRS[@]}"; do
    DIR_PATH="$PROJECT_ROOT/$dir"
    if [ -d "$DIR_PATH" ] && [ -w "$DIR_PATH" ]; then
        true  # 目錄存在且可寫
    else
        ALL_DIRS_OK=false
        break
    fi
done

if [ "$ALL_DIRS_OK" = true ]; then
    print_pass "所有必要目錄存在且可寫"
else
    print_fail "部分目錄缺少或無寫入權限"
    print_info "執行: mkdir -p downloads logs && chmod 755 downloads logs"
fi

# 總結
echo ""
echo "═══════════════════════════════════════"
echo "  驗證結果: $PASSED_CHECKS/$TOTAL_CHECKS 項檢查通過"
echo "═══════════════════════════════════════"
echo ""

if [ "$PASSED_CHECKS" -eq "$TOTAL_CHECKS" ]; then
    echo -e "${GREEN}✅ 環境配置完全正確！可以開始使用${NC}"
    echo ""
    print_info "下一步: 執行瀏覽器功能測試"
    echo "  python3 src/utils/browser_tester.py"
    exit 0
elif [ "$PASSED_CHECKS" -ge $((TOTAL_CHECKS * 2 / 3)) ]; then
    echo -e "${YELLOW}⚠️  大部分檢查通過，但仍有些問題需要修復${NC}"
    echo ""
    print_info "建議: 檢查上述失敗的項目並修復"
    exit 1
else
    echo -e "${RED}❌ 環境配置有嚴重問題${NC}"
    echo ""
    print_info "建議: 執行以下命令重新配置"
    echo "  ./scripts/ubuntu_quick_setup.sh"
    exit 1
fi
