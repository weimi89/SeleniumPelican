# SeleniumPelican 程式碼風格與慣例

## 命名慣例

### 檔案命名
- **Python 模組**: snake_case (例如: `base_scraper.py`, `multi_account_manager.py`)
- **執行腳本**: snake_case 前綴 + 平台副檔名 (例如: `run_payment.sh`, `run_payment.ps1`)
- **設定檔案**: snake_case 或 kebab-case (例如: `accounts.json`, `pyproject.toml`)

### 類別命名
- **PascalCase**: `BaseScraper`, `PaymentScraper`, `MultiAccountManager`
- **繼承命名模式**: 具體實作以功能命名 + "Scraper" 後綴

### 方法與函數命名
- **snake_case**: `init_chrome_browser()`, `run_full_process()`, `safe_print()`
- **私有方法**: 前綴底線 `_fallback_download_excel()`
- **特殊方法**: 遵循 Python 慣例 `__init__()`

### 變數命名
- **snake_case**: `start_date`, `end_date`, `chrome_options`
- **常數**: UPPER_SNAKE_CASE (雖然此專案較少使用)

## 程式碼組織

### 目錄結構原則
```
src/
├── core/          # 核心功能模組
├── scrapers/      # 具體實作
└── utils/         # 工具函數
```

### 模組分離原則
1. **core**: 共用基礎功能和框架
2. **scrapers**: 特定業務邏輯實作
3. **utils**: 跨平台相容性和工具函數

### 導入順序
1. 標準函式庫導入
2. 第三方套件導入
3. 專案內部模組導入

## 文檔慣例

### 檔案頭部
```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
模組說明文字
包含功能描述
"""
```

### 類別文檔
```python
class BaseScraper:
    """基礎抓取器類別"""
```

### 方法文檔
使用簡潔的 docstring，重點說明參數和回傳值。

## 錯誤處理慣例

### Exception 處理
- 使用具體的 Exception 類型而非裸露的 `except:`
- 提供有意義的錯誤訊息
- 使用 `safe_print()` 進行錯誤輸出

### 日誌記錄
- 使用 `safe_print()` 統一輸出介面
- 錯誤訊息包含 emoji 或文字標籤提高可讀性
- 結構化錯誤訊息便於偵錯

## 設計模式慣例

### 抽象基類設計
- 使用 Template Method Pattern 定義處理流程
- 子類別只需實作特定方法
- 提供統一的 `run_full_process()` 入口

### 依賴注入
- 通過建構函數參數注入依賴
- 支援不同策略的動態切換

## 測試慣例
- 目前專案著重實用性，測試以手動執行為主
- 所有功能透過實際執行腳本進行驗證
- 跨平台測試確保在 Windows/macOS/Linux 都能正常運作

## 設定檔慣例

### JSON 設定
- 使用 UTF-8 編碼
- 巢狀結構清晰分層
- 提供 `.example` 範例檔案

### 環境變數
- 使用 `.env` 檔案管理環境特定設定
- 敏感資訊 (如密碼) 不提交至版控

## 跨平台考量

### 路徑處理
- 使用 `pathlib.Path` 而非字串拼接
- 避免硬編碼路徑分隔符

### 字符編碼
- 統一使用 UTF-8 編碼
- Windows 特殊處理透過 `safe_print()` 函數

### 執行腳本
- 每個平台提供對應的執行腳本
- 統一的命令列介面設計