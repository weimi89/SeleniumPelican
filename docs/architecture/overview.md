# SeleniumPelican 架構概述

## 專案願景

SeleniumPelican 是一個現代化的 WEDI 宅配通自動化工具套件，專門為企業用戶設計，提供可靠、高效的資料擷取服務。專案採用模組化架構設計，具備優秀的可擴展性和維護性。

## 核心理念

### 🎯 設計原則
- **關注點分離**: 清晰劃分核心、實作、工具三層架構
- **開放封閉原則**: 對擴展開放，對修改封閉
- **依賴反轉**: 高層模組不依賴低層模組，都依賴抽象
- **單一責任**: 每個模組都有明確定義的職責

### 🏗️ 架構模式
- **Template Method Pattern**: 定義穀蟲操作的骨架
- **Strategy Pattern**: 支援多種實作策略
- **Factory Pattern**: 統一物件創建介面
- **Dependency Injection**: 降低模組間耦合

## 系統架構

### 整體架構圖

```
SeleniumPelican/
├── src/                    # 核心原始碼
│   ├── core/               # 🏛️ 核心架構層
│   │   ├── base_scraper.py        # 抽象基礎類別
│   │   ├── multi_account_manager.py  # 多帳號管理器
│   │   ├── browser_utils.py       # 瀏覽器工具
│   │   └── config_validator.py    # 配置驗證系統
│   ├── scrapers/           # 🔧 業務實作層
│   │   ├── payment_scraper.py     # 代收貨款爬蟲
│   │   ├── freight_scraper.py     # 運費查詢爬蟲
│   │   └── unpaid_scraper.py      # 未請款明細爬蟲
│   └── utils/              # 🛠️ 工具支援層
│       └── windows_encoding_utils.py # 跨平台編碼工具
├── tests/                  # 🧪 測試框架
│   ├── unit/              # 單元測試
│   ├── integration/       # 整合測試
│   └── fixtures/          # 測試夾具
├── scripts/                # 執行腳本層
├── Windows_*.cmd           # 標準化 Windows 執行腳本
├── Linux_*.sh              # 標準化 Linux/macOS 執行腳本
├── docs/                   # 技術文檔
└── config files           # 配置檔案
```

### 分層架構詳解

#### 🏛️ 核心架構層 (`src/core/`)

**BaseScraper** - 抽象基礎類別
- 定義標準化的爬蟲操作流程
- 處理瀏覽器生命週期管理
- 提供統一的登入和導航介面
- 實作基礎的錯誤處理機制

**MultiAccountManager** - 多帳號管理器
- 實作帳號配置的讀取和管理
- 支援批次處理多個帳號
- 提供依賴注入容器功能
- 統一報告生成和輸出

**browser_utils** - 瀏覽器工具模組
- 跨平台 Chrome WebDriver 初始化
- 統一的瀏覽器配置管理
- 支援無頭模式和視窗模式切換

**config_validator** - 配置驗證系統
- JSON Schema 結構驗證
- 業務邏輯一致性檢查
- 自動配置文件修復和建議
- 密碼安全性檢測

#### 🔧 業務實作層 (`src/scrapers/`)

每個爬蟲都繼承 `BaseScraper`，實作特定的業務邏輯：

**PaymentScraper** - 代收貨款查詢
- 特化日期範圍查詢邏輯
- 實作代收貨款項目過濾
- 支援 Excel 檔案下載

**FreightScraper** - 運費查詢
- 月份範圍查詢特化
- 運費結帳資料提取
- 數據轉換和輸出

**UnpaidScraper** - 運費未請款明細
- HTML 表格直接解析
- BeautifulSoup 數據提取
- 無需檔案下載的處理方式

#### 🛠️ 工具支援層 (`src/utils/`)

**windows_encoding_utils** - 跨平台編碼支援
- Unicode 字符安全顯示
- 跨平台編碼兼容處理
- 環境變數檢查和提醒

## 關鍵特性

### 🔄 Template Method 實作

```python
class BaseScraper:
    def execute(self):          # 模板方法
        self.setup_browser()    # 通用步驟
        self.login()           # 通用步驟
        self.navigate_to_query() # 通用步驟
        self.perform_query()    # 子類實作
        self.process_results()  # 子類實作
        self.cleanup()         # 通用步驟
```

### 🎯 Strategy Pattern 應用

```python
class MultiAccountManager:
    def __init__(self, scraper_class):  # 注入策略
        self.scraper_class = scraper_class

    def process_account(self, account):
        scraper = self.scraper_class()  # 使用策略
        return scraper.execute(account)
```

### 🛡️ 容錯設計

- **多層重試機制**: 登入重試、操作重試、網路重試
- **優雅降級**: 個別失敗不影響整體流程
- **自動偵測和手動備援**: 驗證碼處理雙重保障
- **詳細日誌記錄**: 完整的操作追蹤和錯誤診斷

## 技術亮點

### 🌐 跨平台設計

- **多樣化執行腳本**: `.sh` (Unix)、`.cmd` (Windows)、`.ps1` (PowerShell)
- **路徑兼容處理**: 自動適配不同作業系統的 Chrome 路徑
- **編碼統一**: Windows 特殊字符顯示優化

### 📦 現代化工具鏈

- **uv 包管理**: 快速依賴解析和虛擬環境管理
- **pyproject.toml**: 現代 Python 專案標準配置
- **自動更新機制**: git 智慧操作和依賴同步

### 🔧 開發者友善

- **模組化測試**: 獨立的測試目錄結構
- **豐富的執行參數**: 日期範圍、無頭模式等靈活配置
- **詳盡的錯誤訊息**: 幫助快速定位和解決問題

## 演進歷程

### v1.0 - 基礎實作
- 單一檔案結構
- 基本的 Selenium 自動化
- 簡單的命令列介面

### v2.0 - 現代化重構 (目前版本)
- 模組化架構設計
- 抽象基礎類別引入
- 跨平台支援完善
- 現代工具鏈整合
- 完整測試框架建立
- 標準化執行腳本系統
- 配置驗證和自動修復
- 智能安裝和更新機制

### v3.0 - 未來規劃
- 微服務架構考慮
- REST API 介面提供
- 容器化部署支援
- 更豐富的資料處理選項

## 總結

SeleniumPelican 展現了現代 Python 專案的最佳實踐，結合了：

- **穩健的架構設計**: 模組化、可擴展、可維護
- **實用的業務價值**: 解決實際的企業自動化需求
- **優秀的工程實踐**: 跨平台、錯誤處理、測試支援
- **開發者體驗**: 友善的工具鏈和文檔支援

這個架構為未來的功能擴展和維護提供了堅實的基礎，是企業級自動化工具開發的優秀範例。