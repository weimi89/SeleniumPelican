@echo off
chcp 65001 > nul
echo 🔧 安裝 WEDI 宅配通自動下載工具 - Windows 版本
echo ================================================

echo 📦 步驟 1: 安裝 uv...
pip install uv

echo 🔧 步驟 2: 建立虛擬環境...
uv venv

echo 📦 步驟 3: 安裝依賴套件...
uv sync

echo 🌐 步驟 4: 設定 Chrome 路徑...
if not exist ".env" (
    echo CHROME_BINARY_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe" > .env
    echo ✅ Chrome 路徑已設定為預設 Windows 位置
    echo 💡 如果您的 Chrome 安裝在其他位置，請編輯 .env 檔案
)

echo 👤 步驟 5: 建立帳號設定範例...
if not exist "accounts.json" (
    copy accounts.json.example accounts.json 2>nul
    echo ✅ 請編輯 accounts.json 檔案以新增您的登入憑證
)

echo 🎉 安裝完成！
echo.
echo 📋 後續步驟：
echo 1. 編輯 accounts.json 檔案，新增您的 WEDI 登入憑證
echo 2. 執行程式：run.cmd
echo.
echo 💡 如果遇到任何問題，請查看 README.md
pause