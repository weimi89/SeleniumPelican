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

## 專案概述

WEDI 宅配通自動化工具：Selenium 自動下載代收貨款匯款明細、運費結帳資料、運費未請款明細。模組化架構，抽象基礎類別設計。

## 專案結構

```
src/
├── core/       # BaseScraper, ImprovedBaseScraper, MultiAccountManager, browser_utils, config_validator, smart_wait, logging_config, diagnostic_manager
├── scrapers/   # PaymentScraper, FreightScraper, UnpaidScraper
└── utils/      # windows_encoding_utils
tests/          # unit/, integration/, performance/
scripts/        # 安裝/更新/執行腳本
```

**關鍵檔案**：
- `accounts.json`：帳號憑證（gitignore），`enabled: true/false` 控制處理
- `.env`：Chrome 路徑，例：`CHROME_BINARY_PATH="/path/to/chrome"`
- `pyproject.toml`：依賴管理（uv）

## 核心架構

### 爬蟲類型
1. **PaymentScraper**：代收貨款（YYYYMMDD 範圍，預設往前7天）
2. **FreightScraper**：運費月結（YYYYMM 範圍，預設上月）
3. **UnpaidScraper**：運費未請款（預設當日，BeautifulSoup 解析）

### 關鍵技術
- **iframe 導航**：所有操作在 `datamain` iframe 維持上下文
- **驗證碼**：自動偵測（5種方法）+ 手動輸入（20秒等待），⚠️ headless 模式無法手動輸入
- **多帳號**：MultiAccountManager 依序處理，個別失敗不中斷流程
- **跨平台**：.env 設定 Chrome 路徑，safe_print() 處理 Windows Unicode

## 快速指令

### 安裝與更新
```bash
# 首次安裝（Windows/Linux）
Windows_安裝.cmd  或  ./Linux_安裝.sh

# 定期更新
Windows_更新.cmd  或  ./Linux_更新.sh

# 手動安裝 uv
curl -LsSf https://astral.sh/uv/install.sh | sh  # macOS/Linux
uv sync
```

### 執行工具
| 功能 | Windows | Linux/macOS |
|------|---------|-------------|
| 代收貨款查詢 | `Windows_代收貨款查詢.cmd` | `./Linux_代收貨款查詢.sh` |
| 運費查詢 | `Windows_運費查詢.cmd` | `./Linux_運費查詢.sh` |
| 運費未請款明細 | `Windows_運費未請款明細.cmd` | `./Linux_運費未請款明細.sh` |
| 配置驗證 | `Windows_配置驗證.cmd` | `./Linux_配置驗證.sh` |

**參數範例**：
- `--start-date 20241201 --end-date 20241208`（日期範圍）
- `--start-month 202411 --end-month 202412`（月份範圍）
- `--headless`（背景執行，⚠️ 無法手動輸入驗證碼）

**手動執行**（需設定 `PYTHONUNBUFFERED=1` 和 `PYTHONPATH`）：
```bash
uv run python -u src/scrapers/payment_scraper.py
uv run python -u src/scrapers/freight_scraper.py
uv run python -u src/scrapers/unpaid_scraper.py
```

## 輸出結構

- `downloads/`：Excel 檔（`{username}_{type}_{id}.xlsx`）
- `logs/`：執行日誌和除錯資訊
- `reports/`：帳號執行報告（已停用）
- `temp/`：暫存檔案

## 型別檢查

使用 Python 型別註解 + mypy 靜態檢查（覆蓋率：81.9%，目標：90%）

```bash
# 型別檢查
./scripts/type_check.sh

# 覆蓋率報告
./scripts/type_check.sh --report

# 檢查特定檔案
uv run mypy src/core/base_scraper.py --config-file pyproject.toml
```

**工作流程**：修改前閱讀 `docs/type-annotation-guide.md`，參考 `src/core/type_aliases.py` → 修改時加型別註解 → 修改後執行 mypy 確認

**持續整合**：pre-commit hook + GitHub Actions 自動驗證

## 安全提醒

⚠️ 切勿提交真實密碼到 Git，定期更改密碼，參考 `accounts.json.example` 設定帳號
