"""
異常診斷管理器
提供進階的異常記錄、分析和診斷功能
"""

import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from .exceptions import ScrapingError
from .logging_config import get_logger


class DiagnosticInfo:
    """診斷資訊類別"""

    def __init__(self):
        self.timestamp = datetime.now()
        self.system_info = self._collect_system_info()
        self.environment = self._collect_environment()
        self.call_stack = self._get_call_stack()

    def _collect_system_info(self) -> Dict[str, Any]:
        """收集系統資訊"""
        return {
            "platform": sys.platform,
            "python_version": sys.version,
            "python_executable": sys.executable,
            "memory_usage": self._get_memory_usage(),
        }

    def _collect_environment(self) -> Dict[str, Any]:
        """收集環境變數和配置"""
        import os

        relevant_env_vars = [
            "PYTHONPATH", "CHROME_BINARY_PATH", "CHROMEDRIVER_PATH",
            "PYTHONUNBUFFERED", "DEBUG", "ENVIRONMENT"
        ]

        return {var: os.environ.get(var) for var in relevant_env_vars if os.environ.get(var)}

    def _get_memory_usage(self) -> Optional[Dict[str, float]]:
        """取得記憶體使用狀況"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "percent": process.memory_percent(),
            }
        except ImportError:
            return None

    def _get_call_stack(self) -> List[Dict[str, Any]]:
        """取得呼叫堆疊"""
        stack = []
        for frame_info in traceback.extract_stack()[:-1]:  # 排除當前函數
            stack.append({
                "filename": frame_info.filename,
                "line_number": frame_info.lineno,
                "function_name": frame_info.name,
                "code": frame_info.line,
            })
        return stack

    def to_dict(self) -> Dict[str, Any]:
        """轉換為字典格式"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "system_info": self.system_info,
            "environment": self.environment,
            "call_stack": self.call_stack,
        }


class ExceptionStatistics:
    """異常統計類別"""

    def __init__(self):
        self.stats = defaultdict(lambda: {
            "count": 0,
            "first_seen": None,
            "last_seen": None,
            "details": []
        })
        self.total_exceptions = 0

    def record_exception(self, exception_type: str, message: str, context: Dict[str, Any] = None):
        """記錄異常"""
        now = datetime.now()
        self.total_exceptions += 1

        stat = self.stats[exception_type]
        stat["count"] += 1

        if stat["first_seen"] is None:
            stat["first_seen"] = now
        stat["last_seen"] = now

        # 只保留最近 10 個詳細記錄以節省記憶體
        stat["details"].append({
            "timestamp": now.isoformat(),
            "message": message,
            "context": context or {}
        })
        if len(stat["details"]) > 10:
            stat["details"].pop(0)

    def get_statistics(self) -> Dict[str, Any]:
        """取得統計資訊"""
        return {
            "total_exceptions": self.total_exceptions,
            "exception_types": dict(self.stats),
            "top_exceptions": self._get_top_exceptions(),
        }

    def _get_top_exceptions(self, limit: int = 5) -> List[Dict[str, Any]]:
        """取得最常見的異常"""
        sorted_exceptions = sorted(
            self.stats.items(),
            key=lambda x: x[1]["count"],
            reverse=True
        )

        return [
            {
                "type": exc_type,
                "count": data["count"],
                "first_seen": data["first_seen"].isoformat() if data["first_seen"] else None,
                "last_seen": data["last_seen"].isoformat() if data["last_seen"] else None,
            }
            for exc_type, data in sorted_exceptions[:limit]
        ]


class DiagnosticManager:
    """診斷管理器主類別"""

    def __init__(self, log_dir: Optional[Path] = None):
        self.logger = get_logger("diagnostic_manager")
        self.log_dir = log_dir or Path("logs/diagnostics")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.statistics = ExceptionStatistics()
        self.session_id = self._generate_session_id()

    def _generate_session_id(self) -> str:
        """生成會話 ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"session_{timestamp}_{id(self) % 10000:04d}"

    def capture_exception(
        self,
        exception: Exception,
        context: Dict[str, Any] = None,
        capture_screenshot: bool = False,
        capture_page_source: bool = False,
        driver=None,
    ) -> str:
        """
        捕獲並記錄異常的詳細診斷資訊

        Args:
            exception: 異常實例
            context: 額外的上下文資訊
            capture_screenshot: 是否擷取螢幕截圖
            capture_page_source: 是否擷取頁面原始碼
            driver: WebDriver 實例

        Returns:
            診斷報告的檔案路徑
        """
        diagnostic_info = DiagnosticInfo()
        exception_id = self._generate_exception_id()

        # 建立診斷報告
        report = {
            "exception_id": exception_id,
            "session_id": self.session_id,
            "exception": {
                "type": type(exception).__name__,
                "message": str(exception),
                "traceback": traceback.format_exc(),
                "module": getattr(exception, "__module__", None),
            },
            "context": context or {},
            "diagnostic_info": diagnostic_info.to_dict(),
        }

        # 處理 ScrapingError 的特殊資訊
        if isinstance(exception, ScrapingError):
            report["exception"]["details"] = getattr(exception, "details", {})

        # 擷取螢幕截圖
        if capture_screenshot and driver:
            try:
                screenshot_path = self._capture_screenshot(driver, exception_id)
                report["screenshot_path"] = str(screenshot_path)
            except Exception as e:
                self.logger.warning(f"無法擷取螢幕截圖: {e}")

        # 擷取頁面原始碼
        if capture_page_source and driver:
            try:
                page_source_path = self._capture_page_source(driver, exception_id)
                report["page_source_path"] = str(page_source_path)
            except Exception as e:
                self.logger.warning(f"無法擷取頁面原始碼: {e}")

        # 儲存診斷報告
        report_path = self._save_diagnostic_report(report, exception_id)

        # 記錄統計
        self.statistics.record_exception(
            type(exception).__name__,
            str(exception),
            context
        )

        # 記錄到日誌
        self.logger.error(
            f"異常已捕獲並診斷",
            exception_id=exception_id,
            exception_type=type(exception).__name__,
            report_path=str(report_path),
            exc_info=True
        )

        return str(report_path)

    def _generate_exception_id(self) -> str:
        """生成異常 ID"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
        return f"exc_{timestamp}"

    def _capture_screenshot(self, driver, exception_id: str) -> Path:
        """擷取螢幕截圖"""
        screenshot_dir = self.log_dir / "screenshots"
        screenshot_dir.mkdir(exist_ok=True)

        screenshot_path = screenshot_dir / f"{exception_id}.png"
        driver.save_screenshot(str(screenshot_path))

        return screenshot_path

    def _capture_page_source(self, driver, exception_id: str) -> Path:
        """擷取頁面原始碼"""
        page_source_dir = self.log_dir / "page_sources"
        page_source_dir.mkdir(exist_ok=True)

        page_source_path = page_source_dir / f"{exception_id}.html"

        try:
            page_source = driver.page_source
            with open(page_source_path, "w", encoding="utf-8") as f:
                f.write(page_source)
        except Exception as e:
            # 如果無法取得頁面原始碼，記錄錯誤資訊
            with open(page_source_path, "w", encoding="utf-8") as f:
                f.write(f"無法取得頁面原始碼: {e}\n")
                f.write(f"當前 URL: {driver.current_url}\n")

        return page_source_path

    def _save_diagnostic_report(self, report: Dict[str, Any], exception_id: str) -> Path:
        """儲存診斷報告"""
        report_path = self.log_dir / f"{exception_id}_diagnostic.json"

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2, default=str)

        return report_path

    def generate_statistics_report(self) -> Path:
        """生成統計報告"""
        stats = self.statistics.get_statistics()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        stats_path = self.log_dir / f"exception_statistics_{timestamp}.json"

        with open(stats_path, "w", encoding="utf-8") as f:
            json.dump(stats, f, ensure_ascii=False, indent=2, default=str)

        self.logger.info(f"異常統計報告已生成", report_path=str(stats_path))
        return stats_path

    def analyze_exception_patterns(self) -> Dict[str, Any]:
        """分析異常模式"""
        stats = self.statistics.get_statistics()

        analysis = {
            "total_exceptions": stats["total_exceptions"],
            "unique_exception_types": len(stats["exception_types"]),
            "most_common_exception": None,
            "exception_frequency": {},
            "recommendations": [],
        }

        if stats["top_exceptions"]:
            top_exception = stats["top_exceptions"][0]
            analysis["most_common_exception"] = top_exception

            # 頻率分析
            for exc_data in stats["top_exceptions"]:
                exc_type = exc_data["type"]
                analysis["exception_frequency"][exc_type] = exc_data["count"]

            # 建議
            analysis["recommendations"] = self._generate_recommendations(stats)

        return analysis

    def _generate_recommendations(self, stats: Dict[str, Any]) -> List[str]:
        """根據異常統計生成建議"""
        recommendations = []

        if stats["total_exceptions"] > 50:
            recommendations.append("異常發生頻率較高，建議檢查系統穩定性")

        top_exceptions = stats["top_exceptions"]
        if top_exceptions:
            top_type = top_exceptions[0]["type"]

            if top_type == "LoginError":
                recommendations.append("登入錯誤頻繁，建議檢查帳號設定和網路連線")
            elif top_type == "NavigationError":
                recommendations.append("導航錯誤頻繁，建議檢查頁面元素選擇器和等待機制")
            elif top_type == "TimeoutError":
                recommendations.append("超時錯誤頻繁，建議調整等待時間或改善網路環境")
            elif top_type == "DataError":
                recommendations.append("數據錯誤頻繁，建議檢查數據解析邏輯")

        return recommendations

    def get_debug_info(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """取得除錯資訊"""
        diagnostic_info = DiagnosticInfo()

        debug_info = {
            "session_id": self.session_id,
            "diagnostic_info": diagnostic_info.to_dict(),
            "statistics_summary": self.statistics.get_statistics(),
            "log_directory": str(self.log_dir),
        }

        if not include_sensitive:
            # 移除敏感資訊
            if "environment" in debug_info["diagnostic_info"]:
                env = debug_info["diagnostic_info"]["environment"]
                for key in list(env.keys()):
                    if any(sensitive in key.lower() for sensitive in ["password", "key", "token"]):
                        env[key] = "***REDACTED***"

        return debug_info


# 全域診斷管理器實例
_global_diagnostic_manager: Optional[DiagnosticManager] = None


def get_diagnostic_manager(log_dir: Optional[Path] = None) -> DiagnosticManager:
    """
    取得全域診斷管理器實例

    Args:
        log_dir: 日誌目錄

    Returns:
        DiagnosticManager 實例
    """
    global _global_diagnostic_manager

    if _global_diagnostic_manager is None:
        _global_diagnostic_manager = DiagnosticManager(log_dir)

    return _global_diagnostic_manager


def capture_exception_with_diagnostics(
    exception: Exception,
    context: Dict[str, Any] = None,
    capture_screenshot: bool = False,
    capture_page_source: bool = False,
    driver=None,
) -> str:
    """
    便利函數：捕獲異常並生成診斷報告

    Args:
        exception: 異常實例
        context: 額外的上下文資訊
        capture_screenshot: 是否擷取螢幕截圖
        capture_page_source: 是否擷取頁面原始碼
        driver: WebDriver 實例

    Returns:
        診斷報告的檔案路徑
    """
    diagnostic_manager = get_diagnostic_manager()
    return diagnostic_manager.capture_exception(
        exception,
        context,
        capture_screenshot,
        capture_page_source,
        driver
    )