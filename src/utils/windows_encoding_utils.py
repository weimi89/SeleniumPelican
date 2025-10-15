#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows 編碼處理共用函式
"""

import os
import sys
from typing import Any

from src.core.logging_config import get_logger

logger = get_logger("windows_encoding")


def safe_print(message: str) -> None:
    """Windows 相容的列印函數"""
    if sys.platform == "win32":
        # Windows 環境，移除可能造成問題的 Unicode 字符
        message = message.replace("✅", "[OK]")
        message = message.replace("❌", "[ERROR]")
        message = message.replace("⚠️", "[WARNING]")
        message = message.replace("🔇", "[HEADLESS]")
        message = message.replace("🖥️", "[WINDOW]")
        message = message.replace("📦", "[PACKAGE]")
        message = message.replace("🏢", "[MULTI]")
        message = message.replace("📊", "[DATA]")
        message = message.replace("🎯", "[TARGET]")
        message = message.replace("🎉", "[SUCCESS]")
        message = message.replace("🚀", "[START]")
        message = message.replace("💰", "[PAYMENT]")
        message = message.replace("🌐", "[WEB]")
        message = message.replace("📝", "[FORM]")
        message = message.replace("🔍", "[SEARCH]")
        message = message.replace("💥", "[FAIL]")
        message = message.replace("📅", "[DATE]")
        message = message.replace("🔐", "[LOGIN]")
        message = message.replace("📍", "[LOCATION]")
        message = message.replace("🧭", "[NAVIGATE]")
        message = message.replace("🤖", "[AUTO]")
        message = message.replace("📥", "[DOWNLOAD]")
        message = message.replace("🔗", "[LINK]")
        message = message.replace("⏭️", "[SKIP]")
        message = message.replace("🚛", "[FREIGHT]")
        message = message.replace("⏳", "[WAITING]")
        message = message.replace("🔚", "[CLOSE]")
        message = message.replace("📤", "[SUBMIT]")
        message = message.replace("🔄", "[PROCESS]")
    logger.info(message)


def setup_windows_encoding() -> bool:
    """設定 Windows UTF-8 支援（如果可能）"""
    global safe_print

    if sys.platform == "win32":
        try:
            # 設定控制台代碼頁為 UTF-8
            os.system("chcp 65001 > nul 2>&1")

            # 設定控制台輸出編碼為 UTF-8
            import codecs

            sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer, "strict")
            sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer, "strict")

            # 如果成功，使用正常的 print
            safe_print = print  # type: ignore[assignment]
            return True
        except Exception:
            # 如果設定失敗，使用相容模式（已定義的 safe_print）
            return False
    return True


def check_pythonunbuffered() -> None:
    """檢查並強制設定 PYTHONUNBUFFERED 環境變數"""
    if not os.environ.get("PYTHONUNBUFFERED"):
        logger.warning("偵測到未設定 PYTHONUNBUFFERED 環境變數", issue="missing_env_var")
        logger.info("請使用以下方式執行以確保即時輸出", operation="setup_instructions")
        if sys.platform == "win32":
            logger.info("")
            logger.info("   推薦方式 - 使用標準化執行腳本 (根目錄):")
            logger.info("   Windows_代收貨款匯款明細.cmd")
            logger.info("   Windows_運費發票明細.cmd")
            logger.info("   Windows_運費未請款明細.cmd")
            logger.info("")
            logger.info("   進階方式 - 直接使用 PowerShell 腳本:")
            logger.info(r"   .\scripts\run_payment.ps1")
            logger.info(r"   .\scripts\run_freight.ps1")
            logger.info(r"   .\scripts\run_unpaid.ps1")
        else:
            logger.info("")
            logger.info("   推薦方式 - 使用標準化執行腳本 (根目錄):")
            logger.info("   ./Linux_代收貨款匯款明細.sh")
            logger.info("   ./Linux_運費發票明細.sh")
            logger.info("   ./Linux_運費未請款明細.sh")
            logger.info("")
            logger.info("   進階方式 - 直接執行 Python 模組:")
            logger.info("   export PYTHONUNBUFFERED=1")
            logger.info(
                '   PYTHONPATH="$(pwd)" uv run python -u src/scrapers/payment_scraper.py'
            )
            logger.info(
                '   PYTHONPATH="$(pwd)" uv run python -u src/scrapers/freight_scraper.py'
            )
            logger.info(
                '   PYTHONPATH="$(pwd)" uv run python -u src/scrapers/unpaid_scraper.py'
            )
        logger.info("")
        logger.error("程式將退出，請使用上述方式重新執行", action="exit")
        sys.exit(1)

    logger.info("PYTHONUNBUFFERED 環境變數已設定", status="configured")


# 初始化 Windows 編碼支援
setup_windows_encoding()
