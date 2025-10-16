# SeleniumPelican 架構模式分析

## 設計模式

### 1. Template Method Pattern (樣板方法模式)
**實作**: `BaseScraper` 類別
- 定義抓取流程的骨架: `登入 → 導航 → 設定日期 → 搜尋記錄 → 下載資料`
- 子類別 (PaymentScraper, FreightScraper, UnpaidScraper) 實作特定步驟
- 提供 `run_full_process()` 作為統一入口點

### 2. Strategy Pattern (策略模式)
**實作**: 不同的下載策略
- PaymentScraper: 點擊下載連結策略
- FreightScraper: data-fileblob 資料提取策略
- UnpaidScraper: HTML 表格解析策略

### 3. Dependency Injection (依賴注入)
**實作**: `MultiAccountManager.run_all_accounts()`
- 接受不同的 scraper_class 參數
- 支援 PaymentScraper, FreightScraper, UnpaidScraper 等不同實作
- 執行時動態決定使用哪種抓取器

### 4. Factory Pattern (工廠模式)
**實作**: `browser_utils.init_chrome_browser()`
- 統一 WebDriver 建立介面
- 隱藏複雜的瀏覽器設定細節
- 支援不同平台和配置選項

### 5. Observer Pattern (觀察者模式)
**實作**: progress_callback 機制
- MultiAccountManager 支援進度回呼函數
- 允許外部監聽執行進度

## 架構原則

### 1. Single Responsibility Principle (單一職責原則)
- BaseScraper: 處理登入和基礎導航
- MultiAccountManager: 負責多帳號管理
- browser_utils: 專責瀏覽器初始化
- windows_encoding_utils: 處理跨平台編碼問題

### 2. Open/Closed Principle (開放封閉原則)
- 基礎抓取器開放擴展，封閉修改
- 新增抓取器只需繼承 BaseScraper 並實作特定方法

### 3. Liskov Substitution Principle (里氏替換原則)
- 所有抓取器都可以透過 MultiAccountManager 統一管理
- 相同的介面契約，不同的實作行為

### 4. Dependency Inversion Principle (依賴反轉原則)
- MultiAccountManager 依賴抽象的 scraper_class，不依賴具體實作
- 通過參數注入決定使用哪種抓取器
