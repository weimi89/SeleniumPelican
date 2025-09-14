#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
驗證碼調試工具
用於調試驗證碼偵測問題
"""

import sys
import os
import time
import re
from pathlib import Path

# 載入環境變數
from dotenv import load_dotenv
load_dotenv()

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .windows_encoding_utils import safe_print

def debug_captcha():
    """調試驗證碼偵測"""
    safe_print("🔍 驗證碼調試工具")
    print("=" * 50)

    # 設定 Chrome 選項
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1280,720")

    # 從環境變數讀取 Chrome 路徑
    chrome_binary_path = os.getenv('CHROME_BINARY_PATH')
    if chrome_binary_path:
        chrome_options.binary_location = chrome_binary_path

    # 啟動瀏覽器
    try:
        if sys.platform == "win32":
            service = Service()
            service.creation_flags = 0x08000000
        else:
            service = Service(log_path=os.devnull)

        driver = webdriver.Chrome(service=service, options=chrome_options)
        wait = WebDriverWait(driver, 10)

        safe_print("✅ 瀏覽器已啟動")

        # 前往登入頁面
        url = "http://wedinlb03.e-can.com.tw/wEDI2012/wedilogin.asp"
        driver.get(url)
        time.sleep(3)

        safe_print("📄 登入頁面已載入")

        # 分析頁面內容
        page_source = driver.page_source

        # 儲存頁面原始碼
        debug_file = Path("debug_login_page.html")
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(page_source)
        safe_print(f"💾 頁面原始碼已儲存至: {debug_file}")

        # 尋找可能的驗證碼
        safe_print("\n🔍 嘗試偵測驗證碼...")

        # 方法1: 紅色文字
        red_elements = driver.find_elements(By.CSS_SELECTOR, "*[style*='color: red'], *[color='red'], font[color='red']")
        safe_print(f"📍 找到 {len(red_elements)} 個紅色元素:")
        for i, element in enumerate(red_elements):
            text = element.text.strip()
            print(f"   {i+1}. '{text}' (長度: {len(text)})")
            if re.match(r'^[A-Z0-9]{4}$', text):
                safe_print(f"   ✅ 可能的驗證碼: {text}")

        # 方法2: 搜尋識別碼相關文字
        patterns = [
            r'識別碼[：:]\s*([A-Z0-9]{4})',
            r'識別碼[：:]([A-Z0-9]{4})',
            r'識別碼\s*[：:]\s*([A-Z0-9]{4})',
            r'驗證碼[：:]\s*([A-Z0-9]{4})',
            r'CAPTCHA[：:]\s*([A-Z0-9]{4})'
        ]

        safe_print(f"\n📝 搜尋識別碼關鍵字:")
        for i, pattern in enumerate(patterns):
            match = re.search(pattern, page_source, re.IGNORECASE)
            if match:
                safe_print(f"   ✅ 模式 {i+1} 找到: {match.group(1)}")
            else:
                safe_print(f"   ❌ 模式 {i+1} 未找到")

        # 方法3: 所有4碼英數字
        all_4_codes = re.findall(r'\b[A-Z0-9]{4}\b', page_source)
        safe_print(f"\n🔤 頁面中所有4碼英數字:")
        for code in set(all_4_codes):  # 去重複
            print(f"   - {code}")

        # 方法4: 檢查表格
        tables = driver.find_elements(By.TAG_NAME, "table")
        safe_print(f"\n📊 檢查 {len(tables)} 個表格:")
        for i, table in enumerate(tables):
            cells = table.find_elements(By.TAG_NAME, "td")
            for j, cell in enumerate(cells):
                text = cell.text.strip()
                if re.match(r'^[A-Z0-9]{4}$', text):
                    safe_print(f"   表格 {i+1}, 儲存格 {j+1}: '{text}' ✅")

        safe_print("\n⏰ 請檢查瀏覽器頁面，30秒後自動關閉...")
        time.sleep(30)

    except Exception as e:
        safe_print(f"❌ 錯誤: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

if __name__ == "__main__":
    debug_captcha()