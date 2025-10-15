"""
SeleniumPelican 自定義異常類別
提供精確的錯誤處理和診斷資訊
"""

from typing import Any, Dict, List, Optional


class ScrapingError(Exception):
    """基礎爬蟲異常類別"""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - 詳細資訊: {self.details}"
        return self.message


class LoginError(ScrapingError):
    """登入相關異常"""

    def __init__(
        self,
        message: str,
        username: Optional[str] = None,
        retry_count: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        details = {"username": username, "retry_count": retry_count, **kwargs}
        super().__init__(message, details)


class CaptchaError(LoginError):
    """驗證碼相關異常"""

    def __init__(
        self, message: str, captcha_method: Optional[str] = None, **kwargs: Any
    ) -> None:
        details = {"captcha_method": captcha_method, **kwargs}
        super().__init__(message, **details)


class NavigationError(ScrapingError):
    """導航相關異常"""

    def __init__(
        self,
        message: str,
        current_url: Optional[str] = None,
        target_element: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = {
            "current_url": current_url,
            "target_element": target_element,
            **kwargs,
        }
        super().__init__(message, details)


class IframeError(NavigationError):
    """iframe 操作異常"""

    def __init__(
        self, message: str, iframe_name: Optional[str] = None, **kwargs: Any
    ) -> None:
        details = {"iframe_name": iframe_name, **kwargs}
        super().__init__(message, **details)


class DataError(ScrapingError):
    """數據處理相關異常"""

    def __init__(
        self,
        message: str,
        record_count: Optional[int] = None,
        data_type: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = {"record_count": record_count, "data_type": data_type, **kwargs}
        super().__init__(message, details)


class TableParsingError(DataError):
    """表格解析異常"""

    def __init__(
        self,
        message: str,
        table_selector: Optional[str] = None,
        row_count: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        details = {"table_selector": table_selector, "row_count": row_count, **kwargs}
        super().__init__(message, **details)


class RecordFilterError(DataError):
    """記錄過濾異常"""

    def __init__(
        self,
        message: str,
        filter_criteria: Optional[Dict[str, Any]] = None,
        matched_count: Optional[int] = None,
        **kwargs: Any,
    ) -> None:
        details = {
            "filter_criteria": filter_criteria,
            "matched_count": matched_count,
            **kwargs,
        }
        super().__init__(message, **details)


class DownloadError(ScrapingError):
    """下載相關異常"""

    def __init__(
        self,
        message: str,
        file_path: Optional[str] = None,
        download_url: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = {"file_path": file_path, "download_url": download_url, **kwargs}
        super().__init__(message, details)


class FileOperationError(DownloadError):
    """檔案操作異常"""

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        source_path: Optional[str] = None,
        target_path: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = {
            "operation": operation,
            "source_path": source_path,
            "target_path": target_path,
            **kwargs,
        }
        super().__init__(message, **details)


class ValidationError(ScrapingError):
    """驗證相關異常"""

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[str] = None,
        validation_rule: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = {
            "field_name": field_name,
            "field_value": field_value,
            "validation_rule": validation_rule,
            **kwargs,
        }
        super().__init__(message, details)


class ConfigurationError(ValidationError):
    """設定檔案異常"""

    def __init__(
        self,
        message: str,
        config_file: Optional[str] = None,
        config_section: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = {
            "config_file": config_file,
            "config_section": config_section,
            **kwargs,
        }
        super().__init__(message, **details)


class TimeoutError(ScrapingError):
    """超時異常"""

    def __init__(
        self,
        message: str,
        timeout_duration: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = {
            "timeout_duration": timeout_duration,
            "operation": operation,
            **kwargs,
        }
        super().__init__(message, details)


class WebDriverError(ScrapingError):
    """WebDriver 相關異常"""

    def __init__(
        self,
        message: str,
        driver_version: Optional[str] = None,
        browser_version: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        details = {
            "driver_version": driver_version,
            "browser_version": browser_version,
            **kwargs,
        }
        super().__init__(message, details)


class RetryExhaustedError(ScrapingError):
    """重試次數耗盡異常"""

    def __init__(
        self,
        message: str,
        max_retries: Optional[int] = None,
        last_error: Optional[Exception] = None,
        **kwargs: Any,
    ) -> None:
        details = {
            "max_retries": max_retries,
            "last_error": str(last_error) if last_error else None,
            **kwargs,
        }
        super().__init__(message, details)


# 異常映射字典，用於快速查找對應的異常類別
EXCEPTION_MAP = {
    "login": LoginError,
    "captcha": CaptchaError,
    "navigation": NavigationError,
    "iframe": IframeError,
    "data": DataError,
    "table_parsing": TableParsingError,
    "record_filter": RecordFilterError,
    "download": DownloadError,
    "file_operation": FileOperationError,
    "validation": ValidationError,
    "configuration": ConfigurationError,
    "timeout": TimeoutError,
    "webdriver": WebDriverError,
    "retry_exhausted": RetryExhaustedError,
}


def create_exception(exception_type: str, message: str, **kwargs: Any) -> ScrapingError:
    """
    工廠方法：根據異常類型建立對應的異常實例

    Args:
        exception_type: 異常類型名稱
        message: 異常訊息
        **kwargs: 其他異常參數

    Returns:
        對應的異常實例

    Raises:
        ValueError: 無效的異常類型
    """
    if exception_type not in EXCEPTION_MAP:
        available_types = ", ".join(EXCEPTION_MAP.keys())
        raise ValueError(f"無效的異常類型: {exception_type}. " f"可用類型: {available_types}")

    exception_class = EXCEPTION_MAP[exception_type]
    instance: ScrapingError = exception_class(message, **kwargs)
    return instance


class ErrorContext:
    """錯誤上下文管理器，用於收集診斷資訊"""

    def __init__(self) -> None:
        self.context: Dict[str, Any] = {}

    def add(self, key: str, value: Any) -> None:
        """添加上下文資訊"""
        self.context[key] = value

    def get_context(self) -> Dict[str, Any]:
        """取得所有上下文資訊"""
        return self.context.copy()

    def clear(self) -> None:
        """清除所有上下文資訊"""
        self.context.clear()


# 全域錯誤上下文實例
error_context = ErrorContext()


class ExceptionAnalyzer:
    """異常分析器，提供深度分析功能"""

    @staticmethod
    def analyze_selenium_exception(exception: Exception) -> Dict[str, Any]:
        """分析 Selenium 相關異常"""
        details: Dict[str, str] = {}
        exception_str = str(exception).lower()

        # 常見的 Selenium 異常模式分析
        if "no such element" in exception_str:
            details["issue"] = "element_not_found"
            details["suggestion"] = "檢查元素選擇器或等待元素出現"
        elif "timeout" in exception_str:
            details["issue"] = "timeout"
            details["suggestion"] = "增加等待時間或檢查網路連線"
        elif "stale element" in exception_str:
            details["issue"] = "stale_element"
            details["suggestion"] = "重新尋找元素"
        elif "no such frame" in exception_str:
            details["issue"] = "frame_not_found"
            details["suggestion"] = "檢查 iframe 名稱或 ID"
        elif "alert" in exception_str:
            details["issue"] = "unexpected_alert"
            details["suggestion"] = "處理彈出視窗"

        analysis: Dict[str, Any] = {"type": "selenium", "details": details}
        return analysis

    @staticmethod
    def get_recovery_suggestions(exception: Exception) -> List[str]:
        """根據異常類型提供恢復建議"""
        suggestions = []
        exception_type = type(exception).__name__

        if exception_type == "LoginError":
            suggestions.extend(
                [
                    "檢查帳號密碼是否正確",
                    "驗證網路連線狀態",
                    "確認登入頁面是否正常載入",
                    "檢查驗證碼處理邏輯",
                ]
            )
        elif exception_type == "NavigationError":
            suggestions.extend(
                [
                    "檢查目標元素是否存在",
                    "增加頁面載入等待時間",
                    "驗證元素選擇器是否正確",
                    "檢查頁面結構是否有變更",
                ]
            )
        elif exception_type == "TimeoutError":
            suggestions.extend(
                [
                    "增加超時時間設定",
                    "檢查網路連線品質",
                    "確認目標操作是否耗時較長",
                    "考慮分步驟執行複雜操作",
                ]
            )
        elif exception_type == "DataError":
            suggestions.extend(
                [
                    "檢查數據解析邏輯",
                    "驗證數據格式是否一致",
                    "確認數據來源是否穩定",
                    "檢查數據過濾條件",
                ]
            )

        return suggestions


class AdvancedScrapingError(ScrapingError):
    """增強版爬蟲異常，包含更多診斷資訊"""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        context: Optional[Dict[str, Any]] = None,
        recovery_suggestions: Optional[List[str]] = None,
        error_code: Optional[str] = None,
    ):
        super().__init__(message, details)
        self.context = context or {}
        self.recovery_suggestions = recovery_suggestions or []
        self.error_code = error_code
        self.timestamp = datetime.now()
        self.analysis = self._analyze_exception()

    def _analyze_exception(self) -> Dict[str, Any]:
        """分析異常並提供診斷資訊"""
        analyzer = ExceptionAnalyzer()

        # 基本分析
        analysis = {
            "timestamp": self.timestamp.isoformat(),
            "error_code": self.error_code,
            "severity": self._determine_severity(),
            "category": self._categorize_error(),
        }

        # 如果沒有提供恢復建議，自動生成
        if not self.recovery_suggestions:
            self.recovery_suggestions = analyzer.get_recovery_suggestions(self)

        return analysis

    def _determine_severity(self) -> str:
        """判斷異常嚴重程度"""
        message_lower = self.message.lower()

        if any(
            critical in message_lower for critical in ["critical", "fatal", "crashed"]
        ):
            return "critical"
        elif any(high in message_lower for high in ["failed", "error", "exception"]):
            return "high"
        elif any(medium in message_lower for medium in ["warning", "timeout", "retry"]):
            return "medium"
        else:
            return "low"

    def _categorize_error(self) -> str:
        """為異常分類"""
        exception_type = type(self).__name__.lower()

        if "login" in exception_type:
            return "authentication"
        elif "navigation" in exception_type or "iframe" in exception_type:
            return "navigation"
        elif "data" in exception_type or "table" in exception_type:
            return "data_processing"
        elif "download" in exception_type or "file" in exception_type:
            return "file_operations"
        elif "timeout" in exception_type:
            return "performance"
        elif "validation" in exception_type or "config" in exception_type:
            return "configuration"
        else:
            return "general"

    def get_diagnostic_info(self) -> Dict[str, Any]:
        """取得完整的診斷資訊"""
        return {
            "message": self.message,
            "details": self.details,
            "context": self.context,
            "recovery_suggestions": self.recovery_suggestions,
            "analysis": self.analysis,
            "error_hierarchy": self._get_error_hierarchy(),
        }

    def _get_error_hierarchy(self) -> List[str]:
        """取得異常類別階層"""
        hierarchy = []
        for cls in type(self).__mro__:
            if cls == Exception:
                break
            hierarchy.append(cls.__name__)
        return hierarchy

    def __str__(self) -> str:
        base_str = super().__str__()
        if self.error_code:
            base_str = f"[{self.error_code}] {base_str}"

        if self.recovery_suggestions:
            suggestions_str = "; ".join(self.recovery_suggestions[:2])  # 只顯示前兩個建議
            base_str += f" | 建議: {suggestions_str}"

        return base_str


# 導入 datetime 用於時間戳
from datetime import datetime
