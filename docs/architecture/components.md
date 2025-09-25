# 組件分析

## 核心組件架構

SeleniumPelican 採用分層組件架構，每個組件都有明確定義的責任和介面。以下是詳細的組件分析：

## 🏛️ 核心層組件 (`src/core/`)

### BaseScraper - 抽象基礎類別

**位置**: `src/core/base_scraper.py`
**角色**: 核心抽象類別，定義所有爬蟲的通用行為

#### 主要責任
- 🔧 Chrome WebDriver 生命週期管理
- 🔐 統一登入流程處理
- 🧭 標準化導航操作
- ❌ 基礎錯誤處理和重試機制
- 🔍 驗證碼自動偵測和處理

#### 核心方法
```python
class BaseScraper:
    # 抽象方法 - 子類必須實作
    def get_query_params(self) -> dict
    def process_results(self) -> list

    # 模板方法 - 定義標準流程
    def execute(self)
    def setup_browser(self)
    def login(self)
    def navigate_to_query(self)

    # 工具方法 - 提供共用功能
    def detect_captcha(self)
    def wait_for_element(self)
    def safe_click(self)
```

#### 設計特點
- **Template Method Pattern**: `execute()` 定義標準執行流程
- **Hook Methods**: 提供可選的擴展點
- **防禦性程式設計**: 大量的異常處理和容錯機制
- **配置驅動**: 支援動態配置調整

---

### MultiAccountManager - 多帳號管理器

**位置**: `src/core/multi_account_manager.py`
**角色**: 帳號配置管理和批次處理協調器

#### 主要責任
- 📋 帳號配置檔案讀取和解析
- 🔄 批次帳號處理協調
- 📊 統一報告生成和彙整
- 💉 爬蟲策略依賴注入
- 🛡️ 帳號級錯誤隔離

#### 核心方法
```python
class MultiAccountManager:
    def __init__(self, scraper_class)  # 依賴注入
    def load_accounts(self) -> list     # 配置載入
    def process_account(self, account)   # 單帳號處理
    def execute_all(self)               # 批次執行
    def generate_summary(self)          # 報告生成
```

#### 設計特點
- **Dependency Injection**: 支援不同爬蟲策略
- **Fail-Fast vs Fail-Safe**: 平衡錯誤處理策略
- **配置中心化**: 統一的設定管理
- **批次優化**: 高效的多帳號處理

#### 配置結構
```json
{
  "accounts": [
    {
      "username": "account1",
      "password": "password1",
      "enabled": true
    }
  ],
  "settings": {
    "headless": false,
    "download_base_dir": "./downloads"
  }
}
```

---

### browser_utils - 瀏覽器工具模組

**位置**: `src/core/browser_utils.py`
**角色**: 跨平台瀏覽器初始化和配置管理

#### 主要責任
- 🌐 跨平台 Chrome 路徑偵測
- ⚙️ WebDriver 配置標準化
- 🎭 無頭模式和視窗模式切換
- 📦 ChromeDriver 版本管理
- 🔧 瀏覽器選項優化

#### 核心功能
```python
def setup_chrome_driver(headless=False, download_dir=None):
    # 自動偵測平台和 Chrome 路徑
    # 配置下載選項和視窗設定
    # 返回配置完成的 WebDriver
```

#### 跨平台支援
```python
CHROME_PATHS = {
    "darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "win32": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "linux": "/usr/bin/google-chrome"
}
```

---

## 🔧 業務實作層組件 (`src/scrapers/`)

### PaymentScraper - 代收貨款爬蟲

**位置**: `src/scrapers/payment_scraper.py`
**角色**: 代收貨款匯款明細專用爬蟲

#### 特化功能
- 📅 日期範圍查詢邏輯 (YYYYMMDD 格式)
- 🔍 精確的項目過濾機制
- 📊 Excel 檔案下載處理
- 🏷️ 智慧檔名生成

#### 關鍵實作
```python
class PaymentScraper(BaseScraper):
    def get_query_params(self):
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'query_type': 'payment'
        }

    def process_results(self):
        # 過濾「代收貨款」+「匯款明細」項目
        # 排除「已收未結帳」類型
        # 生成下載連結清單
```

#### 過濾邏輯
```python
def is_payment_record(self, record_text):
    return ('代收貨款' in record_text and
            '匯款明細' in record_text and
            '已收未結帳' not in record_text)
```

---

### FreightScraper - 運費查詢爬蟲

**位置**: `src/scrapers/freight_scraper.py`
**角色**: 運費(月結)結帳資料專用爬蟲

#### 特化功能
- 🗓️ 月份範圍查詢 (YYYYMM 格式)
- 🔢 運費項目識別 (2-7) 分類
- 💾 data-fileblob 數據提取
- 📈 Excel 數據生成

#### 核心邏輯
```python
class FreightScraper(BaseScraper):
    def get_query_params(self):
        return {
            'start_month': self.start_month,
            'end_month': self.end_month,
            'category': '(2-7) 運費'
        }
```

---

### UnpaidScraper - 未請款明細爬蟲

**位置**: `src/scrapers/unpaid_scraper.py`
**角色**: 運費未請款明細專用爬蟲

#### 獨特設計
- 🌐 直接 HTML 表格解析
- 🍲 BeautifulSoup 數據提取
- ⏱️ 預設當日結束時間
- 📋 無需下載檔案的處理方式

#### 數據處理流程
```python
class UnpaidScraper(BaseScraper):
    def process_results(self):
        # 1. 抓取 HTML 表格
        # 2. BeautifulSoup 解析
        # 3. 數據清理和轉換
        # 4. 直接生成 Excel
```

---

## 🛠️ 工具支援層 (`src/utils/`)

### windows_encoding_utils - 編碼工具

**位置**: `src/utils/windows_encoding_utils.py`
**角色**: 跨平台編碼相容性處理

#### 核心功能
- 🔤 Unicode 字符安全顯示
- 🪟 Windows 命令列相容
- 🔄 自動字符轉換
- ⚙️ 環境變數檢查

#### 實作範例
```python
def safe_print(text):
    """安全列印 Unicode 字符"""
    if platform.system() == "Windows":
        # 轉換 emoji 和特殊字符
        text = text.replace('✅', '[PASS]')
        text = text.replace('❌', '[FAIL]')
        text = text.replace('🎉', '[DONE]')
    print(text)
```

---

## 🔗 組件互動關係

### 依賴關係圖
```
MultiAccountManager
    ↓ (依賴注入)
具體爬蟲類別 (PaymentScraper/FreightScraper/UnpaidScraper)
    ↓ (繼承)
BaseScraper
    ↓ (使用)
browser_utils + windows_encoding_utils
```

### 資料流向
```
accounts.json → MultiAccountManager → 具體爬蟲 → BaseScraper → 瀏覽器操作 → 結果輸出
```

### 錯誤傳播
```
瀏覽器錯誤 → BaseScraper 處理 → 具體爬蟲決策 → MultiAccountManager 記錄 → 使用者報告
```

---

## 🎯 設計原則體現

### 單一責任原則 (SRP)
- **BaseScraper**: 專注瀏覽器操作和通用流程
- **MultiAccountManager**: 專注帳號管理和批次處理
- **具體爬蟲**: 專注特定業務邏輯

### 開放封閉原則 (OCP)
- 對擴展開放：新爬蟲繼承 BaseScraper
- 對修改封閉：既有組件無需修改

### 依賴反轉原則 (DIP)
- MultiAccountManager 依賴抽象的爬蟲介面
- 具體實作可以靈活替換

### 介面隔離原則 (ISP)
- 各組件只暴露必要的公共介面
- 內部實作細節完全封裝

---

## 📊 組件品質指標

### 內聚性評估
- **高內聚**: 各組件職責明確，功能相關性強
- **BaseScraper**: 9/10 - 專注爬蟲核心邏輯
- **MultiAccountManager**: 8/10 - 統一管理職責
- **工具模組**: 9/10 - 單一功能導向

### 耦合性評估
- **低耦合**: 組件間依賴關係清晰且最小化
- **介面耦合**: 主要通過抽象介面交互
- **配置耦合**: 通過配置檔案而非硬編碼
- **運行時耦合**: 透過依賴注入實現

### 可維護性指標
- **可讀性**: 清晰的命名和文檔
- **可測試性**: 模組化設計便於單元測試
- **可擴展性**: 新功能易於新增
- **可配置性**: 豐富的配置選項

這個組件架構展現了現代軟體工程的最佳實踐，為專案的長期維護和擴展奠定了堅實基礎。