# CLAUDE.md

這個檔案為 Claude Code (claude.ai/code) 在此儲存庫工作時提供指導。

## 專案概述

這是一個 WEDI (宅配通) 自動化工具套件，使用 Selenium 自動從 WEDI 網頁系統下載各種資料。支援代收貨款匯款明細查詢、運費(月結)結帳資料查詢，以及運費未請款明細下載。該工具採用現代化的模組化架構，使用抽象基礎類別設計，易於擴展新功能。

## 專案結構

```
SeleniumPelican/
├── src/                          # 所有 Python 原始碼
│   ├── core/                     # 核心模組
│   │   ├── base_scraper.py       # 基礎爬蟲類別
│   │   ├── multi_account_manager.py  # 多帳號管理器
│   │   └── browser_utils.py      # 瀏覽器初始化工具
│   ├── scrapers/                 # 具體實作的爬蟲
│   │   ├── payment_scraper.py    # 代收貨款查詢工具
│   │   ├── freight_scraper.py    # 運費查詢工具
│   │   └── unpaid_scraper.py     # 運費未請款明細工具
│   └── utils/                    # 工具模組
│       └── windows_encoding_utils.py  # Windows 相容性工具
├── run_payment.sh/.cmd/.ps1      # 代收貨款執行腳本
├── run_freight.sh/.cmd/.ps1      # 運費查詢執行腳本
├── run_unpaid.sh/.cmd/.ps1        # 運費未請款明細執行腳本
├── update.sh/.cmd/.ps1          # 自動更新腳本
├── accounts.json                 # 帳號設定檔
├── pyproject.toml               # Python 專案設定
└── uv.lock                      # 鎖定依賴版本
```

## 核心架構

### 基礎模組 (src/core/)

1. **BaseScraper** (`src/core/base_scraper.py`): 核心基礎類別
   - 處理 Chrome WebDriver 瀏覽器初始化和管理
   - 管理登入流程，包含自動驗證碼偵測
   - 實作基本的導航流程（查詢作業 → 查件頁面 → iframe 切換）
   - 提供共用的瀏覽器管理和連接管理功能

2. **MultiAccountManager** (`src/core/multi_account_manager.py`): 多帳號管理器
   - 讀取和解析 `accounts.json` 設定檔
   - 支援多帳號批次處理
   - 產生整合的總結報告
   - 提供依賴注入模式支援不同的抓取器類別

3. **browser_utils.py** (`src/core/browser_utils.py`): Chrome 瀏覽器初始化工具
   - 跨平台 Chrome WebDriver 設定和啟動
   - 支援無頭模式和視窗模式
   - 自動處理 ChromeDriver 版本和路徑問題

### 工具模組 (src/utils/)

1. **windows_encoding_utils.py**: Windows 編碼相容性處理
   - 提供 `safe_print()` 函數，將 Unicode 字符轉換為純文字
   - 支援跨平台 Unicode 字符顯示
   - 自動檢查和提醒 PYTHONUNBUFFERED 環境變數設定

### 爬蟲實作 (src/scrapers/)

本專案包含三個專門的爬蟲工具，各自針對不同的 WEDI 功能進行優化：

1. **PaymentScraper** (`src/scrapers/payment_scraper.py`): 代收貨款查詢工具
   - **功能**: 下載代收貨款匯款明細
   - **繼承**: BaseScraper 實作代收貨款匯款明細查詢
   - **日期格式**: 支援日期範圍查詢（YYYYMMDD 格式）
   - **預設範圍**: 往前7天
   - **過濾機制**: 精準過濾「代收貨款匯款明細」項目，排除「已收未結帳」類型
   - **檔案命名**: `{帳號}_{payment_no}.xlsx`
   - **下載方式**: 點擊連結下載 Excel 檔案

2. **FreightScraper** (`src/scrapers/freight_scraper.py`): 運費(月結)結帳資料查詢工具
   - **功能**: 下載運費(月結)結帳資料
   - **繼承**: BaseScraper 實作運費(月結)結帳資料查詢
   - **日期格式**: 支援月份範圍查詢（YYYYMM 格式）
   - **預設範圍**: 上個月
   - **搜尋目標**: (2-7) 運費(月結)結帳資料相關項目
   - **檔案命名**: `{帳號}_freight_{record_id}.xlsx`
   - **下載方式**: 使用 data-fileblob 提取數據生成 Excel

3. **UnpaidScraper** (`src/scrapers/unpaid_scraper.py`): 運費未請款明細工具
   - **功能**: 下載運費未請款明細
   - **繼承**: BaseScraper 實作運費未請款明細查詢
   - **日期格式**: 預設結束時間為當日，無需使用者輸入
   - **搜尋目標**: 運費未請款相關頁面
   - **檔案命名**: `{帳號}_FREIGHT_{結束時間}.xlsx`
   - **下載方式**: 直接抓取HTML表格並使用 BeautifulSoup 解析轉換為Excel檔案
   - **特色**: 無需點擊下載連結，直接從網頁表格提取數據

### 關鍵技術細節

- **iframe 導航**: 工具在 WEDI 系統的巢狀 iframe 中導航。所有操作都在 `datamain` iframe 內維持上下文，避免切換衝突。
- **過濾邏輯**: 只下載同時包含「代收貨款」和「匯款明細」關鍵字的項目，排除如「代收款已收未結帳明細」等項目。
- **HTML表格解析**: 運費未請款明細工具使用 BeautifulSoup 直接解析網頁表格，無需下載檔案再處理。
- **跨平台 Chrome 支援**: 使用 `.env` 檔案設定 Chrome 在 macOS、Windows 和 Linux 系統的執行檔路徑。
- **日期範圍彈性**: 支援命令列日期參數（`--start-date`、`--end-date`），預設為當日。
- **現代 Python 管理**: 使用 uv 進行快速依賴管理和虛擬環境處理。

## 開發指令

### 自動更新
```bash
# Linux/macOS
./update.sh

# Windows（自動啟動 PowerShell 7）
update.cmd

# 或直接使用 PowerShell 7 腳本
update.ps1
```

**自動更新功能**：
- 🔍 自動檢查遠端更新
- 💾 自動暫存未提交的變更
- ⬇️ 執行 git pull 更新
- 📦 自動更新依賴套件（如果 pyproject.toml 有變更）
- 🔄 自動還原之前暫存的變更
- 🛡️ 安全機制：遇到衝突會提示手動處理

### 設定和安裝
```bash
# 安裝 uv（如果尚未安裝）
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 建立並啟動虛擬環境及安裝依賴
uv sync

# 或手動建立環境並安裝依賴
uv venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows
uv sync  # 使用 pyproject.toml 管理依賴
```

### 執行工具

**重要：Windows 使用者必須先設定環境變數**
```bash
# Windows 命令提示字元
set PYTHONUNBUFFERED=1

# Windows PowerShell
$env:PYTHONUNBUFFERED='1'

# Linux/macOS
export PYTHONUNBUFFERED=1
```

#### 代收貨款查詢

**Windows 使用者（推薦）：**
```cmd
# 使用 Windows 批次檔（自動啟動 PowerShell 7）
run_payment.cmd

# 或直接使用 PowerShell 7 腳本
run_payment.ps1

# 使用日期參數
run_payment.cmd --start-date 20241201 --end-date 20241208

# 無頭模式（注意：無法手動輸入驗證碼）
run_payment.cmd --headless
```

**Linux/macOS 使用者：**
```bash
# 使用 shell 腳本執行（推薦，已自動設定環境變數）
./run_payment.sh

# 使用日期參數
./run_payment.sh --start-date 20241201 --end-date 20241208

# 無頭模式（注意：無法手動輸入驗證碼）
./run_payment.sh --headless
```

#### 運費查詢

**Windows 使用者：**
```cmd
# 使用 Windows 批次檔（自動啟動 PowerShell 7）
run_freight.cmd

# 或直接使用 PowerShell 7 腳本
run_freight.ps1

# 使用月份參數
run_freight.cmd --start-month 202411 --end-month 202412

# 無頭模式
run_freight.cmd --headless
```

**Linux/macOS 使用者：**
```bash
# 使用 shell 腳本執行
./run_freight.sh

# 使用月份參數
./run_freight.sh --start-month 202411 --end-month 202412

# 無頭模式
./run_freight.sh --headless
```

#### 運費未請款明細下載

**Windows 使用者：**
```cmd
# 使用 Windows 批次檔（自動啟動 PowerShell 7）
run_unpaid.cmd

# 或直接使用 PowerShell 7 腳本
run_unpaid.ps1

# 無頭模式
run_unpaid.cmd --headless
```

**Linux/macOS 使用者：**
```bash
# 使用 shell 腳本執行
./run_unpaid.sh

# 無頭模式
./run_unpaid.sh --headless
```

**手動執行（需要先設定環境變數）：**
```bash
# 代收貨款查詢
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/payment_scraper.py

# 運費查詢
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/freight_scraper.py

# 運費未請款明細下載
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/unpaid_scraper.py

# Windows 使用者設定：
# set PYTHONPATH=%cd%
# uv run python -u src\scrapers\payment_scraper.py
# uv run python -u src\scrapers\freight_scraper.py
# uv run python -u src\scrapers\unpaid_scraper.py
```

### 設定檔案

- **pyproject.toml**: 現代 Python 專案設定，包含依賴和 uv 設定
- **accounts.json**: 包含帳號憑證和設定（⚠️ 不會被 Git 追蹤）
  - `enabled: true/false` 控制要處理哪些帳號
  - `settings.headless` 和 `settings.download_base_dir` 為全域設定
  - **重要**：請參考 `accounts.json.example` 建立此檔案
  - **安全提醒**：切勿將真實密碼提交到 Git

- **.env**: Chrome 執行檔路徑設定（從 `.env.example` 建立）
  ```
  CHROME_BINARY_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  ```

### 安全注意事項

- `accounts.json` 已加入 `.gitignore`，不會被 Git 追蹤
- 請定期更改密碼，確保帳號安全
- 切勿在公開場所或文件中暴露真實密碼
- 建議使用強密碼並啟用雙因素認證（如果支援）

## 輸出結構

- **downloads/**: 按帳號下載的 Excel 檔案
  - 代收貨款：`{username}_{payment_no}.xlsx`
  - 運費資料：`{username}_freight_{record_id}.xlsx`
  - 運費未請款明細：`{username}_FREIGHT_{end_date}.xlsx`
- **reports/**: 個別帳號執行報告（目前版本已停用）
- **logs/**: 執行日誌和除錯資訊
- **temp/**: 暫存處理檔案

## 重要實作說明

### 驗證碼處理

**自動偵測機制**：
- 程式會嘗試5種方法自動偵測登入頁面的4位英數字驗證碼
- 成功偵測到驗證碼會自動填入並登入

**手動輸入模式**：
- 無法自動偵測時，程式會等待20秒讓用戶手動輸入
- **重要**：背景模式（--headless）無法手動輸入，建議使用視窗模式

**重試機制**：
- 登入失敗會自動重試最多3次
- 每次重試會重新載入頁面和重新偵測驗證碼


### iframe 管理
工具在整個過程中維持 iframe 上下文以避免 Chrome 崩潰：
- `navigate_to_query()`: 進入 iframe 並保持
- `set_date_range()`: 在現有 iframe 上下文中工作
- `get_payment_records()`: 在 iframe 內搜尋
- `download_excel_for_record()`: 在 iframe 內下載

### 錯誤處理哲學
工具採用「繼續執行」方式，個別失敗不會停止整個流程：
- 日期設定失敗會記錄但不會中斷執行
- 找不到查詢按鈕時會跳過並顯示警告
- 個別帳號失敗不會影響其他帳號

### 多帳號處理
`MultiAccountManager` 依序處理帳號，並產生單一整合報告而非每個帳號的個別報告，以減少輸出雜亂。

### headless 參數處理
- 已修正 headless 參數處理邏輯，現在會正確讀取 `accounts.json` 中的 `settings.headless` 設定
- 命令列的 `--headless` 參數會覆蓋設定檔案中的設定
- 執行腳本會互動式提示輸入日期，預設查詢過去7天

### 現代化改進

**模組化架構**：
- 採用 `src/` 目錄結構，符合現代 Python 專案標準
- 根目錄不包含 Python 檔案，保持整潔
- 清晰的模組分離：core（核心）、scrapers（實作）、utils（工具）

**依賴管理**：
- 移除舊的 `requirements.txt`，統一使用 `pyproject.toml` + `uv.lock`
- 避免版本衝突和重複安裝問題
- 使用 `uv sync` 確保依賴版本一致性

**Windows 相容性**：
- 實作 `safe_print()` 函數處理 Unicode 字符顯示問題
- 所有 Unicode 字符（如 ✅ ❌ 🎉）自動轉換為純文字標籤
- 確保在 Windows 命令提示字元中正常顯示

**執行腳本優化**：
- 提供跨平台執行腳本（.sh、.cmd、.ps1）
- .cmd 檔案自動啟動 PowerShell 7，享受最佳體驗
- 智慧執行順序：Windows Terminal > PowerShell 7 > 舊版 PowerShell
- 完整 UTF-8 支援和彩色輸出
- 自動設定必要的環境變數（PYTHONUNBUFFERED、PYTHONPATH）
- 簡化使用者執行流程