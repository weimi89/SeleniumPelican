#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import time

# 設定環境變數關閉輸出緩衝，確保 Windows 即時顯示
# 檢查並強制設定 PYTHONUNBUFFERED 環境變數
if not os.environ.get('PYTHONUNBUFFERED'):
    print("⚠️ 偵測到未設定 PYTHONUNBUFFERED 環境變數")
    print("📝 請使用以下方式執行以確保即時輸出：")
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
    print("❌ 程式將退出，請使用上述方式重新執行")
    sys.exit(1)

print("✅ PYTHONUNBUFFERED 環境變數已設定")

# 設定 Windows 終端支援 UTF-8 輸出
if sys.platform == "win32":
    try:
        # 設定控制台輸出編碼為 UTF-8
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

        # 設定控制台代碼頁為 UTF-8
        os.system('chcp 65001 > nul')
    except Exception:
        # 如果設定失敗，使用替代方案
        pass

import re
import json
from datetime import datetime, timedelta
from pathlib import Path
from dotenv import load_dotenv

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


class WEDISeleniumScraper:
    """
    使用 Selenium 的 WEDI 自動登入抓取工具
    """

    def __init__(self, username, password, headless=False, download_base_dir="downloads", start_date=None, end_date=None):
        # 載入環境變數
        load_dotenv()

        self.url = "http://wedinlb03.e-can.com.tw/wEDI2012/wedilogin.asp"
        self.username = username
        self.password = password
        self.headless = headless

        # 日期範圍設定
        self.start_date = start_date
        self.end_date = end_date

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
        print("🚀 啟動瀏覽器...")

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
        chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 如果設定為無頭模式，添加 headless 參數
        if self.headless:
            chrome_options.add_argument("--headless")
            print("🔇 使用無頭模式（不顯示瀏覽器視窗）")
        else:
            print("🖥️ 使用視窗模式（顯示瀏覽器）")

        # 從環境變數讀取 Chrome 路徑（跨平台設定）
        chrome_binary_path = os.getenv('CHROME_BINARY_PATH')
        if chrome_binary_path:
            chrome_options.binary_location = chrome_binary_path
            print(f"🌐 使用指定 Chrome 路徑: {chrome_binary_path}")
        else:
            print("⚠️ 未設定 CHROME_BINARY_PATH 環境變數，使用系統預設 Chrome")

        # 設定下載路徑
        prefs = {
            "download.default_directory": str(self.download_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)

        # 初始化 Chrome 瀏覽器 (優先使用系統 Chrome)
        self.driver = None

        # 方法1: 嘗試使用 .env 中設定的 ChromeDriver 路徑
        chromedriver_path = os.getenv('CHROMEDRIVER_PATH')
        if chromedriver_path and os.path.exists(chromedriver_path):
            try:
                service = Service(chromedriver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print(f"✅ 使用指定 ChromeDriver 啟動: {chromedriver_path}")
            except Exception as env_error:
                print(f"⚠️ 指定的 ChromeDriver 路徑失敗: {env_error}")

        # 方法2: 嘗試使用系統 ChromeDriver (通常最穩定)
        if not self.driver:
            try:
                # 配置 Chrome Service 來隱藏輸出
                if sys.platform == "win32":
                    # Windows 上重導向 Chrome 輸出到 null
                    service = Service()
                    service.creation_flags = 0x08000000  # CREATE_NO_WINDOW
                else:
                    # Linux/macOS 使用 devnull
                    service = Service(log_path=os.devnull)

                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ 使用系統 Chrome 啟動")
            except Exception as system_error:
                print(f"⚠️ 系統 Chrome 失敗: {system_error}")

        # 方法3: 最後嘗試 WebDriver Manager (可能有架構問題)
        if not self.driver:
            try:
                # 抑制 ChromeDriverManager 的輸出
                import logging
                logging.getLogger('WDM').setLevel(logging.WARNING)

                driver_path = ChromeDriverManager().install()
                service = Service(driver_path)
                self.driver = webdriver.Chrome(service=service, options=chrome_options)
                print("✅ 使用 WebDriver Manager 啟動 Chrome")
            except Exception as wdm_error:
                print(f"⚠️ WebDriver Manager 也失敗: {wdm_error}")

        # 如果所有方法都失敗
        if not self.driver:
            print(f"❌ 所有方法都失敗，請檢查以下項目:")
            print(f"   1. 確認已安裝 Google Chrome 瀏覽器")
            print(f"   2. 手動下載 ChromeDriver 並設定到 .env 檔案:")
            print(f"      CHROMEDRIVER_PATH=\"C:\\path\\to\\chromedriver.exe\"")
            print(f"   3. 或將 ChromeDriver 放入系統 PATH")
            print(f"   4. 執行以下命令清除緩存:")
            print(f"      rmdir /s \"%USERPROFILE%\\.wdm\"")
            raise Exception("無法啟動 Chrome 瀏覽器")
        self.wait = WebDriverWait(self.driver, 10)

        print("✅ 瀏覽器初始化完成")

    def login(self):
        """執行登入流程"""
        print("🌐 開始登入流程...")

        # 前往登入頁面
        self.driver.get(self.url)
        time.sleep(2)
        print("✅ 登入頁面載入完成")

        # 登入頁面載入完成

        # 填寫表單
        self.fill_login_form()
        submit_success = self.submit_login()

        if not submit_success:
            print("❌ 登入失敗 - 表單提交有誤")
            return False

        # 檢查登入結果
        success = self.check_login_success()
        if success:
            print("✅ 登入成功！")
            return True
        else:
            print("❌ 登入失敗")
            return False

    def fill_login_form(self):
        """填寫登入表單"""
        print("📝 填寫登入表單...")

        try:
            # 填入客代
            username_field = self.wait.until(
                EC.presence_of_element_located((By.NAME, "CUST_ID"))
            )
            username_field.clear()
            username_field.send_keys(self.username)
            print(f"✅ 已填入客代: {self.username}")

            # 填入密碼
            password_field = self.driver.find_element(By.NAME, "CUST_PASSWORD")
            password_field.clear()
            password_field.send_keys(self.password)
            print("✅ 已填入密碼")

            # 偵測並填入驗證碼
            captcha = self.detect_captcha()
            if captcha:
                captcha_field = self.driver.find_element(By.NAME, "KEY_RND")
                captcha_field.clear()
                captcha_field.send_keys(captcha)
                print(f"✅ 已填入驗證碼: {captcha}")
            else:
                print("⚠️ 無法自動偵測驗證碼，等待手動輸入...")
                time.sleep(10)  # 給用戶10秒手動輸入驗證碼

        except Exception as e:
            print(f"❌ 填寫表單失敗: {e}")

    def detect_captcha(self):
        """偵測驗證碼"""
        print("🔍 偵測驗證碼...")

        try:
            # 方法1: 尋找紅色字體的識別碼 (通常在右側)
            try:
                red_elements = self.driver.find_elements(By.CSS_SELECTOR, "*[style*='color: red'], *[color='red'], font[color='red']")
                for element in red_elements:
                    text = element.text.strip()
                    if re.match(r'^[A-Z0-9]{4}$', text):
                        print(f"✅ 從紅色字體偵測到驗證碼: {text}")
                        return text
            except:
                pass

            # 方法2: 尋找包含 "識別碼:" 的文字
            page_text = self.driver.page_source
            match = re.search(r'識別碼[：:]\s*([A-Z0-9]{4})', page_text)
            if match:
                captcha = match.group(1)
                print(f"✅ 從識別碼標籤偵測到驗證碼: {captcha}")
                return captcha

            # 方法3: 尋找table中的4碼英數字（通常在右側cell）
            try:
                tables = self.driver.find_elements(By.TAG_NAME, "table")
                for table in tables:
                    cells = table.find_elements(By.TAG_NAME, "td")
                    for cell in cells:
                        text = cell.text.strip()
                        if re.match(r'^[A-Z0-9]{4}$', text) and text not in ['POST', 'GET', 'HTTP']:
                            print(f"✅ 從表格偵測到驗證碼: {text}")
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
                    print(f"✅ 從頁面找到可能的驗證碼: {match}")
                    return match

        except Exception as e:
            print(f"❌ 偵測驗證碼失敗: {e}")

        return None

    def submit_login(self):
        """提交登入表單"""
        print("📤 提交登入表單...")

        try:
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
            submit_button.click()

            # 等待頁面載入並處理可能的Alert
            time.sleep(3)

            # 檢查是否有Alert彈窗
            try:
                alert = self.driver.switch_to.alert
                alert_text = alert.text
                print(f"⚠️ 出現警告彈窗: {alert_text}")
                alert.accept()  # 點擊確定
                return False  # 登入失敗
            except:
                pass  # 沒有Alert彈窗

            print("✅ 表單已提交")
            return True

        except Exception as e:
            print(f"❌ 提交表單失敗: {e}")
            return False

    def check_login_success(self):
        """檢查登入是否成功"""
        print("🔐 檢查登入狀態...")

        current_url = self.driver.current_url
        print(f"📍 當前 URL: {current_url}")

        # 檢查是否包含主選單
        if 'wedimainmenu.asp' in current_url:
            print("✅ 登入成功，已進入主選單")
            return True
        else:
            print("❌ 登入失敗或頁面異常")
            # 已移除截圖功能
            return False

    def navigate_to_payment_query(self):
        """簡化導航 - 直接進入查件頁面並準備處理數據"""
        print("🧭 簡化導航流程...")

        try:
            # 點擊查詢作業選單
            query_menu = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "查詢作業"))
            )
            query_menu.click()
            time.sleep(2)
            print("✅ 已點擊查詢作業選單")

            # 點擊查件頁面
            query_page = self.wait.until(
                EC.element_to_be_clickable((By.LINK_TEXT, "查件頁面"))
            )
            query_page.click()
            time.sleep(5)  # 等待頁面載入
            print("✅ 已進入查件頁面")

            # 切換到datamain iframe並保持在其中
            iframe = self.wait.until(
                EC.presence_of_element_located((By.NAME, "datamain"))
            )
            self.driver.switch_to.frame(iframe)
            print("✅ 已切換到 datamain iframe，準備處理數據")

            return True

        except Exception as e:
            print(f"❌ 導航失敗: {e}")
            return False

    def set_date_range(self):
        """設定查詢日期範圍 - 簡化版本"""
        print("📅 設定日期範圍...")

        # 使用指定的日期範圍，如果沒有指定則使用預設值（當日）
        if self.start_date and self.end_date:
            start_date = self.start_date.strftime("%Y%m%d")
            end_date = self.end_date.strftime("%Y%m%d")
        else:
            # 預設值：當日
            today = datetime.now()
            start_date = today.strftime("%Y%m%d")
            end_date = today.strftime("%Y%m%d")

        print(f"📅 查詢日期範圍: {start_date} ~ {end_date}")

        try:
            # 已經在iframe中，嘗試尋找日期輸入框
            date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')

            if len(date_inputs) >= 2:
                try:
                    # 填入開始日期
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(start_date)
                    print(f"✅ 已設定開始日期: {start_date}")

                    # 填入結束日期
                    date_inputs[1].clear()
                    date_inputs[1].send_keys(end_date)
                    print(f"✅ 已設定結束日期: {end_date}")
                except Exception as date_error:
                    print(f"⚠️ 填入日期失敗: {date_error}")

                # 嘗試多種方式尋找查詢按鈕
                query_button_found = False
                button_selectors = [
                    'input[value*="查詢"]',
                    'button[title*="查詢"]',
                    'input[type="submit"]',
                    'button[type="submit"]',
                    'input[value*="搜尋"]',
                    'button:contains("查詢")'
                ]

                for selector in button_selectors:
                    try:
                        query_button = self.driver.find_element(By.CSS_SELECTOR, selector)
                        query_button.click()
                        print(f"✅ 已點擊查詢按鈕 (使用選擇器: {selector})")
                        time.sleep(2)
                        query_button_found = True
                        break
                    except:
                        continue

                if not query_button_found:
                    print("⚠️ 未找到查詢按鈕，直接繼續流程")
            else:
                print("⚠️ 未找到日期輸入框，可能不需要設定日期")

            return True

        except Exception as e:
            print(f"⚠️ 日期範圍設定過程中出現問題，但繼續執行: {e}")
            return True  # 即使失敗也返回True，讓流程繼續

    def get_payment_records(self):
        """直接在iframe中搜尋代收貨款相關數據"""
        print("📊 搜尋當前頁面中的代收貨款數據...")

        records = []
        try:
            # 此時已經在datamain iframe中，直接搜尋數據
            print("🔍 分析當前頁面內容...")

            # 搜尋所有連結，找出代收貨款相關項目
            all_links = self.driver.find_elements(By.TAG_NAME, "a")
            print(f"   找到 {len(all_links)} 個連結")

            # 定義代收貨款匯款明細相關關鍵字（更精確）
            payment_keywords = [
                "代收貨款", "匯款明細", "(2-1)"
            ]

            # 定義排除關鍵字（增加不需要的項目）
            excluded_keywords = [
                "語音取件", "三節加價", "系統公告", "操作說明", "維護通知",
                "Home", "首頁", "登出", "系統設定",
                "代收款已收未結帳明細", "已收未結帳", "未結帳明細"  # 不需要下載的項目
            ]

            for i, link in enumerate(all_links):
                try:
                    link_text = link.text.strip()
                    if link_text:
                        # 檢查是否需要排除
                        should_exclude = any(keyword in link_text for keyword in excluded_keywords)

                        # 更精確的匹配：必須包含「代收貨款」和「匯款明細」
                        is_payment_remittance = ("代收貨款" in link_text and "匯款明細" in link_text) or "(2-1)" in link_text

                        if is_payment_remittance and not should_exclude:
                            # 生成檔案ID
                            file_id = link_text.replace(" ", "_").replace("[", "").replace("]", "").replace("-", "_")
                            records.append({
                                "index": i + 1,
                                "title": link_text,
                                "payment_no": file_id,
                                "link": link
                            })
                            print(f"   ✅ 找到代收貨款匯款明細: {link_text}")
                        elif should_exclude:
                            print(f"   ⏭️ 跳過排除項目: {link_text}")
                        elif "代收" in link_text:
                            print(f"   ⏭️ 跳過非匯款明細項目: {link_text}")
                except:
                    continue

            # 如果沒有找到任何代收貨款連結，嘗試搜尋表格數據
            if not records:
                print("🔍 未找到代收貨款連結，搜尋表格數據...")
                tables = self.driver.find_elements(By.TAG_NAME, "table")

                for table in tables:
                    rows = table.find_elements(By.TAG_NAME, "tr")
                    for row in rows:
                        cells = row.find_elements(By.TAG_NAME, "td")
                        for cell in cells:
                            cell_text = cell.text.strip()
                            if any(keyword in cell_text for keyword in payment_keywords):
                                print(f"   📋 找到表格中的代收貨款數據: {cell_text}")

            print(f"📊 總共找到 {len(records)} 筆代收貨款相關記錄")
            return records

        except Exception as e:
            print(f"❌ 搜尋代收貨款數據失敗: {e}")
            return records

    def download_excel_for_record(self, record):
        """為特定記錄下載Excel檔案 - 簡化版本"""
        print(f"📥 下載記錄 {record['payment_no']} 的Excel檔案...")

        try:
            # 已經在iframe中，直接查找連結
            links = self.driver.find_elements(By.TAG_NAME, "a")
            found_link = None

            # 尋找匹配的連結
            for link in links:
                try:
                    if record['title'] in link.text:
                        found_link = link
                        break
                except:
                    continue

            if found_link:
                # 使用JavaScript點擊避免元素遮蔽問題
                self.driver.execute_script("arguments[0].click();", found_link)
                time.sleep(5)
            else:
                raise Exception(f"找不到標題為 '{record['title']}' 的可點擊連結")

            downloaded_files = []
            payment_no = record['payment_no']

            # 調試：查看頁面上的所有按鈕和表單元素
            print("🔍 頁面調試資訊:")
            buttons = self.driver.find_elements(By.TAG_NAME, "button")
            inputs = self.driver.find_elements(By.TAG_NAME, "input")
            forms = self.driver.find_elements(By.TAG_NAME, "form")

            print(f"   找到 {len(buttons)} 個按鈕:")
            for i, btn in enumerate(buttons[:10]):  # 只顯示前10個
                try:
                    text = btn.text or btn.get_attribute('value') or btn.get_attribute('title')
                    print(f"     按鈕 {i+1}: {text}")
                except:
                    pass

            print(f"   找到 {len(inputs)} 個input元素:")
            for i, inp in enumerate(inputs[:10]):  # 只顯示前10個
                try:
                    inp_type = inp.get_attribute('type')
                    value = inp.get_attribute('value') or inp.text
                    print(f"     Input {i+1}: type='{inp_type}' value='{value}'")
                except:
                    pass

            print(f"   找到 {len(forms)} 個表單")

            # 進入詳細頁面

            # 在詳細頁面填入查詢日期範圍
            print("📅 在詳細頁面填入查詢日期...")
            try:
                # 使用指定的日期範圍
                if self.start_date and self.end_date:
                    start_date = self.start_date.strftime("%Y%m%d")
                    end_date = self.end_date.strftime("%Y%m%d")
                else:
                    # 預設值：當日
                    today = datetime.now()
                    start_date = today.strftime("%Y%m%d")
                    end_date = today.strftime("%Y%m%d")

                # 找到日期輸入框
                date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')
                if len(date_inputs) >= 2:
                    # 填入開始日期
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(start_date)
                    print(f"✅ 已填入開始日期: {start_date}")

                    # 填入結束日期
                    date_inputs[1].clear()
                    date_inputs[1].send_keys(end_date)
                    print(f"✅ 已填入結束日期: {end_date}")
                elif len(date_inputs) >= 1:
                    # 只有一個日期輸入框，填入結束日期
                    date_inputs[0].clear()
                    date_inputs[0].send_keys(end_date)
                    print(f"✅ 已填入查詢日期: {end_date}")

                # 嘗試點擊查詢按鈕
                try:
                    query_button = self.driver.find_element(By.CSS_SELECTOR, 'input[value*="查詢"]')
                    query_button.click()
                    print("✅ 已點擊查詢按鈕")
                    time.sleep(5)  # 等待查詢結果
                except:
                    print("⚠️ 未找到查詢按鈕，跳過此步驟")

                # 查詢後再次檢查頁面元素
                print("🔍 查詢後頁面調試資訊:")
                buttons_after = self.driver.find_elements(By.TAG_NAME, "button")
                inputs_after = self.driver.find_elements(By.TAG_NAME, "input")
                links_after = self.driver.find_elements(By.TAG_NAME, "a")

                print(f"   查詢後找到 {len(buttons_after)} 個按鈕:")
                for i, btn in enumerate(buttons_after[:10]):
                    try:
                        text = btn.text or btn.get_attribute('value') or btn.get_attribute('title')
                        print(f"     按鈕 {i+1}: {text}")
                    except:
                        pass

                print(f"   查詢後找到 {len(inputs_after)} 個input元素:")
                for i, inp in enumerate(inputs_after[:15]):
                    try:
                        inp_type = inp.get_attribute('type')
                        value = inp.get_attribute('value') or inp.text
                        print(f"     Input {i+1}: type='{inp_type}' value='{value}'")
                    except:
                        pass

                print(f"   查詢後找到 {len(links_after)} 個連結:")
                for i, link in enumerate(links_after[:10]):
                    try:
                        text = link.text.strip()
                        if text and "匯出" in text or "Excel" in text or "下載" in text:
                            print(f"     重要連結 {i+1}: {text}")
                    except:
                        pass

                # 查詢結果頁面載入完成

                # 查找查詢結果中的匯款編號連結
                print("🔍 尋找查詢結果中的匯款編號連結...")
                payment_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:') or starts-with(text(), '4')]")

                if payment_links:
                    print(f"   找到 {len(payment_links)} 個匯款編號連結")
                    for i, link in enumerate(payment_links):
                        try:
                            link_text = link.text.strip()
                            print(f"   連結 {i+1}: {link_text}")
                        except:
                            pass

                    # 收集所有匯款編號
                    payment_numbers = []
                    for i, link in enumerate(payment_links):
                        try:
                            link_text = link.text.strip()
                            if link_text and len(link_text) > 10:
                                payment_numbers.append(link_text)
                                print(f"   收集匯款編號: {link_text}")
                        except:
                            pass

                    # 分別處理每個匯款編號 - 使用多視窗方式
                    for i, payment_no in enumerate(payment_numbers):
                        print(f"🔗 正在處理匯款編號 ({i+1}/{len(payment_numbers)}): {payment_no}")

                        try:
                            # 保存當前主視窗handle
                            main_window = self.driver.current_window_handle

                            # 重新找到所有連結
                            current_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:') or starts-with(text(), '4')]")
                            target_link = None

                            for link in current_links:
                                if link.text.strip() == payment_no:
                                    target_link = link
                                    break

                            if target_link:
                                # 獲取連結的href屬性
                                link_href = target_link.get_attribute('href')
                                print(f"🔗 連結href: {link_href}")

                                if 'javascript:' in link_href:
                                    # JavaScript連結需要在新視窗中執行
                                    # 使用Ctrl+Click或者執行JavaScript來開新視窗
                                    self.driver.execute_script("window.open('about:blank', '_blank');")

                                    # 切換到新視窗
                                    new_windows = [handle for handle in self.driver.window_handles if handle != main_window]
                                    if new_windows:
                                        new_window = new_windows[-1]
                                        self.driver.switch_to.window(new_window)

                                        # 在新視窗中重新導航到相同頁面
                                        self.driver.get(self.driver.current_url if hasattr(self, 'current_url') else "about:blank")
                                        time.sleep(2)

                                        # 切換回原始iframe
                                        try:
                                            iframe = WebDriverWait(self.driver, 10).until(
                                                EC.presence_of_element_located((By.NAME, "datamain"))
                                            )
                                            self.driver.switch_to.frame(iframe)
                                        except:
                                            pass

                                        # 重新執行查詢和點擊目標連結
                                        try:
                                            # 重新填入查詢條件
                                            self.refill_query_conditions()

                                            # 重新尋找並點擊目標連結
                                            new_links = self.driver.find_elements(By.XPATH, "//a[contains(@href, 'javascript:') or starts-with(text(), '4')]")
                                            for link in new_links:
                                                if link.text.strip() == payment_no:
                                                    self.driver.execute_script("arguments[0].click();", link)
                                                    time.sleep(3)
                                                    break

                                        except Exception as nav_e:
                                            print(f"⚠️ 新視窗導航失敗: {nav_e}")
                                            # 如果新視窗導航失敗，切換回主視窗並使用原方法
                                            self.driver.close()
                                            self.driver.switch_to.window(main_window)
                                            continue
                                else:
                                    # 普通連結可以直接在新視窗中開啟
                                    self.driver.execute_script("window.open(arguments[0], '_blank');", link_href)
                                    new_windows = [handle for handle in self.driver.window_handles if handle != main_window]
                                    if new_windows:
                                        new_window = new_windows[-1]
                                        self.driver.switch_to.window(new_window)
                                        time.sleep(3)

                                # 匯款詳細頁面載入完成

                                # 下載這個匯款記錄的Excel檔案
                                download_success = self.download_excel_for_payment(payment_no)
                                if download_success:
                                    downloaded_files.append(f"{self.username}_{payment_no}.xlsx")

                                # 關閉新視窗並回到主視窗
                                self.driver.close()
                                self.driver.switch_to.window(main_window)

                                # 切換回iframe
                                try:
                                    iframe = WebDriverWait(self.driver, 5).until(
                                        EC.presence_of_element_located((By.NAME, "datamain"))
                                    )
                                    self.driver.switch_to.frame(iframe)
                                except:
                                    pass

                                print(f"✅ 已關閉新視窗，回到主查詢頁面")

                            else:
                                print(f"⚠️ 找不到匯款編號 {payment_no} 的連結")

                        except Exception as link_e:
                            print(f"⚠️ 處理匯款編號 {payment_no} 時發生錯誤: {link_e}")

                            # 確保回到主視窗
                            try:
                                if len(self.driver.window_handles) > 1:
                                    self.driver.close()
                                    self.driver.switch_to.window(main_window)
                            except:
                                pass
                            continue

                    # 處理完所有連結後返回
                    return downloaded_files

                else:
                    print("❌ 沒有找到匯款編號連結")

            except Exception as date_e:
                print(f"⚠️ 填入查詢日期失敗: {date_e}")

            # 尋找並點擊匯出xlsx按鈕
            try:
                # 嘗試多種可能的匯出按鈕選擇器
                xlsx_selectors = [
                    "//button[contains(text(), '匯出xlsx')]",
                    "//input[@value*='匯出xlsx']",
                    "//a[contains(text(), '匯出xlsx')]",
                    "//button[contains(text(), 'Excel')]",
                    "//input[@value*='Excel']",
                    "//form//input[@type='submit'][contains(@value, '匯出')]"
                ]

                xlsx_button = None
                for selector in xlsx_selectors:
                    try:
                        xlsx_button = self.wait.until(
                            EC.element_to_be_clickable((By.XPATH, selector))
                        )
                        break
                    except:
                        continue

                if xlsx_button:
                    # 獲取下載前的檔案列表
                    before_files = set(self.download_dir.glob("*"))

                    # 使用JavaScript點擊避免元素遮蔽問題
                    self.driver.execute_script("arguments[0].click();", xlsx_button)
                    print(f"✅ 已點擊匯出xlsx按鈕")
                    time.sleep(5)  # 增加等待時間
                else:
                    raise Exception("找不到xlsx匯出按鈕")

                # 獲取新下載的檔案
                after_files = set(self.download_dir.glob("*"))
                new_files = after_files - before_files

                # 重命名新下載的檔案
                for new_file in new_files:
                    if new_file.suffix.lower() in ['.xlsx', '.xls']:
                        new_name = f"{self.username}_{payment_no}{new_file.suffix}"
                        new_path = self.download_dir / new_name
                        new_file.rename(new_path)
                        downloaded_files.append(str(new_path))
                        print(f"✅ 已重命名為: {new_name}")

            except Exception as e:
                print(f"⚠️ xlsx下載失敗: {e}")

            # 保持在iframe中，不切換回主frame
            return downloaded_files

        except Exception as e:
            print(f"❌ 下載記錄失敗: {e}")
            return []

    def refill_query_conditions(self):
        """在新視窗中重新填入查詢條件"""
        print("📅 重新填入查詢條件...")

        try:
            # 使用指定的日期範圍
            if self.start_date and self.end_date:
                start_date = self.start_date.strftime("%Y%m%d")
                end_date = self.end_date.strftime("%Y%m%d")
            else:
                # 預設值：當日
                today = datetime.now()
                start_date = today.strftime("%Y%m%d")
                end_date = today.strftime("%Y%m%d")

            # 尋找日期輸入框
            date_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="text"]')

            if len(date_inputs) >= 2:
                # 填入開始日期
                date_inputs[0].clear()
                date_inputs[0].send_keys(start_date)

                # 填入結束日期
                date_inputs[1].clear()
                date_inputs[1].send_keys(end_date)

                print(f"✅ 已重新填入日期範圍: {start_date} ~ {end_date}")

                # 點擊查詢按鈕
                try:
                    query_button = self.driver.find_element(By.CSS_SELECTOR, 'input[value*="查詢"]')
                    query_button.click()
                    time.sleep(3)
                    print("✅ 已執行查詢")
                except:
                    print("⚠️ 找不到查詢按鈕")
            else:
                print("⚠️ 找不到足夠的日期輸入框")

        except Exception as e:
            print(f"⚠️ 重新填入查詢條件失敗: {e}")

    def download_excel_for_payment(self, payment_no):
        """為單個匯款記錄下載Excel檔案"""
        print(f"📥 下載匯款編號 {payment_no} 的Excel檔案...")

        try:
            # 尋找並點擊匯出xlsx按鈕
            xlsx_selectors = [
                "//button[contains(text(), '匯出xlsx')]",
                "//input[@value*='匯出xlsx']",
                "//a[contains(text(), '匯出xlsx')]",
                "//button[contains(text(), 'Excel')]",
                "//input[@value*='Excel']",
                "//form//input[@type='submit'][contains(@value, '匯出')]"
            ]

            xlsx_button = None
            for selector in xlsx_selectors:
                try:
                    xlsx_button = WebDriverWait(self.driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    break
                except:
                    continue

            if xlsx_button:
                # 獲取下載前的檔案列表
                before_files = set(self.download_dir.glob("*"))

                # 使用JavaScript點擊避免元素遮蔽問題
                self.driver.execute_script("arguments[0].click();", xlsx_button)
                print(f"✅ 已點擊匯出xlsx按鈕")
                time.sleep(5)  # 等待下載完成

                # 獲取新下載的檔案
                after_files = set(self.download_dir.glob("*"))
                new_files = after_files - before_files

                # 重命名新下載的檔案
                for new_file in new_files:
                    if new_file.suffix.lower() in ['.xlsx', '.xls']:
                        new_name = f"{self.username}_{payment_no}{new_file.suffix}"
                        new_path = self.download_dir / new_name

                        # 如果目標檔案已存在，直接覆蓋
                        if new_path.exists():
                            print(f"⚠️ 檔案已存在，將覆蓋: {new_name}")
                            new_path.unlink()  # 刪除舊檔案

                        new_file.rename(new_path)
                        print(f"✅ 已重命名為: {new_name}")
                        return True

                # 處理.crdownload檔案（Chrome下載中的檔案）
                crdownload_files = list(self.download_dir.glob("*.crdownload"))
                if crdownload_files:
                    crdownload_file = crdownload_files[0]
                    new_name = f"{self.username}_{payment_no}.xlsx"
                    new_path = self.download_dir / new_name

                    if new_path.exists():
                        print(f"⚠️ 檔案已存在，將覆蓋: {new_name}")
                        new_path.unlink()  # 刪除舊檔案

                    crdownload_file.rename(new_path)
                    print(f"✅ 已重命名.crdownload檔案為: {new_name}")
                    return True

                return len(new_files) > 0
            else:
                print("⚠️ 找不到xlsx匯出按鈕")
                return False

        except Exception as e:
            print(f"⚠️ 下載匯款編號 {payment_no} 失敗: {e}")
            return False

    def get_latest_downloads(self):
        """獲取最新下載的檔案"""
        download_files = []
        for file_path in self.download_dir.glob("*"):
            if file_path.is_file() and file_path.stat().st_mtime > time.time() - 60:  # 1分鐘內的檔案
                download_files.append(str(file_path))
        return download_files

    def close(self):
        """關閉瀏覽器"""
        if self.driver:
            self.driver.quit()
            print("🔚 瀏覽器已關閉")

    def run_full_process(self):
        """執行完整的自動化流程"""
        success = False
        all_downloads = []
        records = []

        try:
            print("=" * 60)
            print(f"🤖 開始執行 WEDI Selenium 自動下載流程 (帳號: {self.username})")
            print("=" * 60)

            # 1. 初始化瀏覽器
            self.init_browser()

            # 2. 登入
            login_success = self.login()
            if not login_success:
                print(f"❌ 帳號 {self.username} 登入失敗")
                return {"success": False, "username": self.username, "error": "登入失敗", "downloads": [], "records": []}

            # 3. 導航到查詢頁面
            nav_success = self.navigate_to_payment_query()
            if not nav_success:
                print(f"❌ 帳號 {self.username} 導航失敗")
                return {"success": False, "username": self.username, "error": "導航失敗", "downloads": [], "records": []}

            # 4. 設定日期範圍
            self.set_date_range()

            # 5. 獲取付款記錄
            records = self.get_payment_records()

            if not records:
                print(f"⚠️ 帳號 {self.username} 沒有找到付款記錄")
                return {"success": True, "username": self.username, "message": "無資料可下載", "downloads": [], "records": []}

            # 6. 下載每個記錄的Excel檔案
            for record in records:
                try:
                    downloads = self.download_excel_for_record(record)
                    all_downloads.extend(downloads)
                except Exception as download_e:
                    print(f"⚠️ 帳號 {self.username} 下載記錄 {record.get('payment_no', 'unknown')} 失敗: {download_e}")
                    continue

            # 7. 跳過個別報告生成（只保留總結報告）
            # self.generate_report(records, all_downloads)  # 已停用

            print(f"🎉 帳號 {self.username} 自動化流程完成！")
            success = True

            return {"success": True, "username": self.username, "downloads": all_downloads, "records": records}

        except Exception as e:
            print(f"💥 帳號 {self.username} 流程執行失敗: {e}")
            if self.driver:
                # 已移除截圖功能
                pass
            return {"success": False, "username": self.username, "error": str(e), "downloads": all_downloads, "records": records}
        finally:
            self.close()

    def generate_report(self, records, downloaded_files):
        """生成執行報告"""
        print("📋 生成執行報告...")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = {
            "execution_time": timestamp,
            "total_records": len(records),
            "records": [r['payment_no'] for r in records],
            "downloaded_files": downloaded_files,
            "download_directory": str(self.download_dir),
            "total_downloads": len(downloaded_files)
        }

        report_filename = f"selenium_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_file = self.reports_dir / report_filename

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print(f"📋 執行報告已保存: {report_file}")
        print("=" * 60)
        print(f"📊 執行摘要:")
        print(f"   時間: {timestamp}")
        print(f"   付款記錄數: {len(records)}")
        print(f"   下載檔案數: {len(downloaded_files)}")
        print(f"   下載目錄: {self.download_dir}")
        print("=" * 60)


class MultiAccountManager:
    """多帳號管理器"""

    def __init__(self, config_file="accounts.json"):
        self.config_file = config_file
        self.load_config()

    def load_config(self):
        """載入設定檔"""
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(
                f"⛔ 設定檔 '{self.config_file}' 不存在！\n"
                "📝 請建立 accounts.json 檔案，包含 accounts 和 settings 設定"
            )

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)

            if "accounts" not in self.config or not self.config["accounts"]:
                raise ValueError("⛔ 設定檔中沒有找到帳號資訊！")

            print(f"✅ 已載入設定檔: {self.config_file}")

        except json.JSONDecodeError as e:
            raise ValueError(f"⛔ 設定檔格式錯誤: {e}")
        except Exception as e:
            raise RuntimeError(f"⛔ 載入設定檔失敗: {e}")

    def get_enabled_accounts(self):
        """取得啟用的帳號列表"""
        return [acc for acc in self.config["accounts"] if acc.get("enabled", True)]

    def run_all_accounts(self, headless_override=None, progress_callback=None, start_date=None, end_date=None):
        """執行所有啟用的帳號"""
        accounts = self.get_enabled_accounts()

        results = []
        settings = self.config.get("settings", {})

        if progress_callback:
            progress_callback(f"🚀 開始執行多帳號 WEDI 自動下載 (共 {len(accounts)} 個帳號)")
        else:
            print("\n" + "=" * 80)
            print(f"🚀 開始執行多帳號 WEDI 自動下載 (共 {len(accounts)} 個帳號)")
            print("=" * 80)

        for i, account in enumerate(accounts, 1):
            username = account["username"]
            password = account["password"]

            progress_msg = f"📊 [{i}/{len(accounts)}] 處理帳號: {username}"
            if progress_callback:
                progress_callback(progress_msg)
            else:
                print(f"\n{progress_msg}")
                print("-" * 50)

            try:
                # 如果有命令列參數覆寫，則使用該設定
                use_headless = headless_override if headless_override is not None else settings.get("headless", False)

                scraper = WEDISeleniumScraper(
                    username=username,
                    password=password,
                    headless=use_headless,
                    download_base_dir=settings.get("download_base_dir", "downloads"),
                    start_date=start_date,
                    end_date=end_date
                )

                result = scraper.run_full_process()
                results.append(result)

                # 帳號間暫停一下避免過於頻繁
                if i < len(accounts):
                    print("⏳ 等待 3 秒後處理下一個帳號...")
                    time.sleep(3)

            except Exception as e:
                print(f"💥 帳號 {username} 處理失敗: {e}")
                results.append({
                    "success": False,
                    "username": username,
                    "error": str(e),
                    "downloads": [],
                    "records": []
                })
                continue

        # 生成總報告
        self.generate_summary_report(results)
        return results

    def generate_summary_report(self, results):
        """生成總體執行報告"""
        print("\n" + "=" * 80)
        print("📋 多帳號執行總結報告")
        print("=" * 80)

        successful_accounts = [r for r in results if r["success"]]
        failed_accounts = [r for r in results if not r["success"]]
        total_downloads = sum(len(r["downloads"]) for r in results)

        print(f"📊 執行統計:")
        print(f"   總帳號數: {len(results)}")
        print(f"   成功帳號: {len(successful_accounts)}")
        print(f"   失敗帳號: {len(failed_accounts)}")
        print(f"   總下載檔案: {total_downloads}")

        if successful_accounts:
            print(f"\n✅ 成功帳號詳情:")
            for result in successful_accounts:
                username = result["username"]
                download_count = len(result["downloads"])
                if result.get("message") == "無資料可下載":
                    print(f"   🔸 {username}: 無資料可下載")
                else:
                    print(f"   🔸 {username}: 成功下載 {download_count} 個檔案")

        if failed_accounts:
            print(f"\n❌ 失敗帳號詳情:")
            for result in failed_accounts:
                username = result["username"]
                error = result.get("error", "未知錯誤")
                print(f"   🔸 {username}: {error}")

        # 保存詳細報告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"multi_account_report_{timestamp}.json"
        report_file = Path("reports") / report_filename

        # 清理結果中的不可序列化物件
        clean_results = []
        for result in results:
            clean_result = {
                "success": result["success"],
                "username": result["username"],
                "downloads": result["downloads"],
                "records": len(result.get("records", [])) if result.get("records") else 0
            }
            if "error" in result:
                clean_result["error"] = result["error"]
            if "message" in result:
                clean_result["message"] = result["message"]
            clean_results.append(clean_result)

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "execution_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_accounts": len(results),
                "successful_accounts": len(successful_accounts),
                "failed_accounts": len(failed_accounts),
                "total_downloads": total_downloads,
                "details": clean_results
            }, f, ensure_ascii=False, indent=2)

        print(f"\n💾 詳細報告已保存: {report_file}")
        print("=" * 80)


def main():
    """主程式入口"""
    import argparse
    from datetime import datetime, timedelta

    parser = argparse.ArgumentParser(description='WEDI 自動下載工具')
    parser.add_argument('--headless', action='store_true', help='使用無頭模式')
    parser.add_argument('--start-date', type=str, help='開始日期 (格式: YYYYMMDD，例如: 20241201)')
    parser.add_argument('--end-date', type=str, help='結束日期 (格式: YYYYMMDD，例如: 20241208)')

    args = parser.parse_args()

    # 日期參數驗證和處理
    try:
        today = datetime.now()

        # 處理開始日期：如果未指定則使用當日
        if args.start_date:
            start_date = datetime.strptime(args.start_date, '%Y%m%d')
        else:
            start_date = today

        # 處理結束日期：如果未指定則使用當日
        if args.end_date:
            end_date = datetime.strptime(args.end_date, '%Y%m%d')
        else:
            end_date = today

        # 驗證日期範圍
        if start_date > end_date:
            print("⛔ 錯誤: 開始日期不能晚於結束日期")
            return 1

        # 顯示查詢範圍
        if args.start_date and args.end_date:
            print(f"📅 使用指定日期範圍: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
        elif args.start_date:
            print(f"📅 從指定日期到當日: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
        elif args.end_date:
            print(f"📅 從當日到指定日期: {start_date.strftime('%Y%m%d')} ~ {end_date.strftime('%Y%m%d')}")
        else:
            print(f"📅 查詢當日: {today.strftime('%Y%m%d')}")

    except ValueError as e:
        print(f"⛔ 日期格式錯誤: {e}")
        print("💡 日期格式應為 YYYYMMDD，例如: 20241201")
        return 1

    try:
        # 統一使用多帳號管理模式
        print("🏢 WEDI 自動下載工具")

        manager = MultiAccountManager("accounts.json")
        manager.run_all_accounts(
            headless_override=args.headless if args.headless else None,
            start_date=start_date,
            end_date=end_date
        )

        return 0

    except (FileNotFoundError, ValueError, RuntimeError) as e:
        print(f"⛔ 錯誤: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⛔ 使用者中斷執行")
        return 1
    except Exception as e:
        print(f"⛔ 未知錯誤: {e}")
        return 1


if __name__ == "__main__":
    main()