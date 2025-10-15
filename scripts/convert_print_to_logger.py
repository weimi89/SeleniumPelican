#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Print to Logger Conversion Script for SeleniumPelican
Automatically converts print() and safe_print() calls to structured logging
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logging_config import get_logger


class PrintToLoggerConverter:
    """Convert print statements to structured logging calls"""

    def __init__(self):
        self.logger = get_logger("print_converter")
        self.conversion_stats = {
            "safe_print_converted": 0,
            "print_converted": 0,
            "files_processed": 0,
            "total_conversions": 0,
        }

    def analyze_print_pattern(self, content: str) -> str:
        """Analyze print content to determine appropriate log level"""
        content_lower = content.lower()

        if any(
            marker in content_lower for marker in ["❌", "错误", "error", "failed", "失败"]
        ):
            return "error"
        elif any(marker in content_lower for marker in ["⚠️", "警告", "warning", "warn"]):
            return "warning"
        elif any(marker in content_lower for marker in ["✅", "成功", "success", "完成"]):
            return "info"  # success operations
        elif any(
            marker in content_lower for marker in ["🔍", "搜索", "search", "find", "查找"]
        ):
            return "debug"
        elif any(marker in content_lower for marker in ["📊", "数据", "data", "記錄"]):
            return "info"  # data operations
        else:
            return "info"  # default

    def extract_context_info(self, content: str) -> Dict[str, str]:
        """Extract context information from print content"""
        context = {}

        # Extract common patterns
        # Date patterns
        date_match = re.search(r"(\d{8})", content)
        if date_match:
            context["date"] = date_match.group(1)

        # Number patterns
        number_match = re.search(r"(\d+)\s*個", content)
        if number_match:
            context["count"] = number_match.group(1)

        # Error patterns
        error_match = re.search(r"失敗[:：]\s*(.+)", content)
        if error_match:
            context["error"] = error_match.group(1)

        # Operation patterns
        if "登入" in content:
            context["operation"] = "login"
        elif "下載" in content:
            context["operation"] = "download"
        elif "搜尋" in content or "查詢" in content:
            context["operation"] = "search"
        elif "設定" in content:
            context["operation"] = "config"
        elif "導航" in content:
            context["operation"] = "navigation"

        return context

    def convert_safe_print_call(self, match: re.Match) -> str:
        """Convert a safe_print() call to appropriate logger call"""
        full_match = match.group(0)
        content = match.group(1)

        # Remove f-string prefix if present
        if content.startswith('f"') or content.startswith("f'"):
            content = content[2:-1]
        elif content.startswith('"') or content.startswith("'"):
            content = content[1:-1]

        # Determine log level
        log_level = self.analyze_print_pattern(content)

        # Extract context
        context = self.extract_context_info(content)

        # Build context string
        context_str = ""
        if context:
            context_items = [
                f'{k}="{v}"' if isinstance(v, str) else f"{k}={v}"
                for k, v in context.items()
            ]
            context_str = ", " + ", ".join(context_items)

        # Choose appropriate logger method
        if "✅" in content and ("成功" in content or "完成" in content):
            if context.get("operation"):
                clean_content = content.replace("✅ ", "").strip()
                method = (
                    f'self.logger.log_operation_success("{clean_content}"{context_str})'
                )
            else:
                method = f'self.logger.{log_level}(f"{content}"{context_str})'
        elif "❌" in content:
            if context.get("operation"):
                clean_content = content.replace("❌ ", "").strip()
                error_msg = context.get("error", "操作失敗")
                method = f'self.logger.log_operation_failure("{clean_content}", "{error_msg}"{context_str})'
            else:
                method = f'self.logger.{log_level}(f"{content}"{context_str})'
        elif "📊" in content and context.get("count"):
            clean_content = content.split("📊")[1].strip() if "📊" in content else content
            count_value = context["count"]
            context_clean = (
                context_str.replace(f'count="{count_value}"', "")
                .replace(", ,", ",")
                .strip(", ")
            )
            method = f'self.logger.log_data_info("{clean_content}", count={count_value}{context_clean})'
        else:
            method = f'self.logger.{log_level}(f"{content}"{context_str})'

        self.conversion_stats["safe_print_converted"] += 1
        return method

    def convert_print_call(self, match: re.Match) -> str:
        """Convert a print() call to appropriate logger call"""
        full_match = match.group(0)
        content = match.group(1)

        # Simple print calls usually go to info level
        log_level = "info"

        # Build basic logger call
        method = f"self.logger.{log_level}({content})"

        self.conversion_stats["print_converted"] += 1
        return method

    def convert_file(self, file_path: Path) -> bool:
        """Convert print statements in a single file"""
        try:
            self.logger.info(f"🔄 轉換檔案: {file_path}", file_path=str(file_path))

            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Check if file uses ImprovedBaseScraper (has self.logger available)
            if "ImprovedBaseScraper" not in content:
                self.logger.warning(
                    f"⚠️ 檔案 {file_path} 未使用 ImprovedBaseScraper，跳過轉換",
                    file_path=str(file_path),
                )
                return False

            # Convert safe_print() calls
            safe_print_pattern = r"safe_print\(([^)]+)\)"
            content = re.sub(safe_print_pattern, self.convert_safe_print_call, content)

            # Convert print() calls (but be careful not to convert print inside strings)
            # Only convert standalone print() calls that are likely logging
            print_pattern = r"\bprint\(([^)]+)\)(?!\s*#.*debug|#.*test)"
            content = re.sub(print_pattern, self.convert_print_call, content)

            # Remove safe_print import if no longer needed
            if "safe_print(" not in content:
                content = re.sub(
                    r"from\s+.*\.windows_encoding_utils\s+import.*safe_print.*\n",
                    "",
                    content,
                )
                content = re.sub(r",\s*safe_print", "", content)
                content = re.sub(r"safe_print\s*,\s*", "", content)

            # Only write if content changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.logger.log_operation_success("檔案轉換完成", file_path=str(file_path))
                self.conversion_stats["files_processed"] += 1
                return True
            else:
                self.logger.info(f"📝 檔案 {file_path} 無需轉換", file_path=str(file_path))
                return False

        except Exception as e:
            self.logger.log_operation_failure("檔案轉換", e, file_path=str(file_path))
            return False

    def convert_project(self, base_path: Optional[Path] = None) -> None:
        """Convert all Python files in the project"""
        if base_path is None:
            base_path = project_root / "src"

        self.logger.info("🚀 開始批量轉換 print 語句為結構化日誌", base_path=str(base_path))

        # Find all Python files
        python_files = list(base_path.rglob("*.py"))

        self.logger.info(
            f"📁 找到 {len(python_files)} 個 Python 檔案", count=len(python_files)
        )

        # Convert each file
        for file_path in python_files:
            # Skip __pycache__ and test files for now
            if "__pycache__" in str(file_path) or str(file_path).endswith("_test.py"):
                continue

            self.convert_file(file_path)

        # Report statistics
        self.conversion_stats["total_conversions"] = (
            self.conversion_stats["safe_print_converted"]
            + self.conversion_stats["print_converted"]
        )

        self.logger.log_data_info("批量轉換完成統計", **self.conversion_stats)

        print("\n📊 轉換統計:")
        print(f"  • 處理檔案數: {self.conversion_stats['files_processed']}")
        print(f"  • safe_print 轉換: {self.conversion_stats['safe_print_converted']}")
        print(f"  • print 轉換: {self.conversion_stats['print_converted']}")
        print(f"  • 總轉換數: {self.conversion_stats['total_conversions']}")

    def convert_specific_files(self, file_patterns: List[str]) -> None:
        """Convert specific files matching patterns"""
        base_path = project_root / "src"

        for pattern in file_patterns:
            files = list(base_path.rglob(pattern))
            self.logger.info(
                f"🎯 轉換符合 '{pattern}' 的檔案", pattern=pattern, count=len(files)
            )

            for file_path in files:
                self.convert_file(file_path)

        # Report statistics
        self.conversion_stats["total_conversions"] = (
            self.conversion_stats["safe_print_converted"]
            + self.conversion_stats["print_converted"]
        )

        self.logger.log_data_info("特定檔案轉換完成統計", **self.conversion_stats)

    def convert_core_modules(self) -> None:
        """Convert core modules that don't inherit ImprovedBaseScraper"""
        core_modules = [
            "src/utils/windows_encoding_utils.py",
            "src/core/base_scraper.py",
            "src/core/config_validator.py",
            "src/core/logging_config.py",
        ]

        self.logger.info("🔧 開始轉換核心模組", modules=core_modules)

        for module_path in core_modules:
            file_path = project_root / module_path
            if file_path.exists():
                self.convert_core_module_file(file_path)

        # Report statistics
        self.conversion_stats["total_conversions"] = (
            self.conversion_stats["safe_print_converted"]
            + self.conversion_stats["print_converted"]
        )

        self.logger.log_data_info("核心模組轉換完成統計", **self.conversion_stats)

    def convert_core_module_file(self, file_path: Path) -> bool:
        """Convert print statements in core module files"""
        try:
            self.logger.info(f"🔄 轉換核心模組: {file_path}", file_path=str(file_path))

            # Read file content
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            original_content = content
            file_name = file_path.name

            # Different strategies for different core modules
            if file_name == "windows_encoding_utils.py":
                content = self._convert_windows_encoding_utils(content)
            elif file_name == "base_scraper.py":
                content = self._convert_base_scraper(content)
            elif file_name == "config_validator.py":
                content = self._convert_config_validator(content)
            elif file_name == "logging_config.py":
                content = self._convert_logging_config(content)

            # Only write if content changed
            if content != original_content:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                self.logger.log_operation_success("核心模組轉換完成", file_path=str(file_path))
                self.conversion_stats["files_processed"] += 1
                return True
            else:
                self.logger.info(f"📝 核心模組 {file_path} 無需轉換", file_path=str(file_path))
                return False

        except Exception as e:
            self.logger.log_operation_failure("核心模組轉換", e, file_path=str(file_path))
            return False

    def _convert_windows_encoding_utils(self, content: str) -> str:
        """Convert windows_encoding_utils.py specific patterns"""
        # Add logger import at the top
        if "from src.core.logging_config import get_logger" not in content:
            import_line = "\nfrom src.core.logging_config import get_logger\n"
            content = content.replace("import sys", f"import sys{import_line}")

        # Add logger initialization after imports
        if 'logger = get_logger("windows_encoding")' not in content:
            content = content.replace(
                "def safe_print(message):",
                'logger = get_logger("windows_encoding")\n\n\ndef safe_print(message):',
            )

        # Convert print statements to logger calls
        print_pattern = r"print\(([^)]+)\)"

        def replace_print(match):
            self.conversion_stats["print_converted"] += 1
            return f"logger.info({match.group(1)})"

        content = re.sub(print_pattern, replace_print, content)

        # Convert specific safe_print calls (but keep the safe_print function)
        content = content.replace(
            'safe_print("⚠️ 偵測到未設定 PYTHONUNBUFFERED 環境變數")',
            'logger.warning("偵測到未設定 PYTHONUNBUFFERED 環境變數", issue="missing_env_var")',
        )
        content = content.replace(
            'safe_print("📝 請使用以下方式執行以確保即時輸出：")',
            'logger.info("請使用以下方式執行以確保即時輸出", operation="setup_instructions")',
        )
        content = content.replace(
            'safe_print("❌ 程式將退出，請使用上述方式重新執行")',
            'logger.error("程式將退出，請使用上述方式重新執行", action="exit")',
        )
        content = content.replace(
            'safe_print("✅ PYTHONUNBUFFERED 環境變數已設定")',
            'logger.info("PYTHONUNBUFFERED 環境變數已設定", status="configured")',
        )

        return content

    def _convert_base_scraper(self, content: str) -> str:
        """Convert base_scraper.py specific patterns"""
        # Add logger import if not present
        if "from .logging_config import get_logger" not in content:
            content = content.replace(
                "from ..utils.windows_encoding_utils import safe_print",
                "from ..utils.windows_encoding_utils import safe_print\nfrom .logging_config import get_logger",
            )

        # Add logger initialization in __init__ method
        if "self.logger = get_logger" not in content:
            init_pattern = r"(def __init__\(self[^:]*\):\s*)"
            replacement = (
                r'\1\n        self.logger = get_logger(f"base_scraper_{self.username}")'
            )
            content = re.sub(init_pattern, replacement, content, flags=re.MULTILINE)

        # Convert safe_print calls with operation context
        safe_print_patterns = {
            'safe_print("✅ 瀏覽器初始化完成")': 'self.logger.log_operation_success("瀏覽器初始化")',
            'safe_print("🌐 開始登入流程...")': 'self.logger.info("開始登入流程", operation="login")',
            'safe_print("✅ 登入頁面載入完成")': 'self.logger.log_operation_success("登入頁面載入")',
            'safe_print("❌ 登入失敗 - 表單提交有誤")': 'self.logger.log_operation_failure("登入", "表單提交有誤")',
            'safe_print("✅ 登入成功！")': 'self.logger.log_operation_success("登入")',
            'safe_print("❌ 登入失敗")': 'self.logger.log_operation_failure("登入", "認證失敗")',
            'safe_print("📝 填寫登入表單...")': 'self.logger.info("填寫登入表單", operation="form_fill")',
        }

        for old_print, new_log in safe_print_patterns.items():
            if old_print in content:
                content = content.replace(old_print, new_log)
                self.conversion_stats["safe_print_converted"] += 1

        # Convert remaining safe_print calls (both f-strings and regular strings)
        remaining_patterns = {
            'safe_print("✅ 已填入密碼")': 'self.logger.log_operation_success("填入密碼")',
            'safe_print("⚠️ 無法自動偵測驗證碼，等待手動輸入...")': 'self.logger.warning("無法自動偵測驗證碼，等待手動輸入", operation="captcha_detection")',
            'safe_print("🔍 偵測驗證碼...")': 'self.logger.info("偵測驗證碼", operation="captcha_detection")',
            'safe_print("📤 提交登入表單...")': 'self.logger.info("提交登入表單", operation="form_submit")',
            'safe_print("✅ 表單已提交")': 'self.logger.log_operation_success("表單提交")',
            'safe_print("🔐 檢查登入狀態...")': 'self.logger.info("檢查登入狀態", operation="login_verification")',
            'safe_print("✅ 登入成功，已進入主選單")': 'self.logger.log_operation_success("登入", details="已進入主選單")',
            'safe_print("❌ 登入失敗或頁面異常")': 'self.logger.log_operation_failure("登入", "頁面異常或認證失敗")',
            'safe_print("🧭 簡化導航流程...")': 'self.logger.info("簡化導航流程", operation="navigation")',
            'safe_print("✅ 已點擊查詢作業選單")': 'self.logger.log_operation_success("點擊查詢作業選單")',
            'safe_print("✅ 已進入查件頁面")': 'self.logger.log_operation_success("進入查件頁面")',
            'safe_print("✅ 已切換到 datamain iframe，準備處理數據")': 'self.logger.log_operation_success("切換到 datamain iframe", status="ready_for_data")',
            'safe_print("🔚 瀏覽器已關閉")': 'self.logger.info("瀏覽器已關閉", operation="cleanup")',
        }

        for old_print, new_log in remaining_patterns.items():
            if old_print in content:
                content = content.replace(old_print, new_log)
                self.conversion_stats["safe_print_converted"] += 1

        # Convert remaining safe_print with f-strings
        pattern = r'safe_print\(f"([^"]+)"\)'

        def replace_fstring_safe_print(match):
            message = match.group(1)
            self.conversion_stats["safe_print_converted"] += 1
            if "✅" in message:
                return (
                    f'self.logger.log_operation_success(f"{message.replace("✅ ", "")}")'
                )
            elif "❌" in message:
                return f'self.logger.log_operation_failure("操作", f"{message.replace("❌ ", "")}")'
            else:
                return f'self.logger.info(f"{message}")'

        content = re.sub(pattern, replace_fstring_safe_print, content)

        return content

    def _convert_config_validator(self, content: str) -> str:
        """Convert config_validator.py specific patterns"""
        # Add logger import
        if "from .logging_config import get_logger" not in content:
            content = content.replace(
                "from ..utils.windows_encoding_utils import safe_print",
                "from ..utils.windows_encoding_utils import safe_print\nfrom .logging_config import get_logger",
            )

        # Add logger to ConfigValidator class
        if "self.logger = get_logger" not in content:
            init_pattern = (
                r"(def __init__\(self[^:]*\):[^}]*?)(self\.project_root = Path)"
            )
            replacement = r'\1self.logger = get_logger("config_validator")\n        \2'
            content = re.sub(init_pattern, replacement, content, flags=re.DOTALL)

        # Convert safe_print patterns in validation report method
        safe_print_patterns = [
            (
                'safe_print("🔍 SeleniumPelican 配置檔案驗證報告")',
                'self.logger.info("SeleniumPelican 配置檔案驗證報告", operation="validation_report")',
            ),
            ('safe_print("=" * 50)', 'self.logger.info("=" * 50)'),
            (
                'safe_print(f"✅ {config_file}: 驗證通過")',
                'self.logger.log_operation_success(f"{config_file} 驗證", config_file=config_file)',
            ),
            (
                'safe_print(f"❌ {config_file}: 發現 {len(errors)} 個問題")',
                'self.logger.error(f"{config_file} 發現 {len(errors)} 個問題", config_file=config_file, error_count=len(errors))',
            ),
            (
                'safe_print(f"   {i}. {error}")',
                'self.logger.error(f"   {i}. {error}", error_detail=error, error_index=i)',
            ),
            (
                'safe_print("🎉 所有配置檔案驗證通過！")',
                'self.logger.log_operation_success("所有配置檔案驗證")',
            ),
            (
                'safe_print("⚠️ 發現配置問題，請檢查並修正上述錯誤")',
                'self.logger.warning("發現配置問題，請檢查並修正上述錯誤", status="validation_failed")',
            ),
        ]

        for old_print, new_log in safe_print_patterns:
            if old_print in content:
                content = content.replace(old_print, new_log)
                self.conversion_stats["safe_print_converted"] += 1

        # Convert safe_print in create_missing_config_files method
        content = content.replace(
            "safe_print(message)",
            'self.logger.info(message, operation="config_creation")',
        )
        if "safe_print(message)" in content:
            self.conversion_stats["safe_print_converted"] += 1

        return content

    def _convert_logging_config(self, content: str) -> str:
        """Convert logging_config.py - minimal changes needed"""
        # This file is the logging system itself, so minimal changes
        # The safe_print in log_with_safe_print is intentional for transition
        # We can add a comment to clarify this

        if "# Transition function - safe_print is intentional" not in content:
            content = content.replace(
                'def log_with_safe_print(message: str, level: str = "INFO", **kwargs):',
                'def log_with_safe_print(message: str, level: str = "INFO", **kwargs):\n    # Transition function - safe_print is intentional for Windows compatibility',
            )

        return content


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="SeleniumPelican Print to Logger 轉換工具")
    parser.add_argument("--all", action="store_true", help="轉換所有專案檔案")
    parser.add_argument("--files", nargs="+", help="轉換特定檔案 (支援萬用字元)")
    parser.add_argument("--payment", action="store_true", help="只轉換 payment_scraper.py")
    parser.add_argument("--freight", action="store_true", help="只轉換 freight_scraper.py")
    parser.add_argument("--scrapers", action="store_true", help="轉換所有 scraper 檔案")
    parser.add_argument("--core", action="store_true", help="轉換核心模組檔案")

    args = parser.parse_args()

    converter = PrintToLoggerConverter()

    if args.payment:
        converter.convert_specific_files(["scrapers/payment_scraper.py"])
    elif args.freight:
        converter.convert_specific_files(["scrapers/freight_scraper.py"])
    elif args.scrapers:
        converter.convert_specific_files(["scrapers/*.py"])
    elif args.core:
        converter.convert_core_modules()
    elif args.files:
        converter.convert_specific_files(args.files)
    elif args.all:
        converter.convert_project()
    else:
        print("使用方式:")
        print("  python scripts/convert_print_to_logger.py --all")
        print("  python scripts/convert_print_to_logger.py --scrapers")
        print("  python scripts/convert_print_to_logger.py --core")
        print("  python scripts/convert_print_to_logger.py --payment")
        print("  python scripts/convert_print_to_logger.py --files 'scrapers/*.py'")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
