# SeleniumPelican 錯誤處理與容錯機制分析

## 容錯設計哲學
採用「繼續執行」策略，個別失敗不會停止整個流程。

## 核心錯誤處理機制

### 1. 登入錯誤處理
**位置**: `BaseScraper.login()`
**策略**:
- 自動驗證碼偵測失敗時，提供20秒手動輸入時間
- 登入失敗自動重試最多3次
- Alert 彈窗自動處理和確認
- 支援多種驗證碼偵測方法 (5種不同策略)

### 2. 瀏覽器初始化容錯
**位置**: `browser_utils.init_chrome_browser()`
**多重備援策略**:
1. 優先使用環境變數指定的 ChromeDriver
2. 回退到系統預裝的 Chrome
3. 最後使用 WebDriver Manager 自動下載
4. 全部失敗時提供詳細的故障排除指南

### 3. 多帳號處理錯誤隔離
**位置**: `MultiAccountManager.run_all_accounts()`
**隔離機制**:
- 個別帳號失敗不影響其他帳號執行
- 異常捕獲並記錄到結果中
- 繼續處理後續帳號
- 最終產生完整的成功/失敗報告

### 4. 網頁操作超時處理
**實作**: WebDriverWait 與 explicit waits
- 所有網頁元素操作都有超時保護
- 等待元素出現而非盲目操作
- iframe 切換有明確的等待機制

### 5. 下載錯誤恢復
**多重下載策略**:
- 主要下載方法失敗時，自動嘗試備用方法
- UnpaidScraper 直接解析 HTML 避免下載問題
- FreightScraper 使用 data-fileblob 替代點擊下載

## 錯誤記錄與報告

### 1. 安全列印機制
**位置**: `windows_encoding_utils.safe_print()`
- 跨平台 Unicode 字符處理
- Windows 環境自動轉換為文字標籤
- 避免字符編碼導致的程式崩潰

### 2. 詳細執行報告
**功能**:
- JSON 格式的執行結果記錄
- 成功/失敗統計
- 錯誤訊息詳細記錄
- 時間戳和檔案追蹤

### 3. 環境檢查機制
**位置**: `windows_encoding_utils.check_pythonunbuffered()`
- 執行前檢查必要環境變數
- 提供平台特定的設定指導
- 防止執行環境問題

## 容錯最佳實踐

### 1. Graceful Degradation (優雅降級)
- 自動驗證碼偵測失敗時，允許手動輸入
- 主要下載方法失敗時，使用替代方法

### 2. Circuit Breaker Pattern (斷路器模式)
- 連續失敗時提供明確錯誤訊息
- 避免無限重試造成系統負擔

### 3. Fail Fast (快速失敗)
- 環境檢查不通過時立即退出
- 提供清楚的修正指引
