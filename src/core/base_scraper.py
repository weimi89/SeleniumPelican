#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基礎抓取器共用模組
包含登入、導航等核心功能
"""

import os
import re
import time
from pathlib import Path
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .browser_utils import init_chrome_browser
from ..utils.windows_encoding_utils import safe_print


class BaseScraper:
    """基礎抓取器類別"""

    def __init__(self, username, password, headless=False, download_base_dir="downloads"):
        # 載入環境變數
        load_dotenv()

        self.url = "http://wedinlb03.e-can.com.tw/wEDI2012/wedilogin.asp"
        self.username = username
        self.password = password
        self.headless = headless

        self.driver = None
        self.wait = None

        # 所有帳號使用同一個下載目錄
        self.download_dir = Path(download_base_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

        # 建立專屬資料夾
        self.reports_dir = Path("reports")
        self.logs_dir = Path("logs")
        self.temp_dir = Path("temp")

        # 確保資料夾存在
        for dir_path in [self.reports_dir, self.logs_dir, self.temp_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

    def init_browser(self):
        """初始化瀏覽器"""
        # 使用共用的瀏覽器初始化函式
        self.driver, self.wait = init_chrome_browser(
            headless=self.headless,
            download_dir=str(self.download_dir.absolute())
        )
        safe_print("✅ 瀏覽器初始化完成")

    def login(self):
        """執行登入流程"""
        safe_print("🌐 開始登入流程...")

        # 前往登入頁面
        self.driver.get(self.url)
        time.sleep(2)
        safe_print("✅ 登入頁面載入完成")

        # 登入頁面載入完成

        # 填寫表單
        self.fill_login_form()
        submit_success = self.submit_login()

        if not submit_success:
            safe_print("❌ 登入失敗 - 表單提交有誤")
            return False

        # 檢查登入結果
        success = self.check_login_success()
        if success:
            safe_print("✅ 登入成功！")
            return True
        else:
            safe_print("❌ 登入失敗")
            return False

    def fill_login_form(self):
        """填寫登入表單"""
        safe_print("📝 填寫登入表單...")

        try:
            # 填入客代
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "CUST_ID"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            safe_print(f"✅ 已填入客代: {self.username}")

            # 填入密碼
            password_field = self.driver.find_element(By.NAME, "CUST_PASSWORD")
            password_field.clear()
            password_field.send_keys(self.password)
            safe_print("✅ 已填入密碼")

            # 偵測並填入驗證碼
            captcha = self.detect_captcha()
            if captcha:
                captcha_field = self.driver.find_element(By.NAME, "KEY_RND")
                captcha_field.clear()
                captcha_field.send_keys(captcha)
                safe_print(f"✅ 已填入驗證碼: {captcha}")
            else:
                safe_print("⚠️ 無法自動偵測驗證碼，等待手動輸入...")
                time.sleep(10)  # 給用戶10秒手動輸入驗證碼

        except Exception as e:
            safe_print(f"❌ 填寫表單失敗: {e}")

    def detect_captcha(self):
        """偵測驗證碼"""
        safe_print("🔍 偵測驗證碼...")

        try:
            # 方法1: 尋找紅色字體的識別碼 (通常在右側)
            try:
                red_elements = self.driver.find_elements(By.CSS_SELECTOR, "*[style*='color: red'], *[color='red'], font[color='red']")
                for element in red_elements:
                    text = element.text.strip()
                    if re.match(r'^[A-Z0-9]{4}$', text):
                        safe_print(f"✅ 從紅色字體偵測到驗證碼: {text}")
                        return text
            except:
                pass

            # 方法2: 尋找包含 "識別碼:" 的文字
            page_text = self.driver.page_source
            match = re.search(r'識別碼[：:]\s*([A-Z0-9]{4})', page_text)
            if match:
                captcha = match.group(1)
                safe_print(f"✅ 從識別碼標籤偵測到驗證碼: {captcha}")
                return captcha

            # 方法3: 尋找table中的4碼英數字（通常在右側cell）
            try:
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                for table in tables:
                    cells = table.find_elements(By.TAG_NAME, "td")
                    for cell in cells:
                        text = cell.text.strip()
                        if re.match(r'^[A-Z0-9]{4}$', text) and text not in ['POST', 'GET', 'HTTP']:
                            safe_print(f"✅ 從表格偵測到驗證碼: {text}")
                            return text
            except:
                pass

            # 方法4: 搜尋頁面中的4碼英數字（排除常見干擾詞）
            matches = re.findall(r'\b[A-Z0-9]{4}\b', page_text)
            excluded_words = {'POST', 'GET', 'HTTP', 'HTML', 'HEAD', 'BODY', 'FORM', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024', '2025'}

            if matches:
                for match in matches:
                    # 過濾年份和常見網頁詞彙
                    if match in excluded_words:
                        continue
                    if match.isdigit() and 1900 <= int(match) <= 2100:
                        continue
                    safe_print(f"✅ 從頁面找到可能的驗證碼: {match}")
                    return match

        except Exception as e:
            safe_print(f"❌ 偵測驗證碼失敗: {e}")

        return None

    def submit_login(self):
        """提交登入表單"""
        safe_print("📤 提交登入表單...")

        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
            submit_button.click()

            # 等待頁面載入並處理可能的Alert
            time.sleep(3)

            # 檢查是否有Alert彈窗
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                safe_print(f"⚠️ 出現警告彈窗: {alert_text}")
                alert.accept()  # 點擊確定
                return False  # 登入失敗
            except:
                pass  # 沒有Alert彈窗

            safe_print("✅ 表單已提交")
            return True

        except Exception as e:
            safe_print(f"❌ 提交表單失敗: {e}")
            return False

    def check_login_success(self):
        """檢查登入是否成功"""
        safe_print("🔐 檢查登入狀態...")

        current_url = self.driver.current_url
        safe_print(f"📍 當前 URL: {current_url}")

        # 檢查是否包含主選單
        if 'wedimainmenu.asp' in current_url:
            safe_print("✅ 登入成功，已進入主選單")
            return True
        else:
            safe_print("❌ 登入失敗或頁面異常")
            # 已移除截圖功能
            return False

    def navigate_to_query(self):
        """簡化導航 - 直接進入查件頁面並準備處理數據"""
        safe_print("🧭 簡化導航流程...")

        try:
            # 點擊查詢作業選單
            query_menu = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "查詢作業"))
            )
            query_menu.click()
            time.sleep(2)
            safe_print("✅ 已點擊查詢作業選單")

            # 點擊查件頁面
            query_page = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "查件頁面"))
            )
            query_page.click()
            time.sleep(5)  # 等待頁面載入
            safe_print("✅ 已進入查件頁面")

            # 切換到datamain iframe並保持在其中
            iframe = self.wait.until(
                EC.presence_of_element_located((By.NAME, "datamain"))
            )
            self.driver.switch_to.frame(iframe)
            safe_print("✅ 已切換到 datamain iframe，準備處理數據")

            return True

        except Exception as e:
            safe_print(f"❌ 導航失敗: {e}")
            return False

    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            safe_print("🔚 瀏覽器已關閉")