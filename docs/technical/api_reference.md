# API 參考文檔

## 概述

SeleniumPelican 提供了清晰的 API 介面，讓開發者能夠輕鬆擴展功能或整合到其他系統中。本文檔詳細描述了所有公開的類別、方法和介面。

## 🏛️ 核心 API

### BaseScraper

**路徑**: `src.core.base_scraper.BaseScraper`

所有爬蟲的抽象基礎類別，定義了標準的爬取流程和通用方法。

#### 類別定義

```python
class BaseScraper(ABC):
    """網頁爬蟲抽象基礎類別

    提供標準的爬取流程和通用方法，子類別需要實作特定的業務邏輯。
    """
```

#### 主要方法

##### `__init__(self, config=None)`

建構函式，初始化爬蟲實例。

**參數**:
- `config` (dict, optional): 配置字典

**範例**:
```python
scraper = PaymentScraper({
    'timeout': 30,
    'headless': False
})
```

##### `execute(self, account_info)`

主要執行方法，實作 Template Method 模式。

**參數**:
- `account_info` (dict): 帳號資訊字典

**返回值**:
- `list`: 爬取結果列表

**拋出異常**:
- `WebDriverException`: 瀏覽器操作失敗
- `LoginError`: 登入失敗
- `DataExtractionError`: 資料提取失敗

**範例**:
```python
account = {
    'username': 'test_user',
    'password': 'test_password'
}
results = scraper.execute(account)
```

##### `setup_browser(self, headless=None, download_dir=None)`

設置瀏覽器環境。

**參數**:
- `headless` (bool, optional): 是否使用無頭模式
- `download_dir` (str, optional): 下載目錄路徑

**範例**:
```python
scraper.setup_browser(headless=True, download_dir='./downloads')
```

##### `login(self, username, password)`

執行登入操作，包含驗證碼處理。

**參數**:
- `username` (str): 使用者名稱
- `password` (str): 密碼

**返回值**:
- `bool`: 登入是否成功

**範例**:
```python
success = scraper.login('username', 'password')
if success:
    print("登入成功")
```

##### `navigate_to_query(self)`

導航到查詢頁面。

**返回值**:
- `bool`: 導航是否成功

##### `cleanup(self)`

清理資源，關閉瀏覽器。

**範例**:
```python
try:
    results = scraper.execute(account)
finally:
    scraper.cleanup()  # 確保資源清理
```

#### 抽象方法 (子類別必須實作)

##### `get_query_params(self)`

取得查詢參數。

**返回值**:
- `dict`: 查詢參數字典

##### `process_results(self)`

處理查詢結果。

**返回值**:
- `list`: 處理後的結果列表

#### 工具方法

##### `safe_click(self, element, retries=3)`

安全點擊元素，包含重試機制。

**參數**:
- `element` (WebElement): Selenium 元素
- `retries` (int): 重試次數，預設 3

**返回值**:
- `bool`: 點擊是否成功

##### `wait_for_element(self, by, value, timeout=30)`

等待元素出現。

**參數**:
- `by` (By): 定位方法
- `value` (str): 定位值
- `timeout` (int): 超時時間（秒）

**返回值**:
- `WebElement`: 找到的元素

**拋出異常**:
- `TimeoutException`: 等待超時

---

### MultiAccountManager

**路徑**: `src.core.multi_account_manager.MultiAccountManager`

多帳號管理器，負責批次處理多個帳號。

#### 類別定義

```python
class MultiAccountManager:
    """多帳號批次處理管理器"""
```

#### 主要方法

##### `__init__(self, scraper_class)`

建構函式。

**參數**:
- `scraper_class` (class): 爬蟲類別

**範例**:
```python
manager = MultiAccountManager(PaymentScraper)
```

##### `load_accounts(self, config_path='accounts.json')`

載入帳號配置。

**參數**:
- `config_path` (str): 配置檔案路徑

**返回值**:
- `list`: 帳號列表

**拋出異常**:
- `FileNotFoundError`: 配置檔案不存在
- `json.JSONDecodeError`: 配置格式錯誤

##### `execute_all(self)`

批次執行所有啟用的帳號。

**返回值**:
- `dict`: 執行結果摘要

**範例**:
```python
manager = MultiAccountManager(PaymentScraper)
results = manager.execute_all()
print(f"成功處理 {results['success_count']} 個帳號")
```

##### `process_account(self, account_config)`

處理單個帳號。

**參數**:
- `account_config` (dict): 帳號配置

**返回值**:
- `dict`: 處理結果

##### `generate_summary(self, results)`

生成執行摘要報告。

**參數**:
- `results` (list): 執行結果列表

**返回值**:
- `dict`: 摘要報告

---

## 🔧 實作類別 API

### PaymentScraper

**路徑**: `src.scrapers.payment_scraper.PaymentScraper`

代收貨款查詢爬蟲。

#### 特有方法

##### `set_date_range(self, start_date, end_date)`

設定查詢日期範圍。

**參數**:
- `start_date` (str): 開始日期 (YYYYMMDD)
- `end_date` (str): 結束日期 (YYYYMMDD)

**範例**:
```python
scraper = PaymentScraper()
scraper.set_date_range('20241201', '20241208')
```

##### `filter_payment_records(self, records)`

過濾代收貨款記錄。

**參數**:
- `records` (list): 原始記錄列表

**返回值**:
- `list`: 過濾後的記錄

**過濾條件**:
- 包含「代收貨款」關鍵字
- 包含「匯款明細」關鍵字
- 不包含「已收未結帳」關鍵字

##### `download_excel_file(self, record_link)`

下載 Excel 檔案。

**參數**:
- `record_link` (WebElement): 下載連結元素

**返回值**:
- `str`: 下載檔案路徑

---

### FreightScraper

**路徑**: `src.scrapers.freight_scraper.FreightScraper`

運費查詢爬蟲。

#### 特有方法

##### `set_month_range(self, start_month, end_month)`

設定查詢月份範圍。

**參數**:
- `start_month` (str): 開始月份 (YYYYMM)
- `end_month` (str): 結束月份 (YYYYMM)

##### `extract_freight_data(self, data_element)`

提取運費數據。

**參數**:
- `data_element` (WebElement): 包含數據的元素

**返回值**:
- `dict`: 運費數據字典

---

### UnpaidScraper

**路徑**: `src.scrapers.unpaid_scraper.UnpaidScraper`

運費未請款明細爬蟲。

#### 特有方法

##### `parse_html_table(self, table_html)`

解析 HTML 表格。

**參數**:
- `table_html` (str): HTML 表格字符串

**返回值**:
- `list`: 解析後的數據列表

##### `convert_to_excel(self, data, filename)`

將數據轉換為 Excel 檔案。

**參數**:
- `data` (list): 數據列表
- `filename` (str): 輸出檔案名

**返回值**:
- `str`: Excel 檔案路徑

---

## 🛠️ 工具類別 API

### browser_utils

**路徑**: `src.core.browser_utils`

瀏覽器工具模組。

#### 函數

##### `setup_chrome_driver(headless=False, download_dir=None)`

建立 Chrome WebDriver 實例。

**參數**:
- `headless` (bool): 是否無頭模式
- `download_dir` (str): 下載目錄

**返回值**:
- `webdriver.Chrome`: Chrome WebDriver 實例

**範例**:
```python
from src.core.browser_utils import setup_chrome_driver

driver = setup_chrome_driver(
    headless=True,
    download_dir='./downloads'
)
```

##### `get_chrome_binary_path()`

取得 Chrome 執行檔路徑。

**返回值**:
- `str`: Chrome 執行檔路徑

**平台支援**:
- macOS: `/Applications/Google Chrome.app/Contents/MacOS/Google Chrome`
- Windows: `C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe`
- Linux: `/usr/bin/google-chrome`

---

### windows_encoding_utils

**路徑**: `src.utils.windows_encoding_utils`

Windows 編碼相容工具。

#### 函數

##### `safe_print(text)`

安全輸出文字，自動處理跨平台編碼問題。

**參數**:
- `text` (str): 要輸出的文字

**範例**:
```python
from src.utils.windows_encoding_utils import safe_print

safe_print("✅ 操作成功")  # Windows 會顯示 "[PASS] 操作成功"
```

**字符對應表**:
- `✅` → `[PASS]`
- `❌` → `[FAIL]`
- `⚠️` → `[WARN]`
- `🎉` → `[DONE]`
- `🔍` → `[SEARCH]`

##### `check_encoding_support()`

檢查當前環境的編碼支援。

**返回值**:
- `dict`: 編碼支援資訊

---

## 🔧 配置 API

### 帳號配置格式

```json
{
  "accounts": [
    {
      "username": "帳號名稱",
      "password": "密碼",
      "enabled": true,
      "display_name": "顯示名稱 (可選)"
    }
  ],
  "settings": {
    "headless": false,
    "download_base_dir": "./downloads",
    "timeout": 30,
    "retry_count": 3
  }
}
```

### 環境配置 (.env)

```bash
# Chrome 執行檔路徑
CHROME_BINARY_PATH="/path/to/chrome"

# 日誌級別
LOG_LEVEL="INFO"

# 下載超時時間 (秒)
DOWNLOAD_TIMEOUT="60"
```

---

## 📊 回呼和事件 API

### 事件處理器

可以註冊事件處理器來監聽爬蟲執行過程：

```python
class CustomEventHandler:
    def on_login_success(self, account, scraper):
        """登入成功時觸發"""
        print(f"✅ {account['username']} 登入成功")

    def on_login_failed(self, account, error):
        """登入失敗時觸發"""
        print(f"❌ {account['username']} 登入失敗: {error}")

    def on_data_extracted(self, account, data):
        """資料提取完成時觸發"""
        print(f"📊 {account['username']} 提取 {len(data)} 筆資料")

# 使用事件處理器
handler = CustomEventHandler()
scraper = PaymentScraper()
scraper.add_event_handler(handler)
```

---

## 🐛 異常類別 API

### 自定義異常

```python
class ScraperError(Exception):
    """爬蟲基礎異常"""
    pass

class LoginError(ScraperError):
    """登入相關異常"""
    pass

class CaptchaError(ScraperError):
    """驗證碼處理異常"""
    pass

class DataExtractionError(ScraperError):
    """資料提取異常"""
    pass

class ConfigurationError(ScraperError):
    """配置錯誤異常"""
    pass
```

### 異常處理範例

```python
try:
    scraper = PaymentScraper()
    results = scraper.execute(account_info)
except LoginError as e:
    print(f"登入失敗: {e}")
except CaptchaError as e:
    print(f"驗證碼處理失敗: {e}")
except DataExtractionError as e:
    print(f"資料提取失敗: {e}")
except ScraperError as e:
    print(f"爬蟲錯誤: {e}")
```

---

## 🔌 擴展 API

### 建立自定義爬蟲

```python
from src.core.base_scraper import BaseScraper

class CustomScraper(BaseScraper):
    """自定義爬蟲範例"""

    def get_query_params(self):
        """實作查詢參數"""
        return {
            'query_type': 'custom',
            'date_range': self.date_range
        }

    def process_results(self):
        """實作結果處理"""
        # 自定義處理邏輯
        results = []
        # ... 處理邏輯
        return results

    def setup_additional_options(self):
        """可選：額外設置邏輯"""
        # 自定義設置
        pass

# 使用自定義爬蟲
scraper = CustomScraper()
manager = MultiAccountManager(CustomScraper)
```

### 自定義瀏覽器工廠

```python
class CustomWebDriverFactory:
    """自定義瀏覽器工廠"""

    @staticmethod
    def create_firefox_driver(config):
        """建立 Firefox WebDriver"""
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options

        options = Options()
        if config.get('headless'):
            options.add_argument('--headless')

        return webdriver.Firefox(options=options)

# 在 BaseScraper 中使用
class FirefoxScraper(BaseScraper):
    def setup_browser(self):
        factory = CustomWebDriverFactory()
        self.driver = factory.create_firefox_driver(self.config)
```

---

## 📈 監控和日誌 API

### 日誌配置

```python
import logging

# 設定日誌
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraper.log'),
        logging.StreamHandler()
    ]
)

# 在爬蟲中使用
class PaymentScraper(BaseScraper):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
```

### 效能監控

```python
import time
from functools import wraps

def monitor_performance(func):
    """效能監控裝飾器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            print(f"✅ {func.__name__} 執行完成，耗時 {duration:.2f} 秒")
            return result
        except Exception as e:
            duration = time.time() - start_time
            print(f"❌ {func.__name__} 執行失敗，耗時 {duration:.2f} 秒: {e}")
            raise
    return wrapper

# 使用監控裝飾器
class MonitoredScraper(BaseScraper):
    @monitor_performance
    def login(self, username, password):
        return super().login(username, password)

    @monitor_performance
    def process_results(self):
        return super().process_results()
```

---

## 🔄 版本相容性

### API 版本

- **當前版本**: 2.0.0
- **最小支援 Python**: 3.8
- **推薦 Python**: 3.11+

### 向前相容性

```python
# 檢查 API 版本
from src import __version__

if __version__ >= '2.0.0':
    # 使用新 API
    scraper = PaymentScraper(config={'timeout': 30})
else:
    # 使用舊 API
    scraper = PaymentScraper()
    scraper.timeout = 30
```

### 棄用警告

```python
import warnings

def deprecated_method():
    """已棄用的方法"""
    warnings.warn(
        "此方法將在 v3.0 中移除，請使用 new_method() 替代",
        DeprecationWarning,
        stacklevel=2
    )
```

這份 API 文檔提供了 SeleniumPelican 的完整程式介面參考，幫助開發者有效利用和擴展專案功能。
