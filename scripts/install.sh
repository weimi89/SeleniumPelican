#!/bin/bash
# SeleniumPelican 安裝工具 - Shell 版本

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 輔助函式
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo ""
echo "📦 SeleniumPelican 安裝工具"
echo "=========================="
echo ""

# 檢查是否為 root 使用者
if [ "$EUID" -eq 0 ]; then
    print_warning "⚠️  偵測到以 root 使用者執行"
    print_info "注意: 某些套件（如 UV）可能需要特殊處理"
    echo ""
fi

print_info "檢查系統環境..."

# 偵測作業系統
IS_LINUX=false
IS_UBUNTU=false
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    IS_LINUX=true
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        if [[ "$ID" == "ubuntu" ]] || [[ "$ID_LIKE" == *"ubuntu"* ]]; then
            IS_UBUNTU=true
            print_info "偵測到 Ubuntu/Debian 系統"
        fi
    fi
fi

# 檢查 Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    print_success "Python: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    print_success "Python: $PYTHON_VERSION"
else
    print_error "Python 未安裝或無法執行"
    echo "請先安裝 Python 3.8+:"
    echo "• Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "• CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "• macOS: brew install python3"
    exit 1
fi

# 檢查 Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    print_success "Git: $GIT_VERSION"
else
    print_warning "Git 未安裝，建議安裝以獲得完整功能"
    echo "• Ubuntu/Debian: sudo apt install git"
    echo "• CentOS/RHEL: sudo yum install git"
    echo "• macOS: brew install git"
fi

# 檢查 Chrome 瀏覽器
CHROME_INSTALLED=false
CHROME_PATH=""
CHROMEDRIVER_PATH=""

# Linux 平台優先檢查 Chromium
if [ "$IS_LINUX" = true ]; then
    CHROME_PATHS=(
        "/usr/bin/chromium-browser"
        "/usr/bin/chromium"
        "/usr/bin/google-chrome"
        "/usr/bin/google-chrome-stable"
        "/opt/google/chrome/chrome"
    )
else
    CHROME_PATHS=(
        "/usr/bin/google-chrome"
        "/usr/bin/google-chrome-stable"
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        "/usr/bin/chromium"
        "/usr/bin/chromium-browser"
        "/opt/google/chrome/chrome"
    )
fi

for chrome_path in "${CHROME_PATHS[@]}"; do
    if [ -x "$chrome_path" ]; then
        print_success "Chrome/Chromium: 已安裝 ($chrome_path)"
        CHROME_INSTALLED=true
        CHROME_PATH="$chrome_path"
        break
    fi
done

# Ubuntu 環境自動安裝 Chromium
if [ "$CHROME_INSTALLED" = false ] && [ "$IS_UBUNTU" = true ]; then
    print_warning "未找到 Chrome/Chromium，將自動安裝 Chromium"
    echo ""
    print_info "正在執行 Ubuntu 自動化設定..."

    # 檢查權限（root 使用者不需要 sudo）
    if [ "$EUID" -ne 0 ]; then
        if ! sudo -v; then
            print_error "需要 sudo 權限安裝系統套件"
            print_info "建議: 使用 root 使用者執行此腳本以避免權限問題"
            exit 1
        fi
        SUDO_CMD="sudo"
    else
        print_info "偵測到 root 使用者，直接安裝系統套件"
        SUDO_CMD=""
    fi

    # 更新套件清單
    print_info "更新系統套件清單..."
    if $SUDO_CMD apt update -qq; then
        print_success "套件清單更新完成"
    else
        print_warning "套件清單更新失敗，但繼續執行"
    fi

    # 安裝 Chromium
    print_info "安裝 Chromium 瀏覽器..."
    if $SUDO_CMD apt install -y chromium-browser; then
        CHROMIUM_VERSION=$(chromium-browser --version 2>/dev/null || echo "unknown")
        print_success "Chromium 安裝完成 ($CHROMIUM_VERSION)"
        CHROME_INSTALLED=true
        CHROME_PATH=$(which chromium-browser 2>/dev/null || echo "/usr/bin/chromium-browser")
    else
        print_error "Chromium 安裝失敗"
        exit 1
    fi

    # 安裝 ChromeDriver
    print_info "安裝 ChromeDriver..."
    if $SUDO_CMD apt install -y chromium-chromedriver; then
        CHROMEDRIVER_VERSION=$(chromedriver --version 2>/dev/null | cut -d' ' -f2 || echo "unknown")
        print_success "ChromeDriver 安裝完成 (版本: $CHROMEDRIVER_VERSION)"
        CHROMEDRIVER_PATH=$(which chromedriver 2>/dev/null || echo "/usr/bin/chromedriver")
    else
        print_error "ChromeDriver 安裝失敗"
        exit 1
    fi

    echo ""
fi

# 如果仍未找到 Chrome/Chromium，則提示手動安裝
if [ "$CHROME_INSTALLED" = false ]; then
    print_error "Google Chrome/Chromium 未找到"
    echo "請先安裝 Google Chrome 或 Chromium:"
    if [ "$IS_LINUX" = true ]; then
        echo "• Ubuntu/Debian: sudo apt install chromium-browser chromium-chromedriver"
        echo "• 或使用 Google Chrome: wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - && sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list' && sudo apt update && sudo apt install google-chrome-stable"
    else
        echo "• macOS: brew install --cask google-chrome"
    fi
    exit 1
fi

echo ""
echo "🚀 開始安裝 SeleniumPelican..."
echo ""

# 步驟 1: 檢查並安裝 uv
echo "📋 步驟 1: 安裝 UV 包管理器"

# 檢測當前使用者
if [ "$EUID" -eq 0 ]; then
    print_info "當前使用者: root"
    UV_INSTALL_DIR="/root/.local/bin"
else
    print_info "當前使用者: $(whoami)"
    UV_INSTALL_DIR="$HOME/.local/bin"
fi

if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo "✅ uv 已安裝: $UV_VERSION"
else
    echo "⬇️ 正在安裝 UV..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        # 更新 PATH
        export PATH="$UV_INSTALL_DIR:$HOME/.cargo/bin:$PATH"

        # 載入環境設定檔（如果存在）
        if [ -f "$UV_INSTALL_DIR/env" ]; then
            source "$UV_INSTALL_DIR/env"
        fi

        # 驗證安裝（嘗試多種方法）
        if command -v uv &> /dev/null; then
            UV_VERSION=$(uv --version)
            echo "✅ UV 安裝成功: $UV_VERSION"
        elif [ -x "$UV_INSTALL_DIR/uv" ]; then
            # 使用絕對路徑
            export PATH="$UV_INSTALL_DIR:$PATH"
            UV_VERSION=$("$UV_INSTALL_DIR/uv" --version)
            echo "✅ UV 安裝成功（使用絕對路徑）: $UV_VERSION"

            # 建立函式代替 alias（在腳本中 alias 不生效）
            uv() { "$UV_INSTALL_DIR/uv" "$@"; }
            export -f uv
        else
            echo "❌ UV 安裝失敗，找不到執行檔"
            echo "預期路徑: $UV_INSTALL_DIR/uv"
            echo "實際情況:"
            ls -la "$UV_INSTALL_DIR/" 2>/dev/null || echo "  目錄不存在"
            echo ""
            echo "請手動安裝: https://docs.astral.sh/uv/"
            echo "提示: 安裝後執行 'source $UV_INSTALL_DIR/env' 然後重新執行此腳本"
            exit 1
        fi
    else
        echo "❌ UV 安裝失敗，請手動安裝: https://docs.astral.sh/uv/"
        exit 1
    fi
fi

# 步驟 2: 建立虛擬環境並安裝依賴
echo ""
echo "📋 步驟 2: 建立虛擬環境並安裝依賴"
echo "⬇️ 正在執行: uv sync"
if uv sync; then
    echo "✅ 虛擬環境建立成功"
else
    echo "❌ 虛擬環境建立失敗"
    exit 1
fi

# 步驟 3: 設定配置檔案
echo ""
echo "📋 步驟 3: 設定配置檔案"

# 建立 .env 檔案
if [ ! -f ".env" ]; then
    # Ubuntu/Linux 環境自動配置 Chromium 路徑
    if [ "$IS_LINUX" = true ] && [ -n "$CHROME_PATH" ]; then
        print_info "配置 .env 檔案（Ubuntu 環境）..."

        # 偵測 ChromeDriver 路徑（如果尚未設定）
        if [ -z "$CHROMEDRIVER_PATH" ]; then
            CHROMEDRIVER_PATH=$(which chromedriver 2>/dev/null || echo "/usr/bin/chromedriver")
        fi

        cat > ".env" <<EOL
# Chrome 瀏覽器路徑（Ubuntu 環境自動配置）
CHROME_BINARY_PATH=$CHROME_PATH
CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH

# 由 scripts/install.sh 自動生成於 $(date)
EOL
        chmod 600 ".env"
        print_success ".env 檔案配置完成"
        print_info "Chrome 路徑: $CHROME_PATH"
        print_info "ChromeDriver 路徑: $CHROMEDRIVER_PATH"
    else
        # 其他平台從範例複製
        if [ -f ".env.example" ]; then
            cp ".env.example" ".env"
            chmod 600 ".env"
            print_success "已建立 .env 檔案"
            print_warning "請編輯 .env 檔案並設定正確的 Chrome 路徑"
        else
            print_error "找不到 .env.example 檔案"
        fi
    fi
else
    print_info ".env 檔案已存在"
    # Ubuntu 環境檢查並更新路徑（如果需要）
    if [ "$IS_LINUX" = true ] && [ -n "$CHROME_PATH" ]; then
        if ! grep -q "CHROME_BINARY_PATH" ".env"; then
            print_info "更新 .env 檔案中的 Chrome 路徑..."
            echo "" >> ".env"
            echo "# Ubuntu 環境路徑（由 scripts/install.sh 更新於 $(date)）" >> ".env"
            echo "CHROME_BINARY_PATH=$CHROME_PATH" >> ".env"
            if [ -n "$CHROMEDRIVER_PATH" ]; then
                echo "CHROMEDRIVER_PATH=$CHROMEDRIVER_PATH" >> ".env"
            fi
            print_success "已更新 .env 檔案"
        fi
    fi
fi

# 建立 accounts.json 檔案
if [ ! -f "accounts.json" ]; then
    if [ -f "accounts.json.example" ]; then
        cp "accounts.json.example" "accounts.json"
        chmod 600 "accounts.json"
        print_success "已建立 accounts.json 檔案"

        # Ubuntu 無頭環境提醒設定 headless: true
        if [ "$IS_UBUNTU" = true ]; then
            print_warning "Ubuntu 無頭環境建議在 accounts.json 中設定 \"headless\": true"
        else
            print_warning "請編輯 accounts.json 檔案並填入實際的帳號資訊"
        fi
    else
        print_error "找不到 accounts.json.example 檔案"
    fi
else
    print_info "accounts.json 檔案已存在"
fi

# 步驟 4: 建立必要目錄
echo ""
echo "📋 步驟 4: 建立必要目錄"

directories=("downloads" "logs" "temp" "reports")
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        chmod 755 "$dir"
        print_success "已建立目錄: $dir"
    else
        print_info "目錄已存在: $dir"
    fi
done

# 步驟 5: 設定執行權限
echo ""
echo "📋 步驟 5: 設定執行權限"
chmod +x Linux_*.sh 2>/dev/null || true
chmod +x scripts/*.sh 2>/dev/null || true
print_success "已設定執行權限"

# 確保敏感檔案有正確的權限
if [ -f ".env" ]; then
    chmod 600 ".env"
fi
if [ -f "accounts.json" ]; then
    chmod 600 "accounts.json"
fi

# 步驟 6: 執行配置驗證
echo ""
echo "📋 步驟 6: 執行配置驗證"
export PYTHONPATH="$(pwd)"
export PYTHONUNBUFFERED=1
echo "🔍 正在執行配置驗證..."
if uv run python -m src.core.config_validator --create; then
    echo "✅ 配置驗證通過"
else
    echo "⚠️ 配置驗證發現問題，請檢查上方詳細資訊"
fi

# 步驟 7: 執行測試
echo ""
echo "📋 步驟 7: 執行基本測試"
echo "🧪 正在執行基本測試..."
if uv run python -c "
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
"; then
    echo "✅ 基本測試通過"
else
    echo "❌ 基本測試失敗"
fi

echo ""
print_success "══════════════════════════════════════"
print_success "  SeleniumPelican 安裝完成！"
print_success "══════════════════════════════════════"
echo ""

# Ubuntu 環境特定提醒
if [ "$IS_UBUNTU" = true ]; then
    print_info "Ubuntu 環境設定完成！"
    echo ""
    print_info "下一步："
    echo "  1. 編輯 accounts.json 檔案，填入實際的帳號資訊"
    echo "  2. 確認 accounts.json 中設定 \"headless\": true（無頭環境）"
    echo "  3. 執行環境驗證: ./scripts/test_ubuntu_env.sh"
    echo "  4. 測試瀏覽器: python3 scripts/test_browser.py"
    echo "  5. 執行配置驗證: ./Linux_配置驗證.sh"
    echo ""
    print_warning "安全提醒:"
    echo "  ⚠️  請勿將 .env 和 accounts.json 提交到版本控制"
    echo "  ⚠️  這些檔案已自動設定為僅擁有者可讀寫（權限 600）"
    echo ""
    print_info "完整文檔: docs/technical/ubuntu-deployment-guide.md"
else
    echo "📝 後續步驟："
    echo "1. 編輯 .env 檔案，設定正確的 Chrome 路徑"
    echo "2. 編輯 accounts.json 檔案，填入實際的帳號資訊"
    echo "3. 執行配置驗證：./Linux_配置驗證.sh"
    echo "4. 開始使用各項功能"
fi

echo ""
echo "🚀 可用的執行腳本："
echo "• ./Linux_代收貨款查詢.sh - 代收貨款匯款明細查詢"
echo "• ./Linux_運費查詢.sh - 運費(月結)結帳資料查詢"
echo "• ./Linux_運費未請款明細.sh - 運費未請款明細下載"
echo "• ./Linux_配置驗證.sh - 配置檔案驗證工具"

# Ubuntu 環境額外的測試工具
if [ "$IS_UBUNTU" = true ]; then
    echo ""
    echo "🧪 Ubuntu 環境測試工具："
    echo "• ./scripts/test_ubuntu_env.sh - Ubuntu 環境驗證"
    echo "• python3 scripts/test_browser.py - 瀏覽器功能測試"
fi

echo ""
read -p "按 Enter 鍵繼續..."
