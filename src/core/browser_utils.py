#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
瀏覽器初始化共用函式
"""

import os
import sys
from typing import Optional, Tuple

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

from .logging_config import get_logger

# 模組級別快取：避免每次初始化都重複檢測版本
_version_cache: dict[str, Optional[str]] = {}
_init_count: int = 0  # 追蹤初始化次數，用於減少重複日誌


def _get_chrome_version(chrome_path: Optional[str] = None) -> Optional[str]:
    """取得 Chrome 瀏覽器版本號（使用快取）"""
    cache_key = f"chrome_{chrome_path or 'default'}"
    if cache_key in _version_cache:
        return _version_cache[cache_key]
    
    import subprocess
    version: Optional[str] = None
    try:
        if chrome_path and os.path.exists(chrome_path):
            result = subprocess.run([chrome_path, "--version"], capture_output=True, text=True, timeout=5)
        elif sys.platform == "darwin":
            result = subprocess.run(["/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", "--version"], capture_output=True, text=True, timeout=5)
        elif sys.platform == "win32":
            result = subprocess.run(["reg", "query", "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon", "/v", "version"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                import re
                match = re.search(r'(\d+)\.', result.stdout)
                version = match.group(1) if match else None
            _version_cache[cache_key] = version
            return version
        else:
            result = subprocess.run(["google-chrome", "--version"], capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            import re
            match = re.search(r'(\d+)\.', result.stdout)
            version = match.group(1) if match else None
    except Exception:
        pass
    
    _version_cache[cache_key] = version
    return version


def _get_chromedriver_version(driver_path: Optional[str] = None) -> Optional[str]:
    """取得 ChromeDriver 版本號（使用快取）"""
    cache_key = f"driver_{driver_path or 'default'}"
    if cache_key in _version_cache:
        return _version_cache[cache_key]
    
    import subprocess
    import shutil
    version: Optional[str] = None
    try:
        cmd: Optional[str] = None
        if driver_path and os.path.exists(driver_path):
            cmd = driver_path
        else:
            cmd = shutil.which("chromedriver")
        if not cmd:
            _version_cache[cache_key] = None
            return None

        result = subprocess.run([cmd, "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            import re
            match = re.search(r'(\d+)\.', result.stdout)
            version = match.group(1) if match else None
    except Exception:
        pass
    
    _version_cache[cache_key] = version
    return version


def _check_version_compatibility(chrome_version: Optional[str], driver_version: Optional[str]) -> bool:
    """檢查 Chrome 和 ChromeDriver 版本是否兼容"""
    if not chrome_version or not driver_version:
        return False
    # 主版本號必須匹配
    return chrome_version == driver_version


def init_chrome_browser(
    headless: bool = False, download_dir: Optional[str] = None
) -> Tuple[WebDriver, WebDriverWait]:
    """
    初始化 Chrome 瀏覽器

    Args:
        headless (bool): 是否使用無頭模式
        download_dir (str): 下載目錄路徑

    Returns:
        tuple: (driver, wait) WebDriver 實例和 WebDriverWait 實例
    """
    global _init_count
    _init_count += 1
    is_first_init = _init_count == 1
    
    logger = get_logger("browser_utils")
    # 只在首次初始化時顯示詳細資訊
    if is_first_init:
        logger.info("🚀 啟動瀏覽器...", headless=headless, download_dir=download_dir)
    else:
        logger.debug("🚀 啟動瀏覽器...", headless=headless)

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

    # Ubuntu/Linux 平台特定優化
    is_linux = sys.platform.startswith("linux")
    if is_linux:
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        chrome_options.add_argument("--disable-software-rasterizer")
        chrome_options.add_argument("--disable-gpu")
        if is_first_init:
            logger.info("🐧 檢測到 Linux 環境，已套用 Ubuntu 優化參數", platform="linux")

    # 如果設定為無頭模式，添加 headless 參數
    if headless:
        chrome_options.add_argument("--headless=new")  # 使用新版無頭模式
        if is_linux:
            # Linux 無頭模式記憶體優化
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-software-rasterizer")
            if is_first_init:
                logger.info("🔧 已套用 Ubuntu 無頭模式記憶體優化", mode="headless", platform="linux")
        else:
            chrome_options.add_argument("--disable-gpu")
        if is_first_init:
            logger.info("🔇 使用無頭模式（不顯示瀏覽器視窗）", mode="headless")
    else:
        if is_first_init:
            logger.info("🖥️ 使用視窗模式（顯示瀏覽器）", mode="windowed")

    # 從環境變數讀取 Chrome 路徑（跨平台設定）
    chrome_binary_path = os.getenv("CHROME_BINARY_PATH")
    if chrome_binary_path:
        # 驗證路徑是否存在
        if not os.path.exists(chrome_binary_path):
            error_msg = f"Chrome 二進位檔案不存在: {chrome_binary_path}"
            if is_linux:
                error_msg += "\n💡 Ubuntu 系統建議安裝: sudo apt install chromium-browser"
            logger.critical(error_msg, chrome_path=chrome_binary_path, platform=sys.platform)
            raise FileNotFoundError(error_msg)

        chrome_options.binary_location = chrome_binary_path
        if is_first_init:
            logger.info(
                f"🌐 使用指定 Chrome 路徑: {chrome_binary_path}", chrome_path=chrome_binary_path
            )
    else:
        if is_first_init:
            logger.warning(
                "⚠️ 未設定 CHROME_BINARY_PATH 環境變數，使用系統預設 Chrome", chrome_path="system_default"
            )

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
        chrome_options.add_argument(
            "--disable-features=BlockInsecurePrivateNetworkRequests"
        )
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(
            "--disable-features=DownloadBubble,DownloadBubbleV2"
        )
        chrome_options.add_argument(
            "--disable-component-extensions-with-background-pages"
        )
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
        if is_first_init:
            logger.info("🔓 已配置瀏覽器允許不安全內容下載並關閉所有安全檢查", download_dir=download_dir)

    # 初始化 Chrome 瀏覽器 (優先使用系統 Chrome)
    driver = None

    # 取得 Chrome 版本供後續版本檢查使用
    chrome_version = _get_chrome_version(chrome_binary_path)
    if chrome_version:
        logger.debug(f"🔍 檢測到 Chrome 版本: {chrome_version}")

    # 方法1: 嘗試使用 .env 中設定的 ChromeDriver 路徑
    chromedriver_path = os.getenv("CHROMEDRIVER_PATH")
    if chromedriver_path and os.path.exists(chromedriver_path):
        driver_version = _get_chromedriver_version(chromedriver_path)
        if _check_version_compatibility(chrome_version, driver_version):
            try:
                service = Service(chromedriver_path)
                driver = webdriver.Chrome(service=service, options=chrome_options)
                logger.log_operation_success(
                    "ChromeDriver 啟動",
                    chromedriver_path=chromedriver_path,
                    method="specified_path",
                )
            except Exception as env_error:
                logger.warning(
                    f"⚠️ 指定的 ChromeDriver 路徑失敗: {env_error}",
                    chromedriver_path=chromedriver_path,
                    error=str(env_error),
                )
        else:
            logger.debug(
                f"⏭️ 跳過指定的 ChromeDriver (版本 {driver_version})，Chrome 版本為 {chrome_version}"
            )

    # 方法2: 嘗試使用系統 ChromeDriver (先檢查版本兼容性)
    if not driver:
        system_driver_version = _get_chromedriver_version()
        if _check_version_compatibility(chrome_version, system_driver_version):
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
                logger.warning(
                    f"⚠️ 系統 Chrome 失敗: {system_error}",
                    method="system_chrome",
                    error=str(system_error),
                )
        else:
            logger.debug(
                f"⏭️ 跳過系統 ChromeDriver (版本 {system_driver_version})，Chrome 版本為 {chrome_version}，將使用 WebDriver Manager"
            )

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
            logger.error(
                f"⚠️ WebDriver Manager 也失敗: {wdm_error}",
                method="webdriver_manager",
                error=str(wdm_error),
            )

    # 如果所有方法都失敗
    if not driver:
        # 根據平台提供不同的故障排除步驟
        if is_linux:
            error_msg = """所有方法都失敗，請檢查以下項目:
   1. 安裝 Chromium: sudo apt install chromium-browser chromium-chromedriver
   2. 設定 .env 檔案:
      CHROME_BINARY_PATH=/usr/bin/chromium-browser
      CHROMEDRIVER_PATH=/usr/bin/chromedriver
   3. 驗證安裝: chromium-browser --version && chromedriver --version
   4. 檢查權限: ls -la /usr/bin/chromium-browser /usr/bin/chromedriver"""
        else:
            error_msg = """所有方法都失敗，請檢查以下項目:
   1. 確認已安裝 Google Chrome 瀏覽器
   2. 手動下載 ChromeDriver 並設定到 .env 檔案: CHROMEDRIVER_PATH="C:\\path\\to\\chromedriver.exe"
   3. 或將 ChromeDriver 放入系統 PATH
   4. 執行以下命令清除緩存: rmdir /s "%USERPROFILE%\\.wdm" """

        logger.critical(
            f"❌ 無法啟動 Chrome 瀏覽器 (平台: {sys.platform})",
            troubleshooting_steps=error_msg,
            platform=sys.platform,
            exc_info=True,
        )
        raise Exception(f"無法啟動 Chrome 瀏覽器 (平台: {sys.platform})")

    # 創建 WebDriverWait 實例
    wait = WebDriverWait(driver, 10)

    return driver, wait
