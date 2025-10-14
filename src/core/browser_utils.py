#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
瀏覽器初始化共用函式
"""

import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .logging_config import get_logger


def init_chrome_browser(headless=False, download_dir=None):
    """
    初始化 Chrome 瀏覽器

    Args:
        headless (bool): 是否使用無頭模式
        download_dir (str): 下載目錄路徑

    Returns:
        tuple: (driver, wait) WebDriver 實例和 WebDriverWait 實例
    """
    logger = get_logger("browser_utils")
    logger.info("🚀 啟動瀏覽器...", headless=headless, download_dir=download_dir)

    # Chrome 選項設定
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")

    # 隱藏 Chrome 警告訊息
    chrome_options.add_argument("--disable-logging")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--silent")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=0")  # 隱藏 DevTools listening 訊息
    chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # 如果設定為無頭模式，添加 headless 參數
    if headless:
        chrome_options.add_argument("--headless")
        logger.info("🔇 使用無頭模式（不顯示瀏覽器視窗）", mode="headless")
    else:
        logger.info("🖥️ 使用視窗模式（顯示瀏覽器）", mode="windowed")

    # 從環境變數讀取 Chrome 路徑（跨平台設定）
    chrome_binary_path = os.getenv("CHROME_BINARY_PATH")
    if chrome_binary_path:
        chrome_options.binary_location = chrome_binary_path
        logger.info(f"🌐 使用指定 Chrome 路徑: {chrome_binary_path}", chrome_path=chrome_binary_path)
    else:
        logger.warning("⚠️ 未設定 CHROME_BINARY_PATH 環境變數，使用系統預設 Chrome", chrome_path="system_default")

    # 設定下載路徑和安全設定
    if download_dir:
        prefs = {
            "download.default_directory": str(download_dir),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False,  # 關閉安全瀏覽以允許下載
            "safebrowsing.disable_download_protection": True,  # 關閉下載保護
            "profile.default_content_setting_values.automatic_downloads": 1,  # 允許多重下載
            "profile.default_content_settings.popups": 0,  # 關閉彈窗阻擋
            "profile.content_settings.exceptions.automatic_downloads.*.setting": 1,
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # 添加額外的 Chrome 參數來處理不安全下載
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--allow-running-insecure-content")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-features=BlockInsecurePrivateNetworkRequests")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument("--disable-features=DownloadBubble,DownloadBubbleV2")
        chrome_options.add_argument("--disable-component-extensions-with-background-pages")
        chrome_options.add_argument("--disable-default-apps")
        chrome_options.add_argument("--disable-client-side-phishing-detection")
        chrome_options.add_argument("--disable-hang-monitor")
        chrome_options.add_argument("--disable-prompt-on-repost")
        chrome_options.add_argument("--disable-background-timer-throttling")
        chrome_options.add_argument("--disable-renderer-backgrounding")
        chrome_options.add_argument("--disable-backgrounding-occluded-windows")
        chrome_options.add_argument("--force-color-profile=srgb")
        chrome_options.add_argument("--metrics-recording-only")
        chrome_options.add_argument("--disable-background-networking")
        chrome_options.add_argument("--disable-sync")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--safebrowsing-disable-auto-update")
        chrome_options.add_argument("--safebrowsing-disable-download-protection")
        chrome_options.add_argument("--disable-features=TranslateUI")
        chrome_options.add_argument("--disable-features=Translate")
        logger.info("🔓 已配置瀏覽器允許不安全內容下載並關閉所有安全檢查", download_dir=download_dir)

    # 初始化 Chrome 瀏覽器 (優先使用系統 Chrome)
    driver = None

    # 方法1: 嘗試使用 .env 中設定的 ChromeDriver 路徑
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
    if chromedriver_path and os.path.exists(chromedriver_path):
        try:
            service = Service(chromedriver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.log_operation_success("ChromeDriver 啟動", chromedriver_path=chromedriver_path, method="specified_path")
        except Exception as env_error:
            logger.warning(f"⚠️ 指定的 ChromeDriver 路徑失敗: {env_error}", chromedriver_path=chromedriver_path, error=str(env_error))

    # 方法2: 嘗試使用系統 ChromeDriver (通常最穩定)
    if not driver:
        try:
            # 配置 Chrome Service 來隱藏輸出
            if sys.platform == "win32":
                # Windows 上重導向 Chrome 輸出到 null
                service = Service()
                service.creation_flags = 0x08000000  # CREATE_NO_WINDOW
            else:
                # Linux/macOS 使用 devnull
                service = Service(log_path=os.devnull)

            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.log_operation_success("Chrome 啟動", method="system_chrome")
        except Exception as system_error:
            logger.warning(f"⚠️ 系統 Chrome 失敗: {system_error}", method="system_chrome", error=str(system_error))

    # 方法3: 最後嘗試 WebDriver Manager (可能有架構問題)
    if not driver:
        try:
            # 抑制 ChromeDriverManager 的輸出
            import logging

            logging.getLogger("WDM").setLevel(logging.WARNING)

            driver_path = ChromeDriverManager().install()
            service = Service(driver_path)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            logger.log_operation_success("Chrome 啟動", method="webdriver_manager")
        except Exception as wdm_error:
            logger.error(f"⚠️ WebDriver Manager 也失敗: {wdm_error}", method="webdriver_manager", error=str(wdm_error))

    # 如果所有方法都失敗
    if not driver:
        error_msg = """所有方法都失敗，請檢查以下項目:
   1. 確認已安裝 Google Chrome 瀏覽器
   2. 手動下載 ChromeDriver 並設定到 .env 檔案: CHROMEDRIVER_PATH="C:\\path\\to\\chromedriver.exe"
   3. 或將 ChromeDriver 放入系統 PATH
   4. 執行以下命令清除緩存: rmdir /s "%USERPROFILE%\\.wdm" """
        logger.critical("❌ 無法啟動 Chrome 瀏覽器", troubleshooting_steps=error_msg, exc_info=True)
        raise Exception("無法啟動 Chrome 瀏覽器")

    # 創建 WebDriverWait 實例
    wait = WebDriverWait(driver, 10)

    return driver, wait
