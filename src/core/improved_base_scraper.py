"""
改進版 BaseScraper - 展示重構後的架構設計
集成常數管理、異常處理、智慧等待和結構化日誌
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver

from .browser_utils import init_chrome_browser
from .constants import ErrorMessages, Messages, RetryConfig, Selectors, Timeouts
from .diagnostic_manager import DiagnosticManager, get_diagnostic_manager
from .exceptions import AdvancedScrapingError, IframeError, LoginError, NavigationError
from .logging_config import LoggingContext, ScrapingLogger, get_logger
from .smart_wait import SmartWaiter, create_smart_waiter


class ImprovedBaseScraper(ABC):
    """
    改進版基礎爬蟲類別

    特色改進：
    - 使用常數管理硬編碼值
    - 精確的異常處理
    - 智慧等待機制
    - 結構化日誌記錄
    - 更清晰的職責分離
    """

    def __init__(
        self,
        url: str,
        username: str,
        password: str,
        headless: bool = False,
        logger: Optional[ScrapingLogger] = None,
    ):
        """
        初始化爬蟲

        Args:
            url: 登入網址
            username: 使用者名稱
            password: 密碼
            headless: 是否使用無頭模式
            logger: 自定義日誌記錄器
        """
        self.url = url
        self.username = username
        self.password = password
        self.headless = headless

        # 初始化日誌記錄器
        self.logger = logger or get_logger()

        # 初始化診斷管理器
        self.diagnostic_manager = get_diagnostic_manager()

        # WebDriver 相關
        self.driver: Optional[WebDriver] = None
        self.waiter: Optional[SmartWaiter] = None

        # 目錄設定
        self._setup_directories()

        # 初始化瀏覽器
        self._init_browser()

    def _setup_directories(self) -> None:
        """設定工作目錄"""
        from pathlib import Path

        base_dir = Path.cwd()
        # 所有帳號使用同一個下載目錄（與原始 BaseScraper 保持一致）
        self.download_dir = base_dir / "downloads"
        self.reports_dir = base_dir / "reports"
        self.logs_dir = base_dir / "logs"
        self.temp_dir = base_dir / "temp"

        # 建立目錄
        for directory in [
            self.download_dir,
            self.reports_dir,
            self.logs_dir,
            self.temp_dir,
        ]:
            directory.mkdir(parents=True, exist_ok=True)

    def _init_browser(self) -> None:
        """初始化瀏覽器"""
        try:
            with LoggingContext(self.logger, "瀏覽器初始化"):
                self.driver, _ = init_chrome_browser(
                    headless=self.headless, download_dir=str(self.download_dir)
                )
                self.waiter = create_smart_waiter(self.driver, Timeouts.DEFAULT_WAIT)
                self.logger.info("瀏覽器初始化成功", headless=self.headless)
        except Exception as e:
            # 使用診斷管理器捕獲瀏覽器初始化錯誤
            diagnostic_report = self.diagnostic_manager.capture_exception(
                e,
                context={
                    "operation": "browser_initialization",
                    "headless": self.headless,
                    "download_dir": str(self.download_dir),
                },
                capture_screenshot=False,  # 瀏覽器未初始化，無法截圖
                capture_page_source=False,
            )

            enhanced_error = AdvancedScrapingError(
                f"瀏覽器初始化失敗: {str(e)}",
                details={"headless": self.headless},
                context={
                    "download_dir": str(self.download_dir),
                    "diagnostic_report": diagnostic_report,
                },
                recovery_suggestions=[
                    "檢查 Chrome 瀏覽器安裝狀態",
                    "驗證 ChromeDriver 版本相容性",
                    "確認 .env 檔案中的 Chrome 路徑設定",
                    "檢查系統資源是否充足",
                ],
                error_code="BROWSER_INIT_FAILED",
            )
            raise enhanced_error from e

    def login(self) -> bool:
        """
        登入系統

        Returns:
            是否成功登入

        Raises:
            LoginError: 登入失敗
        """
        max_retries = RetryConfig.MAX_LOGIN_RETRIES

        for attempt in range(1, max_retries + 1):
            try:
                with LoggingContext(
                    self.logger,
                    f"登入嘗試 {attempt}/{max_retries}",
                    username=self.username,
                    attempt=attempt,
                ):
                    self.logger.info(f"開始第 {attempt} 次登入嘗試", username=self.username)

                    # 載入登入頁面
                    assert self.driver is not None, "Driver not initialized"
                    assert self.waiter is not None, "Waiter not initialized"
                    self.driver.get(self.url)
                    self.waiter.wait_for_page_load(Timeouts.PAGE_LOAD)

                    # 填寫登入表單
                    if not self._fill_login_form():
                        continue

                    # 處理驗證碼
                    captcha_code = self._handle_captcha()
                    if captcha_code is None and not self.headless:
                        self.logger.warning(Messages.CAPTCHA_MANUAL)
                        # 等待手動輸入
                        self.waiter.wait_for_condition(
                            lambda: self._check_login_success(),
                            Timeouts.CAPTCHA_INPUT_WAIT,
                        )

                    # 提交登入
                    if self._submit_login_form():
                        if self._check_login_success():
                            self.logger.log_operation_success(
                                "登入", username=self.username
                            )
                            return True

                    self.logger.warning(
                        f"登入嘗試 {attempt} 失敗，{max_retries - attempt} 次機會剩餘"
                    )

            except Exception as e:
                # 使用診斷管理器捕獲詳細錯誤資訊
                diagnostic_report = self.diagnostic_manager.capture_exception(
                    e,
                    context={
                        "operation": "login",
                        "attempt": attempt,
                        "max_retries": max_retries,
                        "username": self.username,
                        "url": self.url,
                        "headless": self.headless,
                    },
                    capture_screenshot=True,
                    capture_page_source=True,
                    driver=self.driver,
                )

                self.logger.error(
                    f"登入嘗試 {attempt} 發生異常",
                    exc_info=True,
                    error=str(e),
                    diagnostic_report=diagnostic_report,
                )

                if attempt == max_retries:
                    # 建立增強型異常
                    enhanced_error = AdvancedScrapingError(
                        ErrorMessages.LOGIN_MAX_RETRIES,
                        details={
                            "username": self.username,
                            "retry_count": attempt,
                            "last_error": str(e),
                        },
                        context={
                            "url": self.url,
                            "headless": self.headless,
                            "diagnostic_report": diagnostic_report,
                        },
                        recovery_suggestions=[
                            "檢查網路連線狀態",
                            "驗證帳號密碼是否正確",
                            "確認登入頁面是否正常載入",
                            "檢查 Chrome 版本相容性",
                        ],
                        error_code="LOGIN_RETRY_EXHAUSTED",
                    )
                    raise enhanced_error from e

        # 所有重試都失敗，建立增強型異常
        enhanced_error = AdvancedScrapingError(
            ErrorMessages.LOGIN_MAX_RETRIES,
            details={"username": self.username, "retry_count": max_retries},
            context={
                "url": self.url,
                "headless": self.headless,
                "final_url": self.driver.current_url if self.driver else None,
            },
            recovery_suggestions=[
                "檢查帳號密碼是否正確",
                "驗證網路連線狀態",
                "確認登入頁面是否正常載入",
                "檢查驗證碼處理邏輯",
            ],
            error_code="LOGIN_ALL_RETRIES_FAILED",
        )
        raise enhanced_error

    def _fill_login_form(self) -> bool:
        """填寫登入表單"""
        try:
            assert self.waiter is not None, "Waiter not initialized"
            # 使用智慧等待填寫表單
            username_success = self.waiter.safe_send_keys(
                By.CSS_SELECTOR, Selectors.LOGIN_USERNAME, self.username
            )
            password_success = self.waiter.safe_send_keys(
                By.CSS_SELECTOR, Selectors.LOGIN_PASSWORD, self.password
            )

            if not (username_success and password_success):
                self.logger.error(ErrorMessages.LOGIN_ELEMENT_NOT_FOUND)
                return False

            return True

        except Exception as e:
            self.logger.error("登入表單填寫失敗", exc_info=True, error=str(e))
            return False

    def _handle_captcha(self) -> Optional[str]:
        """
        處理驗證碼

        Returns:
            識別出的驗證碼,或 None 如果無法識別
        """
        try:
            assert self.waiter is not None, "Waiter not initialized"
            # 等待驗證碼元素出現
            if not self.waiter.wait_for_element_present(
                By.CSS_SELECTOR, Selectors.LOGIN_CAPTCHA, Timeouts.SHORT_WAIT
            ):
                return None

            # 嘗試自動識別驗證碼
            captcha_code = self._detect_captcha_auto()

            if captcha_code:
                self.logger.info(Messages.CAPTCHA_DETECTED, captcha=captcha_code)
                # 填入驗證碼
                self.waiter.safe_send_keys(
                    By.CSS_SELECTOR, Selectors.LOGIN_CAPTCHA, captcha_code
                )
                return captcha_code

            return None

        except Exception as e:
            self.logger.warning("驗證碼處理失敗", exc_info=True, error=str(e))
            return None

    def _detect_captcha_auto(self) -> Optional[str]:
        """
        自動識別驗證碼 - 使用多種方法偵測WEDI系統的4位英數字驗證碼
        移植自原始 BaseScraper 的成功邏輯

        Returns:
            識別出的驗證碼
        """
        import re

        assert self.driver is not None, "Driver not initialized"
        self.logger.info("🔍 開始自動偵測驗證碼...", operation="captcha_detection")

        try:
            # 方法1: 尋找紅色字體的識別碼 (通常在右側)
            try:
                red_elements = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "*[style*='color: red'], *[color='red'], font[color='red']",
                )
                for element in red_elements:
                    text = element.text.strip()
                    if re.match(r"^[A-Z0-9]{4}$", text):
                        self.logger.info(
                            "✅ 從紅色字體偵測到驗證碼", captcha=text, method="red_font"
                        )
                        return text
            except Exception:
                pass

            # 方法2: 尋找包含 "識別碼:" 的文字
            page_text = self.driver.page_source
            match = re.search(r"識別碼[：:]\s*([A-Z0-9]{4})", page_text)
            if match:
                captcha = match.group(1)
                self.logger.info(
                    "✅ 從識別碼標籤偵測到驗證碼", captcha=captcha, method="label_search"
                )
                return captcha

            # 方法3: 尋找table中的4碼英數字（通常在右側cell）
            try:
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                for table in tables:
                    cells = table.find_elements(By.TAG_NAME, "td")
                    for cell in cells:
                        text = cell.text.strip()
                        if re.match(r"^[A-Z0-9]{4}$", text) and text not in [
                            "POST",
                            "GET",
                            "HTTP",
                        ]:
                            self.logger.info(
                                "✅ 從表格偵測到驗證碼", captcha=text, method="table_search"
                            )
                            return text
            except Exception:
                pass

            # 方法4: 搜尋頁面中的4碼英數字（排除常見干擾詞）
            matches = re.findall(r"\b[A-Z0-9]{4}\b", page_text)
            excluded_words = {
                "POST",
                "GET",
                "HTTP",
                "HTML",
                "HEAD",
                "BODY",
                "FORM",
                "2012",
                "2013",
                "2014",
                "2015",
                "2016",
                "2017",
                "2018",
                "2019",
                "2020",
                "2021",
                "2022",
                "2023",
                "2024",
                "2025",
            }

            if matches:
                for match in matches:
                    # 過濾年份和常見網頁詞彙
                    matched_str: str = str(match)  # 確保型別為 str
                    if matched_str in excluded_words:
                        continue
                    if matched_str.isdigit() and 1900 <= int(matched_str) <= 2100:
                        continue
                    self.logger.info(
                        "✅ 從頁面找到可能的驗證碼", captcha=matched_str, method="page_scan"
                    )
                    return matched_str

            # 方法5: 最後嘗試查找所有可見文字元素
            try:
                all_elements = self.driver.find_elements(By.XPATH, "//*[text()]")
                for element in all_elements:
                    try:
                        if element.is_displayed():
                            text = element.text.strip()
                            if (
                                re.match(r"^[A-Z0-9]{4}$", text)
                                and text not in excluded_words
                            ):
                                self.logger.info(
                                    "✅ 從可見元素偵測到驗證碼",
                                    captcha=text,
                                    method="visible_elements",
                                )
                                return text
                    except Exception:
                        continue
            except Exception:
                pass

            self.logger.warning("⚠️ 所有自動偵測方法都失敗", operation="captcha_detection")
            return None

        except Exception as e:
            self.logger.warning(
                "⚠️ 驗證碼自動偵測過程中發生錯誤",
                exc_info=True,
                error=str(e),
                operation="captcha_detection",
            )
            return None

    def _submit_login_form(self) -> bool:
        """提交登入表單"""
        try:
            assert self.waiter is not None, "Waiter not initialized"
            return self.waiter.safe_click(By.CSS_SELECTOR, Selectors.LOGIN_SUBMIT)
        except Exception as e:
            self.logger.error("登入表單提交失敗", exc_info=True, error=str(e))
            return False

    def _check_login_success(self) -> bool:
        """檢查登入是否成功 - 針對WEDI系統優化"""
        try:
            assert self.driver is not None, "Driver not initialized"
            # 首先處理可能的 Alert 彈窗
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                self.logger.warning(f"⚠️ 偵測到 Alert 彈窗", alert_text=alert_text)

                # 如果是識別碼錯誤，記錄並接受彈窗
                if "識別碼" in alert_text and "錯誤" in alert_text:
                    self.logger.error("❌ 驗證碼識別錯誤", alert_text=alert_text)
                    alert.accept()
                    return False
                elif "密碼" in alert_text and "錯誤" in alert_text:
                    self.logger.error("❌ 密碼錯誤", alert_text=alert_text)
                    alert.accept()
                    return False
                else:
                    # 其他類型的彈窗也接受並繼續
                    alert.accept()
                    self.logger.warning("⚠️ 已關閉未知類型的彈窗", alert_text=alert_text)
            except Exception:
                # 沒有彈窗，正常繼續
                pass

            # 等待頁面穩定
            import time

            time.sleep(1.0)

            # 檢查 URL 是否包含 WEDI 主選單
            current_url = self.driver.current_url
            self.logger.info(f"📍 當前 URL: {current_url}", current_url=current_url)

            # WEDI 系統登入成功後會導向 wedimainmenu.asp
            if "wedimainmenu.asp" in current_url:
                self.logger.log_operation_success(
                    "登入成功，已進入主選單", current_url=current_url
                )
                return True

            # 備用檢查：查找主選單相關元素
            try:
                # 檢查是否有查詢作業連結（主選單的特徵）
                query_menu = self.driver.find_elements(By.LINK_TEXT, "查詢作業")
                if query_menu:
                    self.logger.log_operation_success("登入成功，偵測到主選單元素")
                    return True
            except Exception:
                pass

            # 如果 URL 仍然包含登入相關關鍵字，表示登入失敗
            login_keywords = ["login", "signin", "auth", "wedilogin"]
            if any(keyword in current_url.lower() for keyword in login_keywords):
                self.logger.warning("⚠️ 仍在登入頁面，登入可能失敗", current_url=current_url)
                return False

            # 如果到達這裡且沒有明確的失敗跡象，可能是成功的
            self.logger.info("📋 無法確定登入狀態，進行保守判斷", current_url=current_url)
            return False

        except Exception as e:
            self.logger.error("登入狀態檢查失敗", exc_info=True, error=str(e))
            return False

    def navigate_to_query(self) -> bool:
        """
        導航到查詢頁面 - 移植原始 BaseScraper 的完整導航流程

        Returns:
            是否成功導航

        Raises:
            NavigationError: 導航失敗
            IframeError: iframe 切換失敗
        """
        assert self.driver is not None, "Driver not initialized"
        try:
            with LoggingContext(self.logger, "導航到查詢頁面"):
                # 步驟1: 點擊查詢作業選單
                self.logger.info("🧭 步驟1: 點擊查詢作業選單")
                if not self._click_query_operations():
                    raise NavigationError(
                        "找不到查詢作業選單",
                        current_url=self.driver.current_url,
                        target_element="查詢作業",
                    )

                # 等待頁面響應
                import time

                time.sleep(2.0)
                self.logger.info("✅ 已點擊查詢作業選單")

                # 步驟2: 點擊查件頁面 (這是原版中缺少的關鍵步驟)
                self.logger.info("🧭 步驟2: 點擊查件頁面")
                if not self._click_query_page():
                    raise NavigationError(
                        "找不到查件頁面連結",
                        current_url=self.driver.current_url,
                        target_element="查件頁面",
                    )

                # 等待頁面載入
                time.sleep(5.0)
                self.logger.info("✅ 已進入查件頁面")

                # 步驟3: 切換到 datamain iframe
                self.logger.info("🧭 步驟3: 切換到 datamain iframe")
                if not self._switch_to_main_iframe():
                    raise IframeError(
                        ErrorMessages.IFRAME_NOT_FOUND,
                        iframe_name="datamain",
                        current_url=self.driver.current_url,
                    )

                self.logger.info("✅ 已切換到 datamain iframe，準備處理數據")
                return True

        except (IframeError, NavigationError):
            raise
        except Exception as e:
            # 使用診斷管理器捕獲詳細錯誤資訊
            diagnostic_report = self.diagnostic_manager.capture_exception(
                e,
                context={
                    "operation": "navigate_to_query",
                    "current_url": self.driver.current_url if self.driver else None,
                    "username": self.username,
                },
                capture_screenshot=True,
                capture_page_source=True,
                driver=self.driver,
            )

            raise NavigationError(
                f"導航過程發生未預期錯誤: {str(e)}",
                current_url=self.driver.current_url,
                diagnostic_report=diagnostic_report,
            ) from e

    def _switch_to_main_iframe(self) -> bool:
        """切換到主要 iframe"""
        assert self.waiter is not None, "Waiter not initialized"
        return self.waiter.wait_for_iframe_available(
            (By.CSS_SELECTOR, Selectors.DATA_MAIN_IFRAME), Timeouts.IFRAME_SWITCH
        )

    def _click_query_operations(self) -> bool:
        """點擊查詢作業連結"""
        # 使用文字內容尋找連結
        try:
            assert self.driver is not None, "Driver not initialized"
            elements = self.driver.find_elements(
                By.PARTIAL_LINK_TEXT, Selectors.QUERY_OPERATIONS
            )
            if elements:
                elements[0].click()
                return True
            return False
        except Exception:
            return False

    def _click_query_page(self) -> bool:
        """點擊查件頁面連結 - 移植自原始 BaseScraper"""
        try:
            assert self.driver is not None, "Driver not initialized"
            # 使用完全匹配的連結文字
            elements = self.driver.find_elements(By.LINK_TEXT, "查件頁面")
            if elements:
                elements[0].click()
                return True

            # 備用方案：使用部分匹配
            elements = self.driver.find_elements(By.PARTIAL_LINK_TEXT, "查件")
            if elements:
                elements[0].click()
                return True

            return False
        except Exception:
            return False

    def close(self) -> None:
        """關閉瀏覽器"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("瀏覽器已關閉")
            except Exception as e:
                self.logger.warning(f"關閉瀏覽器時發生錯誤: {str(e)}")

    def __enter__(self):
        """支援 context manager"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """支援 context manager"""
        self.close()

    @abstractmethod
    def run_full_process(self) -> List[str]:
        """
        執行完整的抓取流程
        子類別必須實作此方法

        Returns:
            下載的檔案清單
        """


class LoginManager:
    """登入管理器 - 單一職責類別"""

    def __init__(self, driver: WebDriver, waiter: SmartWaiter, logger: ScrapingLogger):
        self.driver = driver
        self.waiter = waiter
        self.logger = logger

    def perform_login(self, url: str, username: str, password: str) -> bool:
        """執行登入流程"""
        # 登入邏輯的具體實作
        raise NotImplementedError("Subclasses must implement perform_login")


class DownloadManager:
    """下載管理器 - 單一職責類別"""

    def __init__(
        self,
        driver: WebDriver,
        waiter: SmartWaiter,
        download_dir: str,
        logger: ScrapingLogger,
    ):
        self.driver = driver
        self.waiter = waiter
        self.download_dir = download_dir
        self.logger = logger

    def download_file(
        self, download_link: str, expected_filename: str
    ) -> Optional[str]:
        """下載檔案"""
        # 下載邏輯的具體實作
        raise NotImplementedError("Subclasses must implement download_file")
