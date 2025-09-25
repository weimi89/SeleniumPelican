# WEDI 宅配通自動下載工具 📦

一個使用 Python + Selenium 建立的現代化自動化工具套件，專門用於自動登入 WEDI（宅配通）系統並下載各種資料。支援代收貨款匯款明細、運費(月結)結帳資料查詢，以及運費未請款明細下載。

## 功能特色

✨ **自動登入**: 自動填入客代和密碼
🤖 **智能驗證碼偵測**: 多層次自動偵測右側4碼英數字驗證碼
💰 **代收貨款查詢**: 下載代收貨款匯款明細 Excel 檔案
🚛 **運費查詢**: 下載運費(月結)結帳資料 Excel 檔案
📊 **運費未請款明細**: 直接抓取表格並轉換為 Excel 檔案
👥 **多帳號支援**: 批次處理多個帳號，自動產生總結報告
📅 **彈性日期**: 支援不同的日期格式（YYYYMMDD 或 YYYYMM）
📝 **智能檔案命名**: 檔案自動命名為 `帳號_編號.xlsx` 格式
🔄 **檔案覆蓋**: 重複執行會直接覆蓋同名檔案，保持目錄整潔
🏗️ **模組化架構**: 使用現代化 src/ 目錄結構和抽象基礎類別
🌐 **跨平台相容**: 支援 macOS、Windows、Linux 系統
🖥️ **Windows 友善**: Unicode 字符自動轉換，完美支援中文 Windows 環境

## 專案結構

```
SeleniumPelican/
├── src/                          # 所有 Python 原始碼
│   ├── core/                     # 核心模組
│   │   ├── base_scraper.py       # 基礎爬蟲類別
│   │   ├── multi_account_manager.py  # 多帳號管理器
│   │   ├── browser_utils.py      # 瀏覽器初始化工具
│   │   └── config_validator.py   # 配置檔案驗證系統
│   ├── scrapers/                 # 具體實作的爬蟲
│   │   ├── payment_scraper.py    # 代收貨款查詢工具
│   │   ├── freight_scraper.py    # 運費查詢工具
│   │   └── unpaid_scraper.py     # 運費未請款明細工具
│   └── utils/                    # 工具模組
│       └── windows_encoding_utils.py  # Windows 相容性工具
├── tests/                        # 測試框架 (pytest)
│   ├── unit/                     # 單元測試
│   ├── integration/              # 整合測試
│   └── fixtures/                 # 測試夾具
├── scripts/                      # 執行腳本
│   ├── common_checks.ps1/.sh     # 共用檢查函數
│   ├── run_*.ps1                 # PowerShell 執行腳本
│   ├── install.ps1/.sh           # 安裝腳本
│   └── update.ps1/.sh            # 更新腳本
├── Windows_代收貨款查詢.cmd      # 標準化執行腳本 (Windows)
├── Linux_代收貨款查詢.sh         # 標準化執行腳本 (Linux/macOS)
├── Windows_運費查詢.cmd          # 運費查詢 (Windows)
├── Linux_運費查詢.sh             # 運費查詢 (Linux/macOS)
├── Windows_運費未請款明細.cmd     # 運費未請款明細 (Windows)
├── Linux_運費未請款明細.sh       # 運費未請款明細 (Linux/macOS)
├── Windows_配置驗證.cmd          # 配置驗證 (Windows)
├── Linux_配置驗證.sh             # 配置驗證 (Linux/macOS)
├── Windows_安裝.cmd              # 系統安裝 (Windows)
├── Linux_安裝.sh                 # 系統安裝 (Linux/macOS)
├── Windows_更新.cmd              # 系統更新 (Windows)
├── Linux_更新.sh                 # 系統更新 (Linux/macOS)
├── accounts.json                 # 帳號設定檔
├── pyproject.toml               # Python 專案設定
├── pytest.ini                   # pytest 測試設定
└── uv.lock                      # 鎖定依賴版本
```

## 自動更新 🔄

保持工具為最新版本，享受最新功能和錯誤修復：

### 標準化更新方式 ⚡

**Windows**：
```cmd
# 雙擊執行或在命令提示字元中執行（自動啟動 PowerShell 7）
Windows_更新.cmd
```

**Linux/macOS**：
```bash
./Linux_更新.sh
```

### 更新功能特色

✅ **智能檢查** - 自動檢查是否有新版本可用
💾 **安全更新** - 自動暫存未提交的變更，避免資料遺失
📦 **依賴同步** - 檢測到 pyproject.toml 變更時自動更新套件
🔄 **變更還原** - 更新完成後自動還原之前的變更
🛡️ **衝突處理** - 遇到合併衝突時提供清楚的處理指引
🌐 **網路檢查** - 更新前驗證網路連線和 Git 權限

> **小提示**: 定期執行更新以獲得最佳體驗和最新功能！

## Windows 建議安裝 💻

為了獲得最佳的 Windows 使用體驗，建議安裝以下工具：

### Windows Terminal
1. 開啟 Microsoft Store
   • 在開始選單搜尋「Microsoft Store」
   • 搜尋 Windows Terminal
   • 或直接點這裡：[Windows Terminal 下載](https://www.microsoft.com/store/productId/9N0DX20HK701)
2. 點「取得」→ 安裝完成後打開。

### 安裝 PowerShell 7
PowerShell 7 的彩色支援比舊版 PowerShell / CMD 完整許多，而且相容性很好。

在 PowerShell (舊版) 或 CMD 輸入：
```cmd
winget install --id Microsoft.Powershell --source winget
```

安裝完成後，在 Windows Terminal 裡會自動多一個 Profile 叫「PowerShell 7」。

### 🎨 設定 Windows Terminal 預設 Profile
1. 打開 Windows Terminal
2. 按 Ctrl + , 開啟設定
3. 在「啟動」→「預設設定檔」改成 PowerShell 7（或你想要的 Git Bash / WSL）
4. 按下儲存，之後每次開 Terminal 都用新的 Shell。

### Git 安裝
本專案使用 Git 進行版本控制和自動更新功能，請確保已安裝 Git：

**方法一：使用 winget（推薦）**
```cmd
winget install --id Git.Git -e --source winget
```

**方法二：官網下載**
- 前往 [Git 官網](https://git-scm.com/download/win) 下載安裝程式
- 執行安裝程式，建議保持預設設定
- 安裝完成後重新啟動命令提示字元或 PowerShell

**驗證安裝**：
```cmd
git --version
```

> **小提示**：安裝 Git 時會一併安裝 Git Bash，這是一個優秀的 Unix-like 命令列環境，也可以在 Windows Terminal 中使用。

## 快速開始 🚀

### 方法一：一鍵自動安裝 (推薦) ⚡

**Windows**：
```cmd
# 雙擊執行或在命令提示字元中執行（自動啟動 PowerShell 7）
Windows_安裝.cmd
```

**macOS/Linux**：
```bash
# 執行自動安裝腳本
./Linux_安裝.sh
```

安裝腳本會自動：
- ✅ 檢測系統環境（Python、Git、Chrome）
- ✅ 安裝 uv 套件管理工具
- ✅ 建立虛擬環境並安裝依賴
- ✅ 設定配置檔案（.env、accounts.json）
- ✅ 建立必要目錄結構
- ✅ 執行配置驗證和基本測試

### 方法二：手動安裝

#### 1. 安裝 Python 和 uv
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. 建立環境並安裝依賴
```bash
# 自動建立虛擬環境並安裝依賴
uv sync
```

#### 3. 環境設定
```bash
# 複製環境設定範例檔案
cp .env.example .env

# 編輯 .env 檔案，設定你的 Chrome 瀏覽器路徑
# macOS 範例: CHROME_BINARY_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Windows 範例: CHROME_BINARY_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
```

## 使用方式

### 快速執行 ⚡

**代收貨款查詢**：
```bash
# Windows
Windows_代收貨款查詢.cmd

# Linux/macOS
./Linux_代收貨款查詢.sh
```

**運費查詢**：
```bash
# Windows
Windows_運費查詢.cmd

# Linux/macOS
./Linux_運費查詢.sh
```

**運費未請款明細**：
```bash
# Windows
Windows_運費未請款明細.cmd

# Linux/macOS
./Linux_運費未請款明細.sh
```

**配置驗證**：
```bash
# Windows
Windows_配置驗證.cmd

# Linux/macOS
./Linux_配置驗證.sh
```

### 詳細使用說明

#### 代收貨款查詢

**標準化執行方式 (推薦)**：
```bash
# Windows
Windows_代收貨款查詢.cmd

# Linux/macOS
./Linux_代收貨款查詢.sh

# 指定日期範圍
Windows_代收貨款查詢.cmd --start-date 20241201 --end-date 20241208
./Linux_代收貨款查詢.sh --start-date 20241201 --end-date 20241208

# 背景執行模式
Windows_代收貨款查詢.cmd --headless
./Linux_代收貨款查詢.sh --headless
```

**手動執行**：
```bash
# macOS/Linux
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/payment_scraper.py

# Windows (命令提示字元)
set PYTHONPATH=%cd%
set PYTHONUNBUFFERED=1
uv run python -u src\scrapers\payment_scraper.py
```

### 運費查詢

**標準化執行方式 (推薦)**：
```bash
# Windows
Windows_運費查詢.cmd

# Linux/macOS
./Linux_運費查詢.sh

# 指定月份範圍
Windows_運費查詢.cmd --start-month 202411 --end-month 202412
./Linux_運費查詢.sh --start-month 202411 --end-month 202412

# 背景執行模式
Windows_運費查詢.cmd --headless
./Linux_運費查詢.sh --headless
```

**手動執行**：
```bash
# macOS/Linux
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/freight_scraper.py

# Windows (命令提示字元)
set PYTHONPATH=%cd%
set PYTHONUNBUFFERED=1
uv run python -u src\scrapers\freight_scraper.py
```

### 運費未請款明細

**標準化執行方式 (推薦)**：
```bash
# Windows
Windows_運費未請款明細.cmd

# Linux/macOS
./Linux_運費未請款明細.sh

# 背景執行模式
Windows_運費未請款明細.cmd --headless
./Linux_運費未請款明細.sh --headless
```

**手動執行**：
```bash
# macOS/Linux
PYTHONPATH="$(pwd)" uv run python -u src/scrapers/unpaid_scraper.py

# Windows (命令提示字元)
set PYTHONPATH=%cd%
set PYTHONUNBUFFERED=1
uv run python -u src\scrapers\unpaid_scraper.py
```

## 自動執行流程

### 代收貨款查詢流程：
1. 📅 **日期設定** - 支援互動式輸入或命令列參數，預設往前7天
2. 🔐 **自動登入** - 讀取 `accounts.json` 中的帳號資訊
3. 🧭 **智能導航** - 導航到代收貨款查詢頁面，處理複雜的 iframe 結構
4. 📊 **精準篩選** - 只搜尋「代收貨款匯款明細」，排除其他項目
5. 📥 **自動下載** - 下載 Excel 檔案到 `downloads/` 目錄
6. 📝 **智能重命名** - 檔案重命名為 `帳號_編號.xlsx` 格式
7. 👥 **多帳號處理** - 依序處理所有啟用的帳號
8. 📋 **生成報告** - 產生詳細的執行報告

### 運費查詢流程：
1. 📅 **月份設定** - 支援月份範圍查詢（YYYYMM 格式），預設上個月
2. 🔐 **自動登入** - 讀取帳號設定檔
3. 🧭 **智能導航** - 導航到運費(月結)結帳資料查詢頁面
4. 📊 **搜尋運費記錄** - 搜尋 (2-7) 運費相關的結帳資料
5. 📥 **自動下載** - 下載 Excel 檔案
6. 📝 **智能重命名** - 檔案重命名為 `帳號_freight_編號.xlsx` 格式
7. 👥 **批次處理** - 處理所有啟用的帳號
8. 📋 **總結報告** - 產生執行統計和結果報告

### 運費未請款明細流程：
1. 📅 **自動設定日期** - 預設結束時間為當日，無需使用者輸入
2. 🔐 **自動登入** - 讀取帳號設定檔
3. 🧭 **智能導航** - 導航到運費未請款明細頁面
4. 📊 **直接抓取表格** - 使用 BeautifulSoup 解析 HTML 表格數據
5. 📥 **生成 Excel** - 直接從表格數據創建 Excel 檔案
6. 📝 **智能重命名** - 檔案重命名為 `帳號_FREIGHT_日期.xlsx` 格式
7. 👥 **批次處理** - 處理所有啟用的帳號
8. 📋 **總結報告** - 產生執行統計和結果報告

## 智能驗證碼偵測

系統採用多層次驗證碼偵測策略：

### 🎯 方法1: 紅色字體偵測（主要方法）
- 專門偵測頁面右側紅色字體的4碼英數字
- 根據 WEDI 系統特性，驗證碼通常以紅色字體顯示

### 📋 方法2: 識別碼標籤偵測
- 搜尋包含「識別碼:」標籤的文字
- 分析標籤後的4碼英數字內容

### 📄 方法3: 表格結構偵測
- 掃描頁面表格中的4碼英數字
- 排除常見的干擾詞彙（如 POST、GET 等）

### 🔍 方法4: 全頁面搜尋
- 掃描整個頁面的4碼英數字
- 過濾年份等非驗證碼內容

### ⌛ 方法5: 手動輸入備案
- 自動偵測失敗時，提供20秒手動輸入時間
- 注意：背景模式（--headless）無法手動輸入

## 設定檔案

### accounts.json
設定要處理的帳號清單（⚠️ 此檔案不會被 Git 追蹤）：

> **安全提醒**：請參考 `accounts.json.example` 建立此檔案，切勿將真實密碼提交到版本控制系統。

```json
{
  "accounts": [
    {"username": "0000000001", "password": "your_password", "enabled": true},
    {"username": "0000000002", "password": "your_password", "enabled": false}
  ],
  "settings": {
    "headless": false,
    "download_base_dir": "downloads"
  }
}
```

**重要設定說明**：
- `enabled: true/false` - 控制要處理哪些帳號
- `headless: true/false` - 是否使用背景模式（無法手動輸入驗證碼）
- 已加入 `.gitignore`，不會意外提交敏感資訊

### .env
設定 Chrome 瀏覽器路徑：
```bash
# macOS
CHROME_BINARY_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Windows
CHROME_BINARY_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"

# Linux
CHROME_BINARY_PATH="/usr/bin/google-chrome"
```

## 輸出結構

```
downloads/              # 下載的 Excel 檔案
├── 0000000001_12345678.xlsx          # 代收貨款明細
├── 0000000001_freight_20241101.xlsx  # 運費記錄
├── 0000000001_FREIGHT_20241215.xlsx  # 運費未請款明細
└── ...

reports/               # 執行報告
├── 20240912_132926.json
└── ...

logs/                 # 執行日誌
temp/                 # 暫存檔案
```

## 現代化特色

### 🏗️ 模組化架構
- 採用 `src/` 目錄結構，符合現代 Python 專案標準
- 根目錄保持整潔，不包含 Python 檔案
- 清晰的模組分離：core（核心）、scrapers（實作）、utils（工具）

### 📦 現代依賴管理
- 使用 `pyproject.toml` + `uv.lock` 管理依賴
- 快速且可重現的環境安裝
- 自動版本鎖定，避免依賴衝突

### 🖥️ Windows 完美相容
- 實作 `safe_print()` 函數處理 Unicode 字符顯示
- 所有 Unicode 字符（如 ✅ ❌ 🎉）自動轉換為純文字標籤
- 在 Windows 命令提示字元中完美顯示中文和符號

### 🚀 優化執行體驗
- 提供跨平台執行腳本（.sh、.cmd、.ps1）
- Windows 自動啟動 PowerShell 7，享受完整 UTF-8 支援和彩色輸出
- 自動設定必要的環境變數
- 簡化使用者執行流程

## 技術特色

### 智能導航系統
- 使用 iframe 處理 WEDI 系統的巢狀結構
- 自動處理複雜的頁面跳轉和導航
- 避免因切換 iframe 導致的崩潰問題

### 精準篩選機制
- 專門搜尋包含「代收貨款」和「匯款明細」的項目
- 排除「代收款已收未結帳明細」等不需要的項目
- 確保只下載真正需要的匯款明細表

### 多視窗處理
- 支援多個匯款編號的並行處理
- 使用新視窗方式避免頁面衝突
- 智能管理視窗開關和 iframe 切換

## 故障排除

### 🔧 常見問題

**Q: Chrome 瀏覽器啟動失敗**
A: 檢查 `.env` 檔案中的 `CHROME_BINARY_PATH` 是否正確

**Q: Windows 顯示亂碼或符號異常**
A: 程式已內建 Unicode 相容處理，會自動轉換為純文字顯示

**Q: 執行時顯示「模組找不到」**
A: 確認是否使用了正確的執行腳本，會自動設定 PYTHONPATH

**Q: 驗證碼偵測失敗**
A: 程式會自動嘗試多種偵測方法，失敗時會等待手動輸入

**Q: 找不到代收貨款項目**
A: 檢查帳號是否有代收貨款匯款明細的查詢權限，或該日期範圍是否有資料

**Q: 想要背景執行但無法輸入驗證碼**
A: 背景模式無法手動輸入驗證碼，建議先確認自動偵測功能正常

**Q: 多帳號執行時中斷**
A: 程式採用容錯設計，個別帳號失敗不會影響其他帳號處理


## 依賴套件

- `selenium` - 網頁自動化框架
- `webdriver-manager` - Chrome WebDriver 自動管理
- `python-dotenv` - 環境變數管理
- `beautifulsoup4` - HTML 解析工具
- `openpyxl` - Excel 檔案處理
- `requests` - HTTP 請求處理

## 注意事項

⚠️ **使用須知**:
- 請確保有權限存取 WEDI 系統
- 確認帳號有相應資料的查詢權限
- 遵守網站的使用條款和服務協議
- 適度使用，避免對伺服器造成過大負載
- 定期檢查腳本是否因網站更新而需要調整

🔒 **安全提醒**:
- `accounts.json` 已加入 `.gitignore`，不會被版本控制追蹤
- 請定期更改密碼，確保帳號安全
- 切勿在公開場所或文件中暴露真實密碼
- 建議使用強密碼並啟用雙因素認證（如果支援）
- 如發現密碼洩露，請立即更改所有相關帳號密碼

📝 **法律聲明**: 此工具僅供學習和合法用途使用，使用者需自行承擔使用責任。