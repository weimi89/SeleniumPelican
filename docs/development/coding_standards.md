# 程式碼規範

## 概述

SeleniumPelican 專案遵循 Python 社群的最佳實踐，並結合專案特性制定了一套完整的程式碼規範。本規範旨在確保程式碼品質、可讀性和維護性。

## 📋 基本原則

### 核心理念
- **可讀性勝過技巧性**: 程式碼是寫給人看的
- **一致性勝過個人偏好**: 團隊統一勝過個人習慣
- **簡單性勝過複雜性**: 簡單解決方案優先
- **實用性勝過完美性**: 實用的好程式碼勝過完美的壞程式碼

### 設計原則
- **DRY** (Don't Repeat Yourself): 避免程式碼重複
- **KISS** (Keep It Simple, Stupid): 保持簡單
- **YAGNI** (You Aren't Gonna Need It): 不要過度設計
- **SRP** (Single Responsibility Principle): 單一責任原則

---

## 🐍 Python 程式碼規範

### PEP 8 遵循

嚴格遵循 [PEP 8](https://peps.python.org/pep-0008/) 規範，主要包括：

#### 縮排和空格
```python
# ✅ 正確：使用 4 個空格縮排
def login(self, username, password):
    if self.validate_credentials(username, password):
        return self.perform_login()
    return False

# ❌ 錯誤：使用 Tab 或 2 個空格
def login(self, username, password):
  if self.validate_credentials(username, password):  # 2個空格
      return self.perform_login()
  return False
```

#### 行長度限制
```python
# ✅ 正確：單行不超過 88 字符 (Black 標準)
def extract_payment_records(self, start_date, end_date,
                          filter_criteria=None):
    """提取代收貨款記錄"""
    return self.query_database(
        start_date=start_date,
        end_date=end_date,
        criteria=filter_criteria
    )

# ❌ 錯誤：單行過長
def extract_payment_records(self, start_date, end_date, filter_criteria=None, include_details=True, export_format='xlsx'):
```

#### 空行規則
```python
# ✅ 正確：適當的空行分隔
class PaymentScraper(BaseScraper):
    """代收貨款爬蟲類別"""

    def __init__(self):
        super().__init__()
        self.payment_records = []

    def get_query_params(self):
        """取得查詢參數"""
        return {
            'start_date': self.start_date,
            'end_date': self.end_date
        }

    def process_results(self):
        """處理查詢結果"""
        return self.filter_payment_records()


# 另一個類別前留兩個空行
class FreightScraper(BaseScraper):
    """運費查詢爬蟲類別"""
    pass
```

---

## 🏗️ 架構和設計規範

### 類別設計

#### 命名規範
```python
# ✅ 正確：類別使用 PascalCase
class MultiAccountManager:
    pass

class WebDriverFactory:
    pass

# ❌ 錯誤：不當的命名
class multi_account_manager:  # 應該用 PascalCase
    pass

class WebDriver_Factory:      # 不要使用底線
    pass
```

#### 方法和屬性命名
```python
class BaseScraper:
    # ✅ 正確：方法使用 snake_case
    def setup_browser(self):
        pass

    def navigate_to_query(self):
        pass

    # ✅ 正確：私有方法使用單底線前綴
    def _detect_captcha(self):
        pass

    def _wait_for_element(self):
        pass

    # ✅ 正確：常數使用大寫
    DEFAULT_TIMEOUT = 30
    MAX_RETRY_COUNT = 3

    # ❌ 錯誤：不當命名
    def setupBrowser(self):     # 應該用 snake_case
        pass

    def NavigateToQuery(self):  # 應該用 snake_case
        pass
```

### 檔案和模組組織

#### 檔案命名
```
# ✅ 正確：使用 snake_case
src/core/base_scraper.py
src/core/multi_account_manager.py
src/utils/windows_encoding_utils.py

# ❌ 錯誤：不當命名
src/core/BaseScraper.py          # 檔案名不用 PascalCase
src/core/multi-account-manager.py  # 不要用連字號
src/utils/WindowsEncodingUtils.py  # 檔案名不用 PascalCase
```

#### 模組導入順序
```python
# ✅ 正確：導入順序
# 1. 標準庫
import json
import platform
import time
from abc import ABC, abstractmethod
from pathlib import Path

# 2. 第三方庫
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from bs4 import BeautifulSoup

# 3. 本地模組
from src.core.browser_utils import setup_chrome_driver
from src.utils.windows_encoding_utils import safe_print
```

---

## 📝 文檔和註解規範

### Docstring 規範

採用 Google 風格的 docstring：

```python
class BaseScraper:
    """網頁爬蟲的抽象基類。

    這個類別定義了所有爬蟲的通用行為和介面，子類別需要實作
    特定的查詢邏輯和結果處理方法。

    Attributes:
        driver: Selenium WebDriver 實例
        config: 配置字典
        logger: 日誌記錄器
    """

    def __init__(self, config=None):
        """初始化爬蟲實例。

        Args:
            config (dict, optional): 爬蟲配置字典。預設為 None。
        """
        self.config = config or {}
        self.driver = None
        self.logger = self._setup_logger()

    def execute(self, account_info):
        """執行爬蟲主流程。

        Args:
            account_info (dict): 包含帳號資訊的字典，必須包含
                username 和 password 鍵。

        Returns:
            list: 爬取結果列表，每個元素為字典格式。

        Raises:
            WebDriverException: 當瀏覽器操作失敗時。
            ValueError: 當帳號資訊格式不正確時。

        Example:
            >>> scraper = PaymentScraper()
            >>> results = scraper.execute({
            ...     'username': 'test_user',
            ...     'password': 'test_pass'
            ... })
            >>> print(len(results))
            5
        """
        pass
```

### 註解規範

```python
# ✅ 正確：有意義的註解
def detect_captcha(self):
    """自動偵測頁面上的驗證碼"""
    # 嘗試5種不同的驗證碼偵測方法
    detection_methods = [
        self._detect_by_id,
        self._detect_by_class,
        self._detect_by_xpath,
        self._detect_by_image_analysis,
        self._detect_by_text_pattern
    ]

    for method in detection_methods:
        try:
            captcha = method()
            if captcha:  # 找到驗證碼就返回
                return captcha
        except Exception as e:
            # 記錄失敗但繼續嘗試下一種方法
            self.logger.debug(f"驗證碼偵測方法失敗: {e}")

    return None  # 所有方法都失敗

# ❌ 錯誤：無意義的註解
def detect_captcha(self):
    # 偵測驗證碼
    methods = [...]  # 建立方法列表
    for method in methods:  # 迴圈方法
        captcha = method()  # 呼叫方法
        if captcha:  # 如果有驗證碼
            return captcha  # 返回驗證碼
    return None  # 返回空值
```

---

## ⚠️ 錯誤處理規範

### 異常處理策略

```python
# ✅ 正確：分層的錯誤處理
class BaseScraper:
    def login(self, username, password):
        """登入方法，實作重試機制"""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                return self._perform_login(username, password)
            except WebDriverException as e:
                if attempt == max_retries - 1:  # 最後一次嘗試
                    self.logger.error(f"登入失敗，已嘗試 {max_retries} 次: {e}")
                    raise
                else:
                    self.logger.warning(f"登入嘗試 {attempt + 1} 失敗，準備重試: {e}")
                    time.sleep(2)  # 等待後重試
            except ValueError as e:
                # 配置錯誤不需要重試
                self.logger.error(f"登入參數錯誤: {e}")
                raise

    def _perform_login(self, username, password):
        """實際執行登入操作"""
        if not username or not password:
            raise ValueError("使用者名稱和密碼不能為空")

        try:
            # 尋找登入表單
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")

            # 填入資料
            username_field.send_keys(username)
            password_field.send_keys(password)

            # 處理驗證碼
            if self._handle_captcha():
                login_button = self.driver.find_element(By.ID, "login")
                login_button.click()
                return self._verify_login_success()
            else:
                raise WebDriverException("無法處理驗證碼")

        except Exception as e:
            # 包裝低層異常
            raise WebDriverException(f"登入操作失敗: {e}") from e
```

### 自定義異常

```python
# 定義專案特定的異常
class ScraperError(Exception):
    """爬蟲基礎異常類別"""
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

# 使用自定義異常
class PaymentScraper(BaseScraper):
    def process_results(self):
        try:
            records = self._extract_payment_records()
            if not records:
                raise DataExtractionError("未找到符合條件的付款記錄")
            return records
        except Exception as e:
            raise DataExtractionError(f"資料處理失敗: {e}") from e
```

---

## 🧪 測試程式碼規範

### 測試檔案組織

```
tests/
├── __init__.py
├── unit/                    # 單元測試
│   ├── test_base_scraper.py
│   ├── test_payment_scraper.py
│   └── test_utils.py
├── integration/             # 整合測試
│   ├── test_login_flow.py
│   └── test_data_extraction.py
└── fixtures/                # 測試資料
    ├── sample_accounts.json
    └── mock_responses.html
```

### 測試程式碼範例

```python
# tests/unit/test_base_scraper.py
import pytest
from unittest.mock import Mock, patch

from src.core.base_scraper import BaseScraper
from src.core.exceptions import LoginError


class TestBaseScraper:
    """BaseScraper 類別的單元測試"""

    @pytest.fixture
    def scraper(self):
        """測試用的爬蟲實例"""
        return BaseScraper()

    @pytest.fixture
    def mock_driver(self):
        """模擬的 WebDriver"""
        driver = Mock()
        driver.find_element.return_value = Mock()
        return driver

    def test_setup_browser_success(self, scraper):
        """測試瀏覽器設置成功的情況"""
        with patch('src.core.browser_utils.setup_chrome_driver') as mock_setup:
            mock_driver = Mock()
            mock_setup.return_value = mock_driver

            scraper.setup_browser()

            assert scraper.driver == mock_driver
            mock_setup.assert_called_once()

    def test_login_with_invalid_credentials(self, scraper, mock_driver):
        """測試無效憑證登入"""
        scraper.driver = mock_driver

        # 測試空使用者名稱
        with pytest.raises(LoginError, match="使用者名稱不能為空"):
            scraper.login("", "password")

        # 測試空密碼
        with pytest.raises(LoginError, match="密碼不能為空"):
            scraper.login("username", "")

    @pytest.mark.parametrize("username,password,expected", [
        ("valid_user", "valid_pass", True),
        ("test_user", "test_pass", True),
    ])
    def test_login_with_valid_credentials(self, scraper, mock_driver,
                                        username, password, expected):
        """測試有效憑證登入"""
        scraper.driver = mock_driver

        with patch.object(scraper, '_perform_login') as mock_login:
            mock_login.return_value = expected

            result = scraper.login(username, password)

            assert result == expected
            mock_login.assert_called_with(username, password)
```

---

## 📊 效能和品質規範

### 程式碼複雜度控制

```python
# ✅ 正確：函數保持簡潔，單一責任
def extract_payment_data(self, html_content):
    """從 HTML 內容提取付款資料"""
    soup = BeautifulSoup(html_content, 'html.parser')

    # 分步驟處理，每個函數責任單一
    rows = self._find_payment_rows(soup)
    records = self._parse_payment_records(rows)
    filtered_records = self._filter_valid_records(records)

    return filtered_records

def _find_payment_rows(self, soup):
    """尋找包含付款資料的表格行"""
    return soup.find_all('tr', class_='payment-row')

def _parse_payment_records(self, rows):
    """解析付款記錄"""
    return [self._parse_single_record(row) for row in rows]

def _filter_valid_records(self, records):
    """過濾有效的記錄"""
    return [r for r in records if self._is_valid_record(r)]

# ❌ 錯誤：函數過於複雜，責任過多
def extract_payment_data(self, html_content):
    """不好的範例：函數過於複雜"""
    soup = BeautifulSoup(html_content, 'html.parser')
    records = []

    # 太多巢狀邏輯，難以測試和維護
    for table in soup.find_all('table'):
        for row in table.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 5:
                record = {}
                if cells[0].text.strip():
                    record['id'] = cells[0].text.strip()
                    if cells[1].text and '付款' in cells[1].text:
                        record['type'] = cells[1].text.strip()
                        if cells[2].text:
                            # ... 更多巢狀邏輯
                            records.append(record)
    return records
```

### 資源管理

```python
# ✅ 正確：適當的資源管理
class BaseScraper:
    def __enter__(self):
        """上下文管理器進入"""
        self.setup_browser()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出，確保資源清理"""
        self.cleanup()

    def cleanup(self):
        """清理資源"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"清理瀏覽器時發生錯誤: {e}")
            finally:
                self.driver = None

# 使用上下文管理器
def run_scraper():
    with PaymentScraper() as scraper:
        results = scraper.execute(account_info)
        return results
    # 自動清理資源
```

---

## 🔧 工具整合

### Black 程式碼格式化

`.pyproject.toml` 配置：
```toml
[tool.black]
line-length = 88
target-version = ['py38', 'py39', 'py310', 'py311']
include = '\.pyi?$'
exclude = '''
/(
    \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''
```

### Flake8 程式碼檢查

`.flake8` 配置：
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503, E501
exclude =
    .git,
    __pycache__,
    .venv,
    build,
    dist
max-complexity = 10
```

### Pre-commit 鉤子

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

---

## ✅ 程式碼審查清單

### 提交前檢查

- [ ] 程式碼已通過 Black 格式化
- [ ] 無 Flake8 警告和錯誤
- [ ] 所有公開方法都有 docstring
- [ ] 異常處理得當，有適當的錯誤訊息
- [ ] 無硬編碼的配置和密碼
- [ ] 測試覆蓋率達到要求（建議 >80%）
- [ ] 無 TODO 註解或已建立對應的 Issue
- [ ] 日誌記錄適當且有意義

### 審查重點

- **可讀性**: 程式碼是否易於理解？
- **維護性**: 修改是否容易？
- **測試性**: 是否容易編寫測試？
- **效能**: 是否有明顯的效能問題？
- **安全性**: 是否有安全隱患？
- **一致性**: 是否遵循專案規範？

---

## 📈 持續改進

### 程式碼品質度量

定期檢視以下指標：
- **測試覆蓋率**: 目標 >80%
- **循環複雜度**: 建議 <10
- **程式碼重複率**: 建議 <3%
- **技術債務**: 定期清理

### 規範更新

程式碼規範會隨著專案發展和 Python 生態演進而更新：
- 每季度審視規範合理性
- 關注 Python 新版本的最佳實踐
- 採納團隊回饋和建議
- 更新工具配置和檢查規則

遵循這些規範將確保 SeleniumPelican 專案程式碼的高品質和長期維護性。