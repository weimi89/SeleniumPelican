<!-- OPENSPEC:START -->
# OpenSpec 指令

這些指令是為在此專案中工作的 AI 助理所設計。

當請求有以下情況時，請務必開啟 `@/openspec/AGENTS.md`：
- 提及規劃或提案（如 proposal、spec、change、plan 等詞彙）
- 引入新功能、重大變更、架構調整，或重要的效能/安全性工作
- 聽起來模糊不清，需要權威規格才能開始編碼

使用 `@/openspec/AGENTS.md` 來學習：
- 如何建立和應用變更提案
- 規格格式和慣例
- 專案結構和指導原則

請保留此管理區塊，以便 'openspec update' 可以更新指令。

<!-- OPENSPEC:END -->

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
│   │   ├── improved_base_scraper.py  # 改進版基礎爬蟲類別
│   │   ├── multi_account_manager.py  # 多帳號管理器
│   │   ├── browser_utils.py      # 瀏覽器初始化工具
│   │   ├── config_validator.py   # 配置檔案驗證系統
│   │   ├── constants.py          # 常數定義
│   │   ├── exceptions.py         # 自訂例外類別
│   │   ├── smart_wait.py         # 智能等待機制
│   │   ├── logging_config.py     # 結構化日誌配置
│   │   ├── log_analyzer.py       # 日誌分析工具
│   │   ├── diagnostic_manager.py # 診斷管理器
│   │   └── monitoring_service.py # 監控服務
│   ├── scrapers/                 # 具體實作的爬蟲
│   │   ├── payment_scraper.py    # 代收貨款查詢工具
│   │   ├── freight_scraper.py    # 運費查詢工具
│   │   └── unpaid_scraper.py     # 運費未請款明細工具
│   └── utils/                    # 工具模組
│       └── windows_encoding_utils.py  # Windows 相容性工具
├── tests/                        # 測試框架 (pytest)
│   ├── conftest.py               # pytest 配置和夾具
│   ├── test_diagnostic_manager.py  # 診斷管理器測試
│   ├── test_improvements_validation.py  # 改進驗證測試
│   ├── unit/                     # 單元測試
│   │   ├── test_base_scraper.py  # 基礎爬蟲測試
│   │   └── test_payment_scraper.py  # 代收貨款爬蟲測試
│   ├── integration/              # 整合測試
│   │   └── test_full_workflow.py # 完整工作流程測試
│   └── performance/              # 效能測試
│       ├── __init__.py
│       ├── test_performance_base.py  # 基礎效能測試
│       └── test_scraper_performance.py  # 爬蟲效能測試
├── scripts/                      # 執行腳本和工具
│   ├── common_checks.ps1/.sh/.cmd  # 共用檢查函數
│   ├── run_*.ps1                 # PowerShell 執行腳本
│   ├── install.ps1/.sh           # 安裝腳本
│   ├── update.ps1/.sh            # 更新腳本
│   ├── convert_print_to_logger.py  # 日誌轉換工具
│   ├── log_monitor.py            # 日誌監控工具
│   └── run_performance_tests.py  # 效能測試執行器
├── openspec/                     # OpenSpec 變更管理系統
│   ├── AGENTS.md                 # AI 助理指南
│   ├── project.md                # 專案規格
│   ├── specs/                    # 規格文檔
│   └── changes/                  # 變更提案和實作記錄
├── logs/                         # 執行日誌和診斷資料
│   └── diagnostics/              # 診斷數據目錄
├── downloads/                    # 下載的檔案目錄
├── reports/                      # 執行報告目錄
├── temp/                         # 暫存檔案目錄
├── Windows_代收貨款匯款明細.cmd   # 標準化執行腳本 (Windows)
├── Linux_代收貨款匯款明細.sh     # 標準化執行腳本 (Linux/macOS)
├── Windows_運費發票明細.cmd      # 運費發票明細 (Windows)
├── Linux_運費發票明細.sh         # 運費發票明細 (Linux/macOS)
├── Windows_運費未請款明細.cmd     # 運費未請款明細 (Windows)
├── Linux_運費未請款明細.sh       # 運費未請款明細 (Linux/macOS)
├── Windows_配置驗證.cmd          # 配置驗證 (Windows)
├── Linux_配置驗證.sh             # 配置驗證 (Linux/macOS)
├── Windows_安裝.cmd              # 系統安裝 (Windows)
├── Linux_安裝.sh                 # 系統安裝 (Linux/macOS)
├── Windows_更新.cmd              # 系統更新 (Windows)
├── Linux_更新.sh                 # 系統更新 (Linux/macOS)
├── accounts.json                 # 帳號設定檔
├── accounts.json.example         # 帳號設定範例
├── .env                          # 環境變數設定
├── .env.example                  # 環境變數設定範例
├── pyproject.toml               # Python 專案設定
├── pytest.ini                   # pytest 測試設定
├── pytest-performance.ini       # 效能測試設定
├── .pre-commit-config.yaml      # Git pre-commit 鉤子設定
├── uv.lock                      # 鎖定依賴版本
├── CLAUDE.md                    # Claude Code 工作指南
├── README.md                    # 專案說明文檔
├── AGENTS.md                    # AI 助理說明
└── IMPROVEMENT_SUMMARY.md       # 改進摘要文檔
```

## 核心架構

### 基礎模組 (src/core/)

1. **BaseScraper** (`src/core/base_scraper.py`): 核心基礎類別
   - 處理 Chrome WebDriver 瀏覽器初始化和管理
   - 管理登入流程，包含自動驗證碼偵測
   - 實作基本的導航流程（查詢作業 → 查件頁面 → iframe 切換）
   - 提供共用的瀏覽器管理和連接管理功能

2. **ImprovedBaseScraper** (`src/core/improved_base_scraper.py`): 改進版基礎爬蟲類別
   - 優化的錯誤處理和重試機制
   - 增強的日誌記錄和診斷功能
   - 改進的效能監控和資源管理
   - 更強健的異常恢復能力

3. **MultiAccountManager** (`src/core/multi_account_manager.py`): 多帳號管理器
   - 讀取和解析 `accounts.json` 設定檔
   - 支援多帳號批次處理
   - 產生整合的總結報告
   - 提供依賴注入模式支援不同的抓取器類別

4. **browser_utils.py** (`src/core/browser_utils.py`): Chrome 瀏覽器初始化工具
   - 跨平台 Chrome WebDriver 設定和啟動
   - 支援無頭模式和視窗模式
   - 自動處理 ChromeDriver 版本和路徑問題

5. **config_validator.py** (`src/core/config_validator.py`): 配置檔案驗證系統
   - JSON Schema 驗證 accounts.json 結構完整性
   - 業務邏輯驗證（重複帳號、弱密碼、範例密碼檢查）
   - .env 檔案格式和路徑存在性驗證
   - 自動建立缺失配置檔案功能
   - 詳細驗證報告和錯誤診斷

6. **constants.py** (`src/core/constants.py`): 常數定義
   - 全域常數和配置參數
   - 系統設定和預設值
   - 路徑和URL配置

7. **exceptions.py** (`src/core/exceptions.py`): 自訂例外類別
   - 專案特定的例外類別定義
   - 結構化錯誤處理機制
   - 錯誤分類和錯誤碼管理

8. **smart_wait.py** (`src/core/smart_wait.py`): 智能等待機制
   - 適應性等待策略
   - 動態超時調整
   - 網頁元素智能偵測

9. **logging_config.py** (`src/core/logging_config.py`): 結構化日誌配置
   - 多層級日誌系統設定
   - 格式化和輸出配置
   - 日誌輪轉和存檔管理

10. **log_analyzer.py** (`src/core/log_analyzer.py`): 日誌分析工具
    - 日誌解析和分析功能
    - 錯誤模式識別
    - 效能指標提取

11. **diagnostic_manager.py** (`src/core/diagnostic_manager.py`): 診斷管理器
    - 系統診斷和健康檢查
    - 問題檢測和報告
    - 診斷資料收集

12. **monitoring_service.py** (`src/core/monitoring_service.py`): 監控服務
    - 即時系統監控
    - 效能指標追蹤
    - 警報和通知機制

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

### 測試架構 (tests/)

本專案採用分層測試策略，確保程式碼品質和系統穩定性：

1. **單元測試** (`tests/unit/`): 針對個別模組和函數的測試
   - `test_base_scraper.py`: 基礎爬蟲功能測試
   - `test_payment_scraper.py`: 代收貨款爬蟲邏輯測試

2. **整合測試** (`tests/integration/`): 跨模組協作測試
   - `test_full_workflow.py`: 完整工作流程端到端測試

3. **效能測試** (`tests/performance/`): 系統效能評估
   - `test_performance_base.py`: 基礎效能測試框架
   - `test_scraper_performance.py`: 爬蟲效能基準測試

4. **專項測試**: 
   - `test_diagnostic_manager.py`: 診斷管理器功能測試
   - `test_improvements_validation.py`: 系統改進驗證測試
   - `conftest.py`: pytest 配置和共享夾具

### 工具腳本 (scripts/)

增強的腳本工具集合，提供開發和維護支援：

1. **執行腳本**: 
   - `run_*.ps1`: PowerShell 執行腳本，自動環境設定
   - `common_checks.*`: 跨平台檢查函數庫

2. **系統管理**:
   - `install.ps1/.sh`: 智能安裝腳本，環境檢測和依賴安裝
   - `update.ps1/.sh`: 安全更新腳本，版本控制和依賴同步

3. **開發工具**:
   - `convert_print_to_logger.py`: 自動將 print 語句轉換為結構化日誌
   - `log_monitor.py`: 即時日誌監控和分析工具
   - `run_performance_tests.py`: 效能測試執行器和報告生成

### OpenSpec 變更管理系統 (openspec/)

專業的變更提案和規格管理系統：

1. **核心文檔**:
   - `AGENTS.md`: AI 助理工作指南和最佳實踐
   - `project.md`: 專案總體規格和架構文檔

2. **變更管理**:
   - `changes/`: 變更提案目錄，包含提案、設計、實作和歸檔
   - `specs/`: 詳細技術規格文檔

3. **品質保證**: 系統性的變更追蹤、審查和實作驗證流程

### 關鍵技術細節

- **iframe 導航**: 工具在 WEDI 系統的巢狀 iframe 中導航。所有操作都在 `datamain` iframe 內維持上下文，避免切換衝突。
- **過濾邏輯**: 只下載同時包含「代收貨款」和「匯款明細」關鍵字的項目，排除如「代收款已收未結帳明細」等項目。
- **HTML表格解析**: 運費未請款明細工具使用 BeautifulSoup 直接解析網頁表格，無需下載檔案再處理。
- **跨平台 Chrome 支援**: 使用 `.env` 檔案設定 Chrome 在 macOS、Windows 和 Linux 系統的執行檔路徑。
- **日期範圍彈性**: 支援命令列日期參數（`--start-date`、`--end-date`），預設為當日。
- **現代 Python 管理**: 使用 uv 進行快速依賴管理和虛擬環境處理。
- **結構化日誌**: 實作多層級日誌系統，支援診斷和效能監控。
- **智能等待機制**: 適應性等待策略，提升操作穩定性和效率。
- **品質保證**: 全面的測試覆蓋，包含單元、整合和效能測試。

## 開發指令

### 快速開始

**首次安裝：**
```bash
# Windows
Windows_安裝.cmd

# Linux/macOS
./Linux_安裝.sh
```

**開始使用：**
```bash
# 代收貨款查詢
Windows_代收貨款查詢.cmd    # Windows
./Linux_代收貨款查詢.sh      # Linux/macOS

# 運費查詢
Windows_運費查詢.cmd        # Windows
./Linux_運費查詢.sh          # Linux/macOS

# 運費未請款明細
Windows_運費未請款明細.cmd   # Windows
./Linux_運費未請款明細.sh     # Linux/macOS

# 配置驗證
Windows_配置驗證.cmd        # Windows
./Linux_配置驗證.sh          # Linux/macOS
```

**定期更新：**
```bash
# Windows
Windows_更新.cmd

# Linux/macOS
./Linux_更新.sh
```

### 完整功能說明

#### 安裝腳本功能
- ✅ **系統環境檢查**: Python 3.8+、Git、Google Chrome
- ✅ **UV 包管理器自動安裝**: 最新版本自動下載安裝
- ✅ **虛擬環境建立**: `uv sync` 隔離依賴環境
- ✅ **配置檔案設定**: 自動複製 `.env.example` 和 `accounts.json.example`
- ✅ **目錄結構建立**: 建立必要的工作目錄
- ✅ **權限設定**: Linux/macOS 腳本執行權限
- ✅ **配置驗證**: 整合配置驗證系統檢查
- ✅ **基本測試**: Chrome WebDriver 功能驗證

#### 更新腳本功能
- 🔍 **智慧更新檢查**: Git 儲存庫狀態自動偵測
- 💾 **本地變更保護**: 自動暫存未提交的變更
- ⬇️ **安全更新流程**: Git pull 程式碼更新
- 🔄 **變更還原**: 自動還原暫存的本地變更
- 📦 **智慧依賴更新**: 根據 `pyproject.toml` 變更決定更新
- 🛡️ **錯誤處理**: 更新失敗時自動恢復機制

#### 配置驗證系統
- 📋 **JSON Schema 驗證**: accounts.json 結構完整性檢查
- 🔍 **業務邏輯驗證**: 重複帳號、弱密碼、範例密碼檢查
- 🔧 **.env 檔案驗證**: 格式正確性和路徑存在性檢查
- 🔄 **自動修復**: 缺失配置檔案自動建立
- 📊 **詳細報告**: 完整的驗證結果和修復建議

### 傳統安裝方式

#### 設定和安裝
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