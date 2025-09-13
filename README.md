# WEDI 宅配通自動下載工具 📦

一個使用 Python + Selenium 建立的自動化工具，專門用於自動登入 WEDI（宅配通）系統並下載代收貨款匯款明細。

## 功能特色

✨ **自動登入**: 自動填入客代和密碼
🤖 **智能驗證碼偵測**: 多層次自動偵測右側4碼英數字驗證碼
📥 **精準下載**: 專門下載代收貨款匯款明細 Excel 檔案
👥 **多帳號支援**: 批次處理多個帳號，自動產生總結報告
📅 **彈性日期**: 支援命令列參數指定查詢日期範圍
📝 **智能檔案命名**: 檔案自動命名為 `帳號_編號.xlsx` 格式
🔄 **檔案覆蓋**: 重複執行會直接覆蓋同名檔案，保持目錄整潔
🌐 **跨平台**: 支援 macOS、Windows、Linux 系統

## 快速開始 🚀

### Windows 新手用戶 🪟

**完全沒有程式經驗？請先安裝基礎環境：**

1. **安裝 Python**
   - 前往：https://www.python.org/downloads/
   - 點擊黃色 "Download Python" 按鈕
   - **重要**：安裝時勾選 "Add Python to PATH"

2. **安裝 Chrome**
   - 前往：https://www.google.com/chrome/
   - 下載並安裝

3. **執行安裝**
   - 雙擊專案中的 `setup.cmd`
   - 等待安裝完成

### 方法一：一鍵自動安裝 (推薦) ⚡

**macOS/Linux**：
```bash
# 下載並執行自動安裝
chmod +x setup.sh && ./setup.sh
```

**Windows**：
```cmd
# 雙擊執行
setup.cmd
```

安裝腳本會自動：
- ✅ 檢測並安裝 Python
- ✅ 安裝 uv 套件管理工具
- ✅ 自動偵測 Chrome 路徑
- ✅ 建立虛擬環境並安裝依賴

### 方法二：手動安裝

如果您偏好手動控制安裝過程：

#### 1. 安裝 Python
- **Windows**: 從 [python.org](https://www.python.org/downloads/) 下載安裝
- **macOS**: `brew install python3` 或從官網下載
- **Linux**: `sudo apt install python3 python3-pip` (Ubuntu/Debian)

#### 2. 安裝 uv (Python 套件管理工具)
```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 3. 建立環境並安裝依賴
```bash
# 自動建立虛擬環境並安裝依賴
uv sync

# 或手動建立
uv venv
uv sync
```

#### 4. 環境設定
```bash
# 複製環境設定範例檔案
cp .env.example .env

# 編輯 .env 檔案，設定你的 Chrome 瀏覽器路徑
# macOS 範例: CHROME_BINARY_PATH="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
# Windows 範例: CHROME_BINARY_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
```

### 5. 快速執行

**macOS/Linux 系統**：
```bash
# 使用 shell script (推薦)
./run.sh

# 或直接使用 uv 執行
uv run python wedi_selenium_scraper.py
```

**Windows 系統**：
```cmd
# 使用批次檔 (推薦)
run.cmd

# 或直接使用虛擬環境執行
.venv\Scripts\python.exe wedi_selenium_scraper.py
```

## 使用方式

### 基本使用

**macOS/Linux**：
```bash
# 互動式執行（會提示輸入開始日期）
./run.sh

# 無頭模式（背景執行）
./run.sh --headless

# 或直接使用 uv 指定日期範圍
uv run python wedi_selenium_scraper.py --start-date 20241201 --end-date 20241208
```

**Windows**：
```cmd
# 互動式執行（會提示輸入開始日期）
run.cmd

# 無頭模式（背景執行）
run.cmd --headless

# 或直接使用 Python 指定日期範圍
.venv\Scripts\python.exe wedi_selenium_scraper.py --start-date 20241201
```

### 自動執行流程

程式會自動執行以下步驟：

1. 📅 **互動式日期輸入** - 提示輸入開始日期，直接按 Enter 使用預設值（往前7天）
2. 🔐 **自動登入系統** - 讀取 `accounts.json` 中的帳號資訊
3. 🧭 **智能導航** - 導航到代收貨款查詢頁面，處理複雜的 iframe 結構
4. 📅 **設定日期範圍** - 使用輸入的日期或預設往前7天範圍
5. 📊 **精準篩選** - 只搜尋「代收貨款匯款明細」，排除其他項目
6. 📥 **自動下載** - 下載 Excel 檔案到 `downloads/` 目錄
7. 📝 **智能重命名** - 檔案重命名為 `帳號_編號.xlsx` 格式
8. 👥 **多帳號處理** - 依序處理所有啟用的帳號
9. 📋 **生成報告** - 產生 JSON 格式的總結報告

## 驗證碼偵測策略

腳本採用多層次驗證碼偵測方法：

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

## 檔案命名格式

下載的檔案會自動重命名為：
- **格式**: `帳號_編號.xlsx`
- **範例**: `5081794201_12345678.xlsx`
- **覆蓋**: 重複執行會直接覆蓋同名檔案

## 輸出結構

```
downloads/              # 下載的 Excel 檔案
├── 5081794201_12345678.xlsx
├── 5081794202_87654321.xlsx
└── ...

reports/               # 執行報告
├── multi_account_report_20240912_132926.json
└── ...

logs/                 # 執行日誌
temp/                 # 暫存檔案
```

## 設定檔案

### accounts.json
設定要處理的帳號清單：
```json
{
  "accounts": [
    {"username": "5081794201", "password": "your_password", "enabled": true},
    {"username": "5081794202", "password": "your_password", "enabled": false}
  ],
  "settings": {
    "headless": false,
    "download_base_dir": "downloads"
  }
}
```

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

**Q: Windows 顯示「找不到模組」錯誤**
A: 虛擬環境未正確安裝，重新執行 `setup.cmd`

**Q: 設定檔案中 headless: true 但還是顯示瀏覽器**
A: 使用 `./run.sh` 或 `run.cmd` 會正確讀取設定檔案中的 headless 設定

**Q: 驗證碼偵測失敗**
A: 程式會自動嘗試多種偵測方法，失敗時會等待手動輸入

**Q: iframe 導航錯誤**
A: 程式已優化 iframe 處理，如遇問題請檢查 logs 目錄

**Q: 找不到代收貨款項目**
A: 檢查帳號是否有代收貨款匯款明細的查詢權限，或該日期範圍是否有資料

**Q: 只想處理特定帳號**
A: 在 `accounts.json` 中將不需要的帳號設為 `"enabled": false`

**Q: 想要背景執行**
A: 使用 `--headless` 參數或在 `accounts.json` 中設定 `"headless": true`

**Q: 下載的檔案不是代收貨款匯款明細**
A: 程式已設定精準過濾，只會下載包含「代收貨款」和「匯款明細」的項目

## 依賴套件

- `selenium` - 網頁自動化
- `webdriver-manager` - Chrome WebDriver 管理
- `python-dotenv` - 環境變數管理
- `beautifulsoup4` - HTML 解析
- `openpyxl` - Excel 檔案處理
- `requests` - HTTP 請求處理

## 注意事項

⚠️ **使用須知**:
- 請確保有權限存取 WEDI 系統
- 確認帳號有代收貨款匯款明細的查詢權限
- 遵守網站的使用條款
- 適度使用，避免對伺服器造成過大負載
- 定期檢查腳本是否因網站更新而需要調整

📝 **法律聲明**: 此工具僅供學習和合法用途使用