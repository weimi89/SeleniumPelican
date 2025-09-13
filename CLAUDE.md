# CLAUDE.md

這個檔案為 Claude Code (claude.ai/code) 在此儲存庫工作時提供指導。

## 專案概述

這是一個 WEDI (宅配通) 自動化工具，使用 Selenium 自動從 WEDI 網頁系統下載代收貨款匯款明細。該工具支援多帳號處理，並可處理多種日期範圍的資料擷取。

## 核心架構

### 主要元件

1. **WEDISeleniumScraper** (`wedi_selenium_scraper.py`): 核心自動化類別
   - 處理 Chrome WebDriver 瀏覽器初始化
   - 管理登入流程，包含自動驗證碼偵測
   - 在 iframe 內導航到代收貨款查詢頁面
   - 下載 Excel 檔案（支援 .xls 和 .xlsx 格式）
   - 實作簡化的導航流程，保持在 iframe 內操作

2. **MultiAccountManager** (`wedi_selenium_scraper.py`): 批次處理管理器
   - 處理 `accounts.json` 中的多個帳號
   - 產生整合的總結報告
   - 管理平行執行和錯誤處理

### 關鍵技術細節

- **iframe 導航**: 工具在 WEDI 系統的巢狀 iframe 中導航。所有操作都在 `datamain` iframe 內維持上下文，避免切換衝突。
- **過濾邏輯**: 只下載同時包含「代收貨款」和「匯款明細」關鍵字的項目，排除如「代收款已收未結帳明細」等項目。
- **跨平台 Chrome 支援**: 使用 `.env` 檔案設定 Chrome 在 macOS、Windows 和 Linux 系統的執行檔路徑。
- **日期範圍彈性**: 支援命令列日期參數（`--start-date`、`--end-date`），預設為當日。
- **現代 Python 管理**: 使用 uv 進行快速依賴管理和虛擬環境處理。

## 開發指令

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

**執行命令：**

**Windows 使用者（推薦）：**
```cmd
# 使用 Windows 批次檔（推薦，已自動設定環境變數）
run.cmd

# 無頭模式
run.cmd --headless
```

**Linux/macOS 使用者：**
```bash
# 使用 shell 腳本執行（推薦，已自動設定環境變數）
./run.sh

# 無頭模式
./run.sh --headless
```

**手動執行（需要先設定環境變數）：**
```bash
# 直接使用 uv 執行 Python
uv run python -u wedi_selenium_scraper.py

# 傳統 Python 執行
python -u wedi_selenium_scraper.py
```

### 設定檔案

- **pyproject.toml**: 現代 Python 專案設定，包含依賴和 uv 設定
- **accounts.json**: 包含帳號憑證和設定
  - `enabled: true/false` 控制要處理哪些帳號
  - `settings.headless` 和 `settings.download_base_dir` 為全域設定

- **.env**: Chrome 執行檔路徑設定（從 `.env.example` 建立）
  ```
  CHROME_BINARY_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
  ```

## 輸出結構

- **downloads/**: 按帳號下載的 Excel 檔案（格式：`{username}_{payment_no}.xlsx`）
- **reports/**: 個別帳號執行報告（目前版本已停用）
- **logs/**: 執行日誌和除錯資訊
- **temp/**: 暫存處理檔案

## 重要實作說明

### iframe 管理
工具在整個過程中維持 iframe 上下文以避免 Chrome 崩潰：
- `navigate_to_payment_query()`: 進入 iframe 並保持
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

### 現代依賴管理
- 已移除舊的 `requirements.txt`，統一使用 `pyproject.toml` + `uv.lock` 管理依賴
- 避免版本衝突和重複安裝問題
- 使用 `uv sync` 確保依賴版本一致性