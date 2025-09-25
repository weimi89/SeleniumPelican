# 開發環境設定指南

## 快速開始

SeleniumPelican 使用現代化的 Python 工具鏈，支援 Windows、macOS、Linux 三大平台。

### 🔧 系統需求

#### 必要軟體
- **Python 3.8+** (建議 3.11+)
- **Google Chrome** 瀏覽器
- **Git** 版本控制
- **uv** 包管理工具

#### 支援平台
- ✅ **Windows 10/11** (命令提示字元、PowerShell)
- ✅ **macOS 12+** (Terminal、iTerm2)
- ✅ **Linux** (Ubuntu 20.04+、CentOS 8+)

---

## 🚀 環境建置步驟

### 步驟 1: 安裝 UV 包管理器

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows PowerShell:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**驗證安裝:**
```bash
uv --version
# 應該顯示: uv 0.4.x 或更高版本
```

### 步驟 2: 克隆專案

```bash
git clone <repository-url>
cd SeleniumPelican
```

### 步驟 3: 建立虛擬環境和安裝依賴

```bash
# 一鍵建立環境並安裝所有依賴
uv sync

# 或者分步驟操作
uv venv                    # 建立虛擬環境
source .venv/bin/activate  # 啟動環境 (macOS/Linux)
# .venv\Scripts\activate   # 啟動環境 (Windows)
uv sync                    # 安裝依賴
```

### 步驟 4: 配置 Chrome 路徑

複製環境設定範例檔案：
```bash
cp .env.example .env
```

編輯 `.env` 檔案，設定 Chrome 路徑：
```bash
# macOS
CHROME_BINARY_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Windows
CHROME_BINARY_PATH="C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# Linux
CHROME_BINARY_PATH="/usr/bin/google-chrome"
```

### 步驟 5: 配置帳號資訊

```bash
cp accounts.json.example accounts.json
```

編輯 `accounts.json`，填入實際的帳號資訊：
```json
{
  "accounts": [
    {
      "username": "your_username",
      "password": "your_password",
      "enabled": true
    }
  ],
  "settings": {
    "headless": false,
    "download_base_dir": "./downloads"
  }
}
```

**⚠️ 安全提醒**: `accounts.json` 已被加入 `.gitignore`，不會被 Git 追蹤

---

## 🔨 開發工具設定

### VS Code 設定 (推薦)

安裝推薦的擴展：
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.flake8",
    "ms-python.black-formatter",
    "ms-vscode.vscode-json"
  ]
}
```

Python 解譯器設定：
```json
{
  "python.defaultInterpreterPath": "./.venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "python.formatting.provider": "black",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true
}
```

### PyCharm 設定

1. 開啟專案：`File` → `Open` → 選擇專案目錄
2. 設定解譯器：`File` → `Settings` → `Python Interpreter`
3. 選擇：`Existing environment` → `.venv/bin/python`
4. 啟用程式碼格式化：`Tools` → `External Tools` → 新增 Black

---

## 📋 驗證安裝

### 基本驗證

```bash
# 檢查 Python 環境
python --version
# Python 3.11.x

# 檢查已安裝的包
uv pip list
# 應該看到 selenium, beautifulsoup4, openpyxl 等

# 檢查專案結構
ls -la src/
# 應該看到 core/, scrapers/, utils/ 目錄
```

### 功能測試

```bash
# 測試瀏覽器啟動 (無頭模式)
PYTHONPATH="$(pwd)" uv run python -c "
from src.core.browser_utils import setup_chrome_driver
driver = setup_chrome_driver(headless=True)
print('✅ Chrome WebDriver 啟動成功')
driver.quit()
"
```

### 執行腳本測試

**Linux/macOS:**
```bash
./run_payment.sh --help
# 應該顯示幫助資訊
```

**Windows:**
```cmd
run_payment.cmd --help
```

---

## 🐛 常見問題排解

### 問題 1: uv 命令找不到

**症狀**: `command not found: uv`

**解決方案**:
```bash
# 重新載入 shell 設定
source ~/.bashrc  # 或 ~/.zshrc

# 手動設定 PATH (暫時)
export PATH="$HOME/.cargo/bin:$PATH"

# 永久設定 (加入 shell 設定檔)
echo 'export PATH="$HOME/.cargo/bin:$PATH"' >> ~/.bashrc
```

### 問題 2: Chrome 找不到

**症狀**: `Message: 'chromedriver' executable needs to be in PATH`

**解決方案**:
1. 確認 Chrome 已安裝
2. 檢查 `.env` 檔案中的路徑設定
3. 手動指定 ChromeDriver 路徑

```bash
# macOS 查找 Chrome 路徑
ls -la /Applications/Google\ Chrome.app/Contents/MacOS/

# Windows 查找 Chrome 路徑
dir "C:\Program Files\Google\Chrome\Application\"

# Linux 查找 Chrome 路徑
which google-chrome
```

### 問題 3: 編碼問題 (Windows)

**症狀**: 控制台顯示亂碼或特殊字符

**解決方案**:
```cmd
# 設定環境變數
set PYTHONUNBUFFERED=1

# 或使用 PowerShell
$env:PYTHONUNBUFFERED = '1'

# 永久設定 (系統環境變數)
# 控制台 → 系統 → 進階系統設定 → 環境變數
```

### 問題 4: 依賴版本衝突

**症狀**: `pip` 依賴解析錯誤

**解決方案**:
```bash
# 清理並重建環境
rm -rf .venv/
uv venv
uv sync

# 檢查版本鎖定
cat uv.lock | grep selenium
```

### 問題 5: 權限問題

**症狀**: 執行腳本時權限不足

**解決方案**:
```bash
# macOS/Linux 設定執行權限
chmod +x run_payment.sh
chmod +x run_freight.sh
chmod +x run_unpaid.sh

# Windows 執行策略 (PowerShell)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## 🔄 自動更新機制

### 使用自動更新腳本

**Linux/macOS:**
```bash
./update.sh
```

**Windows:**
```cmd
update.cmd
```

### 自動更新流程

1. 🔍 檢查遠端更新
2. 💾 暫存未提交的變更
3. ⬇️ 執行 `git pull`
4. 📦 更新依賴 (如果 `pyproject.toml` 有變更)
5. 🔄 還原暫存的變更

### 手動更新

```bash
# 更新程式碼
git pull origin main

# 更新依賴
uv sync

# 檢查是否需要重新配置
diff .env.example .env
diff accounts.json.example accounts.json
```

---

## 📚 開發環境最佳實踐

### 目錄結構標準

```
SeleniumPelican/
├── .venv/           # 虛擬環境 (不提交)
├── src/             # 原始碼
├── docs/            # 文檔
├── downloads/       # 下載檔案 (不提交)
├── logs/            # 日誌檔案 (不提交)
├── temp/            # 暫存檔案 (不提交)
└── tests/           # 測試程式碼
```

### Git 工作流程

```bash
# 開發新功能
git checkout -b feature/new-scraper
git add .
git commit -m "feat: 新增某某查詢功能"
git push origin feature/new-scraper

# 合併主分支
git checkout main
git pull origin main
git merge feature/new-scraper
```

### 程式碼品質檢查

```bash
# 格式化程式碼
uv run black src/

# 程式碼風格檢查
uv run flake8 src/

# 型別檢查 (如果使用)
uv run mypy src/
```

### 效能監控

```bash
# 記憶體使用監控
python -m memory_profiler src/scrapers/payment_scraper.py

# 執行時間分析
python -m cProfile -o profile.stats src/scrapers/payment_scraper.py
```

---

## 🎯 下一步

環境設定完成後，建議：

1. 📖 閱讀 [程式碼規範](coding_standards.md)
2. 🧪 了解 [測試策略](testing_strategy.md)
3. 🚀 查看 [部署指南](deployment_guide.md)
4. 📚 參考 [API 文檔](../technical/api_reference.md)

需要協助？請查看 [疑難排解](../technical/troubleshooting.md) 或在專案倉庫建立 Issue。