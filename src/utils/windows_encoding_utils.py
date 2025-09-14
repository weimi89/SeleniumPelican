#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Windows 編碼處理共用函式
"""

import sys
import os

def safe_print(message):
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
    print(message)

def setup_windows_encoding():
    """設定 Windows UTF-8 支援（如果可能）"""
    global safe_print

    if sys.platform == "win32":
        try:
            # 設定控制台代碼頁為 UTF-8
            os.system('chcp 65001 > nul 2>&1')

            # 設定控制台輸出編碼為 UTF-8
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

            # 如果成功，使用正常的 print
            safe_print = print
            return True
        except Exception:
            # 如果設定失敗，使用相容模式（已定義的 safe_print）
            return False
    return True

def check_pythonunbuffered():
    """檢查並強制設定 PYTHONUNBUFFERED 環境變數"""
    if not os.environ.get('PYTHONUNBUFFERED'):
        safe_print("⚠️ 偵測到未設定 PYTHONUNBUFFERED 環境變數")
        safe_print("📝 請使用以下方式執行以確保即時輸出：")
        if sys.platform == "win32":
            print("")
            print("   推薦方式1 - 使用 Windows 批次檔:")
            print("   run.bat download")
            print("")
            print("   推薦方式2 - Windows 命令提示字元:")
            print("   set PYTHONUNBUFFERED=1")
            print("   python -u wedi_selenium_scraper.py")
            print("")
            print("   推薦方式3 - PowerShell:")
            print("   $env:PYTHONUNBUFFERED='1'")
            print("   python -u wedi_selenium_scraper.py")
        else:
            print("   推薦方式 - 使用 shell 腳本:")
            print("   ./run.sh download")
            print("")
            print("   或手動設定:")
            print("   export PYTHONUNBUFFERED=1")
            print("   python -u wedi_selenium_scraper.py")
        print("")
        safe_print("❌ 程式將退出，請使用上述方式重新執行")
        sys.exit(1)

    safe_print("✅ PYTHONUNBUFFERED 環境變數已設定")

# 初始化 Windows 編碼支援
setup_windows_encoding()