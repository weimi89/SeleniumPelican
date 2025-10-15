"""
型別別名定義模組

此模組提供專案中常用的型別別名，以提高程式碼可讀性和型別安全性。
所有型別別名都使用 TypeAlias 顯式標註，符合 PEP 613 標準。
"""

from datetime import date, datetime
from typing import Any, Callable, Dict, List, Optional, Union

from typing_extensions import TypeAlias

# 日期相關型別
DateLike: TypeAlias = Union[str, date, datetime]
"""日期相關型別：可以是字串、date 或 datetime 物件"""

# 配置相關型別
ConfigDict: TypeAlias = Dict[str, Union[str, bool, int, float, None]]
"""配置字典型別：鍵為字串，值可以是字串、布林值、整數、浮點數或 None"""

AccountConfig: TypeAlias = Dict[str, Any]
"""帳號配置型別：包含帳號相關的所有配置資訊"""

SettingsDict: TypeAlias = Dict[str, Any]
"""設定字典型別：包含系統設定的所有資訊"""

# 回呼函數型別
ProgressCallback: TypeAlias = Callable[[str], None]
"""進度回呼函數型別：接受字串訊息參數，無回傳值"""

ErrorCallback: TypeAlias = Callable[[Exception], None]
"""錯誤回呼函數型別：接受例外物件參數，無回傳值"""

# 記錄相關型別
RecordDict: TypeAlias = Dict[str, str]
"""記錄字典型別：鍵值都是字串的字典，用於儲存爬取的記錄資料"""

RecordList: TypeAlias = List[RecordDict]
"""記錄列表型別：RecordDict 的列表"""

# 下載相關型別
DownloadResult: TypeAlias = List[str]
"""下載結果型別：下載檔案的路徑列表"""

# 日誌相關型別
LogContext: TypeAlias = Dict[str, Any]
"""日誌上下文型別：用於結構化日誌的額外資訊"""

DiagnosticData: TypeAlias = Dict[str, Any]
"""診斷資料型別：用於除錯和診斷的資料結構"""

# 統計相關型別
StatisticsDict: TypeAlias = Dict[str, Union[int, float, str]]
"""統計字典型別：包含各種統計資訊的字典"""

# 驗證相關型別
ValidationResult: TypeAlias = Dict[str, Union[bool, str, List[str]]]
"""驗證結果型別：包含驗證狀態和訊息的字典"""
