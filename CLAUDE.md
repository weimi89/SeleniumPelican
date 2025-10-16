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

WEDI (宅配通) 自動化工具套件，使用 Selenium 自動下載代收貨款匯款明細、運費(月結)結帳資料、運費未請款明細。採用模組化架構，使用抽象基礎類別設計，易於擴展。

## 專案結構

```
SeleniumPelican/
├── src/                    # Python 原始碼
│   ├── core/               # 核心模組：base_scraper, multi_account_manager, browser_utils, config_validator 等
│   ├── scrapers/           # 爬蟲實作：payment_scraper, freight_scraper, unpaid_scraper
│   └── utils/              # 工具：windows_encoding_utils
├── tests/                  # 測試框架：unit/, integration/, performance/
├── scripts/                # 執行腳本：run_*.ps1/.sh, install, update
├── openspec/               # OpenSpec 變更管理系統
├── logs/, downloads/, reports/, temp/  # 工作目錄
├── Windows_*.cmd / Linux_*.sh  # 標準化執行腳本
├── accounts.json           # 帳號設定檔（不會被 Git 追蹤）
├── .env                    # Chrome 路徑設定
└── pyproject.toml          # Python 專案設定
```

## 核心架構

### 核心模組 (src/core/)
- **BaseScraper**: Chrome WebDriver 初始化、登入流程（自動驗證碼偵測）、iframe 導航
- **ImprovedBaseScraper**: 優化錯誤處理、重試機制、日誌記錄、效能監控
- **MultiAccountManager**: 讀取 accounts.json、多帳號批次處理、整合報告
- **browser_utils.py**: 跨平台 Chrome WebDriver 設定
- **config_validator.py**: JSON Schema 驗證、業務邏輯驗證、自動修復
- **smart_wait.py**: 適應性等待策略、動態超時調整
- **logging_config.py, log_analyzer.py**: 結構化日誌系統、日誌分析
- **diagnostic_manager.py, monitoring_service.py**: 診斷管理、效能監控

### 爬蟲實作 (src/scrapers/)
1. **PaymentScraper**: 代收貨款查詢，YYYYMMDD 日期範圍，預設往前7天，過濾「代收貨款匯款明細」
2. **FreightScraper**: 運費(月結)結帳資料，YYYYMM 月份範圍，預設上個月
3. **UnpaidScraper**: 運費未請款明細，預設當日，直接解析 HTML 表格（BeautifulSoup）

### 測試架構 (tests/)
- **unit/**: 單元測試（base_scraper, payment_scraper）
- **integration/**: 整合測試（full_workflow）
- **performance/**: 效能測試（performance_base, scraper_performance）

### 關鍵技術細節

- **iframe 導航**: 所有操作在 `datamain` iframe 內維持上下文
- **驗證碼**: 自動偵測（5種方法）+ 手動輸入（20秒等待）
- **過濾邏輯**: 精準過濾「代收貨款匯款明細」，排除「已收未結帳」
- **跨平台支援**: `.env` 設定 Chrome 路徑
- **依賴管理**: `uv` + `pyproject.toml` + `uv.lock`
- **Windows 相容**: `safe_print()` 處理 Unicode 顯示

## 開發指令

### 快速開始

**首次安裝**：`Windows_安裝.cmd` (Windows) 或 `./Linux_安裝.sh` (Linux/macOS)

**執行工具**：
- 代收貨款查詢：`Windows_代收貨款查詢.cmd` / `./Linux_代收貨款查詢.sh`
- 運費查詢：`Windows_運費查詢.cmd` / `./Linux_運費查詢.sh`
- 運費未請款明細：`Windows_運費未請款明細.cmd` / `./Linux_運費未請款明細.sh`
- 配置驗證：`Windows_配置驗證.cmd` / `./Linux_配置驗證.sh`

**定期更新**：`Windows_更新.cmd` / `./Linux_更新.sh`

### 安裝腳本功能
- ✅ Python 3.8+、Git、Chrome 環境檢查
- ✅ UV 包管理器自動安裝 + `uv sync` 建立環境
- ✅ 配置檔案自動設定（.env, accounts.json）
- ✅ 目錄結構建立 + 權限設定
- ✅ 配置驗證 + Chrome WebDriver 測試

### 更新腳本功能
- 🔍 Git 儲存庫狀態偵測 + 本地變更保護
- ⬇️ Git pull 更新 + 變更還原
- 📦 智慧依賴更新（根據 pyproject.toml 變更）
- 🛡️ 錯誤處理 + 自動恢復

### 手動安裝方式

```bash
# 安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
# powershell -c "irm https://astral.sh/uv/install.ps1 | iex"  # Windows

# 建立環境並安裝依賴
uv sync
```

### 執行工具

**Windows 使用者**：執行 `run_payment.cmd` / `run_freight.cmd` / `run_unpaid.cmd`
**Linux/macOS 使用者**：執行 `./run_payment.sh` / `./run_freight.sh` / `./run_unpaid.sh`

**參數範例**：
- 日期參數：`--start-date 20241201 --end-date 20241208`
- 月份參數：`--start-month 202411 --end-month 202412`
- 無頭模式：`--headless`（注意：無法手動輸入驗證碼）

**手動執行**（需先設定環境變數 `PYTHONUNBUFFERED=1` 和 `PYTHONPATH`）：
```bash
uv run python -u src/scrapers/payment_scraper.py
uv run python -u src/scrapers/freight_scraper.py
uv run python -u src/scrapers/unpaid_scraper.py
```

### 設定檔案

- **accounts.json**: 帳號憑證（⚠️ 不會被 Git 追蹤），`enabled: true/false` 控制處理帳號，參考 `accounts.json.example`
- **.env**: Chrome 路徑設定，範例：`CHROME_BINARY_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"`
- **安全提醒**: 切勿提交真實密碼到 Git，定期更改密碼

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
- 自動偵測：5種方法偵測4位英數字驗證碼
- 手動輸入：無法偵測時等待20秒
- 重試機制：登入失敗自動重試最多3次
- **注意**：背景模式（--headless）無法手動輸入驗證碼

### iframe 管理
所有操作在 `datamain` iframe 內維持上下文：`navigate_to_query()` → `set_date_range()` → `get_payment_records()` → `download_excel_for_record()`

### 錯誤處理
個別失敗不停止整個流程：日期設定失敗記錄但不中斷，個別帳號失敗不影響其他帳號

### 多帳號處理
`MultiAccountManager` 依序處理帳號，產生單一整合報告

## 程式碼品質與型別檢查

本專案使用 **Python 型別註解** + **mypy 靜態型別檢查**，確保型別安全性、可維護性和可讀性。

### 關鍵指令

```bash
# 型別檢查
./scripts/type_check.sh

# 生成覆蓋率報告
./scripts/type_check.sh --report

# 檢查特定檔案/目錄
uv run mypy src/core/base_scraper.py --config-file pyproject.toml
```

### 工作流程

1. **修改前**：閱讀 `docs/type-annotation-guide.md`，參考 `src/core/type_aliases.py`
2. **修改時**：
   ```python
   # ✅ 明確型別註解
   def process_account(username: str, config: AccountConfig) -> bool:
       return True
   
   # ❌ 避免缺少註解
   def process_data(data):
       return data
   ```
3. **修改後**：執行 `uv run mypy <檔案> --config-file pyproject.toml` 確認無錯誤

### 持續整合

- **Pre-commit Hook**: 自動執行型別檢查（`pre-commit install`）
- **CI/CD**: GitHub Actions 自動驗證

### 覆蓋率狀態

- **整體**: 81.9% (目標: 90%)
- **核心模組**: 100%（0 errors）
- 完整報告：`./scripts/type_check.sh --report`
