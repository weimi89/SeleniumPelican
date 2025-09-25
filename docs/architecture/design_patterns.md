# 設計模式分析

## 概述

SeleniumPelican 專案廣泛採用多種經典設計模式，創建了一個既靈活又穩健的架構。本文檔詳細分析專案中使用的設計模式及其實作細節。

## 🎭 行為型模式 (Behavioral Patterns)

### Template Method Pattern - 模板方法模式

**應用位置**: `BaseScraper` 類別
**目的**: 定義演算法骨架，讓子類別可以覆寫特定步驟而不改變演算法結構

#### 實作分析
```python
class BaseScraper:
    def execute(self):
        """模板方法 - 定義執行流程骨架"""
        self.setup_browser()       # 1. 具體方法
        if self.login():           # 2. 具體方法
            self.navigate_to_query()  # 3. 具體方法
            self.perform_query()      # 4. 抽象方法 (子類實作)
            self.process_results()    # 5. 抽象方法 (子類實作)
        self.cleanup()             # 6. 具體方法

    # 抽象方法 - 子類必須實作
    @abstractmethod
    def get_query_params(self):
        pass

    @abstractmethod
    def process_results(self):
        pass

    # 鉤子方法 - 子類可選擇性覆寫
    def setup_additional_options(self):
        pass
```

#### 各爬蟲的特化實作
```python
# PaymentScraper 實作
class PaymentScraper(BaseScraper):
    def get_query_params(self):
        return {
            'start_date': self.start_date,
            'end_date': self.end_date,
            'date_format': 'YYYYMMDD'
        }

    def process_results(self):
        # 代收貨款特有的過濾邏輯
        return self.filter_payment_records()

# FreightScraper 實作
class FreightScraper(BaseScraper):
    def get_query_params(self):
        return {
            'start_month': self.start_month,
            'end_month': self.end_month,
            'date_format': 'YYYYMM'
        }

    def process_results(self):
        # 運費資料特有的處理邏輯
        return self.extract_freight_data()
```

#### 模式優勢
- ✅ **程式碼重用**: 通用邏輯在基類中實作一次
- ✅ **一致性**: 所有爬蟲遵循相同的執行流程
- ✅ **擴展性**: 新爬蟲只需實作特定方法
- ✅ **維護性**: 修改通用邏輯只需更新基類

---

### Strategy Pattern - 策略模式

**應用位置**: `MultiAccountManager` 與爬蟲類別的關係
**目的**: 定義演算法家族，讓它們可以互相替換

#### 實作分析
```python
class MultiAccountManager:
    def __init__(self, scraper_class):
        """依賴注入 - 接收策略物件"""
        self.scraper_class = scraper_class  # 策略介面

    def process_account(self, account_config):
        """使用注入的策略執行任務"""
        scraper = self.scraper_class()  # 創建策略實例
        scraper.configure(account_config)
        return scraper.execute()        # 執行策略

# 使用範例
if __name__ == "__main__":
    # 根據命令列參數選擇策略
    if args.type == "payment":
        manager = MultiAccountManager(PaymentScraper)
    elif args.type == "freight":
        manager = MultiAccountManager(FreightScraper)
    elif args.type == "unpaid":
        manager = MultiAccountManager(UnpaidScraper)

    manager.execute_all()
```

#### 策略族群定義
```python
# 策略介面 (抽象基類)
class ScraperStrategy(ABC):
    @abstractmethod
    def execute(self): pass

    @abstractmethod
    def get_query_params(self): pass

# 具體策略實作
class PaymentStrategy(ScraperStrategy):
    """代收貨款查詢策略"""

class FreightStrategy(ScraperStrategy):
    """運費查詢策略"""

class UnpaidStrategy(ScraperStrategy):
    """未請款明細策略"""
```

#### 動態策略切換
```python
class AdvancedManager:
    def __init__(self):
        self.strategies = {
            'payment': PaymentScraper,
            'freight': FreightScraper,
            'unpaid': UnpaidScraper
        }

    def set_strategy(self, strategy_name):
        """運行時切換策略"""
        if strategy_name in self.strategies:
            self.current_strategy = self.strategies[strategy_name]
```

---

## 🏗️ 創建型模式 (Creational Patterns)

### Factory Method Pattern - 工廠方法模式

**應用位置**: `browser_utils.py` 的 WebDriver 創建
**目的**: 創建物件而不指定確切的類別

#### 實作分析
```python
class WebDriverFactory:
    """WebDriver 工廠類別"""

    @staticmethod
    def create_chrome_driver(config=None):
        """工廠方法 - 創建 Chrome WebDriver"""
        options = ChromeOptions()

        # 根據配置和平台創建不同的 WebDriver
        if config and config.get('headless'):
            options.add_argument('--headless')

        if config and config.get('download_dir'):
            prefs = {"download.default_directory": config['download_dir']}
            options.add_experimental_option("prefs", prefs)

        # 跨平台路徑處理
        chrome_path = WebDriverFactory._get_chrome_path()
        if chrome_path:
            options.binary_location = chrome_path

        return webdriver.Chrome(options=options)

    @staticmethod
    def _get_chrome_path():
        """平台特定的 Chrome 路徑偵測"""
        platform_paths = {
            "darwin": "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "win32": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
            "linux": "/usr/bin/google-chrome"
        }
        return platform_paths.get(platform.system().lower())

# 使用範例
class BaseScraper:
    def setup_browser(self):
        """使用工廠創建瀏覽器"""
        config = self.get_browser_config()
        self.driver = WebDriverFactory.create_chrome_driver(config)
```

#### 工廠模式優勢
- ✅ **封裝複雜性**: 隱藏 WebDriver 創建的複雜邏輯
- ✅ **跨平台支援**: 自動處理不同平台的差異
- ✅ **配置驅動**: 根據設定創建不同配置的物件
- ✅ **易於測試**: 可以輕鬆注入測試用的 WebDriver

---

### Builder Pattern - 建造者模式

**應用位置**: 查詢參數和配置建構
**目的**: 逐步建構複雜物件

#### 實作分析
```python
class QueryBuilder:
    """查詢參數建造者"""

    def __init__(self):
        self.query = {}

    def set_date_range(self, start, end):
        """設定日期範圍"""
        self.query['start_date'] = start
        self.query['end_date'] = end
        return self

    def set_query_type(self, query_type):
        """設定查詢類型"""
        self.query['type'] = query_type
        return self

    def set_format(self, date_format):
        """設定日期格式"""
        self.query['format'] = date_format
        return self

    def build(self):
        """建構最終的查詢參數"""
        return self.query.copy()

# 使用範例
class PaymentScraper(BaseScraper):
    def get_query_params(self):
        """使用建造者模式建構查詢參數"""
        return (QueryBuilder()
                .set_date_range(self.start_date, self.end_date)
                .set_query_type('payment')
                .set_format('YYYYMMDD')
                .build())
```

#### 配置建造者
```python
class BrowserConfigBuilder:
    """瀏覽器配置建造者"""

    def __init__(self):
        self.config = {}

    def headless(self, is_headless=True):
        self.config['headless'] = is_headless
        return self

    def download_directory(self, path):
        self.config['download_dir'] = path
        return self

    def window_size(self, width, height):
        self.config['window_size'] = (width, height)
        return self

    def build(self):
        return self.config

# 使用範例
config = (BrowserConfigBuilder()
          .headless(False)
          .download_directory('./downloads')
          .window_size(1920, 1080)
          .build())
```

---

## 🔧 結構型模式 (Structural Patterns)

### Adapter Pattern - 適配器模式

**應用位置**: `windows_encoding_utils.py`
**目的**: 讓不相容的介面可以協同工作

#### 實作分析
```python
class WindowsConsoleAdapter:
    """Windows 控制台輸出適配器"""

    # Unicode 字符對應表
    CHAR_MAPPINGS = {
        '✅': '[PASS]',
        '❌': '[FAIL]',
        '⚠️': '[WARN]',
        '🎉': '[DONE]',
        '🔍': '[SEARCH]',
        '📁': '[FOLDER]',
        '📄': '[FILE]'
    }

    @classmethod
    def safe_print(cls, text):
        """適配器方法 - 轉換並安全輸出"""
        if platform.system() == "Windows":
            # 轉換 Unicode 字符為 ASCII 相容文字
            for unicode_char, ascii_equiv in cls.CHAR_MAPPINGS.items():
                text = text.replace(unicode_char, ascii_equiv)

        # 統一輸出介面
        print(text, flush=True)

    @classmethod
    def safe_input(cls, prompt):
        """適配器方法 - 安全輸入"""
        adapted_prompt = cls._adapt_text(prompt)
        return input(adapted_prompt)

# 原始程式碼中的使用
from src.utils.windows_encoding_utils import safe_print

# 在各個模組中統一使用適配器
safe_print("✅ 登入成功")  # Windows: "[PASS] 登入成功"
safe_print("❌ 操作失败")  # Windows: "[FAIL] 操作失败"
```

#### 適配器模式優勢
- ✅ **跨平台相容**: 解決 Windows 控制台 Unicode 顯示問題
- ✅ **透明使用**: 開發者無需關心平台差異
- ✅ **統一介面**: 所有輸出通過適配器統一處理
- ✅ **易於維護**: 集中處理編碼轉換邏輯

---

### Facade Pattern - 外觀模式

**應用位置**: `MultiAccountManager` 作為系統外觀
**目的**: 提供統一的高層介面，簡化子系統的使用

#### 實作分析
```python
class MultiAccountManager:
    """系統外觀 - 提供簡化的操作介面"""

    def __init__(self, scraper_class):
        self.scraper_class = scraper_class
        self.accounts = []
        self.results = []

    def execute_all(self):
        """外觀方法 - 隱藏複雜的內部操作"""
        # 1. 載入配置
        self._load_configuration()

        # 2. 驗證環境
        self._validate_environment()

        # 3. 批次處理
        self._process_accounts()

        # 4. 生成報告
        self._generate_reports()

        # 5. 清理資源
        self._cleanup()

    def _load_configuration(self):
        """內部方法 - 配置載入邏輯"""
        with open('accounts.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.accounts = [acc for acc in config['accounts'] if acc['enabled']]
            self.settings = config['settings']

    def _process_accounts(self):
        """內部方法 - 複雜的帳號處理邏輯"""
        for account in self.accounts:
            try:
                scraper = self.scraper_class()
                scraper.configure(account, self.settings)
                result = scraper.execute()
                self.results.append(result)
            except Exception as e:
                self._handle_account_error(account, e)

# 客戶端使用 - 非常簡單
if __name__ == "__main__":
    manager = MultiAccountManager(PaymentScraper)
    manager.execute_all()  # 一個方法完成所有操作
```

#### 外觀模式優勢
- ✅ **簡化介面**: 客戶端只需一個方法調用
- ✅ **隱藏複雜性**: 內部的複雜操作對使用者透明
- ✅ **職責分離**: 高層邏輯和具體實作分離
- ✅ **易於使用**: 降低學習和使用成本

---

## 🔄 組合模式使用

### Observer Pattern - 觀察者模式 (隱式實作)

**應用場景**: 錯誤處理和進度追蹤
**實作方式**: 通過回調函數和日誌系統

```python
class ScraperObserver:
    """爬蟲觀察者接口"""

    def on_login_success(self, account): pass
    def on_login_failed(self, account, error): pass
    def on_data_extracted(self, account, count): pass
    def on_operation_complete(self, account, result): pass

class LoggingObserver(ScraperObserver):
    """日誌觀察者實作"""

    def on_login_success(self, account):
        safe_print(f"✅ {account['username']} 登入成功")

    def on_data_extracted(self, account, count):
        safe_print(f"📊 {account['username']} 提取 {count} 筆資料")

# BaseScraper 中的觀察者支援
class BaseScraper:
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self, event, **kwargs):
        for observer in self.observers:
            getattr(observer, event)(**kwargs)
```

---

## 📊 設計模式效益分析

### 程式碼品質提升

| 模式 | 可維護性 | 可擴展性 | 可重用性 | 可測試性 |
|------|----------|----------|----------|----------|
| Template Method | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Strategy | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Factory Method | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| Adapter | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| Facade | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ |

### 複雜度管理
- **降低耦合**: 模組間依賴關係清晰且最小化
- **提高內聚**: 相關功能集中在同一模組
- **責任分離**: 每個類別都有明確的職責
- **擴展便利**: 新功能可以無縫整合

### 開發效率提升
- **程式碼重用**: 通用邏輯實作一次，多處使用
- **模式熟悉**: 經典模式降低學習成本
- **標準化**: 統一的開發方式和規範
- **錯誤減少**: 經過驗證的設計模式減少 bug

---

## 🎯 設計模式最佳實踐

### 模式選擇原則
1. **問題導向**: 根據實際問題選擇合適模式
2. **簡單優先**: 不要為了使用模式而使用模式
3. **漸進演化**: 隨著需求變化逐步引入模式
4. **團隊能力**: 考慮團隊對模式的熟悉程度

### 實作建議
1. **文檔先行**: 清楚記錄模式的使用意圖
2. **介面設計**: 優先設計清晰的抽象介面
3. **單元測試**: 為模式的關鍵部分編寫測試
4. **重構勇氣**: 不合適的模式要勇於重構

### 避免過度設計
- ❌ 不要在簡單場景使用複雜模式
- ❌ 不要為了展示技術而強行使用模式
- ❌ 不要忽視模式的使用成本
- ✅ 平衡模式收益與複雜度

SeleniumPelican 的設計模式應用展現了成熟的軟體工程實踐，為專案的長期演進提供了堅實的架構基礎。