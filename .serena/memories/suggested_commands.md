# SeleniumPelican 建議命令清單

## 環境設定
```bash
# 安裝 uv (如果尚未安裝)
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 建立並啟動虛擬環境及安裝依賴
uv sync

# 手動建立環境並安裝依賴
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
uv sync
```

## 自動更新
```bash
# Linux/macOS
./update.sh

# Windows (自動啟動 PowerShell 7)
update.cmd

# 或直接使用 PowerShell 7
update.ps1
```

## 執行工具

### 設定環境變數 (Windows 必須)
```bash
# Windows 命令提示字元
set PYTHONUNBUFFERED=1

# Windows PowerShell
$env:PYTHONUNBUFFERED='1'

# Linux/macOS
export PYTHONUNBUFFERED=1
```

### 代收貨款查詢
```bash
# Windows (推薦)
run_payment.cmd
run_payment.ps1

# Linux/macOS
./run_payment.sh

# 使用日期參數
run_payment.cmd --start-date 20241201 --end-date 20241208

# 無頭模式
run_payment.cmd --headless
```

### 運費查詢
```bash
# Windows
run_freight.cmd
run_freight.ps1

# Linux/macOS
./run_freight.sh

# 使用月份參數
run_freight.cmd --start-month 202411 --end-month 202412
```

### 運費未請款明細下載
```bash
# Windows
run_unpaid.cmd
run_unpaid.ps1

# Linux/macOS
./run_unpaid.sh
```

## 手動執行 (需要先設定環境變數)
```bash
# 代收貨款查詢
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/payment_scraper.py

# 運費查詢
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/freight_scraper.py

# 運費未請款明細
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/unpaid_scraper.py

# Windows 版本
# set PYTHONPATH=%cd%
# uv run python -u src\scrapers\payment_scraper.py
```

## 開發和偵錯
```bash
# 檢查專案狀態
git status
git branch

# 檢查 Python 環境
python --version
uv --version

# 檢查依賴
uv tree

# 清理快取
uv cache clean
```

## 設定檔案管理
```bash
# 建立帳號設定檔 (從範例複製)
cp accounts.json.example accounts.json

# 建立環境設定檔
cp .env.example .env

# 編輯設定檔
nano accounts.json  # Linux/macOS
notepad accounts.json  # Windows
```

## 系統工具 (Darwin/macOS 特定)
```bash
# 檔案搜尋
find . -name "*.py" -type f

# 內容搜尋
grep -r "pattern" src/

# 目錄列表
ls -la

# 檔案權限 (如果需要)
chmod +x run_*.sh update.sh

# 系統資訊
uname -a
sw_vers  # macOS 版本
```

## 故障排除
```bash
# 清除 WebDriver 快取 (如果瀏覽器問題)
rm -rf ~/.wdm  # Linux/macOS
# rmdir /s "%USERPROFILE%\.wdm"  # Windows

# 檢查 Chrome 版本
google-chrome --version  # Linux
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --version  # macOS

# 檢查 ChromeDriver
chromedriver --version
```
