"""
智慧等待機制模組
替換硬編碼的 time.sleep，提供更可靠和高效的等待策略
"""

import time
from typing import Callable, Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .constants import Timeouts


class SmartWaiter:
    """智慧等待管理器"""

    def __init__(self, driver: WebDriver, default_timeout: float = Timeouts.DEFAULT_WAIT):
        self.driver = driver
        self.default_timeout = default_timeout
        self.wait = WebDriverWait(driver, default_timeout)

    def wait(self, seconds: float) -> None:
        """
        簡單的時間等待方法

        Args:
            seconds: 等待的秒數
        """
        import time
        time.sleep(seconds)

    def wait_for_element_present(self, by: By, value: str, timeout: Optional[float] = None) -> bool:
        """
        等待元素出現在 DOM 中

        Args:
            by: 定位方式
            value: 定位值
            timeout: 等待超時時間

        Returns:
            元素是否出現
        """
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(EC.presence_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False

    def wait_for_element_visible(self, by: By, value: str, timeout: Optional[float] = None) -> bool:
        """
        等待元素可見

        Args:
            by: 定位方式
            value: 定位值
            timeout: 等待超時時間

        Returns:
            元素是否可見
        """
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(EC.visibility_of_element_located((by, value)))
            return True
        except TimeoutException:
            return False

    def wait_for_element_clickable(
        self, by: By, value: str, timeout: Optional[float] = None
    ) -> bool:
        """
        等待元素可點擊

        Args:
            by: 定位方式
            value: 定位值
            timeout: 等待超時時間

        Returns:
            元素是否可點擊
        """
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(EC.element_to_be_clickable((by, value)))
            return True
        except TimeoutException:
            return False

    def wait_for_text_present(
        self, by: By, value: str, text: str, timeout: Optional[float] = None
    ) -> bool:
        """
        等待指定文字出現在元素中

        Args:
            by: 定位方式
            value: 定位值
            text: 期望的文字
            timeout: 等待超時時間

        Returns:
            文字是否出現
        """
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(EC.text_to_be_present_in_element((by, value), text))
            return True
        except TimeoutException:
            return False

    def wait_for_url_contains(self, partial_url: str, timeout: Optional[float] = None) -> bool:
        """
        等待 URL 包含指定字串

        Args:
            partial_url: 期望包含的 URL 片段
            timeout: 等待超時時間

        Returns:
            URL 是否包含指定字串
        """
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(EC.url_contains(partial_url))
            return True
        except TimeoutException:
            return False

    def wait_for_page_load(self, timeout: Optional[float] = None) -> bool:
        """
        等待頁面完全載入

        Args:
            timeout: 等待超時時間

        Returns:
            頁面是否載入完成
        """
        timeout = timeout or Timeouts.PAGE_LOAD

        def page_loaded():
            return self.driver.execute_script("return document.readyState") == "complete"

        return self.wait_for_condition(page_loaded, timeout)

    def wait_for_iframe_available(
        self, iframe_locator: tuple, timeout: Optional[float] = None
    ) -> bool:
        """
        等待 iframe 可用並切換

        Args:
            iframe_locator: iframe 定位器 (By, value)
            timeout: 等待超時時間

        Returns:
            是否成功切換到 iframe
        """
        timeout = timeout or self.default_timeout
        wait = WebDriverWait(self.driver, timeout)

        try:
            wait.until(EC.frame_to_be_available_and_switch_to_it(iframe_locator))
            return True
        except TimeoutException:
            return False

    def wait_for_condition(
        self,
        condition: Callable[[], bool],
        timeout: Optional[float] = None,
        poll_frequency: float = 0.5,
    ) -> bool:
        """
        等待自定義條件成立

        Args:
            condition: 條件函數，返回 True 表示條件成立
            timeout: 等待超時時間
            poll_frequency: 輪詢頻率（秒）

        Returns:
            條件是否成立
        """
        timeout = timeout or self.default_timeout
        start_time = time.time()

        while time.time() - start_time < timeout:
            try:
                if condition():
                    return True
            except Exception:
                # 條件檢查過程中的異常不應中斷等待
                pass
            time.sleep(poll_frequency)

        return False

    def wait_for_download_complete(
        self,
        download_dir: str,
        expected_filename: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> Optional[str]:
        """
        等待檔案下載完成

        Args:
            download_dir: 下載目錄
            expected_filename: 期望的檔案名（可選）
            timeout: 等待超時時間

        Returns:
            下載的檔案路徑，若未完成則返回 None
        """
        import os

        timeout = timeout or Timeouts.MAX_DOWNLOAD_TIME

        def download_completed():
            if not os.path.exists(download_dir):
                return False

            files = os.listdir(download_dir)

            # 過濾掉臨時檔案
            completed_files = [
                f for f in files if not f.endswith(".crdownload") and not f.endswith(".tmp")
            ]

            if not completed_files:
                return False

            if expected_filename:
                return expected_filename in completed_files

            # 如果沒有指定檔名，返回最新的檔案
            if completed_files:
                latest_file = max(
                    completed_files, key=lambda f: os.path.getctime(os.path.join(download_dir, f))
                )
                return latest_file

            return False

        if self.wait_for_condition(download_completed, timeout, poll_frequency=1.0):
            files = os.listdir(download_dir)
            completed_files = [
                f for f in files if not f.endswith(".crdownload") and not f.endswith(".tmp")
            ]

            if expected_filename and expected_filename in completed_files:
                return os.path.join(download_dir, expected_filename)
            elif completed_files:
                latest_file = max(
                    completed_files, key=lambda f: os.path.getctime(os.path.join(download_dir, f))
                )
                return os.path.join(download_dir, latest_file)

        return None

    def safe_click(self, by: By, value: str, timeout: Optional[float] = None) -> bool:
        """
        安全點擊元素（等待可點擊後再點擊）

        Args:
            by: 定位方式
            value: 定位值
            timeout: 等待超時時間

        Returns:
            是否成功點擊
        """
        if self.wait_for_element_clickable(by, value, timeout):
            try:
                element = self.driver.find_element(by, value)
                element.click()
                return True
            except Exception:
                # 嘗試使用 JavaScript 點擊
                try:
                    element = self.driver.find_element(by, value)
                    self.driver.execute_script("arguments[0].click();", element)
                    return True
                except Exception:
                    return False
        return False

    def safe_send_keys(
        self,
        by: By,
        value: str,
        text: str,
        clear_first: bool = True,
        timeout: Optional[float] = None,
    ) -> bool:
        """
        安全輸入文字（等待元素可見後再輸入）

        Args:
            by: 定位方式
            value: 定位值
            text: 要輸入的文字
            clear_first: 是否先清空輸入框
            timeout: 等待超時時間

        Returns:
            是否成功輸入
        """
        if self.wait_for_element_visible(by, value, timeout):
            try:
                element = self.driver.find_element(by, value)
                if clear_first:
                    element.clear()
                element.send_keys(text)
                return True
            except Exception:
                return False
        return False


def create_smart_waiter(driver: WebDriver, timeout: Optional[float] = None) -> SmartWaiter:
    """
    工廠函數：建立智慧等待器實例

    Args:
        driver: WebDriver 實例
        timeout: 預設超時時間

    Returns:
        SmartWaiter 實例
    """
    timeout = timeout or Timeouts.DEFAULT_WAIT
    return SmartWaiter(driver, timeout)


# 便利函數，用於快速等待操作
def quick_wait_and_click(
    driver: WebDriver, by: By, value: str, timeout: Optional[float] = None
) -> bool:
    """快速等待並點擊元素"""
    waiter = SmartWaiter(driver, timeout or Timeouts.SHORT_WAIT)
    return waiter.safe_click(by, value, timeout)


def quick_wait_and_input(
    driver: WebDriver, by: By, value: str, text: str, timeout: Optional[float] = None
) -> bool:
    """快速等待並輸入文字"""
    waiter = SmartWaiter(driver, timeout or Timeouts.SHORT_WAIT)
    return waiter.safe_send_keys(by, value, text, timeout=timeout)
