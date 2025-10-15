# Type Annotation Best Practices

本文檔提供 SeleniumPelican 專案的型別註解標準和最佳實踐指南。

## 目錄

1. [基本原則](#基本原則)
2. [函數簽名](#函數簽名)
3. [常見模式](#常見模式)
4. [第三方型別](#第三方型別)
5. [錯誤處理](#錯誤處理)
6. [測試型別提示](#測試型別提示)
7. [IDE 配置](#ide-配置)

## 基本原則

### Do's ✅

- **總是**為所有公開方法添加型別註解
- **總是**使用 `Optional[T]` 表示可能為 `None` 的值
- **總是**明確指定返回值型別（包括 `-> None`）
- **總是**為回調函數和複雜型別使用 TypeAlias
- **總是**在修改檔案後立即執行 mypy 檢查

### Don'ts ❌

- **避免**使用 `Any` 型別（除非絕對必要）
- **避免**忽略型別錯誤（使用 `# type: ignore` 時需要註釋原因）
- **避免**混用不同的日期型別表示法
- **避免**在私有方法中省略型別註解（除非非常簡單）

## 函數簽名

### 基本範例

```python
# ✅ 正確：完整的型別註解
def login(self, username: str, password: str) -> bool:
    """執行登入流程"""
    return True

# ❌ 錯誤：缺少型別註解
def login(self, username, password):
    return True
```

### 可選參數

```python
from typing import Optional

# ✅ 正確：使用 Optional 表示可選值
def download_file(
    self,
    url: str,
    filename: Optional[str] = None
) -> str:
    """下載檔案"""
    if filename is None:
        filename = "default.xlsx"
    return filename

# ❌ 錯誤：沒有標記 Optional
def download_file(self, url: str, filename: str = None) -> str:
    pass
```

### 實例變數註解

```python
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver

# ✅ 推薦：明確的實例變數型別註解
class BaseScraper:
    def __init__(
        self,
        username: str,
        password: str,
        headless: bool = False
    ) -> None:
        self.username: str = username
        self.password: str = password
        self.headless: bool = headless
        self.driver: Optional[WebDriver] = None

# ✅ 可接受：從 __init__ 推斷型別
class BaseScraper:
    def __init__(
        self,
        username: str,
        password: str,
        headless: bool = False
    ) -> None:
        self.username = username  # 型別推斷為 str
        self.password = password  # 型別推斷為 str
        self.headless = headless  # 型別推斷為 bool
        self.driver = None        # 型別推斷為 None
```

## 常見模式

### 1. WebDriver 型別

```python
from typing import Optional
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By

class BaseScraper:
    driver: Optional[WebDriver]

    def find_element(
        self,
        by: By,
        value: str,
        timeout: float = 10.0
    ) -> Optional[WebElement]:
        """查找單一網頁元素"""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except TimeoutException:
            return None

    def find_elements(
        self,
        by: By,
        value: str
    ) -> list[WebElement]:
        """查找多個網頁元素"""
        return self.driver.find_elements(by, value)
```

### 2. Date/Time 處理

```python
from datetime import date, datetime
from typing import Union, TypeAlias

# 定義型別別名
DateLike: TypeAlias = Union[str, date, datetime]

class PaymentScraper:
    def set_date_range(
        self,
        start_date: DateLike,
        end_date: DateLike
    ) -> bool:
        """設定日期範圍

        Args:
            start_date: 開始日期 (支援 str, date, datetime)
            end_date: 結束日期 (支援 str, date, datetime)

        Returns:
            bool: 設定是否成功
        """
        # 日期轉換邏輯
        start_str = self._convert_to_string(start_date)
        end_str = self._convert_to_string(end_date)
        return True

    def _convert_to_string(self, date_value: DateLike) -> str:
        """將日期轉換為字串"""
        if isinstance(date_value, str):
            return date_value
        elif isinstance(date_value, (date, datetime)):
            return date_value.strftime("%Y%m%d")
        raise ValueError(f"Unsupported date type: {type(date_value)}")
```

### 3. Callback 函數

```python
from typing import Callable, Optional, TypeAlias

# 定義回調函數型別
ProgressCallback: TypeAlias = Callable[[str], None]
ErrorCallback: TypeAlias = Callable[[Exception], None]

class MultiAccountManager:
    def run_all_accounts(
        self,
        scraper_class: type[BaseScraper],
        progress_callback: Optional[ProgressCallback] = None,
        error_callback: Optional[ErrorCallback] = None,
        start_date: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """執行所有帳號的爬蟲任務

        Args:
            scraper_class: 爬蟲類別
            progress_callback: 進度回調函數
            error_callback: 錯誤回調函數
            start_date: 開始日期

        Returns:
            list[dict]: 執行結果列表
        """
        results = []
        for account in self.accounts:
            if progress_callback:
                progress_callback(f"處理帳號: {account['username']}")
            try:
                result = self._run_single_account(scraper_class, account, start_date)
                results.append(result)
            except Exception as e:
                if error_callback:
                    error_callback(e)
        return results
```

### 4. Configuration 字典

```python
from typing import Any, TypeAlias

# 定義配置相關的型別別名
ConfigDict: TypeAlias = dict[str, Union[str, bool, int]]
AccountConfig: TypeAlias = dict[str, Any]
RecordDict: TypeAlias = dict[str, str]

class MultiAccountManager:
    config: ConfigDict
    accounts: list[AccountConfig]

    def __init__(self, config_file: str = "accounts.json") -> None:
        self.config_file: str = config_file
        self.config: ConfigDict = {}
        self.accounts: list[AccountConfig] = []

    def get_enabled_accounts(self) -> list[AccountConfig]:
        """取得所有啟用的帳號"""
        return [acc for acc in self.accounts if acc.get("enabled", True)]
```

## 第三方型別

### Selenium Types

```python
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    WebDriverException
)

def wait_for_element(
    driver: WebDriver,
    by: By,
    value: str,
    timeout: float = 10.0
) -> Optional[WebElement]:
    """等待元素出現"""
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException:
        return None
```

### BeautifulSoup Types

```python
from bs4 import BeautifulSoup, Tag
from typing import Optional

def parse_table(html: str) -> list[dict[str, str]]:
    """解析 HTML 表格"""
    soup = BeautifulSoup(html, 'html.parser')
    table: Optional[Tag] = soup.find('table')

    if table is None:
        return []

    rows: list[dict[str, str]] = []
    for row in table.find_all('tr'):
        cells = row.find_all('td')
        row_data = {f"col_{i}": cell.get_text() for i, cell in enumerate(cells)}
        rows.append(row_data)

    return rows
```

### openpyxl Types

```python
from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet

def create_excel(data: list[dict[str, str]], filename: str) -> None:
    """創建 Excel 檔案"""
    wb: Workbook = Workbook()
    ws: Worksheet = wb.active

    if data:
        # 寫入標題
        headers = list(data[0].keys())
        ws.append(headers)

        # 寫入數據
        for row in data:
            ws.append(list(row.values()))

    wb.save(filename)
```

## 錯誤處理

### 異常型別註解

```python
from typing import Optional
from selenium.common.exceptions import WebDriverException

class ScraperError(Exception):
    """爬蟲基礎異常"""
    pass

class LoginError(ScraperError):
    """登入失敗異常"""
    pass

def safe_login(username: str, password: str) -> bool:
    """安全的登入方法，包含錯誤處理"""
    try:
        return perform_login(username, password)
    except LoginError as e:
        logger.error(f"登入失敗: {e}")
        return False
    except WebDriverException as e:
        logger.error(f"瀏覽器錯誤: {e}")
        raise ScraperError(f"無法執行登入: {e}") from e
```

### Result Type Pattern

```python
from typing import Generic, TypeVar, Union
from dataclasses import dataclass

T = TypeVar('T')
E = TypeVar('E', bound=Exception)

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err(Generic[E]):
    error: E

Result = Union[Ok[T], Err[E]]

def safe_download(url: str) -> Result[str, Exception]:
    """安全的下載函數，返回 Result 型別"""
    try:
        filename = download_file(url)
        return Ok(filename)
    except Exception as e:
        return Err(e)

# 使用範例
result = safe_download("https://example.com/file.xlsx")
if isinstance(result, Ok):
    print(f"下載成功: {result.value}")
else:
    print(f"下載失敗: {result.error}")
```

## 測試型別提示

### 使用 reveal_type() 除錯

```python
from typing import reveal_type  # Python 3.11+
# 或者 from typing_extensions import reveal_type  # Python 3.8-3.10

def example() -> None:
    username = "test@example.com"
    reveal_type(username)  # mypy 會顯示: Revealed type is "str"

    driver = init_chrome_driver()
    reveal_type(driver)  # mypy 會顯示: Revealed type is "WebDriver"
```

### 型別安全的測試

```python
import pytest
from typing import cast

def test_scraper_login() -> None:
    """測試登入功能"""
    scraper = PaymentScraper("user", "pass")

    # 確保 driver 已初始化
    assert scraper.driver is not None
    driver = cast(WebDriver, scraper.driver)  # 型別縮窄

    result = scraper.login()
    assert result is True
```

## IDE 配置

### VSCode 設定

專案已提供完整的 `.vscode/settings.json` 配置檔案。

#### 必要的 VSCode Extension

安裝以下擴充套件以獲得完整的型別檢查支援：

1. **Python** (ms-python.python) - 基礎 Python 支援
2. **Pylance** (ms-python.vscode-pylance) - 語言伺服器，提供型別檢查
3. **Mypy Type Checker** (ms-python.mypy-type-checker) - Mypy 整合
4. **Black Formatter** (ms-python.black-formatter) - 程式碼格式化
5. **isort** (ms-python.isort) - Import 排序

#### 配置說明

專案的 `.vscode/settings.json` 包含以下關鍵配置：

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.languageServer": "Pylance",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.diagnosticMode": "workspace",
  "mypy.configFile": "${workspaceFolder}/pyproject.toml",
  "mypy.runUsingActiveInterpreter": true,
  "mypy.enabled": true,
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "ms-python.black-formatter"
  }
}
```

**關鍵設定解釋**：
- `python.analysis.typeCheckingMode: "basic"`: Pylance 基本型別檢查模式
- `mypy.enabled: true`: 啟用 Mypy 即時檢查
- `mypy.configFile`: 使用專案的 pyproject.toml 配置
- `editor.formatOnSave`: 儲存時自動格式化
- 終端機環境變數自動設定 PYTHONPATH

#### 使用方式

1. 開啟專案後，VSCode 會自動套用配置
2. 型別錯誤會以紅色波浪線標示
3. 滑鼠移到錯誤處可看到詳細說明
4. 存檔時會自動執行 Black 格式化
5. Commit 時會觸發 pre-commit hooks

#### 疑難排解

**問題：型別錯誤沒有顯示**
- 確認已安裝 Pylance 和 Mypy Type Checker 擴充套件
- 檢查 Python 解譯器是否正確指向 `.venv/bin/python`
- 重新載入 VSCode 視窗 (Cmd/Ctrl + Shift + P → "Reload Window")

**問題：Mypy 報告與命令列不一致**
- 確認 `mypy.configFile` 設定正確
- 使用命令列執行 `mypy src/` 確認配置檔案有效

### PyCharm 設定

#### 啟用 Mypy 外部工具

1. **開啟設定**：
   - macOS: PyCharm → Preferences
   - Windows/Linux: File → Settings

2. **配置 Type Checker**：
   - 導航到：Tools → Python Integrated Tools
   - Type checker: 選擇 "Mypy"
   - Mypy path: 設定為 `.venv/bin/mypy` (或虛擬環境中的 mypy 路徑)
   - Arguments: `--config-file=pyproject.toml`

3. **配置外部工具** (選用，用於快速執行)：
   - Tools → External Tools → Add
   - Name: `Run Mypy`
   - Program: `$ProjectFileDir$/.venv/bin/mypy`
   - Arguments: `$ProjectFileDir$/src`
   - Working directory: `$ProjectFileDir$`

4. **啟用即時型別檢查**：
   - Editor → Inspections
   - 勾選 "Python → Type checker issues"
   - Severity: Error

#### 快捷鍵設定

1. Preferences → Keymap
2. 搜尋 "External Tools → Run Mypy"
3. 設定快捷鍵 (建議: Cmd+Shift+M / Ctrl+Shift+M)

#### PyCharm 型別檢查級別

PyCharm 內建型別檢查（不需要 Mypy）：
- 設定：Editor → Inspections → Python → Type checker
- 級別選項：
  - `None`: 不檢查
  - `Warning`: 顯示警告
  - `Error`: 顯示錯誤

**建議**：同時使用 PyCharm 內建檢查和 Mypy
- PyCharm 檢查：即時反饋
- Mypy 檢查：與 CI/CD 一致

### Emacs 設定

使用 `flycheck` 和 `lsp-mode` (適用於進階使用者):

```elisp
(use-package lsp-mode
  :hook ((python-mode . lsp))
  :config
  (setq lsp-pyright-type-checking-mode "basic"))

(use-package flycheck
  :config
  (setq flycheck-python-mypy-config "pyproject.toml"))
```

### Vim/Neovim 設定

使用 ALE (Asynchronous Lint Engine):

```vim
" 在 .vimrc 或 init.vim 中
let g:ale_linters = {
\   'python': ['mypy', 'flake8'],
\}
let g:ale_python_mypy_options = '--config-file pyproject.toml'
```

使用 coc.nvim 與 Pyright:

```json
{
  "python.linting.mypyEnabled": true,
  "python.linting.mypyArgs": ["--config-file=pyproject.toml"]
}
```

## Code Review Checklist

在 Code Review 時，檢查以下項目：

- [ ] 所有新增的公開方法都有完整型別註解
- [ ] 使用了適當的型別別名（DateLike, ConfigDict 等）
- [ ] `Optional` 型別正確標記了可能為 None 的值
- [ ] 回調函數使用了 TypeAlias 定義
- [ ] 沒有不必要的 `# type: ignore` 註釋
- [ ] mypy 檢查通過且無警告
- [ ] 複雜型別有適當的文檔字串說明

## 快速參考

### 常用型別導入

```python
from typing import (
    Any,
    Callable,
    Dict,  # Python 3.8 相容
    List,  # Python 3.8 相容
    Optional,
    TypeAlias,
    Union,
    cast,
)
from datetime import date, datetime
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
```

### 專案型別別名

在 `src/core/type_aliases.py` 中定義：

```python
from typing import TypeAlias, Callable, Union
from datetime import date, datetime

# 日期相關
DateLike: TypeAlias = Union[str, date, datetime]

# 配置相關
ConfigDict: TypeAlias = dict[str, Union[str, bool, int]]
AccountConfig: TypeAlias = dict[str, Any]

# 回調函數
ProgressCallback: TypeAlias = Callable[[str], None]
ErrorCallback: TypeAlias = Callable[[Exception], None]

# 數據結構
RecordDict: TypeAlias = dict[str, str]
ResultList: TypeAlias = list[dict[str, Any]]
```

## 資源連結

- [PEP 484 - Type Hints](https://peps.python.org/pep-0484/)
- [PEP 526 - Syntax for Variable Annotations](https://peps.python.org/pep-0526/)
- [mypy Documentation](https://mypy.readthedocs.io/)
- [typing Module Documentation](https://docs.python.org/3/library/typing.html)
- [Python Type Checking Guide](https://realpython.com/python-type-checking/)

---

*本文檔持續更新中。如有任何問題或建議，請提出 Issue 或 Pull Request。*
