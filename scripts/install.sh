#!/bin/bash
# SeleniumPelican 安裝工具 - Shell 版本

echo ""
echo "📦 SeleniumPelican 安裝工具"
echo "=========================="
echo ""

echo "🔍 檢查系統環境..."

# 檢查 Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python: $PYTHON_VERSION"
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version)
    echo "✅ Python: $PYTHON_VERSION"
else
    echo "❌ Python 未安裝或無法執行"
    echo "請先安裝 Python 3.8+:"
    echo "• Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "• CentOS/RHEL: sudo yum install python3 python3-pip"
    echo "• macOS: brew install python3"
    exit 1
fi

# 檢查 Git
if command -v git &> /dev/null; then
    GIT_VERSION=$(git --version)
    echo "✅ Git: $GIT_VERSION"
else
    echo "⚠️ Git 未安裝，建議安裝以獲得完整功能"
    echo "• Ubuntu/Debian: sudo apt install git"
    echo "• CentOS/RHEL: sudo yum install git"
    echo "• macOS: brew install git"
fi

# 檢查 Chrome 瀏覽器
CHROME_INSTALLED=false
CHROME_PATHS=(
    "/usr/bin/google-chrome"
    "/usr/bin/google-chrome-stable"
    "/usr/bin/chromium"
    "/usr/bin/chromium-browser"
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
    "/opt/google/chrome/chrome"
)

for chrome_path in "${CHROME_PATHS[@]}"; do
    if [ -x "$chrome_path" ]; then
        echo "✅ Chrome: 已安裝 ($chrome_path)"
        CHROME_INSTALLED=true
        break
    fi
done

if [ "$CHROME_INSTALLED" = false ]; then
    echo "❌ Google Chrome 未找到"
    echo "請先安裝 Google Chrome:"
    echo "• Ubuntu/Debian: wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add - && sudo sh -c 'echo \"deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main\" >> /etc/apt/sources.list.d/google-chrome.list' && sudo apt update && sudo apt install google-chrome-stable"
    echo "• CentOS/RHEL: sudo yum install -y google-chrome-stable"
    echo "• macOS: brew install --cask google-chrome"
    exit 1
fi

echo ""
echo "🚀 開始安裝 SeleniumPelican..."
echo ""

# 步驟 1: 檢查並安裝 uv
echo "📋 步驟 1: 安裝 UV 包管理器"
if command -v uv &> /dev/null; then
    UV_VERSION=$(uv --version)
    echo "✅ uv 已安裝: $UV_VERSION"
else
    echo "⬇️ 正在安裝 UV..."
    if curl -LsSf https://astral.sh/uv/install.sh | sh; then
        # 重新載入 shell 設定
        export PATH="$HOME/.cargo/bin:$PATH"
        if command -v uv &> /dev/null; then
            UV_VERSION=$(uv --version)
            echo "✅ UV 安裝成功: $UV_VERSION"
        else
            echo "❌ UV 安裝失敗，請手動安裝: https://docs.astral.sh/uv/"
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
    if [ -f ".env.example" ]; then
        cp ".env.example" ".env"
        echo "✅ 已建立 .env 檔案"
        echo "⚠️ 請編輯 .env 檔案並設定正確的 Chrome 路徑"
    else
        echo "❌ 找不到 .env.example 檔案"
    fi
else
    echo "ℹ️ .env 檔案已存在"
fi

# 建立 accounts.json 檔案
if [ ! -f "accounts.json" ]; then
    if [ -f "accounts.json.example" ]; then
        cp "accounts.json.example" "accounts.json"
        echo "✅ 已建立 accounts.json 檔案"
        echo "⚠️ 請編輯 accounts.json 檔案並填入實際的帳號資訊"
    else
        echo "❌ 找不到 accounts.json.example 檔案"
    fi
else
    echo "ℹ️ accounts.json 檔案已存在"
fi

# 步驟 4: 建立必要目錄
echo ""
echo "📋 步驟 4: 建立必要目錄"

directories=("downloads" "logs" "temp" "reports")
for dir in "${directories[@]}"; do
    if [ ! -d "$dir" ]; then
        mkdir -p "$dir"
        echo "✅ 已建立目錄: $dir"
    else
        echo "ℹ️ 目錄已存在: $dir"
    fi
done

# 步驟 5: 設定執行權限
echo ""
echo "📋 步驟 5: 設定執行權限"
chmod +x Linux_*.sh
chmod +x scripts/*.sh
echo "✅ 已設定執行權限"

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
echo "🎉 SeleniumPelican 安裝完成！"
echo ""
echo "📝 後續步驟："
echo "1. 編輯 .env 檔案，設定正確的 Chrome 路徑"
echo "2. 編輯 accounts.json 檔案，填入實際的帳號資訊"
echo "3. 執行配置驗證：./Linux_配置驗證.sh"
echo "4. 開始使用各項功能"
echo ""
echo "🚀 可用的執行腳本："
echo "• ./Linux_代收貨款查詢.sh - 代收貨款匯款明細查詢"
echo "• ./Linux_運費查詢.sh - 運費(月結)結帳資料查詢"
echo "• ./Linux_運費未請款明細.sh - 運費未請款明細下載"
echo "• ./Linux_配置驗證.sh - 配置檔案驗證工具"

echo ""
read -p "按 Enter 鍵繼續..."