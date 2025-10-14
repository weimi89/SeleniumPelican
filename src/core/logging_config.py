"""
結構化日誌配置模組
提供統一的日誌記錄機制，替換散佈的 print 語句
"""

import json
import logging
import logging.handlers
import sys
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional, Union

# from ..utils.windows_encoding_utils import safe_print  # Removed to prevent circular import
from .constants import LoggingConfig


class LogLevel(Enum):
    """日誌級別枚舉"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class StructuredFormatter(logging.Formatter):
    """結構化日誌格式器"""

    def format(self, record: logging.LogRecord) -> str:
        """格式化日誌記錄為 JSON 格式"""
        log_data = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # 添加額外的上下文資訊
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)

        # 如果有異常資訊，添加到日誌中
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_data, ensure_ascii=False, indent=2)


class ConsoleFormatter(logging.Formatter):
    """控制台友善的日誌格式器"""

    # 定義顏色代碼
    COLORS = {
        "DEBUG": "\033[36m",  # 青色
        "INFO": "\033[32m",  # 綠色
        "WARNING": "\033[33m",  # 黃色
        "ERROR": "\033[31m",  # 紅色
        "CRITICAL": "\033[35m",  # 紫色
        "RESET": "\033[0m",  # 重置
    }

    # 定義 emoji 映射
    EMOJIS = {"DEBUG": "🔍", "INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌", "CRITICAL": "🚨"}

    def format(self, record: logging.LogRecord) -> str:
        """格式化控制台日誌（簡潔版本）"""
        level = record.levelname
        message_text = record.getMessage()

        # 只顯示核心消息，移除冗餘的格式化資訊
        # 對於錯誤和警告，保留顏色提示（但避免重複添加emoji）
        if level in ["ERROR", "CRITICAL"]:
            color = self.COLORS.get(level, "")
            reset = self.COLORS["RESET"]
            # 檢查訊息是否已包含錯誤 emoji
            if "❌" not in message_text and "🚨" not in message_text:
                message = f"{color}❌ {message_text}{reset}"
            else:
                message = f"{color}{message_text}{reset}"
        elif level == "WARNING":
            color = self.COLORS.get(level, "")
            reset = self.COLORS["RESET"]
            # 檢查訊息是否已包含警告 emoji
            if "⚠️" not in message_text:
                message = f"{color}⚠️ {message_text}{reset}"
            else:
                message = f"{color}{message_text}{reset}"
        else:
            # INFO 和 DEBUG 級別使用純文字輸出
            message = message_text

        # 只對異常添加詳細資訊
        if record.exc_info:
            message += f"\n{self.formatException(record.exc_info)}"

        return message


class ScrapingLogger:
    """爬蟲專用日誌記錄器"""

    def __init__(self, name: str = "selenium_pelican", log_dir: Optional[Path] = None):
        self.name = name
        self.log_dir = log_dir or Path("logs")
        self.log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LoggingConfig.LOG_LEVEL))

        # 避免重複添加處理器
        if not self.logger.handlers:
            self._setup_handlers()

    def _setup_handlers(self):
        """設置日誌處理器"""

        # 控制台處理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = ConsoleFormatter()
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

        # 檔案處理器（結構化 JSON）
        log_file = self.log_dir / f"{self.name}.log"
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=LoggingConfig.LOG_FILE_MAX_SIZE,
            backupCount=LoggingConfig.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.DEBUG)
        structured_formatter = StructuredFormatter()
        file_handler.setFormatter(structured_formatter)
        self.logger.addHandler(file_handler)

        # 錯誤檔案處理器
        error_log_file = self.log_dir / f"{self.name}_errors.log"
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=LoggingConfig.LOG_FILE_MAX_SIZE,
            backupCount=LoggingConfig.LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(structured_formatter)
        self.logger.addHandler(error_handler)

    def debug(self, message: str, **kwargs):
        """記錄 DEBUG 級別日誌"""
        self.logger.debug(message, extra={"extra_data": kwargs})

    def info(self, message: str, **kwargs):
        """記錄 INFO 級別日誌"""
        self.logger.info(message, extra={"extra_data": kwargs})

    def warning(self, message: str, **kwargs):
        """記錄 WARNING 級別日誌"""
        self.logger.warning(message, extra={"extra_data": kwargs})

    def error(self, message: str, exc_info: bool = False, **kwargs):
        """記錄 ERROR 級別日誌"""
        self.logger.error(message, exc_info=exc_info, extra={"extra_data": kwargs})

    def critical(self, message: str, exc_info: bool = False, **kwargs):
        """記錄 CRITICAL 級別日誌"""
        self.logger.critical(message, exc_info=exc_info, extra={"extra_data": kwargs})

    def log_operation_start(self, operation: str, **context):
        """記錄操作開始"""
        self.info(f"開始 {operation}", operation=operation, **context)

    def log_operation_success(self, operation: str, duration: Optional[float] = None, **context):
        """記錄操作成功"""
        extra_data = {"operation": operation, **context}
        if duration is not None:
            extra_data["duration_seconds"] = duration
        self.info(f"✅ {operation} 成功完成", **extra_data)

    def log_operation_failure(self, operation: str, error: Union[str, Exception], **context):
        """記錄操作失敗"""
        error_msg = str(error)
        self.error(
            f"❌ {operation} 失敗: {error_msg}", operation=operation, error=error_msg, **context
        )

    def log_data_info(self, message: str, count: Optional[int] = None, **context):
        """記錄數據相關資訊"""
        extra_data = context.copy()
        if count is not None:
            extra_data["count"] = count
        self.info(f"📊 {message}", **extra_data)

    def log_download_info(self, filename: str, size: Optional[int] = None, **context):
        """記錄下載資訊"""
        extra_data = {"filename": filename, **context}
        if size is not None:
            extra_data["file_size_bytes"] = size
        self.info(f"📥 檔案下載: {filename}", **extra_data)

    def log_performance_metric(
        self, metric_name: str, value: Union[int, float], unit: str = "", **context
    ):
        """記錄效能指標"""
        self.info(
            f"⚡ {metric_name}: {value}{unit}",
            metric_name=metric_name,
            value=value,
            unit=unit,
            **context,
        )


class LoggingContext:
    """日誌上下文管理器"""

    def __init__(self, logger: ScrapingLogger, operation: str, **context):
        self.logger = logger
        self.operation = operation
        self.context = context
        self.start_time = None

    def __enter__(self):
        self.start_time = datetime.now()
        self.logger.log_operation_start(self.operation, **self.context)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (datetime.now() - self.start_time).total_seconds()

        if exc_type is None:
            self.logger.log_operation_success(self.operation, duration, **self.context)
        else:
            self.logger.log_operation_failure(self.operation, exc_val, **self.context)

        return False  # 不抑制異常


# 全域日誌記錄器實例
_global_logger: Optional[ScrapingLogger] = None


def get_logger(name: Optional[str] = None, log_dir: Optional[Path] = None) -> ScrapingLogger:
    """
    取得日誌記錄器實例

    Args:
        name: 日誌記錄器名稱
        log_dir: 日誌檔案目錄

    Returns:
        ScrapingLogger 實例
    """
    global _global_logger

    if _global_logger is None or (name and _global_logger.name != name):
        _global_logger = ScrapingLogger(name or "selenium_pelican", log_dir)

    return _global_logger


def log_with_safe_print(message: str, level: str = "INFO", **kwargs):
    # Transition function - safe_print is intentional for Windows compatibility
    # Transition function - removed safe_print dependency to prevent circular import
    """
    過渡期的便利函數，記錄日誌並輸出到控制台
    已移除 safe_print 依賴以避免循環導入

    Args:
        message: 訊息內容
        level: 日誌級別
        **kwargs: 額外的上下文資訊
    """
    # 直接使用 print，避免循環導入
    print(message)

    # 同時記錄到日誌
    logger = get_logger()
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message, **kwargs)


# 便利函數，用於快速日誌記錄
def log_info(message: str, **kwargs):
    """記錄 INFO 日誌"""
    get_logger().info(message, **kwargs)


def log_error(message: str, **kwargs):
    """記錄 ERROR 日誌"""
    get_logger().error(message, **kwargs)


def log_warning(message: str, **kwargs):
    """記錄 WARNING 日誌"""
    get_logger().warning(message, **kwargs)
